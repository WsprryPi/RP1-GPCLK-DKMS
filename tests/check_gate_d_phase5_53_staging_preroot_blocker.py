#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the fail-closed Phase 5.53 split pre-root path blocker."""
import hashlib, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
evidence=json.loads((ROOT/'docs/evidence/gate-d-phase5.53-staging-preroot-blocker.json').read_text())
old_envelope_bytes=subprocess.check_output(['git','show','2d1a5c3e5ca2388679423aa4f2f0f07a56c2d830:release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'],cwd=ROOT)
envelope=json.loads(old_envelope_bytes)
assert evidence['kind']=='gate-d-staging-preroot-blocker'
assert hashlib.sha256(old_envelope_bytes).hexdigest()==evidence['envelopeSha256']
assert evidence['recapture']=={'count':2,'size':7083,'sha256':'df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7','byteIdentical':True,'canonicalByteComparison':'identical'}
assert evidence['transport']['inputCount']==len(envelope['inputFiles'])==64
assert evidence['transport']['productArchiveRegularMemberCount']==54
assert evidence['transport']['qualificationArchiveRegularMemberCount']==28
assert evidence['transport']['stagedRegularFileCount']==118
product_prefix='rp1-gpclk-dkms-0.0.0-phase5.53/'
input_paths={item['path'] for item in envelope['inputFiles']}
stage='/home/pi/gate-d-inputs/phase5.53-1884c0f1c53c/'
for field,name in (('stagedExecutor','gate_d_outer.py'),('preRootModule','gate_d_preroot.py')):
    path=envelope[field]['path']
    assert path==stage+'extracted/'+product_prefix+'scripts/'+name
    assert path not in input_paths
    assert stage+'control-set/scripts/'+name in input_paths
assert envelope['administrator']['path']==stage+'extracted/'+product_prefix+'scripts/rp1-gpclk-admin.py'
assert envelope['administrator']['path'] in input_paths
assert evidence['failure']['executorInvoked'] is False
assert evidence['failure']['administratorInvoked'] is False
assert evidence['failure']['preRootTransitionStarted'] is False
assert evidence['failure']['lifecycleAttemptStarted'] is False
assert all(evidence['cleanup'][key] for key in ('transientStagingRemoved','qualificationRootAbsent','preRootJournalAbsent','attemptNamespaceAbsent','inactiveBaselinePreserved'))
assert evidence['cleanup']['liveOutput'] is False
assert evidence['disposition']=='blocked-fail-closed'
repaired=json.loads((ROOT/'release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json').read_text())
assert repaired['stagedExecutor']['path']==stage+'control-set/scripts/gate_d_outer.py'
assert repaired['preRootModule']['path']==stage+'control-set/scripts/gate_d_preroot.py'
print('Phase 5.53 split pre-root path blocker: PASS')
