<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.31 authorized pre-root execution

## Outcome

The operator authorized the exact output-disabled Phase 5.31 Gate D execution.
Authorization was bound and pushed at commit `d74b87c`. Preflight on `wspr5`
confirmed AArch64 stock kernel `6.18.34+rpt-rpi-2712`, no Phase 5.31 residue,
no DKMS registration, module, endpoint, or overlay, and the expected service
states. All release checksums passed. The authenticated pre-root dry check
returned `valid=true`, `readOnly=true`, and `outputDisabled=true` for envelope
SHA-256 `306c7ec13c352a5b023c04c52a7022985b83082deefba96caf604056a0032572`.

The administrator installed and verified the compressed Phase 5.31 DKMS
module, inactive GPIO4 overlay file, permanent tools, and policy files without
loading the module or activating the overlay. Transition cleanup then removed
the candidate. Both predecessor removal commands returned DKMS status 3, and
the Phase 5.31 correction accepted each only after its bounded exact DKMS
status query succeeded with empty output. This proves the Phase 5.31 removal
idempotency correction on the representative target.

## Blocking failure

The transition stopped at `verify-transition` because one installed-tool
identity differed:

```text
/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin
expected 0e3b8605817d7b5a6bee112184a55e7bc8438a6e15582400570607403f223276
actual   b9c35e9d52a1f2cb67fa055cc517c870c205855ea7d7d052df138c716ad1d9e3
```

The actual hash matches the frozen Phase 5.31 administrator and bootstrap-plan
installed identity. The pre-root envelope inherited a stale installed-tool
hash that the offline control-set review did not compare against the bootstrap
plan. This is a control-set construction and validation defect, not candidate,
target, DKMS, or service drift. None of the 38 lifecycle attempts began.

## Evidence and recovery

Preserved evidence SHA-256 identities are:

- pre-root failure journal: `2d7e39eeb0abacf8e3b492c7075a76afc680d3564c9435aec5a56c3f88c8eaf4`
- completed administrator transaction: `ea568ba3fa2af0ed9f05ed409ece0a8d7cfb9b089e7301fc4946432fc509d8af`
- qualification-root marker: `be2067085f4e8f0027b5a81e3e28645126c1bd6864476daee5c81ed55f3a25f5`

Bounded recovery verified every administrator-ledger file hash and symlink,
then removed 412 owned files and 29 empty owned directories. The partial-root
recovery validated all 58 transition files against the sealed envelope before
removing them, the exact marker, root, and journal. Final audit found no DKMS
entry, module, endpoint, overlay configuration or file, administrator state,
qualification root, source tree, or installed release directory. Services
remained `active`, `active`, `inactive`, `active`.

No module was loaded or bound. No overlay was activated. No GPIO, pinctrl,
clock, DMA, Si5351, transmitter, SDR test, antenna, transmission, reboot, or RF
operation occurred.
