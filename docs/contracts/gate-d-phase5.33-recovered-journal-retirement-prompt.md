<!-- SPDX-License-Identifier: MIT -->

# Phase 5.33 recovered-journal retirement and execution prompt

## Objective

Correct the Phase 5.33 pre-root envelope to name the administrator's canonical
transaction path, preserve the authenticated terminal Phase 5.32 recovery
journal, retire that journal from the live transaction slot, and execute the
already-authorized Phase 5.33 output-disabled Gate D lifecycle exactly once.

## Verified predecessor state

On `wspr5`, `/var/lib/rp1-gpclk-dkms/transaction.json` is a root-owned regular
file with SHA-256
`fabb5a87c8434847e0ed134a94e4502734acee4f27802a196cb4599734216e23`.
Its parsed state is Phase 5.32 `status: recovered`, checkpoint
`inactive-clean`, `recoveryRequired: false`, and `liveOutput: false`. The Phase
5.33 pre-root journal and qualification root are absent.

## Bounded procedure

1. Change only the Phase 5.33 envelope's `administratorState.path` to
   `/var/lib/rp1-gpclk-dkms/transaction.json` and add a regression assertion.
2. Re-run the complete offline control checks and an independent adversarial
   comparison against the frozen administrator source.
3. On `wspr5`, revalidate the canonical journal as a root-owned, mode `0600`,
   non-symlink regular file with the exact hash and terminal fields above.
4. Copy it without transformation to the new Phase 5.33 staging directory as
   `predecessor-phase5.32-recovered-transaction.json`, verify the copy's hash,
   make it read-only, then unlink only the revalidated canonical journal.
5. Stage and hash-check the exact Phase 5.33 release and control inputs. Invoke
   the corrected frozen pre-root executor once. Continue only if its journal,
   qualification root, installed-tool graph, and inactive baseline validate.
6. Dispatch the sealed Phase 5.33 attempt matrix. If any assertion fails, stop
   and use only the sealed recovery path; do not improvise cleanup.
7. Preserve target evidence, record the result in the repository, independently
   review it, and commit and push only attributable changes.

## Safety and non-goals

This authorizes no RF output and no Si5351 operation. The Si5351 remains a
separate I2C output path; GPIO4 and GPIO20 are reserved module routes. Keep
`live_output=0`; do not connect an antenna, enable clocks, submit DMA, use an
SDR, change boot configuration, reboot, publish a release, tag, or modify a
dependent repository. A build or lifecycle pass is qualification evidence only,
not a release or RF-qualification claim.

## Exit criteria

The predecessor journal is durably preserved by exact hash, the canonical
transaction slot is retired only after revalidation, all sealed attempts pass,
the final state is inactive and residue-free, adversarial review has no open
finding, and Git is clean and synchronized after the result commit.
