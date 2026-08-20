<!-- SPDX-License-Identifier: MIT -->

# Phase 5.28 canonical `/lib` successor execution prompt

Create distinct successor `0.0.0-phase5.28` for frozen Phase 5.27, which failed
before DKMS registration because stock Raspberry Pi OS uses `/lib -> usr/lib`.
Preserve all Phase 5.27 source, controls, staging, and failure evidence.

Allow only `/lib` as a distribution alias and only when its link text is
`usr/lib` or `/usr/lib` and it resolves within the target root to the real,
protected `/usr/lib`. Require real, non-symlink `modules/KERNEL`, validate the
kernel release, and retain the strict final `build` resolution beneath the real
`/usr/src`, ownership match, directory type, and no group/world writes. Reject
all other aliases, intermediate symlinks, escapes, overrides, and unknown
layouts. Generic installation paths remain symlink-free.

Add deterministic acceptance tests for the exact stock two-link chain and
negative tests for altered `/lib`, module-tree, escape, ownership, and mode
states. Run the complete offline suite and a separate adversarial review.
Correct every finding and repeat affected checks.

Commit the implementation, freeze that exact clean commit with two isolated
byte-identical development release builds, and record all identities. Perform
an exact build-only compile on `wspr5`; do not install or load it. If and only
if that passes, generate and independently validate a new hash-closed Phase
5.28 route decision, target plan, qualification identity/bootstrap, 38-attempt
bundle, execution instance, and pre-root envelope. Never relabel older controls.

Target lifecycle execution requires the exact new controls and explicit
authorization. It remains output-disabled: no GPIO output, clock enable, DMA,
Si5351, transmitter, SDR operation, antenna, or RF. Stop at the first identity,
residue, service, recovery, or cleanup ambiguity. Report exact hashes, checks,
mutations, cleanup, commits, push state, and remaining gate. Do not tag,
publish, open a PR, or advance dependent repositories.
