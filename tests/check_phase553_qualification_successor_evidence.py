#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate qualification-only successor construction evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
value=json.loads((ROOT/"docs/evidence/phase5.53-qualification-successor-construction.json").read_text())
assert value["kind"]=="qualification-only-successor-construction"
assert value["frozenProduct"]=={"sourceCommit":"1884c0f1c53c661495576bf10ce08d8bf7a90bc3","archive":"rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz","sha256":"ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549","regenerated":False,"copiedByteIdentical":True}
successor=value["qualificationSuccessor"]
assert successor["sourceCommit"]=="834d05c5c5da0c383c4a229eaeff9dae07a4359b"
assert successor["sha256"]=="d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0"
assert successor["members"]==28 and successor["generations"]==2 and successor["byteIdentical"] is True and successor["independentValidationsPassed"]==2
assert value["validation"]["productByteInputClosure"]=="unchanged"
assert value["disposition"]=="qualification-successor-ready-for-control-set-construction"
assert "remains blocked" in value["claimCeiling"]
print("Phase 5.53 qualification successor evidence: PASS")
