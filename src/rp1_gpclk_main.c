// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/atomic.h>
#include <linux/fs.h>
#include <linux/limits.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/of_fdt.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include <linux/utsname.h>

#include "rp1_gpclk/device.h"
#include "rp1_gpclk/execution.h"
#include "rp1_gpclk/kernel_api.h"
#include "rp1_gpclk/lifetime.h"
#include "rp1_gpclk/uapi_dispatch.h"
#include "rp1_gpclk/version.h"

static bool live_output;
module_param(live_output, bool, 0444);
MODULE_PARM_DESC(live_output,
	"Permit live GPCLK output for an exactly qualified compatibility identity");

bool rp1_gpclk_live_output_enabled(void)
{
	return live_output;
}

bool rp1_gpclk_live_output_eligible(const struct rp1_gpclk_device *device)
{
	return live_output && device && device->live_eligible;
}

static bool rp1_gpclk_phase4d_identity_allowed(
	const struct rp1_gpclk_device *device)
{
	return (device->route == RP1_GPCLK_ROUTE_GPIO4 ||
		device->route == RP1_GPCLK_ROUTE_GPIO20) &&
		!strcmp(utsname()->release, "6.18.34+rpt-rpi-2712") &&
		of_machine_is_compatible("raspberrypi,5-model-b");
}

static atomic64_t rp1_gpclk_next_owner = ATOMIC64_INIT(0);
static atomic_t rp1_gpclk_endpoint_owner = ATOMIC_INIT(0);

static int rp1_gpclk_endpoint_claim(struct rp1_gpclk_device *device)
{
	if (atomic_cmpxchg(&rp1_gpclk_endpoint_owner, 0, 1) != 0)
		return -EBUSY;
	device->endpoint_claimed = true;
	return 0;
}

static void rp1_gpclk_endpoint_release(struct rp1_gpclk_device *device)
{
	if (!device->endpoint_claimed)
		return;
	device->endpoint_claimed = false;
	atomic_set_release(&rp1_gpclk_endpoint_owner, 0);
}

static int rp1_gpclk_allocate_owner(u64 *owner)
{
	s64 owner_sequence;

	for (;;) {
		owner_sequence = atomic64_read(&rp1_gpclk_next_owner);
		if (owner_sequence == S64_MAX)
			return -EOVERFLOW;
		if (atomic64_cmpxchg(&rp1_gpclk_next_owner, owner_sequence,
				     owner_sequence + 1) == owner_sequence) {
			*owner = (u64)(owner_sequence + 1);
			return 0;
		}
	}
}

static int rp1_gpclk_open(struct inode *inode, struct file *file)
{
	struct miscdevice *miscdev = file->private_data;
	struct rp1_gpclk_device *device =
		container_of(miscdev, struct rp1_gpclk_device, miscdev);
	struct rp1_gpclk_file *context;
	int ret;

	if (!rp1_gpclk_lifetime_get_live(device))
		return -ENODEV;
	context = kzalloc(sizeof(*context), GFP_KERNEL);
	if (!context) {
		rp1_gpclk_lifetime_put(device);
		return -ENOMEM;
	}
	context->device = device;
	ret = rp1_gpclk_allocate_owner(&context->owner);
	if (ret) {
		kfree(context);
		rp1_gpclk_lifetime_put(device);
		return ret;
	}
	file->private_data = context;
	return nonseekable_open(inode, file);
}

static int rp1_gpclk_release(struct inode *inode, struct file *file)
{
	struct rp1_gpclk_file *context = file->private_data;

	mutex_lock(&context->device->lock);
	if (rp1_gpclk_core_owner_close(&context->device->core,
					context->owner) == RP1_GPCLK_CORE_OK)
		rp1_gpclk_execution_request_stop(context->device,
			RP1_GPCLK_REASON_OWNER_CLOSED);
	mutex_unlock(&context->device->lock);
	rp1_gpclk_lifetime_put(context->device);
	kfree(context);
	return 0;
}

static long rp1_gpclk_ioctl(struct file *file, unsigned int command,
			    unsigned long argument)
{
	return rp1_gpclk_uapi_dispatch(file, command, argument);
}

static const struct file_operations rp1_gpclk_fops = {
	.owner = THIS_MODULE,
	.open = rp1_gpclk_open,
	.release = rp1_gpclk_release,
	.unlocked_ioctl = rp1_gpclk_ioctl,
};

