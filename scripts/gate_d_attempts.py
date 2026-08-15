#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate, validate, and offline-execute Gate D attempt documents.

The executor has a closed structured-operation vocabulary.  ``argv`` is an
exact audit rendering and is never passed through a shell.  The checked-in
offline backend is stateful; target dispatch remains separately gated.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
EXECUTABLE = "/usr/libexec/rp1-gpclk-dkms/gate-d-outer"
SHA = re.compile(r"[0-9a-f]{64}")
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9._-]+")
ROUTES = {"gpio4", "gpio20", "route-neutral"}
PROHIBITED = {"live_output=1", "/dev/mem", "rpi-update", "--force", "rf", "sdr"}

ENVELOPE_BEFORE = (
    "create-evidence", "capture-preflight", "verify-input-hashes",
    "snapshot-services", "quiesce-services", "stage-source",
)
ENVELOPE_AFTER = (
    "restore-services", "audit-residue", "capture-kernel-log-delta",
    "verify-final-safety", "seal-evidence",
)
ROW_ACTIONS = {
    "current-supported-kernel": ("install-successor", "apply-route", "load-disabled", "query-release", "unbind-rebind", "unload", "remove-route", "remove-test-state"),
    "prior-supported-kernel-downgrade": ("select-prior-kernel", "pause-reboot-prior", "verify-prior-kernel", "install-predecessor", "install-successor", "apply-route", "load-disabled", "query-release", "unbind-rebind", "unload", "remove-route", "remove-test-state", "restore-normal-boot", "pause-reboot-normal", "verify-normal-kernel"),
    "signing-not-enforced": ("verify-signing-off", "install-successor", "apply-route", "load-disabled", "query-release", "unload", "remove-route", "remove-test-state", "verify-signing-unchanged"),
    "deliberate-build-failure": ("install-predecessor", "stage-successor", "inject-build-failure", "expect-build-failure", "recover-predecessor", "remove-failed-successor"),
    "interrupted-upgrade": ("install-predecessor", "apply-route", "run-to-checkpoint", "interrupt-after-checkpoint", "freeze-failed-journal", "recover-new-journal", "verify-one-inactive-version", "remove-route", "remove-attempt-residue"),
    "stale-manifest": ("copy-candidate", "inject-stale-identity", "expect-preload-rejection", "remove-injected-copy", "verify-baseline-unchanged"),
    "corrupted-archive-or-dtbo": ("copy-artifact", "flip-byte", "expect-preinstall-rejection", "remove-injected-copy", "verify-baseline-unchanged"),
    "removal-inactive": ("install-successor", "prove-inactive", "inventory-owned-paths", "remove-test-state", "verify-empty-package-state"),
    "removal-open-or-active": ("install-successor", "apply-route", "load-disabled", "start-busy-injector", "expect-removal-refusal", "stop-busy-injector", "unload", "remove-route", "remove-test-state"),
    "reinstall-after-removal": ("prove-empty-package-state", "install-successor", "apply-route", "load-disabled", "query-release", "unload", "remove-route", "remove-test-state", "verify-empty-package-state"),
}
OPERATIONS = set(ENVELOPE_BEFORE + ENVELOPE_AFTER)
for actions in ROW_ACTIONS.values():
    OPERATIONS.update(actions)


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def load_json(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"not a real JSON file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON document must be an object")
    return value


def route_for(row: str, attempt: str) -> str:
    if row == "interrupted-upgrade":
        return "gpio4"
    if "gpio4" in attempt or attempt == "gpio4":
        return "gpio4"
    if "gpio20" in attempt or attempt == "gpio20":
        return "gpio20"
    if row in {"current-supported-kernel", "prior-supported-kernel-downgrade",
               "signing-not-enforced", "reinstall-after-removal"}:
        return attempt
    return "route-neutral"


def expected_final(row: str) -> str:
    if row in {"deliberate-build-failure", "interrupted-upgrade"}:
        return "predecessor-inactive"
    return "empty-inactive-baseline"


