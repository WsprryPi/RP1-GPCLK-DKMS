// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/string.h>

#include "rp1_gpclk/compatibility.h"
#include "rp1_gpclk/core.h"

bool rp1_gpclk_gpio4_candidate_allowed(__u32 route,
				       const char *kernel_release,
				       const char *architecture,
				       const char *module_version,
				       bool pi5_model_b,
				       bool resources_validated)
{
	if (!kernel_release || !architecture || !module_version)
		return false;
	return route == RP1_GPCLK_ROUTE_GPIO4 &&
		!strcmp(kernel_release, RP1_GPCLK_GPIO4_CANDIDATE_KERNEL) &&
		!strcmp(architecture, RP1_GPCLK_GPIO4_CANDIDATE_ARCH) &&
		!strcmp(module_version, RP1_GPCLK_GPIO4_CANDIDATE_VERSION) &&
		pi5_model_b && resources_validated;
}

bool rp1_gpclk_route_candidate_allowed(__u32 route,
				       const char *kernel_release,
				       const char *architecture,
				       const char *module_version,
				       bool pi5_model_b,
				       bool resources_validated)
{
	if (!kernel_release || !architecture || !module_version ||
	    !pi5_model_b || !resources_validated)
		return false;
	if (strcmp(kernel_release, RP1_GPCLK_ROUTE_CANDIDATE_KERNEL) ||
	    strcmp(architecture, RP1_GPCLK_ROUTE_CANDIDATE_ARCH) ||
	    strcmp(module_version, RP1_GPCLK_ROUTE_CANDIDATE_VERSION))
		return false;

	/*
	 * The v3 UAPI changes the exact source identity.  Neither route inherits
	 * the r2 target evidence; a later, route-specific qualification may enable
	 * an r3 candidate.
	 */
	switch (route) {
	case RP1_GPCLK_ROUTE_GPIO4:
	case RP1_GPCLK_ROUTE_GPIO20:
		return false;
	default:
		return false;
	}
}

const char *rp1_gpclk_route_candidate_id(__u32 route)
{
	switch (route) {
	case RP1_GPCLK_ROUTE_GPIO4:
		return RP1_GPCLK_GPIO4_DEVELOPMENT_CANDIDATE_ID;
	case RP1_GPCLK_ROUTE_GPIO20:
		return RP1_GPCLK_GPIO20_DEVELOPMENT_CANDIDATE_ID;
	default:
		return "v1.1.2-invalid-route";
	}
}
