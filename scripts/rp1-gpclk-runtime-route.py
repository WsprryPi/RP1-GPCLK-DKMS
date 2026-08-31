#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Uninstalled Experimental runtime protocol; all target mutation is blocked."""
import json
import sys

from runtime_route import CONTRACT, MAX_INPUT, Rejected, decode, public_response


def main() -> int:
    try:
        if len(sys.argv) != 1:
            raise Rejected("arguments-not-supported")
        payload = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(payload) > MAX_INPUT:
            raise Rejected("request-too-large")
        response = public_response(decode(payload))
    except Rejected as error:
        response = {"schemaVersion": 2, "contract": CONTRACT, "operation": None,
                    "status": "rejected", "classification": "Experimental", "qualification": False,
                    "mutationAvailable": False, "error": str(error)}
    print(json.dumps(response, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
