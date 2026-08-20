#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION = "1.0.0"

rules = (ROOT / "debian/rules").read_text()
control = (ROOT / "debian/control").read_text()
dkms = (ROOT / "dkms.conf").read_text()
header = (ROOT / "include/rp1_gpclk/version.h").read_text()
guide = (ROOT / "docs/operator/debian-packaging.md").read_text()
postinst = (ROOT / "debian/rp1-gpclk-dkms.postinst").read_text()
prerm = (ROOT / "debian/rp1-gpclk-dkms.prerm").read_text()

assert "Package: rp1-gpclk-dkms" in control
assert "Architecture: all" in control
assert "dh-dkms" in control and "device-tree-compiler" in control
assert "dh $@ --with dkms" in rules
assert f"MODULE_VERSION := {VERSION}" in rules
assert 'PACKAGE_VERSION="#MODULE_VERSION#"' in dkms
exclusive = 'BUILD_EXCLUSIVE_KERNEL="^[0-9]+[.][0-9]+[.][0-9]+[+]rpt-rpi-(2712|v8)$"'
assert exclusive in dkms
assert f'RP1_GPCLK_MODULE_VERSION "{VERSION}"' in header
assert "rp1-gpclk-gpio4.dtbo" in rules and "rp1-gpclk-gpio20.dtbo" in rules
assert "rp1-gpclk-gpio4.dts" in rules and "rp1-gpclk-gpio20.dts" in rules
assert "/usr/lib/$(PACKAGE)/overlays" in rules
assert "/boot/firmware" not in rules
assert "cmp -s" in postinst and "mv -f" in postinst
assert "refusing to replace unrecognized" in postinst
assert "cmp -s" in prerm and "rm -f" in prerm
assert "config.txt" not in rules and "dtoverlay" not in rules and "modprobe" not in rules
assert "qualification" not in rules.lower()
assert "Qualification tools" in guide
assert "standard exit-77 exclusion" in guide

installed_source = {
    "Kbuild", "Makefile", "dkms.conf", "src/rp1_gpclk_main.c",
    "include/rp1_gpclk/version.h", "include/uapi/linux/rp1_gpclk.h",
}
for member in installed_source:
    if member == "dkms.conf":
        continue
    assert re.search(r"\b" + re.escape(member.split("/")[0]), rules)

print("Debian DKMS packaging contract: PASS")
