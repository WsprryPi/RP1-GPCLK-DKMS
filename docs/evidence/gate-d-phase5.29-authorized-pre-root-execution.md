<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.29 authorized pre-root execution

## Outcome

The operator authorized the exact output-disabled Phase 5.29 Gate D execution
on 2026-08-16. Authorization was bound and pushed at commit `08f5cc4`. Target
preflight confirmed `wspr5`, AArch64 stock kernel
`6.18.34+rpt-rpi-2712`, no module, endpoint, overlay, candidate DKMS state,
source tree, transaction, or qualification root. Services were
`wsprrypi=active`, `sdrplay=active`, `sdrconnect-server=inactive`, and
`SoapySDRServer=active`.

All 67 sealed input files matched the Phase 5.29 pre-root envelope. Release
checksum verification passed. The separately staged self-authenticating
envelope matched SHA-256
`acd8acfabe1583a8503b816bc496db50d4f6e5971d539c51a6e64a8ba7fa7d79`.
Authenticated dry validation passed with `outputDisabled=true`,
`readOnly=true`, and `valid=true`. Privileged bootstrap then began.

The administrator accepted the canonical kernel-header path, registered and
built the candidate with DKMS, resolved the built
`rp1_gpclk_dkms.ko.xz`, and passed its version and vermagic checks. DKMS then
installed the candidate.

## Blocking failure

Bootstrap failed before module loading, overlay installation, or any lifecycle
attempt. DKMS installed the module as:

```text
/lib/modules/6.18.34+rpt-rpi-2712/updates/dkms/rp1_gpclk_dkms.ko.xz
```

The frozen Phase 5.29 administrator still required the uncompressed installed
path ending in `rp1_gpclk_dkms.ko`. Its post-install `modinfo -F version`
check therefore failed closed because that `.ko` path did not exist. This is a
bounded installed-module representation defect. The Phase 5.29 built-module
correction worked as designed; target identity and build compatibility did not
drift.

## Evidence and cleanup

Preserved target evidence beneath the staging directory has these SHA-256
values:

- failed administrator transaction: `25dba43738be2347e3f34b54828b2bb3cff3f308e5728f7e25e9a7bbbc075760`
- failed pre-root transaction: `5074c2541176939bf7d4bbad5f907f00187f4570a77bad047299ee6fa2c73f33`
- qualification-root marker: `0c77c3d2d40db57aa457e31b5a60334158f4e9b84cdf601e7d306f838feaeeb6`
- recovered administrator transaction: `410b0ef37ed78f31afd269c830e7423a0dea23c68470166d60822b21c8f83189`

The exact frozen administrator recovery removed the installed compressed
module, candidate DKMS state, and owned source tree. The recovered transaction,
failed pre-root journal, marker, and now-empty qualification root were removed
after evidence preservation. Final checks found no candidate DKMS entry,
source tree, installed module, transaction, qualification root, loaded module,
endpoint, or overlay. All monitored services matched their initial states.

None of the 38 lifecycle attempts began. No module was loaded or bound, no
overlay was activated, and no GPIO, clock, DMA, Si5351, transmitter, SDR,
antenna, or RF operation occurred. Phase 5.29 must not be patched or bypassed
in place. A new successor requires bounded installed-module representation
resolution and verification, followed by a new freeze, representative build,
control set, and authorization.
