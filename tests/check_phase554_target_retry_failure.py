#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.54-target-install-retry-failure.json").read_text())

assert value["kind"] == "phase5.54-target-install-retry-failure-evidence"
assert value["orphanRecovery"]["packageRetryAttempts"] == 1
assert value["packageState"]["status"] == "install ok half-configured"
assert value["dkmsResults"]["6.18.34+rpt-rpi-2712"] == "installed"
assert value["dkmsResults"]["6.18.44-v8-16k+"] == "build-failed"
assert value["rootCause"]["failedKernelClass"] == "historical custom 16K development kernel"
assert value["rootCause"]["conflictingUapiSha256"] != value["rootCause"]["candidateUapiSha256"]
assert value["safety"]["moduleLoaded"] is False
assert value["safety"]["additionalRetryOrRepairPerformed"] is False
print("Phase 5.54 target retry failure: PASS")
