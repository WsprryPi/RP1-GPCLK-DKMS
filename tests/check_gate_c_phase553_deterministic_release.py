#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-c-phase5.53-deterministic-release-generation.json").read_text())
assert value["release"] == "0.0.0-phase5.53"
assert value["sourceCommit"] == "d7099814e2021a7b206dc68517be542aa94fb162"
assert value["builds"] == {
    "count": 2,
    "independentDetachedWorktrees": True,
    "byteIdentical": True,
    "regularFileCount": 7,
}
assert value["artifacts"]["rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz"] == \
    "d5799c29eeaf6594c91620d76028112a4a3af6518f17b57efdfaf7283c129a8c"
assert value["archiveInspection"]["unsafeDuplicateLinkSpecialOrForbiddenMemberCount"] == 0
assert value["archiveInspection"]["extendedAttributeResourceForkOrAclHeaderCount"] == 0
assert {item["result"] for item in value["archivedRegressions"].values()} == {"failed"}
assert value["candidatePromoted"] is False
assert value["targetAccessPerformed"] is False
assert value["hardwareOrSystemMutationPerformed"] is False
print("Phase 5.53 deterministic release evidence: PASS (candidate correctly blocked)")
