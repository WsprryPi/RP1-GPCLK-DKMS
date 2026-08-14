// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/errno.h>
#include <linux/fs.h>
#include <linux/string.h>
#include <linux/uaccess.h>

#include "rp1_gpclk/device.h"
#include "rp1_gpclk/uapi_dispatch.h"
#include "rp1_gpclk/version.h"

#define RP1_GPCLK_PHASE2E_CAPABILITIES \
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
	request.capabilities = RP1_GPCLK_PHASE2E_CAPABILITIES;
	strscpy(request.module_id, "rp1-gpclk-dkms", sizeof(request.module_id));
	strscpy(request.build_id, RP1_GPCLK_MODULE_VERSION,
		sizeof(request.build_id));
	strscpy(request.compatibility_id, "phase3b-clock-disabled",
		sizeof(request.compatibility_id));
	if (copy_to_user(user, &request, sizeof(request)))
		return -EFAULT;
	return 0;
}

static long rp1_gpclk_acquire(struct rp1_gpclk_file *context, void __user *user)
{
	struct rp1_gpclk_acquire_v1 request;
	int result;

	if (copy_from_user(&request, user, sizeof(request)))
		return -EFAULT;
	if (!rp1_gpclk_header_valid(&request.header, sizeof(request)) ||
		request.reserved0 != 0 ||
		!rp1_gpclk_reserved_zero(request.reserved, 4) ||
		request.lease_id != 0 ||
		(request.required_capabilities & ~RP1_GPCLK_PHASE2E_CAPABILITIES) != 0)
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
	default:
		return -EOPNOTSUPP;
	}
}
