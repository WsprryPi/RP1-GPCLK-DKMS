// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/init.h>
#include <linux/module.h>

static int __init rp1_gpclk_init(void)
{
    pr_info("rp1_gpclk_dkms: inert Phase 2A skeleton; no device registered\n");
    return 0;
}

static void __exit rp1_gpclk_exit(void)
{
    pr_info("rp1_gpclk_dkms: inert Phase 2A skeleton removed\n");
}

module_init(rp1_gpclk_init);
module_exit(rp1_gpclk_exit);

MODULE_AUTHOR("Lee Bussy");
MODULE_DESCRIPTION("Inert RP1 GPCLK DKMS Phase 2A skeleton");
MODULE_LICENSE("Dual MIT/GPL");
