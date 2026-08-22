// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <string.h>

#include "rp1_gpclk/compatibility.h"
#include "rp1_gpclk/core.h"

#define CHECK(value) do { if (!(value)) return __LINE__; } while (0)

int main(void)
{
	const char *kernel = RP1_GPCLK_GPIO4_CANDIDATE_KERNEL;
	const char *arch = RP1_GPCLK_GPIO4_CANDIDATE_ARCH;
	const char *version = RP1_GPCLK_GPIO4_CANDIDATE_VERSION;

	CHECK(rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, arch, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO20,
		kernel, arch, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_INVALID,
		kernel, arch, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		"6.18.35+rpt-rpi-2712", arch, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		"6.18.34+rpt-rpi-v8", arch, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, "armv7l", version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, arch, "1.0.2", true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, arch, version, false, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, arch, version, true, false));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		NULL, arch, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, NULL, version, true, true));
	CHECK(!rp1_gpclk_gpio4_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		kernel, arch, NULL, true, true));

	version = RP1_GPCLK_ROUTE_CANDIDATE_VERSION;
	CHECK(!rp1_gpclk_route_candidate_allowed(RP1_GPCLK_ROUTE_GPIO4,
		RP1_GPCLK_ROUTE_CANDIDATE_KERNEL,
		RP1_GPCLK_ROUTE_CANDIDATE_ARCH, version, true, true));
	CHECK(!rp1_gpclk_route_candidate_allowed(RP1_GPCLK_ROUTE_GPIO20,
		RP1_GPCLK_ROUTE_CANDIDATE_KERNEL,
		RP1_GPCLK_ROUTE_CANDIDATE_ARCH, version, true, true));
	CHECK(!strcmp(rp1_gpclk_route_candidate_id(RP1_GPCLK_ROUTE_GPIO4),
		RP1_GPCLK_GPIO4_UNAVAILABLE_ID));
	CHECK(!strcmp(rp1_gpclk_route_candidate_id(RP1_GPCLK_ROUTE_GPIO20),
		RP1_GPCLK_GPIO20_UNAVAILABLE_ID));
	CHECK(strcmp(rp1_gpclk_route_candidate_id(RP1_GPCLK_ROUTE_GPIO4),
		rp1_gpclk_route_candidate_id(RP1_GPCLK_ROUTE_GPIO20)));
	puts("compatibility identity: PASS (GPIO4/GPIO20 independent and denied)");
	return 0;
}
