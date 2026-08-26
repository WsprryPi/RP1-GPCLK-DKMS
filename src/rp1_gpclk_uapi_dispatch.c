// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>
#include <linux/fs.h>
#include <linux/ktime.h>
#include <linux/string.h>
#include <linux/uaccess.h>

#include "rp1_gpclk/compatibility.h"
#include "rp1_gpclk/device.h"
#include "rp1_gpclk/execution.h"
#include "rp1_gpclk/kernel_api.h"
#include "rp1_gpclk/uapi_dispatch.h"
#include "rp1_gpclk/version.h"

#define RP1_GPCLK_V1_CAPABILITIES \
	(RP1_GPCLK_CAP_SUBMIT_WSPR | RP1_GPCLK_CAP_SUBMIT_EVENTS | \
	 RP1_GPCLK_CAP_STOP_DRAIN | RP1_GPCLK_CAP_STABLE_STATE | \
	 RP1_GPCLK_CAP_ROUTE_IDENTITY | RP1_GPCLK_CAP_COMPAT_IDENTITY | \
	 RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH)

#define RP1_GPCLK_V2_CAPABILITIES \
	(RP1_GPCLK_V1_CAPABILITIES | RP1_GPCLK_CAP_TONE_CONTINUOUS | \
	 RP1_GPCLK_CAP_TONE_FINITE)

#define RP1_GPCLK_V3_CAPABILITIES \
	(RP1_GPCLK_V2_CAPABILITIES | RP1_GPCLK_CAP_PASSIVE_SNAPSHOT)

#define RP1_GPCLK_PHASE4A_INERT_CAPABILITIES \
	(RP1_GPCLK_CAP_ROUTE_IDENTITY | RP1_GPCLK_CAP_COMPAT_IDENTITY | \
	 RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH)

static bool rp1_gpclk_reserved_zero(const __u64 *reserved,
				    size_t count)
{
	size_t index;

	for (index = 0; index < count; index++) {
		if (reserved[index] != 0)
			return false;
	}
	return true;
}

static bool rp1_gpclk_header_valid(const struct rp1_gpclk_uapi_header *header,
				   size_t size)
{
	return header->size == size &&
		header->version == RP1_GPCLK_UAPI_ABI_V1 && header->flags == 0;
}

static bool rp1_gpclk_header_v2_valid(
	const struct rp1_gpclk_uapi_header *header, size_t size)
{
	return header->size == size &&
		header->version == RP1_GPCLK_UAPI_ABI_V2 && header->flags == 0;
}

static bool rp1_gpclk_header_v3_valid(
	const struct rp1_gpclk_uapi_header *header, size_t size)
{
	return header->size == size &&
		header->version == RP1_GPCLK_UAPI_ABI_V3 && header->flags == 0;
}

static long rp1_gpclk_core_error(int result)
{
	switch (result) {
	case RP1_GPCLK_CORE_OK:
		return 0;
	case RP1_GPCLK_CORE_INVALID:
		return -EINVAL;
	case RP1_GPCLK_CORE_BUSY:
		return -EBUSY;
	case RP1_GPCLK_CORE_STALE:
		return -ESTALE;
	case RP1_GPCLK_CORE_STATE:
		return -EALREADY;
	case RP1_GPCLK_CORE_FAULT:
		return -EIO;
	case RP1_GPCLK_CORE_LATCHED:
		return -EUCLEAN;
	default:
		return -EIO;
	}
}

