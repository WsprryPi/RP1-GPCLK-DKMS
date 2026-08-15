<!-- SPDX-License-Identifier: MIT -->

# Gate D offline lifecycle adversarial assessment

## Scope and result

This review attempted to falsify the offline output-disabled Gate D lifecycle
coordinator and execution-instance contract. The first complete offline run was
not accepted as final evidence because review found five objective omissions.
All findings were reinjected and covered by deterministic tests. The final review
found no unresolved objective issue within this offline-only implementation
slice.

No Raspberry Pi was contacted or changed. No package, module, service, boot
configuration, GPIO, clock, DMA, transmitter, SDR, or RF operation was
performed. This assessment is not Gate D target evidence and does not freeze a
candidate.

## Findings and reinjection

1. The removal-open-or-active matrix row had no executable refusal action.
   `refuse-removal` now requires an exact enumerated blocker, retains verified
   owned bytes, dispatches no external command, and records
   `installation-retained`.
2. Complete removal did not independently prove final DKMS and runtime absence.
   Final-state audit now queries every declared test version and rejects module,
   endpoint, platform binding, or owned-path residue.
3. Recovery could replace the failed journal. Recovery now requires the prior
   operation identity, reads a separate immutable failed journal, and writes a
   new attempt journal.
4. Upgrade and downgrade failure did not automatically restore the retained
   predecessor. Ordinary failure now runs the bounded exact rollback sequence;
   rollback failure remains `inactive-recovery-required`.
5. Command evidence lacked complete bounded timing and result records. Each
   dispatched command now records checkpoint, deadline, UTC and monotonic
   timestamps, exit status, and at most 65,536 output characters with an
   explicit truncation flag.
6. Packaging the concrete instance made its archive digest self-referential and
   exposed host-specific authorization as installed data. The build and install
   contracts now exclude the instance while retaining the generic schema and
   tools; a separately sealed post-build instance is the execution input.

## Remaining gates

The checked-in execution instance remains intentionally blocked. Candidate
freeze, exact missing representative systems and signing cases, target
execution, publication/download verification, and consuming-repository
integration remain separate future gates requiring their own authorization and
evidence.
