<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 attempt 2 current-kernel GPIO20 execution prompt

Execute only the second indexed Phase 5.52 attempt,
`gd-current-supported-kernel-gpio20`, SHA-256
`e3eff89826a8aadf0ae8f16d907cb439fd37717b4bef06705ae2f1fb796ce70c`,
through authorization commit `8e8cdbe5d573d9c1744003c173c47463060d7f31`,
successful pre-root evidence commit
`08db08f4aa18bd471bb6424b23f80b8d745c42ba`, and successful attempt-1
evidence commit `86608dee5571ca8faf7308633883a81a24f3e6a5`.

Use only the installed permanent executor at
`/usr/libexec/rp1-gpclk-dkms/gate-d-executor`, SHA-256
`70f845be52c2cc7993a53aa2d7e7258319e261854903fd7a2c6d5dce29fa4061`.
Invoke its `validate`, `plan`, and `execute` CLI directly. Do not substitute
the control-set copy, archived pre-root executor, or underscore-named installed
copy. If independent import of the extensionless executor is required, use
`importlib.machinery.SourceFileLoader`.

Before execution, require schema-6 instance SHA-256
`8f53fa6c41153965d49f11a4da7b139c3aa0e17cd1e9a2a77f8157c21cf43bd2`,
attempt-index SHA-256
`744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8`,
terminal pre-root journal SHA-256
`9cd462085a3c86d2d8992197470a600aff6ec256526a5c30e49d62239fde403a`,
and successful sealed attempt-1 journal SHA-256
`17b35b2e3105dbb12c867009bd335d8c478cbe65bdaea6f7302245c68a89f825`.
Require absent attempt-2 evidence and staging paths, inactive runtime and all
six services, zero forbidden files or extended attributes in Phase 5.52-owned
namespaces, unchanged physical safety, and no mutation of historical paths.

Execute the sealed 20-step output-disabled GPIO20 lifecycle exactly once. Stop
on the first identity, state, service, timeout, recovery, residue, cleanup, or
safety discrepancy and use only journal-authorized recovery. On success require
20 accepted records, terminal `complete`, `sealed=true`,
`recoveryRequired=false`, and verify the seven canonical schema-2 evidence
files through their own `SHA256SUMS`.

Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA,
Si5351 or SDR operation, antenna connection, transmission, RF, `/dev/mem`,
forced removal, general upgrade, reboot, persistent boot mutation, and every
other indexed attempt remain prohibited.