static long rp1_gpclk_query(struct rp1_gpclk_file *context, void __user *user)
{
	struct rp1_gpclk_query_v1 request;
	__u32 route;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
		request.reserved0 != 0 || request.reserved1 != 0 ||
		!rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	mutex_lock(&context->device->lock);
	if (context->device->dead) {
		mutex_unlock(&context->device->lock);
		return -ENODEV;
	}
	route = context->device->route;
	mutex_unlock(&context->device->lock);
	memset(&request, 0, sizeof(request));
	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V1;
	request.abi_min = RP1_GPCLK_UAPI_ABI_V1;
	request.abi_max = RP1_GPCLK_UAPI_ABI_V1;
	request.route = route;
	request.compatibility_state =
		RP1_GPCLK_COMPAT_COMPATIBLE_UNQUALIFIED;
	request.compatibility_reason =
		RP1_GPCLK_COMPAT_REASON_ADMIN_ENROLLMENT_REQUIRED;
	request.capabilities = RP1_GPCLK_V1_CAPABILITIES;
	if (rp1_gpclk_live_output_eligible(context->device))
		request.capabilities |= RP1_GPCLK_CAP_LIVE_ELIGIBLE;
	if (rp1_gpclk_live_output_eligible(context->device))
		request.compatibility_state = RP1_GPCLK_COMPAT_EXPERIMENTAL;
	request.max_tones = RP1_GPCLK_MAX_TONES;
	request.wspr_symbols = RP1_GPCLK_WSPR_SYMBOLS;
	request.max_events = RP1_GPCLK_MAX_EVENTS;
	request.max_dither_period = RP1_GPCLK_DITHER_PERIOD_MAX;
	request.supported_drive_ma_mask = RP1_GPCLK_DRIVE_SUPPORT_2_MA;
	request.max_event_duration_ns = RP1_GPCLK_EVENT_DURATION_NS_MAX;
	request.max_request_duration_ns = RP1_GPCLK_REQUEST_DURATION_NS_MAX;
	strscpy(request.module_id, "rp1-gpclk-dkms", sizeof(request.module_id));
	strscpy(request.build_id, RP1_GPCLK_MODULE_VERSION,
		sizeof(request.build_id));
	strscpy(request.compatibility_id, rp1_gpclk_route_candidate_id(route),
		sizeof(request.compatibility_id));
	if (copy_to_user(user, &request, sizeof(request)))
		return -EFAULT;
	return 0;
}

static long rp1_gpclk_query_v2(struct rp1_gpclk_file *context, void __user *user)
{
	struct rp1_gpclk_query_v2 request;
	__u32 route;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_v2_valid(&request.header, sizeof(request)) ||
	    request.reserved0 || request.reserved1 ||
	    !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	mutex_lock(&context->device->lock);
	if (context->device->dead) {
		mutex_unlock(&context->device->lock);
		return -ENODEV;
	}
	route = context->device->route;
	mutex_unlock(&context->device->lock);
	memset(&request, 0, sizeof(request));
	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V2;
	request.abi_min = RP1_GPCLK_UAPI_ABI_V1;
	request.abi_max = RP1_GPCLK_UAPI_ABI_V2;
	request.route = route;
	request.compatibility_state = RP1_GPCLK_COMPAT_COMPATIBLE_UNQUALIFIED;
	request.compatibility_reason = RP1_GPCLK_COMPAT_REASON_ADMIN_ENROLLMENT_REQUIRED;
	request.capabilities = RP1_GPCLK_V2_CAPABILITIES;
	if (rp1_gpclk_live_output_eligible(context->device)) {
		request.capabilities |= RP1_GPCLK_CAP_LIVE_ELIGIBLE;
		request.compatibility_state = RP1_GPCLK_COMPAT_EXPERIMENTAL;
	}
	request.max_tones = RP1_GPCLK_MAX_TONES;
	request.wspr_symbols = RP1_GPCLK_WSPR_SYMBOLS;
	request.max_events = RP1_GPCLK_MAX_EVENTS;
	request.max_dither_period = RP1_GPCLK_DITHER_PERIOD_MAX;
	request.supported_drive_ma_mask = RP1_GPCLK_DRIVE_SUPPORT_2_MA;
	request.max_event_duration_ns = RP1_GPCLK_EVENT_DURATION_NS_MAX;
	request.max_request_duration_ns = RP1_GPCLK_REQUEST_DURATION_NS_MAX;
	request.min_tone_duration_ns = RP1_GPCLK_TONE_DURATION_NS_MIN;
	request.max_tone_duration_ns = RP1_GPCLK_TONE_DURATION_NS_MAX;
	strscpy(request.module_id, "rp1-gpclk-dkms", sizeof(request.module_id));
	strscpy(request.build_id, RP1_GPCLK_MODULE_VERSION, sizeof(request.build_id));
	strscpy(request.compatibility_id, rp1_gpclk_route_candidate_id(route),
		sizeof(request.compatibility_id));
	if (copy_to_user(user, &request, sizeof(request)))
		return -EFAULT;
	return 0;
}

