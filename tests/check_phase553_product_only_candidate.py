#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate recorded product-only Phase 5.53 candidate evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'docs/evidence/phase5.53-product-only-development-candidate.json').read_text())
assert v['sourceCommit']=='40b2ffd2fa944511b549737bcf6eb1a199125971'
assert v['builds']=={'count':2,'byteIdentical':True,'completeReleaseDirectoriesIdentical':True}
assert v['artifacts']['productArchiveSha256']=='c46cec7641fc7e0aae31a86ce2e9ec78948deb8f22fe55cdfdde34636b2e4d3b'
assert v['productArchive']=={'regularFileCount':54,'containsAllowDevelopmentInstaller':True,'installsBothInactiveOverlays':True,'containsQualificationTools':False,'containsLedgerBoundRemoval':True}
assert v['validation']['extractedProductInstallerTest']=='passed'
assert v['validation']['qualificationArchivePresentDuringInstallerTest'] is False
assert v['validation']['sameVersionProductReinstall']=='passed'
assert v['validation']['phase5.52ProductMigration']=='passed'
assert v['validation']['phase5.52DkmsAbsentMigration']=='passed'
assert v['deployment']['performed'] is False and v['deployment']['qualificationArchiveRequired'] is False
print('Phase 5.53 product-only development candidate: PASS')
