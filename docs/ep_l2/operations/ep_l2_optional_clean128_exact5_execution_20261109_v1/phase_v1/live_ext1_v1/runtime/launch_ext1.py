#!/usr/bin/env python3
"""Detach the already staged one-point Native supervisor; never retries."""
import json,os,subprocess
from pathlib import Path
P=Path
R=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
REQ='EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
CASE='EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
def main():
 q=json.loads((N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())['registered_future_requests'][REQ]
 assert q['remaining']==1 and q['consumed']=={} and q['admitted_specs'][CASE]
 claims=json.loads((R/'control/DISPATCH_CLAIMS.json').read_bytes())['claims']
 assert set(claims)=={CASE} and claims[CASE]['request']==REQ and claims[CASE]['state']=='CLAIMED'
 log=R/'control/EXT1_RUN_NATIVE_20261110.log'
 assert not log.exists(),'existing run log; inspect before any action'
 command=[str(N/'bin/native'),'experiment','run-native',CASE,'--project','EP_L2']
 with log.open('xb') as out:
  p=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,
                     cwd='/root/workspace',start_new_session=True,close_fds=True)
 print(json.dumps({'status':'EXT1_NATIVE_SUPERVISOR_SPAWNED','supervisor_pid':p.pid,'log':str(log),'command':command,'no_auto_retry':True}))
if __name__=='__main__':main()
