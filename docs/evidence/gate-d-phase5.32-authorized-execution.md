<!-- SPDX-License-Identifier: MIT -->

# Phase 5.32 authorized Gate D execution

## Outcome

The exact authorized instance SHA-256 was
`82bc5719111b7bcbdcbada47fb4ae877fba190252085d8ecc739677da7c3e8cb`;
the authenticated pre-root envelope SHA-256 was
`b557fb7cdb96d750693846062ef61961d1f9b055468c51727e3cb3887e73ec9b`.
All 67 staged input hashes matched on `wspr5`, and the read-only pre-root check
returned `valid=true`, `readOnly=true`, and `outputDisabled=true`.

The privileged transition built and installed the Phase 5.32 DKMS module for
stock kernel `6.18.34+rpt-rpi-2712`, then stopped before permanent-tool commit
because the administrator rejected the existing retained Phase 5.31
`/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe` as unsafe or existing. None of
the 38 lifecycle attempts began.

The sealed `--resume` path was invoked exactly and also failed closed. It
requires the pre-administrator baseline to contain no test DKMS version before
it will invoke administrator recovery, even though the journal records a real
administrator-owned Phase 5.32 installation requiring recovery. No manual or
improvised cleanup was substituted.

## Preserved state

The pre-root journal remains `recovery-required`, checkpoint `install`, with
`liveOutput=false`; SHA-256 is
`213ba7df7972f790c9401d2bdd0d505b183042a640cc0373d4329058da662b0f`.
The administrator transaction SHA-256 is
`d3d34e3eaca69fd807bf576dce0b910d519a82cf231e46c11e51347d8767dff2`.
Phase 5.32 remains installed in DKMS and `/usr/src`; the module is not loaded,
the endpoint is absent, and no overlay is active. Services remain `active`,
`active`, `inactive`, `active`.

No GPIO, active pinctrl, clock, DMA, Si5351, transmitter, SDR, antenna,
transmission, reboot, or RF operation occurred.

## Separately authorized ledger recovery

Recovery-only authorization was committed before execution at `6b3058a`. The
exact envelope-declared administrator command authenticated the preserved
ledger, uninstalled and removed the exact Phase 5.32 DKMS version, verified and
removed 386 owned files and 26 owned directories where empty, and committed
`status=recovered`, `checkpoint=inactive-clean`, `recoveryRequired=false`, and
`liveOutput=false`. The recovered administrator journal SHA-256 is
`fabb5a87c8434847e0ed134a94e4502734acee4f27802a196cb4599734216e23`.

Final audit found no Phase 5.32 DKMS status, source tree, installed release
data, installed module, loaded module, endpoint, or active overlay. The
pre-root failure journal remains preserved with its original SHA-256. Retained
Phase 5.31 UAPI probe, executor, and administrator hashes remained
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`,
`49b26b3f056df6855f7e0530b2f64d2f9a423836bf4b5b773c3db31980505864`,
and `b9c35e9d52a1f2cb67fa055cc517c870c205855ea7d7d052df138c716ad1d9e3`.
Services remained unchanged. Staging and failure journals were preserved.
