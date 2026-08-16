#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp1_admin", ROOT / "scripts/rp1-gpclk-admin.py")
assert spec and spec.loader
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

model = json.loads((ROOT / "release/installation-model-v1.json").read_text())
layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
assert model["release"] == layout["release"] == "0.0.0-phase5.31"
assert model["dkmsModule"] == layout["package"]
assert model["kernelModule"] == layout["module"]
assert model["transaction"] == admin.STEPS
assert set(model["routes"]) == set(admin.ROUTES)
assert all(value is False for value in model["implicitActions"].values())
for key in ("source", "module", "overlays", "releaseData", "configuration", "enrollment", "state",
            "administrationCommand", "diagnosticsCommand", "implementations", "documentation"):
    assert model["paths"][key].startswith("/")

for route in admin.ROUTES:
    planned = admin.plan(route, False)
    assert planned["liveOutput"] is False
    assert planned["moduleLoad"] == planned["overlayActivation"] == "not-performed"
try:
    admin.plan("gpio17", False)
except ValueError:
    pass
else:
    raise AssertionError("arbitrary route accepted")

for unsafe in ("relative", "/", "/tmp/../etc", "/tmp/$name"):
    try:
        admin.rooted(pathlib.Path("/tmp/root"), unsafe)
    except ValueError:
        pass
    else:
        raise AssertionError(f"unsafe path accepted: {unsafe}")

with tempfile.TemporaryDirectory() as temporary:
    header_root = pathlib.Path(temporary)
    kernel = "6.18.34+rpt-rpi-2712"
    (header_root / "lib").symlink_to("usr/lib")
    module_dir = header_root / "usr/lib/modules" / kernel
    header_dir = header_root / "usr/src" / f"linux-headers-{kernel}"
    module_dir.mkdir(parents=True)
    header_dir.mkdir(parents=True)
    (module_dir / "build").symlink_to(f"/usr/src/linux-headers-{kernel}")
    assert admin.kernel_headers(header_root, kernel) == header_dir.resolve()
    (module_dir / "build").unlink()
    (module_dir / "build").symlink_to(header_root / "tmp/escaped")
    (header_root / "tmp/escaped").mkdir(parents=True)
    try:
        admin.kernel_headers(header_root, kernel)
    except ValueError:
        pass
    else:
        raise AssertionError("kernel header symlink escape accepted")
    (module_dir / "build").unlink()
    header_dir.chmod(0o777)
    (module_dir / "build").symlink_to(f"/usr/src/linux-headers-{kernel}")
    try:
        admin.kernel_headers(header_root, kernel)
    except ValueError:
        pass
    else:
        raise AssertionError("writable kernel header directory accepted")

with tempfile.TemporaryDirectory() as temporary:
    module_root = pathlib.Path(temporary)
    kernel = "6.18.34+rpt-rpi-2712"
    architecture = "aarch64"
    module_dir = module_root / f"var/lib/dkms/{admin.PACKAGE}/{admin.VERSION}/{kernel}/{architecture}/module"
    module_dir.mkdir(parents=True)
    for suffix in (".ko", ".ko.xz", ".ko.gz", ".ko.zst"):
        candidate = module_dir / f"{admin.MODULE}{suffix}"
        candidate.write_bytes(b"module")
        assert admin.dkms_built_module(module_root, kernel, architecture) == candidate
        candidate.unlink()
    for invalid in (".ko.bz2", ".ko.tmp"):
        unknown = module_dir / f"{admin.MODULE}{invalid}"
        unknown.write_bytes(b"module")
        regular = module_dir / f"{admin.MODULE}.ko"
        regular.write_bytes(b"module")
        try:
            admin.dkms_built_module(module_root, kernel, architecture)
        except ValueError:
            pass
        else:
            raise AssertionError("unknown DKMS module representation passed")
        regular.unlink()
        unknown.unlink()
    regular = module_dir / f"{admin.MODULE}.ko"
    compressed = module_dir / f"{admin.MODULE}.ko.xz"
    regular.write_bytes(b"module")
    compressed.write_bytes(b"module")
    try:
        admin.dkms_built_module(module_root, kernel, architecture)
    except ValueError:
        pass
    else:
        raise AssertionError("ambiguous DKMS module representations passed")
    regular.unlink(); compressed.unlink()
    regular.symlink_to("foreign.ko")
    try:
        admin.dkms_built_module(module_root, kernel, architecture)
    except ValueError:
        pass
    else:
        raise AssertionError("symlink DKMS module representation passed")
    regular.unlink()
    regular.mkdir()
    try:
        admin.dkms_built_module(module_root, kernel, architecture)
    except ValueError:
        pass
    else:
        raise AssertionError("directory DKMS module representation passed")

