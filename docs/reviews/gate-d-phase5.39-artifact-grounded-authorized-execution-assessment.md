<!-- SPDX-License-Identifier: MIT -->

# Phase 5.39 artifact-grounded authorized execution assessment

Status: pre-root transition passed; first lifecycle attempt failed closed at
read-only preflight; no later attempt began

The fresh authorization was bound to corrected control-set commit
`b215da6358d9638ae1363c0662d2f52aa340d9c0`. Authorization-bound bytes were
committed and pushed as `7dc1da0` before staging. The authorized
execution-instance SHA-256 was
`32e65d7da87902ed3d4903756e4b891eebbe2cbe2a40009c7d3f5fff64b87dbc`,
and the schema-4 pre-root envelope SHA-256 was
`506e5d10af83ddec81621c106ffd670242b9254a05a2a74a6302183cb063eeac`.

Target preflight passed the inactive stock-kernel baseline, exact typed 28-path
predecessor package inventory, recovered Phase 5.37 ledger, preserved Phase
5.36 and Phase 5.34 archives, and live comparison of all seven representative
build artifacts against the measured inventory. After staging, all 67 bound
input files matched. The envelope itself was then staged and independently
verified against its authorized digest. The authenticated read-only pre-root
validation returned `valid=true`, `readOnly=true`, and
`outputDisabled=true`.

The schema-4 pre-root transition completed. It transitioned all 28 package
paths, installed and built Phase 5.39, copied and authenticated the qualification
root, and ran bounded cleanup. Its journal is complete with `liveOutput=false`.
The canonical administrator transaction is complete, recovery-free, and
output-disabled, SHA-256
`6b01b65dff8db2d2b583229b56c9724b1a0b703f2adc5a7f715b984242345844`.
The recovered predecessor ledger is preserved as the Phase 5.37 read-only
archive with its prior SHA-256
`24af8111eaa7e9f0c5084dd39063160a5188195a73667b3fcbf115c3c4ea64cf`.

The permanent executor and the first indexed plan validated. Execution of
`gd-current-supported-kernel-gpio4` then failed during its second internal
step, `capture-preflight`, while reading:

```text
/proc/sys/kernel/module_sig_enforce
```

That procfs entry is absent on the exact stock kernel
`6.18.34+rpt-rpi-2712`. The executor calls `/usr/bin/cat` with only exit status
zero accepted, so absence raises `CalledProcessError`. The sealed attempt
journal has document SHA-256
`173ceac3d8d85953572f8e718fd021fb7986ffcd2d0fd0d3171309e11335429e`,
status `inactive-recovery-required`, `liveOutput=false`, and contains only the
completed evidence-creation record plus the pending preflight record.

No indexed recovery document authorizes transforming this unexpected
top-level preflight failure into another attempt. The matrix therefore stopped;
the failed authorization must not be reused. The qualification root, completed
pre-root journal, installed inactive package/tool transition, and immutable
failed-attempt evidence remain preserved for a reviewed successor recovery.

Final inspection found no DKMS test version, loaded module, device endpoint, or
overlay. Services retained their observed states. No route was applied; no
GPIO, clock, DMA, Si5351, SDR, transmitter, antenna, reboot, transmission, or RF
operation occurred.

The next successor must define the stock-kernel module-signing policy probe
without requiring `/proc/sys/kernel/module_sig_enforce` to exist. It must
distinguish an absent optional sysctl from an actual read error, derive the
effective enforcement state from reviewed stock-kernel sources, add exact
present/absent/error tests, and provide a sealed terminal recovery for this
preserved preflight failure before any new lifecycle attempt or authorization.
