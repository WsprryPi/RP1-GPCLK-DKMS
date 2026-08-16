<!-- SPDX-License-Identifier: MIT -->

# Phase 5.34 authorized execution result

Date: 2026-08-16
Host: `wspr5`
Candidate: `0.0.0-phase5.34` at `3a3f970739934ead0f49629d0a9cda8113b33357`
Result: **failed closed during qualification installation; recovered inactive**

The exact authorized control set was committed before staging. Release and
control inputs passed their hashes, the 18 retained predecessor paths matched
Phase 5.31, and the authenticated pre-root executor began the bounded
qualification installation.

The administrator completed DKMS add, build, and install verification and
began the ledgered permanent-tool transition. It then failed with `KeyError`
for `/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-diagnostics`. The qualification
identity correctly enumerated only the 18 permanent Gate D transition paths,
but `install_tool()` incorrectly required every unrelated installed tool to be
present whenever a transition graph existed. No module was loaded or bound and
no overlay was activated.

The sealed terminal pre-root recovery ran once and returned `status: recovered`
without beginning another attempt. The failure journal was preserved at
`/var/lib/rp1-gpclk-dkms/gate-d/pre-root-phase5.34.failure.json`, SHA-256
`3602390602ce5ef2aaa979e26fa569c9c002407966a90f435b8b991c94b52904`.
The administrator's recovered ledger remains at its canonical path with
SHA-256 `48946aff65cc88a765510e86891fc9b67de71fa9b651a8ba0198893a053d2afa`.

Final checks found no Phase 5.34 qualification root, active pre-root journal,
DKMS version, loaded module, or endpoint. The Phase 5.31 executor, pre-root
module, and administrator hashes were restored exactly. No GPIO access, clock
enablement, DMA, Si5351 operation, SDR or transmitter use, antenna connection,
transmission, reboot, or RF occurred.

Phase 5.34 must not be retried. The next successor must make transition lookup
conditional per exact path: paths enumerated in the qualification transition
graph use the ledgered predecessor/successor replacement contract; unrelated
ordinary package tools retain their existing installation contract. Tests must
cover a mixed transition/non-transition installation before a new freeze.
