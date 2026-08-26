<!-- SPDX-License-Identifier: MIT -->

# Read-only diagnostics

Run `rp1-gpclk-diagnostics` to print a bounded JSON report. Optionally pass
`--release-directory RELEASE` to compare a sealed release directory. The tool
does not install, load, bind, apply an overlay, enroll, change GPIO, repair, or
remove anything.

For an exact-source installation, pass
`--development-manifest DEVELOPMENT_MANIFEST.json` instead. Diagnostics checks
the separate source-development schema and reports it as Experimental and not
release-qualified. A release directory and development manifest are mutually
exclusive.

Endpoint discovery checks `/dev/rp1-gpclk`, the only canonical ABI v1/v2/v3 path.
The historical `/dev/rp1-gpclk0` spelling is not a supported fallback. A
missing endpoint is reported as unavailable; diagnostics do not create a
platform device or attempt binding.

Diagnostics attempts the additive ABI-v2 query first and falls back to ABI v1
only when the endpoint reports that v2 is unsupported. The report records the
query version, complete advertised capability mask, ABI range, module/build/
compatibility identities, and finite-TONE bounds when v2 is available.

When ABI v3 is available, diagnostics also performs one read-only
`GET_SNAPSHOT_V3` request on a separately opened descriptor and closes that
descriptor in all outcomes. The request never acquires an execution owner or
lease and never exposes a lease token. It reports the route and compatibility
identity, owner/lease presence, operation and drain state, retained terminal
reason and generation, valid elapsed/remaining time, cleanup fault, live-output
and live-eligibility observations, and tri-state GPIO/clock/DMA quiescence.
`unknown` is preserved as unknown; it is never converted into a safe result.
The descriptor open itself is passive but still counts as endpoint access and
therefore requires separate target authorization before running diagnostics on
a target.

Active route discovery walks the live device tree for the exact
`rp1-gpclk-dkms-gpio4` and `rp1-gpclk-dkms-gpio20` endpoint names. It reports
zero, exactly one, or ambiguous active topology and separately checks whether
the sole endpoint name, endpoint route property, and module-reported route
agree. It records the size and SHA-256 of that node's compatible, register,
clock, DMA, and pinctrl properties without interpreting phandles through a
fixed path. These observations do not substitute for WsprryPi's requested and
persisted route or for the route manager's configured and reconciled state.

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
