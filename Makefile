# SPDX-License-Identifier: MIT

.PHONY: all modules check clean

all: modules

modules:
	@test -n "$(KERNEL_BUILD)" || { echo "KERNEL_BUILD=/path/to/kernel/build is required"; exit 2; }
	$(MAKE) -C $(KERNEL_BUILD) M=$(CURDIR) modules

check:
	./tests/run-offline-checks.sh

clean:
	@test -n "$(KERNEL_BUILD)" || { echo "KERNEL_BUILD=/path/to/kernel/build is required"; exit 2; }
	$(MAKE) -C $(KERNEL_BUILD) M=$(CURDIR) clean
