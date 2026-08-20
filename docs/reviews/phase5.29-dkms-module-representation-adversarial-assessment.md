<!-- SPDX-License-Identifier: MIT -->

# Phase 5.29 DKMS module-representation adversarial assessment

Status: implementation review passed; representative build still required

The review challenged path containment, filename allowlisting, ambiguity,
symlinks, non-regular files, unknown suffixes, identity verification, and
scope. The first implementation would have ignored an unknown module-like
sibling when one allowlisted representation was also present. That finding was
re-injected: the resolver now rejects every entry beginning with
`rp1_gpclk_dkms.ko` unless its complete name is one of the four allowlisted
representations. The negative test retains an otherwise valid `.ko` while
injecting each unknown suffix.

The corrected implementation selects only beneath the exact rooted DKMS
package/version/kernel/architecture module directory, requires exactly one
regular non-symlink candidate, and passes that path unchanged to the existing
version, vermagic, signer, and key-ID checks. It neither decompresses nor
copies the module. Installed-module checks remain unchanged. Tests cover all
four positive representations plus absence, ambiguity, unknown suffixes,
symlinks, and directories.

No GPIO, clock, DMA, Si5351, transmitter, SDR, antenna, module lifecycle, or RF
behavior is introduced or authorized by this implementation review.
