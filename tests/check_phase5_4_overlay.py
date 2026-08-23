#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline Phase 5.4 overlay identity and route-transition checks."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

admin = load("rp1_admin_phase54", ROOT / "scripts/rp1-gpclk-admin.py")
builder = load("rp1_builder_phase54", ROOT / "scripts/build_release.py")
contract = json.loads((ROOT / "release/overlay-contract-v1.json").read_text())
assert contract["selection"] == {"exactlyOne": True, "arbitraryGpioParameter": False,
                                  "automaticSubstitution": False, "hotMutation": False}
assert contract["routeChange"] == admin.ROUTE_CHANGE_STEPS
assert all(contract["evidenceIndependence"].values())
assert set(contract["routes"]) == set(admin.ROUTES) == {"gpio4", "gpio20"}
dtc = shutil.which("dtc")
if not dtc:
    raise SystemExit("dtc is required for Phase 5.4 deterministic overlay validation")
shared = contract["sharedIdentity"]
compiled = {}
endpoint_names = set()
with tempfile.TemporaryDirectory() as temporary:
    out = pathlib.Path(temporary)
    for route, identity in contract["routes"].items():
        source = ROOT / identity["source"]
        text = source.read_text()
        endpoint_names.add(identity["endpointName"])
        other = "gpio20" if route == "gpio4" else "gpio4"
        required = (f'{identity["endpointLabel"]}: {identity["endpointName"]}',
                    f'compatible = "{shared["compatible"]}"',
                    f'wsprrypi,route = <{identity["routeId"]}>',
                    f'wsprrypi,pin = <{identity["pin"]}>',
                    f'clocks = <&{shared["clockProvider"]} {shared["clockId"]}>',
                    f'dmas = <&{shared["dmaProvider"]} {shared["dmaId"]}>',
                    'reg-names = "tick-dma0", "dma-tick0"',
                    'pinctrl-names = "default", "active", "safe"',
                    'function = "gpio"', 'input-enable;', 'bias-disable;',
                    'function = "gpclk0"', 'drive-strength = <2>')
        assert all(token in text for token in required)
        assert f'pins = "{route}"' in text and f'pins = "{other}"' not in text
        assert "__overrides__" not in text
        first, second = out / f"{route}-1.dtbo", out / f"{route}-2.dtbo"
        builder.build_dtbo(source, first, dtc)
        builder.build_dtbo(source, second, dtc)
        assert first.read_bytes() == second.read_bytes()
        decompiled = subprocess.check_output([dtc, "-I", "dtb", "-O", "dts", str(first)],
                                             text=True, stderr=subprocess.DEVNULL)
        for token in (shared["compatible"], identity["endpointName"], "tick-dma0",
                      "dma-tick0", "gpclk", "default", "active", "safe", route):
            assert token in decompiled
        numeric = {"gpio4": ("0x01", "0x04"), "gpio20": ("0x02", "0x14")}[route]
        for token in (f"wsprrypi,route = <{numeric[0]}>", f"wsprrypi,pin = <{numeric[1]}>",
                      "reg = <0xc0 0x40174024 0x00 0x08 0xc0 0x40158000 0x00 0x08>"):
            assert token in decompiled
        # dtc 1.8 may retain symbolic external phandles while dtc 1.7 emits
        # the canonical unresolved value and records the provider in
        # __fixups__. Accept both renderings, but always require the exact
        # provider/property fixup so a numeric placeholder cannot pass alone.
        assert ("dmas = <&rp1_dma>, <0x30>" in decompiled or
                "dmas = <0xffffffff 0x30>" in decompiled)
        assert ("clocks = <&rp1_clocks>, <0x21>" in decompiled or
                "clocks = <0xffffffff 0x21>" in decompiled)
        for token in ("rp1_dma =", f'{identity["endpointName"]}:dmas:0',
                      "rp1_clocks =", f'{identity["endpointName"]}:clocks:0'):
            assert token in decompiled
        compiled[route] = (hashlib.sha256(source.read_bytes()).hexdigest(),
                           hashlib.sha256(first.read_bytes()).hexdigest())
assert compiled["gpio4"] != compiled["gpio20"]
assert endpoint_names == {"rp1-gpclk-dkms-gpio4", "rp1-gpclk-dkms-gpio20"}
combined = "\n".join((ROOT / contract["routes"][route]["source"]).read_text()
                     for route in ("gpio4", "gpio20"))
assert combined.count('compatible = "wsprrypi,rp1-gpclk-dkms-v1"') == 2

snapshot = {field: False for field in ("moduleLoaded", "endpointBound", "endpointOpen",
            "ownerPresent", "generationActive", "callbackPending", "dmaActive",
            "clockPrepared", "clockEnabled", "cleanupFault", "routeConflict",
            "persistentConflict", "duplicateMarker", "runtimeOverlayConflict", "endpointBusy")}
snapshot.update({field: True for field in ("liveEligibilityDisabled", "gpio4Safe",
                "gpio20Safe", "oldBindingCleanupProven", "artifactIdentityValid",
                "compatibilityIdentityValid", "enrollmentPolicyRequiresRenewal")})
snapshot["configurationOwnershipKnown"] = True
snapshot["currentRoute"] = "gpio4"
plan = admin.route_change_plan(snapshot, "gpio20")
assert plan["steps"] == contract["routeChange"]
assert plan["liveOutput"] is plan["persistentMutation"] is plan["automaticSubstitution"] is False
assert plan["renewedEnrollmentRequired"] is True
for field in tuple(snapshot):
    broken = dict(snapshot)
    broken[field] = "gpio17" if field == "currentRoute" else not broken[field]
    try:
        admin.route_change_plan(broken, "gpio20")
    except ValueError:
        pass
    else:
        raise AssertionError(f"route transition accepted invalid {field}")
for route in ("gpio4", "gpio17"):
    try:
        admin.route_change_plan(snapshot, route)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid transition accepted: {route}")
for malformed in ({**snapshot, "unknown": False},
                  {key: value for key, value in snapshot.items() if key != "gpio20Safe"}):
    try:
        admin.route_change_plan(malformed, "gpio20")
    except ValueError:
        pass
    else:
        raise AssertionError("malformed snapshot accepted")
source = (ROOT / "scripts/rp1-gpclk-admin.py").read_text()
for prohibited in ("dtoverlay", "config.txt", "modprobe", "live_output=1", "/dev/mem"):
    assert prohibited not in source
print("Phase 5.4 overlay contract: PASS")
