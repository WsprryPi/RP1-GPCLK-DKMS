// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>
#ifndef RP1_GPCLK_HOST_TEST
#include <linux/math64.h>
#endif

#include "rp1_gpclk/execution_policy.h"

int rp1_gpclk_execution_tones_valid(const struct rp1_gpclk_tone *tones,
				    __u32 tone_count, __u32 drive_ma)
{
	__u64 integer;
	__u32 index;

	if (!tones || !tone_count || tone_count > RP1_GPCLK_MAX_TONES ||
	    drive_ma != RP1_GPCLK_DRIVE_MA_2)
		return -EINVAL;
	integer = tones[0].lower_divider_q16 >>
		RP1_GPCLK_DIVIDER_FRACTIONAL_BITS;
	if (!integer || integer > RP1_GPCLK_DIVIDER_INTEGER_MAX)
		return -ERANGE;
	for (index = 0; index < tone_count; index++) {
		if (tones[index].lower_divider_q16 > RP1_GPCLK_DIVIDER_Q16_MAX ||
		    tones[index].upper_divider_q16 > RP1_GPCLK_DIVIDER_Q16_MAX ||
		    tones[index].upper_divider_q16 !=
			    tones[index].lower_divider_q16 + 1 ||
		    (tones[index].lower_divider_q16 >>
			    RP1_GPCLK_DIVIDER_FRACTIONAL_BITS) != integer ||
		    (tones[index].upper_divider_q16 >>
			    RP1_GPCLK_DIVIDER_FRACTIONAL_BITS) != integer)
			return -ERANGE;
	}
	return 0;
}

int rp1_gpclk_execution_event_writes(__u64 duration_ns, size_t *writes)
{
	__u64 value;

	if (!writes || !duration_ns)
		return -EINVAL;
#ifdef RP1_GPCLK_HOST_TEST
	value = (__u64)(((__uint128_t)duration_ns *
		RP1_GPCLK_TICK_SOURCE_HZ) /
		((__u64)RP1_GPCLK_TICK_DIVIDER * 1000000000ULL));
#else
	value = mul_u64_u64_div_u64(duration_ns, RP1_GPCLK_TICK_SOURCE_HZ,
		(__u64)RP1_GPCLK_TICK_DIVIDER * 1000000000ULL);
#endif
	if (!value || value > (size_t)-1)
		return -ERANGE;
	*writes = value;
	return 0;
}

int rp1_gpclk_execution_fill_words(const struct rp1_gpclk_tone *tone,
				   __u32 *words, size_t count)
{
	__u64 period;
	__u64 accumulator = 0;
	size_t index;

	if (!tone || !words || !count)
		return -EINVAL;
	period = (__u64)tone->lower_count + tone->upper_count;
	if (!period)
		return -EINVAL;
	for (index = 0; index < count; index++) {
		accumulator += tone->lower_count;
		if (accumulator >= period) {
			words[index] = (__u32)(tone->lower_divider_q16 & 0xffffULL)
				       << 16;
			accumulator -= period;
		} else {
			words[index] = (__u32)(tone->upper_divider_q16 & 0xffffULL)
				       << 16;
		}
	}
	return 0;
}