static long rp1_gpclk_acquire(struct rp1_gpclk_file *context, void __user *user)
{
	struct rp1_gpclk_acquire_v1 request;
	__u64 available = RP1_GPCLK_V2_CAPABILITIES;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
		request.reserved0 != 0 ||
		!rp1_gpclk_reserved_zero(request.reserved, 4) ||
		request.lease_id != 0 ||
		(request.required_capabilities &
		 ~(available | (rp1_gpclk_live_output_eligible(context->device) ?
		 RP1_GPCLK_CAP_LIVE_ELIGIBLE : 0))) != 0)
		return -EINVAL;
	mutex_lock(&context->device->lock);
	if (context->device->dead) {
		mutex_unlock(&context->device->lock);
		return -ENODEV;
	}
	if (request.expected_route != context->device->route) {
		mutex_unlock(&context->device->lock);
		return -EINVAL;
	}
	result = rp1_gpclk_core_acquire(&context->device->core,
		context->owner, request.expected_route,
		request.required_capabilities, &request.lease_id);
	mutex_unlock(&context->device->lock);
	if (result != RP1_GPCLK_CORE_OK)
		return rp1_gpclk_core_error(result);
	if (copy_to_user(user, &request, sizeof(request))) {
		mutex_lock(&context->device->lock);
		rp1_gpclk_core_release(&context->device->core, context->owner,
			request.lease_id);
		mutex_unlock(&context->device->lock);
		return -EFAULT;
	}
	return 0;
}

static long rp1_gpclk_execution_error(int result)
{
	if (result <= RP1_GPCLK_CORE_OK &&
	    result >= RP1_GPCLK_CORE_LATCHED)
		return rp1_gpclk_core_error(result);
	return result;
}

static long rp1_gpclk_submit_wspr(struct rp1_gpclk_file *context,
				  void __user *user)
{
	struct rp1_gpclk_submit_wspr_v1 request;
	struct rp1_gpclk_tone_v1 *tones;
	unsigned char *symbols;
	long result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
	    request.reserved0 != 0 || request.reserved1 != 0 ||
	    !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	if (!rp1_gpclk_live_output_eligible(context->device))
		return -EACCES;
	if (request.tone_count != RP1_GPCLK_MAX_TONES ||
	    request.symbol_count != RP1_GPCLK_WSPR_SYMBOLS)
		return -EINVAL;
	tones = memdup_user(u64_to_user_ptr(request.tones_ptr),
			   sizeof(*tones) * request.tone_count);
	if (IS_ERR(tones))
		return PTR_ERR(tones);
	symbols = memdup_user(u64_to_user_ptr(request.symbols_ptr),
			     request.symbol_count);
	if (IS_ERR(symbols)) {
		result = PTR_ERR(symbols);
		goto free_tones;
	}
	mutex_lock(&context->device->lock);
	if (context->device->dead)
		result = -ENODEV;
	else
		result = rp1_gpclk_execution_submit_wspr(context->device,
			context->owner, &request, tones, symbols);
	mutex_unlock(&context->device->lock);
	if (!result && copy_to_user(user, &request, sizeof(request))) {
		mutex_lock(&context->device->lock);
		rp1_gpclk_execution_stop(context->device, context->owner,
			request.lease_id, request.generation,
			RP1_GPCLK_REASON_STOPPED);
		mutex_unlock(&context->device->lock);
		result = -EFAULT;
	} else {
		result = rp1_gpclk_execution_error(result);
	}
	if (!result)
		rp1_gpclk_execution_activate(context->device);
	kfree(symbols);
free_tones:
	kfree(tones);
	return result;
}

