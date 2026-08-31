<!-- SPDX-License-Identifier: MIT -->

# ABI v4 operation-scoped live authorization

ABI v4 adds `RP1_GPCLK_IOC_ACQUIRE_V4` without changing ABI v1, v2, or v3
layouts or command identities. The new acquire request requires the exact
route, `LIVE_ELIGIBLE`, `OPERATION_LIVE_GATE`, the single
`AUTHORIZE_LIVE` flag, and a nonzero 32-byte application authorization digest.
Unknown flags, capabilities, reserved fields, zero digests, incompatible
routes, ineligible devices, or existing owners fail closed.

The digest binds application-reviewed request and plan identity; the kernel
does not interpret its contents or grant authority merely because bytes are
nonzero. Endpoint permissions, application policy, compatibility enrollment,
physical topology confirmation, and operator authorization remain separate
requirements.

A successful v4 acquire authorizes output only for its returned owner and
lease. Submission checks that exact binding. Ordinary v1 acquire retains the
immutable module-load gate behavior. Explicit release, generation-specific
release, owner close, copyout failure, provider removal, and teardown revoke
the operation-scoped gate. A later lease must present a fresh authorization.

The ABI-v3 passive snapshot reports `live_output=true` while either the legacy
load-time gate or one operation-scoped lease is active. It does not disclose
the authorization digest or lease token. Intrinsic route compatibility remains
visible while safely idle so an application can authenticate the provider
before acquiring the exact authorized operation.

The current 0.9.0 development build uses route-specific
`v0.9.0-pi5-gpio4-6.18.34-development` and
`v0.9.0-pi5-gpio20-6.18.34-development` identifiers. No predecessor evidence
transfers to changed bytes or between GPIO4 and GPIO20.
