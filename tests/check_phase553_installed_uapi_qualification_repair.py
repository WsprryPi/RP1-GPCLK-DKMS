#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the installed-product-UAPI qualification repair evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-installed-uapi-qualification-repair.json").read_text())
assert value["kind"] == "phase5.53-installed-uapi-qualification-repair"
assert value["productArchiveSha256"] == "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["qualificationSourceCommit"] == "1ccf73ebd350af461d4a2d8e3d4ed48cb70356f0"
assert value["qualificationArchiveSha256"] == "71b53f8f5a015e042bd6c771f20db45a21fb3182e9b2ffa31d49e7eb427ec2a6"
assert value["generation"] == {"count": 2, "byteIdentical": True,
    "independentValidationCount": 2, "productArchiveRetainedByteIdentical": True}
contract = value["installedPathContract"]
assert contract["uapi"] == "/usr/src/rp1-gpclk-dkms-0.0.0-phase5.53/include/uapi/linux/rp1_gpclk.h"
assert contract["globalHeaderInjectedByTest"] is False
assert contract["literalProductArchiveInstalledPathExercise"] == "passed"
assert contract["missingProductUapiFailsClosed"] is True
assert value["offlineChecksTwiceRequired"] is True
assert value["targetContactDuringRepair"] is False
assert value["targetMutationDuringRepair"] is False
assert value["hardwareOrRfActivityPerformed"] is False
print("Phase 5.53 installed-product-UAPI qualification repair: PASS")
