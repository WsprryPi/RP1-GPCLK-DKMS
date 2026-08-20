<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 metadata-free staging and pre-root execution prompt

Execute only the explicitly authorized Phase 5.51 pre-attempt slice bound to
authorization commit `f25ecb5f57cec4f255861e8f790aea11e4e804eb`, control-set
commit `64baef473a04810627598015b32797e46e6e43a2`, preauthorization
commit `cd81650bd324ec3e8d608bfe2cc67252d34e4e88`, frozen source
`cc87e0cdec7195eb69de2a6606f388e23ee0799c`, and execution-instance
SHA-256 `3e3dadb4a553b2e9f083e05301a711b28d3b1e287082080d3f5437109607c532`.

Require release archive SHA-256
`253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549`.
Construct a metadata-free ustar transport solely from the 63
envelope-declared inputs, the separately sealed envelope with SHA-256
`1acccb9e8c0e8aa9bd215e088bcb761ccaf449f15208fbb23000c0c6ac4271f6`,
and the 729 regular-file members of that archive. Independently compare the
complete file allowlist before and after transfer. Reject missing, extra,
duplicate, unsafe, AppleDouble, Finder, VCS, cache, backup, bytecode, link,
device, FIFO, extended-attribute, resource-fork, or outer PAX content.

Before staging, recapture wspr5 twice with the exact frozen archived capture
bytes. Require both captures to be identical to the 7,082-byte canonical
snapshot whose SHA-256 is
`badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a`.
Require the Phase 5.51 staging path, qualification root, pre-root journal, and
attempt namespace to be absent; runtime and all six services inactive; the
separate I2C Si5351 path disconnected and unused; no antenna; an unused SDR;
and recovery available. Use absolute system paths, including `/usr/sbin/dkms`
and `/usr/sbin/modinfo`.

Verify the exact 792-file target path set, all declared hashes, zero forbidden
paths, and zero extended attributes after extraction. Run the exact
envelope-bound archived executor in read-only pre-root mode. Only after every
check passes, invoke the authenticated schema-5 pre-root transition exactly
once. On failure, use only journal-authorized recovery and return.

On success, independently validate the terminal journal, root marker, all 55
transition files, all 22 installed tools, authorized schema-6 instance,
unchanged attempt index, inactive runtime and services, absence of forbidden
or transient target files, and absence of the Phase 5.51 attempt namespace.
The exact installed permanent executor must bootstrap and validate the
schema-6 instance through its complete installed import graph.

Stop before lifecycle attempt 1. The five deferred rows remain deferred.
Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA
submission, Si5351 or SDR operation, antenna connection, transmission, RF,
`/dev/mem`, forced removal, general upgrade, and unreviewed persistent boot
mutation remain prohibited.
