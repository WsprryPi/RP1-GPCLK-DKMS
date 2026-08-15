#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_outer", ROOT / "scripts/gate_d_outer.py")
assert spec and spec.loader
outer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = outer
spec.loader.exec_module(outer)


def refresh_actions(value):
    dispatcher = outer.ClosedDispatcher(value)
    for item in value["steps"]:
        item["action"] = dispatcher.action(item["operation"]).as_json()

document_path = ROOT / "release/gate-d-attempts-v1/gd-current-supported-kernel-gpio4.json"
document = json.loads(document_path.read_text())
outer.validate_document(document)
plan = outer.ClosedDispatcher(document).plan()
assert len(plan) == len(document["steps"])
assert all(action["kind"] in {"internal", "command", "service-transaction"} for action in plan)
assert all(not any(token in " ".join(action["argv"]).lower()
                       for token in outer.PROHIBITED) for action in plan)

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    (root / "inputs").mkdir()
    for label in ("candidate", "predecessor"):
        archive = root / f"inputs/{label}.tar.gz"
        payload = root / f"{label}.txt"
        payload.write_text(label)
        with tarfile.open(archive, "w:gz") as output:
            output.add(payload, arcname=f"rp1-gpclk-dkms-{label}/README")
        field = "candidate" if label == "candidate" else "predecessor"
        document["inputs"][f"{field}Archive"] = f"/inputs/{label}.tar.gz"
        document["inputs"][f"{field}ArchiveSha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    for route in ("gpio4", "gpio20"):
        dtbo = root / f"inputs/rp1-gpclk-{route}.dtbo"
        dtbo.write_bytes(route.encode())
        document["inputs"][f"{route}Dtbo"] = f"/inputs/rp1-gpclk-{route}.dtbo"
        document["inputs"][f"{route}DtboSha256"] = hashlib.sha256(dtbo.read_bytes()).hexdigest()
    refresh_actions(document)
    fake = outer.FilesystemFake(root, document)
    result = outer.execute(
        document,
        document_sha256=hashlib.sha256(document_path.read_bytes()).hexdigest(),
        index_sha256="1" * 64,
        root=root,
        runner=fake.run,
        internal=fake.internal,
    )
    assert result["status"] == "complete" and result["sealed"] is True
    evidence = outer.rooted(root, document["evidenceDirectory"])
    assert evidence.stat().st_mode & 0o777 == 0o500
    assert outer.rooted(root, document["journal"]).stat().st_mode & 0o777 == 0o400

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    interrupted = copy.deepcopy(document)
    (root / "inputs").mkdir()
    for label in ("candidate", "predecessor"):
        archive = root / f"inputs/{label}.tar.gz"
        payload = root / f"{label}.txt"
        payload.write_text(label)
        with tarfile.open(archive, "w:gz") as output:
            output.add(payload, arcname=f"rp1-gpclk-dkms-{label}/README")
        field = "candidate" if label == "candidate" else "predecessor"
        interrupted["inputs"][f"{field}Archive"] = f"/inputs/{label}.tar.gz"
        interrupted["inputs"][f"{field}ArchiveSha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    for route in ("gpio4", "gpio20"):
        dtbo = root / f"inputs/rp1-gpclk-{route}.dtbo"
        dtbo.write_bytes(route.encode())
        interrupted["inputs"][f"{route}Dtbo"] = f"/inputs/rp1-gpclk-{route}.dtbo"
        interrupted["inputs"][f"{route}DtboSha256"] = hashlib.sha256(dtbo.read_bytes()).hexdigest()
    refresh_actions(interrupted)
    try:
        interrupted_fake = outer.FilesystemFake(root, interrupted)
        outer.execute(interrupted, document_sha256="2" * 64, index_sha256="3" * 64,
                      root=root, runner=interrupted_fake.run, internal=interrupted_fake.internal,
                      stop_after="install-successor")
    except InterruptedError:
        pass
    else:
        raise AssertionError("requested durable interruption was not preserved")
    journal = json.loads(outer.rooted(root, interrupted["journal"]).read_text())
    assert journal["status"] == "inactive-recovery-required" and journal["sealed"] is True
    assert journal["nextStep"] > 0 and journal["recoveryRequired"] is True
    assert interrupted_fake.services == interrupted_fake.original_services
    assert any(item["operation"] == "restore-services" and item["status"] == 0
               for item in journal["compensation"])
    try:
        outer.execute(interrupted, document_sha256="2" * 64, index_sha256="3" * 64,
                      root=root, runner=interrupted_fake.run, internal=interrupted_fake.internal)
    except ValueError:
        pass
    else:
        raise AssertionError("existing evidence directory was reused")
    recovery = copy.deepcopy(interrupted)
    recovery["operationId"] += "-recovery"
    recovery["evidenceDirectory"] += "-recovery"
    recovery["journal"] = recovery["evidenceDirectory"] + "/transaction.json"
    recovery["inputs"]["stagingDirectory"] += "-recovery"
    recovery["inputs"]["ownedPaths"] = [
        recovery["inputs"]["stagingDirectory"], recovery["evidenceDirectory"]]
    refresh_actions(recovery)
    recovery_fake = outer.FilesystemFake(root, recovery)
    recovered = outer.execute(
        recovery, document_sha256="4" * 64, index_sha256="3" * 64,
        root=root, runner=recovery_fake.run, internal=recovery_fake.internal,
        recover_from=pathlib.Path(interrupted["journal"]),
    )
    assert recovered["status"] == "complete"
    assert recovered["recovers"]["operationId"] == interrupted["operationId"]

bad = copy.deepcopy(document)
bad["steps"][0]["operation"] = "arbitrary-command"
try:
    outer.validate_document(bad)
except ValueError:
    pass
else:
    raise AssertionError("unknown operation reached the permanent dispatcher")

index = json.loads((ROOT / "release/gate-d-attempts-v1/index.json").read_text())
checkpoint_states = {}
for record in index["attempts"]:
    attempt = json.loads((ROOT / "release/gate-d-attempts-v1" / record["file"]).read_text())
    with tempfile.TemporaryDirectory() as temporary:
        root = pathlib.Path(temporary)
        (root / "inputs").mkdir()
        for label in ("candidate", "predecessor"):
            archive = root / f"inputs/{label}.tar.gz"
            payload = root / f"{label}.txt"
            payload.write_text(label)
            with tarfile.open(archive, "w:gz") as output:
                output.add(payload, arcname=f"rp1-gpclk-dkms-{label}/README")
            field = "candidate" if label == "candidate" else "predecessor"
            attempt["inputs"][f"{field}Archive"] = f"/inputs/{label}.tar.gz"
            attempt["inputs"][f"{field}ArchiveSha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        for route in ("gpio4", "gpio20"):
            dtbo = root / f"inputs/rp1-gpclk-{route}.dtbo"
            dtbo.write_bytes(route.encode())
            attempt["inputs"][f"{route}Dtbo"] = f"/inputs/rp1-gpclk-{route}.dtbo"
            attempt["inputs"][f"{route}DtboSha256"] = hashlib.sha256(dtbo.read_bytes()).hexdigest()
        refresh_actions(attempt)
        fake = outer.FilesystemFake(root, attempt)
        result = outer.execute(attempt, document_sha256=record["sha256"],
                               index_sha256="5" * 64, root=root,
                               runner=fake.run, internal=fake.internal)
        reboot_count = 0
        while result["status"] == "reboot-required":
            reboot_count += 1
            result = outer.execute(attempt, document_sha256=record["sha256"],
                                   index_sha256="5" * 64, root=root,
                                   runner=fake.run, internal=fake.internal, resume=True)
        assert result["status"] == "complete" and result["sealed"] is True
        assert reboot_count == (2 if attempt["matrixRow"] == "prior-supported-kernel-downgrade" else 0)
        assert fake.services == fake.original_services
        assert not fake.module_loaded and not fake.overlay and not fake.owner and not fake.open_descriptor
        if attempt["matrixRow"] == "interrupted-upgrade":
            transition = outer.rooted(root, attempt["evidenceDirectory"]) / "transition/transaction.json"
            state = json.loads(transition.read_text())
            checkpoint_states[state["checkpoint"]] = (state["phase"], state["moduleLoaded"],
                                                        state["endpointOpen"], state["overlay"])

assert set(checkpoint_states) == {
    "preflight", "retain-predecessor", "dkms-add", "dkms-build", "dkms-install",
    "load-disabled", "query-disabled", "uapi-query-release", "unbind-bind", "unload",
    "dkms-uninstall", "dkms-remove", "owned-residue-remove", "verify-final-state", "commit-state"}
assert checkpoint_states["dkms-add"][0] == "registered"
assert checkpoint_states["dkms-build"][0] == "built"
assert checkpoint_states["dkms-install"][0] == "installed"
assert checkpoint_states["load-disabled"][1:3] == (True, True)
assert checkpoint_states["unload"][1:3] == (False, False)
assert checkpoint_states["dkms-remove"][0] == "absent"

# The real target preflight is exercised against a rooted synthetic filesystem
# and a closed command transcript.  Each mutable identity must fail closed.
preflight_doc = copy.deepcopy(document)
with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    evidence = outer.rooted(root, preflight_doc["evidenceDirectory"])
    evidence.mkdir(parents=True)
    (root / "proc/sys/kernel/random").mkdir(parents=True)
    (root / "proc/sys/kernel/random/boot_id").write_text(
        "01234567-89ab-cdef-0123-456789abcdef\n")
    for item in preflight_doc["inputs"]["tooling"].values():
        installed = outer.rooted(root, item["installedPath"])
        installed.parent.mkdir(parents=True, exist_ok=True)
        source = ROOT / item["sourcePath"]
        installed.write_bytes(source.read_bytes())
        item["sha256"] = hashlib.sha256(installed.read_bytes()).hexdigest()

    original_run = outer.subprocess.run
    def preflight_run(argv, **kwargs):
        outputs = {("/usr/bin/uname", "-r"): preflight_doc["kernelRelease"] + "\n",
                   ("/usr/bin/cat", "/proc/sys/kernel/module_sig_enforce"): "0\n",
                   ("/usr/bin/dtoverlay", "-l"): "No overlays loaded\n"}
        return outer.subprocess.CompletedProcess(argv, 0, outputs[tuple(argv)], "")
    outer.subprocess.run = preflight_run
    try:
        outer.default_internal("capture-preflight", preflight_doc, root)
        captured = json.loads((evidence / "preflight.json").read_text())
        assert captured["runningKernel"] == preflight_doc["kernelRelease"]
        assert captured["moduleSigEnforce"] == "0" and captured["liveOutput"] is False
        victim = next(iter(preflight_doc["inputs"]["tooling"].values()))
        outer.rooted(root, victim["installedPath"]).write_bytes(b"changed")
        try:
            outer.default_internal("capture-preflight", preflight_doc, root)
        except ValueError as error:
            assert "installed permanent tool differs" in str(error)
        else:
            raise AssertionError("changed installed permanent tool passed preflight")
    finally:
        outer.subprocess.run = original_run

print("Gate D permanent outer executor: PASS")
