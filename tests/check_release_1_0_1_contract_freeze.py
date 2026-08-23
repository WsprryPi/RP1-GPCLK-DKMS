#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
freeze = json.loads((ROOT / "release/uapi-contract-freeze-v1.0.1.json").read_text())
schema = json.loads((ROOT / "schema/rp1-gpclk-uapi-contract-freeze-v1.schema.json").read_text())
header = ROOT / "release/uapi/rp1_gpclk-v1.0.1.h"

assert schema["$id"].endswith("rp1-gpclk-uapi-contract-freeze-v1.schema.json")
assert freeze["release"] == freeze["dkmsVersion"] == freeze["moduleVersion"] == "1.0.1"
assert freeze["debianVersion"] == "1.0.1-1"
assert freeze["expectedTag"] == "v1.0.1"
assert freeze["endpoint"]["path"] == "/dev/rp1-gpclk"
assert freeze["uapi"]["abi"] == 1
assert hashlib.sha256(header.read_bytes()).hexdigest() == freeze["uapi"]["sha256"]

assert [(c["name"], c["number"], c["direction"], c["size"]) for c in freeze["uapi"]["commands"]] == [
    ("QUERY", 0x20, "read-write", 304),
    ("ACQUIRE", 0x21, "read-write", 64),
    ("SUBMIT_WSPR", 0x22, "read-write", 112),
    ("SUBMIT_EVENTS", 0x23, "read-write", 112),
    ("STOP", 0x24, "write", 56),
    ("GET_STATE", 0x25, "read-write", 88),
    ("RELEASE", 0x26, "write", 48),
]
assert [(r["name"], r["value"], r["pin"]) for r in freeze["routes"]] == [
    ("GPIO4", 1, 4), ("GPIO20", 2, 20)
]
assert [(m["name"], m["value"]) for m in freeze["modes"]] == [
    ("WSPR", 1), ("QRSS", 2), ("FSKCW", 3), ("DFCW", 4)
]

main = (ROOT / "src/rp1_gpclk_main.c").read_text()
dispatch = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text()
contract = (ROOT / "docs/contracts/rp1-gpclk-dkms-module-contract.md").read_text()
assert 'device->miscdev.name = "rp1-gpclk";' in main
assert "/dev/rp1-gpclk0" not in main
assert "rp1_gpclk_route_candidate_allowed" in main
assert 'of_machine_is_compatible("raspberrypi,5-model-b")' in main
assert dispatch.count("return -EACCES;") >= 2
assert "normative UAPI and endpoint freeze" in contract
assert "Changing the endpoint or canonical UAPI reopens the freeze" in contract
assert "Final documentation freeze remains pending" in contract

for path in (
    "release/release-layout-v1.json",
    "release/qualification-layout-v1.json",
    "release/qualification-layout-v2.json",
    "release/installation-model-v1.json",
    "release/lifecycle-removal-contract-v1.json",
):
    document = json.loads((ROOT / path).read_text())
    assert document["release"] == "1.0.1", path

layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
canonical = next(item for item in layout["artifacts"] if item["id"] == "canonical-uapi")
assert canonical["destination"] == (
    "/usr/src/rp1-gpclk-dkms-1.0.1/include/uapi/linux/rp1_gpclk.h"
)
assert not any(item["destination"].startswith("/usr/include/") for item in layout["artifacts"])

assert "rp1-gpclk-dkms (1.0.1-1) UNRELEASED" in (ROOT / "debian/changelog").read_text()
rules = (ROOT / "debian/rules").read_text()
assert "include/uapi/linux/rp1_gpclk.h" in rules
assert "SOURCE_DEST := debian/$(PACKAGE)/usr/src/$(PACKAGE)-$(MODULE_VERSION)" in rules
assert freeze["packaging"]["canonicalHeaderInPackage"] == (
    "/usr/src/rp1-gpclk-dkms-1.0.1/include/uapi/linux/rp1_gpclk.h"
)
assert freeze["compatibility"]["positiveEntryRequired"] is True
assert freeze["compatibility"]["liveOutputModuleParameterRequired"] is True
assert freeze["compatibility"]["submissionWithoutBothGates"] == "EACCES"

print("1.0.1 normative contract freeze: PASS")
