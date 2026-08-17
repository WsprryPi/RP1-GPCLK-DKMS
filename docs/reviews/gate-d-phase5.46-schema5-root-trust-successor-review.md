<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 schema-5 root-trust successor review

Status: PASS for the bounded offline repair. No successor was frozen or built.

The executor now declares the complete supported relationship instead of using
an incomplete conditional: instance schema 3 binds target-plan schema 4, and
instance schemas 4 and 5 bind target-plan schema 5. Unknown instance schemas
remain rejected before this mapping, and known mismatches fail closed.

The installed-executor regression now uses schema 5 for its primary instance
and schema 5 for its target plan, authenticates the complete installed Python
module graph, and reaches normal document validation. It separately proves the
legacy schema-4/schema-5 relationship remains accepted and that a
schema-5/schema-4 mismatch is rejected with the exact trust-binding failure.
All prior adversarial import and filesystem cases remain exercised.

Adversarial assessment confirmed that no frozen Phase 5.45 byte may be changed.
It also exposed a separate successor-control requirement: the frozen Phase 5.45
instance references `release/gate-d-matrix-policy-v2.json`, but that shared
policy was not included in its root transition set. The index validator also
resolves its authenticated executor identities through the qualification root,
while the frozen transition omitted the target plan's bound `scripts/` source
graph. The historical validator now obtains frozen source/tool bytes instead of
comparing them with moving successor bytes, while explicitly supplying those
referenced frozen files for offline instance validation. Phase 5.46 control
construction must bind every required policy and tool identity into the root,
or make installed-tool resolution explicit, and assert complete closure over
every root-bound reference.

The source defect fixed in this slice remains confined to the executor's
relationship lookup and the missing schema-pair regression. Phase 5.45 remains
a retired failed candidate and must not be retried.

No target connection, staging, recovery, service, DKMS, module, overlay, GPIO,
clock, DMA, I2C, Si5351, SDR, antenna, transmission, or RF operation occurred.
The next gated slice is a new Phase 5.46 freeze and representative build from
this repaired source, followed by successor-specific controls with complete
root-bound policy closure.