static int rp1_gpclk_probe(struct platform_device *pdev)
{
	struct rp1_gpclk_device *device;
	int ret;

	device = kzalloc(sizeof(*device), GFP_KERNEL);
	if (!device)
		return -ENOMEM;
	device->dev = &pdev->dev;
	ret = rp1_gpclk_lifetime_init(device);
	if (ret)
		goto free_device;
	rp1_gpclk_core_init(&device->core);
	ret = rp1_gpclk_execution_init(device);
	if (ret)
		goto put_device;
	ret = rp1_gpclk_dt_validate(device);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "device-tree identity validation failed\n");
		goto put_device;
	}
	ret = rp1_gpclk_endpoint_claim(device);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "endpoint resource ownership conflict\n");
		goto put_device;
	}
	ret = rp1_gpclk_clock_acquire(device);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "clock resource acquisition failed\n");
		goto release_resources;
	}
	ret = rp1_gpclk_pinctrl_acquire(device);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "pinctrl resource acquisition failed\n");
		goto release_resources;
	}
	ret = rp1_gpclk_tick_resources_acquire(pdev, device);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "DMA-tick resource acquisition failed\n");
		goto release_resources;
	}
	ret = rp1_gpclk_dma_acquire(device);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "DMA resource acquisition failed\n");
		goto release_resources;
	}
	device->live_eligible = rp1_gpclk_phase4d_identity_allowed(device);
	if (live_output && !device->live_eligible) {
		ret = -EOPNOTSUPP;
		dev_err_probe(&pdev->dev, ret,
			      "live output rejected by exact Phase 4D compatibility allowlist\n");
		goto release_resources;
	}

	device->miscdev.minor = MISC_DYNAMIC_MINOR;
	device->miscdev.name = "rp1-gpclk";
	device->miscdev.fops = &rp1_gpclk_fops;
	device->miscdev.parent = &pdev->dev;
	device->miscdev.mode = 0600;
	ret = misc_register(&device->miscdev);
	if (ret) {
		dev_err_probe(&pdev->dev, ret,
			      "misc-device registration failed\n");
		goto release_resources;
	}
	device->misc_registered = true;
	platform_set_drvdata(pdev, device);
	return 0;

release_resources:
	rp1_gpclk_resources_release(device);
	rp1_gpclk_endpoint_release(device);
put_device:
	rp1_gpclk_lifetime_mark_dead(device);
	rp1_gpclk_lifetime_put(device);
	return ret;
free_device:
	kfree(device);
	return ret;
}

static void rp1_gpclk_remove(struct platform_device *pdev)
{
	struct rp1_gpclk_device *device = platform_get_drvdata(pdev);

	if (!device)
		return;
	if (device->misc_registered) {
		misc_deregister(&device->miscdev);
		device->misc_registered = false;
	}
	rp1_gpclk_lifetime_mark_dead(device);
	mutex_lock(&device->lock);
	rp1_gpclk_core_mark_dead(&device->core,
				 RP1_GPCLK_REASON_PROVIDER_REMOVED);
	mutex_unlock(&device->lock);
	rp1_gpclk_execution_quiesce(device,
				    RP1_GPCLK_REASON_PROVIDER_REMOVED);
	rp1_gpclk_quiesce(device);
	rp1_gpclk_resources_release(device);
	rp1_gpclk_endpoint_release(device);
	platform_set_drvdata(pdev, NULL);
	rp1_gpclk_lifetime_put(device);
}

static const struct of_device_id rp1_gpclk_of_match[] = {
	{ .compatible = "wsprrypi,rp1-gpclk-dkms-v1" },
	{ }
};
MODULE_DEVICE_TABLE(of, rp1_gpclk_of_match);

static struct platform_driver rp1_gpclk_driver = {
	.probe = rp1_gpclk_probe,
	.remove = rp1_gpclk_remove,
	.driver = {
		.name = "rp1-gpclk-dkms",
		.of_match_table = rp1_gpclk_of_match,
	},
};

module_platform_driver(rp1_gpclk_driver);

MODULE_AUTHOR("Lee Bussy");
MODULE_DESCRIPTION("Experimental RP1 GPCLK controlled-output provider");
MODULE_LICENSE("Dual MIT/GPL");
MODULE_VERSION(RP1_GPCLK_MODULE_VERSION);
