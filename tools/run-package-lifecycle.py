#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Opt-in real dpkg/DKMS tests in disposable, restricted Linux containers."""
import argparse
import json
from pathlib import Path
import subprocess
import uuid
from lifecycle_results import (SCENARIOS, accept, context, input_identity,
                               selection, source_identity)

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--predecessor', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scenario', choices=(*SCENARIOS, 'all'), default='all')
    args = parser.parse_args()
    for path in (args.candidate, args.predecessor):
        if not path.is_absolute() or path != path.resolve() or not path.is_dir():
            parser.error('absolute nonsymlink input directories required')
    output = args.output
    if (not output.is_absolute() or output != output.resolve() or output.exists() or
            not output.parent.is_dir() or output.is_relative_to(ROOT)):
        parser.error('new absolute output outside source required')
    checkout = subprocess.run(['git', '-C', str(output.parent), 'rev-parse', '--show-toplevel'],
                              capture_output=True, env={'PATH': '/usr/bin:/bin',
                              'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'})
    if checkout.returncode == 0:
        parser.error('lifecycle output must be outside every Git checkout')
    image = subprocess.check_output(['docker', 'image', 'inspect', args.image], text=True)
    identity = json.loads(image)[0]
    requested = selection(SCENARIOS if args.scenario == 'all' else (args.scenario,))
    inputs = input_identity(args.candidate, args.predecessor, identity['Id'], source_identity(ROOT))
    run_id = uuid.uuid4().hex
    output.mkdir(mode=0o700)
    (output/'image.json').write_text(image)
    results = []
    for scenario in requested:
        expected = context(run_id, scenario, inputs)
        destination = output/scenario
        destination.mkdir()
        # Linux bind mounts retain the runner's uid. Container root deliberately
        # lacks DAC_OVERRIDE, so share only this directory below the private
        # host-owned result root. Do not broaden container capabilities.
        destination.chmod(0o777)
        command = ['docker', 'run', '--rm', '--network', 'none', '--cap-drop', 'ALL',
                   '--cap-add', 'CHOWN', '--cap-add', 'FOWNER', '--cap-add', 'SETUID',
                   '--cap-add', 'SETGID', '--security-opt', 'no-new-privileges',
                   '--pids-limit', '256', '--cpus', '4', '--memory', '2g',
                   '--cidfile', str(destination/'container.cid'),
                   '-e', 'RP1_LIFECYCLE_CONTEXT='+json.dumps(expected),
                   '-v', str(ROOT)+':/source:ro',
                   '-v', str(args.candidate)+':/candidate:ro',
                   '-v', str(args.predecessor)+':/predecessor:ro',
                   '-v', str(destination)+':/results', identity['Id'],
                   'python3', '/source/tests/package_lifecycle_linux.py', scenario]
        try:
            with (destination/'container.log').open('w') as stream:
                result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        finally:
            cid = destination/'container.cid'
            if cid.exists():
                subprocess.run(['docker', 'rm', '-f', cid.read_text().strip()],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        error = None
        try:
            accept(destination/'result.json', expected, result.returncode)
        except (ValueError, OSError, KeyError, TypeError) as failure:
            error = str(failure)
        results.append({'scenario': scenario, 'exitStatus': result.returncode,
                        'accepted': error is None, 'error': error})
        print(json.dumps(results[-1]), flush=True)
        if result.returncode or error:
            print((destination/'container.log').read_text()[-8192:], flush=True)
    passed = len(results) == len(requested) and all(r['accepted'] for r in results)
    if passed:
        passed = input_identity(args.candidate, args.predecessor, identity['Id'],
                                source_identity(ROOT)) == inputs
    (output/'result.json').write_text(json.dumps({'status': 'PASS' if passed else 'FAIL',
        'runId': run_id, 'identity': inputs, 'imageId': identity['Id'],
        'scenarios': results, 'targetQualification': False,
        'wsprrypiAcceptance': False, 'rfQualification': False}, indent=2)+'\n')
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
