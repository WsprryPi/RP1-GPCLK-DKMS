#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADMIN_PATH = pathlib.Path(os.environ.get(
    "RP1_GPCLK_ADMIN_PATH", ROOT / "scripts/rp1-gpclk-admin.py"))
spec = importlib.util.spec_from_file_location("rp1_admin", ADMIN_PATH)
assert spec and spec.loader
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

model = json.loads((ROOT / "release/installation-model-v1.json").read_text())
layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
assert model["release"] == layout["release"] == "0.0.0-phase5.53"
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
    qualification_archive = release / f"{admin.PACKAGE}-qualification-{admin.VERSION}.tar.gz"
    fixtures = [("dkms.conf", f'PACKAGE_VERSION="{admin.VERSION}"\n'.encode(), 0o644),
                    ("Kbuild", b"obj-m := rp1_gpclk_dkms.o\n", 0o644),
                    ("include/rp1_gpclk/version.h", f'#define RP1_GPCLK_MODULE_VERSION "{admin.VERSION}"\n'.encode(), 0o644)]
    for relative in ("scripts/rp1-gpclk-admin.py", "scripts/rp1-gpclk-diagnostics.py",
                         "release/release-layout-v1.json",
                         "release/installation-model-v1.json", "release/overlay-contract-v1.json",
                         "release/permissions-enrollment-policy-v1.json",
                         "release/diagnostics-contract-v1.json",
                         "release/lifecycle-removal-contract-v1.json",
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
                         "docs/operator/diagnostics.md", "docs/operator/gate-d-target-runbook.md",
                         "docs/operator/lifecycle.md", "docs/operator/signing.md"):
        fixtures.append((relative, (ROOT / relative).read_bytes(), 0o755 if relative.startswith("scripts/") else 0o644))
    qualification_names = {name for name, _, _ in fixtures
                           if name.startswith(("scripts/gate_d_", "schema/gate-d-", "tools/gate_d_")) or
                           name == "docs/operator/gate-d-target-runbook.md"}
    qualification_fixtures = [item for item in fixtures if item[0] in qualification_names]
    qualification_fixtures.append(("release/qualification-layout-v1.json",
                                   (ROOT / "release/qualification-layout-v1.json").read_bytes(), 0o644))
    product_fixtures = [item for item in fixtures if item[0] not in qualification_names]
    with tarfile.open(archive, "w:gz") as output:
        for name, data, mode in product_fixtures:
            member = tarfile.TarInfo(f"{admin.PACKAGE}-{admin.VERSION}/{name}")
            member.size = len(data); member.mode = mode
            output.addfile(member, io.BytesIO(data))
    with tarfile.open(qualification_archive, "w:gz") as output:
        for name, data, mode in qualification_fixtures:
            member = tarfile.TarInfo(f"{admin.PACKAGE}-qualification-{admin.VERSION}/{name}")
            member.size = len(data); member.mode = mode
            output.addfile(member, io.BytesIO(data))
    artifacts = {archive.name: archive.read_bytes(), "rp1-gpclk-gpio4.dtbo": b"gpio4",
                 "rp1-gpclk-gpio20.dtbo": b"gpio20", "PROVENANCE.json": b"{}\n",
                 "rp1-gpclk-compatibility-manifest.json": b"{}\n"}
    metadata = {"release": admin.VERSION, "publishable": True, "tagPresent": True,
                "sourceCommit": "1" * 40, "archive": archive.name,
                "archiveSha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "qualificationArchive": qualification_archive.name,
                "qualificationArchiveSha256": hashlib.sha256(qualification_archive.read_bytes()).hexdigest()}
    artifacts[qualification_archive.name] = qualification_archive.read_bytes()
    artifacts["release-metadata.json"] = (json.dumps(metadata) + "\n").encode()
    for name, data in artifacts.items():
        (release / name).write_bytes(data)
    checksum_names = sorted(artifacts)
    (release / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(artifacts[name]).hexdigest()}  {name}\n" for name in checksum_names))
    qualification_bytes = qualification_archive.read_bytes()
    qualification_archive.unlink()
    assert qualification_archive.name in admin.load_checksums(
        release, frozenset({qualification_archive.name}))
    qualification_archive.write_bytes(qualification_bytes)
    package_paths = admin.qualification_package_paths(archive, qualification_archive)
    observed_retained = {
        *admin.QUALIFICATION_RETAINED_TOOLS,
        "/usr/share/doc/rp1-gpclk-dkms/diagnostics.md",
        "/usr/share/doc/rp1-gpclk-dkms/gate-d-target-runbook.md",
        "/usr/share/doc/rp1-gpclk-dkms/lifecycle.md",
        "/usr/share/doc/rp1-gpclk-dkms/signing.md",
        "/usr/sbin/rp1-gpclk-admin",
        "/usr/sbin/rp1-gpclk-diagnostics",
    }
    assert observed_retained.issubset(package_paths)
    assert package_paths["/usr/sbin/rp1-gpclk-admin"]["kind"] == "installed-link"
    assert package_paths["/usr/share/doc/rp1-gpclk-dkms/diagnostics.md"]["kind"] == "archive"
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
    assert (target / "boot/firmware/overlays/rp1-gpclk-gpio20.dtbo").read_bytes() == b"gpio20"
    assert (target / "usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/overlay-contract-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/permissions-enrollment-policy-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/diagnostics-contract-v1.json").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/lifecycle-removal-contract-v1.json").is_file()
    assert not (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/gate-d-phase5.24-residue-recovery-v1.json").exists()
    assert (target / "usr/libexec/rp1-gpclk-dkms/lifecycle-policy").is_file()
    assert not (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/gate-d-execution-instance-v1.json").exists()
    assert not (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53/gate-d-execution-instance-v1.schema.json").exists()
    for schema_name in ("gate-d-qualification-root-v1.schema.json", "gate-d-qualification-bootstrap-plan-v1.schema.json", "gate-d-target-plan-v1.schema.json", "gate-d-attempt-index-v1.schema.json", "gate-d-pre-root-bootstrap-envelope-v1.schema.json"):
        assert not (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.53" / schema_name).exists()
    assert not (target / "usr/libexec/rp1-gpclk-dkms/gate-d-instance").exists()
    assert not (target / "usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle").exists()
    assert not (target / "usr/libexec/rp1-gpclk-dkms/gate-d-platform").exists()
    for tool in ("gate-d-boot", "gate-d-target-plan", "gate-d-attempts", "gate-d-bootstrap",
                 "gate-d-executor", "gate-d-busy-injector", "gate-d-residue"):
        assert not (target / "usr/libexec/rp1-gpclk-dkms" / tool).exists()
    assert not (target / "usr/libexec/rp1-gpclk-dkms/gate_d_root.py").exists()
    for module_name in ("gate_d_bootstrap.py", "gate_d_target_plan.py",
                        "gate_d_lifecycle.py", "gate_d_outer.py",
                        "gate_d_attempts.py", "gate_d_instance.py",
                        "gate_d_preroot.py"):
        module_path = target / "usr/libexec/rp1-gpclk-dkms" / module_name
        assert not module_path.exists()
    assert not (target / "usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe").exists()
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
    # An unpublished candidate uses the ordinary product-only lifecycle when
    # --allow-development is explicit.  Prove the qualification archive is not
    # read or required by removing it for the complete transaction.
    qualification_archive.unlink()
    development_target = base / "development-product-only-target"
    (development_target / "boot/firmware/overlays").mkdir(parents=True)
    (development_target / "usr/src/test-headers").mkdir(parents=True)
    (development_target / "lib").symlink_to("usr/lib")
    development_modules = development_target / f"usr/lib/modules/{admin.platform.release()}"
    development_modules.mkdir(parents=True)
    (development_modules / "build").symlink_to("/usr/src/test-headers")
    add_built_module(development_target)
    add_installed_module(development_target)
    development_result = admin.execute(
        release, "gpio4", False, None, None, root=development_target,
        runner=fake_runner, allow_development=True)
    assert development_result["status"] == "complete"
    assert not (development_target / "usr/libexec/rp1-gpclk-dkms/gate-d-executor").exists()

    # A same-version development successor is a complete removal followed by
    # the ordinary product-only install. The terminal ledger, not a
    # qualification identity, is the removal ownership authority.
    development_state = development_target / "var/lib/rp1-gpclk-dkms/transaction.json"
    predecessor_version = "0.0.0-phase5.52"
    current_source = development_target / "usr/src" / f"{admin.PACKAGE}-{admin.VERSION}"
    predecessor_source = development_target / "usr/src" / f"{admin.PACKAGE}-{predecessor_version}"
    current_source.rename(predecessor_source)
    current_data = development_target / "usr/share" / admin.PACKAGE / admin.VERSION
    predecessor_data = development_target / "usr/share" / admin.PACKAGE / predecessor_version
    current_data.rename(predecessor_data)
    predecessor_state = json.loads(development_state.read_text())
    predecessor_state["release"] = predecessor_version
    encoded = json.dumps(predecessor_state)
    encoded = encoded.replace(f"{admin.PACKAGE}-{admin.VERSION}",
                              f"{admin.PACKAGE}-{predecessor_version}")
    encoded = encoded.replace(f"/{admin.PACKAGE}/{admin.VERSION}",
                              f"/{admin.PACKAGE}/{predecessor_version}")
    development_state.write_text(encoded + "\n")
    removed = admin.remove(development_state, fake_runner)
    assert removed["status"] == "removed" and removed["checkpoint"] == "inactive-clean"
    assert removed["predecessorRelease"] == predecessor_version
    assert removed["predecessorDkmsPresent"] is False
    assert not predecessor_source.exists()
    assert not any(command[:2] == ["dkms", "uninstall"] for command in commands[-2:])
    for overlay_name in admin.ROUTES.values():
        assert not (development_target / "boot/firmware/overlays" / overlay_name).exists()
    add_built_module(development_target)
    add_installed_module(development_target)
    reinstalled = admin.execute(
        release, "gpio20", False, None, None, root=development_target,
        runner=fake_runner, allow_development=True)
    assert reinstalled["status"] == "complete"
    for overlay_name in admin.ROUTES.values():
        assert (development_target / "boot/firmware/overlays" / overlay_name).is_file()
    assert not (development_target / "usr/libexec/rp1-gpclk-dkms/gate-d-executor").exists()

    # Preflight identity validation is mutation-free: a changed owned file
    # prevents both DKMS commands and removal of every other owned path.
    changed_admin = development_target / "usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin"
    changed_admin.write_bytes(b"foreign replacement\n")
    command_count = len(commands)
    try:
        admin.remove(development_state, fake_runner)
    except ValueError as error:
        assert "differs from removal ledger" in str(error)
        assert len(commands) == command_count
        assert json.loads(development_state.read_text())["status"] == "complete"
        assert (development_target / "boot/firmware/overlays/rp1-gpclk-gpio4.dtbo").is_file()
    else:
        raise AssertionError("tampered product installation was removed")
    changed_admin.write_bytes((ROOT / "scripts/rp1-gpclk-admin.py").read_bytes())
    def failing_removal_runner(command: list[str]) -> str:
        if command[:2] == ["dkms", "status"]:
            return f"{admin.PACKAGE}/{admin.VERSION}, {admin.platform.release()}, installed"
        raise RuntimeError("injected DKMS failure")
    try:
        admin.remove(development_state, failing_removal_runner)
    except RuntimeError:
        failed_removal = json.loads(development_state.read_text())
        assert failed_removal["status"] == "inactive-removal-recovery-required"
        assert failed_removal["checkpoint"] == "remove-dkms"
        assert failed_removal["recoveryRequired"] is True
        assert changed_admin.is_file()
    else:
        raise AssertionError("injected DKMS removal failure unexpectedly succeeded")
    qualification_archive.write_bytes(qualification_bytes)
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
    transition_identity = dict(identity)
    transition_identity["schemaVersion"] = 2
    transition_identity["toolTransitions"] = [{
        "path": "/usr/libexec/rp1-gpclk-dkms/gate-d-executor",
        "predecessorSha256": "1" * 64,
        "successorSha256": "2" * 64,
        "mode": "0755",
    }]
    transition_identity_path = base / "qualification-transition-identity.json"
    transition_identity_path.write_text(json.dumps(transition_identity) + "\n")
    assert admin.validate_qualification_identity(
        transition_identity_path, metadata, metadata["archiveSha256"]
    )["schemaVersion"] == 2
    snapshot=json.loads((ROOT/"docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-final-v1.json").read_text())
    predecessor_paths=[]
    for item in snapshot["packagePaths"]:
        predecessor_paths.append({"path":item["path"],"type":item["type"],
                                  **({"sha256":item["sha256"]} if item["type"]=="file" else {"target":item["target"]})})
    fresh_identity=dict(identity)
    fresh_identity.update(schemaVersion=4,preRemovalLedgerSha256=snapshot["administratorLedger"]["sha256"],
                          predecessorPackagePaths=predecessor_paths,
                          predecessorPackagePathsSha256=hashlib.sha256((json.dumps(predecessor_paths,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest())
    fresh_identity_path=base/"qualification-fresh-identity.json";fresh_identity_path.write_text(json.dumps(fresh_identity)+"\n")
    assert admin.validate_qualification_identity(fresh_identity_path,metadata,metadata["archiveSha256"])["schemaVersion"]==4
    removed_state={"status":"removed","checkpoint":"inactive-clean","recoveryRequired":False,"liveOutput":False,
                   "package":admin.PACKAGE,"release":admin.VERSION,"predecessorRelease":admin.VERSION,
                   "ownedFiles":[{"path":item["path"],**({"sha256":item["sha256"]} if item["type"]=="file" else {"symlink":item["target"]})} for item in predecessor_paths],"replacedFiles":[]}
    admin.validate_fresh_qualification_prestate(fresh_identity,removed_state)
    changed=json.loads(json.dumps(removed_state));changed["ownedFiles"].pop()
    try:admin.validate_fresh_qualification_prestate(fresh_identity,changed)
    except ValueError:pass
    else:raise AssertionError("fresh qualification accepted changed removed inventory")
    # Schema 3 derives the complete existing package closure from the sealed
    # layout. One omitted documentation path is rejected before a transaction
    # or external command can exist, and the diagnostic reports the full diff.
    closure_target = base / "closure-omission-target"
    closure_docs = closure_target / "usr/share/doc/rp1-gpclk-dkms"
    closure_docs.mkdir(parents=True)
    for name in ("diagnostics.md", "lifecycle.md"):
        (closure_docs / name).write_bytes(f"predecessor {name}\n".encode())
        (closure_docs / name).chmod(0o644)
    retained_doc = closure_docs / "diagnostics.md"
    retained_status = retained_doc.stat()
    closure_identity = dict(identity)
    closure_identity["schemaVersion"] = 3
    closure_identity["packageTransitions"] = [{
        "path": "/usr/share/doc/rp1-gpclk-dkms/diagnostics.md", "type": "file",
        "predecessorSha256": hashlib.sha256(retained_doc.read_bytes()).hexdigest(),
        "successorSha256": hashlib.sha256((ROOT / "docs/operator/diagnostics.md").read_bytes()).hexdigest(),
        "mode": "0644", "ownerUid": retained_status.st_uid, "groupGid": retained_status.st_gid,
    }]
    closure_identity_path = base / "qualification-package-closure-identity.json"
    closure_identity_path.write_text(json.dumps(closure_identity) + "\n")
    command_count = len(commands)
    try:
        admin.execute(release, "gpio4", False, None, None, root=closure_target,
                      runner=fake_runner, qualification_identity=closure_identity_path)
    except ValueError as error:
        assert "package-transition closure differs" in str(error)
        assert "/usr/share/doc/rp1-gpclk-dkms/lifecycle.md" in str(error)
        assert len(commands) == command_count
        assert not (closure_target / "var/lib/rp1-gpclk-dkms/transaction.json").exists()
    else:
        raise AssertionError("incomplete package-path closure accepted")
    for mutation in (
        lambda value: value["toolTransitions"][0].update(path="/tmp/../escape"),
        lambda value: value["toolTransitions"][0].update(predecessorSha256="0" * 63),
        lambda value: value["toolTransitions"].append(dict(value["toolTransitions"][0])),
    ):
        bad_transition = json.loads(json.dumps(transition_identity))
        mutation(bad_transition)
        bad_transition_path = base / f"bad-transition-{len(list(base.glob('bad-transition-*')))}.json"
        bad_transition_path.write_text(json.dumps(bad_transition))
        try:
            admin.validate_qualification_identity(
                bad_transition_path, metadata, metadata["archiveSha256"]
            )
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe qualification tool transition accepted")

    primitive = base / "transition-primitive"
    primitive.mkdir()
    destination = primitive / "tool"
    prepared = primitive / ".tool.successor"
    destination.write_bytes(b"predecessor\n")
    prepared.write_bytes(b"successor\n")
    transition = {
        "path": str(destination),
        "predecessorSha256": hashlib.sha256(b"predecessor\n").hexdigest(),
        "successorSha256": hashlib.sha256(b"successor\n").hexdigest(),
        "mode": "0755",
    }
    transition_state = primitive / "transaction.json"
    transition_transaction = {"replacedFiles": []}
    admin.replace_qualification_tool(destination, prepared, transition,
                                     transition_transaction, transition_state)
    assert destination.read_bytes() == b"successor\n"
    recovery_state = {
        "status": "inactive-recovery-required", "liveOutput": False,
        "kernel": admin.platform.release(), "ownedFiles": [],
        "ownedDirectories": [],
        "replacedFiles": transition_transaction["replacedFiles"],
    }
    admin.atomic_json(transition_state, recovery_state)
    recovered_transition = admin.recover(transition_state, runner=lambda command: "")
    assert recovered_transition["status"] == "recovered"
    assert destination.read_bytes() == b"predecessor\n"
    for tamper in ("successor", "backup"):
        tamper_root = base / f"transition-tamper-{tamper}"
        tamper_root.mkdir()
        tamper_destination = tamper_root / "tool"
        tamper_prepared = tamper_root / ".tool.successor"
        tamper_destination.write_bytes(b"predecessor\n")
        tamper_prepared.write_bytes(b"successor\n")
        tamper_state = tamper_root / "transaction.json"
        tamper_transaction = {"replacedFiles": []}
        admin.replace_qualification_tool(tamper_destination, tamper_prepared,
                                         transition, tamper_transaction,
                                         tamper_state)
        record = tamper_transaction["replacedFiles"][0]
        pathlib.Path(record["path"] if tamper == "successor" else record["backup"]).write_bytes(b"foreign\n")
        admin.atomic_json(tamper_state, {
            "status": "inactive-recovery-required", "liveOutput": False,
            "kernel": admin.platform.release(), "ownedFiles": [],
            "ownedDirectories": [], "replacedFiles": [record],
        })
        try:
            admin.recover(tamper_state, runner=lambda command: "")
        except ValueError:
            pass
        else:
            raise AssertionError(f"tampered transition {tamper} accepted")
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

    def mixed_qualification_target(name):
        mixed_target = base / name
        (mixed_target / "boot/firmware/overlays").mkdir(parents=True)
        (mixed_target / "usr/src/test-headers").mkdir(parents=True)
        (mixed_target / "lib").symlink_to("usr/lib")
        mixed_modules = mixed_target / f"usr/lib/modules/{admin.platform.release()}"
        mixed_modules.mkdir(parents=True)
        (mixed_modules / "build").symlink_to("/usr/src/test-headers")
        add_built_module(mixed_target)
        add_installed_module(mixed_target)
        mixed_libexec = mixed_target / "usr/libexec/rp1-gpclk-dkms"
        mixed_libexec.mkdir(parents=True)
        predecessors = {
            "rp1-gpclk-admin": b"phase5.31 admin predecessor\n",
            "gate-d-executor": b"phase5.31 executor predecessor\n",
        }
        for tool, content in predecessors.items():
            path = mixed_libexec / tool
            path.write_bytes(content)
            path.chmod(0o755)
        return mixed_target, mixed_libexec, predecessors

    def mixed_identity(predecessors, executor_successor=None):
        transitions = []
        for tool, source_name in (("rp1-gpclk-admin", "rp1-gpclk-admin.py"),
                                  ("gate-d-executor", "gate_d_outer.py")):
            successor = hashlib.sha256((ROOT / f"scripts/{source_name}").read_bytes()).hexdigest()
            if tool == "gate-d-executor" and executor_successor is not None:
                successor = executor_successor
            transitions.append({
                "path": f"/usr/libexec/rp1-gpclk-dkms/{tool}",
                "predecessorSha256": hashlib.sha256(predecessors[tool]).hexdigest(),
                "successorSha256": successor,
                "mode": "0755",
            })
        value = dict(identity)
        value["schemaVersion"] = 2
        value["toolTransitions"] = transitions
        return value

    source_by_tool = {
        "rp1-gpclk-admin": "scripts/rp1-gpclk-admin.py",
        "rp1-gpclk-diagnostics": "scripts/rp1-gpclk-diagnostics.py",
        "lifecycle-policy": "scripts/lifecycle_policy.py",
        "gate-d-instance": "scripts/gate_d_instance.py",
        "gate-d-lifecycle": "scripts/gate_d_lifecycle.py",
        "gate-d-platform": "scripts/gate_d_platform.py",
        "gate-d-boot": "scripts/gate_d_boot.py",
        "gate-d-target-plan": "scripts/gate_d_target_plan.py",
        "gate-d-attempts": "scripts/gate_d_attempts.py",
        "gate-d-executor": "scripts/gate_d_outer.py",
        "gate-d-bootstrap": "scripts/gate_d_bootstrap.py",
        "gate-d-residue": "scripts/gate_d_residue.py",
        "gate_d_root.py": "scripts/gate_d_root.py",
        "gate_d_bootstrap.py": "scripts/gate_d_bootstrap.py",
        "gate_d_target_plan.py": "scripts/gate_d_target_plan.py",
        "gate_d_lifecycle.py": "scripts/gate_d_lifecycle.py",
        "gate_d_outer.py": "scripts/gate_d_outer.py",
        "gate_d_attempts.py": "scripts/gate_d_attempts.py",
        "gate_d_instance.py": "scripts/gate_d_instance.py",
        "gate_d_preroot.py": "scripts/gate_d_preroot.py",
    }

    def complete_transition_target(name):
        complete_target, complete_libexec, _ = mixed_qualification_target(name)
        predecessors = {}
        for raw in sorted(admin.QUALIFICATION_RETAINED_TOOLS):
            tool = pathlib.PurePosixPath(raw).name
            path = complete_libexec / tool
            if not path.exists():
                path.write_bytes(f"phase5.39 {tool} predecessor\n".encode())
            path.chmod(0o644 if tool.endswith(".py") else 0o755)
            predecessors[raw] = path.read_bytes()
        return complete_target, complete_libexec, predecessors

    def complete_transition_identity(predecessors, wrong_successor=None):
        transitions = []
        for raw, predecessor in sorted(predecessors.items()):
            tool = pathlib.PurePosixPath(raw).name
            successor = (b"gate-d-probe" if tool in {"gate-d-uapi-probe", "gate-d-busy-injector"}
                         else (ROOT / source_by_tool[tool]).read_bytes())
            successor_hash = hashlib.sha256(successor).hexdigest()
            if raw == wrong_successor:
                successor_hash = "0" * 64
            transitions.append({
                "path": raw,
                "predecessorSha256": hashlib.sha256(predecessor).hexdigest(),
                "successorSha256": successor_hash,
                "mode": "0644" if tool.endswith(".py") else "0755",
            })
        value = dict(identity)
        value["schemaVersion"] = 2
        value["toolTransitions"] = transitions
        return value

    def complete_package_transition(name, wrong_successor=None):
        package_target, package_libexec, predecessors = complete_transition_target(name)
        package_docs = package_target / "usr/share/doc/rp1-gpclk-dkms"
        package_docs.mkdir(parents=True)
        for doc in ("diagnostics.md", "gate-d-target-runbook.md", "lifecycle.md", "signing.md"):
            path = package_docs / doc
            path.write_bytes(f"phase5.31 {doc} predecessor\n".encode())
            predecessors[f"/usr/share/doc/rp1-gpclk-dkms/{doc}"] = path.read_bytes()
        package_sbin = package_target / "usr/sbin"
        package_sbin.mkdir(parents=True)
        links = {}
        for command in ("rp1-gpclk-admin", "rp1-gpclk-diagnostics"):
            path = package_sbin / command
            target = f"../libexec/rp1-gpclk-dkms/{command}"
            path.symlink_to(target)
            links[f"/usr/sbin/{command}"] = target
        transitions = []
        for raw, predecessor in sorted(predecessors.items()):
            destination = package_target / raw.lstrip("/")
            name = pathlib.PurePosixPath(raw).name
            if raw.startswith("/usr/share/doc/"):
                successor = (ROOT / "docs/operator" / name).read_bytes()
                mode = "0644"
            else:
                successor = (b"gate-d-probe" if name in {"gate-d-uapi-probe", "gate-d-busy-injector"}
                             else (ROOT / source_by_tool[name]).read_bytes())
                mode = "0644" if name.endswith(".py") else "0755"
            status = destination.stat()
            successor_hash = hashlib.sha256(successor).hexdigest()
            if raw == wrong_successor:
                successor_hash = "0" * 64
            transitions.append({"path": raw, "type": "file",
                                "predecessorSha256": hashlib.sha256(predecessor).hexdigest(),
                                "successorSha256": successor_hash,
                                "mode": mode, "ownerUid": status.st_uid, "groupGid": status.st_gid})
        for raw, target_value in sorted(links.items()):
            status = (package_target / raw.lstrip("/")).lstat()
            successor_target = ("../invalid-successor" if raw == wrong_successor else target_value)
            transitions.append({"path": raw, "type": "symlink",
                                "predecessorTarget": target_value,
                                "successorTarget": successor_target,
                                "ownerUid": status.st_uid, "groupGid": status.st_gid})
        value = dict(identity)
        value["schemaVersion"] = 3
        value["packageTransitions"] = sorted(transitions, key=lambda item: item["path"])
        return package_target, package_libexec, predecessors, links, value

    package_target, package_libexec, package_predecessors, package_links, package_identity = (
        complete_package_transition("complete-package-transition-target"))
    package_identity_path = base / "complete-package-transition-identity.json"
    package_identity_path.write_text(json.dumps(package_identity) + "\n")
    package_result = admin.execute(release, "gpio4", False, None, None,
                                   root=package_target, runner=fake_runner,
                                   qualification_identity=package_identity_path)
    assert package_result["status"] == "complete"
    assert len(package_result["replacedFiles"]) == len(package_predecessors) + len(package_links) == 28
    assert all(item["status"] == "committed" for item in package_result["replacedFiles"])

    # Inject a successor mismatch at every file and symlink boundary. Recovery
    # must restore the complete 28-path predecessor closure without residue.
    for boundary in sorted({*package_predecessors, *package_links}):
        boundary_name = boundary.strip("/").replace("/", "-").replace(".", "-")
        recovery_target, _, recovery_predecessors, recovery_links, recovery_identity = (
            complete_package_transition(f"package-recovery-{boundary_name}", boundary))
        recovery_identity_path = base / f"package-recovery-{boundary_name}.json"
        recovery_identity_path.write_text(json.dumps(recovery_identity) + "\n")
        try:
            admin.execute(release, "gpio4", False, None, None,
                          root=recovery_target, runner=fake_runner,
                          qualification_identity=recovery_identity_path)
        except ValueError:
            recovery_state = recovery_target / "var/lib/rp1-gpclk-dkms/transaction.json"
            assert json.loads(recovery_state.read_text())["status"] == "inactive-recovery-required"
            recovered = admin.recover(recovery_state, fake_runner)
            assert recovered["status"] == "recovered" and recovered["liveOutput"] is False
            for raw, predecessor in recovery_predecessors.items():
                assert (recovery_target / raw.lstrip("/")).read_bytes() == predecessor
            for raw, target_value in recovery_links.items():
                path = recovery_target / raw.lstrip("/")
                assert path.is_symlink() and path.readlink() == pathlib.Path(target_value)
        else:
            raise AssertionError(f"invalid package successor accepted at boundary: {boundary}")

    # Exact regression: transitioned permanent tools can bracket ordinary
    # package files without making those ordinary paths transition lookups.
    mixed_target, mixed_libexec, mixed_predecessors = mixed_qualification_target(
        "mixed-qualification-target")
    mixed_identity_path = base / "mixed-qualification-identity.json"
    mixed_identity_path.write_text(json.dumps(mixed_identity(mixed_predecessors)) + "\n")
    mixed_result = admin.execute(release, "gpio4", False, None, None,
                                 root=mixed_target, runner=fake_runner,
                                 qualification_identity=mixed_identity_path)
    assert mixed_result["status"] == "complete" and mixed_result["recoveryRequired"] is False
    assert (mixed_libexec / "rp1-gpclk-diagnostics").read_bytes() == (
        ROOT / "scripts/rp1-gpclk-diagnostics.py").read_bytes()
    assert (mixed_libexec / "gate-d-executor").read_bytes() == (
        ROOT / "scripts/gate_d_outer.py").read_bytes()
    assert all(item["status"] == "committed" for item in mixed_result["replacedFiles"])

    # The successor graph must cover the complete retained permanent inventory,
    # including the four paths omitted by the Phase 5.37 control set.
    complete_target, complete_libexec, complete_predecessors = complete_transition_target(
        "complete-transition-target")
    complete_identity_path = base / "complete-transition-identity.json"
    complete_identity_path.write_text(json.dumps(
        complete_transition_identity(complete_predecessors)) + "\n")
    complete_result = admin.execute(release, "gpio4", False, None, None,
                                    root=complete_target, runner=fake_runner,
                                    qualification_identity=complete_identity_path)
    assert complete_result["status"] == "complete"
    assert len(complete_result["replacedFiles"]) == len(admin.QUALIFICATION_RETAINED_TOOLS)
    assert all(item["status"] == "committed" for item in complete_result["replacedFiles"])
    for required in ("gate-d-attempts", "rp1-gpclk-diagnostics",
                     "lifecycle-policy", "gate-d-residue"):
        assert (complete_libexec / required).is_file()

    # An omitted or non-permanent transition is rejected before transaction
    # creation and before the external runner can perform DKMS work.
    for case in ("omitted", "extra"):
        rejected_target, _, rejected_predecessors = complete_transition_target(
            f"complete-transition-{case}")
        rejected = complete_transition_identity(rejected_predecessors)
        if case == "omitted":
            rejected["toolTransitions"].pop()
        else:
            rejected["toolTransitions"].append({
                "path": "/usr/libexec/rp1-gpclk-dkms/not-a-permanent-tool",
                "predecessorSha256": "1" * 64, "successorSha256": "2" * 64,
                "mode": "0755",
            })
        rejected_path = base / f"complete-transition-{case}-identity.json"
        rejected_path.write_text(json.dumps(rejected) + "\n")
        command_count = len(commands)
        try:
            admin.execute(release, "gpio4", False, None, None,
                          root=rejected_target, runner=fake_runner,
                          qualification_identity=rejected_path)
        except ValueError:
            assert len(commands) == command_count
            assert not (rejected_target / "var/lib/rp1-gpclk-dkms/transaction.json").exists()
        else:
            raise AssertionError(f"incomplete retained-tool graph accepted: {case}")

    # Exercise recovery with the invalid successor placed at every permanent
    # replacement boundary. Earlier replacements must roll back byte-for-byte.
    for boundary in sorted(admin.QUALIFICATION_RETAINED_TOOLS):
        boundary_name = pathlib.PurePosixPath(boundary).name.replace(".", "-")
        recovery_target, recovery_libexec, recovery_predecessors = complete_transition_target(
            f"complete-transition-recovery-{boundary_name}")
        recovery_identity_path = base / f"complete-transition-recovery-{boundary_name}.json"
        recovery_identity_path.write_text(json.dumps(
            complete_transition_identity(recovery_predecessors, wrong_successor=boundary)) + "\n")
        try:
            admin.execute(release, "gpio4", False, None, None,
                          root=recovery_target, runner=fake_runner,
                          qualification_identity=recovery_identity_path)
        except ValueError:
            recovery_state = recovery_target / "var/lib/rp1-gpclk-dkms/transaction.json"
            assert json.loads(recovery_state.read_text())["status"] == "inactive-recovery-required"
            recovered = admin.recover(recovery_state, fake_runner)
            assert recovered["status"] == "recovered" and recovered["liveOutput"] is False
            for raw, predecessor in recovery_predecessors.items():
                assert (recovery_libexec / pathlib.PurePosixPath(raw).name).read_bytes() == predecessor
        else:
            raise AssertionError(f"invalid successor accepted at boundary: {boundary}")

    # A late successor mismatch must recover earlier transitions and remove
    # ordinary files installed between them.
    recovery_target, recovery_libexec, recovery_predecessors = mixed_qualification_target(
        "mixed-qualification-recovery-target")
    recovery_identity_path = base / "mixed-qualification-recovery-identity.json"
    recovery_identity_path.write_text(json.dumps(
        mixed_identity(recovery_predecessors, executor_successor="0" * 64)) + "\n")
    try:
        admin.execute(release, "gpio4", False, None, None,
                      root=recovery_target, runner=fake_runner,
                      qualification_identity=recovery_identity_path)
    except ValueError:
        recovery_state = recovery_target / "var/lib/rp1-gpclk-dkms/transaction.json"
        failed_mixed = json.loads(recovery_state.read_text())
        assert failed_mixed["status"] == "inactive-recovery-required"
        recovered_mixed = admin.recover(recovery_state, fake_runner)
        assert recovered_mixed["status"] == "recovered"
        for tool, content in recovery_predecessors.items():
            assert (recovery_libexec / tool).read_bytes() == content
        assert not (recovery_libexec / "rp1-gpclk-diagnostics").exists()
    else:
        raise AssertionError("incorrect mixed-transition successor unexpectedly installed")

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
    ambiguous = subprocess.run([
        str(ROOT / "scripts/rp1-gpclk-admin.py"), "install", "--execute",
        "--release-directory", str(release), "--allow-development",
        "--qualification-install", "--qualification-identity", str(identity_path),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False)
    assert ambiguous.returncode != 0
    assert "cannot be combined with qualification install" in ambiguous.stderr

source = (ROOT / "scripts/rp1-gpclk-admin.py").read_text()
for prohibited in ("live_output=1", "dtoverlay", "update-initramfs", "/dev/mem", "blacklist"):
    assert prohibited not in source

print("Phase 5.3 installation model: PASS")
