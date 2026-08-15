// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>
#include <linux/fs.h>
#include <linux/ktime.h>
#include <linux/string.h>
#include <linux/uaccess.h>

#include "rp1_gpclk/device.h"
#include "rp1_gpclk/execution.h"
#include "rp1_gpclk/kernel_api.h"
#include "rp1_gpclk/uapi_dispatch.h"
#include "rp1_gpclk/version.h"

#define RP1_GPCLK_PHASE4A_CAPABILITIES \
	(RP1_GPCLK_CAP_SUBMIT_WSPR | RP1_GPCLK_CAP_SUBMIT_EVENTS | \
	 RP1_GPCLK_CAP_STOP_DRAIN | RP1_GPCLK_CAP_STABLE_STATE | \
	 RP1_GPCLK_CAP_ROUTE_IDENTITY | RP1_GPCLK_CAP_COMPAT_IDENTITY | \
	 RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH)

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
	request.capabilities = RP1_GPCLK_PHASE4A_CAPABILITIES;
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
	strscpy(request.compatibility_id, "phase4b-wspr5-gpio4-6.18.34",
		sizeof(request.compatibility_id));
	if (copy_to_user(user, &request, sizeof(request)))
		return -EFAULT;
	return 0;
}

static long rp1_gpclk_acquire(struct rp1_gpclk_file *context, void __user *user)
{
	struct rp1_gpclk_acquire_v1 request;
	__u64 available = RP1_GPCLK_PHASE4A_CAPABILITIES;
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
