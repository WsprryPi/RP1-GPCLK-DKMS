/* SPDX-License-Identifier: GPL-2.0-only OR MIT */
#ifndef RP1_GPCLK_DEVICE_H
#define RP1_GPCLK_DEVICE_H

#include <linux/clk.h>
#include <linux/dmaengine.h>
#include <linux/kref.h>
#include <linux/miscdevice.h>
#include <linux/mutex.h>
#include <linux/pinctrl/consumer.h>
#include <linux/types.h>

#include "rp1_gpclk/core.h"

struct rp1_gpclk_device {
	struct device *dev;
	struct kref refcount;
	struct mutex lock;
	bool dead;
	bool misc_registered;
	bool rate_exclusive;
	bool divider_mapped;
	struct miscdevice miscdev;
	struct clk *clock;
	struct dma_chan *dma_chan;
	struct pinctrl *pinctrl;
	struct pinctrl_state *pins_default;
	struct pinctrl_state *pins_active;
	struct pinctrl_state *pins_safe;
	phys_addr_t divider_phys;
	dma_addr_t divider_dma;
	struct rp1_gpclk_core core;
};

#endif /* RP1_GPCLK_DEVICE_H */
