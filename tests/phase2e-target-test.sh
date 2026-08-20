#!/bin/bash
# SPDX-License-Identifier: MIT
set -Eeuo pipefail

if [[ $EUID -ne 0 ]]; then
	echo "run as root" >&2
	exit 2
fi
if [[ $# -ne 2 ]]; then
	echo "usage: $0 SOURCE_DIR EVIDENCE_DIR" >&2
	exit 2
fi

source_dir=$(realpath "$1")
[[ ! -e $2 ]] || { echo "evidence directory already exists" >&2; exit 2; }
evidence_dir=$(realpath -m "$2")
kernel_release=$(uname -r)
kernel_build="/usr/src/linux-headers-$kernel_release"
kernel_common="/usr/src/linux-headers-${kernel_release%+rpt-rpi-2712}+rpt-common-rpi"
dt_include="$kernel_common/include"
common_package="linux-headers-${kernel_release%+rpt-rpi-2712}+rpt-common-rpi"
module_name=rp1_gpclk_dkms
driver_dir=/sys/bus/platform/drivers/rp1-gpclk-dkms
installed_module="/lib/modules/$kernel_release/updates/dkms/$module_name.ko"
work_dir=$(mktemp -d /tmp/rp1-gpclk-phase2e.XXXXXX)
overlay_dir="$work_dir/overlays"
log_file="$evidence_dir/target-run.log"
start_iso=$(date --iso-8601=seconds)
declare -a applied_overlays=()
holder=
manifest_list=

mkdir -p "$evidence_dir" "$overlay_dir"
dmesg >"$work_dir/dmesg-baseline.txt"
dmesg --level=emerg,alert,crit,err,warn >"$work_dir/dmesg-warning-baseline.txt"
exec 3>&1 4>&2
exec > >(tee "$log_file") 2>&1
log_tee_pid=$!

step()
{
	printf '\n[%s] STEP %s\n' "$(date --iso-8601=ns)" "$*"
}

record_command()
{
	printf '[%s] COMMAND ' "$(date --iso-8601=ns)"
	printf '%q ' "$@"
	printf '\n'
	set +e
	timeout --signal=TERM --kill-after=5s 180s "$@"
	local status=$?
	set -e
	printf '[%s] STATUS %d\n' "$(date --iso-8601=ns)" "$status"
	return "$status"
}

expect_failure()
{
	local label=$1
	shift
	printf '[%s] EXPECTED_FAILURE_COMMAND %s ' "$(date --iso-8601=ns)" "$label"
	printf '%q ' "$@"
	printf '\n'
	set +e
	timeout --signal=TERM --kill-after=5s 180s "$@"
	local status=$?
	set -e
	printf '[%s] EXPECTED_FAILURE_STATUS %s %d\n' \
		"$(date --iso-8601=ns)" "$label" "$status"
	[[ $status -ne 0 && $status -ne 124 && $status -ne 125 && $status -ne 137 ]]
}

assert_safe()
{
	local label=$1 expected_protect=$2 pin clock_prepare clock_enable clock_protect
	pin=$(pinctrl get 4)
	clock_prepare=$(cat /sys/kernel/debug/clk/clk_gp0/clk_prepare_count)
	clock_enable=$(cat /sys/kernel/debug/clk/clk_gp0/clk_enable_count)
	clock_protect=$(cat /sys/kernel/debug/clk/clk_gp0/clk_protect_count)
	printf '[%s] SAFE %s pin=%q prepare=%s enable=%s protect=%s expected_protect=%s\n' \
		"$(date --iso-8601=ns)" "$label" "$pin" "$clock_prepare" "$clock_enable" \
		"$clock_protect" "$expected_protect"
	[[ $pin == *"GPIO4 = none"* || $pin == *"GPIO4 = input"* ]]
	[[ $pin != *"gpclk"* && $clock_prepare == 0 && $clock_enable == 0 && \
		$clock_protect == "$expected_protect" ]]
}

assert_absent()
{
	local label=$1 overlays module_loaded device_present installed_present clients
	overlays=$(dtoverlay -l)
	module_loaded=0
	device_present=0
	installed_present=0
	lsmod | grep -Eq '^rp1_gpclk_dkms\b' && module_loaded=1
	[[ -e /dev/rp1-gpclk ]] && device_present=1
	[[ -e $installed_module ]] && installed_present=1
	clients=$(pgrep -f "$work_dir/phase2e_uapi_client" || true)
	printf '[%s] ABSENT %s overlays=%q module=%d device=%d installed=%d clients=%q\n' \
		"$(date --iso-8601=ns)" "$label" "$overlays" "$module_loaded" \
		"$device_present" "$installed_present" "$clients"
	[[ $overlays == 'No overlays loaded' && $module_loaded -eq 0 && \
		$device_present -eq 0 && $installed_present -eq 0 && -z $clients ]]
}

driver_write()
{
	local value=$1 operation=$2
	# Expansion occurs in the bounded child shell.
	# shellcheck disable=SC2016
	record_command sh -c 'printf %s "$1" >"$2"' sh "$value" "$driver_dir/$operation"
}

bound_devices()
{
	find "$driver_dir" -mindepth 1 -maxdepth 1 -type l -printf '%f\n' 2>/dev/null |
		grep -v '^module$' || true
}

only_bound_device()
{
	local devices
	devices=$(bound_devices)
	[[ $(printf '%s\n' "$devices" | sed '/^$/d' | wc -l) -eq 1 ]]
	printf '%s\n' "$devices"
}

apply_overlay()
{
	local name=$1
	applied_overlays+=("$name")
	record_command dtoverlay -d "$overlay_dir" "$name"
}

remove_overlay()
{
	local name=$1
	record_command dtoverlay -r "$name"
	local index
	for index in "${!applied_overlays[@]}"; do
		if [[ ${applied_overlays[$index]} == "$name" ]]; then
			unset 'applied_overlays[index]'
		fi
	done
}

cleanup()
{
	local status=$? index name cleanup_failed=0
	set +e
	if [[ -n $holder ]] && kill -0 "$holder" 2>/dev/null; then
		kill -TERM "$holder" 2>/dev/null || cleanup_failed=1
		timeout 5s tail --pid="$holder" -f /dev/null || true
		kill -KILL "$holder" 2>/dev/null || true
		wait "$holder" 2>/dev/null || true
	fi
	for ((index=${#applied_overlays[@]}-1; index>=0; index--)); do
		name=${applied_overlays[$index]:-}
		[[ -z $name ]] || timeout 30s dtoverlay -r "$name" || cleanup_failed=1
	done
	if lsmod | grep -Eq '^rp1_gpclk_dkms\b'; then
		timeout 30s rmmod "$module_name" || cleanup_failed=1
	fi
	if [[ -f $installed_module ]]; then
		rm -f "$installed_module" || cleanup_failed=1
		timeout 30s depmod -a "$kernel_release" || cleanup_failed=1
	fi
	rm -rf "$work_dir" || cleanup_failed=1
	if [[ -n $manifest_list ]]; then
		rm -f "$manifest_list" || cleanup_failed=1
	fi
	printf '[%s] CLEANUP status=%d\n' "$(date --iso-8601=ns)" "$status"
	assert_safe final-cleanup 0 || cleanup_failed=1
	assert_absent final-cleanup || cleanup_failed=1
	if [[ $cleanup_failed -ne 0 ]]; then status=1; fi
	trap - EXIT HUP INT TERM
	exit "$status"
}
trap cleanup EXIT HUP INT TERM

step "exact target and baseline"
[[ $(hostname) == wspr5 ]]
grep -aFq 'Raspberry Pi 5 Model B Rev 1.0' /proc/device-tree/model
[[ -d $kernel_build ]]
[[ -f $dt_include/dt-bindings/clock/rp1.h ]]
[[ -f $dt_include/dt-bindings/mfd/rp1.h ]]
[[ $(dpkg-query -S "$dt_include/dt-bindings/clock/rp1.h") == \
	"$common_package: $dt_include/dt-bindings/clock/rp1.h" ]]
[[ $(dpkg-query -S "$dt_include/dt-bindings/mfd/rp1.h") == \
	"$common_package: $dt_include/dt-bindings/mfd/rp1.h" ]]
[[ ! -e $installed_module ]]
if lsmod | grep -Eq '^rp1_gpclk_dkms\b'; then
	echo "module was already loaded" >&2
	exit 1
fi
[[ $(dtoverlay -l) == 'No overlays loaded' ]]
assert_safe baseline 0
{
	echo "start=$start_iso"
	echo "hostname=$(hostname)"
	echo "kernel=$kernel_release"
	echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
	echo "model=$(tr -d '\000' </proc/device-tree/model)"
	echo "compatible=$(tr '\000' ',' </proc/device-tree/compatible)"
	dpkg-query -W -f='header_package=${Package} ${Version}\n' "linux-headers-$kernel_release"
	dpkg-query -S "$dt_include/dt-bindings/clock/rp1.h" \
		"$dt_include/dt-bindings/mfd/rp1.h"
	echo "compiler=$(gcc --version | head -1)"
		echo "module_sig=$(grep -E '^CONFIG_MODULE_SIG(=|_)' "$kernel_build/.config" || echo unset)"
	vcgencmd version 2>/dev/null || true
	sha256sum /sys/firmware/fdt 2>/dev/null || true
	cat /sys/kernel/debug/clk/clk_gp0/clk_rate
	cat /sys/kernel/debug/clk/clk_gp0/clk_parent
	cat /sys/kernel/debug/clk/clk_gp0/clk_protect_count
} | tee "$evidence_dir/identity.txt"
find "$source_dir" -type f -not -path '*/.git/*' -print0 | sort -z |
	xargs -0 sha256sum >"$evidence_dir/source-tree-sha256.txt"

step "source boundary, build, and overlays"
record_command "$source_dir/tests/run-offline-checks.sh"
record_command make -C "$source_dir" KERNEL_BUILD="$kernel_build" clean
record_command make -C "$source_dir" KERNEL_BUILD="$kernel_build" W=1 KCFLAGS=-Werror
for dts in "$source_dir/overlays/rp1-gpclk-gpio4.dts" "$source_dir"/overlays/fixtures/*.dts; do
	name=$(basename "$dts" .dts)
	cpp -nostdinc -I "$dt_include" -undef -x assembler-with-cpp "$dts" >"$work_dir/$name.pp.dts"
	record_command dtc -@ -I dts -O dtb -o "$overlay_dir/$name.dtbo" "$work_dir/$name.pp.dts"
done
record_command python3 "$source_dir/tests/check_built_module.py" \
	"$source_dir/$module_name.ko" --kernel-release "$kernel_release"
record_command cc -std=c11 -Wall -Wextra -Werror \
	-I"$source_dir/include/uapi" "$source_dir/tests/phase2e_uapi_client.c" \
	-o "$work_dir/phase2e_uapi_client"
sha256sum "$source_dir/$module_name.ko" "$overlay_dir"/*.dtbo | tee "$evidence_dir/artifact-sha256.txt"
modinfo "$source_dir/$module_name.ko" | tee "$evidence_dir/module-unsigned.txt"

step "local signing behavior and installed artifact"
if grep -q '^CONFIG_MODULE_SIG=y' "$kernel_build/.config"; then
	echo "exact target unexpectedly enables CONFIG_MODULE_SIG" >&2
	exit 1
fi
openssl req -new -x509 -newkey rsa:2048 -nodes -days 1 -subj /CN=RP1-GPCLK-Phase2E/ \
	-keyout "$work_dir/signing-key.pem" -outform DER -out "$work_dir/signing-cert.der"
cp "$source_dir/$module_name.ko" "$work_dir/$module_name.ko"
record_command "$kernel_build/scripts/sign-file" sha256 "$work_dir/signing-key.pem" \
	"$work_dir/signing-cert.der" "$work_dir/$module_name.ko"
sha256sum "$work_dir/$module_name.ko" | tee "$evidence_dir/tested-module-sha256.txt"
modinfo "$work_dir/$module_name.ko" | tee "$evidence_dir/module-signed.txt"
grep -q '^signer:.*RP1-GPCLK-Phase2E' "$evidence_dir/module-signed.txt"
record_command install -D -m 0644 "$work_dir/$module_name.ko" "$installed_module"
record_command depmod -a "$kernel_release"
[[ $(modinfo -n "$module_name") == "$installed_module" ]]
cmp "$work_dir/$module_name.ko" "$installed_module"
sha256sum "$installed_module" >>"$evidence_dir/tested-module-sha256.txt"
record_command modprobe "$module_name"
[[ $(cat "/sys/module/$module_name/version") == 0.0.0-phase2e ]]
assert_safe signed-load 0
record_command rmmod "$module_name"
cp "$work_dir/$module_name.ko" "$work_dir/malformed.ko"
truncate -s 128 "$work_dir/malformed.ko"
expect_failure malformed-artifact-preflight \
	python3 "$source_dir/tests/check_built_module.py" "$work_dir/malformed.ko" \
	--kernel-release "$kernel_release"
echo "SIGNATURE_REJECTION=not-applicable CONFIG_MODULE_SIG unset" | tee "$evidence_dir/signing-policy.txt"

step "load and GPIO4 production bind"
record_command modprobe "$module_name"
apply_overlay rp1-gpclk-gpio4
sleep 1
device=$(only_bound_device)
[[ -c /dev/rp1-gpclk ]]
[[ $(stat -c '%a:%U:%G' /dev/rp1-gpclk) == 600:root:root ]]
assert_safe production-bind 1
record_command "$work_dir/phase2e_uapi_client" query
record_command "$work_dir/phase2e_uapi_client" once
record_command python3 "$source_dir/tests/phase2e_dt_identity.py" \
	"/sys/bus/platform/devices/$device/of_node"
find -L "/sys/bus/platform/devices/$device/of_node" -maxdepth 1 -type f -print -exec sh -c \
	'printf "="; od -An -tx1 "$1" | tr -d " \n"; printf "\n"' sh {} \; | tee "$evidence_dir/production-dt.txt"
[[ -s $evidence_dir/production-dt.txt ]]

step "exclusive resource conflict"
before_devices=$(bound_devices)
apply_overlay rp1-gpclk-gpio4-conflict
sleep 1
[[ $(bound_devices) == "$before_devices" ]]
[[ -c /dev/rp1-gpclk ]]
assert_safe conflict-rejected 1
remove_overlay rp1-gpclk-gpio4-conflict
apply_overlay rp1-gpclk-gpio4-dma-conflict
sleep 1
[[ $(bound_devices) == "$before_devices" ]]
[[ -c /dev/rp1-gpclk ]]
assert_safe dma-conflict-rejected 1
remove_overlay rp1-gpclk-gpio4-dma-conflict

step "open descriptor across unbind and unload rejection"
printf '[%s] COMMAND open-descriptor %q\n' "$(date --iso-8601=ns)" /dev/rp1-gpclk
exec 9</dev/rp1-gpclk
printf '[%s] STATUS open-descriptor 0\n' "$(date --iso-8601=ns)"
expect_failure open-descriptor-unload rmmod "$module_name"
lsmod | grep -Eq '^rp1_gpclk_dkms\b'
assert_safe failed-unload-cleanup 1
driver_write "$device" unbind
[[ ! -e /dev/rp1-gpclk ]]
printf '[%s] EXPECTED_FAILURE_COMMAND new-open-after-unbind %q\n' \
	"$(date --iso-8601=ns)" /dev/rp1-gpclk
if exec 8</dev/rp1-gpclk; then
	echo "new open succeeded after unbind" >&2
	exit 1
fi
printf '[%s] EXPECTED_FAILURE_STATUS new-open-after-unbind 1\n' \
	"$(date --iso-8601=ns)"
assert_safe unbound-with-open-descriptor 0
printf '[%s] COMMAND close-descriptor 9\n' "$(date --iso-8601=ns)"
exec 9<&-
printf '[%s] STATUS close-descriptor 0\n' "$(date --iso-8601=ns)"
driver_write "$device" bind
sleep 1
[[ -c /dev/rp1-gpclk ]]
assert_safe rebound-after-open-close 1

step "process death releases descriptor and module reference"
marker="$work_dir/process-holder.pid"
printf '[%s] COMMAND holder-start %q hold %q\n' \
	"$(date --iso-8601=ns)" "$work_dir/phase2e_uapi_client" "$marker"
"$work_dir/phase2e_uapi_client" hold "$marker" &
holder=$!
printf '[%s] STATUS holder-start 0 pid=%d\n' "$(date --iso-8601=ns)" "$holder"
for _ in $(seq 1 50); do [[ -s $marker ]] && break; sleep 0.1; done
[[ -s $marker ]]
read -r marker_pid marker_lease <"$marker"
[[ $marker_pid == "$holder" && $marker_lease -gt 0 ]]
printf '[%s] STATUS holder-ready 0 pid=%d lease=%s\n' \
	"$(date --iso-8601=ns)" "$holder" "$marker_lease"
record_command "$work_dir/phase2e_uapi_client" expect-busy
record_command kill -KILL "$holder"
set +e
wait "$holder" 2>/dev/null
holder_status=$?
set -e
printf '[%s] EXPECTED_FAILURE_STATUS holder-sigkill-wait %d\n' \
	"$(date --iso-8601=ns)" "$holder_status"
[[ $holder_status -eq 137 ]]
holder=
record_command "$work_dir/phase2e_uapi_client" once
driver_write "$device" unbind
record_command rmmod "$module_name"
assert_safe process-death-unload 0

step "partial-probe cleanup fixtures"
record_command modprobe "$module_name"
remove_overlay rp1-gpclk-gpio4
for fixture in rp1-gpclk-gpio4-missing-active rp1-gpclk-gpio4-bad-dma; do
	apply_overlay "$fixture"
	sleep 1
	[[ -z $(bound_devices) ]]
	[[ ! -e /dev/rp1-gpclk ]]
	assert_safe "$fixture-rejected" 0
	remove_overlay "$fixture"
done

step "simulated failed DKMS-recipe kernel update and known-good recovery"
# Expansion occurs after sourcing dkms.conf in the bounded child shell.
# shellcheck disable=SC2016
expect_failure missing-header-dkms-recipe bash -c \
	'cd "$1" || exit 125; kernel_source_dir=/usr/src/linux-headers-phase2e-missing; source ./dkms.conf; set +e; output=$(eval "${MAKE[0]}" 2>&1); status=$?; set -e; printf "%s\n" "$output"; grep -Fq /usr/src/linux-headers-phase2e-missing <<<"$output" || exit 125; exit "$status"' \
	sh "$source_dir"
[[ ! -e /lib/modules/phase2e-missing/updates/dkms/$module_name.ko ]]
apply_overlay rp1-gpclk-gpio4
sleep 1
device=$(only_bound_device)
[[ -c /dev/rp1-gpclk ]]
assert_safe known-good-recovery 1

step "final removal and diagnostics"
remove_overlay rp1-gpclk-gpio4
record_command rmmod "$module_name"
record_command rm -f "$installed_module"
record_command depmod -a "$kernel_release"
assert_safe explicit-final-state 0
assert_absent explicit-final-state
dmesg >"$work_dir/dmesg-final.txt"
dmesg --level=emerg,alert,crit,err,warn >"$work_dir/dmesg-warning-final.txt"
record_command python3 "$source_dir/tests/phase2e_dmesg_delta.py" \
	"$work_dir/dmesg-baseline.txt" "$work_dir/dmesg-final.txt" \
	"$evidence_dir/dmesg-since-start.txt"
record_command python3 "$source_dir/tests/phase2e_dmesg_delta.py" \
	"$work_dir/dmesg-warning-baseline.txt" "$work_dir/dmesg-warning-final.txt" \
	"$evidence_dir/dmesg-warning-or-higher.txt"
cp "$work_dir"/dmesg-{baseline,final}.txt "$evidence_dir/"
cp "$work_dir"/dmesg-warning-{baseline,final}.txt "$evidence_dir/"
cat "$evidence_dir/dmesg-since-start.txt"
cat "$evidence_dir/dmesg-warning-or-higher.txt"
record_command python3 "$source_dir/tests/phase2e_check_dmesg.py" \
	"$evidence_dir/dmesg-warning-or-higher.txt"
record_command rm -rf "$work_dir"
[[ ! -e $work_dir ]]
exec 1>&3 2>&4
wait "$log_tee_pid"
manifest_list=$(mktemp /tmp/rp1-gpclk-phase2e-manifest.XXXXXX)
(cd "$evidence_dir" &&
	find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 | sort -z) \
	>"$manifest_list"
(cd "$evidence_dir" &&
	xargs -0 sha256sum <"$manifest_list" >SHA256SUMS &&
	sha256sum -c SHA256SUMS >/dev/null)
rm -f "$manifest_list"
manifest_list=
trap - EXIT HUP INT TERM
echo "PHASE2E_TARGET_RESULT=PASS"
