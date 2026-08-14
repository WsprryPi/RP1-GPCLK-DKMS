#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

unset CDPATH
repo_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/rp1-gpclk-offline.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

python3 "$repo_dir/tests/check_spdx.py"
python3 "$repo_dir/tests/check_uapi_identity.py"
python3 "$repo_dir/tests/check_manifest.py"
python3 "$repo_dir/tests/check_phase2c_integration.py"
python3 "$repo_dir/tests/check_phase2d_build.py"
python3 "$repo_dir/tests/check_phase2e_target_assets.py"
python3 "$repo_dir/tests/check_phase3_interface_freeze.py"
python3 "$repo_dir/tests/test_phase2e_dmesg.py"
python3 "$repo_dir/tests/check_doc_links.py"
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck "$repo_dir/tests/run-offline-checks.sh" \
        "$repo_dir/tests/phase2e-target-test.sh"
    echo "shellcheck: PASS"
else
    echo "shellcheck: SKIP (not installed)"
fi

${CC:-cc} -std=c11 -Wall -Wextra -Werror \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include/uapi" "$repo_dir/tests/uapi_contract.c" \
    -o "$tmp_dir/uapi_contract"
"$tmp_dir/uapi_contract"

if [ "$(uname -s)" = Linux ]; then
    ${CC:-cc} -std=c11 -Wall -Wextra -Werror \
        -I"$repo_dir/include/uapi" "$repo_dir/tests/phase2e_uapi_client.c" \
        -o "$tmp_dir/phase2e_uapi_client"
    echo "Phase 2E UAPI client compile: PASS"
else
    echo "Phase 2E UAPI client compile: SKIP (Linux target only)"
fi

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -DRP1_GPCLK_HOST_TEST \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include" -I"$repo_dir/include/uapi" \
    "$repo_dir/src/rp1_gpclk_core.c" "$repo_dir/tests/lifecycle_core.c" \
    -o "$tmp_dir/lifecycle_core"
"$tmp_dir/lifecycle_core"
"$tmp_dir/lifecycle_core"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
	-I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include" \
	-I"$repo_dir/include/uapi" \
    "$repo_dir/src/rp1_gpclk_resource_policy.c" \
    "$repo_dir/tests/resource_policy.c" -o "$tmp_dir/resource_policy"
"$tmp_dir/resource_policy"
"$tmp_dir/resource_policy"

if ${CC:-cc} -std=c11 -fsanitize=address,undefined \
    -DRP1_GPCLK_HOST_TEST \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include" -I"$repo_dir/include/uapi" \
    "$repo_dir/src/rp1_gpclk_core.c" "$repo_dir/tests/lifecycle_core.c" \
    -o "$tmp_dir/lifecycle_core_sanitized" >/dev/null 2>&1; then
    "$tmp_dir/lifecycle_core_sanitized"
    echo "lifecycle sanitizers: PASS"
else
    echo "lifecycle sanitizers: SKIP (compiler support unavailable)"
fi

cp "$repo_dir/include/uapi/linux/rp1_gpclk.h" "$tmp_dir/consumer.h"
python3 "$repo_dir/tests/check_uapi_identity.py" "$tmp_dir/consumer.h"
printf '\n' >> "$tmp_dir/consumer.h"
if python3 "$repo_dir/tests/check_uapi_identity.py" "$tmp_dir/consumer.h" >/dev/null 2>&1; then
    echo "byte-different consumer UAPI unexpectedly passed" >&2
    exit 1
fi
echo "UAPI negative identity: PASS"

if git -C "$repo_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$repo_dir" diff --check
    echo "whitespace: PASS"
else
    echo "whitespace: SKIP (source archive has no Git metadata)"
fi