def lifecycle_safety() -> dict:
    false = {field: False for field in (
        "liveOutput", "clockEnabled", "clockPrepared", "dmaActive", "gpioOutput",
        "transmitterActive", "sdrActive", "antennaConnected", "moduleLoaded",
        "platformBound", "endpointOpen", "ownerPresent", "workActive",
        "callbackPending", "cleanupLatched")}
    true = {field: True for field in (
        "si5351Disconnected", "ownershipKnown", "routeSelectedInactive",
        "selectedPinSafe", "unselectedPinSafe", "unrelatedBytesPreserved")}
    return {**false, **true}


def subordinate_documents(operation_id: str, row: dict, candidate: dict,
                          predecessor: str, attempt: str) -> dict | None:
    if row["id"] != "interrupted-upgrade":
        return None
    base = row["evidenceDirectory"]
    transition_id = f"{operation_id}-transition"
    recovery_id = f"{operation_id}-recovery"
    common = {
        "schemaVersion": 1, "matrixRow": row["id"], "hostId": "wspr5-stock",
        "kernelRelease": row["kernel"], "route": "gpio4",
        "deadlineSeconds": row["deadlineSeconds"],
        "predecessorVersion": predecessor, "successorVersion": candidate["release"],
        "testVersions": [candidate["release"]], "ownedPaths": [],
        "safety": lifecycle_safety(), "rollbackOnFailure": False,
    }
    transition = {**common, "operationId": transition_id,
                  "operation": "qualification-transition",
                  "evidenceDirectory": f"{base}/{transition_id}",
                  "expectedFinalState": "predecessor-inactive", "priorOperationId": None}
    recovery = {**common, "operationId": recovery_id, "operation": "recover",
                "evidenceDirectory": f"{base}/{recovery_id}",
                "expectedFinalState": "predecessor-inactive",
                "priorOperationId": transition_id}
    return {"checkpoint": attempt.removeprefix("after-"),
            "transition": transition, "recovery": recovery}


def step(operation: str, operation_id: str, number: int) -> dict:
    if operation not in OPERATIONS:
        raise ValueError(f"operation has no executor: {operation}")
    return {"id": f"{number:02d}-{operation}", "operation": operation,
            "deadlineScope": "attempt-total", "action": None}


