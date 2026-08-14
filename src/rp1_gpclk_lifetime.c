// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>

#include "rp1_gpclk/lifetime.h"

int rp1_gpclk_lifetime_init(struct rp1_gpclk_device *device)
{
    return -EOPNOTSUPP;
}

void rp1_gpclk_lifetime_mark_dead(struct rp1_gpclk_device *device)
{
}

void rp1_gpclk_lifetime_put(struct rp1_gpclk_device *device)
{
}
