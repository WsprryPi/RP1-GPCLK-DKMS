#!/bin/bash
# SPDX-License-Identifier: MIT
set -Eeuo pipefail

export RP1_GPCLK_TARGET_PHASE=phase4a
export RP1_GPCLK_TARGET_CLIENT_SOURCE=phase4a_uapi_client.c
export RP1_GPCLK_TARGET_CLIENT_NAME=phase4a_uapi_client
export RP1_GPCLK_TARGET_VERSION=0.0.0-phase4d-combined
export RP1_GPCLK_TARGET_RUN_INERT=1
export RP1_GPCLK_TARGET_MODULE_PARAMETERS=live_output=0
export RP1_GPCLK_TARGET_AUTHORIZATION='On wspr5, build, install, sign, load, bind, unbind, unload, and remove the Phase 4 test module; apply/remove only GPIO4/GPIO20 test overlays; create/remove disposable files; no boot, reboot, service, GPIO, or RF output.'

exec "$(dirname "$0")/phase3b-target-test.sh" "$@"