with tempfile.TemporaryDirectory() as temporary:
    installed_root = pathlib.Path(temporary)
    kernel = "6.18.34+rpt-rpi-2712"
    (installed_root / "lib").symlink_to("usr/lib")
    installed_dir = installed_root / f"usr/lib/modules/{kernel}/updates/dkms"
    installed_dir.mkdir(parents=True)
    for suffix in (".ko", ".ko.xz", ".ko.gz", ".ko.zst"):
        candidate = installed_dir / f"{admin.MODULE}{suffix}"
        candidate.write_bytes(b"module")
        assert admin.dkms_installed_module(installed_root, kernel) == candidate
        candidate.unlink()
    regular = installed_dir / f"{admin.MODULE}.ko"
    unknown = installed_dir / f"{admin.MODULE}.ko.bz2"
    regular.write_bytes(b"module"); unknown.write_bytes(b"module")
    try:
        admin.dkms_installed_module(installed_root, kernel)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown installed module representation passed")
    regular.unlink(); unknown.unlink()
    regular.write_bytes(b"module")
    compressed = installed_dir / f"{admin.MODULE}.ko.xz"
    compressed.write_bytes(b"module")
    try:
        admin.dkms_installed_module(installed_root, kernel)
    except ValueError:
        pass
    else:
        raise AssertionError("ambiguous installed module representations passed")
    regular.unlink(); compressed.unlink()
    regular.symlink_to("foreign.ko")
    try:
        admin.dkms_installed_module(installed_root, kernel)
    except ValueError:
        pass
    else:
        raise AssertionError("symlink installed module representation passed")
    regular.unlink(); regular.mkdir()
    try:
        admin.dkms_installed_module(installed_root, kernel)
    except ValueError:
        pass
    else:
        raise AssertionError("directory installed module representation passed")

