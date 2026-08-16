<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 authorized execution adversarial assessment

Status: failed closed safely during pre-root transition; no lifecycle attempt
began

The staged archive SHA-256 was
`7c327c88dc2da810745d417332db4cc67e81488c30d98f19c3f46b48a53db494`.
The pre-root envelope SHA-256 was
`d79c51337a4f78aff996c2c0e8991dfe344d5c8a78f7f77a54ab957b43b775fa`.
Target-side archive verification and read-only envelope validation passed before
the privileged command. The schema-v3 pre-root transition authenticated and
archived the prior recovered ledger, then invoked the administrator.

The administrator built and installed the Phase 5.36 DKMS candidate without
loading it, prepared the two compiled Gate D helpers, and transitioned the
three paths it was given. It then stopped at the first remaining installed
permanent tool:

```text
ValueError: unsafe or existing package file:
/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-diagnostics
```

This is a control-set integration defect. The pre-root envelope authenticates
an 18-path Phase 5.31-to-Phase 5.36 retained-tool transition, but the
administrator invocation receives transition identities for only the two
compiled helpers and `rp1-gpclk-admin`. `install_tool()` therefore treats the
other authenticated predecessor tools as unsafe existing package files. The
first rejection is diagnostics; bypassing it would merely expose the next
unrepresented retained path.

The authenticated `--resume` path ran immediately. Administrator recovery
removed the Phase 5.36 installation and restored every replaced predecessor
tool. Pre-root recovery then completed and retired its journal. Final-state
checks found no loaded module, device endpoint, or overlay. `dkms status` listed
no `rp1-gpclk-dkms` version. The separate I2C Si5351 path, GPIO output, clocks,
DMA, SDR, transmitter, antenna, reboot, transmission, and RF were not used.

Recovery preserved both ledgers rather than erasing evidence. The prior
Phase 5.34 recovered ledger is now the bound read-only archive at
`/var/lib/rp1-gpclk-dkms/history/phase5.34-transaction-recovered.json`, mode
`0400`, SHA-256
`48946aff65cc88a765510e86891fc9b67de71fa9b651a8ba0198893a053d2afa`.
The canonical mode-`0600` ledger records the recovered Phase 5.36 administrator
transaction, `liveOutput=false`, `recoveryRequired=false`, SHA-256
`1ee3c83cbd88d8980ee0be5b1514939a8bc66953b74d966a5a6151f295e6a51e`.

The result is path-invalid and supplies no lifecycle, compatibility, or
qualification evidence. Phase 5.36 must not be retried or modified in place.
The next successor must pass the complete authenticated transition map into
the administrator, prove that every retained destination is replaced exactly
once with predecessor and successor hashes bound, recover correctly after
failure at every replacement boundary, and reject omitted, extra, duplicate,
tampered, or non-permanent paths. It must also define the next recovered-ledger
handoff from the new canonical Phase 5.36 recovery ledger while retaining the
bound Phase 5.34 archive, then perform a new freeze, representative build, and
independently validated control set before any target retry.
