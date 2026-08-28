#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Enforce the bounded RP1 endpoint bootstrap and ownership contract."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/rp1_gpclk_main.c").read_text(encoding="utf-8")
KERNEL_API = (ROOT / "src/rp1_gpclk_kernel_api.c").read_text(encoding="utf-8")
CONTRACT = (ROOT / "docs/contracts/rp1-gpclk-dkms-module-contract.md").read_text(
    encoding="utf-8"
)
DATA = json.loads(
    (ROOT / "release/endpoint-bootstrap-contract-v1.json").read_text(encoding="utf-8")
)
VERSION = (ROOT / "include/rp1_gpclk/version.h").read_text(encoding="utf-8")
DEBIAN_RULES = (ROOT / "debian/rules").read_text(encoding="utf-8")
CHANGELOG = (ROOT / "debian/changelog").read_text(encoding="utf-8")
OVERLAYS = [
    (ROOT / "overlays/rp1-gpclk-gpio4.dts").read_text(encoding="utf-8"),
    (ROOT / "overlays/rp1-gpclk-gpio20.dts").read_text(encoding="utf-8"),
]

required_source = (
    "platform_driver_register(&rp1_gpclk_driver)",
    "platform_driver_unregister(&rp1_gpclk_driver)",
    "for_each_matching_node(node, rp1_gpclk_of_match)",
    "rp1_gpclk_validate_endpoint_topology",
    "pre-registration topology rejected",
    "of_device_is_available(node)",
    "of_find_device_by_node(node)",
    "rp1_gpclk_find_instantiated_ancestor(node)",
    "ancestor = of_get_parent(node)",
    "parent = of_get_parent(ancestor)",
    "of_platform_device_create(node, NULL, &parent->dev)",
    "rp1_gpclk_bound_to_this_driver",
    "bus_register_notifier(&platform_bus_type",
    "bus_unregister_notifier(&platform_bus_type",
    "BUS_NOTIFY_DEL_DEVICE",
    "rp1_gpclk_creating_node",
    "rp1_gpclk_creation_removed",
    "get_device(&created->dev)",
    "put_device(&created->dev)",
    "rp1_gpclk_detach_created_device",
    "rp1_gpclk_unregister_created_device(created)",
    "of_node_clear_flag(node, OF_POPULATED)",
    "module_init(rp1_gpclk_init)",
    "module_exit(rp1_gpclk_exit)",
)
for token in required_source:
    assert token in MAIN, token

assert "module_platform_driver" not in MAIN
for prohibited in (
    "of_platform_populate(",
    "of_platform_default_populate(",
    "platform_device_register_full(",
    "platform_device_register_resndata(",
    "/dev/mem",
):
    assert prohibited not in MAIN, prohibited

init = MAIN[MAIN.index("static int __init rp1_gpclk_init") :]
init = init[: init.index("static void __exit rp1_gpclk_exit")]
init_order = [
    init.index("rp1_gpclk_validate_endpoint_topology"),
    init.index("bus_register_notifier"),
    init.index("platform_driver_register"),
    init.index("rp1_gpclk_bootstrap_endpoint"),
]
assert init_order == sorted(init_order)
assert init.index("platform_driver_unregister", init.index("unregister_driver:")) < init.index(
    "bus_unregister_notifier", init.index("unregister_notifier:")
)

exit_source = MAIN[MAIN.index("static void __exit rp1_gpclk_exit") :]
exit_order = [
    exit_source.index("rp1_gpclk_unregister_created_device(created)"),
    exit_source.index("platform_driver_unregister"),
    exit_source.index("bus_unregister_notifier"),
]
assert exit_order == sorted(exit_order)

assert '#define RP1_GPCLK_MODULE_VERSION "1.1.2"' in VERSION
assert DATA["canonicalEndpoint"] == "/dev/rp1-gpclk"
assert DATA["ancestry"] == "endpoint-clock-provider-and-dma-provider-share-rp1-parent"
assert DATA["selection"]["matchingNodes"] == 1
assert DATA["existingDevice"]["moduleMayUnregister"] is False
assert DATA["missingDevice"]["scope"] == "exact-selected-node-only"
assert DATA["missingDevice"]["linuxDeviceParent"] == "nearest-instantiated-platform-ancestor"
assert DATA["missingDevice"]["synchronousBindingRequired"] is True
assert "device->dev->of_node->parent != clock_spec.np->parent" in KERNEL_API

for overlay, route, pin in zip(OVERLAYS, (1, 2), (4, 20), strict=True):
    assert re.search(r"&rp1\s*\{", overlay)
    assert 'compatible = "wsprrypi,rp1-gpclk-dkms-v1"' in overlay
    assert f"wsprrypi,route = <{route}>" in overlay
    assert f"wsprrypi,pin = <{pin}>" in overlay
    assert 'clock-names = "gpclk", "xosc"' in overlay
    assert 'clocks = <&rp1_clocks RP1_CLK_GP0>, <&clk_xosc>' in overlay
    assert 'dma-names = "tx"' in overlay

assert "rp1-gpclk-dkms-gpio4" in OVERLAYS[0]
assert "rp1-gpclk-dkms-gpio20" not in OVERLAYS[0]
assert "rp1-gpclk-dkms-gpio20" in OVERLAYS[1]
assert "rp1-gpclk-dkms-gpio4" not in OVERLAYS[1]
assert "rp1_gpclk_route_endpoint_validate(route," in KERNEL_API
assert "device->dev->of_node->name" in KERNEL_API

for phrase in (
    "exactly one matching node",
    "kernel-created platform device",
    "unregister only the device it created",
    "must not populate or depopulate the RP1 bus generally",
    "A loaded module or matching OF modalias alone is not binding evidence",
):
    assert phrase in CONTRACT, phrase

print("Endpoint bootstrap contract: PASS")
