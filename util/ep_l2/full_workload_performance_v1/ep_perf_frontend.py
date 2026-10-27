"""Exact registered EP cohorts only; preserve per-case immutable engine versions."""
import importlib.util, json, os, pathlib, sys
from ep_perf_common import *


def main(args):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')
    need(len(args) == 5 and args[0] == 'experiment' and args[3:] == ['--project','EP_L2'], 'exact native EP command')
    need(args[1] in ['prepare','inspect','run-native'], 'unsupported operation')
    case = args[2]
    registry, unused = authority()
    q = registry['registered_future_requests'][GOAL]
    need(case in q['admitted_specs'], 'case not exactly registered for this Goal')
    path = ROOT/'cases'/case/'control/FROZEN_SPEC.json'
    need(sha(path) == q['admitted_specs'][case], 'registered spec changed')
    s = read(path)
    item = s['host_engine_ref']
    need(P(item['path']).is_relative_to(ROOT/'tools') and sha(item['path']) == item['sha256'], 'unqualified engine location/content')
    return module(item, 'ep_perf_exact_case_engine').main(args)


if __name__ == '__main__':
    try:
        print(json.dumps(main(sys.argv[1:])))
    except Exception as exc:
        print(json.dumps(dict(status='HOLD', reason=str(exc), automatic_retry=False)),file=sys.stderr)
        sys.exit(2)
