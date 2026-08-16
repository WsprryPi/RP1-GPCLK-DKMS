<!-- SPDX-License-Identifier: MIT -->

# Phase 5.32 authorized-execution adversarial assessment

Status: blocked safely; recovery required

The control set failed to model coexistence with permanent tools retained by
the committed Phase 5.31 qualification root. The administrator treats an
existing compiled UAPI probe as categorically unsafe instead of accepting only
an exact reviewed predecessor identity or replacing it through a sealed
transaction. This stopped installation after DKMS state was created.

The recovery contract then contradicted the administrator ledger: pre-root
recovery requires `dkmsTestVersions=false` before calling the administrator's
owned-state recovery, making the reviewed recovery unreachable for the actual
post-install failure. Ordinary green simulations did not model retained
predecessor tools plus real administrator-created DKMS residue together.

The failure and failed recovery are preserved. Manually deleting the existing
tool, directly invoking administrator recovery, or patching installed bytes
would bypass the sealed transition and is not authorized. A successor must
first provide a bounded, identity-aware predecessor-tool transition and make
ledger-backed recovery reachable when exact owned DKMS state exists. Its
offline rehearsal must start with retained predecessor permanent tools and
inject failure after DKMS installation, then prove exact recovery.

No lifecycle attempt began and output remained disabled. No loaded module,
endpoint, overlay, GPIO, clock, DMA, Si5351, transmitter, SDR, antenna,
transmission, reboot, or RF action occurred.

The later recovery-only slice invoked the envelope-declared administrator
recovery directly under separate authorization. It succeeded because the
administrator ledger, unlike the outer pre-root guard, correctly treats exact
owned DKMS state as the object of recovery. Final absence and retained-tool
identity checks passed. This restores a safe baseline but does not cure the
outer recovery reachability or predecessor-tool transition defects; both remain
Phase 5.33 blockers.