static long rp1_gpclk_submit_events(struct rp1_gpclk_file *context,
				    void __user *user)
{
	struct rp1_gpclk_submit_events_v1 request;
	struct rp1_gpclk_tone_v1 *tones;
	struct rp1_gpclk_event_v1 *events;
	long result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
	    request.reserved0 != 0 || request.reserved1 != 0 ||
	    !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	if (!rp1_gpclk_live_output_eligible(context->device))
		return -EACCES;
	if (!request.tone_count || request.tone_count > RP1_GPCLK_MAX_TONES ||
	    !request.event_count || request.event_count > RP1_GPCLK_MAX_EVENTS)
		return -EINVAL;
	tones = memdup_user(u64_to_user_ptr(request.tones_ptr),
			   sizeof(*tones) * request.tone_count);
	if (IS_ERR(tones))
		return PTR_ERR(tones);
	events = memdup_user(u64_to_user_ptr(request.events_ptr),
			    sizeof(*events) * request.event_count);
	if (IS_ERR(events)) {
		result = PTR_ERR(events);
		goto free_tones;
	}
	mutex_lock(&context->device->lock);
	if (context->device->dead)
		result = -ENODEV;
	else
		result = rp1_gpclk_execution_submit_events(context->device,
			context->owner, &request, tones, events);
	mutex_unlock(&context->device->lock);
	if (!result && copy_to_user(user, &request, sizeof(request))) {
		mutex_lock(&context->device->lock);
		rp1_gpclk_execution_stop(context->device, context->owner,
			request.lease_id, request.generation,
			RP1_GPCLK_REASON_STOPPED);
		mutex_unlock(&context->device->lock);
		result = -EFAULT;
	} else {
		result = rp1_gpclk_execution_error(result);
	}
	if (!result)
		rp1_gpclk_execution_activate(context->device);
	kfree(events);
free_tones:
	kfree(tones);
	return result;
}

static long rp1_gpclk_submit_tone_v2(struct rp1_gpclk_file *context,
				     void __user *user)
{
	struct rp1_gpclk_submit_tone_v2 request;
	long result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_v2_valid(&request.header, sizeof(request)) ||
	    request.reserved0 || !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	if (!rp1_gpclk_live_output_eligible(context->device))
		return -EACCES;
	mutex_lock(&context->device->lock);
	if (context->device->dead)
		result = -ENODEV;
	else
		result = rp1_gpclk_execution_submit_tone(context->device,
			context->owner, &request);
	mutex_unlock(&context->device->lock);
	if (!result && copy_to_user(user, &request, sizeof(request))) {
		mutex_lock(&context->device->lock);
		rp1_gpclk_execution_stop(context->device, context->owner,
			request.lease_id, request.generation, RP1_GPCLK_REASON_STOPPED);
		mutex_unlock(&context->device->lock);
		result = -EFAULT;
	} else {
		result = rp1_gpclk_execution_error(result);
	}
	if (!result)
		rp1_gpclk_execution_activate(context->device);
	return result;
}

static long rp1_gpclk_stop(struct rp1_gpclk_file *context, void __user *user)
{
	struct rp1_gpclk_stop_v1 request;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
	    !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	mutex_lock(&context->device->lock);
	result = context->device->dead ? -ENODEV :
		rp1_gpclk_execution_stop(context->device, context->owner,
			request.lease_id, request.generation,
			RP1_GPCLK_REASON_STOPPED);
	mutex_unlock(&context->device->lock);
	return rp1_gpclk_execution_error(result);
}

