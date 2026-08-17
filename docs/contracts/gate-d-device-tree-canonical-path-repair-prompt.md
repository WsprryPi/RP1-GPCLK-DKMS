<!-- SPDX-License-Identifier: MIT -->

# Gate D canonical device-tree path repair prompt

Repair the frozen-executor defect recorded at commit
`8409b4a44532cc0a60fd916688f63f55539a8f68` without retrying Phase 5.46 or
advancing into a new release cycle.

Use read-only wspr5 inspection to bind the real target topology. Require
`/proc/device-tree` to be exactly the canonical symlink to
`/sys/firmware/devicetree/base`, and require that canonical root to be a direct,
root-owned directory. Audit every other path used by target preflight and
record whether it is direct, absent as allowed, or unexpectedly symlinked.

Implement a narrow device-tree resolver rather than weakening the general
controlled-path guard. Permit only the exact `/proc/device-tree` alias and
exact canonical target. Resolve the fixed `rp1-gpclk` resource beneath the
canonical root. Reject a missing or changed alias, a symlinked canonical-root
component, a symlinked resource node, an unsafe resource name, and any
descendant symlink. Preserve the existing fail-closed behavior for every other
controlled path.

Add deterministic regressions covering the real Raspberry Pi alias topology,
an absent resource, a present direct resource, a changed alias target, a
symlinked canonical component, a symlinked resource, and a malicious
descendant symlink. Update the target-preflight fixture so it reproduces the
real alias rather than an unreal direct `/proc` tree. Adversarially inspect all
remaining target-facing paths for the same synthetic-versus-real mismatch.

Run focused tests and the complete offline suite. Correct every actionable
finding and repeat affected validation until clean. Commit and push only this
offline implementation, tests, prompt, and independent review.

Do not change Phase 5.46 controls or sealed evidence; retry an attempt; freeze
a successor; build a release; generate controls; request authorization; stage
inputs; change services; administer DKMS, modules, overlays, or boot state; or
perform GPIO, clock, DMA, I2C, Si5351, SDR, antenna, transmission, or RF work.
