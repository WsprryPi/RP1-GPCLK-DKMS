<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 semantic-version selection prompt

## Decision

Select `1.0.0` as the initial public semantic version for RP1-GPCLK-DKMS and
`v1.0.0` as its exact expected Git tag. Use Debian binary-package version
`1.0.0-1` and DKMS/module version `1.0.0`.

## Required work

1. Update the module version, Debian build version, changelog, active roadmap,
   operator documentation, release notes, and every active version validator.
2. Preserve Phase 5.54 package, target, lifecycle, and removal evidence at its
   original development identities. Do not relabel it as exact `1.0.0`
   evidence.
3. Record the explicit version decision and advance only the
   `semantic-version-selection` gate.
4. Require final product and qualification artifacts to be generated twice
   from the clean committed `1.0.0` source and compared byte-for-byte.
5. Require exact-candidate inactive installation, GPIO4 and GPIO20
   output-disabled lifecycle, and removal/reinstall verification before final
   release review. Development-package evidence may guide those checks but may
   not substitute for the changed artifact identity.

## Authority boundary

This prompt authorizes repository-only version and contract changes, offline
tests, and a cohesive commit and push. It does not authorize artifact
publication, Git tag creation or push, GitHub release changes, target contact,
package installation or removal, module or overlay activity, boot changes,
reboot, GPIO/clock/DMA activity, transmission, RF, or consumer-repository work.

## Exit

Exit with a clean committed `1.0.0` source identity and next gate
`final-artifact-reproduction`. Do not construct release artifacts from dirty or
uncommitted bytes.
