<!-- SPDX-License-Identifier: MIT -->

# wspr5 runtime-route source and target review

Date: 2026-08-31. Local baseline: `f242645`, draft PR #6. This supersedes the
proposed **hardware adapter assumptions** in the earlier v2 reference model;
it does not rewrite that model's historical test evidence.

[Curated target/source identities](../evidence/runtime-route-wspr5-20260831.json)
record the collector hash, observed artifact hashes, reviewed source hashes,
and explicit unknowns without publishing the full root-owned deployment record.

## Outcome and implemented changes

An actual bounded read-only Linux collector, `scripts/runtime_inventory.py`,
has been implemented, tested and run on wspr5 over stdin without installation.
It reads fixed files and runs only six fixed read-only commands. It does not
open the RP1 endpoint, invoke dtoverlay, load a module, alter a service, or write
target configuration. It reports unknowns and inconsistent boot observations
without converting them into readiness. No caller-selected paths or commands
are exposed by its CLI.

The old executor is now named `ModelEngine`, requires an explicitly model-only
backend, and uses `model_effect` rather than a purported Linux compare-and-effect
interface. Its tests remain useful for reference failure scenarios; it must not
be adapted to Linux by echoing predicted state or inventing a revision counter.
The public mutation entry point remains blocked. No placeholder write adapter
or deployment path has been added.

**The operational switching feature remains incomplete.** The blocker is now
grounded in the target's actual removal/error interface, not just absence of
the reference model's imagined atomic operation.

## Direct target observations

The read-only inventory was bracketed by matching boot ID
`28d025ed-0dcf-4a0b-b299-7819eed0ce6d`. It is a sequence of observations, not an
atomic snapshot or exclusion lock.

| Item | Observed value and limits |
| --- | --- |
| Hardware | Raspberry Pi 5 Model B Rev 1.0, aarch64 |
| Kernel | `6.18.34+rpt-rpi-2712`, Debian source package `linux 1:6.18.34-1+rpt1` |
| Kernel source | Installed package changelog identifies `c8c7494100e99ee05b11aaa4f0588a223a63d1af`; upstream `stable_20260609` resolves to the same commit |
| Compiler in `/proc/version` | GCC 14.2.0, Debian `14.2.0-19`; binutils 2.44 |
| Kernel configuration | OF_DYNAMIC, OF_OVERLAY, OF_CONFIGFS and MODULE_UNLOAD enabled; MODULE_FORCE_UNLOAD and MODULE_SIG disabled |
| Bootloader version property | `086b83e3332dfc8927c56762771d082f3077a1ae`; this does not identify every firmware component |
| Installed module package | `rp1-gpclk-dkms 1.1.1-1` |
| Installed and loaded development module | Version `1.1.2`, srcversion `293C640C590889FE2BA06EB`; installed GNU build-note bytes match the loaded module's exposed note |
| Source corroboration | Installed main, execution and dispatch source hashes equal the locally reviewed files; development manifest and manager binding name commit `c6d4da8` |
| Output observations | Immutable `live_output=N`; observed module refcount 0. Operation authorization, owner/lease, and electrical state were not queried or qualified |
| Active endpoint | One enabled GPIO20 route node beneath RP1; bound platform device `1f00174024.rp1-gpclk-dkms-gpio20` |
| Runtime-overlay configfs inventory | Empty; no runtime ownership token established |
| Boot configuration | GPIO20 selected by the owned predecessor route block; no include directive in inspected config.txt. The file has board conditionals and an `[all]` line with a trailing comment |
| Manager | Package manager preserved; systemd drop-in selects the executable under the `c6d4da8` source-development directory |
| Current adoption | Boot, config digest, module manifest, UAPI, manager hash and GPIO20 identity agree with the observed record. This is not permission to remove a firmware overlay |
| Services | wsprrypi active, enabled, User=root, Restart=on-failure; SoapyRemote inactive and disabled; manager socket active and enabled |
| Historical journals | Inspected entries report complete or rolled-back terminal status; all files preserved. This observation does not independently revalidate each old journal's entire schema |

Installed artifact hashes, exposed build-note matching and srcversion are
corroborating evidence. They do **not** establish a full hash of executing
module memory. The collector reports loaded-byte identity as not established.
The active tree does not prove which currently installed DTBO bytes firmware
used at boot. Both routes require separately verified artifact bindings before
future administration.

