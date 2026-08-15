<!-- SPDX-License-Identifier: MIT -->

# Phase 5.5 permissions and enrollment adversarial assessment

## Scope and evidence class

This review challenges only the offline Phase 5.5 contract, pure evaluator,
administrator record writers, packaging inventory, documentation, and tests.
No target, device node, DKMS state, module, overlay, GPIO, clock, DMA,
transmission, or RF was operated.

## Findings and reinjection

The first pass found that a boolean enrollment could survive a relevant
identity change, that Qualified status could be confused with enrollment, and
that active ownership had been incorrectly made dependent on live eligibility.
The execution prompt now enumerates the full invalidation identity, defines
Experimental enrollment as false/not-required for Qualified identities, and
allows a single output-disabled administrative owner without granting output.

The second pass found that permissions tests covered mode but not owner, group,
or character-device type, and that revocation could be modeled as deletion
without durable attribution. Tests now vary all four device-node assertions;
revocation atomically records who revoked the acceptance and when.

The final pass found no remaining objective issue. Exact acknowledgement and
UID 0 are required; records are atomic root-owned `0600` files; all identity
fields are equality checked; route and normal operator authorization remain
mandatory; installation never creates enrollment; and the implementation has
no udev, ACL, group, setuid, custom-kernel, fallback, hardware, or RF path.

## Claim boundary

This is deterministic offline policy evidence. It does not prove privileged
installation ownership, runtime device-node state, target identity discovery,
WsprryPi authorization integration, or live output. Those remain later gates.
