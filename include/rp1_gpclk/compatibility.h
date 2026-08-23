/* SPDX-License-Identifier: GPL-2.0-only OR MIT */
#ifndef RP1_GPCLK_COMPATIBILITY_H
#define RP1_GPCLK_COMPATIBILITY_H

#include <linux/types.h>

#define RP1_GPCLK_GPIO4_CANDIDATE_KERNEL "6.18.34+rpt-rpi-2712"
#define RP1_GPCLK_GPIO4_CANDIDATE_ARCH "aarch64"
#define RP1_GPCLK_GPIO4_CANDIDATE_VERSION "1.0.1"
#define RP1_GPCLK_GPIO4_CANDIDATE_ID "v1.0.1-wspr5-gpio4-6.18.34"

#define RP1_GPCLK_ROUTE_CANDIDATE_KERNEL "6.18.34+rpt-rpi-2712"
#define RP1_GPCLK_ROUTE_CANDIDATE_ARCH "aarch64"
#define RP1_GPCLK_ROUTE_CANDIDATE_VERSION "1.1.2"
#define RP1_GPCLK_GPIO4_DEVELOPMENT_CANDIDATE_ID \
	"v1.1.2-pi5-gpio4-6.18.34-development-candidate"
#define RP1_GPCLK_GPIO20_DEVELOPMENT_CANDIDATE_ID \
	"v1.1.2-pi5-gpio20-6.18.34-development-candidate"

bool rp1_gpclk_gpio4_candidate_allowed(__u32 route,
				       const char *kernel_release,
				       const char *architecture,
				       const char *module_version,
				       bool pi5_model_b,
				       bool resources_validated);

bool rp1_gpclk_route_candidate_allowed(__u32 route,
				       const char *kernel_release,
				       const char *architecture,
				       const char *module_version,
				       bool pi5_model_b,
				       bool resources_validated);

const char *rp1_gpclk_route_candidate_id(__u32 route);

#endif /* RP1_GPCLK_COMPATIBILITY_H */
