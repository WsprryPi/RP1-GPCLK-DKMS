<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 metadata-free staging and pre-root execution prompt

Execute only the explicitly authorized Phase 5.48 pre-attempt slice bound to
authorization commit `63c582fc26983d369868965c9b982bd6411b5436`, control-set
commit `833db92a5b3aadf30c3dd617bea734d0d7f5b20a`, preauthorization
commit `7423b5076563486123ca32d32406550f68b12d84`, frozen source
`ef96f246b66b25bb70536341b60a5f1e64708c65`, and execution-instance
SHA-256 `3dc6dff32898768e52f9a6d5d46075b65a33a60c3759d14dbae53009134cc667`.

Reproduce the release archive and require SHA-256
`18418395eac577d8718c1e74f6601e005160d2768ea7634a35d00e4ddead9120`.
Construct a fresh staging transport solely from the 62 envelope-declared
inputs, the separately sealed envelope with SHA-256
`9d01a08530d6d059936d51e4a5dbd796cd8b3353efbd5d52cf891ee51e5b3699`,
and regular-file members of that archive. Independently freeze and compare the
complete file allowlist before and after transfer. Reject missing, extra,
duplicate, unsafe, AppleDouble, Finder, VCS, cache, backup, bytecode, link,
device, FIFO, extended-attribute, resource-fork, or PAX-metadata content.

Before staging, recapture wspr5 with the exact frozen archived capture and
validator bytes. Require raw byte identity with the 7,057-byte canonical
snapshot whose SHA-256 is
`9377d109235305f29e85134026cf9247e5d462b0bd2c8e05d9c0463162156e33`.
Require the staging path, qualification root, and pre-root journal to be
absent; the runtime and six controlled services to remain inactive; the
separate I2C Si5351 path disconnected and unused; no antenna; an unused SDR;
and recovery available. Use absolute system paths, including
`/usr/sbin/dkms` and `/usr/sbin/modinfo` where a sealed tool requires them.

Transfer only the authenticated archive and reviewed read-only verifier.
Verify the exact target path set and all declared hashes after extraction.
Run the exact archived executor in read-only pre-root mode. Only after all
checks pass, invoke the authenticated schema-5 pre-root transition exactly
once. On failure, use only journal-authorized recovery and return. On success,
validate the terminal journal, root marker, all 54 transition files, all 22
installed tools, authorized instance, attempt index, matrix policy, inactive
runtime, inactive services, absence of forbidden target files, and removal of
all transient transfer files.

Stop before lifecycle attempt 1. The five deferred rows remain deferred.
Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA
submission, Si5351 or SDR operation, antenna connection, transmission, RF,
`/dev/mem`, forced removal, general upgrade, and unreviewed persistent boot
mutation remain prohibited.
