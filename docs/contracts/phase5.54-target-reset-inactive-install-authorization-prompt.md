<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 target reset and inactive Debian installation authorization prompt

## Objective

Perform one bounded transition on `wspr5` from the verified inactive Phase
5.53 custom installation to the exact conventional Phase 5.54 Debian DKMS
package, then stop before module lifecycle testing.

This document is non-authorizing until the operator supplies the exact phrase
below. The preauthorization slice has completed only two byte-identical
read-only captures; it performed no transfer or target mutation.

## Bound identities

- candidate evidence commit:
  `d1c11b01ac48e25299f7b3eff4b983f9928cf9da`;
- package: `rp1-gpclk-dkms_0.0.0~phase5.54-1_all.deb`;
- package SHA-256:
  `a6bcc854bb807c298b07d81a0405960fbdc7e053df80802e2e95ebc2ca02f095`;
- package-member inventory SHA-256:
  `636d7782d3387514b33afbb55ec32bf9d899bbc205b3a70dd662e5a0840327c8`;
- package-control inventory SHA-256:
  `5332cf73af15f17e0bc8a921e58bf1aaaae52d2513b404f56fa6f948322ff0a7`;
- predecessor ledger SHA-256:
  `d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d`;
- preauthorization recapture SHA-256:
  `c0ae4d544135462eda9454c750082d30617c045500ce3d81159da14d6feead80`;
- canonical UAPI SHA-256:
  `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`;
- GPIO4 DTBO SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`;
- GPIO20 DTBO SHA-256:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

## Authorized work only after the exact phrase

1. Require the repository and ignored local package candidate to match every
   bound identity. Reinspect the literal package members and generated
   `postinst`/`prerm`; reject any difference.
2. Repeat the exact read-only target capture. Require byte equality with the
   preauthorization capture, including boot ID, kernel, predecessor ledger,
   DKMS state, inactive services, absent module and endpoint, no loaded or
   boot-selected overlay, absent Debian successor, and absent qualification
   ledger. Any mismatch exhausts authorization.
3. Transfer only the exact `.deb` to a newly created user-owned staging
   directory using a byte stream, restrictive mode, and no copied metadata,
   links, special files, or directory tree. Rehash it on `wspr5` and reject a
   mismatch.
4. Before removal, require `dkms`, `dpkg`, the exact running-kernel headers,
   compiler, `Module.symvers`, and both inactive safety conditions. Run no
   package repair, dependency installation, network access, or kernel action.
5. Invoke exactly one installed Phase 5.53
   `/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin remove --execute`. Its own
   ledger validation must authenticate every removal path before its first
   write. It may uninstall/remove only DKMS release `0.0.0-phase5.53` and
   remove only ledger-owned bytes. Stop on any mismatch; do not improvise.
   Preserve its terminal `status=removed` ledger as the authenticated audit of
   the one-time transition; the Debian package does not own or consume it.
6. Verify the Phase 5.53 DKMS registration and ledger-owned product paths are
   absent, while the staged `.deb` remains exact. Invoke exactly one
   `dpkg --install` for the bound package. Accept only the standard generated
   `dh-dkms` add/build/install behavior for module `0.0.0-phase5.54` against
   kernel `6.18.34+rpt-rpi-2712`.
7. Verify `dpkg` reports the exact Debian version, DKMS reports the exact
   module/kernel installed, the versioned source closure and UAPI hashes match,
   both DTBO hashes match, the module and endpoint remain absent, no overlay is
   applied or boot-selected, controlled services remain inactive, and no
   qualification file was installed. Require the preserved Phase 5.53 ledger
   to be terminal `status=removed`, `checkpoint=inactive-clean`, and
   `recoveryRequired=false`.
8. Remove the user-owned transferred `.deb`, record durable evidence and an
   adversarial review, commit and push attributable repository evidence, then
   stop. Do not begin representative lifecycle attempt 1.

If package installation fails after the predecessor is removed, preserve the
ordinary `dpkg` and DKMS failure state, capture it read-only, and stop. This
authorization does not permit improvised repair, rollback, package downloads,
or manual deletion.

## Prohibited work and claim ceiling

Do not install qualification tooling; load, bind, unbind, or unload the
module; apply an overlay; edit boot configuration; reboot; change GPIO or
pinctrl state; enable a clock; submit DMA; operate the Si5351 or SDR; transmit;
or produce RF. Success establishes only an inactive conventional package and
representative DKMS build/install result for the exact kernel. Lifecycle and
route qualification remain separate gates.

## Exact authorization phrase

> I explicitly authorize the exact Phase 5.54 target reset and inactive Debian
> installation on wspr5 bound to candidate evidence commit
> d1c11b01ac48e25299f7b3eff4b983f9928cf9da, predecessor ledger
> d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d,
> preauthorization recapture
> c0ae4d544135462eda9454c750082d30617c045500ce3d81159da14d6feead80,
> and Debian package
> a6bcc854bb807c298b07d81a0405960fbdc7e053df80802e2e95ebc2ca02f095,
> including one final byte-identical read-only recapture, metadata-free
> transfer, exactly one ledger-bound Phase 5.53 removal, and exactly one
> standard inactive Phase 5.54 package installation. Stop before lifecycle
> attempt 1. I do not authorize qualification tooling, module or overlay
> activity, boot changes, reboot, GPIO/clock/DMA activity, transmission, or RF.
