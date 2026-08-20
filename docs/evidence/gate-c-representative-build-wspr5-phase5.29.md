<!-- SPDX-License-Identifier: MIT -->

# Phase 5.29 representative build on wspr5

## Outcome

The exact clean implementation commit
`c58b541158aa6b8e535becb04c50d41767558793` produced two independently built,
byte-identical development release units. The source archive SHA-256 is
`7d2516c0a85a56fd7be521c519883c69214cac81759d05efb36352890cefd68e`.
Both release validations passed.

That archive was extracted beneath
`/home/pi/gate-c-evidence/phase5.29-c58b541` on `wspr5`. A build against the
stock `6.18.34+rpt-rpi-2712` headers completed successfully. The module SHA-256
is `1d532a063daae542a341e33649a9c87d56e902b781affadeebe0f2025d72d0eb`;
`modinfo` reported version `0.0.0-phase5.29` and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. Both Gate D
helpers compiled but were not executed.

The first metadata command used bare `modinfo`, which was absent from the
non-interactive SSH `PATH`. The already-built artifact was then checked with
the target's absolute `/usr/sbin/modinfo`; this was an evidence-command path
correction, not a source or target change.

## Target and safety evidence

The target was AArch64 with `/lib -> usr/lib`, the stock header `build` alias
resolving to root-owned mode-0755
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`, configuration SHA-256
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`,
`Module.symvers` SHA-256
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`,
and compiler `cc (Debian 14.2.0-19) 14.2.0`.

No DKMS installation, module load, binding, endpoint, overlay, GPIO, clock,
DMA, Si5351, transmitter, SDR operation, antenna, or RF activity occurred.
Services remained `wsprrypi=active`, `sdrplay=active`,
`sdrconnect-server=inactive`, and `SoapySDRServer=active`. The retained staging
directory is build evidence, not installed system state. This result supports
only `Compatible-unqualified` build compatibility.
