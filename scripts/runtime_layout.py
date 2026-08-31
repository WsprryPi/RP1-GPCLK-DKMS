# SPDX-License-Identifier: MIT
"""Fixed runtime deployment inventory; no caller-selected destinations."""
KERNEL = '6.18.34+rpt-rpi-2712'
LIB = '/usr/lib/rp1-gpclk-dkms/'
INVENTORY = {
    f'/lib/modules/{KERNEL}/updates/dkms/{name}.ko': f'{name}.ko'
    for name in ('rp1_route_controller', 'rp1_gpclk_dkms')
}
INVENTORY.update({LIB+name: 'scripts/'+name for name in (
    'runtime_controller_admin.py', 'runtime_manager.py', 'runtime_route_client.py',
    'runtime_layout.py', 'runtime_deployment.py', 'runtime_output.py', 'runtime_application.py')})
INVENTORY['/etc/systemd/system/rp1-gpclk-route-manager@.service.d/95-runtime-controller.conf'] = 'systemd/95-runtime-controller.conf'

for name in ('rp1_gpclk.h', 'rp1_route_admin.h'):
    INVENTORY[LIB+'runtime-uapi/'+name] = 'include/uapi/linux/'+name
for route in ('gpio4', 'gpio20'):
    INVENTORY[LIB+'runtime-overlays/'+route+'.dtbo'] = 'build/runtime-controller/'+route+'.dtbo'
