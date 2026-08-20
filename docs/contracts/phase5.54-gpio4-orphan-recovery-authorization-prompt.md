<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 GPIO4 orphan recovery authorization prompt

## Objective

Recover the stopped `wspr5` transition with one exact orphan deletion and one
retry of the unchanged conventional Debian package, then stop before lifecycle
attempt 1.

## Bound state

- failure-state capture SHA-256:
  `603477ad4a34947dc56ef993cb177e92248dde9b01f7a0b1b9e442182d953b88`;
- staged package SHA-256:
  `a6bcc854bb807c298b07d81a0405960fbdc7e053df80802e2e95ebc2ca02f095`;
- orphan path: `/boot/firmware/overlays/rp1-gpclk-gpio4.dtbo`;
- orphan and candidate-member SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`;
- predecessor ledger status: `removed`, checkpoint `inactive-clean`;
- `dpkg` state: audit empty, `rp1-gpclk-dkms` not installed;
- candidate DKMS registration and source tree: absent.

## Authorized operations

1. Recapture the complete bound failure state read-only and require exact
   equality. Require the orphan to be a regular non-symlink file, exact hash,
   unowned by `dpkg`, inactive, and not boot-selected.
2. Delete exactly that one orphan path. Do not delete any other boot file.
3. Rehash the unchanged staged `.deb` and invoke exactly one
   `/usr/bin/dpkg --install` retry.
4. Require exact package and DKMS versions, the versioned UAPI/source closure,
   package ownership of both overlay paths, exact overlay hashes, absent module
   and endpoint, no active or boot-selected overlay, inactive controlled
   services, and no qualification installation.
5. Remove only the user-owned staged package and its empty staging directory;
   record evidence, commit, push, and stop before lifecycle attempt 1.

If any precondition differs or the retry fails, preserve the resulting state,
capture it read-only, and stop without another retry or improvised repair.

## Prohibited work

Do not install qualification tooling; load, bind, unbind, or unload the
module; apply an overlay; edit boot configuration; reboot; change GPIO,
pinctrl, clock, or DMA state; transmit; or produce RF.

## Exact authorization phrase

> I explicitly authorize the exact Phase 5.54 GPIO4 orphan recovery on wspr5
> bound to failure-state capture
> 603477ad4a34947dc56ef993cb177e92248dde9b01f7a0b1b9e442182d953b88,
> staged Debian package
> a6bcc854bb807c298b07d81a0405960fbdc7e053df80802e2e95ebc2ca02f095,
> and exact unowned inactive GPIO4 orphan
> c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6,
> including deletion of only that orphan, exactly one package-install retry,
> verification, and removal of only the user-owned staging residue. Stop before
> lifecycle attempt 1. I do not authorize qualification tooling, module or
> overlay activity, boot changes, reboot, GPIO/clock/DMA activity,
> transmission, or RF.
