<!-- SPDX-License-Identifier: MIT -->

# Module signing and key enrollment

Use an administrator-controlled private key and X.509 certificate outside the
source, archive, release, and evidence directories. Restrict private-key access,
record only the public certificate fingerprint, and use the running kernel's
`scripts/sign-file` after each DKMS build. Verify the installed module's signer,
signature algorithm, hash algorithm, vermagic, release version, and file hash
before loading it.

Enrollment is platform and policy specific. Inspect Secure Boot and kernel
signature enforcement first; enroll only the intended public certificate using
the distribution's documented MOK or firmware workflow. Reboot and key
enrollment are separate administrator actions and are never automatic. A
signature proves provenance and load eligibility, not compatibility or safety.

Rotation installs and verifies a newly enrolled public certificate before
retiring the prior certificate. Retain any key needed to rebuild older installed
kernels until those modules are removed. Uninstalling this package never
deletes private keys, public certificates, MOK entries, or keys shared with
another module. Missing, wrong, expired, revoked, or unenrolled signing identity
leaves the module unavailable; never weaken enforcement to obtain a load.
