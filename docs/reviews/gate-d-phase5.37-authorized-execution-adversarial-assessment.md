<!-- SPDX-License-Identifier: MIT -->

# Phase 5.37 authorized execution adversarial assessment

Status: failed closed safely during pre-root transition; no lifecycle attempt
began

The authorized control-set commit was
`67ceb102ad670955a498344eb4899a98dd94f744`, for frozen source commit
`71932324ec977d30ec0fadd48ef2673c49a6e173`. The authorized execution-instance
SHA-256 was
`05b8f70094fc2c613d75c9d93bc4e9b9f5bdd282b9462910e8f65bc89a322c26`.
The staged archive SHA-256 was
`91432acb0a852fb949884142b68edd65c97496e20898c7b8ffbbc796895817c0`,
and the pre-root envelope SHA-256 was
`dea97404b14012431fe96505b7ba2ff3ea1371637f9dcefda89ecf00dae9d60b`.

Before staging, the target had the required inactive baseline: no loaded
module, device endpoint, Phase 5.37 DKMS entry, or overlay; no pre-root journal;
and no Phase 5.37 input or qualification directory. The canonical recovered
ledger and retained Phase 5.34 archive had their sealed identities, ownership,
and modes. All 22 retained permanent-tool identities matched the Phase 5.31
predecessor inventory. Target-side archive verification and read-only envelope
validation passed before the privileged command.

The schema-v3 pre-root transition authenticated and archived the predecessor
ledger, installed all 22 successor permanent tools, and invoked the
administrator. The administrator then stopped at the first pre-existing
documentation destination:

```text
ValueError: unsafe or existing documentation:
/usr/share/doc/rp1-gpclk-dkms/diagnostics.md
```

This is a control-set integration defect. Phase 5.37 completely models the
retained executable-tool set, but not the complete retained package-owned path
set. The target also retains these four root-owned, mode-`0644` documentation
files:

- `diagnostics.md`, SHA-256
  `380f809e238309535e228492bd04bd5bd3c7ac19acf3448550747bb08a45d66c`;
- `gate-d-target-runbook.md`, SHA-256
  `59a3b9b2803e7c12593addbfefca4a251a6c43e42c917736d42f8b7cd3e47cbf`;
- `lifecycle.md`, SHA-256
  `2878cd700e00b2c466929b5be810df6205bd318cc117245c0470901b192d9649`;
  and
- `signing.md`, SHA-256
  `8a86a6c6a1cbbe69d28ca982a3a89794181dd1e6924dedba0b513ad9452058db`.

The retained package surface also includes the root-owned
`/usr/sbin/rp1-gpclk-admin` and `/usr/sbin/rp1-gpclk-diagnostics` symlinks,
whose relative targets are respectively
`../libexec/rp1-gpclk-dkms/rp1-gpclk-admin` and
`../libexec/rp1-gpclk-dkms/rp1-gpclk-diagnostics`. The observed documentation
failure occurred before either symlink became a failure point, so their
existing treatment is not inferred to be sufficient.

The sealed `--resume` recovery path ran immediately. Administrator recovery
removed the Phase 5.37 installation and restored all 22 predecessor tools.
Pre-root recovery then completed and retired its journal. Final-state checks
found no loaded module, device endpoint, overlay, Phase 5.37 DKMS entry, or
Phase 5.37 qualification directory. The documentation files and command
symlinks retained their predecessor identities. The separate I2C Si5351 path,
GPIO output, clocks, DMA, SDR, transmitter, antenna, reboot, transmission, and
RF were not used.

Recovery preserved the evidence chain. The Phase 5.34 read-only archive remains
SHA-256
`48946aff65cc88a765510e86891fc9b67de71fa9b651a8ba0198893a053d2afa`.
The Phase 5.36 predecessor ledger is now the mode-`0400` read-only archive at
`/var/lib/rp1-gpclk-dkms/history/phase5.36-transaction-recovered.json`, SHA-256
`1ee3c83cbd88d8980ee0be5b1514939a8bc66953b74d966a5a6151f295e6a51e`.
The canonical mode-`0600` ledger records recovered state with
`liveOutput=false` and `recoveryRequired=false`, SHA-256
`24af8111eaa7e9f0c5084dd39063160a5188195a73667b3fcbf115c3c4ea64cf`.

The result is path-invalid and supplies no lifecycle, compatibility, or
qualification evidence. Phase 5.37 must not be retried or modified in place.
The next successor must enumerate and authenticate the complete retained
package-owned canonical-path closure before DKMS or installation begins,
including regular files, directories, and symlinks with exact type, hash or
link target, mode, owner, and group. It must reject omitted, extra, duplicate,
tampered, substituted-type, or non-canonical paths; transition each mutable
destination exactly once; and prove recovery after failure at every boundary.
It must preserve the Phase 5.34 and Phase 5.36 archives and define the handoff
from the recovered Phase 5.37 canonical ledger. Only after independent
adversarial validation may that successor receive a new freeze, representative
build, control set, and separately authorized target execution.
