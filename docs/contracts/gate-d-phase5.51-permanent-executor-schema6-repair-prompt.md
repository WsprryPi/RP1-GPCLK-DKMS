<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 permanent-executor schema-6 repair prompt

Repair only the Phase 5.50 failed-closed permanent-executor blocker recorded at
commit `a2c809a8822c218e8917ae8a5bebe5003e2ef5da`. Extend
`gate_d_outer.bootstrap_root_validator()` to accept execution-instance schema
6 and bind it to target-plan schema 5, while retaining schema 3, 4, and 5
compatibility and every existing root, marker, ownership, mode, import-graph,
tool-identity, and fail-closed check.

Strengthen the pre-freeze installed-import regression so its primary instance
is schema 6. It must copy the exact workspace permanent executor and complete
Python module graph into reconstructed installed paths, authenticate the root
marker and target plan, invoke the permanent executor's actual
`bootstrap_root_validator()` through its installed-executor selection path,
and validate an exact indexed Phase 5.50 schema-2 attempt. Preserve explicit
schema-5 and schema-4 compatibility cases and all missing, swapped, symlinked,
writable, substituted, extra-module, unbound-import, and initialization-failure
negative cases.

Run the focused regression, the complete offline suite, and a second clean
validation from an archive made from the committed repair bytes. The archive
validation must execute the same permanent-executor regression from the
extracted tree; direct `gate_d_instance` validation, monkey-patched root
validation, fake lifecycle execution, or ordinary schema validation is not a
substitute.

This is a corrective pre-freeze slice only. Do not create a source freeze,
release archive, representative build, snapshot, control set, authorization,
target transport, staging transition, or lifecycle attempt. Do not connect to
wspr5 or perform service, DKMS, module, overlay, boot, GPIO, I2C, Si5351, SDR,
clock, DMA, antenna, transmission, or RF activity.
