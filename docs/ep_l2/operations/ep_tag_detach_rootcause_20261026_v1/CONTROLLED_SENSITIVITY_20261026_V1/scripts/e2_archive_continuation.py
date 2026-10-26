#!/usr/bin/env python3
"""Exact E2 COPY_ONLY continuation within its still-held whole-operation reservation."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,os,resource,time
import experiment_runtime as v
import e2_postrun_entry_adapter as old
P=pathlib.Path
WRAPPER='''#!/bin/sh
set -eu
if [ "$#" -ge 3 ] && [ "$1:$2:$3" = "result:archive:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1" ]; then
 exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/e2_archive_continuation.py "$@"
fi
exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/prior_postrun_native_entry.sh "$@"
'''
PROCESS_AS=256*2**20
TOTAL_RAM_ENVELOPE=2*PROCESS_AS
LOCAL_GROWTH_CAP=128*2**20
def footprint(root):
 rows=[p for p in root.rglob('*') if p.is_file() and not p.is_symlink()]
 return sum(p.stat().st_size for p in rows),sum(p.stat().st_blocks*512 for p in rows)
def main(args):
 v.need(args==['result','archive',v.E2,'--project','EP_L2'],'exact E2 COPY_ONLY command only')
 os.sched_setaffinity(0,{16});os.nice(10)
 resource.setrlimit(resource.RLIMIT_AS,(PROCESS_AS,PROCESS_AS))
 v.bind(v.E2);B=v.B
 prior=v.ROOT/'tools/prior_postrun_native_entry.sh'
 v.need(v.sha(prior)=='c3c2d8b3405ea631930d1d938ab6ecc4b58f7242b5654b06a0a2403df226d8c6','postrun prior snapshot drift')
 v.need(prior.read_bytes()==old.WRAPPER.encode(),'prior accept/archive wrapper drift')
 v.need(v.sha(v.ROOT/'tools/e2_postrun_entry_adapter.py')=='78f9165010f5be5cf76f86753055b0018b82991d110a31477950bdea1ad401e0','postrun adapter source drift')
 v.need((v.N/'bin/native').read_bytes()==WRAPPER.encode(),'archive continuation entry drift')
 old.WRAPPER=WRAPPER
 s=old.postrun_pins()
 done=v.read(v.LED/(v.E2+'.DONE.json'));out=P(done['output'])
 point=v.read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
 v.need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'natural completion required')
 v.need(point['status']=='EP_MEMORY_PATH_SENSITIVITY_CASE_ACCEPTED' and point['uuid']==done['uuid'] and point['raw_sha256']==done['raw_sha256']==v.sha(out/'raw.log') and point['native_spec_sha256']==v.sha(B/'control/FROZEN_SPEC.json'),'accepted raw/spec/uuid join required')
 maps=v.read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 try:
  current=v.info(maps['pid'])
  v.need(current['start_ticks']!=maps['start_ticks'],'model still live')
 except (FileNotFoundError,ProcessLookupError):pass
 source_bytes=footprint(out)[0]
 v.need(source_bytes<=32*v.MIB and source_bytes*2+32*v.MIB<=LOCAL_GROWTH_CAP,'restore incremental envelope too large')
 reg=v.read(v.REG);row=reg['registered_future_requests'][v.E2]
 v.need(row['state']=='NATURAL_COMPLETE_PENDING_ACCEPTANCE_ARCHIVE' and row['consumed']==1 and row['uuid']==done['uuid'] and row['reserved_write_bytes']==s['advertised_peer_reservation_bytes']==3758096384 and row['actual_write_restore_envelope_bytes']==536870912,'whole-operation reservation must still be held')
 peer_before={k:r for k,r in reg['registered_future_requests'].items() if k!=v.E2}
 initial=footprint(B)
 original_resources=v.resources
 old_admission=original_resources(runtime=False)
 log=B/'control/ARCHIVE_CONTINUATION_RESOURCE_SAMPLES.jsonl'
 def continuation_resources(runtime=False):
  # No new model admission. This is completion of the already consumed, still-reserved operation.
  r=original_resources(runtime=True)
  v.need(r['consistent_snapshot'] and r['disk_pass'] and r['RAM_pass'],'COPY_ONLY actual-headroom HOLD')
  v.need(r['host_MemAvailable_bytes']>=64*v.GIB+TOTAL_RAM_ENVELOPE and r['cgroup_effective_headroom_bytes']>=48*v.GIB+TOTAL_RAM_ENVELOPE,'COPY_ONLY additional process RAM margin HOLD')
  current=footprint(B)
  growth=[max(0,current[i]-initial[i]) for i in [0,1]]
  v.need(max(growth)<=LOCAL_GROWTH_CAP,'COPY_ONLY local increment hard cap')
  r.update(resource_phase='RESERVED_POSTRUN_COPY_ONLY_CONTINUATION',reservation_held=True,new_model_admission=False,process_AS_cap_bytes=PROCESS_AS,maximum_concurrent_process_RAM_envelope_bytes=TOTAL_RAM_ENVELOPE,additional_local_write_cap_bytes=LOCAL_GROWTH_CAP,observed_local_growth_logical_allocated_bytes=growth)
  with log.open('a') as f:f.write(json.dumps(r,sort_keys=True)+'\n')
  return r
 v.resources=continuation_resources
 before=continuation_resources()
 proof={'schema':'EP_E2_RESERVED_COPY_ONLY_CONTINUATION_V1','status':'CONTINUATION_ACTUAL_HEADROOM_PASS_NOT_NEW_MODEL_ADMISSION',
 'cohort':v.E2,'uuid':done['uuid'],'raw_sha256':done['raw_sha256'],'spec_sha256':point['native_spec_sha256'],
 'adapter_sha256':v.sha(__file__),'entry_sha256':v.sha(v.N/'bin/native'),'prior_entry_sha256':v.sha(prior),
 'source_bytes_before_archive':source_bytes,'model_process_exited':True,
 'own_registered_reservation_bytes_before':row['reserved_write_bytes'],'original_write_envelope_bytes':row['actual_write_restore_envelope_bytes'],
 'additional_local_write_cap_bytes':LOCAL_GROWTH_CAP,'per_process_AS_cap_bytes':PROCESS_AS,'maximum_concurrent_process_RAM_envelope_bytes':TOTAL_RAM_ENVELOPE,
 'new_model_or_help_forks':0,'stage_change_only':True,'old_full_model_admission_snapshot':old_admission,
 'actual_continuation_snapshot':before,'peer_registry_mutations_requested':0,
 'scientific_acceptance_granted_by_adapter':False}
 proofpath=B/'control/ARCHIVE_CONTINUATION_STAGE_PROOF.json'
 v.need(not proofpath.exists(),'continuation already attempted; review partial archive before COPY_ONLY resume')
 v.put(proofpath,proof)
 import archive_results
 result=archive_results.archive(v.E2)
 current=footprint(B);v.need(max(max(0,current[i]-initial[i]) for i in [0,1])<=LOCAL_GROWTH_CAP,'final local increment cap')
 regafter=v.read(v.REG);own=regafter['registered_future_requests'][v.E2]
 v.need(own['state']=='CLOSED' and own['reserved_write_bytes']==0,'release only after archive and two restores')
 # Concurrent peer owners may legitimately progress; no assertions that their rows stay frozen in time.
 v.put(B/'control/ARCHIVE_CONTINUATION_CLOSEOUT.json',{'status':'PASS','uuid':done['uuid'],'stage_proof_sha256':v.sha(proofpath),'local_growth_logical_allocated_bytes':[max(0,current[i]-initial[i]) for i in [0,1]],'additional_local_write_cap_bytes':LOCAL_GROWTH_CAP,'own_final_state':own['state'],'own_final_reserved_write_bytes':0,'peer_registry_writes_by_adapter':0,'new_model_or_help_forks':0})
 return result
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as exc:print(json.dumps({'status':'HOLD','reason':str(exc),'automatic_scientific_retry':False}),file=sys.stderr);sys.exit(2)
