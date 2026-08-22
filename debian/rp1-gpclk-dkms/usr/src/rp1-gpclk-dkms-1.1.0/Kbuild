# SPDX-License-Identifier: MIT

obj-m += rp1_gpclk_dkms.o
rp1_gpclk_dkms-y := src/rp1_gpclk_main.o \
	src/rp1_gpclk_bootstrap_policy.o \
	src/rp1_gpclk_compatibility.o \
	src/rp1_gpclk_core.o \
	src/rp1_gpclk_execution.o \
	src/rp1_gpclk_execution_machine.o \
	src/rp1_gpclk_execution_policy.o \
	src/rp1_gpclk_kernel_api.o \
	src/rp1_gpclk_lifetime.o \
	src/rp1_gpclk_resource_policy.o \
	src/rp1_gpclk_uapi_dispatch.o

ccflags-y += -I$(src)/include -I$(src)/include/uapi
