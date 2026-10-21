"""Dry preview by default; --adopt uses the published original E Coordinator.

Only the E owner calls --adopt after source publication, CLIENT rebinding and
actual controller/PID/lease readback. Never swaps CLIENT or edits runtime files.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
REGISTRY=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
FIELD='mechanism_study_20261019_v1'

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--adopt',action='store_true');args=parser.parse_args()
 raw=REGISTRY.read_bytes();data=json.loads(raw);item=data[FIELD]
 loader=importlib.util.spec_from_file_location('capacity_policy_preview',HERE/'candidate_runtime/capacity_policy.py')
 policy=importlib.util.module_from_spec(loader);loader.loader.exec_module(policy)
 preview=copy.deepcopy(item);changed=policy.amend(preview,HERE/'USER_APPROVAL.json',time.time())
 if args.adopt:
  sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
  import coordinator
  coordinator.tooling_binding()
  answer=coordinator.Coordinator().adopt_capacity_diagnostic(HERE/'USER_APPROVAL.json')
 else:
  answer=dict(status='READ_ONLY_PREVIEW',changed_if_adopted=changed,registry_mutated=False,
       registry_sha256=hashlib.sha256(raw).hexdigest(),actual_starts=item['actual_starts'],
       proposed_limits=policy.effective_limits(preview),original_allocations_preserved=True,
       original_unstarted_four_frozen_for_this_batch=True,controller=item['controller'])
 print(json.dumps(answer,indent=2))

if __name__=='__main__':main()