An offline deterministic build of the current overlay sources produced GPIO4
SHA-256 `96b157b50961ebf74915f84186494f9a0d5427faa59bf9729a8bd4c95dc5f681`,
which differs from installed GPIO4
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`.
GPIO20's current build and installed file both hash to
`b43691796628e4675f9f8cae8aef187cc670b3f7a3713cb67e352ee585c53713`.
Thus a coherent current dual-route deployment is not present. This comparison
does not authorize replacing either file or qualify either route.

The boot selection, active GPIO20 tree, empty runtime inventory and current
adoption together support a firmware-selected route. That conclusion is an
inference from those observations; an empty dtoverlay listing alone would not
establish it. The collector deliberately reports config directives as candidates,
not an implementation of Raspberry Pi's effective configuration parser.

## Exact source review

Kernel sources were read from the immutable commit identified above:

- [Module unloading](https://github.com/raspberrypi/linux/blob/c8c7494100e99ee05b11aaa4f0588a223a63d1af/kernel/module/main.c):
  `try_stop_module` atomically handles the reference transition and rejects a
  busy module unless forced. `delete_module` marks it going, invokes its exit
  callback, synchronizes async work and frees it before success. This gives a
  narrower lifetime guarantee than a preflight refcount check. It does not
  atomically include later overlay operations or attest electrical silence.
- [Configfs overlay ownership](https://github.com/raspberrypi/linux/blob/c8c7494100e99ee05b11aaa4f0588a223a63d1af/drivers/of/configfs.c):
  `cfs_overlay_release` calls `of_overlay_remove` but discards its result, then
  frees the configfs bookkeeping. The drop/release path has no error-return
  channel preserving the item for retry. Thus successful directory removal is
  not evidence of successful overlay removal. If removal fails before revert,
  the live overlay can remain after its userspace configfs handle is gone.
- [Overlay removal](https://github.com/raspberrypi/linux/blob/c8c7494100e99ee05b11aaa4f0588a223a63d1af/drivers/of/overlay.c):
  `of_overlay_remove` serializes with the OF mutex and rejects dependent
  changesets, corrupt-tree state and pre-remove vetoes. Its return value and
  retained ID distinguish failures from removal. Later notification failures
  have different semantics: overlay memory may already be freed. Checking for
  an absent endpoint after rmdir cannot recover every lost error distinction.
- [Platform notifications](https://github.com/raspberrypi/linux/blob/c8c7494100e99ee05b11aaa4f0588a223a63d1af/drivers/of/platform.c):
  dynamic creation depends on parent population state; deletion depends on
  OF_POPULATED and device references. The module's fallback device creation
  and owned-device unregister are therefore still relevant. Module unload and
  configfs removal must remain separate, observed lifecycle stages.

The module source's remove path marks dead, quiesces execution, releases DMA,
pinctrl and clock references, and releases endpoint ownership. Its owned-device
unregister brackets the node reference and clears its own population flag.
Those source properties do not prove every external consumer releases overlay
references. `execution_quiesce` also contains timeout escalation into synchronous
DMA termination and worker stop: a userspace process timeout is not a bound on
all kernel teardown or proof that a syscall has stopped.

The installed overlay tool is `raspi-utils-dt 20260626-1`. The matching official
[source descriptor](https://archive.raspberrypi.com/debian/pool/main/r/raspi-utils/raspi-utils_20260626-1.dsc)
and source archives were downloaded locally. Archive SHA-256 values match the
descriptor; its PGP signature was not independently verified, and no
bit-for-bit binary rebuild is claimed. No Debian patch files were present in
the inspected Debian archive.

In that source package, `dtmerge/dtoverlay_main.c` selects a removal position,
removes that overlay and all later overlays, and replays retained ones. It
checks rmdir, so it inherits configfs's lost-error problem. Its startup may
create working/configfs directories before dispatching a listing operation.
Consequently this investigation did not invoke even `dtoverlay -l`; it read
existing configfs directory entries directly. A future fixed-route executor
must not use broad removal/replay as its ownership mechanism.

## Decisions replacing the earlier assumptions

1. Reject whole-system atomic compare-and-effect as a real adapter contract.
   Use operation-specific preconditions, actual syscall outcomes, independently
   observed postconditions and durable failure states. Never synthesize
   success by matching the model's desired observation.
2. Do not require protection from an unrestricted root administrator. Define
   cooperative administration and exclude conflicting privileged activity
   operationally; detect foreign changes and stop. Root isolation cannot be
   supplied by an application lock or another ordinary module API.
3. Retain a crash-persistent application inhibit as an integration requirement,
   not a claim that every unload needs a new kernel lock. On this host the
   application runs as root with restart-on-failure; stopping it alone is not
   a durable policy. A reviewed inhibit must cover restart/autoload and keep
   normal transmission disabled until separately released.
4. Reject direct configfs deletion as a recoverable success/error interface on
   this kernel. A timeout, disappearance of the configfs directory, or absence
   of the endpoint does not replace the missing removal result. Recovery may
   require a separately approved reboot; never add a second route to conceal
   uncertain first-route removal.
5. Do not deploy another source manager or install a binding just to suppress
   these blockers. The current package and source-development paths remain
   unchanged. No custom kernel dependency or raw-MMIO fallback is introduced.

## Remaining implementation versus validation

The actionable implementation blocker is a supported, ownership-preserving
overlay-removal interface that exposes the kernel result and retains the
appropriate handle on retryable failure. The stock kernel exports
`of_overlay_fdt_apply` and `of_overlay_remove` to GPL-compatible modules. A
bounded module-owned route controller using those APIs is a possible next
architecture to assess; it is **not implemented or proven here**. It would need
an explicit route-neutral lifecycle, fixed authenticated overlays, module/device
lifetime review, an additive administrative contract, and coordinated
application inhibition. It must not accept arbitrary DTBOs or rewrite existing
firmware nodes. This is substantive implementation work, not a qualification
flag awaiting operator approval.

After a real result-preserving interface and the cooperative administration
contract exist, implement the concrete effect runner and its crash recovery,
then opt-in deployment and migration tooling. Real command-construction and
failure tests must accompany those effects. The existing model cannot provide
their evidence. No kernel code was changed merely to pretend those gaps closed.

Target validation is a later gate: separately authorize exact artifacts and
commands for migration to a route-neutral boot, an initial reboot if still
firmware-selected, inhibited GPIO4 binding/cleanup, GPIO4-to-GPIO20 switching,
reverse switching, and bounded safe failure recovery. Keep services inhibited
through uncertainty; retain all evidence; never force unload or automatically
reboot. No transmission or RF test belongs to that administration plan.

## Validation and adversarial assessment

The collector's tests exercise fixed argv construction, time/output/file bounds,
unknown observations, reboot during inventory, conservative config handling,
untrusted modinfo paths, compressed-module/ELF bounds and loaded-note matching.
Source review caught the unsafe broad overlay-removal and lost-error assumptions;
they were removed from the real-adapter plan rather than bypassed.

The first code assessment corrected directory-walk error suppression, unknown
build-note observations being reported as a mismatch, and missing validation of
the bracketing boot ID. It also required explicit model-only naming and admission.
The subsequent assessment must be read within this scope: passing collector and
model tests does not complete the write adapter or establish hardware safety.

The second assessment found no remaining actionable defects in the delivered
read-only collector and explicitly synthetic model. Validation completed with
`make check` using the local JSON Schema validation environment: all 35
registered Python checks, the parameterized utility check, and nine host C tests
passed. These include 10 collector test methods and 21 model test methods.
Documentation links, SPDX checks, schema validation, deterministic overlay
checks, shell checks and whitespace checks passed. Target clients were classified
but not run. No kernel-header build was performed because kernel and UAPI source
were unchanged. The closing read-only inventory observed the same boot ID and
unchanged inspected administrative configuration. Operational switching remains
incomplete for the implementation reasons above; this assessment does not close
that separate requirement.

No target services, module state, overlays, boot files, endpoint permissions,
GPIO, DMA, transmission or RF state were changed. SSH and sudo read-only access
may generate normal audit logs. No target helper was installed. New independent
code and documentation use MIT; upstream source was reviewed locally, not
vendored or relicensed. Module/UAPI/compatibility identities are unchanged.
