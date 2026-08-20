#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads(
    (ROOT / "docs/evidence/phase5.54-package-removal-reinstall-success.json").read_text()
)

assert value["package"]["version"] == "0.0.0~phase5.54-2"
assert value["package"]["sha256"] == (
    "f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b"
)
assert value["preflight"]["dpkgAuditEmpty"] is True
assert value["preflight"]["stockDkmsInstallCount"] == 4
assert value["removal"]["attemptCount"] == 1
assert value["removal"]["packagePresentAfter"] is False
assert value["removal"]["dkmsResidueCount"] == 0
assert value["removal"]["installedModuleFileCount"] == 0
assert value["removal"]["unrelatedOverlayTreeUnchanged"] is True
assert value["removal"]["inactiveBaselinePreserved"] is True
assert value["reinstall"]["attemptCount"] == 1
assert value["reinstall"]["packageStatus"] == "install ok installed"
assert value["reinstall"]["stockDkmsInstallCount"] == 4
assert value["reinstall"]["excludedCustomKernelInstallCount"] == 0
assert value["reinstall"]["installedModuleFileCount"] == 4
assert value["reinstall"]["uapiRestored"] is True
assert value["reinstall"]["gpio4CanonicalAndBootIdentityRestored"] is True
assert value["reinstall"]["gpio20CanonicalAndBootIdentityRestored"] is True
assert value["reinstall"]["unrelatedOverlayTreeUnchanged"] is True
assert value["terminal"]["userOwnedStagingResidueRemoved"] is True
assert not any(value["safety"].values())
assert value["result"] == "pass-package-removed-and-restored-inactive"

print("Phase 5.54 package removal and reinstall: PASS")
