<!-- SPDX-License-Identifier: MIT -->

# Gate D authorized target-preflight adversarial assessment

## Outcome

The 2026-08-15 authorized read-only preflight stopped the Gate D target run
before mutation. The `wspr5` baseline matched the recorded current kernel and
was free of the test DKMS versions, module, endpoint, route overlay, and platform
binding. Exact headers, build tools, device-tree compiler, DKMS, kmod tools, and
sudo access were present. The named `wsprrypi`, `sdrplay`, and
`SoapySDRServer` services were active and therefore require the already
authorized exact stop-and-restore transaction before module activity.

No service was stopped or changed. No file was written on the target. No DKMS
registration, build, installation, module load, binding, overlay operation,
boot change, reboot, GPIO or clock access, DMA submission, transmission, SDR,
or RF activity occurred.

## Blocking findings

1. `gate_d_lifecycle.py` generates DKMS and module commands but does not stage
   either frozen source version or install the package-owned helpers, policy
   files, and allowlisted overlay needed by those commands.
2. No reviewed operation plan applies and removes one allowlisted runtime
   overlay. Without that binding, the UAPI and unbind/rebind checkpoints cannot
   execute; adding unreviewed commands would violate the authorization dossier.
3. The coordinator does not stop and exactly restore the named conflicting
   services, and it has no reviewed stock-kernel switch/recovery transaction.
4. The deliberate build-failure, stale-manifest, corrupted-archive/DTBO, and
   busy-state injectors are not dispatched by their lifecycle plans.
5. `refuse-removal` accepts caller-supplied blocker booleans and dispatches no
   live probe or the frozen busy-state injector, so it cannot prove the required
   open and owner refusal attempts on a target.
6. `--stop-after` interrupts before the named checkpoint command. It therefore
   does not implement the matrix requirement to interrupt separately after
   every durable checkpoint, and its recovery plan has not been proven against
   the resulting real DKMS/filesystem states.
7. Final verification does not collect or seal the complete required evidence:
   scoped kernel-log delta, live safety/ownership snapshot, overlay and service
   restoration, unrelated-byte preservation, exact residue audit, and immutable
   evidence-directory state.

## Required correction gate

Implement one deterministic operation-plan contract covering target preflight,
source staging, exact service quiescence/restoration, allowlisted output-disabled
overlay lifecycle, both frozen versions, stock-kernel switching and recovery,
each bounded injector, live refusal proof, exact owned-path cleanup, and sealed
evidence. Offline tests must assert every generated command and interruption
boundary. A separate adversarial review must then reinject all failures. Only
after every required row returns to `ready` and `--require-ready` passes may the
already authorized target subset be reconsidered; any materially expanded
command or mutation envelope requires fresh authorization.

## Offline closure

The blocker-resolution slice added the machine-validated 38-attempt plan in
`release/gate-d-target-operation-plan-v1.json` and bound it by hash to the
execution instance. The plan names exact artifacts, routes, services, failure
attempts, interruption checkpoints, evidence gates, recovery deadlines, and
execution-only tool identities. `scripts/gate_d_boot.py` implements the missing
stock-kernel selector without touching the unrelated `tryboot.txt` or
historical custom images.

The first offline adversarial pass found that the initial boot selector could
leave an unjournaled staged kernel after interruption. That finding was
reinjected: state is the first mutation, before even the configuration backup,
every checkpoint
updates it, and restore accepts partial, selected, or restoring states while
refusing changed configuration, tryboot, backup, kernel, or initramfs bytes.
Deterministic tests cover success, partial recovery, unrelated tryboot
preservation, and tamper refusal. No unresolved offline finding remains.

A final pass also found that lifecycle interruption was occurring before the
named command rather than after its durable checkpoint. The coordinator now
dispatches and verifies the command first; the deterministic test proves both
DKMS add and build completed before the `after-dkms-build` interruption. This
corrected coordinator, the boot selector, plan validator, and busy injector are
separately hash-bound execution-only inputs and do not rewrite the frozen
candidate archive.
