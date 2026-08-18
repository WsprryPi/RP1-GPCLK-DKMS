#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate final Phase 5.53 split-candidate offline evidence."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
value=json.loads((ROOT/"docs/evidence/phase5.53-final-split-offline-checks-twice.json").read_text())
assert value["kind"]=="phase5.53-final-split-offline-checks-twice"
assert value["product"]["archiveSha256"]=="032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["product"]["regenerated"] is False
successor=value["qualificationSuccessor"]
assert successor["sourceCommit"]=="e074c9dc01244f7efb73b95a8007bca3625b9c85"
assert successor["archiveSha256"]=="31dd96079930d4c77788aea506cd0fa549d2ec101c1cf93ab3d5b392e76caaf5"
assert successor["generations"]==2 and successor["byteIdentical"] is True
assert len(value["runs"])==2
assert all(r["exitStatus"]==0 and r["passLines"]==192 and r["skipLines"]==5 and r["failLines"]==0 for r in value["runs"])
assert value["transcriptsByteIdentical"] is True and len({r["transcriptSha256"] for r in value["runs"]})==1
transcript=ROOT/value["durableTranscript"]
assert hashlib.sha256(transcript.read_bytes()).hexdigest()==value["runs"][0]["transcriptSha256"]
text=transcript.read_text(); assert text.count("SKIP")==5 and "FAIL" not in text
assert value["result"]=="passed" and value["nextGate"]=="reconstruct exact-closure representative lifecycle controls"
print("Phase 5.53 final split-candidate offline checks twice: PASS")