def generate(instance: dict, plan: dict) -> list[dict]:
    candidate = instance["candidate"]
    policy = instance["executionPolicy"]
    rows = {row["id"]: row for row in instance["rows"]}
    services = copy.deepcopy(plan["services"])
    safety = copy.deepcopy(plan["invariants"])
    safety.update({"clockEnabled": False, "dmaActive": False, "gpioOutput": False,
                   "moduleLoaded": False, "platformBound": False,
                   "endpointOpen": False, "ownerPresent": False})
    documents = []
    for row_plan in plan["rows"]:
        row = rows[row_plan["id"]]
        for attempt in row_plan["attempts"]:
            row_id = row_plan["id"]
            operation_id = f"gd-{row_id}-{attempt}".replace("_", "-")
            evidence = f"/var/lib/rp1-gpclk-dkms/{row['evidenceDirectory']}/{operation_id}"
            actions = ENVELOPE_BEFORE + ROW_ACTIONS[row_id] + ENVELOPE_AFTER
            steps = [step(action, operation_id, number) for number, action in enumerate(actions, 1)]
            document = {
                "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
                "kind": "gate-d-executable-attempt", "operationId": operation_id,
                "matrixRow": row_id, "attempt": attempt, "hostId": "wspr5-stock",
                "kernelRelease": row["kernel"], "route": route_for(row_id, attempt),
                "deadlineSeconds": row["deadlineSeconds"], "evidenceDirectory": evidence,
                "journal": f"{evidence}/transaction.json",
                "inputs": {
                    "candidateRelease": candidate["release"],
                    "candidateArchive": plan["artifacts"]["successor"]["archive"],
                    "candidateArchiveSha256": candidate["archiveSha256"],
                    "predecessorVersion": plan["artifacts"]["predecessor"]["version"],
                    "predecessorArchive": plan["artifacts"]["predecessor"]["archive"],
                    "predecessorArchiveSha256": plan["artifacts"]["predecessor"]["sha256"],
                    "sourceCommit": candidate["sourceCommit"], "uapiSha256": candidate["uapiSha256"],
                    "manifestSha256": candidate["manifestSha256"],
                    "gpio4DtboSha256": candidate["gpio4DtboSha256"],
                    "gpio20DtboSha256": candidate["gpio20DtboSha256"],
                    "gpio4Dtbo": str(pathlib.PurePosixPath(plan["artifacts"]["successor"]["archive"]).with_name("rp1-gpclk-gpio4.dtbo")),
                    "gpio20Dtbo": str(pathlib.PurePosixPath(plan["artifacts"]["successor"]["archive"]).with_name("rp1-gpclk-gpio20.dtbo")),
                    "matrixPolicySha256": policy["matrixPolicySha256"],
                    "routeDecisionSha256": policy["routeDecisionSha256"],
                    "targetPlanSha256": policy["targetPlanSha256"],
                    "boot": copy.deepcopy(plan["boot"]),
                    "tooling": copy.deepcopy(plan["tooling"]),
                    "stagingDirectory": f"/var/lib/rp1-gpclk-dkms/gate-d/staging/{operation_id}",
                    "ownedPaths": [
                        f"/var/lib/rp1-gpclk-dkms/gate-d/staging/{operation_id}", evidence
                    ],
                    "subordinateLifecycle": subordinate_documents(
                        operation_id, row, candidate,
                        plan["artifacts"]["predecessor"]["version"], attempt),
                },
                "services": services, "safety": safety,
                "expectedFinalState": expected_final(row_id), "steps": steps,
            }
            from gate_d_outer import ClosedDispatcher
            dispatcher = ClosedDispatcher(document)
            for item in document["steps"]:
                item["action"] = dispatcher.action(item["operation"]).as_json()
            validate_document(document)
            documents.append(document)
    if len(documents) != 38 or len({doc["operationId"] for doc in documents}) != 38:
        raise ValueError("attempt generation is not exactly 38 unique documents")
    return documents


