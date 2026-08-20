<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 target installation failure review

Status: safely stopped; package not installed.

The authorized Phase 5.53 remover succeeded and reached terminal
`inactive-clean`. It exposed a defect in the old installation ledger: GPIO20
was ledger-owned and removed, but GPIO4 was not ledger-owned and remained as an
unowned file even though the old product claimed to install both overlays.

The remaining GPIO4 file was inactive, unowned by any Debian package, and
byte-identical to the Phase 5.54 package member. Standard `dpkg --install`
nevertheless failed before configuration because the boot filesystem rejected
the backup hard link `dpkg` attempted before replacing the existing path.

The failure did not register Phase 5.54 with DKMS, create its `/usr/src` tree,
or leave a package repair state. `dpkg --audit` is empty and package status is
`install ok not-installed`. The module and endpoint remain absent, no overlay
is active or boot-selected, the exact staged package remains available, and
the exact GPIO4 orphan remains unchanged.

The smallest recovery is not a package redesign or another installer. It is
one authenticated deletion of the exact unowned, inactive GPIO4 orphan,
followed by one retry of the same conventional package. This requires new
authorization because the original authorization allowed one installation
attempt and did not permit manual deletion.
