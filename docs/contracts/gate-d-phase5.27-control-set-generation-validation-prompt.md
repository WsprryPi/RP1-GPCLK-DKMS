<!-- SPDX-License-Identifier: MIT -->

# Phase 5.27 Gate D control-set generation and independent validation prompt

## Objective

Generate a new, complete, hash-closed Gate D control set for frozen candidate
`0.0.0-phase5.27`, source commit
`bfb92725631748db3f7f7def8d331442872cab7d`, archive SHA-256
`c623a8ebf6b5dc01a6e85a17e8709c479ad349aa2a08b34a86d71a2dc2a6adbb`,
and representative module SHA-256
`0d0401ce932ca2b5020cce20e6cafbd8ee8d3133f8046ec12c8dc53a1e0541d6`.
Phase 5.26 controls and failure evidence are immutable and must not be edited,
renamed, or treated as Phase 5.27 evidence.

## Required artifacts

Create a Phase 5.27 route decision, target-operation plan, qualification-install
identity, qualification bootstrap, deterministic 38-attempt bundle and index,
execution instance, and pre-root bootstrap envelope. Bind every file and nested
reference to the exact source, archive, sidecars, canonical UAPI, representative
module, stock kernels, target staging directory, qualification root, installed
tool identities, services, rescue contract, deadlines, and authorization.

The execution instance may be ready only for the ten previously reviewed rows;
retain five environmental rows as explicitly deferred. Both GPIO4 and GPIO20
remain independent DKMS routes. The Si5351 remains a separate I2C path and is
prohibited during this lifecycle work.

## Safety and non-goals

This slice generates and validates controls offline. Do not install, register,
load, bind, unbind, or unload the module; do not activate overlays, reboot,
change services, access GPIO, enable clocks, submit DMA, operate the Si5351 or
transmitter, use SDR hardware, or produce RF. Do not tag, publish, open a PR,
or advance dependent repositories.

## Independent validation

Validate schemas and closed field sets; every embedded SHA-256 and path; the
38 unique attempts and required interruption/busy cardinalities; deterministic
regeneration; fake execution with sealed evidence, service restoration, and
output disabled; qualification-root identity; transition-file uniqueness and
completeness; release-input colocation; installed import/tool closure; ten
ready and five deferred rows; and exact authorization/prohibition language.

Adversarially mutate release inputs, duplicate roles and destinations, hashes,
paths, safety flags, authorization, route identities, source/archive/module
identities, and attempt documents. Every mutation must fail closed. Correct all
actionable findings and repeat affected checks plus the complete offline suite.

## Exit criteria

Finish only when the distinct Phase 5.27 set is deterministic, internally
closed, independently adversarially validated, and the repository is clean
after any authorized commit and push. Report exact artifact paths, counts,
hashes, checks, safety exclusions, Git commits, push result, and the next gated
step. This prompt does not authorize target lifecycle execution itself.
