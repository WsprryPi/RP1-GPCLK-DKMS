/* SPDX-License-Identifier: GPL-2.0-only OR MIT */
#ifndef RP1_GPCLK_UAPI_DISPATCH_H
#define RP1_GPCLK_UAPI_DISPATCH_H

struct file;

/* No file operations or device node are registered in Phase 2A. */
long rp1_gpclk_uapi_dispatch(struct file *file, unsigned int command,
                            unsigned long argument);

#endif /* RP1_GPCLK_UAPI_DISPATCH_H */
