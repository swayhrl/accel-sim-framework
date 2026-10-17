"""Current Lane5 scientific supersession overrides historical terminal/certificate PASS."""
import hashlib
import json
from pathlib import Path
import subprocess

from registry import canonical, run_key

BRANCH = 'hrl/ep-l2-ft20261016-lane5-v1'
MANIFEST = 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/APPLICATION_ACCEPTANCE.json'
CLIENT = Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json')
SCHEMA = 'EPL2_SCIENTIFIC_ACCEPTANCE_V2'
RELEASE_FIELDS = ('core_source_commit', 'framework_source_commit', 'binary_sha256')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    p = Path(name)
    require(not p.is_absolute() and '..' not in p.parts and
            name.startswith('docs/ep_l2/review_packs/'), 'unsafe supersession evidence path')
    return p


def bind_manifest(raw, binding, read_evidence):
    """Bind exact current bytes and evidence; loaders establish freshness."""
    manifest = json.loads(raw)
    require(manifest.get('schema_version') == SCHEMA, 'missing current supersession schema')
    require(manifest.get('authority', {}).get('lane_id') == 5 and
            manifest['authority'].get('framework_branch') == BRANCH,
            'not Lane5 scientific authority')
    require(type(manifest.get('generation')) is int and manifest['generation'] > 0,
            'invalid acceptance generation')
    require(binding['manifest_sha256'] == sha(raw), 'current acceptance bytes changed')
    require(binding['generation'] == manifest['generation'] and
            binding['revision'] == manifest['revision'], 'stale acceptance revision')
    require(binding['kind'] in ('LOCAL_CURRENT_POINTER', 'FETCHED_GITHUB_BRANCH'),
            'unverified current authority binding')
    require(bool(manifest.get('supersession_evidence')), 'missing supersession evidence')
    for item in manifest['supersession_evidence']:
        name = str(safe_path(item['path']))
        require(sha(read_evidence(name)) == item['sha256'], 'supersession evidence changed: ' + name)
    seen = set()
    for row in manifest['rows']:
        require(row['run_key'] not in seen, 'duplicate acceptance run key')
        seen.add(row['run_key'])
        require(run_key(row['identity']) == row['run_key'], 'acceptance identity/key mismatch')
        for name in (*RELEASE_FIELDS, 'runtime_config_sha256', 'trace_content_sha256', 'workload'):
            require(row[name] == row['identity'][name], 'acceptance flat identity mismatch: ' + name)
    for row in manifest['withdrawn_releases']:
        require(all(row.get(n) for n in RELEASE_FIELDS) and row.get('reason'),
                'incomplete withdrawal identity')
    return {'manifest': manifest,
            'binding': {**binding, 'canonical_sha256': sha(canonical(manifest))}}


def load_current_authority(client_path=CLIENT):
    client = json.loads(Path(client_path).read_text())
    pointer = client.get('scientific_acceptance')
    require(isinstance(pointer, dict), 'current scientific acceptance pointer missing')
    path = Path(pointer['path']).resolve(strict=True)
    repo = path.parents[5]  # docs/ep_l2/codex_handoff/<stage>/lane5/file
    require(path == repo / MANIFEST, 'noncanonical scientific acceptance path')
    # Immutable V2 snapshots let one result be published while other compatible
    # clients keep validating against the exact atomic current pointer.
    snapshot = pointer.get('snapshot_path')
    payload = path
    if snapshot is not None:
        payload = Path(snapshot).resolve(strict=True)
        require(payload.is_relative_to(repo / 'docs/ep_l2/review_packs') and
                payload.name == 'SCIENTIFIC_ACCEPTANCE_V2.json', 'unsafe current snapshot')
    return bind_manifest(payload.read_bytes(), {'kind': 'LOCAL_CURRENT_POINTER',
        'manifest_sha256': pointer['sha256'], 'generation': pointer['generation'],
        'revision': pointer['revision']}, lambda name: (repo / name).read_bytes())


