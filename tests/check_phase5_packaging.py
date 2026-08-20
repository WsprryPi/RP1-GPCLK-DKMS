#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import platform
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
dkms_text = (ROOT / "dkms.conf").read_text()
if 'PACKAGE_VERSION="#MODULE_VERSION#"' in dkms_text:
    subprocess.run(
        ["python3", str(ROOT / "tests/check_debian_packaging.py")],
        check=True,
    )
    print("Phase 5.54 Debian packaging route: PASS")
    raise SystemExit(0)

layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
qualification_layout = json.loads((ROOT / "release/qualification-layout-v1.json").read_text())
release = layout["release"]

assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-[0-9A-Za-z][0-9A-Za-z.-]*", release)
assert layout["expectedTag"] == f"v{release}"
assert f'PACKAGE_VERSION="{release}"' in dkms_text
assert f'RP1_GPCLK_MODULE_VERSION "{release}"' in (ROOT / "include/rp1_gpclk/version.h").read_text()
assert release in (ROOT / f"docs/releases/{release}-security.md").read_text()
assert release in (ROOT / f"docs/releases/{release}-behavior.md").read_text()

artifact_ids = [item["id"] for item in layout["artifacts"]]
assert len(artifact_ids) == len(set(artifact_ids))
required_ids = {"source-archive", "qualification-archive", "module-source", "module-headers", "kbuild", "makefile", "dkms-conf", "kernel-module",
                "canonical-uapi", "gpio4-overlay-source", "gpio20-overlay-source", "gpio4-dtbo", "gpio20-dtbo",
                "compatibility-schema", "compatibility-manifest", "provenance", "checksums", "release-metadata",
                "installation-model", "overlay-contract", "permissions-enrollment-policy", "compatibility-decisions", "compatibility-policy", "signing-policy-data", "signing-policy-tool", "diagnostics-contract", "administration-tool", "administration-command", "diagnostics-command",
                "configuration-directory", "transaction-state", "lifecycle-tool", "lifecycle-removal-contract",
                "artifact-scoped-invalidation-policy", "qualification-successor-builder", "representative-system-matrix", "gate-d-bootstrap-schema", "gate-d-root-schema", "gate-d-target-plan-schema", "gate-d-attempt-index-schema", "gate-d-execution-schema", "gate-d-pre-root-schema", "gate-d-instance-validator", "gate-d-lifecycle-tool", "gate-d-platform-tool", "gate-d-boot-tool", "gate-d-target-plan-tool", "gate-d-attempt-generator", "gate-d-bootstrap-tool", "gate-d-root-tool", "gate-d-bootstrap-module", "gate-d-target-plan-module", "gate-d-lifecycle-module", "gate-d-outer-module", "gate-d-attempts-module", "gate-d-instance-module", "gate-d-pre-root-module", "gate-d-residue-tool", "gate-d-permanent-executor", "gate-d-busy-injector-source", "gate-d-busy-injector-header", "gate-d-busy-injector", "gate-d-uapi-probe-source", "gate-d-uapi-probe", "release-integration-gates", "calibrated-review-release-policy", "lifecycle-policy-tool", "diagnostic-tool", "operator-doc-diagnostics", "operator-doc-lifecycle", "operator-doc-signing", "gate-d-target-runbook",
                "security-notes", "behavioral-notes"}
qualification_ids = [item["id"] for item in qualification_layout["artifacts"]]
required_ids.update({"qualification-installer", "qualification-successor-validator", "gate-d-same-version-tool", "gate-d-same-version-driver", "gate-d-same-version-probe",
                     "gate-d-same-version-contract", "gate-d-matrix-policy"})
assert len(qualification_ids) == len(set(qualification_ids))
assert required_ids == set(artifact_ids) | set(qualification_ids)
assert set(artifact_ids).isdisjoint(qualification_ids)
for item in [*layout["artifacts"], *qualification_layout["artifacts"]]:
    assert item["destination"] and item["owner"] and item["group"]
    assert item["mode"] in {"0600", "0644", "0755"}
    assert item["replacement"] and item["removalOwner"]

lifecycle = (ROOT / "scripts/rp1-gpclk-lifecycle.sh").read_text()
for required in ("live_output=0", "dkms add", "dkms build", "dkms install", "dkms uninstall", "dkms remove", "sign-file", "overlay-build", "gpio4|gpio20"):
    assert required in lifecycle, f"lifecycle tool missing {required}"
for prohibited in ("/dev/mem", "gpio write", "live_output=1"):
    assert prohibited not in lifecycle, f"lifecycle tool contains prohibited operation {prohibited}"

diagnostics = (ROOT / "scripts/rp1-gpclk-diagnostics.py").read_text()
for prohibited in ("sudo", "modprobe", "dtoverlay", "dkms install", "dkms remove"):
    assert prohibited not in diagnostics, f"diagnostics contain mutating operation {prohibited}"

module_main = (ROOT / "src/rp1_gpclk_main.c").read_text()
release_gate = module_main[module_main.index("static bool rp1_gpclk_release_identity_allowed"):]
release_gate = release_gate[:release_gate.index("\n}")]
assert "return false;" in release_gate, "Phase 5.2 must remain live-ineligible without an exact manifest entry"

