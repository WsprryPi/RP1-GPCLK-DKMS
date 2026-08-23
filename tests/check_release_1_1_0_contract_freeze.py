#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
f=json.loads((R/'release/uapi-contract-freeze-v1.1.0.json').read_text())
h=R/f['uapi']['path']
assert f['release']==f['dkmsVersion']==f['moduleVersion']=='1.1.0'
assert f['debianVersion']=='1.1.0-1' and f['expectedTag']=='v1.1.0'
assert f['endpoint']['path']=='/dev/rp1-gpclk'
assert f['uapi']['abiMin']==1 and f['uapi']['abi']==2
assert hashlib.sha256(h.read_bytes()).hexdigest()==f['uapi']['sha256']
assert [(x['name'],x['number'],x['size']) for x in f['uapi']['commands'][-3:]]==[('QUERY_V2',39,320),('SUBMIT_TONE_V2',40,112),('RELEASE_V2',41,56)]
assert f['uapi']['toneOperations'][0]['durationNs']=='must-be-zero'
assert f['uapi']['toneOperations'][1]['durationNsMin']==1000000
assert f['uapi']['toneOperations'][1]['durationNsMax']==120000000000
assert {x['name']:x['bit'] for x in f['uapi']['capabilities']}=={'TONE_CONTINUOUS':8,'TONE_FINITE':9}
assert all(not x['liveEligible'] for x in f['routes'])
assert f['compatibility']['priorGpio4EvidenceTransfers'] is False
assert (R/'release/uapi/rp1_gpclk-v1.0.1.h').is_file()
print('1.1.0 ABI v2 normative contract freeze: PASS')
