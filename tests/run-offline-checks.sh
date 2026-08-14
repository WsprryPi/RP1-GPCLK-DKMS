#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

unset CDPATH
repo_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/rp1-gpclk-phase2a.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

python3 "$repo_dir/tests/check_spdx.py"
python3 "$repo_dir/tests/check_uapi_identity.py"
python3 "$repo_dir/tests/check_manifest.py"
python3 "$repo_dir/tests/check_inert_skeleton.py"
python3 "$repo_dir/tests/check_doc_links.py"
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck "$repo_dir/tests/run-offline-checks.sh"
    echo "shellcheck: PASS"
else
    echo "shellcheck: SKIP (not installed)"
fi

${CC:-cc} -std=c11 -Wall -Wextra -Werror \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include/uapi" "$repo_dir/tests/uapi_contract.c" \
    -o "$tmp_dir/uapi_contract"
"$tmp_dir/uapi_contract"

cp "$repo_dir/include/uapi/linux/rp1_gpclk.h" "$tmp_dir/consumer.h"
python3 "$repo_dir/tests/check_uapi_identity.py" "$tmp_dir/consumer.h"
printf '\n' >> "$tmp_dir/consumer.h"
if python3 "$repo_dir/tests/check_uapi_identity.py" "$tmp_dir/consumer.h" >/dev/null 2>&1; then
    echo "byte-different consumer UAPI unexpectedly passed" >&2
    exit 1
fi
echo "UAPI negative identity: PASS"

if git -C "$repo_dir" diff --check; then
    echo "whitespace: PASS"
fi
