#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pure fail-closed compatibility transition evaluator."""

from __future__ import annotations

EVENTS = {
    "identical-rebuild", "new-kernel-build-success", "dkms-build-failure",
    "signing-failure", "module-identity-mismatch", "overlay-identity-mismatch",
    "cleanup-failure-latched", "explicit-recovery-success",
    "manifest-missing-or-malformed", "experimental-enrollment-stale",
}
STATES = {"Qualified", "Experimental", "Compatible-unqualified", "Unavailable", "Rejected"}


def evaluate_update(prior: dict, event: str, *, identity_identical: bool = False,
                    manifest_preserves_state: bool = False,
                    enrollment_current: bool = False) -> dict:
    """Return policy only; never discovers or changes system state."""
    if set(prior) != {"state", "liveEligible", "reason"} or prior["state"] not in STATES:
        raise ValueError("prior decision is incomplete or malformed")
    if not isinstance(prior["liveEligible"], bool) or not isinstance(prior["reason"], str) or not prior["reason"]:
        raise ValueError("prior decision has invalid fields")
    if prior["state"] == "Qualified" and not prior["liveEligible"]:
        raise ValueError("Qualified prior decision must be live eligible")
    if prior["state"] in {"Compatible-unqualified", "Unavailable", "Rejected"} and prior["liveEligible"]:
        raise ValueError("non-live prior state cannot be live eligible")
    if event not in EVENTS:
        raise ValueError("unknown update event")
    result = {"state": "Unavailable", "liveEligible": False,
              "reason": event, "priorInstallation": "retain-bootable",
              "allowLoad": False, "allowBind": False, "recoveryRequired": False,
              "fallbackAllowed": False}
    if event == "identical-rebuild":
        if identity_identical and manifest_preserves_state:
            result.update(state=prior["state"], liveEligible=prior["liveEligible"],
                          reason="exact manifest rule preserves prior decision",
                          allowLoad=prior["state"] not in {"Unavailable", "Rejected"},
                          allowBind=prior["state"] in {"Qualified", "Experimental"})
        else:
            result.update(state="Compatible-unqualified", reason="rebuild has no exact manifest preservation rule")
    elif event == "new-kernel-build-success":
        result.update(state="Compatible-unqualified", reason="build success cannot preserve or create qualification")
    elif event == "dkms-build-failure":
        result["reason"] = "DKMS build failed; retain prior bootable kernel installation"
    elif event == "signing-failure":
        result["reason"] = "signing failed; unsigned loading prohibited"
    elif event == "module-identity-mismatch":
        result["reason"] = "loaded module identity differs; reject use"
    elif event == "overlay-identity-mismatch":
        result["reason"] = "overlay identity differs; reject binding"
    elif event == "cleanup-failure-latched":
        result.update(state="Rejected", reason="cleanup failure latched", recoveryRequired=True)
    elif event == "explicit-recovery-success":
        if prior["state"] != "Rejected":
            raise ValueError("recovery can clear only a rejected cleanup latch")
        result["reason"] = "explicit recovery succeeded; full identity revalidation required"
    elif event == "manifest-missing-or-malformed":
        result["reason"] = "compatibility manifest missing or malformed"
    elif event == "experimental-enrollment-stale":
        if prior["state"] != "Experimental":
            raise ValueError("stale enrollment applies only to Experimental")
        result.update(state="Experimental", reason="Experimental enrollment stale; live eligibility revoked")
    if result["state"] == "Experimental" and event == "identical-rebuild" and not enrollment_current:
        result.update(liveEligible=False, allowBind=False,
                      reason="exact rebuild preserved Experimental state but enrollment is stale")
    return result
