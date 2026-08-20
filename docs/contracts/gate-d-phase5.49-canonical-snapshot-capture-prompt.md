<!-- SPDX-License-Identifier: MIT -->

# Phase 5.49 canonical live-target snapshot prompt

Before constructing Phase 5.49 controls, capture the current wspr5 predecessor
state with the reviewed read-only canonical snapshot tool. Stream the tool over
SSH without creating a target file. Require the terminal-complete Phase 5.48
administrator ledger and sealed Phase 5.48 attempt journal, measured installed
package paths, stock kernel and canonical headers, non-enforcing signing state,
inactive module, endpoint, overlay, test DKMS versions, live output, and all six
reviewed services.

Bind the existing operator physical-safety declarations: the separate I2C
Si5351 path is disconnected and unused, the SDR is unused, and no antenna is
connected. The capture must not probe or operate GPIO, I2C, Si5351, SDR, clock,
DMA, antenna, transmitter, or RF hardware.

Independently validate the exact canonical bytes. Require the current ledger,
terminal journal, package inventory, and package digest to differ from the
older Phase 5.48 predecessor snapshot wherever the completed Phase 5.48
transition changed them. Reject any attempt to combine the new ledger with an
older inventory.

This slice produces only the canonical Phase 5.49 predecessor snapshot and its
offline validation. Do not generate controls, stage target inputs, request or
consume lifecycle authorization, change services, administer DKMS or a module,
apply overlays, change boot state, enable clocks, submit DMA, transmit, or
produce RF. Commit and push only the prompt, canonical snapshot, review, and
deterministic validator.