with tempfile.TemporaryDirectory() as tools_dir, tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
    fake_dtc = pathlib.Path(tools_dir) / "dtc"
    fake_dtc.write_text("""#!/bin/sh
if [ "$1" = "--version" ]; then echo 'Version: deterministic-test-dtc 1'; exit 0; fi
out=
input=
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then shift; out=$1; else input=$1; fi
  shift
done
sha256sum "$input" | awk '{print $1}' >"$out"
""")
    fake_dtc.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = f"{tools_dir}:{environment['PATH']}"
    for destination in (first, second):
        subprocess.run([str(ROOT / "scripts/build_release.py"), destination, "--development"], check=True, env=environment)
        subprocess.run([str(ROOT / "scripts/validate_release.py"), destination, "--allow-development"], check=True, env=environment)
    archive = pathlib.Path(first) / f"rp1-gpclk-dkms-{release}.tar.gz"
    qualification_archive = pathlib.Path(first) / f"rp1-gpclk-dkms-qualification-{release}.tar.gz"
    listing = subprocess.check_output(["tar", "-tzf", archive], text=True)
    archived = {name.split("/", 1)[1] for name in listing.splitlines()}
    for prefix in ("docs/contracts/", "docs/development/", "docs/evidence/",
                   "docs/reviews/", "tests/", "release/gate-d-attempts"):
        assert not any(name.startswith(prefix) for name in archived)
    assert "AGENTS.md" not in archived
    assert "docs/releases/0.0.0-phase5.52-security.md" not in archived
    assert f"docs/releases/{release}-security.md" in archived
    assert f"docs/releases/{release}-behavior.md" in archived
    assert not any(name.startswith(("scripts/gate_d_", "schema/gate-d-", "tools/gate_d_"))
                   for name in archived)
    assert "release/gate-d-phase5.24-residue-recovery-v1.json" not in archived
    assert "docs/operator/gate-d-target-runbook.md" not in archived
    assert "scripts/build_release.py" in archived
    assert "scripts/validate_release.py" in archived
    assert not any(re.match(r"release/gate-d-(?:pre-root-bootstrap-envelope|qualification-bootstrap-plan)-phase", name)
                   for name in archived)
    qualification_listing = subprocess.check_output(["tar", "-tzf", qualification_archive], text=True)
    qualified = {name.split("/", 1)[1] for name in qualification_listing.splitlines()}
    assert "release/qualification-layout-v1.json" in qualified
    assert "scripts/gate_d_outer.py" in qualified
    assert "schema/gate-d-qualification-root-v1.schema.json" in qualified
    assert "tools/gate_d_busy_injector.c" in qualified
    assert "release/representative-system-matrix-v1.json" in qualified
    assert "release/gate-d-matrix-policy-v2.json" in qualified
    assert "docs/operator/gate-d-target-runbook.md" in qualified
    assert "release/gate-d-phase5.24-residue-recovery-v1.json" not in qualified
    assert not any(name.startswith(("tests/", "release/gate-d-attempts")) for name in qualified)
    names = sorted(path.name for path in pathlib.Path(first).iterdir())
    assert names == sorted(path.name for path in pathlib.Path(second).iterdir())
    for name in names:
        left = hashlib.sha256((pathlib.Path(first) / name).read_bytes()).hexdigest()
        right = hashlib.sha256((pathlib.Path(second) / name).read_bytes()).hexdigest()
        assert left == right, f"release artifact is not reproducible: {name}"
    with tempfile.TemporaryDirectory() as extracted:
        subprocess.run(["tar", "-xzf", archive, "-C", extracted], check=True)
        subprocess.run(["tar", "-xzf", qualification_archive, "-C", extracted], check=True)
        source = pathlib.Path(extracted) / f"rp1-gpclk-dkms-{release}"
        qualification = pathlib.Path(extracted) / f"rp1-gpclk-dkms-qualification-{release}"
        assert (qualification / "tools/gate_d_busy_injector.h").is_file()
        held_qualification = pathlib.Path(extracted) / qualification_archive.name
        qualification_archive.rename(held_qualification)
        try:
            subprocess.run([str(source / "scripts/validate_release.py"), first,
                            "--allow-development"], check=True, env=environment)
        finally:
            held_qualification.rename(qualification_archive)
        if platform.system() == "Linux":
            for source_name, output_name in (("gate_d_busy_injector.c", "gate-d-busy-injector"),
                                             ("gate_d_uapi_probe.c", "gate-d-uapi-probe")):
                subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                                f"-I{source / 'include/uapi'}", str(qualification / "tools" / source_name),
                                "-o", str(pathlib.Path(extracted) / output_name)], check=True)
    metadata = json.loads((pathlib.Path(first) / "release-metadata.json").read_text())
    expected_dirty = bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=all"], text=True))
    assert metadata["publishable"] is False and metadata["tagPresent"] is False
    assert metadata["dirtySource"] is expected_dirty
    checksum = pathlib.Path(first) / "SHA256SUMS"
    checksum.write_text(checksum.read_text().replace("0", "1", 1))
    result = subprocess.run([str(ROOT / "scripts/validate_release.py"), first, "--allow-development"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert result.returncode != 0, "tampered checksum unexpectedly passed"

print("Phase 5.2 release-unit contracts: PASS")
