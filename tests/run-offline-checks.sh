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
python3 "$repo_dir/tests/check_artifact_scoped_invalidation_policy.py"
python3 "$repo_dir/tests/check_qualification_successor.py"
python3 "$repo_dir/tests/check_phase553_qualification_successor_evidence.py"
python3 "$repo_dir/tests/check_phase553_final_qualification_successor.py"
python3 "$repo_dir/tests/check_phase553_final_split_offline_twice.py"
python3 "$repo_dir/tests/check_phase553_final_control_package_recapture.py"
python3 "$repo_dir/tests/check_phase553_same_version_qualification_successor.py"
python3 "$repo_dir/tests/check_phase553_final_control_reconstruction_prerequisite.py"
python3 "$repo_dir/tests/check_phase553_final_control_closure_readiness.py"
python3 "$repo_dir/tests/check_phase553_fresh_qualification_after_removal.py"
python3 "$repo_dir/tests/check_phase553_representative_build_transfer.py"
python3 "$repo_dir/tests/check_phase553_final_control_set.py"
python3 "$repo_dir/tests/check_phase553_final_control_preauthorization.py"
python3 "$repo_dir/tests/check_phase553_final_staging_transport.py"
python3 "$repo_dir/tests/check_phase553_final_staging_transport_evidence.py"
python3 "$repo_dir/tests/check_phase553_final_staging_authorization_decision.py"
python3 "$repo_dir/tests/check_phase553_product_only_candidate.py"
python3 "$repo_dir/tests/check_phase553_product_target_decision.py"
python3 "$repo_dir/tests/check_phase553_product_target_install.py"
python3 "$repo_dir/tests/check_phase5_26_topology_docs.py"
python3 "$repo_dir/tests/check_gate_d_lifecycle.py"
python3 "$repo_dir/tests/check_gate_d_instance_schema6.py"
python3 "$repo_dir/tests/check_gate_d_boot.py"
python3 "$repo_dir/tests/check_gate_d_boot_operation_construction.py"
python3 "$repo_dir/tests/check_gate_d_target_plan.py"
python3 "$repo_dir/tests/check_gate_d_attempts.py"
python3 "$repo_dir/tests/check_gate_d_phase_scoped_paths.py"
python3 "$repo_dir/tests/check_gate_d_phase5_24_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_25_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_26_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_27_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_28_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_29_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_30_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_31_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_32_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_33_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_34_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_35_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_36_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_37_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_39_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_41_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_42_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_43_control_set.py"
if [ -n "${PHASE5_43_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_43_archived_preroot.py" "$PHASE5_43_RELEASE_ARCHIVE"
else
    echo "Phase 5.43 exact archived pre-root envelope validation: SKIP (archive not supplied)"
fi
python3 "$repo_dir/tests/check_gate_d_phase5_45_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_45_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_45_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_45_authorization.py"
if [ -n "${PHASE5_45_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_45_archived_preroot.py" "$PHASE5_45_RELEASE_ARCHIVE"
else
    echo "Phase 5.45 exact archived pre-root envelope validation: SKIP (archive not supplied)"
fi
python3 "$repo_dir/tests/check_gate_d_phase5_46_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_46_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_46_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_46_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_46_target_staging_preroot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_46_attempt1_failure.py"
if [ -n "${PHASE5_46_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_46_archived_preroot.py" "$PHASE5_46_RELEASE_ARCHIVE"
else
    echo "Phase 5.46 exact archived pre-root envelope validation: SKIP (archive not supplied)"
fi
python3 "$repo_dir/tests/check_gate_d_phase5_47_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_metadata_free_preroot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_attempt1_residue_blocker.py"
python3 "$repo_dir/tests/check_gate_d_phase5_48_attempt1_residue_cleanup.py"
if [ -n "${PHASE5_48_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_48_archived_preroot.py" "$PHASE5_48_RELEASE_ARCHIVE"
else
    echo "Phase 5.48 exact archived pre-root envelope validation: SKIP (archive not supplied)"
fi
python3 "$repo_dir/tests/check_gate_d_phase5_47_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_47_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_47_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_47_target_staging_failure.py"
python3 "$repo_dir/tests/check_gate_d_phase5_47_metadata_free_preroot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_47_attempt1_preflight_blocker.py"
python3 "$repo_dir/tests/check_gate_d_service_snapshot_contract.py"
if [ -n "${PHASE5_47_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_47_archived_preroot.py" "$PHASE5_47_RELEASE_ARCHIVE"
else
    echo "Phase 5.47 exact archived pre-root envelope validation: SKIP (archive not supplied)"
fi
python3 "$repo_dir/tests/check_gate_d_live_snapshot.py"
python3 "$repo_dir/tests/check_gate_d_live_snapshot_owned.py"
python3 "$repo_dir/tests/check_gate_d_same_version.py"
python3 "$repo_dir/tests/check_gate_d_phase5_49_snapshot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_50_snapshot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_50_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_snapshot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_snapshot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_control_set.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_split_staging_rehearsal.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_repaired_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_repaired_staging_preroot_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_staging_preroot_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_53_staging_preroot_blocker.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_metadata_free_preroot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_metadata_free_preroot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_attempt1.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_attempt1.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_attempt2.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_attempt2.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_attempt3_failure.py"
python3 "$repo_dir/tests/check_gate_d_phase5_52_attempt3_failure.py"
python3 "$repo_dir/tests/check_gate_d_phase5_50_preauthorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_50_authorization_decision.py"
python3 "$repo_dir/tests/check_gate_d_phase5_50_authorization.py"
python3 "$repo_dir/tests/check_gate_d_phase5_50_metadata_free_preroot.py"
python3 "$repo_dir/tests/check_gate_d_phase5_51_schema6_repair.py"
if [ -n "${PHASE5_50_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_50_archived_control_set.py" "$PHASE5_50_RELEASE_ARCHIVE"
else
    echo "Phase 5.50 exact archived control-set validation: SKIP (archive not supplied)"
fi
if [ -n "${PHASE5_51_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_51_archived_control_set.py" "$PHASE5_51_RELEASE_ARCHIVE"
else
    echo "Phase 5.51 exact archived control-set validation: SKIP (archive not supplied)"
fi
if [ -n "${PHASE5_52_RELEASE_ARCHIVE:-}" ]; then
    python3 "$repo_dir/tests/check_gate_d_phase5_52_archived_control_set.py" "$PHASE5_52_RELEASE_ARCHIVE"
else
    echo "Phase 5.52 exact archived control-set validation: SKIP (archive not supplied)"
fi
python3 "$repo_dir/tests/check_gate_d_outer.py"
python3 "$repo_dir/tests/check_gate_d_schema2_terminal_cleanup.py"
python3 "$repo_dir/tests/check_gate_d_target_path_topology_audit.py"
python3 "$repo_dir/tests/check_gate_d_bootstrap.py"
python3 "$repo_dir/tests/check_gate_d_root.py"
python3 "$repo_dir/tests/check_gate_d_root_schemas.py"
python3 "$repo_dir/tests/check_gate_d_root_trust.py"
python3 "$repo_dir/tests/check_gate_d_preroot.py"
python3 "$repo_dir/tests/check_gate_d_preroot_split_inputs.py"
python3 "$repo_dir/tests/check_gate_d_residue.py"
python3 "$repo_dir/tests/check_gate_d_installed_import_graph.py"
python3 "$repo_dir/tests/check_gate_d_installed_cli_rehearsal.py"
python3 "$repo_dir/tests/check_gate_d_version_pair.py"
python3 "$repo_dir/tests/check_gate_c_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase545_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase546_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase547_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase548_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase549_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase550_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase551_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase552_representative_build.py"
python3 "$repo_dir/tests/check_gate_c_phase553_representative_build.py"
python3 "$repo_dir/tests/check_gate_d_phase553_control_set_blocker.py"
python3 "$repo_dir/tests/check_gate_c_phase549_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase550_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase551_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase552_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase553_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase548_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase547_offline_twice.py"
python3 "$repo_dir/tests/check_gate_c_phase545_offline_twice.py"
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
