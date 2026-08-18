#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.52 attempt 1 and permanent-executor boundaries."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prompt=(ROOT/'docs/contracts/gate-d-phase5.52-attempt1-current-kernel-gpio4-prompt.md').read_text()
v=json.loads((ROOT/'docs/evidence/gate-d-phase5.52-attempt1-current-kernel-gpio4-attestation.json').read_text())
permanent='/usr/libexec/rp1-gpclk-dkms/gate-d-executor'
assert permanent in prompt and 'SourceFileLoader' in prompt
assert v['attempt']=={'ordinal':1,'operationId':'gd-current-supported-kernel-gpio4','documentSha256':'30ff96e0a83f667184f922a89f8bb64562f6feb3b74631438fec4e9ec0beb930','indexSha256':'744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8','executorPath':permanent,'executorSha256':'70f845be52c2cc7993a53aa2d7e7258319e261854903fd7a2c6d5dce29fa4061'}
assert v['preflight']['installedExecutorCliValidation']=='passed'
assert v['preflight']['installedExecutorCliPlan']=='passed'
assert v['preflight']['phase552ForbiddenPathCount']==0
assert v['preflight']['historicalNamespacesExcludedFromMutation'] is True
assert v['result']=={'status':'complete','sealed':True,'recoveryRequired':False,'recordCount':20,'nextStep':20,'completedUtc':'2026-08-18T10:55:39.694306Z','liveOutput':False,'journalSha256':'17b35b2e3105dbb12c867009bd335d8c478cbe65bdaea6f7302245c68a89f825','evidenceSha256SumsSha256':'f4daa39bef65c9ac768fd9790fb2dfc89db988a6d9164b04c5ce8624d1799e6c'}
assert v['evidenceFiles']==sorted(v['evidenceFiles']) and len(v['evidenceFiles'])==7
assert v['postState']['outputDisabled'] is True
assert v['postState']['historicalNamespacesExcludedFromMutation'] is True
print('Phase 5.52 attempt 1 current-kernel GPIO4: PASS')
