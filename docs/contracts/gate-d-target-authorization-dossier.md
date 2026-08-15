<!-- SPDX-License-Identifier: MIT -->

# Gate D target-execution authorization dossier

## Status

On 2026-08-15 the operator granted the exact execution release requested below.
The first authorized read-only target preflight found incomplete command-plan
coverage. The offline blocker-resolution slice subsequently bound a validated
38-attempt target-operation plan, exact execution-tool identities, and a
digest-guarded reversible stock-kernel selector. All ten required-executable
rows are again `ready`; the execution instance reports `inputsReady: true`,
`targetExecutionApproved: true`, and `executionReady: true`. Its resealed
SHA-256 is
`fa0f70a3c2920c4dc18bf304979636d87e3d05ec52b54acd2fc4e6caa31b0b08`.

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
for the required-executable run. The corrected plan is
`release/gate-d-target-operation-plan-v1.json`; do not fill any future identity
or per-attempt plan difference with ad-hoc target commands.
