"""Exact registered EP cohorts only; preserve per-case immutable engine versions."""
import importlib.util, json, os, pathlib, sys
from ep_perf_common_v2 import *


def main(args):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')
    need(len(args) == 5 and args[0] == 'experiment' and args[3:] == ['--project','EP_L2'], 'exact native EP command')
    need(args[1] in ['prepare','inspect','run-native','accept'], 'unsupported operation')
    case = args[2]
    need(case in ('EP_PERF_PF_DRAM_FWT_S_1020_V1', 'EP_PERF_PF_DRAM_FWT_WV_ZERO_RO_1020_V1', 'EP_PERF_PF_DRAM_FWT_S_1275_V1', 'EP_PERF_PF_DRAM_FWT_WV_ZERO_RO_1275_V1', 'EP_PERF_PF_DRAM_FWT_S_1700_V1', 'EP_PERF_PF_DRAM_FWT_WV_ZERO_RO_1700_V1', 'EP_PERF_PF_DRAM_GEMM_S_1020_V1', 'EP_PERF_PF_DRAM_GEMM_WV_ZERO_RO_1020_V1', 'EP_PERF_PF_DRAM_GEMM_S_1275_V1', 'EP_PERF_PF_DRAM_GEMM_WV_ZERO_RO_1275_V1', 'EP_PERF_PF_DRAM_GEMM_S_1700_V1', 'EP_PERF_PF_DRAM_GEMM_WV_ZERO_RO_1700_V1', 'EP_PERF_PF_DRAM_VECTOR4M_S_1275_V1', 'EP_PERF_PF_DRAM_VECTOR4M_F_1275_V1', 'EP_PERF_PF_DRAM_VECTOR4M_S_1700_V1', 'EP_PERF_PF_DRAM_VECTOR4M_F_1700_V1'), 'cohort outside approved DRAM family')
    registry, unused = authority()
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
