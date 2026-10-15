<!-- SPDX-License-Identifier: MIT -->

# Package transitions and recovery

The maintained [lifecycle matrix](../../release/package-lifecycle-matrix-v1.json)
defines supported states and results. It separates real Debian/DKMS operations,
controlled command failures and offline ownership fixtures. It is a test contract,
not a target or application qualification record.

## Identities and ownership

The authoritative lifecycle predecessor is commit
`a1cb772107ba46f626b67af0b83a45c7b54ede78`, tree
`a53c4e859f6d9a2b2d7d30f3afdcd2c2c076cced`, version `0.9.0-1`.
The [predecessor record](../../release/lifecycle-predecessor-v1.json) binds its
version, both UAPIs, compatibility identities and rendering rule. This is
unpublished historical source, not a previously published release. Its package
builds the ordinary consumer only; its runtime controller was a separate
development profile. The `1.0.0-1` candidate owns both interlocked modules in
one DKMS instance. Equal consumer UAPI bytes do not establish package or runtime
migration compatibility.

The test predecessor builder changes only Debian archive compression. Its
transformation inventory records the original and rendered rules hashes and
exact appended bytes. Runtime sources, old maintainer scripts, module names,
UAPIs and compatibility identities remain unchanged. No tag or release is made.

The current package owns its complete dpkg-listed data: versioned `/usr/src`
closure, inactive `/usr/lib/rp1-gpclk-dkms/overlays`, route executors under
`/usr/sbin` and `/usr/libexec`, versioned schema under `/usr/share`, documentation
and inactive systemd unit fragments. Native DKMS owns generated source links,
kernel links, build caches and the two modules in each kernel's `updates/dkms`.
Their ownership must agree with the exact package source. Orphan kernel links,
unexpected cache entries, changed cached source copies and unsafe cache types or
ownership are refused before native DKMS can recursively remove them. Missing installed
modules may be rebuilt; changed bytes, changed modes, duplicate compressed
artifacts, unlisted descendants and foreign registrations are refused.

The package creates the route group if absent and deliberately retains it on
removal and purge: an administrator may have enrolled other accounts. It creates
no runtime/development/application ownership record. Signing keys, certificates,
trust enrollment, DKMS-global configuration, boot configuration, foreign overlay
files, unrelated DKMS instances and application state remain outside package
ownership. Runtime state, source-development installations, manager drop-ins and
WsprryPi's default `/var/lib/wsprrypi/rp1-gpclk-dkms-installation.json` record block
replacement/removal until their owning workflow retires them. A nonstandard
application record path must also be checked by its owning orchestrator; the
package does not search arbitrary application files or infer their ownership.

## Preflight before the package manager

Verify the exact [candidate assets](release-candidate.md) and retain the previous
package before any change. From the incoming reviewed source, run the read-only
guard **before** invoking dpkg or APT:

```sh
sudo python3 -I /absolute/reviewed/source/scripts/package_preflight.py unpack
sudo dpkg -i /absolute/candidate/rp1-gpclk-dkms_1.0.0-1_all.deb
```

The guard emits `rp1-gpclk-package-preflight-v1` JSON, exits 0 for `permitted`,
and exits 1 for `refused`, retaining the underlying diagnostic. It does not open
either endpoint. The incoming preinst embeds those exact guard bytes and runs
Python in isolated mode. It does not trust an older installed helper. Configure and removal repeat the
appropriate checks before native DKMS effects.

Debian invokes the outgoing prerm before the incoming preinst. Consequently a
new package cannot prevent an old script's earlier effects. Direct `0.9.0` to
`1.0.0` replacement is unsupported and refused; do not bypass the external
preflight by running dpkg first. The approved path is owning runtime/development
cleanup, owning predecessor removal, then a clean successor installation.
The old scripts copy inactive overlays into `/boot` and contain debhelper
systemd integration. Their cleanup has historical boot/service effects and needs
its own authorization on an actual host. It is not covered by the current
package's passive guarantees. Never delete their evidence to admit the successor.

The same rule applies to downgrade: never submit a predecessor archive over an
installed successor. Version ordering is not rollback. The predecessor preinst
also refuses an in-place downgrade, but that check is later than the successor
prerm. Verify successor absence before submitting the retained old archive.

## Repeat, kernels, compression and signing

Exact repeated dpkg installation and APT reinstall replace the attributable
same-version DKMS instance and rebuild all eligible installed header trees.
They do not promise a build-free no-op. Dpkg's database lock refuses a concurrent
same-version request; independent privileged DKMS work must be excluded by its
owning orchestrator. A native `dkms install` or `autoinstall`
for an already installed exact kernel may be a no-op. Guard and audit those
operations; native DKMS registration alone does not prove installed-file identity.

For a separately approved kernel addition or native DKMS operation:

```sh
sudo python3 -I /usr/libexec/rp1-gpclk-dkms/package_preflight.py configure
sudo dkms autoinstall -k EXACT_KERNEL_RELEASE
sudo python3 -I /usr/libexec/rp1-gpclk-dkms/package_preflight.py configure
dkms status -m rp1-gpclk-dkms
```

Every eligible installed kernel must have usable headers. A missing configuration
refuses mutation. Excluded kernels remain outside the build filter and acquire
no qualification. A non-running kernel can be built/installed without loading.
Native removal for one kernel retains the others; package removal retires the
named package version across all kernels. Kernel hooks and privileged DKMS
commands are distribution-owned entry points: their orchestration must retain
the same preflight and post-operation audit. Changing global configuration or
running them outside this procedure invalidates the passive-state assumptions;
the package does not isolate arbitrary root activity.