def validate_document(value: dict) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "operationId",
                "matrixRow", "attempt", "hostId", "kernelRelease", "route",
                "deadlineSeconds", "evidenceDirectory", "journal", "inputs",
                "services", "safety", "expectedFinalState", "steps"}
    if set(value) != required or value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or value.get("kind") != "gate-d-executable-attempt":
        raise ValueError("attempt document fields are incomplete or unknown")
    if not SAFE_ID.fullmatch(value["operationId"]):
        raise ValueError("unsafe operation ID")
    if value["matrixRow"] not in ROW_ACTIONS or value["hostId"] != "wspr5-stock" or value["route"] not in ROUTES:
        raise ValueError("unknown row, host, or route")
    if not isinstance(value["deadlineSeconds"], int) or not 1 <= value["deadlineSeconds"] <= 1800:
        raise ValueError("invalid deadline")
    evidence = value["evidenceDirectory"]
    if not isinstance(evidence, str) or not evidence.startswith("/var/lib/rp1-gpclk-dkms/gate-d/") or ".." in pathlib.PurePosixPath(evidence).parts:
        raise ValueError("unsafe evidence directory")
    if value["journal"] != f"{evidence}/transaction.json":
        raise ValueError("journal is not bound to evidence directory")
    inputs = value["inputs"]
    required_inputs = {"candidateRelease", "candidateArchive", "candidateArchiveSha256",
                       "predecessorVersion", "predecessorArchive", "predecessorArchiveSha256", "sourceCommit", "uapiSha256",
                       "manifestSha256", "gpio4DtboSha256", "gpio20DtboSha256",
                       "gpio4Dtbo", "gpio20Dtbo",
                       "matrixPolicySha256", "routeDecisionSha256", "targetPlanSha256",
                       "boot", "tooling", "stagingDirectory", "ownedPaths",
                       "subordinateLifecycle"}
    if set(inputs) != required_inputs:
        raise ValueError("attempt inputs are incomplete")
    for field in {"candidateArchiveSha256", "predecessorArchiveSha256", "uapiSha256",
                  "manifestSha256", "gpio4DtboSha256", "gpio20DtboSha256",
                  "matrixPolicySha256", "routeDecisionSha256", "targetPlanSha256"}:
        if not isinstance(inputs[field], str) or not SHA.fullmatch(inputs[field]):
            raise ValueError(f"invalid attempt input: {field}")
    for field in ("candidateArchive", "predecessorArchive", "gpio4Dtbo", "gpio20Dtbo", "stagingDirectory"):
        path = inputs[field]
        if not isinstance(path, str) or not path.startswith("/") or ".." in pathlib.PurePosixPath(path).parts:
            raise ValueError(f"unsafe attempt path: {field}")
    if not isinstance(inputs["ownedPaths"], list) or not inputs["ownedPaths"] or len(inputs["ownedPaths"]) != len(set(inputs["ownedPaths"])):
        raise ValueError("owned path inventory is invalid")
    if not isinstance(inputs["boot"], dict) or not isinstance(inputs["tooling"], dict):
        raise ValueError("boot or tooling inputs are absent")
    subordinate = inputs["subordinateLifecycle"]
    if value["matrixRow"] == "interrupted-upgrade":
        if not isinstance(subordinate, dict) or set(subordinate) != {"checkpoint", "transition", "recovery"}:
            raise ValueError("interruption subordinate lifecycle is absent")
        from gate_d_lifecycle import CHECKPOINTS, validate_operation
        if subordinate["checkpoint"] not in CHECKPOINTS:
            raise ValueError("unknown subordinate interruption checkpoint")
        validate_operation(subordinate["transition"])
        validate_operation(subordinate["recovery"])
        if (subordinate["transition"]["operation"] != "qualification-transition" or
                subordinate["recovery"]["operation"] != "recover" or
                subordinate["recovery"]["priorOperationId"] != subordinate["transition"]["operationId"]):
            raise ValueError("subordinate transition/recovery relationship differs")
    elif subordinate is not None:
        raise ValueError("non-interruption attempt contains subordinate lifecycle")
    if not isinstance(value["steps"], list) or not value["steps"]:
        raise ValueError("attempt has no executable steps")
    seen = set()
    for item in value["steps"]:
        if set(item) != {"id", "operation", "deadlineScope", "action"}:
            raise ValueError("step fields are incomplete")
        if item["id"] in seen or item["operation"] not in OPERATIONS:
            raise ValueError("duplicate or undispatchable step")
        seen.add(item["id"])
        if item["deadlineScope"] != "attempt-total":
            raise ValueError("step command differs from closed executor template")
        action = item["action"]
        if (not isinstance(action, dict) or set(action) != {"kind", "name", "argv", "expectedStatus"} or
                action["name"] != item["operation"] or action["kind"] not in {"internal", "command", "service-transaction"} or
                not isinstance(action["argv"], list) or not isinstance(action["expectedStatus"], list)):
            raise ValueError("step lacks an exact permanent-executor action")
        flat = " ".join(action["argv"]).lower()
        if any(token in flat for token in PROHIBITED) or any("${" in token or "*" in token for token in action["argv"]):
            raise ValueError("prohibited or unresolved command token")
    expected_actions = ENVELOPE_BEFORE + ROW_ACTIONS[value["matrixRow"]] + ENVELOPE_AFTER
    if tuple(item["operation"] for item in value["steps"]) != expected_actions:
        raise ValueError("attempt steps differ from exact row recipe")
    return {"valid": True, "operationId": value["operationId"], "readOnly": True}


