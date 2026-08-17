<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 authorized output-disabled execution prompt

The operator's explicit authorization is bound to the Phase 5.45 decision
prompt committed at `d25abbf877fb889435b16e0b7d033291d0388af5`, the complete
control set committed at `53e55780d6e1aec4551836e9c499de501a83a602`, and the
preauthorization recapture committed at
`59c83bd57de5eb69c1982c4c24bc868564f5f7d7`.

The authorized candidate is frozen source
`4b50db7868b7fe5ca9d830f51cd404c250192188`, release archive SHA-256
`21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356`,
and canonical snapshot SHA-256
`66208586a112792e91185a7ce67d5952427dc218fb8a392ac1bfb221ed51e4c8`.
The preauthorization execution instance was
`8418fd031ac14e40c69c19b2d192783f2acf092351406b6455b3c96ede1f03ba`
and its envelope was
`39708b026f38da5edc83932a740d246233d26e4f87fccfc73a540e13542bef90`.

The authorized regenerated execution instance is
`0a4e2b88263262d408aa30c39e4843aa1204735333cedf6bb472dfc1a50ef228`
and its dependent pre-root envelope is
`1a01c76d95e06fae7a132b05c3dc5d1ef3db1c71ea4e00fc4f7d6a10cc686742`.
The unchanged 38-attempt index is
`3375c809dd699949f991742716628016a680bcf7253fc30ba8f3de52c294f020`.

Authorization is limited to those 38 attempts in ten ready rows, namespace
`phase5.45-4b50db7868b7`, seven release inputs, the snapshot-derived 28-path
Phase 5.43 predecessor inventory, the frozen successor inventory, and the
sealed schema-5 transition, recovery, service, stock-kernel, DKMS, overlay,
load-disabled, query, unbind/rebind, unload, bounded failure-injection, and
cleanup operations. Five deferred environmental rows remain excluded.

Before staging, require a byte-identical canonical recapture, the exact
inactive runtime and six inactive services, a terminal complete Phase 5.43
ledger, exact inventories and kernel identities, authenticated recovery, no
antenna, unused SDR, and the disconnected and unused separate I2C Si5351 path.
Stop on the first identity, state, timeout, service, recovery, residue,
cleanup, transition, or safety discrepancy. Use only authenticated permanent
tools and journal-authorized recovery. Terminal recovery must not start a new
attempt.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation remain prohibited.

This slice records and validates authorization only. It does not stage inputs
on `wspr5` or begin lifecycle execution.
