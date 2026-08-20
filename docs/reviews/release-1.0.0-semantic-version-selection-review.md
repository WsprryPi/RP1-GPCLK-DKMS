<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 semantic-version selection review

Result: **`1.0.0` selected; final artifacts not yet built**.

The module, DKMS, Debian, documentation, expected-tag, and active roadmap
contracts consistently select module version `1.0.0`, Debian revision
`1.0.0-1`, and Git tag `v1.0.0`. This is an appropriate initial stable semantic
version decision; it makes no claim about later API compatibility beyond the
current versioned UAPI contract.

The Phase 5.54 `-2` package remains the exact identity that was installed and
tested. Changing the module version changes package bytes, build identity, and
installed source paths, so that evidence was not relabeled as `1.0.0` evidence.
The active roadmap now requires committed-source artifact reproduction followed
by exact-candidate target verification.

No artifact, tag, publication, target, hardware, transmission, RF, or consumer
action occurred.