static long rp1_gpclk_get_state(struct rp1_gpclk_file *context,
				void __user *user)
{
	struct rp1_gpclk_state_v1 request;
	struct rp1_gpclk_core_snapshot snapshot;
	__u64 elapsed = 0;
	__u64 remaining = 0;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
	    !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	mutex_lock(&context->device->lock);
	result = rp1_gpclk_core_get_state(&context->device->core,
		context->owner, request.lease_id, request.generation, &snapshot);
	if (result == RP1_GPCLK_CORE_OK &&
	    context->device->execution_started_ns) {
		__u64 now = ktime_get_boottime_ns();

		elapsed = now > context->device->execution_started_ns ?
			now - context->device->execution_started_ns : 0;
		if (elapsed > context->device->execution_total_ns)
			elapsed = context->device->execution_total_ns;
		remaining = context->device->execution_total_ns - elapsed;
	}
	mutex_unlock(&context->device->lock);
	if (result != RP1_GPCLK_CORE_OK)
		return rp1_gpclk_core_error(result);
	memset(&request, 0, sizeof(request));
	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V1;
	request.lease_id = snapshot.lease_id;
	request.generation = snapshot.generation;
	request.state = snapshot.state;
	request.terminal_reason = snapshot.terminal_reason;
	request.current_event = snapshot.completed_units;
	request.cleanup_fault = snapshot.cleanup_fault;
	request.elapsed_ns = elapsed;
	request.remaining_ns = remaining;
	if (copy_to_user(user, &request, sizeof(request)))
		return -EFAULT;
	return 0;
}

static __u32 rp1_gpclk_observe_quiescent(bool active, bool settled)
{
	if (active)
		return RP1_GPCLK_OBSERVATION_FALSE;
	return settled ? RP1_GPCLK_OBSERVATION_TRUE :
		RP1_GPCLK_OBSERVATION_UNKNOWN;
}

