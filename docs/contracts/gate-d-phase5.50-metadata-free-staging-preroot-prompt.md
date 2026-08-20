<!-- SPDX-License-Identifier: MIT -->

# Phase 5.50 metadata-free staging and pre-root execution prompt

Execute only the explicitly authorized Phase 5.50 pre-attempt slice bound to
authorization commit `31cff85a746655eeac3a6e23b375a2ceacae8539`, control-set
commit `8e908928642bf3a4052f13cfb087c77a9bcbc7f8`, preauthorization
commit `dbc983e275ca6250c93d67d6dc3639f32ad3dff1`, frozen source
`c24160517b10900bf61243d4988f38247eeed58e`, and execution-instance
SHA-256 `90291e87686ef9771ff7ced3390465852371fdcc19775915ec90436063e65ac8`.

Require release archive SHA-256
`ef989bf79faa5c30ddaf8ac5651d75b1755ba2fa385680692183e6145b2927c2`.
Construct a metadata-free staging transport solely from the 63
envelope-declared inputs, the separately sealed envelope with SHA-256
`f5b10feaf56524e8251386b3e6c65f13bb2616cc43e3b4a4ec08e9cc42b7e435`,
and regular-file members of that archive. Independently compare the complete
file allowlist before and after transfer. Reject missing, extra, duplicate,
unsafe, AppleDouble, Finder, VCS, cache, backup, bytecode, link, device, FIFO,
extended-attribute, resource-fork, or PAX-metadata content.

Before staging, recapture wspr5 twice with the exact frozen archived capture
and validator bytes. Require both captures to be identical to the 7,082-byte
canonical snapshot whose SHA-256 is
`3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5`.
Require the staging path, qualification root, pre-root journal, and Phase 5.50
attempt namespace to be absent; the runtime and six controlled services to
remain inactive; the separate I2C Si5351 path disconnected and unused; no
antenna; an unused SDR; and recovery available. Use absolute system paths,
including `/usr/sbin/dkms` and `/usr/sbin/modinfo`.

Verify the exact target path set and all declared hashes after extraction. Run
the exact archived executor in read-only pre-root mode. Only after all checks
pass, invoke the authenticated schema-5 pre-root transition exactly once. On
failure, use only journal-authorized recovery and return. On success, validate
the terminal journal, root marker, every transition file, every installed tool,
authorized schema-6 instance, attempt index, matrix policy, inactive runtime,
inactive services, absence of forbidden target files, and removal of all
transient transfer files. The installed permanent executor itself must
successfully bootstrap and validate the exact schema-6 instance; a standalone
module validation is not a substitute.

Stop before lifecycle attempt 1. The five deferred rows remain deferred.
Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA
submission, Si5351 or SDR operation, antenna connection, transmission, RF,
`/dev/mem`, forced removal, general upgrade, and unreviewed persistent boot
mutation remain prohibited.
