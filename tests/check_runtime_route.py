#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline only: fake effects, private temporary journals, no target commands."""
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import runtime_route as rt


def identity():
    return {"schemaVersion": 2, "classification": "Experimental", "qualification": False,
            "managerCommit": "1" * 40, "moduleCommit": "2" * 40,
            "managerSha256": "3" * 64, "moduleSha256": "4" * 64,
            "moduleBuildSha256": "5" * 64, "uapiSha256": "6" * 64,
            "kernel": "fixture-kernel", "kernelConfigSha256": "7" * 64,
            "firmwareSha256": "8" * 64,
            "routes": {route: {"overlaySha256": str(index) * 64,
                                "compatibilityId": f"fixture-{route}-candidate"}
                       for index, route in enumerate(rt.ROUTES, 1)}}


def initial(route="gpio4"):
    ids = identity()
    state = rt.Observation(
        boot_id="11111111-2222-3333-4444-555555555555", binding_sha256=rt.digest(ids),
        revision=0, foreign_sha256="a" * 64, boot_route=None,
        origin="runtime" if route else "none", route=route, module_route=route,
        overlay_sha256=ids["routes"][route]["overlaySha256"] if route else None,
        module_sha256=ids["moduleSha256"] if route else None,
        compatibility_id=ids["routes"][route]["compatibilityId"] if route else None,
        overlay_owner="old-overlay-0001" if route else None, top_owned=True,
        admission_closed=False, services=("active", "inactive"),
        owner_present=False, lease_present=False, operation_live=False, load_live=False,
        pending_work=False, cleanup_fault=False, gpio_safe=True, clock_quiescent=True,
        dma_quiescent=True, stable=True)
    if route is not None:
        state = replace(state, adoption="adoption-00000001",
                        adoption_sha256=rt.adoption_digest(state, "adoption-00000001"))
    return state


def switch(route="gpio20", number=1):
    return {"schemaVersion": 2, "operation": "switch", "route": route,
            "execute": True, "requestId": f"switch-{number:08d}", "actor": "fixture.operator"}


def recover(strategy="resume", number=1):
    return {"schemaVersion": 2, "operation": "recover", "execute": True,
            "requestId": f"recover-{number:08d}", "transactionId": "switch-00000001",
            "strategy": strategy, "actor": "fixture.recovery"}


class Crash(BaseException):
    pass


class Fake:
    def __init__(self, state=None):
        self.state = state or initial()
        self.effects = []
        self.fail_at = None
        self.fail_after = False
        self.corrupt_at = None
        self.race_at = None

    def observe(self):
        return self.state

    def compare_effect(self, before, after, action):
        # Independent admission and ordering assertions, not transition().
        if action == self.race_at:
            self.state = replace(self.state, revision=self.state.revision + 1)
        rt.require(self.state == before, "fake-external-race")
        if action == self.fail_at and not self.fail_after:
            raise Crash(action)
        if action != "inhibit":
            assert before.admission_closed
            assert before.services == ("inactive", "inactive")
        if action == "remove":
            assert before.module_route is None
        if action == "apply":
            assert before.route is None and before.module_route is None
        if action == "load":
            assert before.route in rt.ROUTES and before.module_route is None
            assert after.load_live is False and after.operation_live is False
        self.effects.append(action)
        self.state = after
        if action == self.corrupt_at:
            self.state = replace(after, module_sha256="f" * 64)
        if action == self.fail_at and self.fail_after:
            raise Crash(action)


