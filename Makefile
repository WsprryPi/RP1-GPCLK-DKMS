# SPDX-License-Identifier: MIT

.PHONY: all modules check package-check release-unit validate-release clean

all: modules

modules:
	@test -n "$(KERNEL_BUILD)" || { echo "KERNEL_BUILD=/path/to/kernel/build is required"; exit 2; }
	$(MAKE) -C $(KERNEL_BUILD) M=$(CURDIR) modules

check:
	./tests/run-offline-checks.sh

package-check:
	python3 tests/check_debian_packaging.py
	python3 tests/check_phase554_dkms_kernel_scope.py

release-unit:
	./scripts/build_release.py "$(if $(OUTPUT_DIR),$(OUTPUT_DIR),dist)" $(if $(DEVELOPMENT),--development,)

validate-release:
	./scripts/validate_release.py "$(if $(OUTPUT_DIR),$(OUTPUT_DIR),dist)" $(if $(DEVELOPMENT),--allow-development,)

clean:
	@test -n "$(KERNEL_BUILD)" || { echo "KERNEL_BUILD=/path/to/kernel/build is required"; exit 2; }
	$(MAKE) -C $(KERNEL_BUILD) M=$(CURDIR) clean
