<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.30 authorized pre-root execution

## Outcome

The operator authorized the exact output-disabled Phase 5.30 Gate D execution
on 2026-08-16. Authorization was bound and pushed at commit `99bde14`. Target
preflight confirmed `wspr5`, AArch64 stock kernel
`6.18.34+rpt-rpi-2712`, no module, endpoint, overlay, candidate DKMS state,
source tree, transaction, or qualification root. Services were
`wsprrypi=active`, `sdrplay=active`, `sdrconnect-server=inactive`, and
`SoapySDRServer=active`.

All staged release checksums passed. The self-authenticating envelope matched
SHA-256
`7c42e5d5464e361693058f252119a90be1df7513cdd79a7eba18c2cf84c35754`.
Authenticated dry validation returned `valid=true`, `readOnly=true`, and
`outputDisabled=true`. The privileged administrator then completed the
qualification installation. DKMS built and installed the compressed module,
both version and vermagic checks passed, the inactive GPIO4 overlay file and
permanent tools were installed, and the administrator recorded that module
load, overlay activation, route selection, reboot, and live output were not
performed.

## Blocking failure

The mandatory transition cleanup removed the Phase 5.30 DKMS registration and
then invoked:

```text
dkms uninstall -m rp1-gpclk-dkms -v 0.0.0-phase5.2 -k 6.18.34+rpt-rpi-2712
```

The historical predecessor was already absent, so DKMS returned exit status
3. The frozen lifecycle dispatcher treated that already-absent state as fatal
instead of accepting it as the required package-absent postcondition. The
pre-root journal stopped at `cleanup-runtime` with `status=recovery-required`
and `liveOutput=false`. None of the 38 lifecycle attempts began.

This is a bounded complete-removal idempotency defect. Phase 5.30 must not be
patched or bypassed in place. A successor must make exact-version uninstall
and removal accept a verified already-absent DKMS state while retaining strict
failure for ambiguous or still-present state, then receive a new freeze,
representative build, complete control set, independent review, and fresh
authorization.

## Evidence and recovery

Preserved evidence has these SHA-256 identities:

- pre-root failure journal: `a7418495b792c9b4a7d910fdd3051806d05905a576494cb674d25d5556d646c4`
- completed administrator transaction: `1a230d10e8d59be26acaaf2735f5b3743cf8a86ba1580094c8d1c4fad4f163a2`
- qualification-root marker: `473181b27d4acc7f8ab29edb6799622d79654e1941b9554e96cade8797b8027d`

The administrator recovery entry point correctly refused the completed
administrator transaction; its install had not failed. The combined pre-root
resume was not used because it couples cleanup to an immediate retry of the
same defective transition. A bounded ledger recovery verified every recorded
file hash or symlink target, refused active module or endpoint state, removed
exactly 402 owned files and 29 now-empty owned directories, and removed the
administrator ledger. The preserved marker and journal hashes were then
rechecked before removing only those two test-owned objects and the empty root.

Final audit found no DKMS entry, module, endpoint, overlay configuration,
candidate overlay file, administrator state, qualification root, source tree,
or installed release directory. All monitored services matched preflight.

No module was loaded or bound. No overlay was activated. No GPIO, pinctrl,
GPCLK, clock, DMA, Si5351, transmitter, SDR test, antenna, transmission, or RF
operation occurred.
