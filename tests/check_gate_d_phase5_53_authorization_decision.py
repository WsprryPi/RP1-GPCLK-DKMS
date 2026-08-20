#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.53 decision prompt is exact and non-authorizing."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prompt=(ROOT/"docs/contracts/gate-d-phase5.53-authorization-decision-prompt.md").read_text()
expected={
"2838380a639d7af71ddc53be20829efd56cedc1d","1884c0f1c53c661495576bf10ce08d8bf7a90bc3","ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549","834d05c5c5da0c383c4a229eaeff9dae07a4359b","d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0","df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7","0cb6d2744b20ba5aa412df0702abe230e38b1e407db1c5bd31bfc36c976ac7f1","e9865ebd6208aa4dac1ee60a9b0715936cef1d60b9357b9bdce370343c0087ac","3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2","ef3f074a0e05f78485a9f1e505f302f5fa6adfb900347f2218651cd076effda1","b3ae7d71aa1eb8881450b068f9c3525ecf33925ab797419c735b9f4f5aca18cb","17220ae534936e55fc1710edcd8cebff88add93adb82bd607e020714569a175d","c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb"}
assert all(value in prompt for value in expected)
instance=json.loads(subprocess.check_output([
    "git", "show", "2838380a639d7af71ddc53be20829efd56cedc1d:release/gate-d-execution-instance-phase5.53-v1.json"
],cwd=ROOT))
assert instance["authorization"]["approved"] is False
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
assert "read-only canonical `wspr5`" in prompt and "byte-identical" in prompt
assert "I do not yet" in prompt and "authorize target staging" in prompt
print("Phase 5.53 authorization decision prompt: PASS")
