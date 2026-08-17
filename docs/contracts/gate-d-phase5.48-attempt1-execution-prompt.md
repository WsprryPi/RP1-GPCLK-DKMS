<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 bounded lifecycle attempt 1 prompt

Execute only indexed Phase 5.48 attempt 1 on `wspr5`, using authorization
commit `63c582fc26983d369868965c9b982bd6411b5436` and authenticated pre-root
evidence commit `398487c7186853f125a4792a2404f355c3998c34`.

Bind execution to installed executor SHA-256
`6af8b9fe690b5a2bb22930cb77593a46894da77bf9623c3722b9feb66139a004`,
root-marker SHA-256
`0178a13f603b5c4a007f3983a28264abe64c620dd19ecf9e88b9796a40852e8a`,
authorized instance SHA-256
`3dc6dff32898768e52f9a6d5d46075b65a33a60c3759d14dbae53009134cc667`,
attempt-index SHA-256
`aa71bda96970d8e1c2faabf7121a8015cefa5148fde5cb89d809cfef1d37265f`,
and index-entry-1 document `gd-current-supported-kernel-gpio4`, SHA-256
`2250622cb7af92f8445c21c26551a157d406bfdae87f182c02f02de109e2245e`.

Before creating attempt evidence, independently require the complete terminal
Phase 5.48 pre-root journal; exact root, installed-tool, document, index, and
instance identities; absent attempt evidence and attempt staging paths;
running stock kernel `6.18.34+rpt-rpi-2712`; inactive runtime; absent Phase
5.48 DKMS registration and overlay; and all six controlled services inactive.
Require the canonical snapshot and every sealed attempt `requiredPreState` to
agree with live service state. Do not start or stop a service to manufacture a
match. Use absolute system paths, including `/usr/sbin/dkms` and
`/usr/sbin/modinfo` when required by sealed tools.

Only after every precondition and read-only installed-executor validation
passes, invoke `/usr/libexec/rp1-gpclk-dkms/gate-d-executor execute` exactly
once with the root-bound document, index, instance, root privileges, and
`--execute`. Permit only its 19 sealed operations and exact owned paths. On
failure, use only journal-authorized recovery and stop. Never retry, resume,
skip, substitute, or begin attempt 2.

After a terminal result, independently validate the immutable journal and
evidence path set, final empty inactive baseline, candidate and predecessor
test versions absent, overlay absent, module and endpoint absent, services
restored to their inactive pre-states, no owned staging residue, and no
unsealed target files. Preserve the sealed Phase 5.48 input tree,
qualification root, pre-root journal, and installed permanent tools.

Output remains disabled. GPIO output, active clock output, DMA submission,
Si5351 operation, transmitter keying, SDR operation, antenna connection, RF,
`/dev/mem`, forced removal, general upgrade, and unreviewed persistent boot
mutation remain prohibited. The five deferred rows remain deferred.
