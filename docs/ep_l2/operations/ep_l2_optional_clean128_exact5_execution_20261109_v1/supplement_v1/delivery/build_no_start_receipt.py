#!/usr/bin/env python3
"""Read small exact5 control files and report finite no-start checks."""
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REG = pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH = pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    reg = json.loads(REG.read_bytes())
    epoch = json.loads(EPOCH.read_bytes())
    assert epoch['native_registry_sha256'] == sha(REG)
    claims_path = ROOT/'control/DISPATCH_CLAIMS.json'
    claims = json.loads(claims_path.read_bytes())['claims']
    checks = json.loads(subprocess.check_output([sys.executable, '/tmp/ep_l2_exact5_no_start_checks.py'],
                     env={'EP_L2_TEST_RUNTIME_ROOT': str(ROOT/'runtime')}, text=True))
    points = []
    for case in sorted((ROOT/'cases').glob('*/control/FROZEN_SPEC.json')):
        spec = json.loads(case.read_bytes())
        cohort = spec['cohort']
        request = spec['science_request_id']
        if request not in ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
                           'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'):
            continue
        q = reg['registered_future_requests'][request]
        prep = case.parent/'NATIVE_PRELAUNCH_QUALIFICATION.json'
        p = json.loads(prep.read_bytes())
        assert p['status'] == 'EP_PERF_PREPARE_PASS_NO_START'
        assert p['spec_sha256'] == sha(case)
        assert q['admitted_specs'][cohort] == sha(case)
        points.append(dict(cohort=cohort, request=request, spec_sha256=sha(case),
                           prepare_receipt=str(prep), prepare_receipt_sha256=sha(prep),
                           prepare_status=p['status'], consumed=cohort in q['consumed']))
    assert len(points) == 5
    holds=[]
    for family, suffix in (('gemm','59551b01-ac15-4600-9b3d-8e0071fd802c'),
                           ('stencil','5ee40e2f-97e8-4dc8-9543-2a3fa6887e10')):
        path=ROOT/'control'/('STAGED_ADMISSION_'+family.upper()+'_'+suffix+'.json')
        receipt=json.loads(path.read_bytes())
        assert receipt['status']=='RESOURCE_HOLD_NO_NEW_CLAIM' and receipt['no_model_started']
        holds.append(dict(family=family, path=str(path), sha256=sha(path),
                          utc=receipt['utc'], cohort=receipt['cohort'],
                          status=receipt['status'],
                          required_free_bytes=receipt['admission_decision']['required_free_bytes'],
                          observed_native_free_bytes=receipt['observed_native_free_bytes'],
                          hold_reasons=receipt['admission_decision']['hold_reasons'],
                          global_restore_dedup=receipt['admission_decision']['global_restore_dedup']))
    requests={name:dict(remaining=reg['registered_future_requests'][name]['remaining'],
                        consumed=len(reg['registered_future_requests'][name]['consumed']),
                        carrier_bytes=reg['registered_future_requests'][name]['reserved_write_bytes'])
              for name in ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
                           'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1')}
    print(json.dumps(dict(schema='EP_L2_EXACT5_SUPPLEMENT_NO_START_VERIFICATION_V1',
          checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          registry_sha256=sha(REG), epoch_sha256=sha(EPOCH), epoch=epoch['epoch'],
          claims_sha256=sha(claims_path), claims=claims, requests=requests,
          points=points, point_admission_holds=holds, in_memory_checks=checks,
          scope='No model start, budget registration, refund or archive action'),
          ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
