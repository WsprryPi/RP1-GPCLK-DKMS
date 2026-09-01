#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION = "0.9.0"

rules = (ROOT / "debian/rules").read_text()
control = (ROOT / "debian/control").read_text()
dkms = (ROOT / "dkms.conf").read_text()
header = (ROOT / "include/rp1_gpclk/version.h").read_text()
guide = (ROOT / "docs/operator/debian-packaging.md").read_text()
postinst = (ROOT / "debian/rp1-gpclk-dkms.postinst").read_text()
prerm = (ROOT / "debian/rp1-gpclk-dkms.prerm").read_text()

assert "Package: rp1-gpclk-dkms" in control
assert "Architecture: all" in control
for build_dependency in (
    "debhelper-compat (= 13)", "dh-dkms", "device-tree-compiler", "python3"
):
    assert build_dependency in control
assert re.search(r"Depends:\s+dkms,", control)
assert "linux-headers-arm64" not in control
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
assert "scripts/rp1-gpclk-route-manager.py" in rules
assert "usr/sbin/rp1-gpclk-route-manager" in rules
assert "rp1-gpclk-route-manager-v1.schema.json" in rules
assert "route-manager-v1.md" in rules
assert "rp1-gpclk-route-manager.socket" in rules
assert "rp1-gpclk-route-manager@.service" in rules
assert "dh_installsystemd --no-enable --no-start" in rules
assert "dh_compress -Xroute-manager-v1.md" in rules
assert "addgroup --system rp1-gpclk-route" in postinst

socket = (ROOT / "systemd/rp1-gpclk-route-manager.socket").read_text()
service = (ROOT / "systemd/rp1-gpclk-route-manager@.service").read_text()
assert "SocketGroup=rp1-gpclk-route" in socket and "SocketMode=0660" in socket
assert "Accept=yes" in socket and "WantedBy=sockets.target" in socket
assert "ExecStart=/usr/sbin/rp1-gpclk-route-manager" in service
assert "StandardInput=socket" in service and "StandardOutput=socket" in service
assert "User=root" in service and "/bin/sh" not in service
assert "ReadWritePaths=/boot/firmware /var/lib/rp1-gpclk-dkms" in service
assert "ReadWritePaths=/boot/firmware/config.txt" not in service
assert "Both overlays remain inactive" in guide
assert "standard exclusion behavior" in guide

installed_source = {
    "Kbuild", "Makefile", "dkms.conf", "src/rp1_gpclk_main.c",
    "include/rp1_gpclk/version.h", "include/uapi/linux/rp1_gpclk.h",
}
for member in installed_source:
    if member == "dkms.conf":
        continue
    assert re.search(r"\b" + re.escape(member.split("/")[0]), rules)

print("Debian DKMS packaging contract: PASS")
