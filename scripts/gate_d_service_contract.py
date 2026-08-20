#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently validate attempt service contracts against a live snapshot."""
from __future__ import annotations

import argparse
import json
import pathlib

SERVICE_NAMES = ("wsprrypi", "sdrplay", "sdrconnect-server", "SoapySDRServer")


def expected_contract(names: list[str], snapshot: dict) -> list[dict]:
    states = snapshot.get("services") if isinstance(snapshot, dict) else None
    if (not isinstance(states, dict) or tuple(names) != SERVICE_NAMES or
            len(names) != len(set(names))):
        raise ValueError("snapshot services or planned names differ")
    result = []
    for name in names:
        state = states.get(f"{name}.service")
        if state not in {"active", "inactive"}:
            raise ValueError(f"snapshot service is missing or unsupported: {name}")
        result.append({
            "action": "stop-then-restore-exact" if state == "active" else "preserve",
            "name": name,
            "requiredPreState": state,
        })
    return result


def validate(snapshot: dict, documents: list[dict]) -> dict:
    if not isinstance(documents, list) or not documents:
        raise ValueError("attempt documents are absent")
    first = documents[0].get("services")
    if not isinstance(first, list) or not first:
        raise ValueError("attempt service contract is absent")
    names = [item.get("name") for item in first if isinstance(item, dict)]
    expected = expected_contract(names, snapshot)
    if first != expected:
        raise ValueError("attempt service contract differs from canonical snapshot")
    for document in documents[1:]:
        if document.get("services") != expected:
            raise ValueError("attempt documents have inconsistent service contracts")
    return {"valid": True, "attemptCount": len(documents),
            "serviceCount": len(expected), "readOnly": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=pathlib.Path)
    parser.add_argument("attempts", type=pathlib.Path, nargs="+")
    args = parser.parse_args()
    load = lambda path: json.loads(path.read_text())
    print(json.dumps(validate(load(args.snapshot), [load(path) for path in args.attempts]),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
