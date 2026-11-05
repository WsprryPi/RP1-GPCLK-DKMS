#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Print only bounded lifecycle outcome fields, never collect filesystem payloads."""
import json
from pathlib import Path
import sys
from lifecycle_results import decode, read_regular, require, SCENARIOS


def main():
    value = decode(read_regular(Path(sys.argv[1]), 1024*1024))
    require(value.get('status') in ('PASS', 'FAIL'), 'invalid aggregate status')
    rows = value.get('scenarios')
    require(isinstance(rows, list) and len(rows) <= len(SCENARIOS), 'invalid scenario summary')
    for row in rows:
        require(row.get('scenario') in SCENARIOS and type(row.get('accepted')) is bool,
                'invalid scenario outcome')
        print(json.dumps({key: row.get(key) for key in ('scenario', 'accepted', 'exitStatus')}))
    print('Lifecycle aggregate: '+value['status'])
    if value['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
