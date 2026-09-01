#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

python3 tests/check_development_workflow.py
python3 tests/check_development_identity.py

unset CDPATH
repo_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/rp1-gpclk-offline.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

python3 "$repo_dir/tests/check_spdx.py"
python3 "$repo_dir/tests/check_test_inventory.py"
python3 "$repo_dir/tests/check_uapi_identity.py"
python3 "$repo_dir/tests/check_uapi_static.py"
python3 "$repo_dir/tests/check_clock_disabled_source_boundary.py"
python3 "$repo_dir/tests/check_pll_sys_parent_contract.py"
python3 "$repo_dir/tests/check_build_contract.py"
python3 "$repo_dir/tests/check_route_uapi_contract.py"
python3 "$repo_dir/tests/check_debian_packaging.py"
python3 "$repo_dir/tests/check_overlay_admin_contract.py"
python3 "$repo_dir/tests/check_signing_policy.py"
python3 "$repo_dir/tests/check_diagnostics_contract.py"
python3 "$repo_dir/tests/check_qualification_harness_contract.py"
python3 "$repo_dir/tests/check_dkms_kernel_scope.py"
python3 "$repo_dir/tests/check_route_manager.py"
python3 "$repo_dir/tests/check_runtime_inventory.py"
python3 "$repo_dir/tests/check_runtime_controller.py"
python3 "$repo_dir/tests/check_runtime_manager.py"
python3 "$repo_dir/tests/check_runtime_output.py"
python3 "$repo_dir/tests/check_runtime_restoration.py"
python3 "$repo_dir/tests/check_runtime_inhibitor_cleanup.py"
python3 "$repo_dir/tests/check_development_route_manager.py"
python3 "$repo_dir/tests/check_doc_links.py"

if command -v shellcheck >/dev/null 2>&1; then
    shellcheck "$repo_dir/tests/run-offline-checks.sh" \
        "$repo_dir/scripts/rp1-gpclk-lifecycle.sh"
    echo "shellcheck: PASS"
else
    echo "shellcheck: SKIP (not installed)"
fi

${CC:-cc} -std=c11 -Wall -Wextra -Werror \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include/uapi" "$repo_dir/tests/uapi_contract.c" \
    -o "$tmp_dir/uapi_contract"
"$tmp_dir/uapi_contract"

${CC:-cc} -std=c11 -Wall -Wextra -Werror \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include/uapi" "$repo_dir/tools/gate_d_uapi_probe.c" \
    -o "$tmp_dir/gate_d_uapi_probe"
echo "UAPI probe compile: PASS"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -DGATE_D_BUSY_LIBRARY \
    -I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include/uapi" \
    -I"$repo_dir/tools" "$repo_dir/tools/gate_d_busy_injector.c" \
    "$repo_dir/tests/busy_state_injector_test.c" \
    -o "$tmp_dir/busy_state_injector_test"
"$tmp_dir/busy_state_injector_test"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -DRP1_GPCLK_HOST_TEST \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include" -I"$repo_dir/include/uapi" \
    "$repo_dir/src/rp1_gpclk_core.c" "$repo_dir/tests/lifecycle_core.c" \
    -o "$tmp_dir/lifecycle_core"
"$tmp_dir/lifecycle_core"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include" -I"$repo_dir/include/uapi" \
    "$repo_dir/src/rp1_gpclk_resource_policy.c" "$repo_dir/tests/resource_policy.c" \
    -o "$tmp_dir/resource_policy"
"$tmp_dir/resource_policy"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include" \
    "$repo_dir/src/rp1_gpclk_compatibility.c" \
    "$repo_dir/tests/compatibility_identity.c" \
    -o "$tmp_dir/compatibility_identity"
"$tmp_dir/compatibility_identity"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -DRP1_GPCLK_HOST_TEST \
    -I"$repo_dir/tests/fixtures/linux" \
    -I"$repo_dir/include" -I"$repo_dir/include/uapi" \
    "$repo_dir/src/rp1_gpclk_execution_policy.c" "$repo_dir/tests/execution_policy.c" \
    -o "$tmp_dir/execution_policy"
"$tmp_dir/execution_policy"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -DRP1_GPCLK_HOST_TEST \
    -I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include" \
    "$repo_dir/src/rp1_gpclk_clock_setup.c" "$repo_dir/tests/clock_setup.c" \
    -o "$tmp_dir/clock_setup"
"$tmp_dir/clock_setup"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include" \
    "$repo_dir/src/rp1_gpclk_execution_machine.c" "$repo_dir/tests/execution_machine.c" \
    -o "$tmp_dir/execution_machine"
"$tmp_dir/execution_machine"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -DRP1_GPCLK_HOST_TEST \
    -I"$repo_dir/include" \
    "$repo_dir/src/rp1_gpclk_bootstrap_policy.c" \
    "$repo_dir/tests/bootstrap_policy.c" \
    -o "$tmp_dir/bootstrap_policy"
"$tmp_dir/bootstrap_policy"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
    -I"$repo_dir/include" "$repo_dir/tests/dma_segments.c" -o "$tmp_dir/dma_segments"
"$tmp_dir/dma_segments"
echo "DMA segment alignment and byte conservation: PASS"

git -C "$repo_dir" diff --check
echo "whitespace: PASS"
