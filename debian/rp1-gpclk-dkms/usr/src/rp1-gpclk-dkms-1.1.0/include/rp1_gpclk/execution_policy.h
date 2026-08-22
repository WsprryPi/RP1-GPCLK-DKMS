/* SPDX-License-Identifier: GPL-2.0-only OR MIT */
#ifndef RP1_GPCLK_EXECUTION_POLICY_H
#define RP1_GPCLK_EXECUTION_POLICY_H

#include <linux/types.h>
#include <linux/stddef.h>

#include <uapi/linux/rp1_gpclk.h>

#define RP1_GPCLK_TICK_SOURCE_HZ 50000000ULL

int rp1_gpclk_execution_tones_valid(const struct rp1_gpclk_tone_v1 *tones,
				    __u32 tone_count, __u32 drive_ma);
int rp1_gpclk_execution_event_writes(__u64 duration_ns, size_t *writes);
int rp1_gpclk_execution_fill_words(const struct rp1_gpclk_tone_v1 *tone,
				   __u32 *words, size_t count);

#endif /* RP1_GPCLK_EXECUTION_POLICY_H */
