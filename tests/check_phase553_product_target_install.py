#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
value = json.loads((root / "docs/evidence/phase5.53-product-only-target-install-attestation.json").read_text())
assert value["status"] == "complete"
assert value["productArchiveSha256"] == "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["successorLedgerSha256"] == "d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d"
assert value["successorClosureSha256"] == "414653b869feb38b8151a68c808d5fc7d8d4693410692078f59670d4a9aa0d5e"
for field in ("qualificationArchiveTransferred", "qualificationToolsInstalled",
              "moduleLoaded", "endpointPresent", "overlayApplied",
              "bootConfigurationChanged", "rebootPerformed",
              "transferResiduePresent", "gpioClockDmaActivityPerformed",
              "transmissionOrRfPerformed"):
    assert value[field] is False
assert value["ownedFiles"] == 72 and value["controlledServicesActive"] == 0
print("Phase 5.53 product-only target installation: PASS")
