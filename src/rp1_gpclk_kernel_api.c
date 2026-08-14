// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>

#include "rp1_gpclk/kernel_api.h"

int rp1_gpclk_dt_validate(struct rp1_gpclk_device *device)
{
    return -EOPNOTSUPP;
}

int rp1_gpclk_clock_acquire(struct rp1_gpclk_device *device)
{
    return -EOPNOTSUPP;
}

int rp1_gpclk_dma_acquire(struct rp1_gpclk_device *device)
{
    return -EOPNOTSUPP;
}

int rp1_gpclk_pinctrl_acquire(struct rp1_gpclk_device *device)
{
    return -EOPNOTSUPP;
}

void rp1_gpclk_resources_release(struct rp1_gpclk_device *device)
{
}
