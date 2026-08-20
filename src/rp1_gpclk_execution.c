// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/clk.h>
#include <linux/clk-provider.h>
#include <linux/dmaengine.h>
#include <linux/dma-mapping.h>
#include <linux/err.h>
#include <linux/jiffies.h>
#include <linux/iopoll.h>
#include <linux/kthread.h>
#include <linux/math64.h>
#include <linux/ktime.h>
#include <linux/pinctrl/consumer.h>
#include <linux/slab.h>
#include <linux/wait.h>

#include "rp1_gpclk/device.h"
#include "rp1_gpclk/execution.h"
#include "rp1_gpclk/execution_machine.h"
#include "rp1_gpclk/execution_policy.h"
#include "rp1_gpclk/kernel_api.h"

#define RP1_GPCLK_TICKS_DMA0_CTRL 0x0
#define RP1_GPCLK_TICKS_DMA0_CYCLES 0x4
#define RP1_GPCLK_DMA_TICK0_EN 0x0
#define RP1_GPCLK_DMA_TICK0_CTRL 0x4
#define RP1_GPCLK_DMA_TICK_REQUEST BIT(0)
#define RP1_GPCLK_DMA_TICK_SINGLE BIT(1)
#define RP1_GPCLK_DMA_TICK_FINISH_CLEAR BIT(0)
#define RP1_GPCLK_DMA_TICK_DWELL (19U << 4)
#define RP1_GPCLK_COMPLETION_SLACK_MS 1000U
#define RP1_GPCLK_QUIESCE_TIMEOUT_MS 122000U

struct rp1_gpclk_execution_plan {
	__u32 mode;
	__u32 drive_ma;
	__u32 tone_count;
	__u32 event_count;
	__u32 symbol_count;
	__u32 writes_per_symbol;
	__u64 expected_frame_duration_ns;
	struct rp1_gpclk_tone_v1 tones[RP1_GPCLK_MAX_TONES];
	struct rp1_gpclk_event_v1 events[RP1_GPCLK_MAX_EVENTS];
	unsigned char symbols[RP1_GPCLK_WSPR_SYMBOLS];
};

struct rp1_gpclk_execution_context {
	struct rp1_gpclk_device *device;
	const struct rp1_gpclk_execution_plan *plan;
	__u32 *word;
	dma_addr_t word_dma;
	__u32 expected;
};

static void rp1_gpclk_dma_complete(void *argument)
{
	struct rp1_gpclk_device *device = argument;

	if (READ_ONCE(device->dma_generation) ==
	    READ_ONCE(device->execution_generation))
		complete(&device->dma_done);
}

static void rp1_gpclk_tick_stop(struct rp1_gpclk_device *device)
{
	writel(0, device->dma_tick0 + RP1_GPCLK_DMA_TICK0_EN);
	writel(0, device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CTRL);
}

static void rp1_gpclk_tick_start(struct rp1_gpclk_device *device)
{
	writel(RP1_GPCLK_TICK_DIVIDER,
	       device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CYCLES);
	writel(RP1_GPCLK_DMA_TICK_FINISH_CLEAR | RP1_GPCLK_DMA_TICK_DWELL,
	       device->dma_tick0 + RP1_GPCLK_DMA_TICK0_CTRL);
	dma_async_issue_pending(device->dma_chan);
	writel(RP1_GPCLK_DMA_TICK_REQUEST | RP1_GPCLK_DMA_TICK_SINGLE,
	       device->dma_tick0 + RP1_GPCLK_DMA_TICK0_EN);
	writel(1, device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CTRL);
}

static unsigned long rp1_gpclk_timeout_jiffies(__u64 duration_ns)
{
	__u64 milliseconds = div_u64(duration_ns + NSEC_PER_MSEC - 1,
				      NSEC_PER_MSEC);

	if (milliseconds > UINT_MAX - RP1_GPCLK_COMPLETION_SLACK_MS)
		milliseconds = UINT_MAX - RP1_GPCLK_COMPLETION_SLACK_MS;
	return msecs_to_jiffies((unsigned int)milliseconds +
				RP1_GPCLK_COMPLETION_SLACK_MS);
}

