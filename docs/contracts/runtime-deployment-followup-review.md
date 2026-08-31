<!-- SPDX-License-Identifier: MIT -->

# Runtime deployment follow-up review

This offline follow-up executed the
[deployment hardening prompt](runtime-deployment-followup-prompt.md).
The initial review found three actionable problems in the prior integration:

1. A known-loaded module could cause refusal only after creation of a pending
   deployment marker. Admission now checks module absence before that marker,
   and checks again before and after application quiescence. Failures after
   quiescence begins retain the barrier.
2. The journal writer could accept a plan larger than the recovery reader's
   32 MiB limit. Strict plan validation now enforces the same bound before any
   filesystem or service effect.
3. Bundle files were fully read before checking size, and binding metadata was
   read twice. Bounded, non-following regular-file reads and a single validated
   binding snapshot now prevent those inconsistencies. The complete binding
   schema, fixed inventory, version type and digest format are required.

The next assessment identified a weakness in the crash tests: they reused the
original in-memory plan rather than reading the persisted recovery journal. The
revised tests reconstruct the plan from saved bytes and distinguish a crash after
barrier removal from an incomplete deployment. This caught and closed a temporary
variable-shadowing serialization defect in this follow-up before commit.

The final assessment rechecked pre-effect rejection, post-quiescence barriers,
foreign-file protection, exact recovery bytes, strict schema/version handling,
symlink/non-regular rejection, metadata snapshot consistency and every existing
crash boundary. No remaining actionable finding was identified within this offline
scope. This is an in-thread assessment, not independent human or target approval.

The manager/deployment suite now has 16 passing methods. The full offline suite,
including existing controller/admin and actual C ioctl fixture checks, was rerun.
Documentation links, SPDX and whitespace checks pass. A fresh local bundle built
from the previously compiled opt-in pair passed strict payload validation; its
first-install journal was 213384 bytes. This is not an installed-host snapshot or
an approved target deployment plan. Kernel source, transmission UAPI, application
source and licensing policy are unchanged; tooling/tests/docs remain MIT.

No host installation, services, module/overlay operations, GPIO, reboot,
transmission or RF work was performed. Target signing/module resolution, service
sandbox behavior, firmware migration and clock-disabled route switching/recovery
remain unvalidated. Repository AGENTS.md requires explicit authorization for the
exact installation, service, module, overlay and clock-disabled target operations.

The next authorization must identify the target (expected wspr5, not inspected in
this follow-up), fresh boot/kernel/firmware/module inventory, exact reviewed bundle
and application commits/hashes, signing policy, neutral migration procedure and
application downtime. Review the target-specific deployment plan digest before
installation. A firmware boot edit and migration reboot need their own concrete
diff and approval. Then separately authorize GPIO4/GPIO20 clock-disabled tests with
ownership/error, clock-off and cleanup checks and explicit stopping criteria. Do
not restore the service mask or enable output as an automatic completion step.