static long rp1_gpclk_get_snapshot_v3(struct rp1_gpclk_file *context,
				      void __user *user)
{
	struct rp1_gpclk_snapshot_v3 request;
	struct rp1_gpclk_core_snapshot core;
	struct rp1_gpclk_device *device = context->device;
	bool settled;
	bool terminal;
	__u64 elapsed = 0;
	__u64 remaining = 0;
	__u32 flags = 0;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_v3_valid(&request.header, sizeof(request)) ||
	    request.reserved0 ||
	    !rp1_gpclk_reserved_zero(request.reserved, 8))
		return -EINVAL;

	mutex_lock(&device->lock);
	if (device->dead) {
		mutex_unlock(&device->lock);
		return -ENODEV;
	}
	result = rp1_gpclk_core_get_public_state(&device->core, &core);
	if (result != RP1_GPCLK_CORE_OK) {
		mutex_unlock(&device->lock);
		return rp1_gpclk_core_error(result);
	}
	settled = completion_done(&device->execution_done) &&
		!READ_ONCE(device->worker) && !device->execution_plan;
	terminal = core.state == RP1_GPCLK_STATE_COMPLETE ||
		core.state == RP1_GPCLK_STATE_FAILED ||
		core.state == RP1_GPCLK_STATE_DEAD;
	if (core.generation) {
		flags |= RP1_GPCLK_SNAPSHOT_F_CURRENT_EVENT_VALID;
		if (device->execution_started_ns) {
			__u64 end = terminal && device->execution_finished_ns ?
				device->execution_finished_ns : ktime_get_boottime_ns();

			elapsed = end > device->execution_started_ns ?
				end - device->execution_started_ns : 0;
			if (device->execution_total_ns &&
			    elapsed > device->execution_total_ns)
				elapsed = device->execution_total_ns;
			flags |= RP1_GPCLK_SNAPSHOT_F_ELAPSED_VALID;
			if (device->execution_total_ns) {
				remaining = terminal ? 0 :
					device->execution_total_ns - elapsed;
				flags |= RP1_GPCLK_SNAPSHOT_F_REMAINING_VALID;
			}
		}
	}

	memset(&request, 0, sizeof(request));
	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V3;
	request.abi_min = RP1_GPCLK_UAPI_ABI_V1;
	request.abi_max = RP1_GPCLK_UAPI_ABI_V3;
	request.route = device->route;
	request.compatibility_state = device->live_eligible ?
		RP1_GPCLK_COMPAT_EXPERIMENTAL :
		RP1_GPCLK_COMPAT_COMPATIBLE_UNQUALIFIED;
	request.compatibility_reason = device->live_eligible ?
		RP1_GPCLK_COMPAT_REASON_NONE :
		RP1_GPCLK_COMPAT_REASON_ADMIN_ENROLLMENT_REQUIRED;
	request.operation_state = core.state;
	request.terminal_reason = core.terminal_reason;
	request.current_event = core.completed_units;
	request.snapshot_flags = flags;
	request.cleanup_fault = core.cleanup_fault ?
		RP1_GPCLK_OBSERVATION_TRUE : RP1_GPCLK_OBSERVATION_FALSE;
	request.owner_present = core.owner_id ?
		RP1_GPCLK_OBSERVATION_TRUE : RP1_GPCLK_OBSERVATION_FALSE;
	request.lease_present = core.lease_id ?
		RP1_GPCLK_OBSERVATION_TRUE : RP1_GPCLK_OBSERVATION_FALSE;
	request.live_output = rp1_gpclk_live_output_enabled() ?
		RP1_GPCLK_OBSERVATION_TRUE : RP1_GPCLK_OBSERVATION_FALSE;
	request.live_eligible = device->live_eligible ?
		RP1_GPCLK_OBSERVATION_TRUE : RP1_GPCLK_OBSERVATION_FALSE;
	if (core.state == RP1_GPCLK_STATE_DRAINING)
		request.drain_state = RP1_GPCLK_DRAIN_ACTIVE;
	else if (terminal &&
		 (core.terminal_reason == RP1_GPCLK_REASON_STOPPED ||
		  core.terminal_reason == RP1_GPCLK_REASON_OWNER_CLOSED))
		request.drain_state = RP1_GPCLK_DRAIN_COMPLETE;
	else
		request.drain_state = RP1_GPCLK_DRAIN_NONE;
	request.gpio_safe = rp1_gpclk_observe_quiescent(
		device->pins_active_selected, settled);
	request.clock_quiescent = rp1_gpclk_observe_quiescent(
		device->clock_prepared || device->clock_enabled, settled);
	request.dma_quiescent = rp1_gpclk_observe_quiescent(
		device->dma_submitted || device->tick_state_captured, settled);
	request.stable = ((core.state == RP1_GPCLK_STATE_IDLE || terminal) &&
		settled && !core.cleanup_fault &&
		request.gpio_safe == RP1_GPCLK_OBSERVATION_TRUE &&
		request.clock_quiescent == RP1_GPCLK_OBSERVATION_TRUE &&
		request.dma_quiescent == RP1_GPCLK_OBSERVATION_TRUE) ?
		RP1_GPCLK_OBSERVATION_TRUE : RP1_GPCLK_OBSERVATION_FALSE;
	request.capabilities = RP1_GPCLK_V3_CAPABILITIES;
	if (device->live_eligible)
		request.capabilities |= RP1_GPCLK_CAP_LIVE_ELIGIBLE;
	request.generation = core.generation;
	request.elapsed_ns = elapsed;
	request.remaining_ns = remaining;
	request.min_tone_duration_ns = RP1_GPCLK_TONE_DURATION_NS_MIN;
	request.max_tone_duration_ns = RP1_GPCLK_TONE_DURATION_NS_MAX;
	strscpy(request.module_id, "rp1-gpclk-dkms",
		sizeof(request.module_id));
	strscpy(request.build_id, RP1_GPCLK_MODULE_VERSION,
		sizeof(request.build_id));
	strscpy(request.compatibility_id,
		rp1_gpclk_route_candidate_id(device->route),
		sizeof(request.compatibility_id));
	mutex_unlock(&device->lock);

	if (copy_to_user(user, &request, sizeof(request)))
		return -EFAULT;
	return 0;
}

