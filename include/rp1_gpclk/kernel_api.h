/* SPDX-License-Identifier: GPL-2.0-only OR MIT */
#ifndef RP1_GPCLK_KERNEL_API_H
#define RP1_GPCLK_KERNEL_API_H

struct rp1_gpclk_device;

/* Phase 2A seams: every implementation remains fail-closed and unavailable. */
int rp1_gpclk_dt_validate(struct rp1_gpclk_device *device);
int rp1_gpclk_clock_acquire(struct rp1_gpclk_device *device);
int rp1_gpclk_dma_acquire(struct rp1_gpclk_device *device);
int rp1_gpclk_pinctrl_acquire(struct rp1_gpclk_device *device);
void rp1_gpclk_resources_release(struct rp1_gpclk_device *device);

#endif /* RP1_GPCLK_KERNEL_API_H */
