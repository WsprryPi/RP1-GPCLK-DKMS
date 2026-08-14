// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>
#include <linux/fs.h>

#include "rp1_gpclk/uapi_dispatch.h"

long rp1_gpclk_uapi_dispatch(struct file *file, unsigned int command,
                            unsigned long argument)
{
    return -EOPNOTSUPP;
}
