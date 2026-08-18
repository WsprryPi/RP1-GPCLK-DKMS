#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate recorded product-only Phase 5.53 candidate evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'docs/evidence/phase5.53-product-only-development-candidate.json').read_text())
assert v['sourceCommit']=='83b1de0e82c30ab4c2781dc941eef0556d6bfede'
assert v['builds']=={'count':2,'byteIdentical':True,'completeReleaseDirectoriesIdentical':True}
assert v['artifacts']['productArchiveSha256']=='d014e60f7a76d6c5b178ff5bec4caa1d4978f4a9fd0a2a6a5552614c7d6b2276'
assert v['productArchive']=={'regularFileCount':54,'containsAllowDevelopmentInstaller':True,'installsBothInactiveOverlays':True,'containsQualificationTools':False,'containsLedgerBoundRemoval':True}
assert v['validation']['extractedProductInstallerTest']=='passed'
assert v['validation']['qualificationArchivePresentDuringInstallerTest'] is False
assert v['validation']['sameVersionProductReinstall']=='passed'
assert v['deployment']['performed'] is False and v['deployment']['qualificationArchiveRequired'] is False
print('Phase 5.53 product-only development candidate: PASS')
