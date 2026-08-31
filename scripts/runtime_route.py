#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reference model only; its synthetic atomic effects are not a Linux API.

The matching kernel review rejects using this model as a hardware adapter
contract. ModelEngine requires an explicitly model-only backend. The public
entry point cannot execute this model or accept evidence. See the target review
and runtime_inventory.py for actual read-only observations.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Protocol

CONTRACT = "rp1-gpclk-runtime-route-v2"
ROUTES = ("gpio4", "gpio20")
SERVICES = ("wsprrypi.service", "soapyremote-server.service")
TOKEN = r"[A-Za-z0-9][A-Za-z0-9._-]{7,63}"
SHA = r"[0-9a-f]{64}"
BOOT = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
MAX_INPUT = 16384
MAX_LEDGER = 4 * 1024 * 1024
BLOCKERS = (
    "reviewed-configfs-removal-errors-not-propagated",
    "runtime-switch-adapter-not-implemented",
)


class Rejected(ValueError):
    """Unknown, unsafe or inconsistent state; no speculative recovery."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def matches(pattern: str, value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def decode(payload: bytes) -> object:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate-json-key")
            result[key] = value
        return result
    try:
        return json.loads(payload, object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              Rejected("nonfinite-json-number")))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Rejected("invalid-json") from error


def request(value: object) -> dict:
    require(isinstance(value, dict), "request-not-object")
    require(type(value.get("schemaVersion")) is int and value["schemaVersion"] == 2,
            "unsupported-schema")
    operation = value.get("operation")
    require(operation in ("query", "preflight", "switch", "recover"),
            "unsupported-operation")
    fields = {"schemaVersion", "operation"}
    if operation in ("preflight", "switch"):
        fields.add("route")
        require(value.get("route") in ROUTES, "unsupported-route")
    if operation in ("switch", "recover"):
        fields.update(("execute", "requestId", "actor"))
        require(value.get("execute") is True, "explicit-execution-required")
        require(matches(TOKEN, value.get("requestId")), "invalid-request-id")
        require(matches(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{1,127}", value.get("actor")),
                "invalid-actor")
    if operation == "recover":
        fields.update(("transactionId", "strategy"))
        require(matches(TOKEN, value.get("transactionId")), "invalid-transaction-id")
        require(value.get("strategy") in ("resume", "rollback"), "invalid-strategy")
    require(set(value) == fields, "unexpected-request-fields")
    return dict(value)


def binding(value: object) -> dict:
    """Validate identity syntax, not authenticity; adapter must attest bytes."""
    fields = {"schemaVersion", "classification", "qualification", "managerCommit",
              "managerSha256", "moduleCommit", "moduleSha256", "moduleBuildSha256",
              "uapiSha256", "kernel", "kernelConfigSha256", "firmwareSha256", "routes"}
    require(isinstance(value, dict) and set(value) == fields, "binding-fields")
    require(type(value["schemaVersion"]) is int and value["schemaVersion"] == 2,
            "binding-version")
    require(value["classification"] == "Experimental" and value["qualification"] is False,
            "binding-classification")
    for name in fields:
        if name.endswith("Sha256"):
            require(matches(SHA, value[name]), "binding-hash")
        if name.endswith("Commit"):
            require(matches(r"[0-9a-f]{40}", value[name]), "binding-commit")
    require(matches(r"[A-Za-z0-9][A-Za-z0-9.+_-]{0,127}", value["kernel"]), "binding-kernel")
    require(isinstance(value["routes"], dict) and set(value["routes"]) == set(ROUTES),
            "both-route-identities-required")
    for route, entry in value["routes"].items():
        require(isinstance(entry, dict) and set(entry) == {"overlaySha256", "compatibilityId"},
                "route-binding-fields")
        require(matches(SHA, entry["overlaySha256"]), "overlay-hash")
        require(matches(r"[A-Za-z0-9._+-]{1,128}", entry["compatibilityId"])
                and f"-{route}-" in entry["compatibilityId"], "route-compatibility")
    require(value["routes"]["gpio4"]["overlaySha256"] !=
            value["routes"]["gpio20"]["overlaySha256"], "duplicate-overlay-identity")
    return json.loads(canonical(value))


@dataclass(frozen=True)
class Observation:
    """Authenticated adapter observation, never accepted over stdin/socket.

    revision is an adapter compare-and-effect epoch, NOT ABI generation.
    safe booleans require positive supported evidence; unknown is rejected.
    """
    boot_id: str
    binding_sha256: str
    revision: int
    foreign_sha256: str
    boot_route: str | None
    origin: str
    route: str | None
    module_route: str | None
    overlay_sha256: str | None
    module_sha256: str | None
    compatibility_id: str | None
    overlay_owner: str | None
    top_owned: bool
    admission_closed: bool
    services: tuple[str, str]
    owner_present: bool
    lease_present: bool
    operation_live: bool
    load_live: bool
    pending_work: bool
    cleanup_fault: bool
    gpio_safe: bool
    clock_quiescent: bool
    dma_quiescent: bool
    stable: bool
    adoption: str | None = None
    adoption_sha256: str | None = None

    @classmethod
    def read(cls, value: dict) -> Observation:
        require(isinstance(value, dict) and set(value) == set(cls.__dataclass_fields__),
                "observation-fields")
        require(isinstance(value["services"], list) and len(value["services"]) == 2,
                "observation-services")
        return cls(**{**value, "services": tuple(value["services"])})

    def check(self, identity: dict) -> None:
        require(matches(BOOT, self.boot_id) and matches(SHA, self.foreign_sha256),
                "observation-provenance")
        require(type(self.revision) is int and 0 <= self.revision < 2**63,
                "observation-revision")
        require(self.binding_sha256 == digest(identity), "identity-mismatch")
        require(self.boot_route in (*ROUTES, None), "unknown-boot-route")
        require(self.origin in ("runtime", "none", "firmware", "foreign"), "unknown-origin")
        require(self.boot_route is None and self.origin != "firmware", "migration-required")
        require(self.origin != "foreign", "foreign-overlay")
        require(self.route in (*ROUTES, None) and self.module_route in (*ROUTES, None),
                "ambiguous-route")
        require(type(self.services) is tuple and len(self.services) == 2 and
                all(s in ("active", "inactive", "failed") for s in self.services),
                "unknown-service-state")
        for name in ("top_owned", "admission_closed", "owner_present", "lease_present",
                     "operation_live", "load_live", "pending_work", "cleanup_fault",
                     "gpio_safe", "clock_quiescent", "dma_quiescent", "stable"):
            require(type(getattr(self, name)) is bool, "unknown-safety-observation")
        require(not any((self.owner_present, self.lease_present, self.operation_live,
                         self.load_live, self.pending_work, self.cleanup_fault)), "unsafe-output-state")
        require(all((self.gpio_safe, self.clock_quiescent, self.dma_quiescent, self.stable)),
                "cleanup-not-proven")
        require(self.top_owned, "stacked-or-unowned-overlay")
        if self.route is None:
            require(self.origin == "none" and self.overlay_sha256 is None and
                    self.overlay_owner is None and self.module_route is None, "zero-route-mismatch")
        else:
            require(self.origin == "runtime" and matches(TOKEN, self.overlay_owner),
                    "runtime-ownership-missing")
            require(self.overlay_sha256 == identity["routes"][self.route]["overlaySha256"],
                    "overlay-identity-mismatch")
        if self.module_route is None:
            require(self.module_sha256 is None and self.compatibility_id is None,
                    "unloaded-module-mismatch")
        else:
            require(self.module_route == self.route and self.module_sha256 == identity["moduleSha256"]
                    and self.compatibility_id == identity["routes"][self.route]["compatibilityId"],
                    "module-identity-mismatch")
        require(self.adoption is None or matches(TOKEN, self.adoption), "invalid-adoption")
        require((self.adoption is None and self.adoption_sha256 is None) or
                (self.adoption is not None and matches(SHA, self.adoption_sha256)), "invalid-adoption-digest")


def adoption_digest(state: Observation, token: str) -> str:
    return digest({"bootId": state.boot_id, "bindingSha256": state.binding_sha256,
                   "route": state.route, "overlayOwner": state.overlay_owner,
                   "transactionId": token})


def require_adoption(state: Observation) -> None:
    require(state.adoption is not None and
            state.adoption_sha256 == adoption_digest(state, state.adoption), "stale-adoption")


def plan(state: Observation, target: str | None) -> list[str]:
    require(target in (*ROUTES, None), "invalid-target")
    actions = ["inhibit"]
    if state.route != target:
        if state.module_route is not None:
            actions.append("unload")
        if state.route is not None:
            actions.append("remove")
        if target is not None:
            actions.extend(("apply", "load"))
    elif target is not None and state.module_route is None:
        actions.append("load")
    return actions + ["adopt", "restore-services"]


def transition(state: Observation, action: str, target: str | None,
               transaction: str, services: tuple[str, str], identity: dict) -> Observation:
    state.check(identity)
    require(matches(TOKEN, transaction), "invalid-transaction-id")
    changes = {"revision": state.revision + 1}
    if action == "inhibit":
        changes.update(admission_closed=True, services=("inactive", "inactive"))
    else:
        require(state.admission_closed and state.services == ("inactive", "inactive"),
                "administrative-exclusion-lost")
        if action == "unload":
            require(state.module_route is not None, "module-already-absent")
            changes.update(module_route=None, module_sha256=None, compatibility_id=None)
        elif action == "remove":
            require(state.module_route is None and state.route is not None, "unsafe-overlay-removal")
            changes.update(route=None, origin="none", overlay_sha256=None, overlay_owner=None,
                           adoption=None, adoption_sha256=None)
        elif action == "apply":
            require(state.route is None and target in ROUTES, "unsafe-overlay-application")
            changes.update(route=target, origin="runtime", overlay_owner=transaction,
                           overlay_sha256=identity["routes"][target]["overlaySha256"])
        elif action == "load":
            require(state.route == target and target in ROUTES and state.module_route is None,
                    "unsafe-module-load")
            changes.update(module_route=target, module_sha256=identity["moduleSha256"],
                           compatibility_id=identity["routes"][target]["compatibilityId"])
        elif action == "adopt":
            require(state.route == target and state.module_route == target, "unreconciled-route")
            changes.update(adoption=transaction, adoption_sha256=adoption_digest(state, transaction))
        elif action == "restore-services":
            require(state.adoption == transaction and state.route == target and
                    state.module_route == target, "unreconciled-restoration")
            require_adoption(state)
            changes.update(services=services)
        else:
            raise Rejected("unknown-effect")
    result = replace(state, **changes)
    result.check(identity)
    return result


class ModelAdapter(Protocol):
    """Synthetic reference semantics, deliberately NOT implementable by shell.

    The model assumes atomic full-state comparison and successor observations.
    Linux only supplies narrower per-operation synchronization. Do not fabricate
    a revision counter or echo the predicted state to adapt Linux to this type.
    """
    model_only: bool
    def observe(self) -> Observation: ...
    def model_effect(self, before: Observation, after: Observation, action: str) -> None: ...


class Ledger:
    """Bounded append-only hash chain in an existing private directory.

    Hashes detect corruption, not malicious rewriting by the owning user.
    No pruning, truncation, symlink following, or automatic corruption repair.
    The same inode holds the nonblocking flock for the whole transaction.
    """
    def __init__(self, directory: Path):
        self.directory = directory
        self.fd = None
        self.directory_fd = None
        self.records = []

    @contextmanager
    def locked(self):
        require(self.fd is None, "ledger-already-locked")
        # Resolve parents through directory descriptors, without following links.
        path = self.directory.absolute()
        parent = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        try:
            for part in path.parts[1:]:
                require(part not in (".", ".."), "unsafe-ledger-path")
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                os.close(parent)
                parent = child
            metadata = os.fstat(parent)
            require(metadata.st_uid == os.geteuid() and stat.S_IMODE(metadata.st_mode) == 0o700,
                    "ledger-directory-not-private")
            fd = os.open("events.jsonl", os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW,
                         0o600, dir_fd=parent)
            try:
                metadata = os.fstat(fd)
                require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1 and
                        metadata.st_uid == os.geteuid() and stat.S_IMODE(metadata.st_mode) == 0o600,
                        "unsafe-ledger-file")
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as error:
                    raise Rejected("transaction-busy") from error
                os.fsync(parent)
                self.fd = fd
                self.directory_fd = parent
                self.records = self._read()
                yield self
            finally:
                self.fd = None
                self.directory_fd = None
                os.close(fd)
        finally:
            os.close(parent)

    def _read(self) -> list[dict]:
        require(os.fstat(self.fd).st_size <= MAX_LEDGER, "ledger-full")
        os.lseek(self.fd, 0, os.SEEK_SET)
        chunks = []
        size = 0
        while True:
            chunk = os.read(self.fd, min(65536, MAX_LEDGER + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            require(size <= MAX_LEDGER, "ledger-full")
        payload = b"".join(chunks)
        require(not payload or payload.endswith(b"\n"), "incomplete-ledger-write")
        records = []
        previous = "0" * 64
        for line in payload.splitlines():
            require(len(line) <= MAX_INPUT, "oversized-ledger-record")
            item = decode(line)
            require(isinstance(item, dict) and set(item) == {"sequence", "previous", "record", "sha256"},
                    "ledger-fields")
            require(type(item["sequence"]) is int and item["sequence"] == len(records) and
                    item["previous"] == previous, "ledger-chain")
            require(item["sha256"] == digest({k: v for k, v in item.items() if k != "sha256"}),
                    "ledger-digest")
            records.append(item)
            previous = item["sha256"]
        return records

    def append(self, record: dict) -> None:
        require(self.fd is not None, "ledger-not-locked")
        opened = os.fstat(self.fd)
        linked = os.stat("events.jsonl", dir_fd=self.directory_fd, follow_symlinks=False)
        require((opened.st_dev, opened.st_ino) == (linked.st_dev, linked.st_ino) and
                opened.st_nlink == 1 and stat.S_IMODE(opened.st_mode) == 0o600 and
                opened.st_uid == os.geteuid(), "ledger-replaced-or-exposed")
        item = {"sequence": len(self.records), "previous": self.records[-1]["sha256"]
                if self.records else "0" * 64, "record": record}
        item["sha256"] = digest(item)
        payload = canonical(item) + b"\n"
        require(len(payload) <= MAX_INPUT and os.fstat(self.fd).st_size + len(payload) <= MAX_LEDGER,
                "ledger-full")
        # A short or interrupted write is retained and blocks future operation.
        require(os.write(self.fd, payload) == len(payload), "short-ledger-write")
        os.fsync(self.fd)
        self.records.append(json.loads(canonical(item)))


class ModelEngine:
    """Reference model for failure exploration, not a future Linux executor."""
    def __init__(self, identity: dict, adapter: ModelAdapter, ledger: Ledger):
        require(getattr(adapter, "model_only", False) is True, "model-adapter-required")
        self.identity = binding(identity)
        self.adapter = adapter
        self.ledger = ledger

    def _state(self) -> Observation:
        state = self.adapter.observe()
        require(type(state) is Observation, "invalid-adapter-observation")
        state.check(self.identity)
        return state

    def _history(self) -> dict[str, dict]:
        latest = {}
        self.used_requests = {}
        for item in self.ledger.records:
            record = item["record"]
            fields = {"request", "initial", "current", "target", "actions", "position",
                      "phase", "direction", "recoveryRequest"}
            require(isinstance(record, dict) and set(record) == fields, "transaction-fields")
            original = request(record["request"])
            require(original["operation"] == "switch", "transaction-request")
            initial = Observation.read(record["initial"])
            current = Observation.read(record["current"])
            initial.check(self.identity)
            current.check(self.identity)
            require(initial.boot_id == current.boot_id and initial.foreign_sha256 == current.foreign_sha256,
                    "transaction-provenance")
            require(record["direction"] in ("forward", "rollback") and
                    record["phase"] in ("ready", "intent", "complete"), "transaction-phase")
            require(record["target"] == (original["route"] if record["direction"] == "forward"
                                         else initial.route), "transaction-target")
            require(isinstance(record["actions"], list) and 3 <= len(record["actions"]) <= 7 and
                    all(a in ("inhibit", "unload", "remove", "apply", "load", "adopt", "restore-services")
                        for a in record["actions"]), "transaction-actions")
            require(type(record["position"]) is int and 0 <= record["position"] <= len(record["actions"]),
                    "transaction-position")
            require((record["phase"] == "complete") == (record["position"] == len(record["actions"])),
                    "transaction-completion")
            if record["recoveryRequest"] is not None:
                recovery = request(record["recoveryRequest"])
                require(recovery["operation"] == "recover" and recovery["transactionId"] == original["requestId"],
                        "recovery-attribution")
            for attributed in (original, record["recoveryRequest"]):
                if attributed is not None:
                    prior = self.used_requests.setdefault(attributed["requestId"], attributed)
                    require(prior == attributed, "request-id-conflict")
            previous = latest.get(original["requestId"])
            if previous is None:
                require(not any(r["phase"] != "complete" for r in latest.values()),
                        "overlapping-transactions")
                require(record["phase"] == "ready" and record["position"] == 0 and
                        record["direction"] == "forward" and record["recoveryRequest"] is None and
                        record["current"] == record["initial"] and initial.route == initial.module_route and
                        record["actions"] == plan(initial, original["route"]), "invalid-initial-record")
                if initial.route is not None:
                    require_adoption(initial)
            else:
                require(previous["phase"] != "complete", "modified-terminal-transaction")
                candidates = []
                if previous["phase"] in ("ready", "intent"):
                    candidates.append({**previous, "phase": "intent"})
                if previous["phase"] == "intent":
                    candidates.append(self._advance(previous, self._expected(previous)))
                if record["recoveryRequest"] is not None:
                    bases = [previous]
                    if previous["phase"] == "intent":
                        bases.append(self._advance(previous, self._expected(previous)))
                    for base in bases:
                        base = {**base, "recoveryRequest": record["recoveryRequest"]}
                        candidates.append(base)
                        if record["recoveryRequest"]["strategy"] == "rollback" and base["direction"] == "forward":
                            state = Observation.read(base["current"])
                            candidates.append({**base, "direction": "rollback", "target": initial.route,
                                               "actions": plan(state, initial.route), "position": 0, "phase": "ready"})
                require(record in candidates, "invalid-journal-transition")
            latest[original["requestId"]] = record
        return latest

    def execute(self, value: dict) -> dict:
        incoming = request(value)
        require(incoming["operation"] in ("switch", "recover"), "engine-mutation-only")
        with self.ledger.locked():
            history = self._history()
            used = self.used_requests.get(incoming["requestId"])
            require(used is None or used == incoming, "request-id-conflict")
            pending = [r for r in history.values() if r["phase"] != "complete"]
            require(len(pending) <= 1, "ambiguous-pending-transactions")
            if incoming["operation"] == "switch":
                old = history.get(incoming["requestId"])
                if old is not None:
                    require(old["request"] == incoming, "request-id-conflict")
                    require(not pending and old["phase"] == "complete", "recovery-required")
                    require(self._state() == Observation.read(old["current"]), "stale-completion")
                    return old
                require(not pending, "recovery-required")
                state = self._state()
                require(state.route == state.module_route, "initial-binding-incomplete")
                if state.route is not None:
                    require_adoption(state)
                record = {"request": incoming, "initial": asdict(state), "current": asdict(state),
                          "target": incoming["route"], "actions": plan(state, incoming["route"]),
                          "position": 0, "phase": "ready", "direction": "forward", "recoveryRequest": None}
                # Normalize tuples to JSON arrays before persisting or reading.
                record = json.loads(canonical(record))
                self.ledger.append(record)
            else:
                completed = history.get(incoming["transactionId"])
                if completed is not None and completed["phase"] == "complete":
                    require(not pending and completed["recoveryRequest"] == incoming,
                            "no-matching-pending-transaction")
                    require(self._state() == Observation.read(completed["current"]), "stale-completion")
                    return completed
                require(len(pending) == 1 and pending[0]["request"]["requestId"] == incoming["transactionId"],
                        "no-matching-pending-transaction")
                record = pending[0]
                record = {**record, "recoveryRequest": incoming}
                record = self._resolve_intent(record)
                if incoming["strategy"] == "rollback" and record["direction"] != "rollback":
                    state = Observation.read(record["current"])
                    record = {**record, "direction": "rollback", "target": record["initial"]["route"],
                              "actions": plan(state, record["initial"]["route"]), "position": 0, "phase": "ready"}
                self.ledger.append(record)
            return self._run(record)

    def _expected(self, record: dict) -> Observation:
        return transition(Observation.read(record["current"]), record["actions"][record["position"]],
                          record["target"], record["request"]["requestId"],
                          tuple(record["initial"]["services"]), self.identity)

    def _advance(self, record: dict, state: Observation) -> dict:
        position = record["position"] + 1
        return {**record, "current": json.loads(canonical(asdict(state))), "position": position,
                "phase": "complete" if position == len(record["actions"]) else "ready"}

    def _resolve_intent(self, record: dict) -> dict:
        actual = self._state()
        before = Observation.read(record["current"])
        if record["phase"] == "intent" and actual == self._expected(record):
            return self._advance(record, actual)
        require(actual == before, "unattributable-state-change")
        return record

    def _run(self, record: dict) -> dict:
        while record["phase"] != "complete":
            before = Observation.read(record["current"])
            require(self._state() == before, "unattributable-state-change")
            after = self._expected(record)
            record = {**record, "phase": "intent"}
            self.ledger.append(record)
            self.adapter.model_effect(before, after, record["actions"][record["position"]])
            require(self._state() == after, "effect-readback-mismatch")
            record = self._advance(record, after)
            self.ledger.append(record)
        return record


def public_response(value: object) -> dict:
    """No adapter selection, evidence input, deployment, or override is exposed."""
    parsed = request(value)
    return {"schemaVersion": 2, "contract": CONTRACT, "operation": parsed["operation"],
            "status": "blocked", "classification": "Experimental", "qualification": False,
            "mutationAvailable": False, "blockers": list(BLOCKERS)}
