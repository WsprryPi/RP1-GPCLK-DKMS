#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the non-authorizing repaired Phase 5.53 decision prompt."""
import hashlib, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
prompt=(ROOT/'docs/contracts/gate-d-phase5.53-repaired-control-set-authorization-decision-prompt.md').read_text()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
expected={
    'dff45f11720496a983327131972f7d78ca66ff70',
    '2b6dc7e2d81711c2179aec8a73bd5e9d54e9090cd82c1a7195f0272a35ed0890',
    '866c433bbf25ef71953fd79fb7f82ff103be18a62b1af8b4df57daaca9b4b8c2',
    '3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2',
    'd484fe0ff19bdc2de2e1b78c8269f05ac278587b10bf0ca042f4eb9398af9b7c',
    'df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7',
    'ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549',
    'd931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0',
    '17220ae534936e55fc1710edcd8cebff88add93adb82bd607e020714569a175d',
    'c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb',
    'b3ae7d71aa1eb8881450b068f9c3525ecf33925ab797419c735b9f4f5aca18cb',
    'aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c',
}
assert all(value in prompt for value in expected)
instance=json.loads(subprocess.check_output(['git','show','dff45f11720496a983327131972f7d78ca66ff70:release/gate-d-execution-instance-phase5.53-v1.json'],cwd=ROOT))
envelope=json.loads((ROOT/'release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json').read_text())
decision_envelope=subprocess.check_output(['git','show','dff45f11720496a983327131972f7d78ca66ff70:release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'],cwd=ROOT)
assert hashlib.sha256(decision_envelope).hexdigest() in prompt
assert instance['authorization']['approved'] is False
assert instance['authorization']['targetExecutionApproved'] is False
assert instance['executionReady'] is False
inputs={item['path']:item['sha256'] for item in envelope['inputFiles']}
for field in ('stagedExecutor','preRootModule','administrator','qualificationIdentity'):
    item=envelope[field]; assert inputs[item['path']]==item['sha256']
old=subprocess.check_output(['git','show','2d1a5c3e5ca2388679423aa4f2f0f07a56c2d830:release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'],cwd=ROOT)
assert hashlib.sha256(old).hexdigest() in prompt
assert 'This decision prompt is non-authorizing' in prompt
assert 'I do not yet authorize target staging' in prompt
assert 'Stop before target staging' in prompt
print('Phase 5.53 repaired authorization decision prompt: PASS')
