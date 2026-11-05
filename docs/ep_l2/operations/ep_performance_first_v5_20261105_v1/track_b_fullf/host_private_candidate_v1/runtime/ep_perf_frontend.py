"""Exact registered EP cohorts only; preserve per-case immutable engine versions."""
import importlib.util, json, os, pathlib, sys
from ep_perf_common_v2 import *


def main(args):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')
    need(len(args) == 5 and args[0] == 'experiment' and args[3:] == ['--project','EP_L2'], 'exact native EP command')
    need(args[1] in ['prepare','inspect','run-native','accept'], 'unsupported operation')
    case = args[2]
    need(case in ('EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1', 'EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1'), 'outside exact newSource F scope')
    engine=module(dict(path=str(P(__file__).with_name('ep_perf_native_wv_modes_draft.py')),sha256='a9d3420fddad95bb261b590578aff9362a34b1496c24e529be4e3e0669e9171b'),'pfv5_b1_frontend_engine')
    engine.engineering_static(read((ROOT/'cases'/case/'control/FROZEN_SPEC.json') if (ROOT/'cases'/case/'control/FROZEN_SPEC.json').exists() else P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/host_private_candidate_v1/prospective_specs')/(case+'.json')))
    registry, unused = authority()
    need(GOAL in registry['registered_future_requests'],'FRESH_EXACT_TWO_POINT_SCIENTIFIC_SCOPE_NOT_REGISTERED')
    q = registry['registered_future_requests'][GOAL]
    need(case in q['admitted_specs'], 'case not exactly registered for this Goal')
    path = ROOT/'cases'/case/'control/FROZEN_SPEC.json'
    need(sha(path) == q['admitted_specs'][case], 'registered spec changed')
    s = read(path)
    item = s['host_engine_ref']
    need(P(item['path']).is_relative_to(P(__file__).resolve().parent) and sha(item['path']) == item['sha256'], 'unqualified engine location/content')
    if args[1] == 'accept':
        return module(s['postprocess_module_ref'], 'ep_perf_exact_postprocess').postprocess(case)
    return module(item, 'ep_perf_exact_case_engine').main(args)


if __name__ == '__main__':
    try:
        print(json.dumps(main(sys.argv[1:])))
    except Exception as exc:
        print(json.dumps(dict(status='HOLD', reason=str(exc), automatic_retry=False)),file=sys.stderr)
        sys.exit(2)
