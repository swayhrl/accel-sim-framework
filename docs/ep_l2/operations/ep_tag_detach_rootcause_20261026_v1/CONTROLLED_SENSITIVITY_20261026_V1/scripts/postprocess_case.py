#!/usr/bin/env python3
"""Offline comparison/report and predeclared E2 information decision after accepted E1."""
import sys
sys.dont_write_bytecode=True
import json,pathlib
import experiment_runtime as v
import comparison,l1_plan
def main(case):
 v.bind(case);B=v.B
 result=comparison.compare(case)
 pointpath=pathlib.Path(result['variant']['identity']['output'])/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json'
 point=v.read(pointpath)
 rows=[r for r in result['variant']['l1_last_records'].values() if r.get('scope')=='application']
 v.need(len(rows)==1,'exact application L1 scope')
 if case==v.E1:
  decision=l1_plan.recommend_e2(True,rows[0]['accesses'],rows[0]['miss_queue_full'])
  decision.update(E1_scientifically_accepted=True,E1_accepted_point_sha256=v.sha(pointpath),
     E1_raw_sha256=point['raw_sha256'],E1_spec_sha256=point['native_spec_sha256'],
     E1_comparison_sha256=v.sha(pointpath.parent/'SENSITIVITY_COMPARISON.json'),
     E1_uuid=point['uuid'],source_identity=point['source_identity'],
     decision_rule_sha256=v.sha(v.ROOT/'tools/l1_plan.py'),
     condition_frozen_before_E1_results=True)
  p=v.ROOT/'control/E2_DECISION.json'
  if p.exists():v.need(v.read(p)==decision,'decision collision')
  else:v.put(p,decision)
 else:decision=None
 return {'comparison':result,'E2_decision':decision}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('case');a=p.parse_args()
 print(json.dumps(main(a.case),ensure_ascii=False,indent=2))
