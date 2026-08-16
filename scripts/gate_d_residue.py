#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and remove one exactly identified failed pre-root residue."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import stat

SHA = __import__("re").compile(r"[0-9a-f]{64}")
BASELINE = {"moduleLoaded": False, "endpointPresent": False, "overlayActive": False,
            "dkmsTestVersions": False, "liveOutput": False}


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(value: dict) -> dict:
    if isinstance(value, dict) and value.get("kind") == "gate-d-failed-attempt-terminal-recovery":
        return validate_attempt_recovery(value)
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "operationId",
                "host", "candidate", "root", "marker", "journal",
                "administratorState", "preservedPaths", "expectedBaseline", "safety"}
    if (not isinstance(value, dict) or set(value) != required or
            value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or
            value.get("kind") != "gate-d-failed-preroot-residue-recovery"):
        raise ValueError("invalid residue-recovery identity")
    if value["host"] != "wspr5" or value["candidate"] != "0.0.0-phase5.24":
        raise ValueError("residue-recovery target differs")
    identities = (value["marker"], value["journal"])
    if any(not isinstance(item, dict) or set(item) != {"path", "sha256"} or
           not pathlib.PurePosixPath(item.get("path", "")).is_absolute() or
           not SHA.fullmatch(item.get("sha256", "")) for item in identities):
        raise ValueError("invalid residue-recovery file identity")
    root = pathlib.PurePosixPath(value["root"])
    if (not root.is_absolute() or root in {pathlib.PurePosixPath("/"), pathlib.PurePosixPath("/home/pi")} or
            pathlib.PurePosixPath(value["marker"]["path"]).parent != root):
        raise ValueError("invalid residue-recovery root")
    admin = value["administratorState"]
    if (not isinstance(admin, dict) or set(admin) != {"path", "expected"} or
            admin.get("expected") != "absent" or not pathlib.PurePosixPath(admin.get("path", "")).is_absolute()):
        raise ValueError("invalid residue-recovery administrator state")
    if value["expectedBaseline"] != BASELINE:
        raise ValueError("residue-recovery baseline differs")
    safety = {"outputDisabled": True, "liveOutput": False, "gpioAccess": False,
              "clockEnabled": False, "dmaActive": False, "sdrActive": False, "rf": False}
    if value["safety"] != safety:
        raise ValueError("residue-recovery safety differs")
    if (not isinstance(value["preservedPaths"], list) or not value["preservedPaths"] or
            any(not pathlib.PurePosixPath(path).is_absolute() for path in value["preservedPaths"])):
        raise ValueError("residue-recovery preservation boundary differs")
    return {"valid": True, "readOnly": True, "outputDisabled": True}


def validate_attempt_recovery(value: dict) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "operationId",
                "host", "candidate", "source", "destination", "expectedFailure",
                "expectedBaseline", "safety"}
    if (set(value) != required or value.get("SPDX-License-Identifier") != "MIT" or
            value.get("schemaVersion") != 1 or value.get("host") != "wspr5" or
            value.get("candidate") != "0.0.0-phase5.39"):
        raise ValueError("invalid attempt-recovery identity")
    source = value["source"]
    source_keys = {"evidenceDirectory", "journalPath", "journalSha256",
                   "manifestPath", "manifestSha256"}
    if (set(source) != source_keys or
            pathlib.PurePosixPath(source["journalPath"]).parent !=
            pathlib.PurePosixPath(source["evidenceDirectory"]) or
            pathlib.PurePosixPath(source["manifestPath"]).parent !=
            pathlib.PurePosixPath(source["evidenceDirectory"]) or
            any(not SHA.fullmatch(source[key]) for key in ("journalSha256", "manifestSha256"))):
        raise ValueError("invalid attempt-recovery source")
    destination = value["destination"]
    if (set(destination) != {"evidenceDirectory", "journalPath"} or
            pathlib.PurePosixPath(destination["journalPath"]).parent !=
            pathlib.PurePosixPath(destination["evidenceDirectory"]) or
            destination["evidenceDirectory"] == source["evidenceDirectory"]):
        raise ValueError("invalid attempt-recovery destination")
    expected = value["expectedFailure"]
    if set(expected) != {"operationId", "documentSha256", "indexSha256", "executorSha256",
                         "failure", "nextStep", "completedOperation", "pendingOperation"}:
        raise ValueError("invalid attempt-recovery failure contract")
    for key in ("documentSha256", "indexSha256", "executorSha256"):
        if not SHA.fullmatch(expected.get(key, "")):
            raise ValueError("invalid attempt-recovery failure hash")
    if (expected.get("failure") != "CalledProcessError" or expected.get("nextStep") != 1 or
            expected.get("completedOperation") != "create-evidence" or
            expected.get("pendingOperation") != "capture-preflight"):
        raise ValueError("attempt-recovery failure boundary differs")
    if value["expectedBaseline"] != BASELINE:
        raise ValueError("attempt-recovery baseline differs")
    safety = {"outputDisabled": True, "liveOutput": False, "gpioAccess": False,
              "clockEnabled": False, "dmaActive": False, "sdrActive": False, "rf": False}
    if value["safety"] != safety:
        raise ValueError("attempt-recovery safety differs")
    return {"valid": True, "readOnly": True, "outputDisabled": True}