Native installed `.ko`, `.ko.gz`, `.ko.xz` and `.ko.zst` are separate file
identities when the installed libkmod supports their compression. A `-ZLIB`
libkmod cannot inspect gzip modules: the guard refuses that state before native
DKMS effects. Unsupported bzip2 lifecycle is likewise refused. Record installed bytes and decompressed ELF hashes, version,
vermagic, signature and controller interlock for every kernel. Never conflate a
signed cache with another installed file or accept two suffixes for one module.
The bounded ELF decoder also recognizes `.ko.bz2` for identity inspection;
native creation/removal of that format is not claimed. Compression/signing fixture variants do not qualify
a kernel's signature enforcement or certificate trust.

Signing checks use DKMS's effective `include/config/auto.conf`, falling back to
`.config`. For signing-capable Debian/Raspberry Pi OS headers, a secure existing
administrator key/certificate and the canonical target signing command are
required. Dynamic framework configuration, unreviewed compression arguments,
module overrides and non-passive hooks are refused, including before removal.
Other signing distributions/mechanisms require a separate review. See
[signing](signing.md). No package operation generates a key or enrolls trust.

## Failure, removal, purge and rollback

Retain dpkg's exact state, DKMS status, failing command/stage/exit, full bounded
log and per-kernel module identities outside the checkout. After repairing only
the proven prerequisite, retry configuration:

```sh
sudo dpkg --configure rp1-gpclk-dkms
```

A missing payload file needs reinstall from the verified exact archive. Changed
or foreign files require ownership review; a retry cannot overwrite them. A
DKMS add/build/install/depmod failure leaves an attributable native prefix.
Retry removes/rebuilds that named version without duplicating registrations.
For signing-capable header configurations, the package verifies each installed
PKCS#7 signature cryptographically against only the selected public certificate
and checks that certificate's validity period. Native DKMS signing warnings do
not establish success: missing, corrupt or wrong-certificate signatures refuse
configuration. This never reads private key bytes or establishes kernel trust.

The package explicitly checks the installed module set and runs `depmod` after
native DKMS configure/removal. Its `rp1-gpclk-package-indices-v1` result preserves
the command, stage, underlying exit status, signature results and diagnostic; it does not trust
DKMS's `do_depmod` success message, which can mask an index-command failure.
If removal fails, repair its prerequisite and repeat removal. Never force-remove
an unknown registration or clear a runtime journal to make recovery succeed.

After owning runtime recovery and verified module/endpoint absence:

```sh
sudo python3 -I /usr/libexec/rp1-gpclk-dkms/package_preflight.py remove
sudo dpkg --remove rp1-gpclk-dkms
sudo dpkg --purge rp1-gpclk-dkms
```

Remove and purge delete attributable package data and native DKMS artifacts;
there is no package-owned active configuration or postrm cleanup. Administrator
keys, trust, shared configuration, unrelated modules and the route group remain.
Missing files may permit finishing interrupted removal. Modified present files
are preserved through refusal. Reinstall is a clean installation after removal.

Rollback is explicitly remove/reinstall, using the retained exact predecessor
archive and its manifest. First recover/remove any successor runtime, remove or
purge the inactive failed successor, verify its DKMS/source/modules absent, then
install the retained predecessor through its owning policy. This restores the
predecessor's package/module profile across installed kernels; it does not
restore runtime-controller sessions, routes, WsprryPi ownership/configuration,
services, a transmission or qualification. A failed predecessor configure is
retried with that exact package's own `dpkg --configure` path. Legacy effects
remain separately scoped, including during rollback.

## Disposable integration harness

Use ARM64 Linux/Docker. The [image recipe](../../tools/package-lifecycle.Containerfile)
pins its base, Raspberry Pi archive key and representative header versions.
APT tools may receive distribution updates at image construction; retain the
immutable image ID and recorded tool versions. Package tests run without a
network. They require no host boot/module/service/device mounts and no module,
reboot or hardware capabilities. Only filesystem ownership and APT user-switch
capabilities are retained. Each scenario is removed with its container; results
and logs stay in the new external output directory. Its mode is `0700`;
individual scenario bind-mount directories use `0777` beneath it so both users
can record results without `CAP_DAC_OVERRIDE`.

```sh
docker build -t rp1-package-lifecycle -f tools/package-lifecycle.Containerfile .
./scripts/build-lifecycle-predecessor \
  --source-commit a1cb772107ba46f626b67af0b83a45c7b54ede78 \
  --output /absolute/new/predecessor
python3 tools/run-package-lifecycle.py --image rp1-package-lifecycle \
  --candidate /absolute/verified/candidate \
  --predecessor /absolute/new/predecessor --output /absolute/new/results
```

The predecessor builder runs in the provisioned Linux build environment, not on
macOS. Fetch the exact selected Git history before an offline predecessor build.
Use `--scenario` for a focused rerun. The harness records distribution,
architecture, package manager, DKMS/compiler/compression tools, header configs,
candidate/predecessor digests and every before/after transition. Legacy service
attempts are separately logged and interlocked; candidate service/module-loader
attempts fail the test. Native DKMS is real; command faults and signing/compression
header variants are explicitly controlled test inputs. Actual service-manager,
signing trust, target binding, GPIO, WsprryPi and RF validation remain separate.
Item 16 accepts the exact final candidate against then-current WsprryPi `devel`
before freeze or publication.
