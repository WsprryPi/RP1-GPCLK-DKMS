#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build/validate supplemental evidence for immutable software; never operate hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TAG = 'qualification-v1.0.0-r1'
NAME = 'rp1-qualification.json'
SCHEMA = 'rp1-qualification.schema.json'
ASSETS = {NAME, SCHEMA, 'qualification_status.py', 'SHA256SUMS'}
INPUT = 'release/qualification-1.0.0-r1.json'
SOFTWARE = 'release/software-1.0.0.json'


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON field: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False, 'nonfinite JSON number'))


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-c', 'core.fsmonitor=false',
                                   '-c', 'safe.directory='+str(ROOT), '-C', str(ROOT), *args])


def blob(commit, name):
    return git('show', commit + ':' + name)


def documents(commit):
    require(re.fullmatch('[0-9a-f]{40}', commit), 'exact metadata source commit required')
    data = strict_json(blob(commit, INPUT))
    software = strict_json(blob(commit, SOFTWARE))
    require(data['revision'] == 1 and data['softwareTag'] == 'v1.0.0' and
            len(data['routes']) == 2 and {e['route'] for e in data['routes']} == {'gpio4', 'gpio20'},
            'revision or independent route set differs')
    require(len({e['id'] for e in data['evidence']}) == len(data['evidence']), 'duplicate evidence reference')
    require(git('rev-parse', 'v1.0.0^{commit}').decode().strip() == software['sourceCommit'],
            'original software tag moved')
    require(git('rev-parse', 'v1.0.0').decode().strip() == software['tagObject'],
            'original annotated tag object moved')
    reuse = data['reuse']
    require(reuse['publishedProviderCommit'] == software['sourceCommit'], 'reuse release differs')
    require(not git('diff', '--name-only', reuse['testedProviderCommit'],
                    software['sourceCommit'], '--', *reuse['unchangedInputs']).strip(),
            'evidence reuse changes executable/build inputs')
    require(data['applicationQualification']['earlierCampaignProvenance'] and
            data['applicationQualification']['earlierCampaignObservations']['applicability'],
            'earlier application evidence applicability required')
    # The publication is reproducible from this separate source, never from a new module version.
    layout = {}
    exec(compile(blob(software['sourceCommit'], 'scripts/runtime_layout.py'),
                 'released runtime_layout.py', 'exec'), layout)
    routes = {entry['route']: entry for entry in data['routes']}
    runtime_files = {destination: (routes[Path(source).stem]['runtimeOverlaySha256']
        if source.startswith('build/runtime-controller/') else
        sha(blob(software['sourceCommit'], source))) for destination, source in layout['INVENTORY'].items()}
    value = {'SPDX-License-Identifier': 'MIT', 'schema': 'rp1-qualification-v1',
             'schemaVersion': 1, 'metadataTag': TAG, 'revision': 1,
             'metadataSource': {'commit': commit,
                 'tree': git('rev-parse', commit + '^{tree}').decode().strip(),
                 'inputSha256': sha(blob(commit, INPUT))},
             'software': software, 'runtimeFiles': runtime_files, 'evidence': data}
    for entry in data['routes']:
        route = entry['route']
        require(entry['routeId'] == software['compatibilityIdentities'][route], 'route substitution')
        require(entry['evidenceId'] in {e['id'] for e in data['evidence']} and
                entry['evidenceSelector'] == {'field': 'cases.route', 'value': route.upper()},
                'evidence route selector differs')
        entry['overlaySha256'] = software['overlaySha256'][route]
    return value


def verify_original(directory, software):
    require(directory.resolve() == directory and directory.is_dir(), 'absolute original directory required')
    require({p.name for p in directory.iterdir()} == set(software['assets']), 'original asset set differs')
    for name, digest in software['assets'].items():
        path = directory / name
        require(not path.is_symlink() and path.is_file() and sha(path.read_bytes()) == digest,
                'original asset changed: ' + name)
    original = strict_json((directory / 'rp1-gpclk-compatibility-manifest.json').read_bytes())
    require(original['defaultState'] == 'Unavailable' and original['entries'] == [],
            'original empty manifest changed')
    provenance = strict_json((directory / 'release-metadata.json').read_bytes())
    require(provenance['sourceCommit'] == software['sourceCommit'], 'original source differs')
    for route in ('gpio4', 'gpio20'):
        require(provenance['routes'][route]['dtboSha256'] == software['overlaySha256'][route],
                'original overlay differs')
    for name, key in [('rp1_gpclk.h', 'consumer'), ('rp1_route_admin.h', 'controller')]:
        require(provenance['uapi'][name]['sha256'] == software['uapiSha256'][key], 'original UAPI differs')


def payloads(commit):
    value = documents(commit)
    # Reconstruct both overlay forms rather than trusting a route label/hash pair.
    import overlay_builder
    require(Path(overlay_builder.__file__).read_bytes() ==
            blob(value['software']['sourceCommit'], 'scripts/overlay_builder.py'),
            'overlay compiler helper differs from original release')
    with tempfile.TemporaryDirectory(prefix='rp1-qualification-overlays-') as temporary:
        directory = Path(temporary)
        for entry in value['evidence']['routes']:
            source = blob(value['software']['sourceCommit'], 'overlays/rp1-gpclk-'+entry['route']+'.dts')
            require(sha(source) == entry['overlaySourceSha256'], 'overlay source evidence differs')
            path, output = directory/'route.dts', directory/'route.dtbo'
            path.write_bytes(source)
            overlay_builder.build_dtbo(path, output, 'dtc')
            require(sha(output.read_bytes()) == entry['overlaySha256'], 'packaged overlay evidence differs')
            subprocess.run(['fdtput', '-r', str(output), '/__symbols__'], check=True,
                           capture_output=True, timeout=10)
            require(sha(output.read_bytes()) == entry['runtimeOverlaySha256'], 'runtime overlay evidence differs')
    schema = blob(commit, 'schema/rp1-qualification-v1.schema.json')
    import jsonschema
    jsonschema.Draft202012Validator(strict_json(schema)).validate(value)
    result = {NAME: encode(value), SCHEMA: schema,
              'qualification_status.py': blob(commit, 'scripts/qualification_status.py')}
    result['SHA256SUMS'] = ''.join(sha(result[n]) + '  ' + n + '\n' for n in sorted(result)).encode()
    return value, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--original-directory', required=True, type=Path)
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    require(not git('status', '--porcelain=v1', '--untracked-files=all').strip(),
            'clean committed metadata source required')
    for name in ('scripts/qualification_metadata.py', 'scripts/qualification_status.py'):
        require((ROOT / name).read_bytes() == blob(args.source_commit, name),
                'metadata implementation differs from selected source')
    value, assets = payloads(args.source_commit)
    verify_original(args.original_directory, value['software'])
    destination = args.directory
    require(destination.is_absolute() and destination.resolve() == destination and
            not destination.is_relative_to(ROOT), 'external nonsymlink output required')
    if args.validate:
        require(destination.is_dir() and {p.name for p in destination.iterdir()} == ASSETS,
                'supplement asset set differs')
        for name, raw in assets.items():
            path = destination / name
            require(not path.is_symlink() and path.is_file() and path.read_bytes() == raw,
                    'supplement not reproducible: ' + name)
    else:
        destination.mkdir(exist_ok=False, parents=True)
        for name, raw in assets.items():
            (destination / name).write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'metadataTag': TAG, 'sourceCommit': args.source_commit,
                      'assets': {name: sha(raw) for name, raw in assets.items()}}, sort_keys=True))


if __name__ == '__main__':
    main()
