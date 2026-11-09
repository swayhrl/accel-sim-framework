"""One exact family Native entry; all starts consume before model fork."""
import json, os, sys
from ep_perf_common_v2 import *

def main(args):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'sole Native entry required')
    need(len(args) == 5 and args[0] == 'experiment' and args[3:] == ['--project', 'EP_L2'],
         'exact Native command')
    need(args[1] in ('prepare', 'inspect', 'run-native', 'accept'), 'unknown operation')
    case = args[2]
    need(case in ('EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1', 'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1', 'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1'), 'outside family cohorts')
    registry, unused = authority()
    need(GOAL in registry['registered_future_requests'], 'family unregistered')
    q = registry['registered_future_requests'][GOAL]
    path = ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'
    need(path.exists() and q['admitted_specs'].get(case) == sha(path), 'immutable Spec not registered')
    s = read(path)
    item = s['host_engine_ref']
    need(P(item['path']).is_relative_to(P(__file__).resolve().parent) and
         sha(item['path']) == item['sha256'], 'Host engine location/content')
    if args[1] == 'accept':
        return module(s['postprocess_module_ref'], 'exact5_postprocess').postprocess(case)
    return module(item, 'exact5_case_engine').main(args)

if __name__ == '__main__':
    try:
        print(json.dumps(main(sys.argv[1:])))
    except Exception as exc:
        print(json.dumps(dict(status='HOLD', reason=str(exc), automatic_retry=False)), file=sys.stderr)
        sys.exit(2)
