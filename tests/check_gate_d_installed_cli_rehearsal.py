#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rehearse the packaged Gate D CLI path before freezing a successor."""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = (
    "gate_d_root", "gate_d_bootstrap", "gate_d_target_plan",
    "gate_d_lifecycle", "gate_d_outer", "gate_d_attempts",
    "gate_d_instance", "gate_d_preroot",
)


def invoke(executor: pathlib.Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(executor), *arguments], stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )


# Prevent the exact lexical-binding class that escaped the earlier unit tests:
# importing a module-level name anywhere inside main() makes it local throughout
# that function, including branches that execute before the import statement.
tree = ast.parse((ROOT / "scripts/gate_d_outer.py").read_text(encoding="utf-8"))
module_imports: set[str] = set()
main: ast.FunctionDef | None = None
for node in tree.body:
    if isinstance(node, ast.Import):
        module_imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        module_imports.update(alias.asname or alias.name for alias in node.names)
    elif isinstance(node, ast.FunctionDef) and node.name == "main":
        main = node
assert main is not None
shadowing: set[str] = set()
for node in ast.walk(main):
    if isinstance(node, ast.Import):
        shadowing.update((alias.asname or alias.name.split(".")[0]) for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        shadowing.update((alias.asname or alias.name) for alias in node.names)
assert not module_imports.intersection(shadowing), (
    f"main() shadows module imports: {sorted(module_imports.intersection(shadowing))}"
)

index_path = ROOT / "release/gate-d-attempts-v1/index.json"
index = json.loads(index_path.read_text(encoding="utf-8"))
assert index["attemptCount"] == 38 and len(index["attempts"]) == 38

with tempfile.TemporaryDirectory() as temporary:
    installed = pathlib.Path(temporary) / "usr/libexec/rp1-gpclk-dkms"
    installed.mkdir(parents=True)
    for name in MODULES:
        shutil.copy2(ROOT / "scripts" / f"{name}.py", installed / f"{name}.py")
    executor = installed / "gate-d-executor"
    shutil.copy2(ROOT / "scripts/gate_d_outer.py", executor)
    executor.chmod(0o755)

    for record in index["attempts"]:
        document = index_path.parent / record["file"]
        assert hashlib.sha256(document.read_bytes()).hexdigest() == record["sha256"]
        validated = invoke(executor, "validate", str(document))
        assert validated.returncode == 0, (record["operationId"], validated.stderr)
        value = json.loads(validated.stdout)
        assert value == {"operationId": record["operationId"], "readOnly": True, "valid": True}

        planned = invoke(executor, "plan", str(document))
        assert planned.returncode == 0, (record["operationId"], planned.stderr)
        plan = json.loads(planned.stdout)
        assert plan["operationId"] == record["operationId"] and plan["readOnly"] is True
        assert len(plan["actions"]) == len(json.loads(document.read_text())["steps"])

        gated = invoke(executor, "execute", str(document))
        assert gated.returncode != 0
        assert "target execution requires root, --execute, --index, and --instance" in gated.stderr
        assert "Traceback" not in gated.stderr and "UnboundLocalError" not in gated.stderr

print("Gate D installed CLI pre-freeze rehearsal: PASS (38 attempts)")
