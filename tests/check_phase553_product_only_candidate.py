#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate recorded product-only Phase 5.53 candidate evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'docs/evidence/phase5.53-product-only-development-candidate.json').read_text())
assert v['sourceCommit']=='4e7a64a0ca353d2fcab6e25891f5254746e2b91a'
assert v['builds']=={'count':2,'byteIdentical':True,'completeReleaseDirectoriesIdentical':True}
assert v['artifacts']['productArchiveSha256']=='032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76'
assert v['productArchive']=={'regularFileCount':54,'containsAllowDevelopmentInstaller':True,'installsBothInactiveOverlays':True,'containsQualificationTools':False,'containsLedgerBoundRemoval':True}
assert v['validation']['extractedProductInstallerTest']=='passed'
assert v['validation']['qualificationArchivePresentDuringInstallerTest'] is False
assert v['validation']['sameVersionProductReinstall']=='passed'
assert v['validation']['phase5.52ProductMigration']=='passed'
assert v['validation']['phase5.52DkmsAbsentMigration']=='passed'
assert v['validation']['extractedProductValidatorWithoutQualificationClosure']=='passed'
assert v['deployment']['performed'] is False and v['deployment']['qualificationArchiveRequired'] is False
print('Phase 5.53 product-only development candidate: PASS')