class FakeSystem:
    def __init__(self, document: dict):
        self.document = document
        self.services = {item["name"]: item["requiredPreState"] for item in document["services"]}
        self.original_services = copy.deepcopy(self.services)
        self.kernel = "6.18.34+rpt-rpi-2712"
        self.dkms: set[str] = set()
        self.module_loaded = False
        self.overlay: str | None = None
        self.endpoint = False
        self.busy: str | None = None
        self.evidence_created = False
        self.evidence_sealed = False
        self.source_staged = False
        self.injected = False
        self.failed_journal = False
        self.recovery_journal = False
        self.elapsed = 0
        self.commands: list[list[str]] = []
        self.logs: list[str] = []

    def dispatch(self, operation: str) -> None:
        if self.evidence_sealed:
            raise ValueError("sealed evidence is immutable")
        if operation not in OPERATIONS:
            raise ValueError("undispatchable operation")
        method = getattr(self, f"op_{operation.replace('-', '_')}", None)
        if method is None:
            raise ValueError(f"operation lacks backend implementation: {operation}")
        self.elapsed += 1
        if self.elapsed > self.document["deadlineSeconds"]:
            raise TimeoutError("attempt total deadline exhausted")
        self.commands.append([operation])
        method()

    def op_create_evidence(self): self.evidence_created = True
    def op_capture_preflight(self):
        if not self.evidence_created or self.module_loaded or self.overlay or self.busy: raise ValueError("unsafe preflight")
    def op_verify_input_hashes(self): pass
    def op_snapshot_services(self): pass
    def op_quiesce_services(self):
        for name in ("wsprrypi", "sdrplay", "SoapySDRServer"):
            if self.services[name] != "active": raise ValueError("service pre-state drift")
            self.services[name] = "inactive"
    def op_stage_source(self): self.source_staged = True
    def op_restore_services(self): self.services = copy.deepcopy(self.original_services)
    def op_audit_residue(self):
        if self.module_loaded or self.overlay or self.busy: raise ValueError("runtime residue")
    def op_capture_kernel_log_delta(self): self.logs.append("scoped-clean")
    def op_verify_final_safety(self):
        if self.module_loaded or self.overlay or self.busy or self.services != self.original_services: raise ValueError("unsafe final state")
    def op_seal_evidence(self):
        if not self.evidence_created: raise ValueError("evidence absent")
        self.evidence_sealed = True
    def op_install_successor(self):
        if not self.source_staged: raise ValueError("source not staged")
        self.dkms.add("0.0.0-phase5.16")
    def op_install_predecessor(self): self.dkms.add("0.0.0-phase5.2")
    def op_apply_route(self):
        if self.document["route"] not in {"gpio4", "gpio20"}: raise ValueError("route required")
        self.overlay = self.document["route"]; self.endpoint = self.module_loaded
    def op_load_disabled(self):
        if "0.0.0-phase5.16" not in self.dkms or not self.overlay: raise ValueError("load precondition")
        self.module_loaded = True; self.endpoint = True
    def op_query_release(self):
        if not self.module_loaded or not self.endpoint: raise ValueError("query unavailable")
    def op_unbind_rebind(self):
        if not self.module_loaded or not self.endpoint: raise ValueError("binding unavailable")
    def op_unload(self): self.module_loaded = False; self.endpoint = False
    def op_remove_route(self):
        if self.module_loaded: raise ValueError("module still loaded")
        self.overlay = None
    def op_remove_test_state(self):
        if self.module_loaded or self.overlay or self.busy: raise ValueError("active removal")
        self.dkms.clear(); self.source_staged = False
    def op_select_prior_kernel(self): self.kernel = "boot-selection-pending-prior"
    def op_pause_reboot_prior(self):
        if self.kernel != "boot-selection-pending-prior": raise ValueError("prior selection absent")
        self.kernel = "6.12.75+rpt-rpi-2712"
    def op_verify_prior_kernel(self):
        if self.kernel != "6.12.75+rpt-rpi-2712": raise ValueError("wrong prior kernel")
    def op_restore_normal_boot(self): self.kernel = "boot-selection-pending-normal"
    def op_pause_reboot_normal(self):
        if self.kernel != "boot-selection-pending-normal": raise ValueError("normal selection absent")
        self.kernel = "6.18.34+rpt-rpi-2712"
    def op_verify_normal_kernel(self):
        if self.kernel != "6.18.34+rpt-rpi-2712": raise ValueError("wrong normal kernel")
    def op_verify_signing_off(self): pass
    def op_verify_signing_unchanged(self): pass
    def op_stage_successor(self): self.source_staged = True
    def op_inject_build_failure(self): self.injected = True
    def op_expect_build_failure(self):
        if not self.injected: raise ValueError("build failure absent")
    def op_recover_predecessor(self):
        self.dkms = {"0.0.0-phase5.2"}; self.module_loaded = False; self.overlay = None
    def op_remove_failed_successor(self): self.dkms.discard("0.0.0-phase5.16")
    def op_run_to_checkpoint(self): self.failed_journal = False
    def op_interrupt_after_checkpoint(self): self.failed_journal = True
    def op_freeze_failed_journal(self):
        if not self.failed_journal: raise ValueError("failed journal absent")
    def op_recover_new_journal(self): self.recovery_journal = True; self.dkms = {"0.0.0-phase5.2"}
    def op_verify_one_inactive_version(self):
        if self.dkms != {"0.0.0-phase5.2"} or self.module_loaded: raise ValueError("mixed recovery state")
    def op_remove_attempt_residue(self): self.source_staged = False
    def op_copy_candidate(self): self.source_staged = True
    def op_inject_stale_identity(self): self.injected = True
    def op_expect_preload_rejection(self):
        if not self.injected or self.module_loaded: raise ValueError("stale rejection absent")
    def op_copy_artifact(self): self.source_staged = True
    def op_flip_byte(self): self.injected = True
    def op_expect_preinstall_rejection(self):
        if not self.injected or self.dkms: raise ValueError("integrity rejection absent")
    def op_remove_injected_copy(self): self.source_staged = False; self.injected = False
    def op_verify_baseline_unchanged(self):
        if self.dkms or self.module_loaded or self.overlay: raise ValueError("baseline changed")
    def op_prove_inactive(self):
        if self.module_loaded or self.overlay or self.busy: raise ValueError("not inactive")
    def op_inventory_owned_paths(self): pass
    def op_verify_empty_package_state(self):
        if self.dkms or self.module_loaded or self.overlay or self.busy: raise ValueError("package state not empty")
    def op_start_busy_injector(self):
        attempt = self.document["attempt"]
        self.busy = "owner" if attempt.startswith("owner-") else "open"
    def op_expect_removal_refusal(self):
        if self.busy not in {"open", "owner"}: raise ValueError("busy blocker absent")
    def op_stop_busy_injector(self): self.busy = None
    def op_prove_empty_package_state(self): self.op_verify_empty_package_state()


