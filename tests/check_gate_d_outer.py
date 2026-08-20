#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_outer", ROOT / "scripts/gate_d_outer.py")
assert spec and spec.loader
outer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = outer
spec.loader.exec_module(outer)

# Exercise the actual CLI execute branch through its explicit fail-closed gate.
# A function-local import in another branch previously shadowed the module-level
# ``sys`` binding and crashed here before reaching this authorization check.
cli = subprocess.run(
    ["python3", str(ROOT / "scripts/gate_d_outer.py"), "execute",
     str(ROOT / "release/gate-d-attempts-v1/gd-current-supported-kernel-gpio4.json")],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=False,
)
assert cli.returncode != 0
assert "target execution requires root, --execute, --index, and --instance" in cli.stderr
assert "UnboundLocalError" not in cli.stderr


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
assert outer.initial_preflight_kernel(document) == document["kernelRelease"]

failed_prior = copy.deepcopy(document)
failed_prior["matrixRow"] = "prior-supported-kernel-downgrade"
failed_prior["kernelRelease"] = "6.12.75+rpt-rpi-2712"
failed_prior["inputs"]["boot"]["normalKernel"] = "6.18.34+rpt-rpi-2712"
failed_prior["inputs"]["boot"]["priorKernel"] = "6.12.75+rpt-rpi-2712"
assert outer.initial_preflight_kernel(failed_prior) == failed_prior["inputs"]["boot"]["normalKernel"]
for mutation in (
        lambda value: value.update(inputs=None),
        lambda value: value["inputs"].pop("boot"),
        lambda value: value["inputs"]["boot"].pop("normalKernel"),
        lambda value: value["inputs"]["boot"].update(normalKernel=value["kernelRelease"]),
        lambda value: value["inputs"]["boot"].update(priorKernel="different-kernel")):
    invalid = copy.deepcopy(failed_prior)
    mutation(invalid)
    try:
        outer.initial_preflight_kernel(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed prior-kernel preflight identity passed")

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
    (root / "proc/cmdline").write_text("root=/dev/test quiet\n")
    (root / "sys/firmware/devicetree/base").mkdir(parents=True)
    (root / "proc/device-tree").symlink_to("/sys/firmware/devicetree/base")
    (root / "boot").mkdir()
    (root / "boot" / f"config-{preflight_doc['kernelRelease']}").write_text(
        "# CONFIG_MODULE_SIG is not set\n")
    for item in preflight_doc["inputs"]["tooling"].values():
        installed = outer.rooted(root, item["installedPath"])
        installed.parent.mkdir(parents=True, exist_ok=True)
        source = ROOT / item["sourcePath"]
        installed.write_bytes(source.read_bytes())
        source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        item.pop("sha256")
        item["sourceSha256"] = source_sha
        item["installKind"] = "target-built" if item["sourcePath"].endswith(".c") else "copied"
        item["installedSha256"] = hashlib.sha256(installed.read_bytes()).hexdigest()

    original_run = outer.subprocess.run
    def preflight_run(argv, **kwargs):
        outputs = {("/usr/bin/uname", "-r"): preflight_doc["kernelRelease"] + "\n",
                   ("/usr/bin/dtoverlay", "-l"): "No overlays loaded\n"}
        return outer.subprocess.CompletedProcess(argv, 0, outputs[tuple(argv)], "")
    outer.subprocess.run = preflight_run
    try:
        outer.default_internal("capture-preflight", preflight_doc, root)
        captured = json.loads((evidence / "preflight.json").read_text())
        assert captured["runningKernel"] == preflight_doc["kernelRelease"]
        assert captured["moduleSigningPolicy"] == {
            "enforced": False, "source": "config-disabled-sysctl-absent",
            "sysctl": None, "configPath": f"/boot/config-{preflight_doc['kernelRelease']}",
            "commandLineEnforced": False, "lockdown": None,
        } and captured["liveOutput"] is False
        prior_preflight = copy.deepcopy(preflight_doc)
        prior_preflight["matrixRow"] = "prior-supported-kernel-downgrade"
        prior_preflight["inputs"]["boot"]["priorKernel"] = "prior-test-kernel"
        prior_preflight["kernelRelease"] = "prior-test-kernel"
        outer.default_internal("capture-preflight", prior_preflight, root)
        captured = json.loads((evidence / "preflight.json").read_text())
        assert captured["runningKernel"] == preflight_doc["kernelRelease"]
        assert captured["moduleSigningPolicy"]["configPath"] == (
            f"/boot/config-{preflight_doc['kernelRelease']}")

        def prior_kernel_run(argv, **kwargs):
            outputs = {("/usr/bin/uname", "-r"): "prior-test-kernel\n",
                       ("/usr/bin/dtoverlay", "-l"): "No overlays loaded\n"}
            return outer.subprocess.CompletedProcess(argv, 0, outputs[tuple(argv)], "")
        outer.subprocess.run = prior_kernel_run
        try:
            outer.default_internal("capture-preflight", prior_preflight, root)
        except ValueError as error:
            assert str(error) == "running kernel differs from attempt"
        else:
            raise AssertionError("prior kernel passed initial downgrade preflight")
        outer.subprocess.run = preflight_run
        victim = next(iter(preflight_doc["inputs"]["tooling"].values()))
        outer.rooted(root, victim["installedPath"]).write_bytes(b"changed")
        try:
            outer.default_internal("capture-preflight", preflight_doc, root)
        except ValueError as error:
            assert "installed permanent tool differs" in str(error)
        else:
            raise AssertionError("changed installed permanent tool passed preflight")
        victim_path = outer.rooted(root, victim["installedPath"])
        victim_path.unlink()
        victim_path.symlink_to("/nonexistent")
        try:
            outer.default_internal("capture-preflight", preflight_doc, root)
        except ValueError as error:
            assert "symlink in controlled path" in str(error)
        else:
            raise AssertionError("symlinked installed permanent tool passed preflight")
    finally:
        outer.subprocess.run = original_run

# Match the Raspberry Pi kernel alias exactly while rejecting every less
# specific symlink allowance and every symlink below the canonical DT root.
with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    canonical = root / "sys/firmware/devicetree/base"
    canonical.mkdir(parents=True)
    (root / "proc").mkdir()
    alias = root / "proc/device-tree"
    alias.symlink_to("/sys/firmware/devicetree/base")
    resource = outer.device_tree_resource(root, "rp1-gpclk")
    assert resource == canonical / "rp1-gpclk" and not resource.exists()
    resource.mkdir()
    (resource / "compatible").write_bytes(b"wsprrypi,rp1-gpclk\0")
    assert outer.device_tree_resource(root, "rp1-gpclk") == resource
    (resource / "malicious").symlink_to("/etc/passwd")
    try:
        outer.device_tree_resource(root, "rp1-gpclk")
    except ValueError as error:
        assert "symlink below canonical device-tree resource" in str(error)
    else:
        raise AssertionError("device-tree descendant symlink passed")
    (resource / "malicious").unlink()
    resource.rename(canonical / "direct")
    (canonical / "rp1-gpclk").symlink_to("direct")
    try:
        outer.device_tree_resource(root, "rp1-gpclk")
    except ValueError as error:
        assert "symlink in controlled path" in str(error)
    else:
        raise AssertionError("symlinked device-tree resource passed")
    (canonical / "rp1-gpclk").unlink()
    alias.unlink()
    alias.symlink_to("/sys/firmware/devicetree/wrong")
    try:
        outer.device_tree_resource(root, "rp1-gpclk")
    except ValueError as error:
        assert "canonical /proc/device-tree alias differs" in str(error)
    else:
        raise AssertionError("changed /proc/device-tree alias passed")
    try:
        outer.device_tree_resource(root, "../rp1-gpclk")
    except ValueError as error:
        assert "unsafe device-tree resource name" in str(error)
    else:
        raise AssertionError("unsafe device-tree resource name passed")

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    (root / "proc").mkdir()
    (root / "proc/device-tree").symlink_to("/sys/firmware/devicetree/base")
    (root / "sys").mkdir()
    (root / "outside").mkdir()
    (root / "sys/firmware").symlink_to(root / "outside")
    try:
        outer.device_tree_resource(root, "rp1-gpclk")
    except ValueError as error:
        assert "symlink in controlled path" in str(error)
    else:
        raise AssertionError("symlinked canonical device-tree component passed")

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    kernel = "test-kernel"
    (root / "boot").mkdir()
    (root / "proc/sys/kernel").mkdir(parents=True)
    (root / "proc/cmdline").write_text("root=/dev/test quiet\n")
    config = root / f"boot/config-{kernel}"
    config.write_text("# CONFIG_MODULE_SIG is not set\n")
    policy = outer.module_signing_policy(root, kernel)
    assert policy["enforced"] is False and policy["sysctl"] is None

    (root / "proc/cmdline").write_text("root=/dev/test module.sig_enforce=1\n")
    try:
        outer.module_signing_policy(root, kernel)
    except ValueError as error:
        assert "contradicts runtime policy" in str(error)
    else:
        raise AssertionError("contradictory disabled-signing policy passed")
    (root / "proc/cmdline").write_text("root=/dev/test quiet\n")

    config.write_text("CONFIG_MODULE_SIG=y\n# CONFIG_MODULE_SIG_FORCE is not set\n")
    sysctl = root / "proc/sys/kernel/module_sig_enforce"
    try:
        outer.module_signing_policy(root, kernel)
    except ValueError as error:
        assert "requires runtime policy evidence" in str(error)
    else:
        raise AssertionError("signing-enabled policy without runtime evidence passed")
    sysctl.write_text("0\n")
    policy = outer.module_signing_policy(root, kernel)
    assert policy["enforced"] is False and policy["sysctl"] == "0"
    sysctl.write_text("1\n")
    assert outer.module_signing_policy(root, kernel)["enforced"] is True

    sysctl.unlink()
    sysctl.mkdir()
    try:
        outer.module_signing_policy(root, kernel)
    except ValueError as error:
        assert "sysctl is unsafe" in str(error)
    else:
        raise AssertionError("unsafe signature sysctl passed")
    sysctl.rmdir()
    config.unlink()
    try:
        outer.module_signing_policy(root, kernel)
    except ValueError as error:
        assert "configuration is unavailable" in str(error)
    else:
        raise AssertionError("missing kernel configuration passed")

print("Gate D permanent outer executor: PASS")
