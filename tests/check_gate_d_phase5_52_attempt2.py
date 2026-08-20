#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.52 attempt 2 GPIO20 evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prompt=(ROOT/'docs/contracts/gate-d-phase5.52-attempt2-current-kernel-gpio20-prompt.md').read_text()
v=json.loads((ROOT/'docs/evidence/gate-d-phase5.52-attempt2-current-kernel-gpio20-attestation.json').read_text())
permanent='/usr/libexec/rp1-gpclk-dkms/gate-d-executor'
assert permanent in prompt and 'SourceFileLoader' in prompt
assert v['attempt']=={'ordinal':2,'operationId':'gd-current-supported-kernel-gpio20','documentSha256':'e3eff89826a8aadf0ae8f16d907cb439fd37717b4bef06705ae2f1fb796ce70c','indexSha256':'744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8','executorPath':permanent,'executorSha256':'70f845be52c2cc7993a53aa2d7e7258319e261854903fd7a2c6d5dce29fa4061'}
assert v['preflight']['installedExecutorCliValidation']=='passed'
assert v['preflight']['installedExecutorCliPlan']=='passed'
assert v['preflight']['phase552ForbiddenPathCount']==0
assert v['result']=={'status':'complete','sealed':True,'recoveryRequired':False,'recordCount':20,'nextStep':20,'completedUtc':'2026-08-18T11:08:18.704463Z','liveOutput':False,'journalSha256':'4abe76ce12cc5091c3b38fff5128efd09dd61978dcc6afd0728ce9ffdef862a1','evidenceSha256SumsSha256':'feee25aad736e9f4c5d31f00b63df435742d14c3bdafd00b1cfac6b4633ad1d4'}
assert v['uapiResult']=='route=gpio20 build=0.0.0-phase5.52 live_eligible=0 released=1'
assert v['evidenceFiles']==sorted(v['evidenceFiles']) and len(v['evidenceFiles'])==7
assert v['postState']['outputDisabled'] is True
assert v['postState']['historicalNamespacesExcludedFromMutation'] is True
print('Phase 5.52 attempt 2 current-kernel GPIO20: PASS')
