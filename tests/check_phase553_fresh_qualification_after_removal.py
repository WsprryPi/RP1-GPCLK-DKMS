#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate fresh-after-removal qualification evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
value=json.loads((ROOT/"docs/evidence/phase5.53-fresh-qualification-after-removal.json").read_text())
assert value["kind"]=="phase5.53-fresh-qualification-after-removal"
assert value["qualificationSourceCommit"]=="e1ed88b40f63e72960ae610747b2ada913687895"
assert value["qualificationArchiveSha256"]=="c72ba1293815698d96a6045c7cf5a3c2f6c31302a88727cbc3d91e280c3b25b6"
assert value["qualificationIdentitySchema"]==4
assert value["generations"]==2 and value["byteIdentical"] is True
assert value["independentValidationsPassed"]==2
assert set(value["fakeSystem"].values())=={"passed",False}
assert value["authorization"]=={"approved":False,"targetExecutionApproved":False,"executionReady":False}
print("Phase 5.53 fresh qualification after removal: PASS")
