#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Executable consumer for a sealed same-version qualification plan."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess

import gate_d_same_version


def atomic_json(path: pathlib.Path, value: dict) -> None:
    if path.is_symlink():
        raise ValueError("same-version journal is symlinked")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)
    path.chmod(0o600)


def load_real_json(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("same-version input must be a real file")
    return json.loads(path.read_text(encoding="utf-8"))


def command(argv: list[str]) -> None:
    subprocess.run(argv, check=True, stdin=subprocess.DEVNULL,
                   env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})


def probe(argv: list[str]) -> dict:
    output = subprocess.check_output(argv, stdin=subprocess.DEVNULL, text=True,
                                     env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
    value = json.loads(output)
    if not isinstance(value, dict):
        raise ValueError("same-version probe output differs")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "execute", "recover"))
    parser.add_argument("plan", type=pathlib.Path)
    parser.add_argument("journal", type=pathlib.Path)
    args = parser.parse_args()
    plan = gate_d_same_version.validate(load_real_json(args.plan))
    if args.action == "validate":
        print(json.dumps({"valid": True, "readOnly": True, "outputDisabled": True}, sort_keys=True))
        return
    if args.journal.is_symlink():
        raise ValueError("same-version journal is symlinked")
    if args.action == "execute":
        if args.journal.exists():
            raise ValueError("same-version journal already exists")
        result = gate_d_same_version.execute(
            plan, run=command, probe=lambda: probe(plan["probeArgv"]),
            record=lambda value: atomic_json(args.journal, value))
    else:
        state = load_real_json(args.journal)
        result = gate_d_same_version.recover(
            plan, state, run=command, probe=lambda: probe(plan["probeArgv"]),
            record=lambda value: atomic_json(args.journal, value))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
