#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import io
import json
from pathlib import Path
import stat
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_release_candidate as builder
from scripts import release_candidate_controls as controls


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
    product = root / "rp1-gpclk-dkms_1.0.0-1_all.deb"
    control = tar_xz({
        "control": b"Package: rp1-gpclk-dkms\nVersion: 1.0.0-1\nArchitecture: all\n",
        "md5sums": b"",
    })
    base = "usr/src/rp1-gpclk-dkms-1.0.0"
    data_files = {
        f"{base}/dkms.conf": b'PACKAGE_NAME="rp1-gpclk-dkms"\nPACKAGE_VERSION="1.0.0"\n',
        f"{base}/Kbuild": b"obj-m += rp1_gpclk_dkms.o\n",
        f"{base}/Makefile": b"all:\n\t@true\n",
        f"{base}/include/uapi/linux/rp1_gpclk.h": b"uapi\n",
        f"{base}/overlays/rp1-gpclk-gpio4.dts": b"gpio4\n",
        f"{base}/overlays/rp1-gpclk-gpio20.dts": b"gpio20\n",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo": b"dtbo4\n",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo": b"dtbo20\n",
        "usr/share/doc/rp1-gpclk-dkms/copyright": b"MIT\n",
    }
    product.write_bytes(
        b"!<arch>\n"
        + ar_member("debian-binary", b"2.0\n")
        + ar_member("control.tar.xz", control)
        + ar_member("data.tar.xz", tar_xz(data_files))
    )
    inventory, extracted = builder.validate_product(product)
    assert inventory["debianVersion"] == "1.0.0-1"
    assert inventory["packageSha256"] == builder.sha256(product)
    assert set(data_files) <= set(extracted)
    inventory_bytes = builder.pretty(inventory)
    identity = {
        "release": "1.0.0", "expectedTag": "v1.0.0",
        "productPackageSha256": inventory["packageSha256"],
    }
    identity_bytes = builder.pretty(identity)
    plan = builder.target_plan(
        inventory["packageSha256"], builder.sha256_bytes(inventory_bytes),
        builder.sha256_bytes(identity_bytes), builder.sha256_bytes(b"uapi\n"),
        builder.sha256_bytes(b"dtbo4\n"), builder.sha256_bytes(b"dtbo20\n"),
    )
    qualification_root = root / "qualification"
    qualification_root.mkdir()
    (qualification_root / "scripts").mkdir()
    (qualification_root / "scripts/release_candidate_target.py").write_text("# fixture\n")
    (qualification_root / "PRODUCT-INVENTORY.json").write_bytes(inventory_bytes)
    (qualification_root / "QUALIFICATION.json").write_bytes(identity_bytes)
    (qualification_root / "TARGET-VERIFICATION.json").write_bytes(builder.pretty(plan))
    controls.validate(qualification_root)
    assert plan["authorized"] is False and plan["executed"] is False
    assert all(not step["mutating"] or step["requiresAuthorization"] for step in plan["steps"])
    invoked = {arg for step in plan["steps"] for arg in step["argv"] if arg.startswith("scripts/")}
    layout = json.loads((ROOT / "release/qualification-layout-v2.json").read_text())
    assert invoked <= set(layout["sourceMembers"])

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

containerfile = (ROOT / "tools/release-builder.Containerfile").read_text()
assert "FROM docker.io/library/debian@sha256:c94f5ddd41327aa2d4a7cfba7889056c02936182fd76a513fec6160c97181fc0" in containerfile
for package in ("build-essential", "debhelper", "dh-dkms", "device-tree-compiler", "python3"):
    assert package in containerfile

assert stat.S_IMODE((ROOT / "scripts/build_release_candidate.py").stat().st_mode) in {0o644, 0o755}
print("Release candidate builder and target-plan contract: PASS")
