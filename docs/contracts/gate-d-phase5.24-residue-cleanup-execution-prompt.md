<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.24 residue-cleanup execution prompt

## Objective

Execute only the reviewed, output-disabled recovery described by
`release/gate-d-phase5.24-residue-recovery-v1.json` on `wspr5`. Remove the
authenticated residue left by the failed Phase 5.24 pre-root transition, prove
that the operation is repeatably clean, and preserve all historical inputs and
evidence. Stop before the Phase 5.25 representative build or any Gate D
lifecycle execution.

## Authority and boundaries

The operator's instruction to execute this prompt authorizes the exact cleanup
document on `wspr5`, including read-only preflight, temporary staging of the
reviewed cleanup tool and document, the document's bounded deletion, final
audit, and removal of that temporary staging. It does not authorize package or
DKMS changes, module or overlay administration, service or boot changes,
reboot, GPIO or clock access, DMA, Si5351 or SDRplay use, transmission, RF,
tagging, publication, or consuming-repository changes.

Preserve without modification:

- `/home/pi/gate-d-inputs/phase5.24-2a6ddeb8e0f7`
- `/home/pi/gate-c-evidence`

The only target residue eligible for deletion is:

- the authenticated `.gate-d-root.json` marker;
- its otherwise-empty
  `/home/pi/gate-d-qualification/phase5.24-2a6ddeb8e0f7` directory; and
- the authenticated
  `/var/lib/rp1-gpclk-dkms/gate-d/pre-root-phase5.24.json` journal.

## Required procedure

1. Confirm the repository worktree is clean and identify the committed cleanup
   tool and document hashes.
2. Read-only audit the target path types, owners, modes, marker and journal
   hashes, directory closure, absent administrator transaction, preserved
   paths, and empty module, endpoint, overlay, and test-DKMS baseline.
3. Stop without deletion on any missing, foreign, symlinked, substituted,
   ambiguous, unexpected, or active state.
4. Stage only the exact cleanup tool and document in a unique user-owned `0700`
   directory. Verify their hashes on-target.
5. Run the tool without `--execute`; require `status: ready`, `readOnly: true`,
   and `outputDisabled: true`.
6. Run the same tool and document with `sudo` and `--execute`; require
   `status: complete` and `outputDisabled: true`.
7. Repeat the execution and require `status: already-clean`.
8. Independently prove the three residue paths and administrator transaction
   are absent, both preserved trees remain directories, and the module,
   endpoint, overlays, and test DKMS versions remain absent.
9. Remove only the two staged files and their exact empty staging directory.
10. Record the execution separately from the frozen Phase 5.25 identity file;
    do not rewrite freeze-time facts.

## Exit criteria

The slice passes only if both committed hashes match on-target, the preflight
returns ready, cleanup returns complete, replay returns already-clean, the
independent post-audit proves the expected baseline and preservation boundary,
and temporary staging is absent. Perform an adversarial review of the observed
execution. Stop before representative build or further target work.
