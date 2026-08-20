<!-- SPDX-License-Identifier: MIT -->

# Gate D live-target snapshot contract v1

A control-set generator must not infer target state from an earlier control
set. Before a successor is frozen, one read-only capture on the named target
must produce a canonical `gate-d-live-target-snapshot` document. Its SHA-256 is
the sole target-state input to later generation.

The snapshot binds host, boot, kernel, headers, signing evidence, the complete
installed package inventory, the current administrator ledger, the terminal
recovery attestation, inactive runtime state, services, and explicit physical
safety declarations. Package paths are derived from the current ledger's
committed replacement records and then measured from the filesystem; they are
not copied from a historical envelope.

The capture tool is read-only and emits JSON to standard output. It does not
create evidence directories, journals, qualification roots, staging paths, or
system state. Physical declarations are separately authored operator input and
must state that the I2C Si5351 path is disconnected and unused, the SDR is
unused, and no antenna is connected.

An independently implemented validator must validate the snapshot structure
and compare every target-derived control field with that snapshot. It must not
import the capture tool or generator. Mixed-generation input—such as current
package paths with a stale ledger—must reject before freeze, authorization, or
target staging.

A second read-only capture immediately before authorization must be
byte-identical to the snapshot bound into the proposed control set. Any change
retires that proposed set before authorization.
