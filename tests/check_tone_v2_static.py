#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
R=Path(__file__).resolve().parents[1]
u=(R/'include/uapi/linux/rp1_gpclk.h').read_text()
d=(R/'src/rp1_gpclk_uapi_dispatch.c').read_text()
e=(R/'src/rp1_gpclk_execution.c').read_text()
c=(R/'src/rp1_gpclk_core.c').read_text()
for token in ('RP1_GPCLK_IOC_QUERY_V2','RP1_GPCLK_IOC_SUBMIT_TONE_V2','RP1_GPCLK_IOC_RELEASE_V2','RP1_GPCLK_CAP_TONE_CONTINUOUS','RP1_GPCLK_CAP_TONE_FINITE'):
    assert token in u
assert 'request.capabilities = RP1_GPCLK_V1_CAPABILITIES' in d
assert 'request.capabilities = RP1_GPCLK_V2_CAPABILITIES' in d
assert e.count('complete_all(&device->dma_done);') >= 2
assert 'if (atomic_read(&device->stop_requested)) {' in e
assert 'dmaengine_terminate_sync(device->dma_chan);' in e
finish=e.index('cleanup_ret = rp1_gpclk_execution_machine_finish')
assert finish < e.index('rp1_gpclk_core_progress', finish)
assert 'request->duration_ns != 0' in c
assert 'request->duration_ns < RP1_GPCLK_TONE_DURATION_NS_MIN' in c
assert 'request->duration_ns > RP1_GPCLK_TONE_DURATION_NS_MAX' in c
assert 'request->expected_route != core->value.route' in c
assert 'RP1_GPCLK_MODE_WSPR' in c and 'RP1_GPCLK_MODE_QRSS' in c and 'RP1_GPCLK_MODE_FSKCW' in c and 'RP1_GPCLK_MODE_DFCW' in c
assert '#define RP1_GPCLK_GPIO4_CANDIDATE_VERSION "1.0.1"' in (R/'include/rp1_gpclk/compatibility.h').read_text()
assert '#define RP1_GPCLK_MODULE_VERSION "1.1.2"' in (R/'include/rp1_gpclk/version.h').read_text()
assert '#define RP1_GPCLK_TONE_DURATION_NS_MIN 1000000ULL' in u
assert '#define RP1_GPCLK_TONE_DURATION_NS_MAX 120000000000ULL' in u
assert 1_000_000 <= 1_000_000_000 <= 120_000_000_000
print('ABI v2 TONE static safety contract: PASS')
