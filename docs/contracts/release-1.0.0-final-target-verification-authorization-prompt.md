<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 exact-candidate target-verification authorization prompt

I explicitly authorize the single bounded final-candidate target-verification
sequence on `wspr5`, bound to candidate source commit
`a20abc828ec300ad3227a34be7572f4fa28525b2`, control commit
`913adad58ca3790ac682be7b7d9de2bde6f8ec69`, preauthorization recapture
`41f45616f3521b74c61e443aeed552a6c173a5b4dc2367b3d42b8c3ba8f04089`,
Debian product package
`951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8`,
and separate qualification archive
`fa11f86c8a5f1443560d71720e44a4fa1e3d209d64542c0d416e00debc9dea5e`.

I freshly confirm that the Si5351 path is physically disconnected and that no
antenna or transmitter is connected to either GPIO4/GPCLK or GPIO20/GPCLK.

Begin with one final read-only recapture and require it to match the recorded
kernel, installed `0.0.0~phase5.54-2` package, empty `dpkg --audit`, four stock
DKMS installations, installed UAPI and both overlay identities, unloaded
module, absent endpoint, zero active or boot-selected project overlays,
inactive conflicting services, executable command paths, and the two physical
safety confirmations. Stop without mutation on any mismatch.

Only after the match, transfer the exact product and qualification artifacts
without metadata into one new user-owned staging directory. Rehash both outer
artifacts, validate the literal qualification archive inventory before
extraction, extract into that directory, run the archive-contained validator
and renderer from the extracted qualification root, and require the complete
`SHA256SUMS` check to pass. Stop and remove only the user-owned staging
directory on any failure before installation.

Execute the rendered plan once and in order:

1. Perform one conventional `dpkg --install` upgrade to the exact `1.0.0-1`
   package.
2. Prove `install ok installed`, empty package audit, four stock-kernel DKMS
   installations, exact UAPI and both installed DTBO identities, unloaded
   module, absent endpoint, and zero active or boot-selected project overlays.
3. Perform exactly one GPIO4 lifecycle using only `live_output=0`: load the
   module, prove the output gate disabled, apply only the GPIO4 runtime overlay,
   query/acquire/release through the bounded UAPI probe, remove only its
   captured overlay identifier, unload the module, and prove the inactive
   package baseline restored.
4. Repeat that same bounded output-disabled lifecycle exactly once for GPIO20,
   independently capturing and removing its overlay identifier, then prove the
   inactive package baseline restored.
5. Perform exactly one conventional package removal, prove package and DKMS
   absence plus absence of every product-owned installed path while unrelated
   overlays remain unchanged, then reinstall the same exact package once.
6. Prove the final inactive `1.0.0-1` baseline, empty package audit, four stock
   DKMS installations, exact UAPI and DTBO identities, unloaded module, absent
   endpoint, zero project overlays, inactive conflicting services, and no new
   scoped kernel warnings, errors, or failures.

On any post-install failure, preserve evidence, remove only a runtime overlay
whose identifier was captured by this sequence, unload only the module loaded
by this sequence, and use the conventional package operation necessary to
return to an inactive package-manager-consistent state. Do not improvise a new
repair path; stop and report the exact state if the bounded recovery cannot
restore consistency. Remove only user-owned staging residue after evidence is
sealed.

This authorization permits the named package upgrade/removal/reinstallation,
output-disabled module load/unload, GPIO4 and GPIO20 runtime overlay
apply/remove with safe inactive pinctrl binding, and bounded UAPI
query/acquire/release. It does not permit `live_output=1`, clock enable or rate
change, DMA submission, GPIO output, boot changes, reboot, transmission, RF,
tag creation, release publication, or consumer-repository changes. Stop after
sealing the exact-candidate verification evidence; release review, tagging, and
publication remain separate gates.
