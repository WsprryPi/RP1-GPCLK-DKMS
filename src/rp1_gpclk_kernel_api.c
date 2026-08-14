// SPDX-License-Identifier: GPL-2.0-only OR MIT
#include <linux/clk.h>
#include <linux/dma-mapping.h>
#include <linux/dmaengine.h>
#include <linux/err.h>
#include <linux/of_address.h>
#include <linux/of_clk.h>
#include <linux/pinctrl/consumer.h>

#include "rp1_gpclk/device.h"
#include "rp1_gpclk/kernel_api.h"
#include "rp1_gpclk/resource_policy.h"

int rp1_gpclk_dt_validate(struct rp1_gpclk_device *device)
{
	struct of_phandle_args spec;
	struct resource resource;
	__u64 divider_phys;
	int ret;

	if (!device || !device->dev || !device->dev->of_node)
		return -ENODEV;
	if (of_property_count_strings(device->dev->of_node, "clock-names") != 1 ||
	    of_count_phandle_with_args(device->dev->of_node, "clocks",
				       "#clock-cells") != 1)
		return -EINVAL;
	if (of_property_match_string(device->dev->of_node, "clock-names",
				     "gpclk") != 0)
		return -EINVAL;
	ret = of_parse_phandle_with_args(device->dev->of_node, "clocks",
					 "#clock-cells", 0, &spec);
	if (ret)
		return ret;
	if (!of_device_is_compatible(spec.np,
				     RP1_GPCLK_PROVIDER_COMPATIBLE) ||
	    spec.args_count != 1 || spec.args[0] != RP1_GPCLK_CLOCK_ID) {
		ret = -EINVAL;
		goto put_node;
	}
	ret = of_address_to_resource(spec.np, 0, &resource);
	if (ret)
		goto put_node;
	if (resource_type(&resource) != IORESOURCE_MEM) {
		ret = -EINVAL;
		goto put_node;
	}
	if (rp1_gpclk_derive_target(resource.start, resource.end,
				    RP1_GPCLK_DIV_FRAC_OFFSET,
				    RP1_GPCLK_REGISTER_BYTES, &divider_phys)) {
		device->divider_phys = 0;
		ret = -ERANGE;
	} else {
		device->divider_phys = (phys_addr_t)divider_phys;
	}
put_node:
	of_node_put(spec.np);
	return ret;
}

int rp1_gpclk_clock_acquire(struct rp1_gpclk_device *device)
{
	int ret;

	device->clock = clk_get(device->dev, "gpclk");
	if (IS_ERR(device->clock)) {
		ret = PTR_ERR(device->clock);
		device->clock = NULL;
		return ret;
	}
	ret = clk_rate_exclusive_get(device->clock);
	if (ret)
		goto put_clock;
	device->rate_exclusive = true;
	return 0;
put_clock:
	clk_put(device->clock);
	device->clock = NULL;
	return ret;
}

int rp1_gpclk_dma_acquire(struct rp1_gpclk_device *device)
{
	int ret;

	device->dma_chan = dma_request_chan(device->dev, "tx");
	if (IS_ERR(device->dma_chan)) {
		ret = PTR_ERR(device->dma_chan);
		device->dma_chan = NULL;
		return ret;
	}
	device->divider_dma = dma_map_resource(device->dev,
		device->divider_phys, RP1_GPCLK_REGISTER_BYTES, DMA_TO_DEVICE, 0);
	if (dma_mapping_error(device->dev, device->divider_dma)) {
		device->divider_dma = 0;
		dma_release_channel(device->dma_chan);
		device->dma_chan = NULL;
		return -EIO;
	}
	device->divider_mapped = true;
	return 0;
}

int rp1_gpclk_pinctrl_acquire(struct rp1_gpclk_device *device)
{
	device->pinctrl = pinctrl_get(device->dev);
	if (IS_ERR(device->pinctrl))
		return PTR_ERR(device->pinctrl);
	device->pins_default = pinctrl_lookup_state(device->pinctrl, "default");
	if (IS_ERR(device->pins_default))
		return PTR_ERR(device->pins_default);
	device->pins_active = pinctrl_lookup_state(device->pinctrl, "active");
	if (IS_ERR(device->pins_active))
		return PTR_ERR(device->pins_active);
	device->pins_safe = pinctrl_lookup_state(device->pinctrl, "safe");
	if (IS_ERR(device->pins_safe))
		return PTR_ERR(device->pins_safe);
	return 0;
}

void rp1_gpclk_quiesce(struct rp1_gpclk_device *device)
{
	/* Phase 2C cannot create a descriptor, callback, clock, or pin transition. */
}

void rp1_gpclk_resources_release(struct rp1_gpclk_device *device)
{
	if (device->divider_mapped) {
		dma_unmap_resource(device->dev, device->divider_dma,
				   RP1_GPCLK_REGISTER_BYTES, DMA_TO_DEVICE, 0);
		device->divider_mapped = false;
		device->divider_dma = 0;
	}
	if (device->dma_chan) {
		dma_release_channel(device->dma_chan);
		device->dma_chan = NULL;
	}
	if (device->pinctrl && !IS_ERR(device->pinctrl)) {
		pinctrl_put(device->pinctrl);
		device->pinctrl = NULL;
		device->pins_default = NULL;
		device->pins_active = NULL;
		device->pins_safe = NULL;
	}
	if (device->rate_exclusive) {
		clk_rate_exclusive_put(device->clock);
		device->rate_exclusive = false;
	}
	if (device->clock) {
		clk_put(device->clock);
		device->clock = NULL;
	}
	device->divider_phys = 0;
}
