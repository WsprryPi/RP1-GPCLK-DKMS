<!-- SPDX-License-Identifier: MIT -->

# Read-only diagnostics

Run `rp1-gpclk-diagnostics` to print a bounded JSON report. Optionally pass
`--release-directory RELEASE` to compare a sealed release directory. The tool
does not install, load, bind, apply an overlay, enroll, change GPIO, repair, or
remove anything.

Endpoint discovery checks `/dev/rp1-gpclk`, the only canonical ABI v1 path.
The historical `/dev/rp1-gpclk0` spelling is not a supported fallback. A
missing endpoint is reported as unavailable; diagnostics do not create a
platform device or attempt binding.

The summary distinguishes healthy qualified, healthy Experimental,
build-compatible but live-disabled, unavailable, rejected, and indeterminate
because required inspection lacked privileges. Run as an administrator only
when support needs fields reported as permission-denied; elevated inspection
still performs no repair.

The report limits commands to five seconds, each command stream to 8192 bytes,
ordinary files to 4096 bytes, build/kernel logs to 16384 bytes, eight build
logs, and 128 journal-recorded residue paths. Kernel messages are current-boot
entries matching only this module. It excludes private keys, passphrases,
tokens, unrelated logs, and unrestricted system data.

An incomplete transaction or cleanup fault is a stop condition, not a repair
request. Preserve the report and request a separately authorized recovery
operation. A clean report does not prove absence of competing or direct-MMIO
software and is not hardware, timing, cleanup, coexistence, transmission, or
RF qualification.
