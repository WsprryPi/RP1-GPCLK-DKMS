<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 freeze and exact representative-build prompt

Freeze `0.0.0-phase5.46` from the clean schema-5 root-trust repair commit
`f4c2fcf4b106cd03344d705528fe903a0e4d8bcb`. Update only active module,
packaging, release-policy, diagnostic, lifecycle, and current-test identities.
Add behavior and security notes for the explicit schema relationship and the
still-required complete root-reference closure. Preserve all historical Phase
5.45 release, control, authorization, staging, execution, and stop evidence
byte-for-byte.

Reset active release gates to a source-freeze-only state. Run the complete
archive-bound offline suite, independently inspect the entire diff, then commit
and push the exact clean freeze before producing any archive or target claim.

From the resulting freeze commit, generate the Phase 5.46 release unit twice
from independent clean exports. Validate both units and require byte-for-byte
equality. On `wspr5`, require the exact hostname, AArch64 architecture, running
stock kernel, canonical header tree and hashes, compiler, inactive six-service
baseline, absent module and endpoint, no overlay, no Phase 5.46 DKMS state, and
a previously absent Phase 5.46 build-evidence directory. The separate I2C
Si5351 path remains disconnected and unused, the SDR remains unused, no
antenna is connected, and recovery remains available.

Transfer only one validated release unit and a clean Git archive of the exact
freeze commit. Build the module against the running stock-kernel headers from
that clean source export. Compile the two permanent helper programs from the
same source and canonical UAPI. Capture complete commands, statuses, hashes,
module metadata, target identities, release-input inventory, and post-build
safety state. Independently validate every recorded identity and correct every
actionable evidence defect before handoff.

This slice is compilation-only. Do not register or install DKMS, install or
load the module, bind or unbind it, apply an overlay, alter services or boot
state, reboot, access GPIO or I2C, operate the Si5351 or SDR, enable clocks,
submit DMA, key a transmitter, connect an antenna, transmit, or produce RF.
Do not construct Phase 5.46 Gate D controls or stage lifecycle inputs.

Commit and push the build evidence only after all checks pass. Report the
freeze commit, deterministic archive identity, exact build result, target
identity, prohibited operations not performed, Git state, and the next gated
step.
