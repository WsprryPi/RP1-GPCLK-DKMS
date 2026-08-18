#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.52 attempt-3 boot-operation failure."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=(ROOT/'docs/contracts/gate-d-phase5.52-attempt3-prior-kernel-downgrade-gpio4-prompt.md').read_text()
v=json.loads((ROOT/'docs/evidence/gate-d-phase5.52-attempt3-prior-kernel-downgrade-gpio4-failure-attestation.json').read_text())
assert '/usr/libexec/rp1-gpclk-dkms/gate-d-executor' in p and '--resume --execute' in p
assert v['attempt']=={'indexEntry':3,'operationId':'gd-prior-supported-kernel-downgrade-gpio4','documentSha256':'37d60b9903eb224e3654786c3181fbbfa3e925b0544763bc7ff0ede34ffd29b1','indexSha256':'744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8','executorPath':'/usr/libexec/rp1-gpclk-dkms/gate-d-executor','executorSha256':'70f845be52c2cc7993a53aa2d7e7258319e261854903fd7a2c6d5dce29fa4061'}
r=v['result'];assert r['status']=='inactive-recovery-required' and r['failedStepId']=='07-select-prior-kernel' and r['failureMessage']=='boot operation must be a real file' and r['sealed'] is True
b=v['mutationBoundary'];assert b['completedOperations']==['create-evidence','capture-preflight','verify-input-hashes','snapshot-services','quiesce-services','stage-source'];assert b['servicesRestoredByCompensation'] is True and b['stagedSourcePresent'] is True and b['bootSelectionCommitted'] is False and b['rebootStarted'] is False
assert all(v['postState'][k] is False for k in ['moduleLoaded','endpointPresent','overlayActive','candidateDkmsTestVersionPresent','predecessorDkmsTestVersionPresent'])
assert v['postState']['allSixServicesInactive'] is True and v['postState']['outputDisabled'] is True
assert v['recovery']=={'journalReportsRecoveryRequired':True,'sameOperationResumeViable':False,'recoveryInvoked':False,'evidenceAndStagingPreserved':True,'successorControlSetRequired':True}
print('Phase 5.52 attempt 3 sealed boot-operation failure: PASS')
