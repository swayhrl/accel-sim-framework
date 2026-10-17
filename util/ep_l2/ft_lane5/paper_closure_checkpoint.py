"""Index accepted evidence for Lane3/6; never launch, qualify, or accept a run."""
import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from acceptance import current_manifest, load_current_authority
from package_r0 import freeze_checksums
from registry import PARALLEL, Registry, write_json

REPO = Path(__file__).resolve().parents[3]
AUTHORITY = 'f1980a84c8e637ff2050048bd11b3c1fa5362583'
CONTRACT = 'docs/ep_l2/chatgpt_handoff/paper_closure_2026_10_17_v1/THREE_GAPS_RTL_AND_MINIMAL_VALIDATION_PLAN_V1.md'
FB = 'fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pack', type=Path, required=True)
    a = p.parse_args()
    if a.pack.exists():
        raise ValueError('Preserve immutable prior revision')
    state = load_current_authority()
    manifest = current_manifest(state)
    registry = Registry().snapshot()
    rows = [r for r in manifest['rows'] if r['scientific_acceptance'] == 'CURRENT_ACCEPTED']
    a.pack.mkdir(parents=True)
    (a.pack / 'INCREMENTAL_CONTRACT.md').write_bytes(subprocess.check_output(
        ['git', 'show', AUTHORITY + ':' + CONTRACT], cwd=REPO))
    fields = ['workload', 'regime', 'profile', 'mode', 'observed_cycles', 'instructions',
              'core_source_commit', 'framework_source_commit', 'binary_sha256',
              'runtime_config_sha256', 'trace_content_sha256', 'run_key',
              'raw_log_sha256', 'original_raw_log', 'independent_review']
    with (a.pack / 'ACCEPTED_LOG_INDEX.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            run = registry['runs'].get(r['run_key'])
            review = r['independent_review']['path']
            raw = str(Path(run['result_directory']) / 'raw.log') if run else ''
            writer.writerow({**{k: r.get(k, '') for k in fields},
                             'original_raw_log': raw, 'independent_review': review})
    groups = []
    for workload in ['convolutionSeparable', 'FWT_7_21']:
        endpoints = {}
        for profile in ['B16_OFF', 'S64', 'U_CAP16', 'U_OFF', 'I_WB', 'I_META',
                        'I_WB_META', 'I_READ_HIT', 'I_MEM_ALL_DATA']:
            matched = [r for r in rows if r.get('experiment_id') == PARALLEL
                       and r['binary_sha256'] == FB and r['workload'] == workload
                       and r.get('regime') == 'H0' and r.get('profile') == profile]
            if len(matched) > 1:
                raise ValueError('Ambiguous exact-source endpoint')
            endpoints[profile] = matched[0] if matched else None
        groups.append({'workload': workload, 'binary_sha256': FB,
                       'four_organization_complete': all(endpoints[k] for k in
                           ['B16_OFF', 'S64', 'U_CAP16', 'U_OFF']),
                       'endpoints': endpoints})
    write_json(a.pack / 'RECEIPT.json', {
        'at_utc': datetime.now(timezone.utc).isoformat(), 'authority': AUTHORITY,
        'status': 'DERIVED_CURRENT_ACCEPTED_EVIDENCE_INDEX_NOT_NEW_ACCEPTANCE',
        'current_V2_binding': state['binding'], 'groups': groups,
        'accepted_rows': len(rows), 'source37_vector_anchors_remain_source37': True,
        'constraints': 'No starts, qualification reruns, binary changes, cap/deadline changes or cleanup',
        'candidate_policy': 'WAD256 Conv is exploratory. Any finite performance claim requires same-condition strong-static/necessary ablations; one unused-in-selection existing-input pair only if original budget permits.',
        'analysis_scope': 'Use absolute cycles and exact denominator identities. Do not sum overlapping windows or retry counters as elapsed time. ALL_DATA is a reference-service opportunity, not EP-L2 speedup or a mathematical bound.',
        'delivery': 'Publish exact branch SHA and verify Git bytes before installing Lane3/6 event.'})
    (a.pack / 'README.md').write_text(
        '# Lane5 incremental evidence for Lane3/6\n\n'
        'ACCEPTED_LOG_INDEX.csv locates existing raw logs and immutable independent reviews, '
        'including negative ROP40/ICNT2 and positive WAD256 Conv. Read pressure/resource '
        'tables beside each pair review; no new observer or runtime is needed.\n\n'
        'RECEIPT.json lists same-FB Conv/FWT endpoints independently. Missing endpoints '
        'remain pending; no source2309/source37 cycles fill them. The current V2 pointer '
        'and withdrawal checks remain authoritative after this historical snapshot.\n')
    freeze_checksums(a.pack)
    print(json.dumps({'pack': str(a.pack), 'accepted_rows': len(rows),
                      'generation': manifest['generation']}))


if __name__ == '__main__':
    main()
