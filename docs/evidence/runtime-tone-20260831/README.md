<!-- SPDX-License-Identifier: MIT -->

# GPIO20 runtime TONE integration, 2026-08-31

The user authorized a 20m, 10-second test on the previously confirmed isolated
path, deployment, and recovery reboots, with GPIO20 selected afterward. The
commanded frequency was 14,097,100 Hz. No analyzer measurement or GPIO4 output was
performed. This is execution and cleanup evidence, not RF qualification.

## Exact target and build

- Host: wspr5, Raspberry Pi 5, ARM64.
- Stock kernel/headers: `6.18.34+rpt-rpi-2712`, Debian
  `1:6.18.34-1+rpt1`; GCC 14.2.0. No custom kernel was introduced.
- Target kernel configuration SHA-256:
  `d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d`.
- Module version 1.1.2; existing ABI-v4 operation lease and ABI-v2 finite TONE.
- Module source for runs 6 and 7: `4cdf717`.
- Consumer SHA-256: `72dda7cad9e1df0c3e73a180eca792e980c823efb0b6e005493ff7728e5bddfe`.
- Controller SHA-256: `59b3ae00e8a504fe82109ea80f5753831ff92608043e8c206f7adadf4b92b4c8`.
- Runtime binding SHA-256: `80a80c1657fc75a3c567889e4e278fad7499adbd66270f2df7fb1b50cb666adc`.
- Application source for runs 6 and 7: `1f63344`; executable SHA-256:
  `e23a4211bd565f338611b036507e3eb31e15d101ac7d657c2fcbe2e7aeb0a3b2`.
- Later response-only repair: `9db11cd`, excluding previous-operation records
  from the asynchronous acknowledgement; final deployment is recorded separately.
- Final run 9 and installed deployment: module `6b248a5`, application `9db11cd`.
  Exact final hashes and stopped state are in [final-target.json](final-target.json).
  The last module change makes startup/duplicate cleanup respect tick ownership.

Module build used `make KERNEL_BUILD=/lib/modules/6.18.34+rpt-rpi-2712/build
RP1_RUNTIME_CONTROLLER=1`. Application build used `make -j2 release SUDO=`.
The reviewed runtime bundle installer updated all bound artifacts together.
The consumer remained loaded with `live_output=N`; existing ABI-v4 leases
authorized each operation. No new permit or arbitrary duration limit was added.

## Failed attempts retained

The JSON files preserve before/during/after snapshots and WebSocket messages.
Observation values are false=1 and true=2; the snapshot fields describe software
observations, not analyzer measurements. An accepted start is asynchronous and
does not itself prove output began.
Repository copies add an SPDX field and SHA-256 of the original capture bytes;
the original target captures remain unchanged.

1. Original installed consumer rejected DMA length 978473 as unaligned. WsprryPi
   aborted on the resulting worker exception. Both defects were repaired.
2. Aligned descriptors reached output, but DMA failed to stop. Cancellation
   incorrectly concealed the deadline as success; that classification was fixed.
3. A diagnostic run on the already non-idle channel timed out. Reboot was needed
   to clear that state; no successful execution claim is made for this run.
4. A clean-boot run stopped progressing just past the first 4096-byte block,
   leaving residue 3909732. Disabling finish-triggered request clearing repaired
   linked-block pacing.
5. A transient read-only DREQ pulse caused a startup conflict. The application
   correctly reported this failure without crashing. Configuration comparisons
   now exclude the pulse while retaining writable ownership checks.

The applicable hardware descriptions are the RP1 peripherals manual, section
3.8.1.1, and the stock provider's scatterlist/termination implementation:
[RP1 manual](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf),
[installed-era provider source](https://github.com/raspberrypi/linux/blob/b9ec35c5945bd4d48215d4c40267be140bd80ccb/drivers/dma/dw-axi-dmac/dw-axi-dmac-platform.c).
The provider revision is supporting source research, not a claim that its hash
is the target's entire kernel source identity.

## Successful execution and recovery

- Run 6: kernel execution interval 10.001809096 seconds, STOP terminal reason,
  successful bounded drain, cleanup=0. No DMA warning.
- Run 7, same boot and application: 10.001772561 seconds, natural COMPLETE,
  divider readback `0x2fc90000` matched, cleanup=0. No DMA warning.
- Both after-snapshots reported no owner, lease, live gate, or cleanup fault,
  with GPIO, clock, DMA, and stable-state observations quiescent.
- GPCLK enable and prepare counts were both zero after stopping the application.
- Run 8 also drained successfully in 10.002412627 seconds, but its Harness-derived
  client rejected a control frame before receiving the terminal response. Its
  saved `after` snapshot is therefore an early observation, not shutdown evidence.
  The kernel log and subsequent stopped-clock observation establish cleanup.
- Run 9 used a diagnostic client with ping/pong handling and the final installed
  builds. It completed naturally in 10.002182910 seconds, read back the expected
  divider, restored the firmware tick baseline, and released all ownership.
  Its start response contained no stale operation record and its terminal response
  contained the matching operation ID, COMPLETE reason and successful cleanup.
- Three recovery/validation reboots occurred: two to clear failed DMA state;
  the third tested the repaired prior-boot recovery command. The latter succeeded
  without manual journal changes, then switched back to GPIO20 and passed idle.
  Earlier journals remain preserved on the target.

The test used a transient systemd unit with a 180-second process limit and a
temporary GPIO20 RP1 configuration, HTTP disabled, and a loopback WebSocket on
port 31426. The original application INI was not overwritten. Its normal service
was already masked and lacked a separate vendor unit; it remains stopped/masked.
This does not establish normal UI/service installation. Restoring that operator
deployment is distinct from the demonstrated application/module execution path.

## Offline and adversarial assessment

The complete module `make check` passed, including UAPI, packaging/contracts,
controller fault injection, lifecycle tests, aligned-byte conservation, SPDX,
shellcheck, documentation checks, and whitespace. Companion route service,
runtime wiring, backend execution, worker exception/cleanup and bounded-response
regressions passed in a network-disabled Debian container. Target module and
application builds passed. The full unrelated application test suite was not run.

Review covered DMA address/length conservation and scatterlist lifetime, pacing
through intermediate blocks, cancellation/deadline distinction, writable versus
read-only tick state, exact artifact binding, cold-boot journal preservation,
worker exception containment, and terminal record association. Every discovered
issue above was repaired and reassessed. No new licensing provenance was imported;
original kernel changes retain dual GPL-2.0-only/MIT and independent tooling/tests
retain their existing licenses.

## Harness handoff

The Harness already has TONE, WSPR and QRSS execution paths and RP1 development
confirmation support. TONE uses the bounded WebSocket transaction; WSPR and QRSS
use their existing execution adapters. No further route-controller feature is
needed to begin those tests against this coherent deployment.

Its `bounded_tone_control.py` client currently accepts only text frames and rejects
normal ping frames. Repair ping/pong handling with offline protocol tests before
unattended campaigns. The final diagnostic client handled these frames, but the
Harness repository was not modified. WSPR and QRSS on this updated target remain
untested; successful TONE must not be counted as their qualification.