def execute_attempt_recovery(value: dict, *, prefix: pathlib.Path, probe,
                             execute: bool = False) -> dict:
    validate_attempt_recovery(value)
    def rooted(raw: str) -> pathlib.Path:
        pure = pathlib.PurePosixPath(raw)
        current = prefix
        for part in pure.parts[1:]:
            current /= part
            if current.exists() and current.is_symlink():
                raise ValueError("symlink in attempt-recovery path")
        return current
    source = value["source"]
    evidence = rooted(source["evidenceDirectory"])
    journal = rooted(source["journalPath"])
    manifest = rooted(source["manifestPath"])
    destination = rooted(value["destination"]["evidenceDirectory"])
    destination_journal = rooted(value["destination"]["journalPath"])
    if (evidence.is_symlink() or not evidence.is_dir() or
            stat.S_IMODE(evidence.stat().st_mode) != 0o500 or
            journal.is_symlink() or not journal.is_file() or digest(journal) != source["journalSha256"] or
            manifest.is_symlink() or not manifest.is_file() or digest(manifest) != source["manifestSha256"] or
            stat.S_IMODE(journal.stat().st_mode) != 0o400 or
            stat.S_IMODE(manifest.stat().st_mode) != 0o400):
        raise ValueError("attempt-recovery sealed source differs")
    state = json.loads(journal.read_text(encoding="utf-8"))
    expected = value["expectedFailure"]
    records = state.get("records")
    if (state.get("status") != "inactive-recovery-required" or state.get("sealed") is not True or
            state.get("recoveryRequired") is not True or state.get("liveOutput") is not False or
            state.get("operationId") != expected["operationId"] or
            state.get("documentSha256") != expected["documentSha256"] or
            state.get("indexSha256") != expected["indexSha256"] or
            state.get("executorSha256") != expected["executorSha256"] or
            state.get("failure") != expected["failure"] or state.get("nextStep") != expected["nextStep"] or
            not isinstance(records, list) or len(records) != 2 or
            records[0].get("operation") != expected["completedOperation"] or records[0].get("status") != 0 or
            records[1].get("operation") != expected["pendingOperation"] or records[1].get("status") != "pending"):
        raise ValueError("attempt-recovery journal boundary differs")
    if probe() != BASELINE or destination.exists() or destination.is_symlink():
        raise ValueError("attempt-recovery target baseline differs")
    if not execute:
        return {"status": "ready", "readOnly": True, "outputDisabled": True}
    destination.mkdir(parents=True, mode=0o700)
    result = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
              "kind": "gate-d-failed-attempt-terminal-recovery-result",
              "operationId": value["operationId"], "status": "complete",
              "recoveryRequired": False, "liveOutput": False,
              "source": {"operationId": state["operationId"],
                         "journalSha256": source["journalSha256"],
                         "manifestSha256": source["manifestSha256"]},
              "baseline": BASELINE}
    destination_journal.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    destination_journal.chmod(0o400)
    sums = destination / "SHA256SUMS"
    sums.write_text(f"{digest(destination_journal)}  {destination_journal.name}\n")
    sums.chmod(0o400)
    destination.chmod(0o500)
    if probe() != BASELINE:
        raise ValueError("attempt-recovery post-state differs")
    return {"status": "complete", "outputDisabled": True,
            "journalSha256": digest(destination_journal)}


def execute(value: dict, *, prefix: pathlib.Path, probe, execute: bool = False) -> dict:
    if isinstance(value, dict) and value.get("kind") == "gate-d-failed-attempt-terminal-recovery":
        return execute_attempt_recovery(value, prefix=prefix, probe=probe, execute=execute)
    validate(value)
    def rooted(raw: str) -> pathlib.Path:
        pure = pathlib.PurePosixPath(raw)
        path = prefix.joinpath(*pure.parts[1:])
        current = prefix
        for part in pure.parts[1:]:
            current /= part
            if current.exists() and current.is_symlink():
                raise ValueError("symlink in residue-recovery path")
        return path
    root = rooted(value["root"]); marker = rooted(value["marker"]["path"])
    journal = rooted(value["journal"]["path"]); administrator = rooted(value["administratorState"]["path"])
    if not root.exists() and not journal.exists() and not marker.exists():
        if probe() != BASELINE: raise ValueError("already-clean residue baseline differs")
        return {"status": "already-clean", "outputDisabled": True}
    if (root.is_symlink() or not root.is_dir() or marker.is_symlink() or not marker.is_file() or
            digest(marker) != value["marker"]["sha256"] or journal.is_symlink() or
            not journal.is_file() or digest(journal) != value["journal"]["sha256"] or
            administrator.exists() or administrator.is_symlink() or probe() != BASELINE):
        raise ValueError("residue-recovery precondition differs")
    children = list(root.iterdir())
    if children != [marker]:
        raise ValueError("residue-recovery root contains unexpected bytes")
    if not execute:
        return {"status": "ready", "readOnly": True, "outputDisabled": True}
    marker.unlink(); root.rmdir(); journal.unlink()
    if probe() != BASELINE:
        raise ValueError("residue-recovery post-state differs")
    return {"status": "complete", "outputDisabled": True}


def live_probe() -> dict:
    overlays = subprocess.run(["/usr/bin/dtoverlay", "-l"], stdout=subprocess.PIPE,
                              text=True, check=False).stdout
    dkms = subprocess.run(["/usr/sbin/dkms", "status"], stdout=subprocess.PIPE,
                          text=True, check=False).stdout
    return {"moduleLoaded": pathlib.Path("/sys/module/rp1_gpclk_dkms").exists(),
            "endpointPresent": pathlib.Path("/dev/rp1-gpclk").exists(),
            "overlayActive": "rp1-gpclk" in overlays,
            "dkmsTestVersions": "rp1-gpclk-dkms/" in dkms, "liveOutput": False}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("document", type=pathlib.Path)
    parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    value = json.loads(args.document.read_text(encoding="utf-8"))
    if args.execute and os.geteuid() != 0: raise SystemExit("residue recovery requires root and --execute")
    print(json.dumps(execute(value, prefix=pathlib.Path("/"), probe=live_probe,
                             execute=args.execute), indent=2, sort_keys=True))


if __name__ == "__main__": main()
