#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import pathlib
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp1_admin", ROOT / "scripts/rp1-gpclk-admin.py")
assert spec and spec.loader
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

model = json.loads((ROOT / "release/installation-model-v1.json").read_text())
layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
assert model["release"] == layout["release"] == "0.0.0-phase5.2"
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
                         "docs/operator/lifecycle.md", "docs/operator/signing.md"):
            fixtures.append((relative, (ROOT / relative).read_bytes(), 0o755 if relative.startswith("scripts/") else 0o644))
        for name, data, mode in fixtures:
            member = tarfile.TarInfo(f"{admin.PACKAGE}-{admin.VERSION}/{name}")
            member.size = len(data); member.mode = mode
            output.addfile(member, io.BytesIO(data))
    artifacts = {archive.name: archive.read_bytes(), "rp1-gpclk-gpio4.dtbo": b"gpio4",
                 "rp1-gpclk-gpio20.dtbo": b"gpio20", "PROVENANCE.json": b"{}\n",
                 "rp1-gpclk-compatibility-manifest.json": b"{}\n"}
    metadata = {"release": admin.VERSION, "publishable": True, "archive": archive.name,
                "archiveSha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    artifacts["release-metadata.json"] = (json.dumps(metadata) + "\n").encode()
    for name, data in artifacts.items():
        (release / name).write_bytes(data)
    checksum_names = sorted(artifacts)
    (release / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(artifacts[name]).hexdigest()}  {name}\n" for name in checksum_names))
    (target / "boot/firmware/overlays").mkdir(parents=True)
    (target / f"lib/modules/{admin.platform.release()}/build").mkdir(parents=True)
    commands: list[list[str]] = []
    def fake_runner(command: list[str]) -> str:
        commands.append(command)
        if command[:3] == ["modinfo", "-F", "version"]:
            return admin.VERSION
        if command[:3] == ["modinfo", "-F", "vermagic"]:
            return admin.platform.release() + " SMP"
        if command[:3] == ["modinfo", "-F", "signer"]:
            return "test signer"
        return ""
    result = admin.execute(release, "gpio4", False, None, None, root=target, runner=fake_runner)
    assert result["status"] == "complete" and result["liveOutput"] is False
    assert (target / "boot/firmware/overlays/rp1-gpclk-gpio4.dtbo").read_bytes() == b"gpio4"
    assert not (target / "boot/firmware/overlays/rp1-gpclk-gpio20.dtbo").exists()
    assert (target / "usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin").is_file()
    assert (target / "usr/share/rp1-gpclk-dkms/0.0.0-phase5.2/overlay-contract-v1.json").is_file()
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
    (second / f"lib/modules/{admin.platform.release()}/build").mkdir(parents=True)
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

source = (ROOT / "scripts/rp1-gpclk-admin.py").read_text()
for prohibited in ("live_output=1", "dtoverlay", "update-initramfs", "/dev/mem", "blacklist"):
    assert prohibited not in source

print("Phase 5.3 installation model: PASS")
