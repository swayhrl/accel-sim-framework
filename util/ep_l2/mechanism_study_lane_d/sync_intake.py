"""One-shot D analysis of E's accepted pairs; never launch, qualify or poll.

Consumes E's canonical accepted_results pointers and accepted_pairs declarations.
Pair declaration: baseline_attempt_id, variant_attempt_id, mechanism,
comparison_group, status, and E's nonresearch_config_equal assertion. A path/SHA
pointer to that declaration is also accepted. Schema gaps hold only that pair;
E remains the acceptance owner. No old campaign result is imported here.
"""
import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path

CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
AUTHORITY = 'd9263fa2431592b33e900d9b48c6f20029d8b544'
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
FIELD = 'mechanism_study_20261019_v1'
UNKNOWN = 'UNKNOWN'
FIELDS = ['pair_id', 'status', 'mechanism', 'workload', 'comparison_group',
          'baseline_attempt_id', 'variant_attempt_id', 'baseline_run_key', 'variant_run_key',
          'core', 'framework', 'vendor', 'binary', 'trace',
          'baseline_profile', 'variant_profile', 'baseline_labels', 'variant_labels',
          'baseline_qualification_id', 'variant_qualification_id', 'selection_id',
          'comparison_invariants_sha256',
          'baseline_config', 'variant_config', 'baseline_cycles', 'variant_cycles',
          'baseline_instructions', 'variant_instructions', 'baseline_over_variant',
          'cycles_baseline_minus_variant', 'bottleneck', 'trigger', 'local_service',
          'baseline_mechanism_metrics', 'variant_mechanism_metrics',
          'interpretation', 'baseline_receipt_sha256', 'variant_receipt_sha256']

def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pointer(row):
    path = Path(row['path'])
    if digest(path) != row['sha256']: raise ValueError('E receipt bytes changed')
    return json.loads(path.read_text())
def value(record, key):
    if key in record and record[key] is not None: return record[key]
    for group in ['summary', 'terminal_summary', 'metrics']:
        if key in record.get(group, {}) and record[group][key] is not None: return record[group][key]
    return UNKNOWN
def compact(record, key):
    item = record.get(key)
    if item is None: return UNKNOWN
    return json.dumps(item, sort_keys=True, separators=(',', ':'))

def analyze_pair(pair_id, declaration, accepted_results):
    pair = pointer(declaration) if 'path' in declaration else declaration
    row = {k: UNKNOWN for k in FIELDS}
    row.update(pair_id=pair_id, mechanism=pair.get('mechanism', UNKNOWN),
               comparison_group=pair.get('comparison_group', UNKNOWN), status=pair.get('status', UNKNOWN))
    if row['status'] not in ['CURRENT_ACCEPTED', 'ACCEPTED', 'COMPLETE_VALID']:
        row['interpretation'] = 'E_NOT_CURRENT_ACCEPTED_OR_WITHDRAWN_NO_CURRENT_EFFECT'; return row
    ids = [pair['baseline_attempt_id'], pair['variant_attempt_id']]
    if any(key not in accepted_results for key in ids):
        raise ValueError('E pair lacks two accepted_results pointers')
    refs = [accepted_results[key] for key in ids]
    # E's published pair embeds the exact pointers accepted at pair creation.
    # A changed current endpoint must not silently rewrite that historical pair.
    if 'endpoints' in pair:
        for side, key, ref in zip(['left', 'right'], ids, refs):
            frozen = pair['endpoints'][side]
            if frozen.get('attempt_id') != key or any(frozen.get(k) != ref.get(k) for k in ['path', 'sha256', 'identity']):
                raise ValueError('E pair endpoint pointer changed: ' + side)
    records = [pointer(ref) for ref in refs]
    identities = [ref['identity'] for ref in refs]
    for key, record, identity in zip(ids, records, identities):
        if record.get('attempt_id') != key or record.get('identity') != identity:
            raise ValueError('E result identity/attempt mismatch')
        if record.get('status') != 'COMPLETE_VALID' or record.get('independent_acceptance') != 'PASS' or record.get('complete_input_verified') is not True:
            raise ValueError('not E accepted complete full application')
        if identity.get('epoch_range', {}).get('scope') != 'full_application':
            raise ValueError('screen/synthetic evidence cannot be an application pair')
    for field in ['core_source_commit', 'framework_source_commit', 'binary_sha256',
                  'trace_content_sha256', 'epoch_range', 'workload']:
        if field not in identities[0] or identities[0][field] != identities[1].get(field):
            raise ValueError('cross-source/binary/input pair: ' + field)
    a, b = records; i, j = identities
    # E accepts exact source_identity (including vendor), selection and invariant
    # equality. Retain that boundary rather than dropping it in the D projection.
    for field in ['source_identity', 'selection_id', 'comparison_invariants_sha256']:
        if field in a or field in b:
            if a.get(field) != b.get(field):
                raise ValueError('E endpoint comparison boundary differs: ' + field)
    sources = a.get('source_identity') or {}
    row.update(baseline_attempt_id=ids[0], variant_attempt_id=ids[1],
               baseline_run_key=refs[0].get('run_key', a.get('run_key', UNKNOWN)),
               variant_run_key=refs[1].get('run_key', b.get('run_key', UNKNOWN)),
               core=i['core_source_commit'], framework=i['framework_source_commit'], binary=i['binary_sha256'],
               vendor=sources.get('vendor_pybind11_commit', UNKNOWN),
               trace=i['trace_content_sha256'], workload=i['workload'],
               baseline_profile=a.get('profile', UNKNOWN), variant_profile=b.get('profile', UNKNOWN),
               baseline_labels=compact(a, 'labels'), variant_labels=compact(b, 'labels'),
               baseline_qualification_id=a.get('qualification_id', UNKNOWN),
               variant_qualification_id=b.get('qualification_id', UNKNOWN),
               selection_id=a.get('selection_id', UNKNOWN),
               comparison_invariants_sha256=a.get('comparison_invariants_sha256', UNKNOWN),
               baseline_config=i.get('runtime_config_sha256', UNKNOWN), variant_config=j.get('runtime_config_sha256', UNKNOWN),
               baseline_cycles=value(a, 'cycles'), variant_cycles=value(b, 'cycles'),
               baseline_instructions=value(a, 'instructions'), variant_instructions=value(b, 'instructions'),
               baseline_receipt_sha256=refs[0]['sha256'], variant_receipt_sha256=refs[1]['sha256'],
               bottleneck=compact(a.get('mechanism_metrics', {}), 'bottleneck'),
               trigger=compact(b.get('mechanism_metrics', {}), 'trigger'),
               local_service=compact(b.get('mechanism_metrics', {}), 'local_service'),
               baseline_mechanism_metrics=compact(a, 'mechanism_metrics'),
               variant_mechanism_metrics=compact(b, 'mechanism_metrics'))
    if pair.get('nonresearch_config_equal') is not True:
        row.update(status='E_ACCEPTED_PENDING_D_CONFIG_SCOPE', interpretation='UNKNOWN_nonresearch_config_equality; do not infer fairness from equal binary/cycles')
        return row
    if UNKNOWN in [row['baseline_cycles'], row['variant_cycles'], row['baseline_instructions'], row['variant_instructions']]:
        row.update(status='E_ACCEPTED_MISSING_NATIVE_METRICS', interpretation='UNKNOWN_missing_is_not_zero'); return row
    if row['baseline_instructions'] != row['variant_instructions']:
        raise ValueError('matched full input instructions differ')
    ca, cb = int(row['baseline_cycles']), int(row['variant_cycles'])
    if min(ca, cb) <= 0: raise ValueError('nonpositive complete native cycles')
    row.update(baseline_over_variant=ca/cb, cycles_baseline_minus_variant=ca-cb,
               status='E_ACCEPTED_D_ANALYZED', interpretation='same-source matched measured program time; missing trigger/local fields do not establish mechanism causality; retain negative or zero effects')
    return row

