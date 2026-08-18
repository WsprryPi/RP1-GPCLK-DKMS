<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 metadata-free staging and pre-root execution prompt

Execute only the explicitly authorized Phase 5.52 pre-attempt slice bound to
authorization commit `8e8cdbe5d573d9c1744003c173c47463060d7f31`, control-set
commit `477d0b0c62b70a56a6ca61e9b3b56114461db2e5`, preauthorization
commit `38861a81155242caac79dcecc3cfcc722843d0c2`, frozen source
`f710554c4697d75210cbd33c9eea13474d60557a`, and execution-instance
SHA-256 `8f53fa6c41153965d49f11a4da7b139c3aa0e17cd1e9a2a77f8157c21cf43bd2`.

Require release archive SHA-256
`0c67dee49a26bf5ab103d04bcf493bba8ae373a9f45b87e5704f52ede96bce01`.
Construct a metadata-free ustar solely from the 63 envelope-declared inputs,
the separately sealed envelope with SHA-256
`8ae40ffc6f85ec0e34119aaa1cb08a221e9d94b3f08993caa33c4bd394a8ecf8`,
and the 766 regular-file archive members. Reject missing, extra, duplicate,
unsafe, metadata, link, or special content and compare the complete target
path and hash allowlist after extraction.

Before staging, recapture wspr5 twice with the frozen capture bytes. Require
both captures to equal the 7,083-byte canonical snapshot with SHA-256
`449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f`.
Require the staging path, qualification root, pre-root journal, and attempt
namespace absent; runtime and all six services inactive; Si5351 disconnected
and unused; SDR unused; antenna disconnected; and recovery available.

Verify the exact 829-file target set, hashes, zero forbidden paths, and zero
extended attributes. Run the exact envelope-bound archived executor read-only,
then invoke the authenticated schema-5 pre-root transition exactly once. On
success, independently verify the terminal journal, root marker, all 55
transition files, all 22 installed tools, authorized schema-6 instance,
unchanged attempt index, inactive runtime and services, removed transient
transport, and absent attempt namespace. Validate schema 6 through the exact
installed permanent executor and its installed import graph.

Stop before lifecycle attempt 1. The five deferred rows remain deferred.
Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA,
Si5351 or SDR operation, antenna connection, transmission, RF, `/dev/mem`,
forced removal, general upgrade, and unreviewed boot mutation are prohibited.
