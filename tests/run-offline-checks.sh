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
python3 "$repo_dir/tests/check_phase3b_target_assets.py"
python3 "$repo_dir/tests/check_phase4a_live_path.py"
python3 "$repo_dir/tests/check_phase4d_combined_gate.py"
python3 "$repo_dir/tests/check_phase5_packaging.py"
python3 "$repo_dir/tests/check_phase5_3_installation.py"
python3 "$repo_dir/tests/check_phase5_4_overlay.py"
python3 "$repo_dir/tests/check_phase5_5_permissions.py"
python3 "$repo_dir/tests/check_phase5_6_compatibility.py"
python3 "$repo_dir/tests/check_phase5_7_signing.py"
python3 "$repo_dir/tests/check_phase5_8_diagnostics.py"
python3 "$repo_dir/tests/check_phase5_9_lifecycle.py"
python3 "$repo_dir/tests/check_phase5_10_matrix.py"
python3 "$repo_dir/tests/check_phase5_11_release_gates.py"
python3 "$repo_dir/tests/check_phase5_12_calibrated_review.py"
python3 "$repo_dir/tests/check_gate_d_lifecycle.py"
python3 "$repo_dir/tests/check_gate_d_boot.py"
python3 "$repo_dir/tests/check_gate_d_target_plan.py"
python3 "$repo_dir/tests/check_gate_d_attempts.py"
python3 "$repo_dir/tests/check_gate_d_outer.py"
python3 "$repo_dir/tests/check_gate_d_bootstrap.py"
python3 "$repo_dir/tests/check_gate_d_root.py"
python3 "$repo_dir/tests/check_gate_d_root_schemas.py"
python3 "$repo_dir/tests/check_gate_d_root_trust.py"
python3 "$repo_dir/tests/check_gate_d_version_pair.py"
python3 "$repo_dir/tests/check_gate_c_representative_build.py"
python3 "$repo_dir/tests/check_gate_d_matrix_policy.py"
if command -v check-jsonschema >/dev/null 2>&1; then
	check-jsonschema --schemafile "$repo_dir/schema/gate-d-execution-instance-v1.schema.json" \
		"$repo_dir/release/gate-d-execution-instance-v1.json"
	echo "Gate D execution-instance schema: PASS"
	if [ -f "$repo_dir/release/gate-d-version-pair-v1.json" ]; then
		check-jsonschema --schemafile "$repo_dir/schema/gate-d-version-pair-v1.schema.json" \
			"$repo_dir/release/gate-d-version-pair-v1.json"
		echo "Gate D version-pair schema: PASS"
	fi
else
	echo "Gate D execution-instance schema: SKIP (check-jsonschema unavailable)"
fi
python3 "$repo_dir/tests/test_phase2e_dmesg.py"
python3 "$repo_dir/tests/check_doc_links.py"
if command -v shellcheck >/dev/null 2>&1; then
	shellcheck "$repo_dir/tests/run-offline-checks.sh" \
		"$repo_dir/scripts/rp1-gpclk-lifecycle.sh" \
		"$repo_dir/tests/phase2e-target-test.sh" \
		"$repo_dir/tests/phase3b-target-test.sh" \
		"$repo_dir/tests/phase4a-target-test.sh"
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
echo "Gate D UAPI probe compile: PASS"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -DGATE_D_BUSY_LIBRARY \
    -I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include/uapi" \
    -I"$repo_dir/tools" "$repo_dir/tools/gate_d_busy_injector.c" \
    "$repo_dir/tests/gate_d_busy_injector_test.c" \
    -o "$tmp_dir/gate_d_busy_injector_test"
"$tmp_dir/gate_d_busy_injector_test"

${CC:-cc} -std=c11 -Wall -Wextra -Werror \
    -I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include/uapi" \
    -I"$repo_dir/tools" "$repo_dir/tools/gate_d_busy_injector.c" \
    -o "$tmp_dir/gate_d_busy_injector"
echo "Gate D busy-state injector compile: PASS"

if [ "$(uname -s)" = Linux ]; then
    ${CC:-cc} -std=c11 -Wall -Wextra -Werror \
        -I"$repo_dir/include/uapi" "$repo_dir/tests/phase2e_uapi_client.c" \
        -o "$tmp_dir/phase2e_uapi_client"
	echo "Phase 2E UAPI client compile: PASS"
	${CC:-cc} -std=c11 -Wall -Wextra -Werror \
		-I"$repo_dir/include/uapi" "$repo_dir/tests/phase3b_uapi_client.c" \
		-o "$tmp_dir/phase3b_uapi_client"
	echo "Phase 3B UAPI client compile: PASS"
	${CC:-cc} -std=c11 -Wall -Wextra -Werror \
		-I"$repo_dir/include/uapi" "$repo_dir/tests/phase4a_uapi_client.c" \
		-o "$tmp_dir/phase4a_uapi_client"
	echo "Phase 4A UAPI client compile: PASS"
	${CC:-cc} -std=c11 -Wall -Wextra -Werror \
		-I"$repo_dir/include/uapi" "$repo_dir/tests/phase4d_live_client.c" \
		-lm -o "$tmp_dir/phase4d_live_client"
	echo "Phase 4D live client compile: PASS"
else
	echo "Phase 2E UAPI client compile: SKIP (Linux target only)"
	echo "Phase 3B UAPI client compile: SKIP (Linux target only)"
	echo "Phase 4A UAPI client compile: SKIP (Linux target only)"
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

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
	-DRP1_GPCLK_HOST_TEST \
	-I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include" \
	-I"$repo_dir/include/uapi" \
	"$repo_dir/src/rp1_gpclk_execution_policy.c" \
	"$repo_dir/tests/execution_policy.c" -o "$tmp_dir/execution_policy"
"$tmp_dir/execution_policy"
"$tmp_dir/execution_policy"

${CC:-cc} -std=c11 -Wall -Wextra -Werror -pedantic \
	-I"$repo_dir/tests/fixtures/linux" -I"$repo_dir/include" \
	"$repo_dir/src/rp1_gpclk_execution_machine.c" \
	"$repo_dir/tests/execution_machine.c" -o "$tmp_dir/execution_machine"
"$tmp_dir/execution_machine"
"$tmp_dir/execution_machine"

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
