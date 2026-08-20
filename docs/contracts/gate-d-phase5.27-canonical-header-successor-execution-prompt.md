<!-- SPDX-License-Identifier: MIT -->

# Phase 5.27 canonical-header successor execution prompt

## Objective and verified starting point

Create a distinct `0.0.0-phase5.27` successor for the Phase 5.26 candidate that
failed before DKMS registration on `wspr5` because the installer rejected the
stock kernel's `/lib/modules/6.18.34+rpt-rpi-2712/build` symlink. Preserve the
Phase 5.26 candidate and failure evidence. The Si5351 is a separate I2C output
path; GPIO4 and GPIO20 are reserved, independent DKMS routes.

## Required correction

Keep the generic installation-path resolver symlink-free. Add one bounded
kernel-header resolver that accepts only the final `build` link, resolves it
strictly, and requires the canonical directory to be below the target root's
`/usr/src`. Reject missing paths, escapes, unexpected canonical symlink
components, non-directory targets, ownership different from the target root,
and group- or world-writable targets. Accept no arbitrary header override.

Add deterministic tests for the real stock absolute-link shape and for escape
and writable-target rejection. Perform no module load, overlay activation,
GPIO access, clock enablement, DMA submission, transmitter action, or RF.

## Successor lifecycle

1. Give all active package, module, layout, lifecycle, and test identities the
   distinct Phase 5.27 version; retain historical Phase 5.26 evidence unchanged.
2. Run the complete offline suite and whitespace checks, then independently
   review path containment, TOCTOU exposure, ownership/mode policy, fake-root
   behavior, packaging identity, safety boundaries, and claim accuracy. Correct
   every actionable finding and repeat affected checks.
3. Commit the reviewed implementation. From that exact clean commit, create two
   isolated development release builds and require byte-identical archives.
   Record the source commit, archive SHA-256, sidecar hashes, commands, and
   non-publishable status as the new freeze.
4. Stage only the exact frozen archive and sidecars on `wspr5`; verify hashes,
   kernel/config/compiler/architecture identities, then compile against the
   running stock kernel headers. This is build-compatibility evidence only.
5. Rebind the Gate D route decision, target plan, attempts, bootstrap envelope,
   execution instance, authorization record, and all embedded hashes to the
   exact Phase 5.27 freeze and representative module. Validate the complete
   control set adversarially before mutation.
6. Under the user's explicit authorization, execute only the bounded,
   output-disabled lifecycle. Fail closed on identity drift, unrelated target
   activity, residue, timeout, or cleanup ambiguity. Preserve evidence and
   restore the declared inactive baseline after each attempt.

## Exit criteria and report

Do not claim success unless the correction is reviewed, the freeze reproduces,
the representative build passes, the control set is closed, and every executed
attempt has sealed evidence plus an inactive baseline. Otherwise stop at the
first failed gate and report it as the next blocker. Report exact commits and
hashes, checks, target mutations and cleanup, skipped work, Git state, and push
result. Do not tag, publish, open a PR, or advance WsprryPi qualification.
