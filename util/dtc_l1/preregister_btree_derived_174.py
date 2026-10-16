#!/usr/bin/env python3
"""Freeze the six authorized Btree arms; no simulation or scheduler."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
from collect_service_closure_attempts import sha
from collect_service_closure_matched import effective_options, contract_checks
from collect_btree_derived_174 import BUNDLE


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2); f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--admission', type=Path, required=True)
    ap.add_argument('--producer-review', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args()
    admission = a.admission.resolve(); gate = json.loads(admission.read_text())
    assert gate['status'] == 'DERIVED_INPUT_ADMITTED_FOR_BTRE_E_LIST_CONTRACT' and gate['bundle_sha256'] == BUNDLE and all(gate['checks'].values())
    producer = a.producer_review.resolve()
    proposal = json.loads((producer/'SIX_ARM_PROPOSAL.json').read_text())
    fw = Path(__file__).resolve().parents[2]
    original_plan = fw/'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r2/REGISTERED_ROWS_V2.tsv'
    assert sha(original_plan) == '281b2d22ace3bbf105711473516f075fc11c495a1d6c214d9f4a3e42414892e1'
    out = a.output_dir.resolve(); out.mkdir(exist_ok=False)
    for name in ['attempts', 'specs', 'execution_sources']:
        (out/name).mkdir()
    shutil.copytree(producer/'proposed_config', out/'proposed_config')
    execution_names = ['service_closure_attempt.py', 'run_btree_derived_174.py',
                       'collect_btree_derived_174.py', 'collect_service_closure_attempts.py',
                       'collect_service_closure_matched.py', 'service_closure_scientific_disposition.py']
    for name in execution_names:
        shutil.copyfile(Path(__file__).with_name(name), out/'execution_sources'/name)
        (out/'execution_sources'/name).chmod(0o444)
    owned = Path(gate['owned_input_directory'])
    identity = json.loads((producer/'INPUT_IDENTITY.json').read_text())
    files = identity['identity_contract']['files']
    head = subprocess.check_output(['git', '-C', str(fw), 'rev-parse', 'HEAD'], text=True).strip()
    specs, rows = {}, []
    for source_arm in ['B16-N', 'TC80-N', 'TRAD96/C+', 'IO256', 'OO128', 'IO128']:
        proposed = proposal['arms'][source_arm]
        assert sha(Path(proposed['template']['path'])) == proposed['template']['sha256']
        arm = 'TRAD96' if source_arm == 'TRAD96/C+' else source_arm
        finite = arm in ['IO256', 'OO128', 'IO128']
        mode = 'io' if arm.startswith('IO') else 'oo' if arm == 'OO128' else 'base'
        configs = [dict(path=str(out/c['relative_path']), sha256=c['sha256']) for c in proposed['configs']]
        spec = dict(label='BTREE_E_LIST_V1_'+arm.replace('-', '_'),
                    workload='Btree_CONDITIONAL_E_LIST_V1', arm=arm,
                    phase='DERIVED_QUALIFIED_SIX_ARM',
                    classification='CONDITIONAL_E_LIST_DERIVED_INPUT_SIMULATION_NOT_CAPTURE_OR_NATIVE_EQUIVALENCE',
                    core=proposed['core'], build_framework=proposed['build_framework'],
                    orchestrator_framework=head, runtime=proposed['runtime']['path'],
                    runtime_sha256=proposed['runtime']['sha256'], finite_service=finite,
                    dtc_mode=mode, expected_mode=2 if mode == 'io' else 3 if mode == 'oo' else 1,
                    input_bundle_sha256=BUNDLE, input_interpretation=gate['input_interpretation'],
                    admission_receipt=str(admission), admission_receipt_sha256=sha(admission),
                    producer_proposal_sha256=sha(producer/'SIX_ARM_PROPOSAL.json'),
                    trace_list=str(owned/'kernelslist.g'), trace_list_sha256=sha(owned/'kernelslist.g'),
                    expected_instructions=444467849, expected_kernel_names=['findRangeK', 'findK'],
                    expected_kernel_instructions=[217350912, 227116937],
                    members=[dict(path=str(owned/f['name']), sha256=f['sha256'], bytes=f['bytes']) for f in files if f['name'] != 'kernelslist.g'],
                    configs=configs)
        assert sha(Path(spec['runtime'])) == spec['runtime_sha256']
        vector = proposed['resource_vector']
        if finite:
            spec['expected_active_pib'] = vector['active_PIB']
        else:
            spec.update(expected_dl1=proposed['effective_options']['-gpgpu_cache:dl1'][0],
                        expected_pib=vector['active_PIB'], expected_mshr=vector['MSHR'])
        actual = effective_options(spec)
        assert actual == proposed['effective_options'], arm
        assert all(actual.get(k) == v for k, v in proposal['common_required_options'].items())
        path = out/'specs'/(spec['label']+'.json'); save(path, spec); path.chmod(0o444)
        specs[arm] = spec
        rows.append(dict(label=spec['label'], arm=arm, workload=spec['workload'],
                         input_bundle_sha256=BUNDLE, spec_path=str(path), spec_sha256=sha(path),
                         gate='INDEPENDENT_A_ADMISSION_AND_FROZEN_SERVICE',
                         action='PREREGISTERED_BEFORE_ANY_NEW_INPUT_PERFORMANCE'))
    assert len(specs) == 6 and all(len({json.dumps(s[k], sort_keys=True) for s in specs.values()}) == 1 for k in ['members', 'trace_list', 'trace_list_sha256', 'input_bundle_sha256', 'expected_instructions', 'expected_kernel_names'])
    matched = contract_checks(specs['IO128'], specs['OO128'], effective_options(specs['IO128']), effective_options(specs['OO128']))
    assert all(matched.values()), matched
    with (out/'REGISTERED_DERIVED_ROWS.tsv').open('x') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
    save(out/'PAIRING_CONTRACT.json', dict(
        utc=datetime.now(timezone.utc).isoformat(), status='PREREGISTERED_SIX_SAME_INPUT_ARMS_BEFORE_PERFORMANCE',
        input_bundle_sha256=BUNDLE, plan_sha256=sha(out/'REGISTERED_DERIVED_ROWS.tsv'),
        admission_sha256=sha(admission), producer_proposal_sha256=sha(producer/'SIX_ARM_PROPOSAL.json'),
        effective_options={arm: effective_options(s) for arm, s in specs.items()},
        resource_vectors={('TRAD96' if arm == 'TRAD96/C+' else arm): s['resource_vector'] for arm, s in proposal['arms'].items()},
        declared_design_differences=proposal['declared_effective_option_differences'],
        matched128_contract_checks=matched,
        execution_sources={p.name: sha(p) for p in (out/'execution_sources').iterdir()},
        common_budget='All six new arms cap32768. Historical B16/TC80 cap8192 cannot be new denominators or isolate cross-input address effects.',
        input_scope='One conditional E-list bundle, both complete ordered kernels; no capture/native equivalence, mixed-input ratios or aggregates.',
        necessity='Exactly the six user-authorized capacity/resource/primary/matched128 arms; no WAIT128, 2D, LUD or modern addition.',
        service_contract='Unchanged conventional and qualified finite implementations. Logical tags are coverage, not extra data. DTC ordinary16KiB side path and original96KiB shared remain charged; no equal-area claim.',
        launch_authority='Existing174 authority and CRITICAL_LAUNCH.lock; bounded auxiliary submission only, no second persistent dispatcher.'))
    print(json.dumps(dict(plan=str(out/'REGISTERED_DERIVED_ROWS.tsv'), rows=6, matched128_contract_pass=True)))


if __name__ == '__main__':
    main()
