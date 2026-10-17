#!/usr/bin/env python3
"""One-shot exact-commit transport; preserved native Lane5 scientific gates.

No polling, registry instance, launch or cached acceptance. This transport avoids
incidental submodule recursion. Candidate discovery emits no numeric results.
An explicit --adapter delegates to the existing native/eleven-gate consumer.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.with_name('FT20261016_LANE6_PAPER_PPA_r4')
PIN = '20676888aa9f1d98bb318573a6569f5fe88aa17a'


def command(repo, *args):
    return subprocess.check_output(['git', '-c', 'gc.auto=0', *args],
                                   cwd=repo, timeout=30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--adapter', type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.output.exists():
        raise ValueError('Immutable output already exists')
    source = PREVIOUS / 'current_pair_intake.py'
    exact = command(repo, 'show', PIN + ':' + str(source.relative_to(repo)))
    if source.read_bytes() != exact:
        raise ValueError('Pinned consumer changed')
    spec = importlib.util.spec_from_file_location('r14_pinned_consumer', source)
    consumer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consumer)
    api = consumer.vendor_api()
    url = command(repo, 'remote', 'get-url', 'origin').decode().strip()
    if url not in ['git@github.com:swayhrl/accel-sim-framework.git',
                   'https://github.com/swayhrl/accel-sim-framework.git']:
        raise ValueError('Wrong authority repository')
    commit = consumer.live_head(repo)
    command(repo, 'fetch', '--no-tags', '--no-recurse-submodules', 'origin', commit)
    read = lambda name: command(repo, 'show', commit + ':' + name)
    raw = read(api.MANIFEST)
    meta = json.loads(raw)
    state = api.bind_manifest(raw, {
        'kind':'FETCHED_GITHUB_BRANCH', 'publication_commit':commit,
        'manifest_sha256':hashlib.sha256(raw).hexdigest(),
        'generation':meta['generation'], 'revision':meta['revision']}, read)
    context = consumer.bridge(repo, state)
    accepted = []
    for row in state['manifest']['rows']:
        if row['scientific_acceptance'] == 'CURRENT_ACCEPTED':
            api.require_current_result(row['identity'], row['raw_log_sha256'],
                                       row['observed_cycles'], row['instructions'], state)
            accepted.append({k:row[k] for k in ['run_key','mode','workload','identity','raw_log_sha256']})
    result = {'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'authority':state['binding'], 'transport':'FRESH_BRANCH_HEAD_EXACT_COMMIT_FETCH_NO_SUBMODULES',
              'native_consumer_commit':PIN,
              'status':'CURRENT_ROWS_REQUIRE_NATIVE_PAIR_ADAPTER' if accepted else 'NO_CURRENT_ACCEPTED_PAIR',
              'accepted_row_candidates':accepted, 'paper_results_emitted':False,
              'formal_performance_figures':[], 'geomean':None,
              'registry_mutations':0, 'background_waiter':None}
    if args.adapter:
        result['native_intake'] = consumer.consume(repo, json.loads(args.adapter.read_text()), state)
        result['status'] = 'CURRENT_NATIVE_PAIR_VALIDATED_FOR_NEW_PAPER_REVISION'
        result['paper_results_emitted'] = True
    context.assert_fresh()
    with args.output.open('x') as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write('\n')
    print(json.dumps({'status':result['status'], 'authority':result['authority'],
                      'current_rows':len(accepted)}))


if __name__ == '__main__':
    main()
