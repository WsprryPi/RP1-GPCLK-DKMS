<!-- SPDX-License-Identifier: MIT -->

# Gate D target-execution authorization dossier

## Status

On 2026-08-15 the operator granted the exact execution release requested below.
The first authorized read-only target preflight then found that the reviewed
coordinator does not implement complete command plans for the ten
`required-executable` rows. The authorization remains recorded, but all ten
rows are now `blocked-input-required`; the execution instance reports
`inputsReady: false`, `targetExecutionApproved: true`, and
`executionReady: false`. Its resealed SHA-256 is
`65d5fd9bf05f531b0039e67b1b5e6063fe02a92e8ef043ff1b197948a9069b14`.

The five `deferred-environmental` rows remain unpassed and continue to block
complete environmental coverage, publication, and qualification. They are not
part of this executable subset and cannot be satisfied by simulation.

## Exact requested execution release

The requested release covers the frozen predecessor/successor pair, both
route-specific non-live decisions, `wspr5-stock`, the validated rescue path,
and these required-executable rows only:

1. current supported kernel;
2. prior supported kernel downgrade;
3. signing not enforced;
4. deliberate build failure;
5. interrupted upgrade and recovery at every durable checkpoint;
6. stale manifest rejection;
7. corrupted archive, GPIO4 DTBO, and GPIO20 DTBO rejection;
8. inactive complete removal;
9. refused removal with the exact open/busy injector; and
10. clean reinstall followed by a second complete removal.

The permitted mutation envelope is limited to reviewed prerequisite
installation, exact test-owned DKMS registration/build/install/uninstall and
removal, output-disabled module and allowlisted overlay administration,
temporary stop and exact restoration of named conflicting services when
present, reversible switching between installed stock kernels
`6.18.34+rpt-rpi-2712` and `6.12.75+rpt-rpi-2712`, planned noticed reboot after
recovery preflight, bounded attempt-owned failure injection, rollback/recovery,
immutable evidence, and complete test-owned cleanup. Each attempt requires a
new validated operation document, immediate fail-closed identity/conflict
preflight, its row deadline, and a new evidence directory.

The Si5351 leads must remain disconnected from GPIO4 and GPIO20, no antenna may
be connected, and SDRplay must remain unused. `live_output=1`, active pinctrl,
clock enablement, DMA submission, GPIO output, transmitter keying, Si5351 or SDR
operation, RF, `/dev/mem`, custom-kernel qualification, forced removal, general
upgrade, unreviewed persistent boot change, unrelated cleanup, and fallback to
another physical backend remain prohibited.

The operator's 2026-08-15 authorization makes this dossier the exact boundary
for the required-executable run. The read-only preflight stopped because the
reviewed command plans differed from this boundary. Correct and independently
review those plans before resealing the instance; do not fill the gaps with
ad-hoc target commands.
