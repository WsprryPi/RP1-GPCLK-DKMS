<!-- SPDX-License-Identifier: MIT -->

# Phase 5.3 packaging and installation model execution prompt

## Authority and exit condition

Execute the package-layout and transactional-installation portion of Phase 5A
and Phase 5B in `phase5-packaging-operator-enablement-execution-prompt.md`.
Repository changes and deterministic offline/simulated validation are
authorized. System DKMS registration, installation, signing, key enrollment,
module loading, overlay activation, boot changes, reboot, target access, GPIO,
DMA, transmission, RF, tagging, and publication are not authorized by this
slice.

Phase 5.3 closes when the exact package layout and ownership rules are
machine-readable, the administrator command implements a recoverable
transaction model, every transition and failure point is tested without
dispatching a real system command, the complete offline suite passes twice,
and a separate adversarial review has no unresolved objective finding.

## Frozen package identity and destinations

Use package `rp1-gpclk-dkms`, DKMS module name `rp1-gpclk-dkms`, kernel module
name `rp1_gpclk_dkms`, and the exact Phase 5.2 release candidate
`0.0.0-phase5.2`. Phase slice numbering does not silently change the candidate
identity. Install:

- DKMS source below `/usr/src/rp1-gpclk-dkms-0.0.0-phase5.2/`;
- the DKMS-built module below
  `/lib/modules/KERNEL/updates/dkms/rp1_gpclk_dkms.ko`;
- allowlisted DTBOs below `/boot/firmware/overlays/`;
- release, compatibility, provenance, checksum, and installation policy under
  `/usr/share/rp1-gpclk-dkms/0.0.0-phase5.2/`;
- administrator configuration and enrollment under `/etc/rp1-gpclk-dkms/`;
- transaction state under `/var/lib/rp1-gpclk-dkms/`;
- administrator and diagnostic commands under `/usr/sbin/`, with their
  versioned implementations under `/usr/libexec/rp1-gpclk-dkms/`; and
- documentation below `/usr/share/doc/rp1-gpclk-dkms/`.

All package files and directories are `root:root`; directories and commands are
`0755`, ordinary files are `0644`, transaction state is `0600`, and the device
node remains `root:root 0600`. Administrator enrollment is never created by
installation. Existing administrator configuration, enrollment, keys,
certificates, unrelated overlays, and unmarked boot entries are not package
owned and must not be overwritten or removed.

## Transaction contract

The explicit install transaction is:

1. validate release identity, checksums, architecture/model, running-kernel
   headers, DKMS, overlay destination, signing policy, privileges, paths,
   ownership, and absence of an unresolved prior transaction;
2. create a private transaction directory and stage every package-owned file;
3. compare every staged SHA-256 digest with release/package metadata;
4. run exact-version `dkms add` and `dkms build`;
5. when policy requires it, sign with administrator-supplied material that is
   never copied, logged, owned, or removed;
6. verify module version, vermagic, file identity, and required signer before
   installation, then run exact-version `dkms install` and verify again;
7. install only the explicitly selected allowlisted DTBO, but do not add a boot
   marker, apply a runtime overlay, or select a route in application policy;
8. atomically install package policy, manifest, metadata, tooling, and docs;
9. verify the module is not loaded and record `liveOutput=false`; and
10. commit package state and report separately whether overlay activation, key
    enrollment, or reboot remains necessary.

Every checkpoint is durable. On failure, restore the prior complete package
state when every overwritten byte is still tool-owned and identifiable.
Otherwise converge to a documented inactive state: no module load or overlay
activation, `liveOutput=false`, the failure checkpoint and residue recorded,
and recovery required. `status` is read-only. `recover` is explicit and may
resume only a proven safe checkpoint or remove only recorded package-owned
residue. Unknown, malformed, symlinked, mismatched, or externally changed state
fails closed.

The signing checkpoint operates on DKMS's built, kernel-and-architecture-
specific module before `dkms install`; it must not assume the final installed
module already exists. Verify version, vermagic, and required signer on the
built artifact, then repeat those checks on the installed artifact. Installing
policy includes the frozen libexec implementations, `/usr/sbin` command links,
documentation, release metadata, and the empty configuration directory while
preserving every administrator-created file.

Checking `modinfo` exit status alone is insufficient: the coordinator must
compare the returned version and vermagic with the exact release and kernel,
and require a nonempty signer when signing is mandatory. The journal records
each created file's digest and each created directory. Recovery may remove a
file only while that digest still matches, may remove a directory only when
empty, and uses exact package/version DKMS uninstall/remove commands. Any
external change stops recovery and retains the inactive recovery-required
state.

## Prohibitions

The tool must never silently modify unrelated overlays or boot entries,
blacklist a driver, replace `clk-rp1`, choose an application route, activate an
overlay, enable `live_output`, create Experimental enrollment, load a module
rejected or absent from the manifest, weaken signing policy, reboot, or fall
back to `/dev/mem`, a custom kernel, or another physical transmitter backend.

## Required offline validation

Use a fake filesystem root and a recording command runner. Test success and
every failure checkpoint, hash tampering, path traversal, symlinks, preexisting
non-owned files, invalid route/version/kernel, missing tools/headers/signing
material, wrong module metadata/signature, interrupted state, recovery,
idempotence, exact ownership inventory, inactive-state reporting, and the
absence of every prohibited command or side effect. Inspect tests before
running them. Run SPDX, whitespace, documentation links, release validation,
the complete offline suite twice, and a separate adversarial assessment.

For each objective finding, add the missing assertion here, correct the
implementation, invalidate affected results, and repeat until no finding
remains. Commit and push the cohesive result when all offline gates pass. Do
not create or push a tag or publish a release.
