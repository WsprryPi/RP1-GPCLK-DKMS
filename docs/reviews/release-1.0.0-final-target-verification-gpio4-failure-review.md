<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 final target GPIO4 failure review

Result: **the final package installed successfully, but target verification
failed closed during GPIO4 overlay-identifier capture**.

The authorized final recapture was byte-identical to the preauthorization
capture. Metadata-free staging, complete outer checksum validation, the exact
16-member regular-file qualification inventory, extracted control validation,
and the final staged preflight all passed. One conventional package upgrade
installed `1.0.0-1`, built and installed the module for all four stock kernels,
excluded the custom kernel as designed, and restored an exact inactive state.

During the single GPIO4 attempt, `dtoverlay rp1-gpclk-gpio4` applied the
overlay but returned no stdout. The qualification control assumed the last
stdout line contained the numeric overlay identifier and raised `IndexError`.
Its `finally` path unloaded the attempt-loaded module but could not remove an
identifier it had not captured. A read-only overlay listing then proved that
overlay `0` was the sole active overlay and belonged to this attempt. The
authorized scoped cleanup removed only overlay `0`; subsequent verification
proved the inactive installed `1.0.0-1` baseline, empty package audit, absent
module and endpoint, and zero active overlays.

This is a qualification-control defect, not a product installation failure.
The run stopped without retrying GPIO4 and without attempting GPIO20, package
removal, or reinstall. A successor must derive the applied identifier from an
authoritative before/after overlay listing, exercise both normal and empty
stdout behavior in a fake system, rebuild the separate qualification artifact
twice, and obtain new exact-artifact authorization. The product package need
not change unless that review discovers a product defect.

No live output, clock enable or rate change, DMA submission, GPIO output, boot
change, reboot, transmission, or RF occurred.
