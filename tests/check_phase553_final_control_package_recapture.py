#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final control-package recapture and construction blocker."""
import hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
snapshot_path=ROOT/"docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-final-v1.json"
snapshot=json.loads(snapshot_path.read_text())
evidence=json.loads((ROOT/"docs/evidence/phase5.53-final-control-package-recapture.json").read_text())
blocker=json.loads((ROOT/"docs/evidence/phase5.53-final-control-package-construction-blocker.json").read_text())
spec=importlib.util.spec_from_file_location("owned_snapshot_validator",ROOT/"scripts/gate_d_live_snapshot_owned_validate.py"); assert spec and spec.loader
validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
assert hashlib.sha256(snapshot_path.read_bytes()).hexdigest()==evidence["snapshotSha256"]=="cbaed5a7972bb317a9dc27cabead9419ffde2db474df4de493373b6aa474524f"
assert evidence["captures"]==2 and evidence["byteIdentical"] is True
assert evidence["installedLedgerSha256"]==snapshot["administratorLedger"]["sha256"]=="d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d"
assert len(snapshot["packagePaths"])==evidence["packagePaths"]==72
assert snapshot["packagePathsSha256"]==evidence["packagePathsSha256"]
assert snapshot["runtime"]=={"dkmsTestVersions":True,"endpointPresent":False,"liveOutput":False,"moduleLoaded":False,"overlayActive":False}
assert validator.validate(snapshot)["valid"] is True
assert set(snapshot["services"].values())=={"inactive"}
assert blocker["disposition"]=="no controls generated"
assert blocker["authorizationConsumed"] is False
assert blocker["snapshotSha256"]==evidence["snapshotSha256"]
assert "same-version" in blocker["requiredSuccessor"]
print("Phase 5.53 final control-package recapture and blocker: PASS")
