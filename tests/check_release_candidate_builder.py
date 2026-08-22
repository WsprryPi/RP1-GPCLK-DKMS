#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_release_candidate as builder
from scripts import release_candidate_controls as controls
from scripts import release_candidate_target as target


def tar_xz(files: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:xz", format=tarfile.PAX_FORMAT) as archive:
        directories = set()
        for name in files:
            parts = Path(name).parts[:-1]
            for index in range(1, len(parts) + 1):
                directories.add("/".join(parts[:index]))
        for name in sorted(directories):
            member = tarfile.TarInfo(f"./{name}/")
            member.type = tarfile.DIRTYPE
            member.mode = 0o755
            archive.addfile(member)
        for name, content in sorted(files.items()):
            member = tarfile.TarInfo(f"./{name}")
            member.size = len(content)
            member.mode = 0o644
            archive.addfile(member, io.BytesIO(content))
    return output.getvalue()


def ar_member(name: str, content: bytes) -> bytes:
    header = (
        f"{name + '/':<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(content):<10}`\n"
    ).encode("ascii")
    return header + content + (b"\n" if len(content) % 2 else b"")


with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    product = root / "rp1-gpclk-dkms_1.1.1-1_all.deb"
    control = tar_xz({
        "control": b"Package: rp1-gpclk-dkms\nVersion: 1.1.1-1\nArchitecture: all\n",
        "md5sums": b"",
    })
    base = "usr/src/rp1-gpclk-dkms-1.1.1"
    data_files = {
        f"{base}/dkms.conf": b'PACKAGE_NAME="rp1-gpclk-dkms"\nPACKAGE_VERSION="1.1.1"\n',
        f"{base}/Kbuild": b"obj-m += rp1_gpclk_dkms.o\n",
        f"{base}/Makefile": b"all:\n\t@true\n",
        f"{base}/include/uapi/linux/rp1_gpclk.h": b"uapi\n",
        f"{base}/overlays/rp1-gpclk-gpio4.dts": b"gpio4\n",
        f"{base}/overlays/rp1-gpclk-gpio20.dts": b"gpio20\n",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo": b"dtbo4\n",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo": b"dtbo20\n",
        "usr/libexec/rp1-gpclk-dkms/rp1-gpclk-route-manager": b"#!/usr/bin/python3\n",
        "usr/sbin/rp1-gpclk-route-manager": b"#!/usr/bin/python3\n",
        "usr/share/rp1-gpclk-dkms/1.1.1/rp1-gpclk-route-manager-v1.schema.json": b"{}\n",
        "usr/share/doc/rp1-gpclk-dkms/route-manager-v1.md": b"contract\n",
        "usr/share/doc/rp1-gpclk-dkms/copyright": b"MIT\n",
    }
    product.write_bytes(
        b"!<arch>\n"
        + ar_member("debian-binary", b"2.0\n")
        + ar_member("control.tar.xz", control)
        + ar_member("data.tar.xz", tar_xz(data_files))
    )
    inventory, extracted = builder.validate_product(product)
    assert inventory["debianVersion"] == "1.1.1-1"
    assert inventory["packageSha256"] == builder.sha256(product)
    assert set(data_files) <= set(extracted)
    inventory_bytes = builder.pretty(inventory)
    identity = {
        "release": "1.1.1", "expectedTag": "v1.1.1",
        "productPackageSha256": inventory["packageSha256"],
    }
    identity_bytes = builder.pretty(identity)
    plan = builder.target_plan(
        "1" * 40, inventory["packageSha256"], builder.sha256_bytes(inventory_bytes),
        builder.sha256_bytes(identity_bytes), builder.sha256_bytes(b"uapi\n"),
        builder.sha256_bytes(b"dtbo4\n"), builder.sha256_bytes(b"dtbo20\n"),
    )
    compatibility = builder.compatibility("1" * 40, "2026-08-22T00:00:00-05:00",
                                          inventory["packageSha256"], extracted)
    assert {entry["route"] for entry in compatibility["entries"]} == {"GPIO4", "GPIO20"}
    assert all(entry["uapiAbi"] == 2 and entry["release"] == "1.1.1"
               and entry["state"] == "Unavailable" and entry["liveEligible"] is False
               for entry in compatibility["entries"])
    assert compatibility["entries"][0]["id"] != compatibility["entries"][1]["id"]
    assert compatibility["entries"][0]["overlayDtboSha256"] != compatibility["entries"][1]["overlayDtboSha256"]
    serialized = json.dumps(compatibility)
    for stale in ("1.0.1", "phase4d", "uapiAbi\": 1"):
        assert stale not in serialized
    qualification_root = root / "qualification"
    qualification_root.mkdir()
    (qualification_root / "scripts").mkdir()
    (qualification_root / "scripts/release_candidate_target.py").write_text("# fixture\n")
    (qualification_root / "scripts/inspect_rebooted_route.py").write_text("# fixture\n")
    (qualification_root / "scripts/release_candidate_transaction.py").write_text("# fixture\n")
    (qualification_root / "scripts/release_candidate_controls.py").write_text("# fixture\n")
    (qualification_root / "scripts/validate_release_candidate.py").write_text("# fixture\n")
    (qualification_root / "PRODUCT-INVENTORY.json").write_bytes(inventory_bytes)
    (qualification_root / "QUALIFICATION.json").write_bytes(identity_bytes)
    (qualification_root / "TARGET-VERIFICATION.json").write_bytes(builder.pretty(plan))
    controls.validate(qualification_root)
    assert plan["authorized"] is False and plan["executed"] is False
    assert set(plan["physicalSafety"].values()) == {"fresh-operator-confirmation-required"}
    assert all(not step["mutating"] or step["requiresAuthorization"] for step in plan["steps"])
    assert plan["safety"]["bootChange"] is True and plan["safety"]["reboot"] is True
    assert all(plan["safety"][field] is False for field in
               ("liveOutput", "endpointAcquire", "clockOrRateChange", "dma",
                "gpioOutput", "carrier", "sdrCapture", "transmissionOrRf"))
    invoked = {arg for step in plan["steps"] for arg in step.get("argv", [])
               if arg.startswith("scripts/")}
    layout = json.loads((ROOT / "release/qualification-layout-v3.json").read_text())
    assert invoked <= set(layout["sourceMembers"])
    transfer = next(step for step in plan["steps"] if step["id"] == "validated-transfer")
    assert transfer["argv"] == [
        "/usr/bin/env",
        "--chdir=/home/pi/rp1-gpclk-v1.1.1-owned-service-executor-20260822/release-set",
        "/usr/bin/sha256sum", "--check", "SHA256SUMS",
    ]

    bad = bytearray(product.read_bytes())
    bad[0] = 0
    with tempfile.NamedTemporaryFile() as corrupted:
        corrupted.write(bad)
        corrupted.flush()
        try:
            builder.validate_product(Path(corrupted.name))
        except ValueError:
            pass
        else:
            raise AssertionError("corrupted Debian archive accepted")

target_source = (ROOT / "scripts/release_candidate_target.py").read_text()
assert "live_output=0" in target_source
assert "live_output=1" not in target_source
assert 'choices=("gpio4", "gpio20")' in target_source
assert "/dev/mem" not in target_source
assert "applied.stdout" not in target_source
assert "if len(residual) == 1 and len(matches) == 1" in target_source

route_inspector = (ROOT / "scripts/inspect_rebooted_route.py").read_text()
for token in ("/dev/rp1-gpclk", "/dev/rp1-gpclk0", "wsprrypi,route",
              "wsprrypi,pin", "/sys/bus/platform/devices", "live output is not disabled"):
    assert token in route_inspector
for prohibited in ("live_output=1", "dtoverlay", "/sbin/reboot", "/dev/mem"):
    assert prohibited not in route_inspector


def exercise_overlay_capture(apply_stdout: str) -> None:
    outputs = iter(("No overlays loaded\n", apply_stdout, "Overlays (in load order):\n7:  rp1-gpclk-gpio4\n"))
    calls = []
    original = target.command

    def fake_command(argv, check=True):
        calls.append(argv)
        return SimpleNamespace(stdout=next(outputs), returncode=0)

    target.command = fake_command
    try:
        assert target.apply_overlay("gpio4") == "7"
    finally:
        target.command = original
    assert calls[0][-1] == "-l"
    assert calls[1][-1] == "rp1-gpclk-gpio4"
    assert calls[2][-1] == "-l"


exercise_overlay_capture("")
exercise_overlay_capture("7\n")
original = target.command
ambiguous = iter(("No overlays loaded\n", "", "0: rp1-gpclk-gpio4\n1: rp1-gpclk-gpio20\n"))
target.command = lambda argv, check=True: SimpleNamespace(stdout=next(ambiguous), returncode=0)
try:
    target.apply_overlay("gpio4")
except RuntimeError:
    pass
else:
    raise AssertionError("ambiguous overlay delta accepted")
finally:
    target.command = original

containerfile = (ROOT / "tools/release-builder.Containerfile").read_text()
assert "FROM docker.io/library/debian@sha256:c94f5ddd41327aa2d4a7cfba7889056c02936182fd76a513fec6160c97181fc0" in containerfile
for package in ("build-essential", "debhelper", "dh-dkms", "device-tree-compiler", "python3"):
    assert package in containerfile

def git_mode(path: str) -> str:
    return subprocess.check_output(
        ["git", "ls-files", "--stage", "--", path], cwd=ROOT, text=True
    ).split()[0]


assert git_mode("scripts/build_release_candidate.py") == "100755"
assert git_mode("scripts/validate_release_candidate.py") == "100755"
assert git_mode("scripts/inspect_rebooted_route.py") == "100755"
assert git_mode("scripts/release_candidate_transaction.py") == "100755"
print("Release candidate builder and target-plan contract: PASS")
