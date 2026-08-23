#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp1_admin", ROOT / "scripts/rp1-gpclk-admin.py")
assert spec and spec.loader
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)
policy = json.loads((ROOT / "release/permissions-enrollment-policy-v1.json").read_text())
assert policy["deviceNode"] == {"path": "/dev/rp1-gpclk", "uid": 0, "gid": 0, "mode": "0600", "type": "character"}
assert policy["identityFields"] == list(admin.IDENTITY_FIELDS)
assert policy["implicitEnrollmentSources"] == []

identity = {field: "x" for field in admin.IDENTITY_FIELDS}
for field in admin.HASH_IDENTITY_FIELDS:
    identity[field] = "a" * 64
identity.update({"route": "GPIO4", "uapiAbi": 1})
base = {**identity, "packageFilesPresent": True, "dkmsEntryPresent": True,
        "runtimePrerequisitesPass": True, "compatibilityState": "Experimental",
        "cleanupLatch": False, "routeSelected": True, "operatorAuthorized": True,
        "devicePresent": True, "deviceUid": 0, "deviceGid": 0, "deviceMode": "0600",
        "deviceType": "character", "ownerCount": 0}

assert admin.evaluate_permission_state(base, None) == {
    "installed": True, "available": True, "enrolled": False, "liveEligible": False,
    "active": False, "enrollmentReason": "absent",
    "reasons": ["experimental-enrollment-absent"], "readOnly": True}
with tempfile.TemporaryDirectory() as temporary:
    path = pathlib.Path(temporary) / "etc/rp1-gpclk-dkms/enrollment.json"
    record = admin.write_experimental_enrollment(path, identity, admin.ACKNOWLEDGEMENT,
                                                  0, "root", "2026-08-15T00:00:00Z")
    assert path.stat().st_mode & 0o777 == 0o600
    state = admin.evaluate_permission_state(base, record)
    assert state["enrolled"] and state["liveEligible"] and not state["active"]
    active = dict(base, ownerCount=1)
    assert admin.evaluate_permission_state(active, record)["active"]
    for field in admin.IDENTITY_FIELDS:
        changed = dict(base)
        changed[field] = "GPIO20" if field == "route" else "changed"
        if field == "uapiAbi":
            changed[field] = 2
        result = admin.evaluate_permission_state(changed, record)
        assert not result["enrolled"] and not result["liveEligible"], field
    tombstone = admin.revoke_enrollment(path, 0, "root", "2026-08-15T00:01:00Z")
    revoked = admin.evaluate_permission_state(base, tombstone)
    assert tombstone["revoked"] and not revoked["enrolled"] and revoked["enrollmentReason"] == "revoked"

qualified = dict(base, compatibilityState="Qualified")
result = admin.evaluate_permission_state(qualified, None)
assert result["available"] and result["liveEligible"] and not result["enrolled"]
for field in ("routeSelected", "operatorAuthorized"):
    denied = dict(qualified)
    denied[field] = False
    assert not admin.evaluate_permission_state(denied, None)["liveEligible"]
for compatibility in ("Compatible-unqualified", "Unavailable", "Rejected"):
    denied = dict(base, compatibilityState=compatibility)
    result = admin.evaluate_permission_state(denied, None)
    assert not result["available"] and not result["liveEligible"]
gpio20_identity = dict(identity, route="GPIO20")
with tempfile.TemporaryDirectory() as temporary:
    path = pathlib.Path(temporary) / "enrollment.json"
    gpio20_record = admin.write_experimental_enrollment(
        path, gpio20_identity, admin.ACKNOWLEDGEMENT, 0, "root", "2026-08-15T00:02:00Z")
    gpio20 = dict(base, route="GPIO20")
    assert admin.evaluate_permission_state(gpio20, gpio20_record)["liveEligible"]
    assert not admin.evaluate_permission_state(base, gpio20_record)["enrolled"]
    first = admin.revoke_enrollment(path, 0, "root", "2026-08-15T00:03:00Z")
    second = admin.revoke_enrollment(path, 0, "root", "2026-08-15T00:03:00Z")
    assert first == second
for field, value in (("deviceUid", 1000), ("deviceGid", 1000), ("deviceMode", "0660"),
                     ("deviceType", "regular"), ("cleanupLatch", True),
                     ("runtimePrerequisitesPass", False), ("dkmsEntryPresent", False)):
    denied = dict(base)
    denied[field] = value
    assert not admin.evaluate_permission_state(denied, None)["liveEligible"]
for malformed in ({key: value for key, value in base.items() if key != "kernelRelease"},
                  {**base, "unknown": True}):
    try:
        admin.evaluate_permission_state(malformed, None)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete or unknown snapshot accepted")
inactive_output_owner = admin.evaluate_permission_state(dict(base, ownerCount=1), None)
assert inactive_output_owner["active"] and not inactive_output_owner["liveEligible"]
try:
    admin.write_experimental_enrollment(pathlib.Path("/tmp/unused"), identity,
                                        admin.ACKNOWLEDGEMENT, 1000, "user")
except PermissionError:
    pass
else:
    raise AssertionError("non-root enrollment accepted")
try:
    with tempfile.TemporaryDirectory() as temporary:
        admin.write_experimental_enrollment(pathlib.Path(temporary) / "enrollment.json", identity,
                                            "accept", 0, "root")
except ValueError:
    pass
else:
    raise AssertionError("inexact risk acknowledgement accepted")

source = (ROOT / "scripts/rp1-gpclk-admin.py").read_text()
for prohibited in ("udev", "setfacl", "chmod 066", "chgrp", "setuid", "/dev/mem", "custom-kernel"):
    assert prohibited not in source
print("permissions and enrollment: PASS")
