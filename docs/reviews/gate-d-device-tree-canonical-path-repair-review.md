<!-- SPDX-License-Identifier: MIT -->

# Gate D canonical device-tree path repair independent review

Status: PASS for the bounded offline repair. Phase 5.46 remains retired and no
successor release work was performed.

Read-only wspr5 inspection confirmed the actual Raspberry Pi topology:
`/proc/device-tree` is exactly a symlink to
`/sys/firmware/devicetree/base`; the canonical target is a direct,
root-owned `0755` directory; and the `rp1-gpclk` resource is absent. Every
other target-facing preflight path was direct or absent exactly where the
existing logic permits it. No broader symlink exception is required.

The implementation leaves the general `rooted()` guard unchanged. A new
device-tree-specific resolver accepts only the exact kernel alias and exact
canonical target, requires a non-writable canonical root with the expected
owner, validates a bounded resource name, and resolves the resource beneath
the canonical root. It rejects a missing or changed alias, symlinked canonical
components, a symlinked resource, a non-directory resource, and descendant
symlinks.

The target-preflight fixture now models the real alias. Regressions cover an
absent resource, a direct resource, an altered alias, an unsafe name, a
symlinked canonical component, a symlinked resource, and a malicious
descendant symlink. The permanent-executor tests and the installed-CLI
rehearsal of all 38 attempts pass.

The repaired resolver also passed directly against wspr5's live read-only
filesystem topology from a transient `/tmp` copy, which was removed. The first
dynamic-import harness omitted Python's required module registration and the
second invocation found that cleanup had already removed the file; neither
reached the resolver or changed target state. The corrected harness recopied
the same inspected bytes, invoked the resolver successfully, and removed them.

Adversarial review found no need to relax any other path. The only special
case is the kernel-provided device-tree alias. Full-suite review also exposed
a historical Phase 5.46 assertion that compared its frozen transition
manifest with current worktree bytes. That assertion now uses the validator's
existing frozen-commit payload loader; the sealed Phase 5.46 controls remain
unchanged. The complete offline suite passes.

No Phase 5.46 control or evidence bytes were altered. No retry, freeze, build,
control generation, authorization, staging, service, DKMS, module, overlay,
boot, GPIO, clock, DMA, I2C, Si5351, SDR, antenna, transmission, or RF operation
occurred. Target access was limited to read-only filesystem-topology queries.
