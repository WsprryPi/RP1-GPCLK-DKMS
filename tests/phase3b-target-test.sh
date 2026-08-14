#!/bin/bash
# SPDX-License-Identifier: MIT
set -Eeuo pipefail

if [[ $EUID -ne 0 || $# -ne 2 ]]; then
	echo "usage: sudo $0 SOURCE_DIR NEW_EVIDENCE_DIR" >&2
	exit 2
fi

source_dir=$(realpath "$1")
[[ ! -e $2 ]] || { echo "evidence directory already exists" >&2; exit 2; }
evidence_dir=$(realpath -m "$2")
kernel_release=$(uname -r)
kernel_build="/usr/src/linux-headers-$kernel_release"
kernel_common="/usr/src/linux-headers-${kernel_release%+rpt-rpi-2712}+rpt-common-rpi"
dt_include="$kernel_common/include"
module_name=rp1_gpclk_dkms
driver_dir=/sys/bus/platform/drivers/rp1-gpclk-dkms
installed_module="/lib/modules/$kernel_release/updates/dkms/$module_name.ko"
work_dir=$(mktemp -d /tmp/rp1-gpclk-phase3b.XXXXXX)
overlay_dir="$work_dir/overlays"
log_file="$evidence_dir/target-run.log"
declare -a applied_overlays=()
holder=
manifest_list=

mkdir -p "$evidence_dir" "$overlay_dir"
dmesg >"$work_dir/dmesg-baseline.txt"
dmesg --level=emerg,alert,crit,err,warn >"$work_dir/dmesg-warning-baseline.txt"
exec 3>&1 4>&2
exec > >(tee "$log_file") 2>&1
log_tee_pid=$!

step() { printf '\n[%s] STEP %s\n' "$(date --iso-8601=ns)" "$*"; }

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
	local label=$1 expected_protect=$2 pin4 pin20 prepare enable protect
	pin4=$(pinctrl get 4)
	pin20=$(pinctrl get 20)
	prepare=$(cat /sys/kernel/debug/clk/clk_gp0/clk_prepare_count)
	enable=$(cat /sys/kernel/debug/clk/clk_gp0/clk_enable_count)
	protect=$(cat /sys/kernel/debug/clk/clk_gp0/clk_protect_count)
	printf '[%s] SAFE %s gpio4=%q gpio20=%q prepare=%s enable=%s protect=%s expected=%s\n' \
		"$(date --iso-8601=ns)" "$label" "$pin4" "$pin20" \
		"$prepare" "$enable" "$protect" "$expected_protect"
	[[ $pin4 == *"GPIO4 = none"* || $pin4 == *"GPIO4 = input"* ]]
	[[ $pin20 == *"GPIO20 = none"* || $pin20 == *"GPIO20 = input"* ]]
	[[ $pin4 != *gpclk* && $pin20 != *gpclk* && $prepare == 0 && \
		$enable == 0 && $protect == "$expected_protect" ]]
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

assert_absent()
{
	local label=$1 overlays loaded=0 device=0 installed=0 clients bound
	overlays=$(dtoverlay -l)
	lsmod | grep -Eq '^rp1_gpclk_dkms\b' && loaded=1
	[[ -e /dev/rp1-gpclk ]] && device=1
	[[ -e $installed_module ]] && installed=1
	clients=$(pgrep -f "$work_dir/phase3b_uapi_client" || true)
	bound=$(bound_devices)
	printf '[%s] ABSENT %s overlays=%q loaded=%d device=%d installed=%d bound=%q clients=%q\n' \
		"$(date --iso-8601=ns)" "$label" "$overlays" "$loaded" "$device" \
		"$installed" "$bound" "$clients"
	[[ $overlays == 'No overlays loaded' && $loaded -eq 0 && $device -eq 0 && \
		$installed -eq 0 && -z $bound && -z $clients ]]
}

driver_write()
{
	local attribute=$1 value=$2
	# Positional parameters intentionally expand only in the bounded child shell.
	# shellcheck disable=SC2016
	record_command sh -c 'printf "%s" "$1" >"$2"' sh "$value" "$driver_dir/$attribute"
}

apply_overlay()
{
	local name=$1
	applied_overlays+=("$name")
	record_command dtoverlay -d "$overlay_dir" "$name"
}

expect_overlay_failure()
{
	local name=$1
	expect_failure "$name-overlay-apply" dtoverlay -d "$overlay_dir" "$name"
}

remove_overlay()
{
	local name=$1 index
	record_command dtoverlay -r "$name"
	for index in "${!applied_overlays[@]}"; do
		if [[ ${applied_overlays[$index]} == "$name" ]]; then
			unset 'applied_overlays[index]'
		fi
	done
}

cleanup()
{
	local status=$? index name failed=0
	set +e
	if [[ -n $holder ]] && kill -0 "$holder" 2>/dev/null; then
		kill -TERM "$holder" 2>/dev/null || failed=1
		timeout 5s tail --pid="$holder" -f /dev/null || true
		kill -KILL "$holder" 2>/dev/null || true
		wait "$holder" 2>/dev/null || true
	fi
	for ((index=${#applied_overlays[@]}-1; index>=0; index--)); do
		name=${applied_overlays[$index]:-}
		[[ -z $name ]] || timeout 30s dtoverlay -r "$name" || failed=1
	done
	if lsmod | grep -Eq '^rp1_gpclk_dkms\b'; then
		timeout 30s rmmod "$module_name" || failed=1
	fi
	if [[ -f $installed_module ]]; then
		rm -f "$installed_module" || failed=1
		timeout 30s depmod -a "$kernel_release" || failed=1
	fi
	rm -rf "$work_dir" || failed=1
	[[ -z $manifest_list ]] || rm -f "$manifest_list" || failed=1
	assert_safe trap-final 0 || failed=1
	[[ $failed -eq 0 ]] || status=1
	trap - EXIT HUP INT TERM
	exit "$status"
}
trap cleanup EXIT HUP INT TERM

step "authorization, exact target, and baseline"
echo "authorization=User directed execution of Phase 3B prompt on documented exact target wspr5; clock-disabled administration only" |
	tee "$evidence_dir/authorization.txt"
[[ $(hostname) == wspr5 ]]
grep -aFq 'Raspberry Pi 5 Model B Rev 1.0' /proc/device-tree/model
[[ -d $kernel_build && -d $dt_include ]]
[[ ! -e $installed_module && ! -e /dev/rp1-gpclk ]]
[[ $(dtoverlay -l) == 'No overlays loaded' ]]
if lsmod | grep -Eq '^rp1_gpclk_dkms\b'; then
	echo "module was already loaded" >&2
	exit 1
fi
assert_safe baseline 0
{
	echo "start=$(date --iso-8601=seconds)"
	echo "hostname=$(hostname)"
	echo "kernel=$kernel_release"
	echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
	echo "model=$(tr -d '\000' </proc/device-tree/model)"
	echo "compatible=$(tr '\000' ',' </proc/device-tree/compatible)"
	dpkg-query -W -f='header_package=${Package} ${Version}\n' "linux-headers-$kernel_release"
	echo "compiler=$(gcc --version | head -1)"
	echo "module_sig=$(grep -E '^CONFIG_MODULE_SIG(=|_)' "$kernel_build/.config" || echo unset)"
	vcgencmd version 2>/dev/null || true
	sha256sum /sys/firmware/fdt 2>/dev/null || true
	for field in clk_rate clk_parent clk_prepare_count clk_enable_count clk_protect_count; do
		printf '%s=' "$field"; cat "/sys/kernel/debug/clk/clk_gp0/$field"
	done
} | tee "$evidence_dir/identity.txt"
(cd "$source_dir" && find . -type f -not -path './.git/*' -print0 | sort -z |
	xargs -0 sha256sum) >"$evidence_dir/source-tree-sha256.txt"
if [[ -f ${source_dir}.tar.gz ]]; then
	sha256sum "${source_dir}.tar.gz" | tee "$evidence_dir/source-archive-sha256.txt"
fi

step "offline checks, build, overlays, and client"
record_command "$source_dir/tests/run-offline-checks.sh"
record_command make -C "$source_dir" KERNEL_BUILD="$kernel_build" clean
record_command make -C "$source_dir" KERNEL_BUILD="$kernel_build" W=1 KCFLAGS=-Werror
for dts in "$source_dir"/overlays/*.dts "$source_dir"/overlays/fixtures/*.dts; do
	name=$(basename "$dts" .dts)
	cpp -nostdinc -I "$dt_include" -undef -x assembler-with-cpp "$dts" >"$work_dir/$name.pp.dts"
	record_command dtc -@ -I dts -O dtb -o "$overlay_dir/$name.dtbo" "$work_dir/$name.pp.dts"
	record_command dtc -I dtb -O dts -o "$evidence_dir/$name.decompiled.dts" "$overlay_dir/$name.dtbo"
done
record_command python3 "$source_dir/tests/check_built_module.py" \
	"$source_dir/$module_name.ko" --kernel-release "$kernel_release"
record_command cc -std=c11 -Wall -Wextra -Werror -I"$source_dir/include/uapi" \
	"$source_dir/tests/phase3b_uapi_client.c" -o "$work_dir/phase3b_uapi_client"
sha256sum "$source_dir/$module_name.ko" "$overlay_dir"/*.dtbo |
	tee "$evidence_dir/artifact-sha256.txt"

step "sign, install, load exact artifact"
openssl req -new -x509 -newkey rsa:2048 -nodes -days 1 -subj /CN=RP1-GPCLK-Phase3B/ \
	-keyout "$work_dir/signing-key.pem" -outform DER -out "$work_dir/signing-cert.der"
cp "$source_dir/$module_name.ko" "$work_dir/$module_name.ko"
record_command "$kernel_build/scripts/sign-file" sha256 "$work_dir/signing-key.pem" \
	"$work_dir/signing-cert.der" "$work_dir/$module_name.ko"
record_command install -D -m 0644 "$work_dir/$module_name.ko" "$installed_module"
record_command depmod -a "$kernel_release"
[[ $(modinfo -n "$module_name") == "$installed_module" ]]
cmp "$work_dir/$module_name.ko" "$installed_module"
modinfo "$installed_module" | tee "$evidence_dir/module-signed.txt"
record_command modprobe "$module_name"
[[ $(cat "/sys/module/$module_name/version") == 0.0.0-phase3b ]]
assert_safe load-no-overlay 0

route_matrix()
{
	local route=$1 pin=$2 other=$3 device before fixture
	local overlay="rp1-gpclk-gpio$pin"
	step "GPIO$pin independent route matrix"
	apply_overlay "$overlay"
	sleep 1
	device=$(only_bound_device)
	[[ -c /dev/rp1-gpclk && $(stat -c '%a:%U:%G' /dev/rp1-gpclk) == 600:root:root ]]
	assert_safe "gpio$pin-bind" 1
	record_command "$work_dir/phase3b_uapi_client" query "$route"
	record_command "$work_dir/phase3b_uapi_client" once "$route"
	record_command "$work_dir/phase3b_uapi_client" expect-mismatch "$route"
	record_command "$work_dir/phase3b_uapi_client" once "$route"
	record_command python3 "$source_dir/tests/phase3b_dt_identity.py" \
		"/sys/bus/platform/devices/$device/of_node" "$route" "$pin"
	find -L "/sys/bus/platform/devices/$device/of_node" -maxdepth 1 -type f -print -exec sh -c \
		'printf "="; od -An -tx1 "$1" | tr -d " \n"; printf "\n"' sh {} \; |
		tee "$evidence_dir/gpio$pin-production-dt.txt"
	before=$(bound_devices)
	expect_overlay_failure "rp1-gpclk-gpio$other"
	sleep 1
	[[ $(bound_devices) == "$before" && -c /dev/rp1-gpclk ]]
	assert_safe "gpio$pin-other-route-conflict" 1
	for fixture in "rp1-gpclk-gpio$pin-conflict" \
		"rp1-gpclk-gpio$pin-dma-conflict"; do
		apply_overlay "$fixture"
		sleep 1
		[[ $(bound_devices) == "$before" && -c /dev/rp1-gpclk ]]
		assert_safe "$fixture-rejected" 1
		remove_overlay "$fixture"
	done
	marker="$work_dir/gpio$pin-holder.pid"
	"$work_dir/phase3b_uapi_client" hold "$route" "$marker" &
	holder=$!
	for _ in $(seq 1 50); do [[ -s $marker ]] && break; sleep 0.1; done
	[[ -s $marker ]]
	record_command "$work_dir/phase3b_uapi_client" expect-busy "$route"
	record_command kill -KILL "$holder"
	set +e; wait "$holder" 2>/dev/null; holder_status=$?; set -e
	printf '[%s] EXPECTED_FAILURE_STATUS gpio%s-holder-sigkill-wait %d\n' \
		"$(date --iso-8601=ns)" "$pin" "$holder_status"
	[[ $holder_status -eq 137 ]]
	holder=
	record_command "$work_dir/phase3b_uapi_client" once "$route"
	remove_overlay "$overlay"
	assert_safe "gpio$pin-removed" 0
	for fixture in "rp1-gpclk-gpio$pin-missing-active" \
		"rp1-gpclk-gpio$pin-bad-dma"; do
		apply_overlay "$fixture"
		sleep 1
		[[ -z $(bound_devices) && ! -e /dev/rp1-gpclk ]]
		assert_safe "$fixture-rejected" 0
		remove_overlay "$fixture"
	done
}

route_matrix 1 4 20
route_matrix 2 20 4

step "invalid and mismatched route fixtures"
for fixture in rp1-gpclk-route-invalid rp1-gpclk-gpio20-route-mismatch; do
	apply_overlay "$fixture"
	sleep 1
	[[ -z $(bound_devices) && ! -e /dev/rp1-gpclk ]]
	assert_safe "$fixture-rejected" 0
	remove_overlay "$fixture"
done

step "three repeated administrative cycles in both directions"
for order in '1 4 2 20' '2 20 1 4'; do
	for cycle in 1 2 3; do
		read -r -a route_order <<<"$order"
		set -- "${route_order[@]}"
		while [[ $# -gt 0 ]]; do
			route=$1; pin=$2; shift 2
			apply_overlay "rp1-gpclk-gpio$pin"
			sleep 1
			only_bound_device >/dev/null
			assert_safe "cycle-$cycle-gpio$pin-bind" 1
			record_command "$work_dir/phase3b_uapi_client" query "$route"
			record_command "$work_dir/phase3b_uapi_client" expect-mismatch "$route"
			record_command "$work_dir/phase3b_uapi_client" once "$route"
			remove_overlay "rp1-gpclk-gpio$pin"
			[[ -z $(bound_devices) && ! -e /dev/rp1-gpclk ]]
			assert_safe "cycle-$cycle-gpio$pin-absent" 0
		done
	done
done

open_lifetime_matrix()
{
	local route=$1 pin=$2 device
	step "GPIO$pin open descriptor across unbind and reload"
	apply_overlay "rp1-gpclk-gpio$pin"
	sleep 1
	device=$(only_bound_device)
	printf '[%s] OPEN_EXISTING gpio%s route=%s\n' "$(date --iso-8601=ns)" "$pin" "$route"
	exec 9</dev/rp1-gpclk
	expect_failure "gpio$pin-open-unload-before-unbind" rmmod "$module_name"
	driver_write unbind "$device"
	[[ ! -e /dev/rp1-gpclk && -z $(bound_devices) ]]
	assert_safe "gpio$pin-unbound-open" 0
	# The descriptor path intentionally expands only in the bounded child shell.
	# shellcheck disable=SC2016
	expect_failure "gpio$pin-new-open-after-unbind" sh -c 'exec 8<"$1"' sh /dev/rp1-gpclk
	expect_failure "gpio$pin-open-unload-after-unbind" rmmod "$module_name"
	printf '[%s] CLOSE_EXISTING gpio%s route=%s\n' "$(date --iso-8601=ns)" "$pin" "$route"
	exec 9<&-
	driver_write bind "$device"
	sleep 1
	[[ -c /dev/rp1-gpclk ]]
	assert_safe "gpio$pin-rebound-after-close" 1
	remove_overlay "rp1-gpclk-gpio$pin"
	assert_safe "gpio$pin-lifetime-removed" 0
}

open_lifetime_matrix 1 4
open_lifetime_matrix 2 20

step "missing-header update failure and recovery"
# Expansion intentionally occurs in the bounded child shell after dkms.conf is sourced.
# shellcheck disable=SC2016
expect_failure missing-header-dkms-recipe bash -c \
	'cd "$1" || exit 125; kernel_source_dir=/usr/src/linux-headers-phase3b-missing; source ./dkms.conf; set +e; output=$(eval "${MAKE[0]}" 2>&1); status=$?; set -e; printf "%s\n" "$output"; grep -Fq linux-headers-phase3b-missing <<<"$output" || exit 125; exit "$status"' \
	sh "$source_dir"
for pin in 4 20; do
	apply_overlay "rp1-gpclk-gpio$pin"
	sleep 1
	assert_safe "known-good-gpio$pin" 1
	remove_overlay "rp1-gpclk-gpio$pin"
	assert_safe "known-good-gpio$pin-absent" 0
done

step "final removal, diagnostics, and portable evidence"
record_command rmmod "$module_name"
record_command rm -f "$installed_module"
record_command depmod -a "$kernel_release"
assert_safe explicit-final 0
assert_absent explicit-final
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
record_command python3 "$source_dir/tests/phase3b_check_dmesg.py" \
	"$evidence_dir/dmesg-warning-or-higher.txt"
record_command rm -rf "$work_dir"
exec 1>&3 2>&4
wait "$log_tee_pid"
manifest_list=$(mktemp /tmp/rp1-gpclk-phase3b-manifest.XXXXXX)
(cd "$evidence_dir" && find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 | sort -z) >"$manifest_list"
(cd "$evidence_dir" && xargs -0 sha256sum <"$manifest_list" >SHA256SUMS &&
	sha256sum -c SHA256SUMS >/dev/null)
rm -f "$manifest_list"
manifest_list=
trap - EXIT HUP INT TERM
echo "PHASE3B_TARGET_RESULT=PASS"
