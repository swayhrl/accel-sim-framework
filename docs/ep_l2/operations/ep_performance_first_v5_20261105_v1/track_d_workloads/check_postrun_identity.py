"""Read-only closed-result identity check. No consume/accept/route writes or subprocess."""
from pathlib import Path
import hashlib,json,re,sys,argparse,os
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):
 p=Path(p);need(p.stat().st_size<=16*(1<<20),'metadata size bound');return json.loads(p.read_bytes())
def exact(r):
 need(type(r)is dict and type(r.get('path'))is str and re.fullmatch('[0-9a-f]{64}',r.get('sha256','')),'invalid ref')
 need(sha(r['path'])==r['sha256'],'closed ref drift '+r['path']);return read(r['path'])
def nonlive(pid,ticks,proc=Path('/proc')):
 need(type(pid)is int and type(ticks)is int and pid>0 and ticks>0,'invalid generation')
 try:
  t=(proc/str(pid)/'stat').read_text();fields=t[t.rfind(')')+2:].split()
 except FileNotFoundError:return True
 return int(fields[19])!=ticks or fields[0]=='Z'
def route_check(policy,current_bytes):
 prior=exact(policy['original_Main_review_ref'])
 need(prior['approved_by']=='EP-MAIN' and prior['status']=='EXACT_TWO_AUTHORIZED_FINITE_FOREIGN_INSERTIONS_OLD_NATIVE_SUFFIX_PRESERVED' and prior['reviewed_current_snapshot_ref']==policy['reviewed_current_snapshot_ref'],'not the exact original Main review')
 need(policy['scope']=='POSTRUN_CLOSED_METADATA_ONLY' and policy['new_model_authority']is False,'not a closed-only metadata scope')
 expected=Path(policy['reviewed_current_snapshot_ref']['path']).read_bytes()
 need(hashlib.sha256(expected).hexdigest()==policy['reviewed_current_snapshot_ref']['sha256'],'review snapshot drift')
 # Explicit exact snapshot includes only previously reviewed finite insertions.
 # Unknown new insertion is HOLD; this checker never auto-approves it.
 need(current_bytes==expected,'UNREVIEWED_SHARED_NATIVE_CHANGE_MAIN_INSERT_ONLY_REVIEW_REQUIRED')
 return dict(status='EXACT_PREVIOUSLY_MAIN_REVIEWED_SHARED_NATIVE',current_sha256=hashlib.sha256(current_bytes).hexdigest())
def validate(contract):
 need(contract['schema']=='EP_V5_CLOSED_RESULT_METADATA_CHECK_INPUT_V1','input schema')
 spec=exact(contract['spec_ref']);done=exact(contract['done_ref']);launch=exact(done['closed_artifact_refs']['NATIVE_LAUNCH.json']);pidmap=exact(done['closed_artifact_refs']['NATIVE_SIMULATOR_PID_AND_MAPS.json'])
 case=contract['cohort'];uid=contract['uuid'];request=contract['request']
 need(done['cohort']==spec['cohort']==case and done['uuid']==uid and done['goal']==spec['science_request_id']==request,'same request/cohort/UUID')
 need(done['spec_ref']==contract['spec_ref'] and done['source_identity']==spec['source_identity'],'Spec/Source mismatch')
 need(done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']is True and done['new_attempt_consumed']==1 and done['automatic_retry']is False,'not naturally successful consumed result')
 run=Path(done['output']);need(run.name==uid and run.parent.name=='run' and run.parent.parent.name==case,'run path identity')
 need(sha(run/'FROZEN_SPEC.json')==contract['spec_ref']['sha256'],'launch copied Spec mismatch')
 for name,r in launch['launch_capsule'].items():
  need(Path(r['path']).parent==run and Path(r['path']).name==name,'capsule path escape')
  need(sha(r['path'])==r['sha256'],'launch capsule drift')
 need(launch['dispatch_binding']['cohort']==case and launch['dispatch_binding']['spec_sha256']==contract['spec_ref']['sha256'],'dispatch identity mismatch')
 need(nonlive(pidmap['pid'],pidmap['start_ticks']),'same model generation still live')
 need(sha(spec['binary_path'])==spec['source_identity']['binary_sha256'],'accepted ELF changed')
 proof=done['syscall_proof'];need(proof['status']=='CLOSED_LOCAL_SYSCALL_INPUT_NETWORK_PROOF_PASS' and proof['no_connect']is True and proof['no_ssh_exec']is True and proof['model_pid']==pidmap['pid'],'syscall proof identity')
 syscall=done['closed_artifact_refs']['actual_file_process_network.log'];need(Path(syscall['path']).parent==run and sha(syscall['path'])==syscall['sha256'],'closed syscall bytes drift')
 rr=done['raw_stream_receipt'];need(rr['complete_compressed_stream']is True and rr['truncated']is False and rr['source_keep']is True and rr['stored_sha256']==done['raw_compressed_ref']['sha256'],'complete lossless raw receipt')
 need(Path(rr['path']).parent==run and Path(rr['path']).stat().st_size==rr['stored_bytes']and sha(rr['path'])==rr['stored_sha256'],'closed raw bytes drift')
 reg=read(contract['registry_path']);q=reg['registered_future_requests'][request];row=q['consumed'][case]
 need(row['uuid']==uid and q['admitted_specs'][case]==contract['spec_ref']['sha256']and row['done_ref']==contract['done_ref'],'consumed registry same result')
 # Original production postprocess remains responsible for full command census/numerics.
 need(contract['required_production_terminal_validation_ref']==spec['validation_module_ref'],'terminal validator bypass')
 for p,h in spec['pinned_files'].items():
  # This is code identity, never shared Native route substitution.
  need(sha(p)==h,'frozen runtime dependency drift '+p)
 policy=exact(contract['Main_shared_route_review_ref']);route=route_check(policy,Path(contract['current_shared_native_path']).read_bytes())
 return dict(status='CLOSED_RESULT_IDENTITY_RECHECK_PASS_METADATA_ONLY',request=request,cohort=case,uuid=uid,route=route,full_command_numeric_validation='UNCHANGED_PRODUCTION_VALIDATOR_REQUIRED',science_acceptance=False,new_model_authority=False,shared_Native_modified=False,registry_modified=False)
def main():
 a=argparse.ArgumentParser();a.add_argument('--contract',required=True);a.add_argument('--contract-sha',required=True);v=a.parse_args()
 need(sha(v.contract)==v.contract_sha,'caller contract pin mismatch')
 try:r=validate(read(v.contract))
 except Exception as exc:print(json.dumps(dict(status='HOLD',reason=str(exc),writes=0,new_model_authority=False)));return 2
 print(json.dumps(r,sort_keys=True));return 0
if __name__=='__main__':sys.exit(main())
