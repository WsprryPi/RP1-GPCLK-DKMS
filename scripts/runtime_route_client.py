#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Operator client for the existing route-manager socket; never uses sudo."""
import json
import socket
import sys
import uuid

SOCKET = '/run/rp1-gpclk-dkms/route-manager.sock'
CONTRACT = 'rp1-gpclk-route-manager-runtime-v1'


def exchange(request):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stream:
        stream.settimeout(30)
        stream.connect(SOCKET)
        stream.sendall(json.dumps(request).encode()+b'\n')
        stream.shutdown(socket.SHUT_WR)
        chunks = bytearray()
        while True:
            data = stream.recv(min(4096, 1048577-len(chunks)))
            if not data: break
            chunks.extend(data)
            if len(chunks) > 1048576: raise ValueError('response too large')
    result = json.loads(chunks)
    if result.get('schemaVersion') != 3 or result.get('contract') != CONTRACT:
        raise ValueError('runtime profile is not deployed')
    return result


def main():
    args = sys.argv[1:]
    if args not in (['query'], ['recover', '--execute'], ['preflight','gpio4'], ['preflight','gpio20'],
                    ['switch','gpio4','--execute'], ['switch','gpio20','--execute']):
        raise SystemExit('usage: runtime_route_client.py query | preflight gpio4|gpio20 | switch gpio4|gpio20 --execute | recover --execute')
    operation = args[0]
    request = {'schemaVersion':3, 'operation':operation}
    if operation in ('switch','preflight'): request['route'] = args[1]
    if operation == 'switch':
        checked = exchange({'schemaVersion':3,'operation':'preflight','route':args[1]})
        if checked['status'] != 'ok': print(json.dumps(checked)); return 2
        request['preflightToken'] = checked['state']['preflightToken']
    if operation in ('switch','recover'):
        request.update(execute=True, requestId=str(uuid.uuid4()), actor='runtime-route-client')
    result = exchange(request)
    print(json.dumps(result, indent=2))
    return 2 if result['status'] == 'error' else 0


if __name__ == '__main__':
    raise SystemExit(main())