class FailingLedger(rt.Ledger):
    def __init__(self, path, at, after):
        super().__init__(path)
        self.at, self.after, self.count = at, after, 0

    def append(self, record):
        self.count += 1
        if self.count == self.at and not self.after:
            raise Crash("before-journal-write")
        super().append(record)
        if self.count == self.at and self.after:
            raise Crash("after-journal-write")


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # /var on macOS is a symlink; pass the real private directory.
        self.path = Path(self.temp.name).resolve()
        self.path.chmod(0o700)
        self.fake = Fake()

    def engine(self, ledger=None):
        return rt.Engine(identity(), self.fake, ledger or rt.Ledger(self.path))

    def test_both_directions_and_same_route(self):
        first = self.engine().execute(switch())
        self.assertEqual(self.fake.effects, ["inhibit", "unload", "remove", "apply", "load", "adopt", "restore-services"])
        self.assertEqual(first["phase"], "complete")
        self.assertEqual(self.fake.state.route, "gpio20")
        self.assertEqual(self.fake.state.module_route, "gpio20")
        self.assertEqual(self.fake.state.overlay_sha256, "2" * 64)
        self.assertEqual(self.fake.state.services, ("active", "inactive"))
        self.assertTrue(self.fake.state.admission_closed)
        self.assertEqual(self.engine().execute(switch()), first)
        self.engine().execute(switch("gpio4", 2))
        self.assertEqual(self.fake.state.route, "gpio4")
        self.fake.effects.clear()
        self.engine().execute(switch("gpio4", 3))
        self.assertEqual(self.fake.effects, ["inhibit", "adopt", "restore-services"])
        with self.assertRaisesRegex(rt.Rejected, "stale-completion"):
            self.engine().execute(switch())

    def test_route_neutral_start(self):
        self.fake.state = initial(None)
        self.engine().execute(switch())
        self.assertEqual(self.fake.effects, ["inhibit", "apply", "load", "adopt", "restore-services"])
        self.assertIsNone(self.fake.state.boot_route)

    def test_every_effect_crash_resumes_without_duplicate_effect(self):
        actions = ["inhibit", "unload", "remove", "apply", "load", "adopt", "restore-services"]
        for action in actions:
            for after in (False, True):
                with self.subTest(action=action, after=after), tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp).resolve()
                    fake = Fake()
                    fake.fail_at, fake.fail_after = action, after
                    engine = rt.Engine(identity(), fake, rt.Ledger(path))
                    with self.assertRaises(Crash):
                        engine.execute(switch())
                    fake.fail_at = None
                    completed = rt.Engine(identity(), fake, rt.Ledger(path)).execute(recover())
                    self.assertEqual(completed["phase"], "complete")
                    self.assertEqual(fake.effects, actions)
                    self.assertEqual(fake.state.route, "gpio20")

    def test_every_journal_boundary_recovers(self):
        for index in range(1, 16):
            for after in (False, True):
                with self.subTest(write=index, after=after), tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp).resolve()
                    fake = Fake()
                    with self.assertRaises(Crash):
                        rt.Engine(identity(), fake, FailingLedger(path, index, after)).execute(switch())
                    ledger = rt.Ledger(path)
                    with ledger.locked():
                        last = ledger.records[-1]["record"] if ledger.records else None
                    incoming = switch() if last is None or last["phase"] == "complete" else recover()
                    rt.Engine(identity(), fake, rt.Ledger(path)).execute(incoming)
                    self.assertEqual(fake.state.route, "gpio20")
                    self.assertEqual(len(fake.effects), 7)

    def test_rollback_from_every_effect_boundary(self):
        for source in ("gpio4", None):
            actions = rt.plan(initial(source), "gpio20")
            for action in actions:
                for after in (False, True):
                    with self.subTest(source=source, action=action, after=after), tempfile.TemporaryDirectory() as tmp:
                        path = Path(tmp).resolve()
                        fake = Fake(initial(source))
                        fake.fail_at, fake.fail_after = action, after
                        with self.assertRaises(Crash):
                            rt.Engine(identity(), fake, rt.Ledger(path)).execute(switch())
                        prefix = (path / "events.jsonl").read_bytes()
                        fake.fail_at = None
                        result = rt.Engine(identity(), fake, rt.Ledger(path)).execute(recover("rollback"))
                        self.assertEqual(result["direction"], "rollback")
                        self.assertEqual(fake.state.route, source)
                        self.assertEqual(fake.state.module_route, source)
                        self.assertTrue(fake.state.admission_closed)
                        self.assertTrue((path / "events.jsonl").read_bytes().startswith(prefix))

    def test_unsafe_observations_have_no_effect(self):
        mutations = [dict(boot_route="gpio4"), dict(origin="firmware"), dict(origin="foreign"),
                     dict(origin="unknown"), dict(top_owned=False), dict(route="both"),
                     dict(module_route=None), dict(overlay_owner=None), dict(overlay_sha256="0" * 64),
                     dict(module_sha256="0" * 64), dict(compatibility_id="wrong"),
                     dict(binding_sha256="0" * 64), dict(services=("activating", "inactive")),
                     dict(adoption_sha256="0" * 64), dict(adoption=None, adoption_sha256=None)]
        for name in ("owner_present", "lease_present", "operation_live", "load_live",
                     "pending_work", "cleanup_fault"):
            mutations.append({name: True})
        for name in ("gpio_safe", "clock_quiescent", "dma_quiescent", "stable"):
            mutations.extend(({name: False}, {name: None}, {name: 1}))
        for changes in mutations:
            with self.subTest(changes=changes):
                self.fake.state = replace(initial(), **changes)
                with self.assertRaises(rt.Rejected):
                    self.engine().execute(switch())
                self.assertEqual(self.fake.effects, [])

    def test_pending_and_replay_conflicts(self):
        self.fake.fail_at = "unload"
        with self.assertRaises(Crash):
            self.engine().execute(switch())
        with self.assertRaisesRegex(rt.Rejected, "recovery-required"):
            self.engine().execute(switch(number=2))
        with self.assertRaisesRegex(rt.Rejected, "request-id-conflict"):
            self.engine().execute(switch("gpio4"))
        with self.assertRaisesRegex(rt.Rejected, "no-matching"):
            self.engine().execute({**recover(), "transactionId": "foreign-00000001"})

    def test_reboot_or_foreign_change_blocks_recovery(self):
        self.fake.fail_at = "remove"
        with self.assertRaises(Crash):
            self.engine().execute(switch())
        saved = self.fake.state
        for changes in (dict(boot_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
                        dict(foreign_sha256="b" * 64), dict(revision=999),
                        dict(owner_present=True), dict(admission_closed=False)):
            self.fake.state = replace(saved, **changes)
            count = len(self.fake.effects)
            with self.assertRaises(rt.Rejected):
                self.engine().execute(recover())
            self.assertEqual(len(self.fake.effects), count)

    def test_autoload_readback_or_compare_race_blocks(self):
        for attribute in ("corrupt_at", "race_at"):
            with self.subTest(attribute=attribute), tempfile.TemporaryDirectory() as tmp:
                fake = Fake()
                setattr(fake, attribute, "apply")
                with self.assertRaises(rt.Rejected):
                    rt.Engine(identity(), fake, rt.Ledger(Path(tmp).resolve())).execute(switch())
                self.assertNotIn("load", fake.effects)
                self.assertNotIn("restore-services", fake.effects)

    def test_failed_rollback_remains_recoverable(self):
        self.fake.fail_at = "load"
        with self.assertRaises(Crash):
            self.engine().execute(switch())
        self.fake.fail_at = "remove"
        with self.assertRaises(Crash):
            self.engine().execute(recover("rollback"))
        self.assertTrue(self.fake.state.admission_closed)
        self.fake.fail_at = None
        result = self.engine().execute(recover("rollback"))
        self.assertEqual(result["phase"], "complete")
        self.assertEqual(self.fake.state.route, "gpio4")
        self.assertEqual(self.engine().execute(recover("rollback")), result)

    def test_new_recovery_can_choose_rollback_but_cannot_reuse_id(self):
        self.fake.fail_at = "apply"
        with self.assertRaises(Crash):
            self.engine().execute(switch())
        with self.assertRaises(Crash):
            self.engine().execute(recover())
        with self.assertRaisesRegex(rt.Rejected, "request-id-conflict"):
            self.engine().execute(recover("rollback"))
        self.fake.fail_at = None
        result = self.engine().execute(recover("rollback", 2))
        self.assertEqual(result["direction"], "rollback")
        self.assertEqual(self.fake.state.route, "gpio4")

    def test_lock_and_private_journal(self):
        with rt.Ledger(self.path).locked():
            with self.assertRaisesRegex(rt.Rejected, "transaction-busy"):
                self.engine().execute(switch())
        self.assertEqual(self.fake.effects, [])
        self.path.chmod(0o755)
        with self.assertRaisesRegex(rt.Rejected, "not-private"):
            self.engine().execute(switch())
        self.path.chmod(0o700)

    def test_symlink_and_hardlink_rejection(self):
        file = self.path / "events.jsonl"
        other = self.path / "foreign"
        other.write_text("preserve\n")
        file.symlink_to(other)
        with self.assertRaises(OSError):
            self.engine().execute(switch())
        file.unlink()
        os.link(other, file)
        with self.assertRaises(rt.Rejected):
            self.engine().execute(switch())
        self.assertEqual(other.read_text(), "preserve\n")
        self.assertEqual(self.fake.effects, [])

    def test_replaced_journal_is_not_written_through_old_lock(self):
        ledger = rt.Ledger(self.path)
        with ledger.locked():
            file = self.path / "events.jsonl"
            file.rename(self.path / "historical.jsonl")
            file.write_text("preserve replacement\n")
            with self.assertRaisesRegex(rt.Rejected, "ledger-replaced"):
                ledger.append({"invalid": "unused"})
            self.assertEqual(file.read_text(), "preserve replacement\n")
            self.assertEqual((self.path / "historical.jsonl").read_bytes(), b"")

    def test_ledger_capacity_and_truncated_write(self):
        saved = rt.MAX_LEDGER
        rt.MAX_LEDGER = 1
        try:
            with self.assertRaisesRegex(rt.Rejected, "ledger-full"):
                self.engine().execute(switch())
            self.assertEqual(self.fake.effects, [])
        finally:
            rt.MAX_LEDGER = saved
        write = os.write
        def partial(fd, payload):
            return write(fd, payload[:10])
        rt.os.write = partial
        try:
            with self.assertRaisesRegex(rt.Rejected, "short-ledger-write"):
                self.engine().execute(switch())
        finally:
            rt.os.write = write
        with self.assertRaisesRegex(rt.Rejected, "incomplete-ledger-write"):
            self.engine().execute(switch())
        self.assertEqual(self.fake.effects, [])

    def test_torn_or_corrupt_ledger_never_repaired(self):
        self.engine().execute(switch())
        file = self.path / "events.jsonl"
        original = file.read_bytes()
        for broken in (original[:-1], original.replace(b'"inhibit"', b'"unknown"', 1), b"{}\n"):
            file.write_bytes(broken)
            count = len(self.fake.effects)
            with self.assertRaises(rt.Rejected):
                self.engine().execute(switch(number=2))
            self.assertEqual(file.read_bytes(), broken)
            self.assertEqual(len(self.fake.effects), count)

    def test_rehashed_semantic_corruption_is_rejected(self):
        self.fake.fail_at = "unload"
        with self.assertRaises(Crash):
            self.engine().execute(switch())
        file = self.path / "events.jsonl"
        records = [json.loads(line) for line in file.read_text().splitlines()]
        records[-1]["record"]["actions"] = ["inhibit", "adopt", "restore-services"]
        records[-1]["sha256"] = rt.digest({k: v for k, v in records[-1].items() if k != "sha256"})
        file.write_bytes(b"\n".join(rt.canonical(r) for r in records) + b"\n")
        count = len(self.fake.effects)
        with self.assertRaises(rt.Rejected):
            self.engine().execute(recover())
        self.assertEqual(len(self.fake.effects), count)

    def test_binding_and_request_validation(self):
        for key in identity():
            bad = identity()
            bad.pop(key)
            with self.subTest(key=key), self.assertRaises(rt.Rejected):
                rt.binding(bad)
        bad = identity()
        bad["routes"]["gpio20"]["overlaySha256"] = "1" * 64
        with self.assertRaises(rt.Rejected):
            rt.binding(bad)
        for invalid in (None, [], {**switch(), "route": "gpio5"}, {**switch(), "schemaVersion": True},
                        {**switch(), "actor": 12345}, {**switch(), "requestId": 12345678},
                        {**switch(), "execute": 1}, {**switch(), "command": "arbitrary"}):
            with self.subTest(invalid=invalid), self.assertRaises(rt.Rejected):
                rt.request(invalid)
        for invalid in (b'{"operation":"query","operation":"switch"}', b'{"a":NaN}', b'\xff'):
            with self.assertRaises(rt.Rejected):
                rt.decode(invalid)

    def test_public_entrypoint_is_unconditionally_blocked(self):
        entry = ROOT / "scripts/rp1-gpclk-runtime-route.py"
        for value in ({"schemaVersion": 2, "operation": "query"},
                      {"schemaVersion": 2, "operation": "preflight", "route": "gpio4"},
                      switch(), recover()):
            result = subprocess.run([sys.executable, str(entry)], input=json.dumps(value),
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            reply = json.loads(result.stdout)
            self.assertEqual(reply["status"], "blocked")
            self.assertFalse(reply["mutationAvailable"])
            self.assertFalse(reply["qualification"])
            self.assertEqual(reply["blockers"], list(rt.BLOCKERS))
        result = subprocess.run([sys.executable, str(entry), "--execute"], input="{}",
                                capture_output=True, text=True, check=False)
        self.assertEqual(json.loads(result.stdout)["status"], "rejected")
        result = subprocess.run([sys.executable, str(entry)], input="x" * (rt.MAX_INPUT + 1),
                                capture_output=True, text=True, check=False)
        self.assertEqual(json.loads(result.stdout)["error"], "request-too-large")

    def test_schemas(self):
        protocol = json.loads((ROOT / "schema/rp1-gpclk-runtime-route-v2.schema.json").read_text())
        bindings = json.loads((ROOT / "schema/rp1-gpclk-runtime-binding-v2.schema.json").read_text())
        for name in ("query", "preflight", "switch", "recover", "blocked", "rejected"):
            self.assertFalse(protocol["$defs"][name]["additionalProperties"])
        self.assertFalse(bindings["additionalProperties"])
        self.assertEqual(set(bindings["properties"]["routes"]["required"]), set(rt.ROUTES))
        try:
            import jsonschema
        except ImportError:
            self.skipTest("JSON Schema validation needs jsonschema; structural checks passed")
        jsonschema.Draft202012Validator.check_schema(protocol)
        jsonschema.Draft202012Validator.check_schema(bindings)
        validator = jsonschema.Draft202012Validator(protocol)
        binding_validator = jsonschema.Draft202012Validator(bindings)
        binding_validator.validate(identity())
        accepted = [{"schemaVersion": 2, "operation": "query"},
                    {"schemaVersion": 2, "operation": "preflight", "route": "gpio20"},
                    switch(), recover()]
        for value in accepted:
            validator.validate(value)
            validator.validate(rt.public_response(value))
        invalid = [{**switch(), key: value} for key, value in (
            ("schemaVersion", True), ("route", "gpio5"), ("requestId", 12345678),
            ("requestId", "switch-00000001\n"), ("actor", "valid.actor\n"),
            ("execute", 1), ("unexpected", "field"))]
        for value in invalid:
            with self.subTest(value=value):
                self.assertFalse(validator.is_valid(value))
                with self.assertRaises(rt.Rejected):
                    rt.request(value)
        for key in identity():
            malformed = identity()
            malformed.pop(key)
            self.assertFalse(binding_validator.is_valid(malformed))
        for field in ("managerCommit", "managerSha256", "kernel"):
            malformed = identity()
            malformed[field] += "\n"
            self.assertFalse(binding_validator.is_valid(malformed))
        rejected = {"schemaVersion": 2, "contract": rt.CONTRACT, "operation": None,
                    "status": "rejected", "classification": "Experimental", "qualification": False,
                    "mutationAvailable": False, "error": "invalid-json"}
        validator.validate(rejected)


if __name__ == "__main__":
    unittest.main()