static int rp1_gpclk_configure_dma(struct rp1_gpclk_device *device,
				   dma_addr_t buffer_dma, size_t bytes,
				   enum dma_transfer_direction direction)
{
	struct dma_async_tx_descriptor *descriptor;
	struct dma_slave_config config = { };
	dma_cookie_t cookie;
	int ret;

	config.direction = direction;
	if (direction == DMA_MEM_TO_DEV) {
		config.dst_addr = device->divider_dma;
		config.dst_addr_width = DMA_SLAVE_BUSWIDTH_4_BYTES;
		config.dst_maxburst = 1;
	} else {
		config.src_addr = device->divider_dma;
		config.src_addr_width = DMA_SLAVE_BUSWIDTH_4_BYTES;
		config.src_maxburst = 1;
	}
	ret = dmaengine_slave_config(device->dma_chan, &config);
	if (ret)
		return ret;
	reinit_completion(&device->dma_done);
	descriptor = dmaengine_prep_slave_single(device->dma_chan, buffer_dma,
		bytes, direction, DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
	if (!descriptor)
		return -EIO;
	descriptor->callback = rp1_gpclk_dma_complete;
	descriptor->callback_param = device;
	cookie = dmaengine_submit(descriptor);
	ret = dma_submit_error(cookie);
	if (ret)
		return ret;
	device->dma_cookie = cookie;
	WRITE_ONCE(device->dma_generation, device->execution_generation);
	device->dma_submitted = true;
	return 0;
}

static int rp1_gpclk_wait_dma(struct rp1_gpclk_device *device,
			      __u64 duration_ns)
{
	unsigned long completed;

	rp1_gpclk_tick_start(device);
	completed = wait_for_completion_timeout(&device->dma_done,
		rp1_gpclk_timeout_jiffies(duration_ns));
	rp1_gpclk_tick_stop(device);
	if (!completed) {
		dmaengine_terminate_sync(device->dma_chan);
		device->dma_submitted = false;
		return -ETIMEDOUT;
	}
	/* RP1 DMA must reach a terminated channel state before direction change. */
	dmaengine_terminate_sync(device->dma_chan);
	device->dma_submitted = false;
	return 0;
}

static int rp1_gpclk_machine_set_rate(void *argument)
{
	struct rp1_gpclk_execution_context *context = argument;
	struct rp1_gpclk_device *device = context->device;
	const struct rp1_gpclk_execution_plan *plan = context->plan;
	struct clk *parent;
	unsigned long parent_rate;
	unsigned long requested_rate;
	int ret;

	ret = rp1_gpclk_execution_tones_valid(plan->tones, plan->tone_count,
					      plan->drive_ma);
	if (ret)
		return ret;
	device->initial_tick_dma0_ctrl =
		readl(device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CTRL);
	device->initial_tick_dma0_cycles =
		readl(device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CYCLES);
	device->initial_dma_tick0_en =
		readl(device->dma_tick0 + RP1_GPCLK_DMA_TICK0_EN);
	device->initial_dma_tick0_ctrl =
		readl(device->dma_tick0 + RP1_GPCLK_DMA_TICK0_CTRL);
	device->tick_state_captured = true;
	if (device->initial_tick_dma0_ctrl || device->initial_dma_tick0_en) {
		dev_err(device->dev,
			"phase4d startup conflict: tick=%08x/%08x/%08x/%08x\n",
			device->initial_tick_dma0_ctrl,
			device->initial_tick_dma0_cycles,
			device->initial_dma_tick0_en,
			device->initial_dma_tick0_ctrl);
		return -EBUSY;
	}
	if (__clk_is_enabled(device->clock)) {
		dev_err(device->dev,
			"phase4d startup conflict: common clock reports hardware enabled\n");
		return -EBUSY;
	}
	device->initial_rate = clk_get_rate(device->clock);
	parent = clk_get_parent(device->clock);
	if (!parent)
		return -ENODEV;
	parent_rate = clk_get_rate(parent);
	if (!parent_rate || parent_rate > (U64_MAX >> RP1_GPCLK_FRACTIONAL_BITS))
		return -ERANGE;
	requested_rate = DIV_ROUND_CLOSEST_ULL(
		(__u64)parent_rate << RP1_GPCLK_FRACTIONAL_BITS,
		plan->tones[0].lower_divider_q16);
	if (!requested_rate)
		return -ERANGE;
	ret = clk_set_rate(device->clock, requested_rate);
	return ret;
}

static int rp1_gpclk_machine_prepare(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;
	int ret = clk_prepare(device->clock);

	if (ret)
		return ret;
	device->clock_prepared = true;
	return 0;
}

static int rp1_gpclk_machine_select_active(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;
	int ret = pinctrl_select_state(device->pinctrl, device->pins_active);

	if (ret)
		return ret;
	device->pins_active_selected = true;
	return 0;
}

static int rp1_gpclk_machine_readback(void *argument);

static int rp1_gpclk_machine_stop_tick(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;

	rp1_gpclk_tick_stop(device);
	return 0;
}

static int rp1_gpclk_machine_terminate_dma(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;

	if (device->dma_submitted) {
		dmaengine_terminate_sync(device->dma_chan);
		device->dma_submitted = false;
	}
	if (device->tick_state_captured) {
		__u32 observed;
		int ret;

		writel(device->initial_tick_dma0_cycles,
		       device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CYCLES);
		writel(device->initial_dma_tick0_ctrl,
		       device->dma_tick0 + RP1_GPCLK_DMA_TICK0_CTRL);
		writel(device->initial_dma_tick0_en,
		       device->dma_tick0 + RP1_GPCLK_DMA_TICK0_EN);
		writel(device->initial_tick_dma0_ctrl,
		       device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CTRL);
		ret = readl_poll_timeout(
			device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CTRL, observed,
			observed == device->initial_tick_dma0_ctrl, 1, 1000);
		ret = ret ?: readl_poll_timeout(
			device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CYCLES, observed,
			observed == device->initial_tick_dma0_cycles, 1, 1000);
		ret = ret ?: readl_poll_timeout(
			device->dma_tick0 + RP1_GPCLK_DMA_TICK0_EN, observed,
			observed == device->initial_dma_tick0_en, 1, 1000);
		ret = ret ?: readl_poll_timeout(
			device->dma_tick0 + RP1_GPCLK_DMA_TICK0_CTRL, observed,
			observed == device->initial_dma_tick0_ctrl, 1, 1000);
		if (ret) {
			dev_err(device->dev,
				"phase4d cleanup: tick register restoration verification failed\n");
			return ret;
		}
		device->tick_state_captured = false;
	}
	return 0;
}

static int rp1_gpclk_machine_disable(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;

	if (device->clock_enabled) {
		clk_disable(device->clock);
		device->clock_enabled = false;
	}
	return 0;
}

static int rp1_gpclk_machine_unprepare(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;

	if (device->clock_prepared) {
		clk_unprepare(device->clock);
		device->clock_prepared = false;
	}
	return 0;
}

static int rp1_gpclk_machine_select_safe(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;
	int ret = 0;

	if (device->pins_active_selected)
		ret = pinctrl_select_state(device->pinctrl, device->pins_safe);
	if (ret)
		dev_err(device->dev, "phase4d cleanup: safe pinctrl failed: %d\n",
			ret);
	device->pins_active_selected = false;
	return ret;
}

static int rp1_gpclk_machine_restore_rate(void *argument)
{
	struct rp1_gpclk_device *device =
		((struct rp1_gpclk_execution_context *)argument)->device;
	unsigned long initial_rate = device->initial_rate;

	device->initial_rate = 0;
	if (initial_rate) {
		int ret = clk_set_rate(device->clock, initial_rate);

		if (ret)
			dev_err(device->dev,
				"phase4d cleanup: clock rate restore to %lu failed: %d current=%lu\n",
				initial_rate, ret, clk_get_rate(device->clock));
		return ret;
	}
	return 0;
}

static const struct rp1_gpclk_execution_ops rp1_gpclk_machine_ops = {
	.set_rate = rp1_gpclk_machine_set_rate,
	.prepare = rp1_gpclk_machine_prepare,
	.select_active = rp1_gpclk_machine_select_active,
	.readback = rp1_gpclk_machine_readback,
	.stop_tick = rp1_gpclk_machine_stop_tick,
	.terminate_dma = rp1_gpclk_machine_terminate_dma,
	.disable_clock = rp1_gpclk_machine_disable,
	.unprepare_clock = rp1_gpclk_machine_unprepare,
	.select_safe = rp1_gpclk_machine_select_safe,
	.restore_rate = rp1_gpclk_machine_restore_rate,
};

static int rp1_gpclk_set_enabled(struct rp1_gpclk_device *device, bool enabled)
{
	int ret;

	if (enabled == device->clock_enabled)
		return 0;
	if (enabled) {
		ret = clk_enable(device->clock);
		if (ret)
			return ret;
		device->clock_enabled = true;
	} else {
		clk_disable(device->clock);
		device->clock_enabled = false;
	}
	return 0;
}

static int rp1_gpclk_readback(struct rp1_gpclk_device *device,
			      __u32 *word, dma_addr_t word_dma,
			      __u32 expected)
{
	int ret;

	*word = 0;
	device->readback_expected = expected;
	ret = rp1_gpclk_configure_dma(device, word_dma, sizeof(*word),
				      DMA_DEV_TO_MEM);
	if (ret)
		return ret;
	ret = rp1_gpclk_wait_dma(device, NSEC_PER_MSEC);
	if (ret) {
		device->readback_observed = *word;
		return ret;
	}
	device->readback_observed = *word;
	return *word == expected ? 0 : -EIO;
}

static int rp1_gpclk_machine_readback(void *argument)
{
	struct rp1_gpclk_execution_context *context = argument;

	return rp1_gpclk_readback(context->device, context->word,
		context->word_dma, context->expected);
}

static int rp1_gpclk_sleep_or_stop(struct rp1_gpclk_device *device,
				   __u64 duration_ns)
{
	ktime_t interval = ns_to_ktime(duration_ns);

	set_current_state(TASK_INTERRUPTIBLE);
	if (!atomic_read(&device->stop_requested))
		schedule_hrtimeout(&interval, HRTIMER_MODE_REL);
	__set_current_state(TASK_RUNNING);
	return atomic_read(&device->stop_requested) ? -ECANCELED : 0;
}

static int rp1_gpclk_run_descriptor(struct rp1_gpclk_device *device,
				    struct rp1_gpclk_execution_context *context,
				    const struct rp1_gpclk_tone_v1 *tone,
				    __u32 *words, dma_addr_t words_dma,
				    size_t writes, __u64 duration_ns,
				    __u32 *expected)
{
	int ret;

	ret = rp1_gpclk_execution_fill_words(tone, words, writes);
	if (ret)
		return ret;
	*expected = words[writes - 1];
	ret = rp1_gpclk_configure_dma(device, words_dma,
				      writes * sizeof(*words), DMA_MEM_TO_DEV);
	if (ret)
		return ret;
	if (!device->pins_active_selected) {
		ret = rp1_gpclk_execution_machine_activate(
			&rp1_gpclk_machine_ops, context);
		if (ret) {
			dmaengine_terminate_sync(device->dma_chan);
			device->dma_submitted = false;
			return ret;
		}
	}
	ret = rp1_gpclk_set_enabled(device, true);
	if (ret) {
		dmaengine_terminate_sync(device->dma_chan);
		device->dma_submitted = false;
		return ret;
	}
	return rp1_gpclk_wait_dma(device, duration_ns);
}

static void rp1_gpclk_publish_failure(struct rp1_gpclk_device *device,
				      int error, bool cleanup_failed)
{
	__u32 reason = RP1_GPCLK_REASON_INTERNAL_ERROR;

	if (error == -ETIMEDOUT)
		reason = RP1_GPCLK_REASON_DEADLINE_MISSED;
	else if (error == -EBUSY)
		reason = RP1_GPCLK_REASON_STARTUP_CONFLICT;
	else if (error == -EIO)
		reason = RP1_GPCLK_REASON_DMA_FAILED;
	mutex_lock(&device->lock);
	if (cleanup_failed)
		rp1_gpclk_core_cleanup_failed(&device->core,
			device->execution_owner, device->execution_lease,
			device->execution_generation);
	else
		rp1_gpclk_core_fail(&device->core, device->execution_owner,
			device->execution_lease, device->execution_generation, reason);
	mutex_unlock(&device->lock);
}

static int rp1_gpclk_execution_thread(void *argument)
{
	struct rp1_gpclk_device *device = argument;
	struct rp1_gpclk_execution_plan *plan = device->execution_plan;
	struct device *dma_device = device->dma_chan->device->dev;
	dma_addr_t words_dma;
	__u32 *words;
	__u32 expected = 0;
	size_t maximum = 1;
	__u32 units;
	__u32 index;
	int cleanup_ret;
	int ret = 0;
	struct rp1_gpclk_execution_context context = {
		.device = device,
		.plan = plan,
	};

	if (atomic_read(&device->stop_requested))
		goto cancelled_before_buffer;
	if (plan->mode == RP1_GPCLK_MODE_WSPR) {
		maximum = plan->writes_per_symbol;
		units = plan->symbol_count;
	} else {
		units = plan->event_count;
		for (index = 0; index < units; index++) {
			size_t writes;

			if (!(plan->events[index].flags &
			      RP1_GPCLK_EVENT_F_OUTPUT_ENABLED))
				continue;
			if (rp1_gpclk_execution_event_writes(
				    plan->events[index].duration_ns, &writes)) {
				ret = -ERANGE;
				goto fail_without_buffer;
			}

			if (writes > maximum)
				maximum = writes;
		}
	}
	if (!maximum || maximum > SIZE_MAX / sizeof(*words)) {
		ret = -EOVERFLOW;
		goto fail_without_buffer;
	}
	words = dma_alloc_coherent(dma_device, maximum * sizeof(*words),
				   &words_dma, GFP_KERNEL);
	if (!words) {
		ret = -ENOMEM;
		goto fail_without_buffer;
	}
	context.word = words;
	context.word_dma = words_dma;
	WRITE_ONCE(device->execution_started_ns, ktime_get_boottime_ns());
	ret = rp1_gpclk_execution_machine_start(&rp1_gpclk_machine_ops,
		&context);
	if (ret)
		goto fail;

	for (index = 0; index < units; index++) {
		__u64 duration;
		size_t writes;
		__u32 tone_index;
		bool enabled = true;

		if (atomic_read(&device->stop_requested)) {
			ret = -ECANCELED;
			break;
		}
		if (plan->mode == RP1_GPCLK_MODE_WSPR) {
			duration = div_u64(plan->expected_frame_duration_ns,
					   plan->symbol_count);
			writes = plan->writes_per_symbol;
			tone_index = plan->symbols[index];
		} else {
			duration = plan->events[index].duration_ns;
			enabled = plan->events[index].flags &
				  RP1_GPCLK_EVENT_F_OUTPUT_ENABLED;
			tone_index = plan->events[index].tone_index;
			if (enabled) {
				ret = rp1_gpclk_execution_event_writes(duration,
							       &writes);
				if (ret)
					break;
			} else {
				writes = 0;
			}
		}
		if (!enabled) {
			ret = rp1_gpclk_set_enabled(device, false);
			if (!ret)
				ret = rp1_gpclk_machine_select_safe(&context);
			if (!ret)
				ret = rp1_gpclk_sleep_or_stop(device, duration);
		} else if (!writes) {
			ret = -ERANGE;
		} else {
			ret = rp1_gpclk_run_descriptor(device, &context,
				&plan->tones[tone_index], words, words_dma,
				writes, duration, &expected);
		}
		if (ret && ret != -ECANCELED)
			break;
		if (ret == -ECANCELED ||
		    atomic_read(&device->stop_requested)) {
			ret = -ECANCELED;
			break;
		}
		if (index + 1 != units) {
			mutex_lock(&device->lock);
			rp1_gpclk_core_progress(&device->core,
				device->execution_owner, device->execution_lease,
				device->execution_generation);
			mutex_unlock(&device->lock);
		}
	}

	context.expected = expected;
	cleanup_ret = rp1_gpclk_execution_machine_finish(
		&rp1_gpclk_machine_ops, &context, expected != 0);
	if (cleanup_ret) {
		ret = cleanup_ret;
		rp1_gpclk_publish_failure(device, ret, true);
	} else if (ret && ret != -ECANCELED) {
		rp1_gpclk_publish_failure(device, ret, false);
	} else {
		mutex_lock(&device->lock);
		rp1_gpclk_core_progress(&device->core, device->execution_owner,
			device->execution_lease, device->execution_generation);
		mutex_unlock(&device->lock);
	}
	WRITE_ONCE(device->execution_finished_ns, ktime_get_boottime_ns());
	dev_info(device->dev,
		 "phase4d generation=%llu mode=%u start_ns=%llu finish_ns=%llu expected_div_frac=0x%08x observed_div_frac=0x%08x tick_initial=%08x/%08x/%08x/%08x tick_final=%08x/%08x/%08x/%08x cleanup=%d result=%d\n",
		 device->execution_generation, plan->mode,
		 device->execution_started_ns, device->execution_finished_ns,
		 device->readback_expected, device->readback_observed,
		 device->initial_tick_dma0_ctrl, device->initial_tick_dma0_cycles,
		 device->initial_dma_tick0_en, device->initial_dma_tick0_ctrl,
		 readl(device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CTRL),
		 readl(device->tick_dma0 + RP1_GPCLK_TICKS_DMA0_CYCLES),
		 readl(device->dma_tick0 + RP1_GPCLK_DMA_TICK0_EN),
		 readl(device->dma_tick0 + RP1_GPCLK_DMA_TICK0_CTRL),
		 cleanup_ret, ret);
	dma_free_coherent(dma_device, maximum * sizeof(*words), words, words_dma);
	kfree_sensitive(plan);
	device->execution_plan = NULL;
	WRITE_ONCE(device->worker, NULL);
	complete_all(&device->execution_done);
	return 0;

fail:
	cleanup_ret = rp1_gpclk_execution_machine_finish(
		&rp1_gpclk_machine_ops, &context, false);
	dma_free_coherent(dma_device, maximum * sizeof(*words), words, words_dma);
	if (cleanup_ret)
		rp1_gpclk_publish_failure(device, cleanup_ret, true);
	else
		rp1_gpclk_publish_failure(device, ret, false);
	goto release_plan;

fail_without_buffer:
	rp1_gpclk_publish_failure(device, ret, false);
release_plan:
	kfree_sensitive(plan);
	device->execution_plan = NULL;
	WRITE_ONCE(device->worker, NULL);
	complete_all(&device->execution_done);
	return 0;

cancelled_before_buffer:
	mutex_lock(&device->lock);
	rp1_gpclk_core_progress(&device->core, device->execution_owner,
		device->execution_lease, device->execution_generation);
	mutex_unlock(&device->lock);
	goto release_plan;
}

int rp1_gpclk_execution_init(struct rp1_gpclk_device *device)
{
	if (!device)
		return -EINVAL;
	init_completion(&device->dma_done);
	init_completion(&device->execution_done);
	complete_all(&device->execution_done);
	atomic_set(&device->stop_requested, 0);
	return 0;
}

static int rp1_gpclk_start_thread(struct rp1_gpclk_device *device,
				  struct rp1_gpclk_execution_plan *plan,
				  __u64 owner, __u64 lease, __u64 generation)
{
	struct task_struct *worker;

	if (READ_ONCE(device->worker))
		return -EBUSY;
	device->execution_owner = owner;
	device->execution_lease = lease;
	device->execution_generation = generation;
	device->execution_started_ns = 0;
	device->execution_finished_ns = 0;
	device->readback_expected = 0;
	device->readback_observed = 0;
	device->tick_state_captured = false;
	device->execution_total_ns = plan->mode == RP1_GPCLK_MODE_WSPR ?
		plan->expected_frame_duration_ns : 0;
	if (plan->mode != RP1_GPCLK_MODE_WSPR) {
		__u32 index;

		for (index = 0; index < plan->event_count; index++)
			device->execution_total_ns += plan->events[index].duration_ns;
	}
	device->stop_reason = RP1_GPCLK_REASON_NONE;
	atomic_set(&device->stop_requested, 0);
	device->execution_plan = plan;
	reinit_completion(&device->execution_done);
	worker = kthread_create(rp1_gpclk_execution_thread, device,
				"rp1-gpclk/%llu", generation);
	if (IS_ERR(worker)) {
		device->execution_plan = NULL;
		complete_all(&device->execution_done);
		return PTR_ERR(worker);
	}
	WRITE_ONCE(device->worker, worker);
	return 0;
}

void rp1_gpclk_execution_activate(struct rp1_gpclk_device *device)
{
	struct task_struct *worker = READ_ONCE(device->worker);

	if (worker)
		wake_up_process(worker);
}

int rp1_gpclk_execution_submit_wspr(
	struct rp1_gpclk_device *device, __u64 owner,
	struct rp1_gpclk_submit_wspr_v1 *request,
	const struct rp1_gpclk_tone_v1 *tones, const unsigned char *symbols)
{
	struct rp1_gpclk_execution_plan *plan;
	int result;

	plan = kzalloc(sizeof(*plan), GFP_KERNEL);
	if (!plan)
		return -ENOMEM;
	if (rp1_gpclk_execution_tones_valid(tones, request->tone_count,
					    request->drive_ma)) {
		kfree(plan);
		return RP1_GPCLK_CORE_INVALID;
	}
	if (READ_ONCE(device->worker)) {
		kfree(plan);
		return RP1_GPCLK_CORE_BUSY;
	}
	result = rp1_gpclk_core_submit_wspr(&device->core, owner, request,
					    tones, symbols);
	if (result != RP1_GPCLK_CORE_OK) {
		kfree(plan);
		return result;
	}
	plan->mode = RP1_GPCLK_MODE_WSPR;
	plan->drive_ma = request->drive_ma;
	plan->tone_count = request->tone_count;
	plan->symbol_count = request->symbol_count;
	plan->writes_per_symbol = request->writes_per_symbol;
	plan->expected_frame_duration_ns = request->expected_frame_duration_ns;
	memcpy(plan->tones, tones, sizeof(*tones) * request->tone_count);
	memcpy(plan->symbols, symbols, request->symbol_count);
	result = rp1_gpclk_start_thread(device, plan, owner, request->lease_id,
					request->generation);
	if (result) {
		rp1_gpclk_core_fail(&device->core, owner, request->lease_id,
			request->generation, RP1_GPCLK_REASON_INTERNAL_ERROR);
		kfree(plan);
	}
	return result;
}

int rp1_gpclk_execution_submit_events(
	struct rp1_gpclk_device *device, __u64 owner,
	struct rp1_gpclk_submit_events_v1 *request,
	const struct rp1_gpclk_tone_v1 *tones,
	const struct rp1_gpclk_event_v1 *events)
{
	struct rp1_gpclk_execution_plan *plan;
	__u32 index;
	int result;

	plan = kzalloc(sizeof(*plan), GFP_KERNEL);
	if (!plan)
		return -ENOMEM;
	if (rp1_gpclk_execution_tones_valid(tones, request->tone_count,
					    request->drive_ma)) {
		kfree(plan);
		return RP1_GPCLK_CORE_INVALID;
	}
	for (index = 0; index < request->event_count; index++) {
		size_t writes;

		if ((events[index].flags & RP1_GPCLK_EVENT_F_OUTPUT_ENABLED) &&
		    rp1_gpclk_execution_event_writes(events[index].duration_ns,
						     &writes)) {
			kfree(plan);
			return RP1_GPCLK_CORE_INVALID;
		}
	}
	if (READ_ONCE(device->worker)) {
		kfree(plan);
		return RP1_GPCLK_CORE_BUSY;
	}
	result = rp1_gpclk_core_submit_events(&device->core, owner, request,
					      tones, events);
	if (result != RP1_GPCLK_CORE_OK) {
		kfree(plan);
		return result;
	}
	plan->mode = request->mode;
	plan->drive_ma = request->drive_ma;
	plan->tone_count = request->tone_count;
	plan->event_count = request->event_count;
	memcpy(plan->tones, tones, sizeof(*tones) * request->tone_count);
	memcpy(plan->events, events, sizeof(*events) * request->event_count);
	result = rp1_gpclk_start_thread(device, plan, owner, request->lease_id,
					request->generation);
	if (result) {
		rp1_gpclk_core_fail(&device->core, owner, request->lease_id,
			request->generation, RP1_GPCLK_REASON_INTERNAL_ERROR);
		kfree(plan);
	}
	return result;
}

int rp1_gpclk_execution_stop(struct rp1_gpclk_device *device, __u64 owner,
			     __u64 lease, __u64 generation, __u32 reason)
{
	int result;

	result = rp1_gpclk_core_stop(&device->core, owner, lease, generation);
	if (result != RP1_GPCLK_CORE_OK)
		return result;
	device->stop_reason = reason;
	atomic_set(&device->stop_requested, 1);
	if (READ_ONCE(device->worker))
		wake_up_process(device->worker);
	return RP1_GPCLK_CORE_OK;
}

void rp1_gpclk_execution_quiesce(struct rp1_gpclk_device *device,
				 __u32 reason)
{
	rp1_gpclk_execution_request_stop(device, reason);
	if (!wait_for_completion_timeout(&device->execution_done,
			msecs_to_jiffies(RP1_GPCLK_QUIESCE_TIMEOUT_MS))) {
		struct task_struct *worker;

		rp1_gpclk_tick_stop(device);
		dmaengine_terminate_sync(device->dma_chan);
		if (!wait_for_completion_timeout(&device->execution_done,
				msecs_to_jiffies(RP1_GPCLK_COMPLETION_SLACK_MS))) {
			dev_crit(device->dev,
				 "forced execution teardown after bounded drain failure\n");
			worker = READ_ONCE(device->worker);
			if (worker)
				kthread_stop(worker);
		}
	}
}

void rp1_gpclk_execution_request_stop(struct rp1_gpclk_device *device,
				      __u32 reason)
{
	device->stop_reason = reason;
	atomic_set(&device->stop_requested, 1);
	if (READ_ONCE(device->worker))
		wake_up_process(device->worker);
}
