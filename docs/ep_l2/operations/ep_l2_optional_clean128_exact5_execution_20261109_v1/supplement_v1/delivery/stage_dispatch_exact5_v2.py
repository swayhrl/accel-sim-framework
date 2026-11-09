#!/usr/bin/env python3
"""Stage one authorized, unconsumed exact5 point; this file never starts a model."""
import importlib.util
import json
import pathlib
import sys
import uuid

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
FAMILIES = {
    'gemm': ['EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1',
             'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1',
             'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1'],
    'stencil': ['EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
                'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'],
}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in FAMILIES or sys.argv[2] not in FAMILIES[sys.argv[1]]:
        raise SystemExit('usage: stage_dispatch_exact5_v2.py gemm|stencil EXACT_COHORT')
    family, case = sys.argv[1:]
    host = ROOT/'runtime'/('host_'+family+'_bound_v2')
    sys.path.insert(0, str(host))
    common = load(host/'ep_perf_common_v2.py', 'exact5_stage_common_'+family)
    engine = load(host/'ep_perf_native_wv_modes_draft.py', 'exact5_stage_engine_'+family)
    spec_path = ROOT/'cases'/case/'control/FROZEN_SPEC.json'
    s = common.read(spec_path)
    request = s['science_request_id']
    assert s['cohort'] == case and (family == 'gemm') == ('GEMM' in case)
    claims_path = ROOT/'control/DISPATCH_CLAIMS.json'
    binding_path = ROOT/'control/dispatch_bindings'/(case+'.json')
    with common.locked(common.GLOBAL_MAIN_ADMISSION_LOCK):
        registry, unused = common.authority()
        q = registry['registered_future_requests'][request]
        assert q['admitted_specs'][case] == common.sha(spec_path)
        assert case not in q['consumed'] and q['remaining'] > 0
        assert (ROOT/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json').exists()
        claims = common.read(claims_path)['claims']
        assert case not in claims and not binding_path.exists()
        resource = common.module(s['resource_module_ref'], 'exact5_stage_resources_'+family)
        before = resource.snapshot()
        assert not before.get('foreign_metadata_errors') and before['current_scope_registered']
        assert before['true164_mount_verified']
        occupied = set(before['occupied_model_or_claim_cpus'])
        available = [cpu for cpu in before['cpu_allowed'] if cpu >= 128 and cpu not in occupied]
        if not available:
            print(json.dumps({'status':'RESOURCE_HOLD_NO_CPU_NO_CLAIM','cohort':case}))
            return 2
        session = str(uuid.uuid4())
        binding = dict(cohort=case, controller_session=session, host_cpu=available[0],
                       spec_sha256=q['admitted_specs'][case])
        claim = dict(request=request, cohort=case, state='CLAIMED', host_cpu=available[0],
                     spec_sha256=q['admitted_specs'][case],
                     estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],
                     remaining_write_bytes=s['limits']['result_bytes'])
        common.put(binding_path, binding, True)
        staged = dict(claims)
        staged[case] = claim
        common.put(claims_path, {'claims':staged})
        try:
            receipt = engine.resource_gate(s, binding)
        except Exception as exc:
            # Only this newly created claim and binding are removed. Peers retain
            # their exact bytes, CPU assignments, PID identities and generations.
            common.put(claims_path, {'claims':claims})
            binding_path.unlink()
            raw_reason = str(exc)
            decision = (json.loads(raw_reason.split(':',1)[1])
                        if raw_reason.startswith('RESOURCE_ADMISSION_HOLD:') else None)
            hold = dict(status='RESOURCE_HOLD_NO_NEW_CLAIM', utc=common.now(), cohort=case,
                        request=request, controller_session=session,
                        reason=decision['hold_reasons'] if decision else raw_reason,
                        admission_decision=decision,
                        observed_native_free_bytes=before['native_free_bytes'],
                        registry_sha256=before['registry_sha256'], no_model_started=True)
            common.put(ROOT/'control'/('STAGED_ADMISSION_'+family.upper()+'_'+session+'.json'),hold,True)
            print(json.dumps(hold,separators=(',',':')))
            return 2
        reserve = common.publish_own_write_carrier(staged)
        result = dict(status='STAGED_AND_ADMITTED_NO_CONSUMPTION', cohort=case,
                      request=request, controller_session=session, host_cpu=available[0],
                      reserve_bytes=reserve, admission_ref=receipt, no_model_started=True)
        common.put(ROOT/'control'/('STAGED_ADMISSION_'+family.upper()+'_'+session+'.json'),result,True)
        print(json.dumps(result,separators=(',',':')))
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
