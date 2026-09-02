#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require every standalone Python check to be registered or classified."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
RUNNERS = (
    (ROOT / "tests/run-offline-checks.sh").read_text(encoding="utf-8"),
    (ROOT / "Makefile").read_text(encoding="utf-8"),
)

# This validator requires an externally supplied module and kernel identity.
PARAMETERIZED_UTILITIES = {"check_built_module.py"}
TARGET_ONLY_C_CLIENTS = {"development_fault_client.c",
                         "development_tone_client.c"}
TARGET_ONLY_CPP_CLIENTS = {"development_frequency_sweep.cpp"}

checks = {path.name for path in TESTS.glob("check_*.py")}
registered = {
    name for name in checks
    if any(name in runner for runner in RUNNERS)
}
unclassified = checks - registered - PARAMETERIZED_UTILITIES
missing_utilities = PARAMETERIZED_UTILITIES - checks

if unclassified:
    raise SystemExit(f"unregistered standalone checks: {sorted(unclassified)}")
if missing_utilities:
    raise SystemExit(f"classified utilities are missing: {sorted(missing_utilities)}")

c_tests = {path.name for path in TESTS.glob("*.c")}
registered_c = {name for name in c_tests if name in RUNNERS[0]}
unclassified_c = c_tests - registered_c - TARGET_ONLY_C_CLIENTS
missing_clients = TARGET_ONLY_C_CLIENTS - c_tests
if unclassified_c:
    raise SystemExit(f"unregistered C tests: {sorted(unclassified_c)}")
if missing_clients:
    raise SystemExit(f"classified target clients are missing: {sorted(missing_clients)}")

cpp_clients = {path.name for path in TESTS.glob("*.cpp")}
unclassified_cpp = cpp_clients - TARGET_ONLY_CPP_CLIENTS
missing_cpp_clients = TARGET_ONLY_CPP_CLIENTS - cpp_clients
if unclassified_cpp:
    raise SystemExit(f"unregistered C++ tests: {sorted(unclassified_cpp)}")
if missing_cpp_clients:
    raise SystemExit(f"classified C++ clients are missing: {sorted(missing_cpp_clients)}")

print(f"test inventory: PASS ({len(registered)} registered, "
      f"{len(PARAMETERIZED_UTILITIES)} parameterized utility, "
      f"{len(registered_c)} host C tests, {len(TARGET_ONLY_C_CLIENTS)} target C client, "
      f"{len(TARGET_ONLY_CPP_CLIENTS)} target C++ client)")
