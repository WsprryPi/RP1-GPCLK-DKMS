<!-- SPDX-License-Identifier: MIT -->

# Phase 4 Gate B clock-disabled evidence

Date: 2026-08-14
Status: Phase 4A clock-disabled regression passed; live qualification not run
Compatibility ceiling: `Compatible-unqualified`

## Authorization record

The user authorized the following exact scope:

> On wspr5, you may build, install, sign, load, bind, unbind, unload, and remove
> the Phase 4 test module; apply/remove only the GPIO4 and GPIO20 test overlays;
> and create/remove disposable test, signing, and evidence files. You may not
> change boot configuration, reboot, alter services, or produce GPIO/RF output
> under Gate B.

This authorization permits clock-disabled administration only. It does not
authorize active pinctrl selection, clock preparation or enablement, DMA
descriptor submission, GPIO output, transmitter keying, SDR capture, or RF.

## Read-only entry identity

- Hostname: `wspr5`
- Model: Raspberry Pi 5 Model B Rev 1.0
- Kernel: stock `6.18.34+rpt-rpi-2712`, Debian
  `1:6.18.34-1+rpt1`, aarch64
- Boot ID: `0f9d1f9b-c27b-4e6a-962f-b8e8ac3683d7`
- `/dev/rp1-gpclk`: absent
- `rp1_gpclk_dkms`: not loaded
- Runtime overlays: none loaded

The final accepted run used source archive
`rp1-gpclk-phase4a-build-11.tar.gz`, SHA-256
`06e189eeb46847e018758402d057a7c3ae42c9f4994448b53235bd52c0b0ab44`.
The built unsigned module SHA-256 was
`5ecab68ad1da2319af7e45019c05e53240344a6d834389f537598e87e5b3db84`;
the disposable signed derivative reported version `0.0.0-phase4a`, license
`Dual MIT/GPL`, and exact running-kernel vermagic.

The accepted runner result was `PHASE3B_TARGET_RESULT=PASS`. It completed both
clock-disabled route matrices, inert Phase 4 submissions, route conflicts,
process death, open-file unbind/unload, repeated route orderings,
missing-header recovery, diagnostic classification, and explicit removal.
Both route queries reported capabilities `0x7f`; `LIVE_ELIGIBLE` (`0x80`) was
absent. GPIO4 and GPIO20 remained inputs and clock prepare/enable counts stayed
zero. The protect count was one only while an endpoint was bound and returned
to zero after removal.

The portable evidence archive SHA-256 is
`e7580f19aed26602e37db05c8670ce7a892e338cebbc73cbd19a1e7089585681`.
Its internal `SHA256SUMS` verified on `wspr5`, then verified again after
download and extraction beneath an independently created relocation directory.

Failed runs were preserved separately and excluded from acceptance. Run 7
found a Linux-only errno fixture defect before module build. Runs 8 and 9
exposed incorrect RP1 range derivation and failed closed at probe. Every trap
proved both pins input, all clock counts zero, no overlay, no module, and no
installed artifact before reinjection.

## Gate C authorization recorded after Gate B

The user separately confirmed this exact controlled-output scope:

> Selected GPIO pin -> 10 dB attenuator -> 10 dB attenuator -> RSP1B, with no
> transmitter, amplifier, filter, dummy load, splitter, or antenna connected.
> GPIO4 first, then physically move the lead and qualify GPIO20 separately;
> 2 mA drive; 10.1402 MHz; bounded test bursts no longer than 10 seconds each;
> no service changes.

The attached instrument was identified read-only as an SDRplay RSP1B, serial
`2404058C60`, available locally and through the already-running SoapySDR
server. Gate C permits only the named direct conducted measurement path. GPIO4
must complete cleanup and review before the physical lead is moved and GPIO20
receives a separate run. This does not authorize a transmitter, amplifier,
filter, antenna, intentional radiation, or Gate D RF qualification.

No SDR was opened, no samples were captured, no active pinctrl state was
selected, no clock was prepared/enabled, no target DMA descriptor was
submitted, and no GPIO or RF output occurred during this evidence run.
