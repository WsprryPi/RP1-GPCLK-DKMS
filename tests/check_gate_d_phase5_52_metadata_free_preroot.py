#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.52 metadata-free staging and pre-root evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'docs/evidence/gate-d-phase5.52-metadata-free-staging-preroot-attestation.json').read_text())
assert v['kind']=='gate-d-metadata-free-staging-preroot-attestation'
assert v['authorizationCommit']=='8e8cdbe5d573d9c1744003c173c47463060d7f31'
assert v['recapture']['sha256']=='449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f'
assert v['recapture']['capturesByteIdentical'] is True
assert v['transport']=={'format':'ustar','sha256':'8575671c8ab53d885f4ca6884f04fba9f661d6e936e20ce67c80caa17faec841','regularFileCount':829,'directoryCountIncludingRoot':34,'forbiddenPathCount':0,'extendedAttributeKeyCountOnTarget':0,'outerPaxHeaderCount':0,'targetPathSetIdentical':True,'targetContentHashesIdentical':True}
assert v['staging']['inputCount']==63 and v['staging']['archiveRegularMemberCount']==766
assert v['staging']['archivedExecutorReadOnlyValidation']=='passed'
assert v['transition']['status']=='complete' and v['transition']['checkpoint']=='commit'
assert v['installedIdentities']['transitionFilesVerified']==55
assert v['installedIdentities']['installedToolsVerified']==22
assert v['installedIdentities']['installedExecutorSchema6Validation']=='passed'
assert v['postState']=={'moduleLoaded':False,'endpointPresent':False,'overlayActive':False,'candidateDkmsTestVersionPresent':False,'allSixServicesInactive':True,'transientFilesRemoved':True,'forbiddenPathCount':0,'lifecycleAttemptStarted':False,'outputDisabled':True}
print('Phase 5.52 metadata-free staging and pre-root transition: PASS')
