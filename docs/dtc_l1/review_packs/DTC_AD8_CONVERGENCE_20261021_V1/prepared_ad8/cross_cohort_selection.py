"""Frozen four-point arithmetic after exact accepted AE/AD provenance joins only."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(value,reason):
    if not value:raise ValueError(reason)

def select_cross_cohort(ad_results,manifest,registration):
    decision_path=Path(registration['comparator']['path'])
    require(sha(decision_path)==registration['comparator']['sha256'],'CROSS_COHORT_DECISION_CHANGED')
    decision=json.loads(decision_path.read_text())
    require(decision['BA_scoped_cross_cohort_comparator_acceptance'] is True and
            decision['BA_decision']['canonical_task']=='/root','EXPLICIT_BA_CROSS_COHORT_ACCEPTANCE_REQUIRED')
    require(len(ad_results)==2 and [p['point'] for p in manifest['points']]==['AD_GEMM','AD_Gaussian'],'EXACT_TWO_NEW_AD_POINTS_REQUIRED')
    evidence=[];ae=[]
    for record in decision['accepted_AE_receipts']:
        require(sha(record['strict_path'])==record['strict_sha256'] and
                sha(record['input_identity_path'])==record['input_identity_sha256'],'ACCEPTED_AE_IMMUTABLE_RECEIPTS_CHANGED')
        result=json.loads(Path(record['strict_path']).read_text())
        require(result['status']=='PASS_ACTUAL_REGISTERED_AG7_FULL_STRICT_EVIDENCE' and
                result['performance_accepted'] is True and result['scientific_strict_pass'] is True and
                result['attempt_uuid']==record['attempt_uuid'] and result['cycles']==record['cycles'] and
                result['BASE_cycles']==record['BASE_cycles'] and result['point']==record['point'],
                'HISTORICAL_AE_ACCEPTANCE_SCOPE_CHANGED')
        ae.append(result);evidence.append(record)
    require([x['point'] for x in ae]==['AE_GEMM','AE_Gaussian'],'EXACT_ACCEPTED_AE_ORDER')
    for result,spec in zip(ad_results,manifest['points']):
        require(result['point']==spec['point'] and result['attempt_uuid']==spec['attempt_uuid'] and
                result['status']=='PASS_ACTUAL_REGISTERED_AD8_FULL_STRICT_EVIDENCE' and
                result['performance_accepted'] is True and result['scientific_strict_pass'] is True and
                type(result['cycles']) is int and result['cycles']>0 and
                result['BASE_cycles']==spec['imported_BASE_cycles'],'BOTH_NEW_AD_WHOLE_INPUT_ACCEPTANCES_REQUIRED')
        path=Path(spec['destination'])/'STRICT.json'
        require(json.loads(path.read_text())==result,'ACTUAL_NEW_AD_STRICT_RECEIPT_REQUIRED')
        evidence.append(dict(point=spec['point'],attempt_uuid=spec['attempt_uuid'],strict_path=str(path),strict_sha256=sha(path)))
    path=REPO/'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/selection_v2.py'
    require(sha(path)=='9cda625e6e314b4e51ce9a8087e007ad60fcfeb3c82bffc6a116ddde8daa9f1f','FROZEN_SELECTION_ARITHMETIC_CHANGED')
    module=importlib.util.module_from_spec(importlib.util.spec_from_file_location('ad8_frozen_arithmetic',path))
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    rows=ae+ad_results
    speedups={arm:[Fraction(rows[i]['BASE_cycles'],rows[i]['cycles']) for i in ((0,1) if arm=='AE' else (2,3))] for arm in ('AE','AD')}
    arithmetic=module._arithmetic(speedups);arm=arithmetic['choice']
    final='K0/OO128/Tag64x8/'+('AE0/AD0' if arm=='O' else 'AE1/AD0' if arm=='AE' else 'AE0/AD1')
    return dict(status='COMPLETE_FOUR_POINT_CROSS_COHORT_SELECTION',F=final,selected_arm=arm,exact_arithmetic=arithmetic,
        own_new_AD_UUIDs=[p['attempt_uuid'] for p in manifest['points']],accepted_receipts=evidence,
        comparator_decision_sha256=sha(decision_path),wall_caps_are_not_modeled_cycle_parameters=True,
        scope='DISCOVERY_GEMM_GAUSSIAN_ONLY',no_new_primary_application_GM=True,native_numeric_claim=False)