def sync(ledger, out):
    if ledger.get('campaign_id') != CAMPAIGN or ledger.get('authority_commit') != AUTHORITY or ledger.get('owner') != 'E':
        raise ValueError('wrong campaign/owner/authority; historical acceptance cannot enter new results')
    out.mkdir(parents=True, exist_ok=True)
    state_path = out/'INTAKE_STATE.json'
    prior = json.loads(state_path.read_text()) if state_path.exists() else {'pair_fingerprints': {}, 'history': []}
    rows, fingerprints = [], {}
    for pair_id, declaration in ledger.get('accepted_pairs', {}).items():
        try: row = analyze_pair(pair_id, declaration, ledger.get('accepted_results', {}))
        except (ValueError, KeyError, FileNotFoundError, TypeError) as error:
            row = {k: UNKNOWN for k in FIELDS}; row.update(pair_id=pair_id, status='D_SCHEMA_OR_IDENTITY_HOLD', interpretation=str(error))
        rows.append(row); fingerprints[pair_id] = hashlib.sha256(canonical(row)).hexdigest()
    for key in set(prior['pair_fingerprints']) - set(fingerprints):
        row = {k: UNKNOWN for k in FIELDS}; row.update(pair_id=key, status='NO_LONGER_IN_E_CURRENT_PAIR_SET', interpretation='retain prior history; no current accepted effect')
        rows.append(row); fingerprints[key] = hashlib.sha256(canonical(row)).hexdigest()
    changed = fingerprints != prior['pair_fingerprints']
    for row in rows:
        if fingerprints[row['pair_id']] != prior['pair_fingerprints'].get(row['pair_id']):
            prior['history'].append(dict(row, observed_utc=dt.datetime.now(dt.timezone.utc).isoformat()))
    with (out/'RESULTS_AND_INTERPRETATION.csv').open('w', newline='') as stream:
        writer=csv.DictWriter(stream, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    state={'campaign_id':CAMPAIGN, 'status':'UPDATED' if changed else 'NO_NEW_ACCEPTED_PAIR',
           'current_E_accepted_pairs':len(ledger.get('accepted_pairs', {})),
           'D_analyzed_pairs':sum(r['status']=='E_ACCEPTED_D_ANALYZED' for r in rows),
           'pair_fingerprints':fingerprints, 'history':prior['history'],
           'no_background_poller':True, 'application_starts_by_D':0}
    state_path.write_text(json.dumps(state, indent=2)+'\n')
    return state

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[3]/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d')
    args=parser.parse_args()
    with (SHARED/'REGISTRY.lock').open() as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        ledger=json.loads((SHARED/'RUN_REGISTRY.json').read_text())[FIELD]
    state=sync(ledger, args.out)
    print(json.dumps({k:v for k,v in state.items() if k not in ['history','pair_fingerprints']}))

if __name__ == '__main__': main()
