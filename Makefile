# SPDX-License-Identifier: MIT

.PHONY: all modules check package-check release-unit validate-release validate-release-candidate clean

all: modules

modules:
	@test -n "$(KERNEL_BUILD)" || { echo "KERNEL_BUILD=/path/to/kernel/build is required"; exit 2; }
	$(MAKE) -C $(KERNEL_BUILD) M=$(CURDIR) modules

check:
	./tests/run-offline-checks.sh

package-check:
	python3 tests/check_debian_packaging.py
	python3 tests/check_phase554_dkms_kernel_scope.py
	python3 tests/check_phase554_lifecycle_controls.py
	python3 tests/check_phase554_lifecycle_attempt2_controls.py
	python3 tests/check_release_candidate_builder.py
	python3 tests/check_release_1_0_0_repaired_target_success.py
	python3 tests/check_release_1_0_0_public_download_success.py

release-unit:
	./scripts/build_release.py "$(if $(OUTPUT_DIR),$(OUTPUT_DIR),dist)" $(if $(DEVELOPMENT),--development,)

validate-release:
	./scripts/validate_release.py "$(if $(OUTPUT_DIR),$(OUTPUT_DIR),dist)" $(if $(DEVELOPMENT),--allow-development,)

validate-release-candidate:
	./scripts/validate_release_candidate.py "$(if $(OUTPUT_DIR),$(OUTPUT_DIR),dist)" $(if $(SOURCE_COMMIT),--expect-source-commit $(SOURCE_COMMIT),)

clean:
	@test -n "$(KERNEL_BUILD)" || { echo "KERNEL_BUILD=/path/to/kernel/build is required"; exit 2; }
	$(MAKE) -C $(KERNEL_BUILD) M=$(CURDIR) clean
