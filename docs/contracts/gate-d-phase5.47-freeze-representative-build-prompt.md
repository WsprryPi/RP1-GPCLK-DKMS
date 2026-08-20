<!-- SPDX-License-Identifier: MIT -->

# Phase 5.47 freeze and exact representative-build prompt

Freeze `0.0.0-phase5.47` from the clean canonical device-tree repair commit
`b4fdc2933e343b0ba29de8b1c8007efe6fc7df28`. Update only active module,
packaging, release-policy, diagnostic, lifecycle, and current-test identities.
Add behavior and security notes for the narrow canonical alias resolver.
Preserve all historical Phase 5.46 release, control, authorization, staging,
execution, failure, and repair evidence byte-for-byte.

Reset active release gates to source-freeze-only state. Run the complete
archive-bound offline suite, independently inspect the entire diff, then
commit and push the exact clean freeze before producing an archive or target
claim.

From that commit, generate the Phase 5.47 release unit twice from independent
clean exports. Validate both units and require byte-for-byte equality. On
`wspr5`, require the exact hostname, AArch64 architecture, running stock
kernel, canonical header tree and hashes, compiler, inactive six-service
baseline, absent module and endpoint, no overlay, no Phase 5.47 DKMS state,
and a previously absent Phase 5.47 build-evidence directory. Require the
canonical `/proc/device-tree` alias and direct canonical root observed by the
repair audit. The separate I2C Si5351 path remains disconnected and unused,
the SDR remains unused, no antenna is connected, and recovery remains
available.

Transfer only one validated release unit and a clean Git archive of the exact
freeze commit. Build the module against the running stock-kernel headers from
that clean source export. Compile the permanent helper programs from the same
source and canonical UAPI. Capture commands, statuses, hashes, module
metadata, target identities, release-input inventory, and post-build safety
state. Independently validate every recorded identity and correct every
actionable evidence defect before handoff.

This slice is compilation-only. Do not register or install DKMS, install or
load the module, bind or unbind it, apply an overlay, alter services or boot
state, reboot, access GPIO or I2C, operate the Si5351 or SDR, enable clocks,
submit DMA, key a transmitter, connect an antenna, transmit, or produce RF.
Do not construct Phase 5.47 Gate D controls or stage lifecycle inputs.

Commit and push build evidence only after every check passes. Report the
freeze commit, deterministic archive identity, exact build result, target
identity, prohibited operations not performed, Git state, and next gate.
