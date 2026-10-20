<!-- SPDX-License-Identifier: MIT -->

# Frequently asked questions

## Do I install this separately from WsprryPi?

Normally, no. WsprryPi installs and validates RP1 support on identified Pi 5-family
systems. Use [managed installation](installation.md) to preserve the ownership
and recovery information needed for later maintenance.

## Why is there no execution device after installation?

Fresh setup is route-neutral. `/dev/rp1-gpclk` normally appears after you select
GPIO4 or GPIO20 through WsprryPi. Package installation, neutral activation and
route selection are separate steps.

## Does selecting a route start transmitting?

No. Selection establishes the managed path. WsprryPi separately checks the
requested operation, ownership and readiness before submitting output.

## Can I use GPIO4 and GPIO20 at the same time?

No. Only one managed route can be active. They share GPCLK0 and have separate
wiring, overlay identities and qualification. Use the route that matches the
physical connection.

## Does switching require a reboot?

The WsprryPi-managed runtime workflow switches in the current boot. An older
boot-configured profile follows a different reboot/reconciliation procedure.
Do not mix profiles to work around a failure.

## Does a successful DKMS build prove my transmitter works?

It proves build compatibility for the identified headers and toolchain.
Runtime state, cleanup, frequency accuracy, timing and RF suitability require
their own checks. Consult the WsprryPi band/mode limits for your application.

## Does removing a route uninstall the software?

No. It returns the controller to neutral administration and removes the
transmission endpoint while retaining installed software. Successful normal
removal can restore WsprryPi online and idle. Recovery deliberately retains
application inhibition.

## Can I fix a refusal by deleting the journal or forcing a module load?

No. Those records are needed to establish ownership and safe recovery.
Preserve the failure and follow [maintenance and recovery](maintenance.md).

## Where are the developer documents?

Technical contracts, API details, builds, packaging and maintainer procedures
are in the repository's
[engineering directory](https://github.com/WsprryPi/RP1-GPCLK-DKMS/tree/devel/engineering).
They are kept separately from this operator handbook.