def execute_fake(document: dict) -> dict:
    validate_document(document)
    state = FakeSystem(document)
    for item in document["steps"]:
        state.dispatch(item["operation"])
    if not state.evidence_sealed:
        raise ValueError("evidence was not sealed")
    if document["expectedFinalState"] == "empty-inactive-baseline" and state.dkms:
        raise ValueError("final package residue")
    if document["expectedFinalState"] == "predecessor-inactive" and state.dkms != {"0.0.0-phase5.2"}:
        raise ValueError("predecessor final state differs")
    return {"status": "complete", "operationId": document["operationId"],
            "commands": state.commands, "evidenceSealed": True,
            "servicesRestored": state.services == state.original_services,
            "liveOutput": False, "elapsedSeconds": state.elapsed}


def write_bundle(output: pathlib.Path, documents: list[dict], tool_path: pathlib.Path) -> dict:
    if output.exists() or output.is_symlink():
        raise ValueError("attempt output directory already exists")
    output.mkdir(parents=True, mode=0o755)
    records = []
    for document in documents:
        path = output / f"{document['operationId']}.json"
        path.write_bytes(canonical(document))
        records.append({"operationId": document["operationId"], "file": path.name,
                        "sha256": digest(path)})
    index = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
             "kind": "gate-d-attempt-index", "attemptCount": len(records),
             "executors": {
                 "attemptGenerator": {"path": str(tool_path.relative_to(ROOT)), "sha256": digest(tool_path)},
                 "permanentExecutor": {"path": "scripts/gate_d_outer.py", "sha256": digest(ROOT / "scripts/gate_d_outer.py")},
             },
             "attempts": records}
    (output / "index.json").write_bytes(canonical(index))
    return index


