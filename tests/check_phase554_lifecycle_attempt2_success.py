#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads(
    (ROOT / "docs/evidence/phase5.54-lifecycle-attempt2-success.json").read_text()
)

assert value["attempt"] == 2 and value["route"] == "gpio20"
assert value["preflight"]["softwareStateMatched"] is True
assert value["preflight"]["gpio4EvidencePresent"] is True
assert value["preflight"]["si5351DisconnectedConfirmedByOperator"] is True
assert value["preflight"]["antennaOrTransmitterConnectedToGpio20ConfirmedByOperator"] is False
assert value["execution"]["attemptCount"] == 1
assert value["execution"]["moduleParameter"] == "live_output=0"
assert value["execution"]["observedLiveOutput"] == "N"
assert value["execution"]["uapiRoute"] == "gpio20"
assert value["execution"]["uapiLiveEligible"] is False
assert value["execution"]["uapiLeaseReleased"] is True
assert value["terminal"]["stockDkmsInstallCount"] == 4
assert value["terminal"]["moduleLoaded"] is False
assert value["terminal"]["endpointPresent"] is False
assert value["terminal"]["activeOverlayCount"] == 0
assert value["terminal"]["bootSelectionCount"] == 0
assert all(value["cleanup"].values())
assert not any(value["safety"].values())
assert value["result"] == "pass-inactive-baseline-restored"

print("Phase 5.54 lifecycle attempt 2: PASS")
