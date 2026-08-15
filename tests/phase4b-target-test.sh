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
kernel=$(uname -r)
headers="/usr/src/linux-headers-$kernel"
common="/usr/src/linux-headers-${kernel%+rpt-rpi-2712}+rpt-common-rpi"
work=$(mktemp -d /tmp/rp1-gpclk-phase4b-live.XXXXXX)
installed="/lib/modules/$kernel/updates/dkms/rp1_gpclk_dkms.ko"
overlay=

safe_state()
{
	pinctrl get 4
	pinctrl get 20
	for name in clk_rate clk_parent clk_prepare_count clk_enable_count clk_protect_count; do
		printf '%s=' "$name"; cat "/sys/kernel/debug/clk/clk_gp0/$name"
	done
}

cleanup()
{
	set +e
	pkill -f "$work/phase4b_sdr_capture" 2>/dev/null
	[[ -n $overlay ]] && dtoverlay -r "$overlay" 2>/dev/null
	rmmod rp1_gpclk_dkms 2>/dev/null
	rm -f "$installed"
	depmod -a "$kernel" 2>/dev/null
	rm -f "$work/signing-key.pem"
	safe_state >"$evidence_dir/final-safe.txt" 2>&1
	dtoverlay -l >"$evidence_dir/final-overlays.txt" 2>&1
	test ! -e /dev/rp1-gpclk
	test ! -e "$installed"
	rm -rf "$work"
}
trap cleanup EXIT

mkdir "$evidence_dir" "$work/overlays"
hostname >"$evidence_dir/hostname.txt"
uname -a >"$evidence_dir/uname.txt"
cat /proc/sys/kernel/random/boot_id >"$evidence_dir/boot-id.txt"
dmesg >"$evidence_dir/dmesg-baseline.txt"
safe_state >"$evidence_dir/baseline-safe.txt"
test ! -e /dev/rp1-gpclk
test -z "$(lsmod | awk '$1 == "rp1_gpclk_dkms" { print $1 }')"

make -C "$source_dir" KERNEL_BUILD="$headers" clean
make -C "$source_dir" KERNEL_BUILD="$headers" W=1 KCFLAGS=-Werror
for pin in 4 20; do
	cpp -nostdinc -I "$common/include" -undef -x assembler-with-cpp \
		"$source_dir/overlays/rp1-gpclk-gpio$pin.dts" >"$work/gpio$pin.pp.dts"
	dtc -@ -I dts -O dtb -o "$work/overlays/rp1-gpclk-gpio$pin.dtbo" \
		"$work/gpio$pin.pp.dts"
done
cc -std=c11 -Wall -Wextra -Werror -I"$source_dir/include/uapi" \
	"$source_dir/tests/phase4b_live_client.c" -lm -o "$work/phase4b_live_client"
g++ -std=c++17 -Wall -Wextra -Werror "$source_dir/tests/phase4b_sdr_capture.cpp" \
	$(pkg-config --cflags --libs SoapySDR) -o "$work/phase4b_sdr_capture"

openssl req -new -x509 -newkey rsa:2048 -nodes -days 1 \
	-subj /CN=RP1-GPCLK-Phase4B-GPIO4-Final/ -keyout "$work/signing-key.pem" \
	-outform DER -out "$work/signing-cert.der"
cp "$source_dir/rp1_gpclk_dkms.ko" "$work/module.ko"
"$headers/scripts/sign-file" sha256 "$work/signing-key.pem" \
	"$work/signing-cert.der" "$work/module.ko"
install -D -m 0644 "$work/module.ko" "$installed"
depmod -a "$kernel"
modprobe rp1_gpclk_dkms live_output=1
modinfo "$installed" >"$evidence_dir/modinfo.txt"
sha256sum /sys/firmware/fdt "$source_dir/rp1_gpclk_dkms.ko" "$work/module.ko" \
	"$source_dir/include/uapi/linux/rp1_gpclk.h" "$work/overlays"/*.dtbo \
	>"$evidence_dir/identities.txt"

# GPIO20 is administratively probed but must not enroll or expose an endpoint.
dtoverlay -d "$work/overlays" rp1-gpclk-gpio20
overlay=rp1-gpclk-gpio20
sleep 1
test ! -e /dev/rp1-gpclk
dtoverlay -r "$overlay"
overlay=

dtoverlay -d "$work/overlays" rp1-gpclk-gpio4
overlay=rp1-gpclk-gpio4
sleep 1
"$work/phase4b_live_client" query | tee "$evidence_dir/query.txt"

run_capture()
{
	local name=$1 mode=$2 seconds=$3 before pid
	before=$(dmesg | wc -l)
	"$work/phase4b_sdr_capture" "$evidence_dir/$name.cf32" "$seconds" \
		"$evidence_dir/$name.ready" >"$evidence_dir/$name-capture.txt" \
		2>"$evidence_dir/$name-capture-err.txt" &
	pid=$!
	for _ in $(seq 1 100); do [[ -s $evidence_dir/$name.ready ]] && break; sleep 0.05; done
	[[ -s $evidence_dir/$name.ready ]]
	"$work/phase4b_live_client" "$mode" >"$evidence_dir/$name-client.txt"
	wait "$pid"
	dmesg | tail -n "+$((before + 1))" >"$evidence_dir/$name-dmesg.txt"
	grep 'phase4b generation=' "$evidence_dir/$name-dmesg.txt" \
		>"$evidence_dir/$name-telemetry.txt"
	grep -q 'cleanup=0' "$evidence_dir/$name-telemetry.txt"
	grep -q 'tick_initial=00000000/00000032/00000000/00000000 tick_final=00000000/00000032/00000000/00000000' \
		"$evidence_dir/$name-telemetry.txt"
	safe_state >"$evidence_dir/$name-safe.txt"
}

for number in $(seq -w 1 10); do run_capture "qrss-$number" qrss 3; done
run_capture fskcw fskcw 8
run_capture dfcw dfcw 8
run_capture cancel cancel 3
python3 "$source_dir/tests/phase4b_analyze.py" "$evidence_dir" \
	| tee "$evidence_dir/analysis.txt"

dmesg >"$evidence_dir/dmesg-final-before-cleanup.txt"
python3 "$source_dir/tests/phase2e_dmesg_delta.py" \
	"$evidence_dir/dmesg-baseline.txt" \
	"$evidence_dir/dmesg-final-before-cleanup.txt" \
	"$evidence_dir/dmesg-live-delta.txt"
[[ $(grep -c 'phase4b generation=' "$evidence_dir/dmesg-live-delta.txt") -eq 13 ]]
! grep -Eq 'BUG:|WARNING:|Oops:|Call trace:|phase4b cleanup:|cleanup=-[1-9]' \
	"$evidence_dir/dmesg-live-delta.txt"
cp "$work/module.ko" "$evidence_dir/module.ko"
cp "$work/signing-cert.der" "$evidence_dir/signing-cert.der"
rm -f "$work/signing-key.pem"
cleanup
trap - EXIT
(cd "$evidence_dir" && find . -type f ! -name SHA256SUMS -printf '%P\0' \
	| sort -z | xargs -0 sha256sum) >"$evidence_dir/SHA256SUMS"
echo PHASE4B_GPIO4_TARGET_RESULT=PASS