def fetch_current_authority(repo, remote='origin'):
    """Read-only bounded fetch for off-host/paper consumers; no cached certificate fallback."""
    repo = Path(repo)
    url = subprocess.check_output(['git', 'remote', 'get-url', remote], cwd=repo, text=True).strip()
    require(url.rstrip('/').removesuffix('.git').endswith('github.com:swayhrl/accel-sim-framework') or
            url.rstrip('/').removesuffix('.git').endswith('github.com/swayhrl/accel-sim-framework'),
            'wrong scientific authority repository')
    ref = 'refs/remotes/' + remote + '/' + BRANCH
    subprocess.run(['git', 'fetch', '--no-tags', remote,
                    'refs/heads/' + BRANCH + ':' + ref], cwd=repo, check=True, capture_output=True)
    commit = subprocess.check_output(['git', 'rev-parse', ref], cwd=repo, text=True).strip()
    read = lambda name: subprocess.check_output(['git', 'show', commit + ':' + name], cwd=repo)
    raw = read(MANIFEST)
    meta = json.loads(raw)
    return bind_manifest(raw, {'kind': 'FETCHED_GITHUB_BRANCH', 'publication_commit': commit,
        'manifest_sha256': sha(raw), 'generation': meta['generation'],
        'revision': meta['revision']}, read)


def current_manifest(state):
    manifest = state['manifest']
    require(state['binding']['canonical_sha256'] == sha(canonical(manifest)),
            'acceptance state mutated after binding')
    return manifest


def reject_withdrawn(identity, manifest):
    for row in manifest['withdrawn_releases']:
        # The known-bad Core or the same executable cannot be rehabilitated by
        # renaming configs, Framework metadata, trace aliases or old certificates.
        if (identity['core_source_commit'] == row['core_source_commit'] or
                identity['binary_sha256'] == row['binary_sha256']):
            raise ValueError('scientific qualification withdrawn: ' + row['reason'])
    key = run_key(identity)
    for row in manifest['rows']:
        if row['run_key'] == key:
            require(row['scientific_acceptance'] == 'CURRENT_ACCEPTED',
                    'run scientifically suspended or not run')


def authorize_launch(identity, qualification_sha256, state):
    manifest = current_manifest(state)
    reject_withdrawn(identity, manifest)
    for row in manifest['launch_authorizations']:
        if (all(identity[n] == row[n] for n in RELEASE_FIELDS) and
                row['feature_vector'] == identity['feature_vector'] and
                row['ideal_vector'] == identity['ideal_vector'] and
                row['qualified_release_sha256'] == qualification_sha256 and
                row['status'] == 'CURRENT_QUALIFIED_FOR_LAUNCH'):
            # Whole-ledger revisions may change while an unrelated run finishes.
            # Stable authorization belongs in the immutable input audit; the
            # current pointer is consulted anew on every inspect().
            return row
    raise ValueError('release/vector not currently authorized for launch')


def require_current_result(identity, raw_log_sha256, cycles, instructions, state):
    manifest = current_manifest(state)
    reject_withdrawn(identity, manifest)
    key = run_key(identity)
    matches = [r for r in manifest['rows'] if r['run_key'] == key]
    require(len(matches) == 1, 'current acceptance row missing')
    row = matches[0]
    require(row['identity'] == identity, 'current result identity mismatch')
    require(row['scientific_acceptance'] == 'CURRENT_ACCEPTED' and
            row['original_terminal_status'] == 'COMPLETE_VALID', 'result not currently accepted')
    require(row['raw_log_sha256'] == raw_log_sha256 and len(raw_log_sha256) == 64,
            'accepted raw log identity mismatch')
    require(row['observed_cycles'] == cycles and row['instructions'] == instructions and
            type(cycles) is int and cycles > 0 and type(instructions) is int and instructions > 0,
            'accepted result metrics mismatch')
    return {'run_key': key, 'scientific_acceptance': 'CURRENT_ACCEPTED',
            'authority': state['binding']}


# Capture the executed loader bytes once; later source publication cannot rebind
# an already running client to code it did not import.
EXECUTED_LOADER_SHA256 = sha(Path(__file__).read_bytes())


def immutable_loader_binding(client_path=CLIENT):
    client = json.loads(Path(client_path).read_text())
    require(client['acceptance_module_sha256'] == EXECUTED_LOADER_SHA256,
            'running loader differs from published client contract')
    return {'acceptance_module_sha256': EXECUTED_LOADER_SHA256,
            'acceptance_source_commit': client['acceptance_source_commit'],
            'immutable_scientific_pointer': True}


def require_publication_boundary(registry):
    """Legacy clients drain first; only content-bound new clients permit overlap."""
    from registry import ACTIVE
    active = [r for r in registry.snapshot()['runs'].values() if r['status'] in ACTIVE]
    if not active:
        return
    client = json.loads(CLIENT.read_text())
    allowed = client.get('immutable_acceptance_clients', [])
    for row in active:
        binding = row.get('client_binding')
        require(binding is not None and binding.get('immutable_scientific_pointer') is True
            and {k:binding[k] for k in ('acceptance_module_sha256','acceptance_source_commit')} in allowed,
            'Legacy/unbound active simulator must drain before scientific publication')