def validate_index(index_path: pathlib.Path, *, expected_documents: list[dict] | None = None) -> dict:
    """Validate a checked bundle, including every byte and executor identity."""
    index = load_json(index_path)
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "attemptCount",
                "executors", "attempts"}
    if (set(index) != required or index.get("SPDX-License-Identifier") != "MIT" or
            index.get("schemaVersion") != 1 or index.get("kind") != "gate-d-attempt-index"):
        raise ValueError("invalid attempt-index identity")
    records = index.get("attempts")
    if index.get("attemptCount") != 38 or not isinstance(records, list) or len(records) != 38:
        raise ValueError("attempt index must contain exactly 38 records")
    executors = index.get("executors")
    expected_executors = {
        "attemptGenerator": {"path": "scripts/gate_d_attempts.py", "sha256": digest(ROOT / "scripts/gate_d_attempts.py")},
        "permanentExecutor": {"path": "scripts/gate_d_outer.py", "sha256": digest(ROOT / "scripts/gate_d_outer.py")},
    }
    if executors != expected_executors:
        raise ValueError("attempt executor identity mismatch")
    documents = []
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != {"operationId", "file", "sha256"}:
            raise ValueError("attempt-index record is incomplete")
        filename = record["file"]
        if (not isinstance(filename, str) or pathlib.PurePosixPath(filename).name != filename or
                filename in seen_files or not SHA.fullmatch(record["sha256"])):
            raise ValueError("unsafe, duplicate, or unhashed attempt record")
        path = index_path.parent / filename
        if path.is_symlink() or not path.is_file() or digest(path) != record["sha256"]:
            raise ValueError("attempt document identity mismatch")
        document = load_json(path)
        validate_document(document)
        if document["operationId"] != record["operationId"] or document["operationId"] in seen_ids:
            raise ValueError("attempt operation identity mismatch")
        seen_files.add(filename)
        seen_ids.add(document["operationId"])
        documents.append(document)
    if expected_documents is not None and documents != expected_documents:
        raise ValueError("checked attempts differ from deterministic generation")
    if sum(item["matrixRow"] == "interrupted-upgrade" for item in documents) != 15:
        raise ValueError("interruption attempt cardinality differs")
    if sum(item["matrixRow"] == "removal-open-or-active" for item in documents) != 4:
        raise ValueError("busy attempt cardinality differs")
    return {"valid": True, "attemptCount": 38, "documents": documents, "readOnly": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--instance", type=pathlib.Path, required=True)
    generate_parser.add_argument("--plan", type=pathlib.Path, required=True)
    generate_parser.add_argument("--output", type=pathlib.Path, required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("document", type=pathlib.Path)
    execute_parser = sub.add_parser("execute-fake")
    execute_parser.add_argument("document", type=pathlib.Path)
    args = parser.parse_args()
    if args.action == "generate":
        documents = generate(load_json(args.instance), load_json(args.plan))
        result = write_bundle(args.output, documents, pathlib.Path(__file__).resolve())
    elif args.action == "validate":
        result = validate_document(load_json(args.document))
    else:
        result = execute_fake(load_json(args.document))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