with tempfile.TemporaryDirectory() as temporary:
    base = pathlib.Path(temporary)
    release = base / "release"
    target = base / "target"
    release.mkdir()
    archive = release / f"{admin.PACKAGE}-{admin.VERSION}.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        fixtures = [("dkms.conf", f'PACKAGE_VERSION="{admin.VERSION}"\n'.encode(), 0o644),
                    ("Kbuild", b"obj-m := rp1_gpclk_dkms.o\n", 0o644),
                    ("include/rp1_gpclk/version.h", f'#define RP1_GPCLK_MODULE_VERSION "{admin.VERSION}"\n'.encode(), 0o644)]
        for relative in ("scripts/rp1-gpclk-admin.py", "scripts/rp1-gpclk-diagnostics.py",
                         "release/installation-model-v1.json", "release/overlay-contract-v1.json",
                         "release/permissions-enrollment-policy-v1.json",
                         "release/diagnostics-contract-v1.json",
                         "release/lifecycle-removal-contract-v1.json",
                         "release/gate-d-phase5.24-residue-recovery-v1.json",
                         "schema/gate-d-execution-instance-v1.schema.json",
                         "schema/gate-d-qualification-root-v1.schema.json",
                         "schema/gate-d-qualification-bootstrap-plan-v1.schema.json",
                         "schema/gate-d-target-plan-v1.schema.json",
                         "schema/gate-d-pre-root-bootstrap-envelope-v1.schema.json",
                         "schema/gate-d-attempt-index-v1.schema.json",
                         "scripts/lifecycle_policy.py", "scripts/gate_d_instance.py",
                         "scripts/gate_d_lifecycle.py",
                         "scripts/gate_d_platform.py",
                         "scripts/gate_d_boot.py", "scripts/gate_d_target_plan.py",
                         "scripts/gate_d_attempts.py", "scripts/gate_d_outer.py",
                         "scripts/gate_d_bootstrap.py", "scripts/gate_d_root.py", "scripts/gate_d_preroot.py", "scripts/gate_d_residue.py",
                         "tools/gate_d_uapi_probe.c",
                         "tools/gate_d_busy_injector.c",
                         "docs/operator/lifecycle.md", "docs/operator/signing.md"):
            fixtures.append((relative, (ROOT / relative).read_bytes(), 0o755 if relative.startswith("scripts/") else 0o644))
        for name, data, mode in fixtures:
            member = tarfile.TarInfo(f"{admin.PACKAGE}-{admin.VERSION}/{name}")
            member.size = len(data); member.mode = mode
            output.addfile(member, io.BytesIO(data))
    artifacts = {archive.name: archive.read_bytes(), "rp1-gpclk-gpio4.dtbo": b"gpio4",
                 "rp1-gpclk-gpio20.dtbo": b"gpio20", "PROVENANCE.json": b"{}\n",
                 "rp1-gpclk-compatibility-manifest.json": b"{}\n"}
    metadata = {"release": admin.VERSION, "publishable": True, "tagPresent": True,
                "sourceCommit": "1" * 40, "archive": archive.name,
                "archiveSha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    artifacts["release-metadata.json"] = (json.dumps(metadata) + "\n").encode()
    for name, data in artifacts.items():
        (release / name).write_bytes(data)
    checksum_names = sorted(artifacts)
    (release / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(artifacts[name]).hexdigest()}  {name}\n" for name in checksum_names))
    (target / "boot/firmware/overlays").mkdir(parents=True)
    target_headers = target / "usr/src/test-headers"
    target_headers.mkdir(parents=True)
    (target / "lib").symlink_to("usr/lib")
    target_modules = target / f"usr/lib/modules/{admin.platform.release()}"
    target_modules.mkdir(parents=True)
    (target_modules / "build").symlink_to("/usr/src/test-headers")
    commands: list[list[str]] = []
    def add_built_module(test_root: pathlib.Path) -> None:
        built = test_root / f"var/lib/dkms/{admin.PACKAGE}/{admin.VERSION}/{admin.platform.release()}/{admin.platform.machine()}/module/{admin.MODULE}.ko.xz"
        built.parent.mkdir(parents=True, exist_ok=True)
        built.write_bytes(b"compressed-module")
    def add_installed_module(test_root: pathlib.Path) -> None:
        installed = test_root / f"usr/lib/modules/{admin.platform.release()}/updates/dkms/{admin.MODULE}.ko.xz"
        installed.parent.mkdir(parents=True, exist_ok=True)
        installed.write_bytes(b"compressed-installed-module")
    def fake_runner(command: list[str]) -> str:
        commands.append(command)
        if command[0] == "cc":
            pathlib.Path(command[-1]).write_bytes(b"gate-d-probe")
            return ""
        if command[:3] == ["modinfo", "-F", "version"]:
            return admin.VERSION
        if command[:3] == ["modinfo", "-F", "vermagic"]:
            return admin.platform.release() + " SMP"
        if command[:3] == ["modinfo", "-F", "signer"]:
            return "test signer"
        return ""
    add_built_module(target)
    add_installed_module(target)
    result = admin.execute(release, "gpio4", False, None, None, root=target, runner=fake_runner)
    assert result["status"] == "complete" and result["liveOutput"] is False
    assert (target / "boot/firmware/overlays/rp1-gpclk-gpio4.dtbo").read_bytes() == b"gpio4"
    assert not (target / "boot/firmware/overlays/rp1-gpclk-gpio20.dtbo").exists()
    assert (target / "usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/overlay-contract-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/permissions-enrollment-policy-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/diagnostics-contract-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/lifecycle-removal-contract-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/gate-d-phase5.24-residue-recovery-v1.json").is_file()
    assert (target / "usr/libexec/rp1-gpclk-dkms/lifecycle-policy").is_file()
    assert not (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/gate-d-execution-instance-v1.json").exists()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31/gate-d-execution-instance-v1.schema.json").is_file()
    for schema_name in ("gate-d-qualification-root-v1.schema.json", "gate-d-qualification-bootstrap-plan-v1.schema.json", "gate-d-target-plan-v1.schema.json", "gate-d-attempt-index-v1.schema.json", "gate-d-pre-root-bootstrap-envelope-v1.schema.json"):
        assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.31" / schema_name).is_file()
    assert (target / "usr/libexec/rp1-gpclk-dkms/gate-d-instance").is_file()
    assert (target / "usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle").is_file()
    assert (target / "usr/libexec/rp1-gpclk-dkms/gate-d-platform").is_file()
    for tool in ("gate-d-boot", "gate-d-target-plan", "gate-d-attempts", "gate-d-bootstrap",
                 "gate-d-executor", "gate-d-busy-injector", "gate-d-residue"):
        assert (target / "usr/libexec/rp1-gpclk-dkms" / tool).is_file()
    assert (target / "usr/libexec/rp1-gpclk-dkms/gate_d_root.py").is_file()
    for module_name in ("gate_d_bootstrap.py", "gate_d_target_plan.py",
                        "gate_d_lifecycle.py", "gate_d_outer.py",
                        "gate_d_attempts.py", "gate_d_instance.py",
                        "gate_d_preroot.py"):
        module_path = target / "usr/libexec/rp1-gpclk-dkms" / module_name
        assert module_path.is_file() and module_path.stat().st_mode & 0o777 == 0o644
    assert (target / "usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe").is_file()
    assert (target / "usr/sbin/rp1-gpclk-admin").is_symlink()
    assert (target / "etc/rp1-gpclk-dkms").is_dir()
    assert not (target / "etc/rp1-gpclk-dkms/enrollment.json").exists()
    flat = " ".join(value for command in commands for value in command)
    for prohibited in ("modprobe", "dtoverlay", "live_output=1", "/dev/mem", "reboot", "blacklist"):
        assert prohibited not in flat
    state_path = target / "var/lib/rp1-gpclk-dkms/transaction.json"
    assert json.loads(state_path.read_text())["status"] == "complete"
    # A different pre-existing overlay is never replaced and leaves a
    # recognizable inactive recovery state.
    second = base / "second"
    (second / "boot/firmware/overlays").mkdir(parents=True)
    (second / "boot/firmware/overlays/rp1-gpclk-gpio4.dtbo").write_bytes(b"foreign")
    (second / "usr/src/test-headers").mkdir(parents=True)
    (second / "lib").symlink_to("usr/lib")
    second_modules = second / f"usr/lib/modules/{admin.platform.release()}"
    second_modules.mkdir(parents=True)
    (second_modules / "build").symlink_to("/usr/src/test-headers")
    add_built_module(second)
    add_installed_module(second)
    try:
        admin.execute(release, "gpio4", False, None, None, root=second, runner=fake_runner)
    except ValueError:
        failure_path = second / "var/lib/rp1-gpclk-dkms/transaction.json"
        failure = json.loads(failure_path.read_text())
        assert failure["status"] == "inactive-recovery-required" and failure["liveOutput"] is False
        recovered = admin.recover(failure_path, fake_runner)
        assert recovered["status"] == "recovered"
        assert (second / "boot/firmware/overlays/rp1-gpclk-gpio4.dtbo").read_bytes() == b"foreign"
    else:
        raise AssertionError("foreign overlay replacement unexpectedly succeeded")

    # Qualification bootstrap is a separate, exact, unpublished-candidate path.
    metadata.update(publishable=False, tagPresent=False)
    artifacts["release-metadata.json"] = (json.dumps(metadata) + "\n").encode()
    (release / "release-metadata.json").write_bytes(artifacts["release-metadata.json"])
    (release / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(artifacts[name]).hexdigest()}  {name}\n" for name in checksum_names))
    identity = {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "rp1-gpclk-gate-d-qualification-install-identity",
        "release": admin.VERSION, "sourceCommit": "1" * 40,
        "archiveSha256": metadata["archiveSha256"], "publishable": False,
        "tagPresent": False, "outputDisabled": True, "liveOutput": False,
        "purpose": "gate-d-representative-system-qualification",
    }
    identity_path = base / "qualification-identity.json"
    identity_path.write_text(json.dumps(identity) + "\n")
    qualification_target = base / "qualification-target"
    (qualification_target / "boot/firmware/overlays").mkdir(parents=True)
    (qualification_target / "usr/src/test-headers").mkdir(parents=True)
    (qualification_target / "lib").symlink_to("usr/lib")
    qualification_modules = qualification_target / f"usr/lib/modules/{admin.platform.release()}"
    qualification_modules.mkdir(parents=True)
    (qualification_modules / "build").symlink_to("/usr/src/test-headers")
    add_built_module(qualification_target)
    add_installed_module(qualification_target)
    result = admin.execute(release, "gpio4", False, None, None,
                           root=qualification_target, runner=fake_runner,
                           qualification_identity=identity_path)
    assert result["status"] == "complete" and result["liveOutput"] is False

    for field, replacement in (("archiveSha256", "0" * 64),
                               ("sourceCommit", "2" * 40),
                               ("liveOutput", True), ("outputDisabled", False),
                               ("purpose", "general-install")):
        bad = dict(identity); bad[field] = replacement
        bad_path = base / f"bad-{field}.json"; bad_path.write_text(json.dumps(bad))
        try:
            admin.execute(release, "gpio4", False, None, None,
                          root=base / f"bad-target-{field}", runner=fake_runner,
                          qualification_identity=bad_path)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe qualification identity accepted: {field}")
    symlink_identity = base / "qualification-link.json"
    symlink_identity.symlink_to(identity_path)
    try:
        admin.validate_qualification_identity(symlink_identity, metadata,
                                              metadata["archiveSha256"])
    except ValueError:
        pass
    else:
        raise AssertionError("symlinked qualification identity accepted")
    for extra in (("--qualification-install",),
                  ("--qualification-identity", str(identity_path))):
        command = [str(ROOT / "scripts/rp1-gpclk-admin.py"), "install", "--execute",
                   "--release-directory", str(release), *extra]
        outcome = subprocess.run(command, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, text=True, check=False)
        assert outcome.returncode != 0
        assert "requires both --qualification-install and --qualification-identity" in outcome.stderr

source = (ROOT / "scripts/rp1-gpclk-admin.py").read_text()
for prohibited in ("live_output=1", "dtoverlay", "update-initramfs", "/dev/mem", "blacklist"):
    assert prohibited not in source

print("Phase 5.3 installation model: PASS")