static long rp1_gpclk_release_v2(struct rp1_gpclk_file *context,
				 void __user *user)
{
	struct rp1_gpclk_release_v2 request;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_v2_valid(&request.header, sizeof(request)) ||
	    !rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	mutex_lock(&context->device->lock);
	result = context->device->dead ? -ENODEV :
		rp1_gpclk_execution_stop(context->device, context->owner,
			request.lease_id, request.generation,
			RP1_GPCLK_REASON_STOPPED);
	mutex_unlock(&context->device->lock);
	if (result != RP1_GPCLK_CORE_OK &&
	    !(result == RP1_GPCLK_CORE_STATE &&
	      completion_done(&context->device->execution_done)))
		return rp1_gpclk_execution_error(result);
	if (result == RP1_GPCLK_CORE_OK) {
		long waited = wait_for_completion_interruptible_timeout(
			&context->device->execution_done, msecs_to_jiffies(2000));

		if (waited < 0)
			return waited;
		if (waited == 0)
			return -ETIMEDOUT;
	}
	mutex_lock(&context->device->lock);
	result = rp1_gpclk_core_release(&context->device->core, context->owner,
		request.lease_id);
	mutex_unlock(&context->device->lock);
	return rp1_gpclk_core_error(result);
}

static long rp1_gpclk_release_lease(struct rp1_gpclk_file *context,
				    void __user *user)
{
	struct rp1_gpclk_release_v1 request;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
		!rp1_gpclk_reserved_zero(request.reserved, 4))
		return -EINVAL;
	mutex_lock(&context->device->lock);
	result = rp1_gpclk_core_release(&context->device->core, context->owner,
		request.lease_id);
	mutex_unlock(&context->device->lock);
	return rp1_gpclk_core_error(result);
}

long rp1_gpclk_uapi_dispatch(struct file *file, unsigned int command,
			    unsigned long argument)
{
	struct rp1_gpclk_file *context = file->private_data;
	void __user *user = (void __user *)argument;

	switch (command) {
	case RP1_GPCLK_IOC_GET_SNAPSHOT_V3:
		return rp1_gpclk_get_snapshot_v3(context, user);
	case RP1_GPCLK_IOC_QUERY_V2:
		return rp1_gpclk_query_v2(context, user);
	case RP1_GPCLK_IOC_SUBMIT_TONE_V2:
		return rp1_gpclk_submit_tone_v2(context, user);
	case RP1_GPCLK_IOC_RELEASE_V2:
		return rp1_gpclk_release_v2(context, user);
	case RP1_GPCLK_IOC_QUERY:
		return rp1_gpclk_query(context, user);
	case RP1_GPCLK_IOC_ACQUIRE:
		return rp1_gpclk_acquire(context, user);
	case RP1_GPCLK_IOC_RELEASE:
		return rp1_gpclk_release_lease(context, user);
	case RP1_GPCLK_IOC_SUBMIT_WSPR:
		return rp1_gpclk_submit_wspr(context, user);
	case RP1_GPCLK_IOC_SUBMIT_EVENTS:
		return rp1_gpclk_submit_events(context, user);
	case RP1_GPCLK_IOC_STOP:
		return rp1_gpclk_stop(context, user);
	case RP1_GPCLK_IOC_GET_STATE:
		return rp1_gpclk_get_state(context, user);
	default:
		return -EOPNOTSUPP;
	}
}
