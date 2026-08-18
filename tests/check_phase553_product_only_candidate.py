#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate recorded product-only Phase 5.53 candidate evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'docs/evidence/phase5.53-product-only-development-candidate.json').read_text())
assert v['sourceCommit']=='9185b01454650d0f13aa0c66bb995576a688d571'
assert v['builds']=={'count':2,'byteIdentical':True,'completeReleaseDirectoriesIdentical':True}
assert v['artifacts']['productArchiveSha256']=='a4c9e6cbb0c25140062723edc5103004c6764b6622e4fe05f8795501c0e33800'
assert v['productArchive']=={'regularFileCount':54,'containsAllowDevelopmentInstaller':True,'installsBothInactiveOverlays':True,'containsQualificationTools':False}
assert v['validation']['extractedProductInstallerTest']=='passed'
assert v['validation']['qualificationArchivePresentDuringInstallerTest'] is False
assert v['deployment']['performed'] is False and v['deployment']['qualificationArchiveRequired'] is False
print('Phase 5.53 product-only development candidate: PASS')
