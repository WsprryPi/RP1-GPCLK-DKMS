#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Canonical validation for the exact runtime-profile binding."""
import hashlib
import json
import re

from runtime_layout import INVENTORY, KERNEL

CONTRACT = 'rp1-gpclk-runtime-binding-v2'
PRODUCT_VERSION = '0.9.0'
COMPATIBILITY = {'gpio4': 'v0.9.0-pi5-gpio4', 'gpio20': 'v0.9.0-pi5-gpio20'}
APPLICATION = '/usr/local/lib/wsprrypi/route_application.py'
EXTERNAL_PATHS = {APPLICATION}


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def validate(binding):
    fields = {'schemaVersion', 'contract', 'productVersion',
        'compatibilityIdentities', 'sourceCommit', 'kernel', 'files',
        'externalFiles', 'uapiSha256', 'controllerNoteSha256',
        'consumerNoteSha256', 'artifactSetSha256'}
    if (not isinstance(binding, dict) or set(binding) != fields or
            type(binding.get('schemaVersion')) is not int or binding['schemaVersion'] != 2 or
            binding.get('contract') != CONTRACT or binding.get('productVersion') != PRODUCT_VERSION or
            binding.get('kernel') != KERNEL or binding.get('compatibilityIdentities') != COMPATIBILITY or
            not isinstance(binding.get('sourceCommit'), str) or
            not re.fullmatch('[0-9a-f]{40}', binding['sourceCommit']) or
            not isinstance(binding.get('files'), dict) or set(binding['files']) != set(INVENTORY) or
            not isinstance(binding.get('externalFiles'), dict) or set(binding['externalFiles']) != EXTERNAL_PATHS or
            not isinstance(binding.get('uapiSha256'), dict) or
            set(binding['uapiSha256']) != {'consumer', 'controller'}):
        raise ValueError('runtime binding schema/identity mismatch')
    digests = (list(binding['files'].values()) + list(binding['externalFiles'].values()) +
               list(binding['uapiSha256'].values()) + [binding['controllerNoteSha256'],
               binding['consumerNoteSha256'], binding['artifactSetSha256']])
    if any(not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value)
           for value in digests):
        raise ValueError('runtime binding digest schema')
    if (binding['uapiSha256']['consumer'] != binding['files'][
            '/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h'] or
            binding['uapiSha256']['controller'] != binding['files'][
            '/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_route_admin.h']):
        raise ValueError('runtime binding UAPI identity mismatch')
    identity = dict(binding)
    identity.pop('artifactSetSha256')
    if canonical_digest(identity) != binding['artifactSetSha256']:
        raise ValueError('runtime binding artifact-set digest mismatch')
    return binding
