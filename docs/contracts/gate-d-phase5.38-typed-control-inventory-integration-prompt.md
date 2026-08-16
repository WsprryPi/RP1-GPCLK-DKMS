<!-- SPDX-License-Identifier: MIT -->

# Phase 5.38 typed control-inventory integration prompt

Extend the Gate D bootstrap plan and pre-root envelope with a new schema
version that authenticates the complete package-path closure required by
qualification identity schema 3. Preserve schema versions 1 through 3 solely
for already sealed historical evidence.

The new typed inventory must represent regular files and symlinks explicitly.
Regular files bind canonical absolute path, SHA-256, mode, owner UID, and group
GID. Symlinks bind canonical absolute path, exact relative link target, owner
UID, and group GID. Require unique paths, safe canonical parents, supported
types, exact set equality between bootstrap and pre-root inventories, and the
complete retained Python import graph. During verification, inspect link leaves
without following them and reject missing, extra, duplicate, wrong-type,
wrong-hash, wrong-target, wrong-mode, or wrong-ownership state.

Add deterministic offline tests for a mixed file/symlink inventory and every
identity mutation. Preserve historical validators and control sets. Run
focused tests, the complete offline suite, and a separate adversarial review.
This slice is repository-only: do not stage target inputs, administer DKMS,
mutate ledgers or package paths, load modules, activate overlays, change boot
or services, access GPIO, enable clocks, submit DMA, operate the separate I2C
Si5351, use SDR/transmitter equipment, reboot, transmit, or produce RF.

Exit only when the new typed contract is internally consistent, historical
evidence still validates, all checks pass, and the next gate is explicitly a
new freeze and representative build before Phase 5.38 control-set generation.
