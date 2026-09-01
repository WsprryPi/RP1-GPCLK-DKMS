// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/string.h>

#include "rp1_gpclk/compatibility.h"
#include "rp1_gpclk/core.h"

bool rp1_gpclk_compatibility_allowed(__u32 route,
				     const char *kernel_release,
				     const char *architecture,
				     const char *module_version,
				     bool pi5_model_b,
				     bool resources_validated)
{
	if (!kernel_release || !kernel_release[0] || !architecture ||
	    !module_version ||
	    !pi5_model_b || !resources_validated)
		return false;
	if (strcmp(architecture, RP1_GPCLK_COMPATIBILITY_ARCH) ||
	    strcmp(module_version, RP1_GPCLK_COMPATIBILITY_VERSION))
		return false;

	/*
	 * Eligibility admits an exact 0.9.0 development build on the supported
	 * Pi 5 architecture to an explicitly authorized Experimental attempt.
	 * The running kernel remains diagnostic and build provenance, not a
	 * per-release permission list.  This does not transfer predecessor evidence
	 * or qualify either route; GPIO4 and GPIO20 remain independently attributable.
	 */
	switch (route) {
	case RP1_GPCLK_ROUTE_GPIO4:
	case RP1_GPCLK_ROUTE_GPIO20:
		return true;
	default:
		return false;
	}
}

const char *rp1_gpclk_compatibility_id(__u32 route)
{
	switch (route) {
	case RP1_GPCLK_ROUTE_GPIO4:
		return RP1_GPCLK_GPIO4_COMPATIBILITY_ID;
	case RP1_GPCLK_ROUTE_GPIO20:
		return RP1_GPCLK_GPIO20_COMPATIBILITY_ID;
	default:
		return "v0.9.0-invalid-route";
	}
}
