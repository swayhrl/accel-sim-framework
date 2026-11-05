"""Read-only Main completion audit. No models, registry mutation, trace body scan or restore."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,tarfile,uuid
C=Path(__file__).resolve().parent
N=Path('/root/data/ep_l2_dtc_l1_native_v2')
REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
REQUESTS={'A':'EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1','B':'EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1','D':'EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1'}
BUDGETS={'A':3,'B':2,'D':3}
HARD={'A':28800,'B':7200,'D':259200}
TERMINAL={'CLOSED_ACCEPTED','CLOSED_UNACCEPTED'}
def need(x,m):
 if not x:raise ValueError(m)
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def exact(r):
 need(sha(r['path'])==r['sha256'],'immutable evidence drift '+r['path'])
 return read(r['path'])
def live(pid,ticks):
 p=Path('/proc')/str(pid)/'stat'
 try:
  a=p.read_text().rsplit(')',1)[1].split()
  return int(a[19])==ticks and a[0]not in ['Z','X']
 except FileNotFoundError:return False
def authority():
 for unused in range(5):
  h=sha(REG);r=read(REG);e=read(EPOCH)
  if h==sha(REG)==e['native_registry_sha256']:return r,e
 raise ValueError('authority transitioning; resample, never infer failure')
def archive_audit(cohort,row):
 receipt=exact(row['archive_receipt_ref']);manifest=exact(receipt['manifest_ref'])
 need(receipt['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS','archive qualification')
 need(receipt['cohort']==manifest['cohort']==cohort and receipt['uuid']==manifest['uuid']==row['uuid'],'archive cohort/UUID')
 ar=receipt['archive_ref'];path=Path(ar['path'])
 need(path.is_relative_to('/root/share/mnt164')and path.is_file(),'not genuine164 archive path')
 need(sha(path)==ar['sha256']==manifest['archive_sha256'],'current full archive SHA')
 need(path.stat().st_size==manifest['archive_bytes'],'archive size')
 rows=manifest['members'];by={r['member']:r for r in rows}
 need(len(by)==len(rows)and all(not Path(k).is_absolute()and '..'not in Path(k).parts for k in by),'archive member namespace')
 with tarfile.open(path,'r:')as t:
  actual=t.getmembers();need(len(actual)==len(by)and {r.name for r in actual}==set(by),'full archive member population')
  for x in actual:
   need(x.isfile()and not x.issym()and not x.islnk(),'unsupported archived member')
   r=by[x.name];need(x.size==r['bytes'],'member size')
   h=hashlib.sha256()
   with t.extractfile(x)as f:
    for b in iter(lambda:f.read(1<<20),b''):h.update(b)
   need(h.hexdigest()==r['sha256'],'archived body SHA '+x.name)
 need('FROZEN_SPEC.json'in by and 'NATIVE_EXIT.json'in by and 'raw.log.gz'in by,'mandatory archived scientific artifacts missing')
 need(by['FROZEN_SPEC.json']['sha256']==manifest_spec_sha(cohort),'archived frozen Spec')
 done=exact(row['done_ref'])
 need(by['NATIVE_EXIT.json']['sha256']==row['done_ref']['sha256']and by['raw.log.gz']['sha256']==done['raw_compressed_ref']['sha256'],'archived DONE/raw binding')
 rs=receipt['native_restores'];need(len(rs)==2 and len({x['target']for x in rs})==2 and {x['restore_label']for x in rs}=={'FIRST','INDEPENDENT'},'two distinct fresh Native restorations')
 for x in rs:
  need(x['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'and x['archive_sha256']==ar['sha256'],'Native full-SHA restoration')
  need(x['file_count']==len(rows)and x['logical_bytes']==sum(y['bytes']for y in rows),'restored full manifest population')
  need(x['source_keep']is True and x['permanent_scientific_source_deleted']is False,'restoration Source KEEP')
 commit=read(path.parent/'COMMIT.json')
 need(commit['cohort']==cohort and commit['uuid']==row['uuid']and commit['commit_last']is True,'same object COMMIT')
 need(commit['archive_ref']['sha256']==ar['sha256']and commit['manifest_ref']['sha256']==receipt['manifest_ref']['sha256'],'COMMIT whole object hashes')
 return dict(archive_ref=ar,manifest_ref=receipt['manifest_ref'],members=len(rows),whole_and_every_member_current_SHA=True,two_original_independent_Native_restores_verified=True,additional_Native_restores=0,Source_KEEP=True)
_SPEC_SHA={}
def manifest_spec_sha(c):return _SPEC_SHA[c]
def cell_audit(p,z,q,family):
 s=exact(p['spec_ref']);r=q['consumed'][p['cohort']];cohort=p['cohort']
 need(r.get('consumed',r.get('charged',0))==1,'one consumed start')
 need(q['admitted_specs'][cohort]==p['spec_ref']['sha256'],'official Spec admission')
 need(s['source_identity']==family['Source5']==q['source_identity'],'exact Source5')
 need(s['science_request_id']==q['request']==z['request_id']and s['cohort']==cohort,'exact request/cohort')
 need(s['application_budget']==s['approved_launches']==1 and s['automatic_retry']is False and s['source_keep']is True,'one-start no retry KEEP')
 need(s['limits']['wall_seconds']==HARD[p['group']],'signed wide hard wall')
 need(len(s['expected_effective_options'])==(282 if p['group']=='D'else 283),'full option population')
 need(s['expected_effective_options']['-trace']==s['trace_entry'],'exact trace binding')
 binding=exact(s['input_binding_ref']);commands=binding.get('expectedcommands',binding.get('all_commands'))
 need(type(commands)is list and len(commands)>0,'complete frozen commandlist population')
 need(sha(s['trace_entry'])==binding['literal_commandlist_sha256'],'small current literal commandlist SHA')
 need(s.get('command_count',len(commands))==len(commands),'frozen command count')
 need(r['state']in TERMINAL,'not terminal '+cohort)
 done=exact(r['done_ref']);intent=exact(r['intent_ref'])
 need(done['uuid']==intent['uuid']==r['uuid']and done['cohort']==intent['cohort']==cohort,'consumed intent/DONE identity')
 need(done['new_attempt_consumed']==intent['consumed_before_launcher_fork']==1,'consume before fork')
 need(done['automatic_retry']is False and intent['automatic_retry']is False,'no automatic model retry')
 need(done['source_identity']==intent['source_identity']==s['source_identity']and done['spec_ref']['sha256']==p['spec_ref']['sha256']==intent['spec_ref']['sha256'],'consumed Source/Spec')
 out=Path(done['output']);launch=read(out/'NATIVE_LAUNCH.json');maps=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 need(not live(maps['pid'],maps['start_ticks'])and not live(launch['launcher_pid'],launch['launcher_start_ticks']),'consumed model or launcher generation still live')
 need(maps['actual_AS_limit_bytes']==s['limits']['AS_bytes']and maps['actual_RSS_monitor_limit_bytes']==s['limits']['RSS_bytes'],'actual signed Host limits')
 need(maps['boot_id']==s['native_boot_id']and maps['mnt_namespace']==s['native_mount_namespace'],'actual Native domain')
 need(maps['actual_environment_exact']is True and maps['environment']==launch['environment']==intent['environment'],'actual environment')
 need(maps['cmdline']==launch['model_argv']==intent['model_argv']and maps['affinity']==[launch['dispatch_binding']['host_cpu']],'actual model argv/CPU')
 for name,item in launch['launch_capsule'].items():need(sha(out/name)==item['sha256'],'sealed launch capsule drift')
 for item in done['closed_artifact_refs'].values():need(sha(item['path'])==item['sha256'],'closed original process evidence drift')
 need(sha(done['raw_compressed_ref']['path'])==done['raw_compressed_ref']['sha256'],'current original compressed raw SHA')
 result=dict(cohort=cohort,group=p['group'],state=r['state'],uuid=r['uuid'],Source5=s['source_identity'],spec_ref=p['spec_ref'],mode=s['mode'],actual_geometry=s.get('geometry'),complete_declared_command_count=len(commands),Source_KEEP=True)
 if r['state']=='CLOSED_ACCEPTED':
  point=exact(r['accepted_point_ref']);bundle=exact(r['validation_ref'])
  need(done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']is True,'accepted model natural exit0')
  need(point['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED'and point['hardware_drained']is True and bundle['hardware_drained']is True,'accepted complete hardware drain')
  need(point['uuid']==r['uuid']and point['cohort']==bundle['cohort']==cohort and point['source_identity']==bundle['source_identity']==s['source_identity'],'accepted point identity')
  need(point['input_identity_sha256']==bundle['input_identity_sha256']==s['input_identity_sha256'],'accepted exact input')
  need(point['spec_ref']['sha256']==p['spec_ref']['sha256']and point['mode']==s['mode'],'accepted immutable Spec/mode')
  need(point['cycles']==bundle['cycles']>0 and point['instructions']==bundle['instructions']==s['expected_instructions'],'cycles/instruction population')
  need(point['CTA']==bundle['CTA']==s['expected_CTA']and point['kernel_count']==bundle['kernel_count']==len(s['expected_kernel_launches']),'CTA and full kernel population')
  app=bundle['application'];need(app['actual_options']==s['expected_effective_options'],'every effective option exact')
  need(app['ordered_kernel_catalog']==[[x['uid'],x['name']]for x in s['expected_kernel_launches']],'complete ordered kernel catalog')
  need(bundle['raw_stored_sha256']==done['raw_compressed_ref']['sha256'],'numeric qualification same original raw')
  math=bundle['math_binding'];need(math['numeric_body_sha256']=='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817'and math['frozen_final_suffix_sha256']=='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432','unchanged numerical protocol body')
  if p['group']=='A':
   amendment=exact(point['consumer_amendment_ref']);compat=exact(amendment['metadata_compatibility_approval_ref'])
   need(amendment['approved_by']=='EP-MAIN'and amendment['new_model_starts']==0 and amendment['model_retry']is False and amendment['budget_refund']is False,'exact closed consumer amendment')
   need(r['validation_hold_ref']==r['old_validation_hold_ref']==amendment['original_validation_hold_refs'][cohort]==point['original_validation_hold_ref'],'old HOLD evidence preserved')
   need(compat['Source5']==s['source_identity']and compat['explicit_Main_closed_consumer_approval']is True,'exact canonical Source metadata compatibility')
   repro=exact(compat['Main_independent_build_review_ref'])
   need(repro['Source7b4_tracked_count']==832 and len(repro['objects'])==142 and repro['archive_count']==8 and repro['actual_ELF_SHA256']==s['source_identity']['binary_sha256'],'strict Source/whole-ELF provenance')
   result['A_original_HOLD_and_exact_metadata_amendment_preserved']=True
  result.update(cycles=point['cycles'],instructions=point['instructions'],CTA=point['CTA'],kernel_count=point['kernel_count'],hardware_drained=True,full_declared_commandlist_validation='ORIGINAL_FROZEN_CONSUMER_SCAN_RETAINED_AND_APPLIED_TO_EXACT_SHA_RAW',accepted_point_ref=r['accepted_point_ref'])
 else:result.update(cycles=None,scientific_acceptance=False,technical_negative_retained=True)
 result['archive']=archive_audit(cohort,r)
 return result
def main(closed_only=False):
 m=read(C/'EXACT_EXECUTION_MANIFEST.json');auth=exact(m['user_authorization_ref']);fam={x['name']:x for x in auth['families']}
 need(m['new_model_start_ceiling']==auth['approved_total_launches']==8 and auth['all_eight_independently_released']is True,'exact independent8')
 need(auth['baseline_completion_is_launch_gate']is False and auth['WV_REF_completion_is_launch_gate']is False and auth['cross_family_completion_gates']is False,'no sequential completion gates')
 need(set(m['groups'])==set(REQUESTS)and len(m['points'])==len({p['cohort']for p in m['points']})==8,'exact3 scope eight cell population')
 _SPEC_SHA.update({p['cohort']:p['spec_ref']['sha256']for p in m['points']})
 reg,epoch=authority();before=read(C/'PREIMAGES/NATIVE_SCIENCE_REGISTRY.json');prior={k:q for k,q in before['registered_future_requests'].items()if k.startswith('EP_')}
 need(len(prior)==47 and all(reg['registered_future_requests'][k]==q for k,q in prior.items()),'all prior EP rows/history exact')
 need(reg['old_source_history']==before['old_source_history']and reg['qualification_history']==before['qualification_history'],'old science history')
 mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
 need(mount['source']=='admin-wcx@10.208.130.164:/home/shared'and mount['fstype']=='fuse.sshfs','genuine164')
 uuids=[];pending=[];result=[]
 for g,z in m['groups'].items():
  q=reg['registered_future_requests'][z['request_id']]
  need(z['request_id']==REQUESTS[g]==fam[g]['request']and q['budget']==z['budget']==BUDGETS[g],'exact independent3+2+3')
  need(set(q['consumed'])==set(fam[g]['allowed_cohorts'])and q['remaining']==0 and len(q['consumed'])==q['budget'],'exact all8 starts spent once')
  need(q['automatic_retry']is False and q['refund']is False,'no request retry/refund')
  uuids.extend(x['uuid']for x in q['consumed'].values())
  for p in m['points']:
   if p['group']!=g:continue
   row=q['consumed'][p['cohort']]
   if row['state']not in TERMINAL:pending.append(dict(group=g,cohort=p['cohort'],state=row['state']));continue
   result.append(cell_audit(p,z,q,fam[g]))
 need(len(set(uuids))==len(uuids)==8,'eight distinct UUIDs no duplicates')
 complete=not pending and len(result)==8
 if not closed_only:
  need(complete,'full goal not complete; pending '+json.dumps(pending))
  for g,z in m['groups'].items():need(reg['registered_future_requests'][z['request_id']]['state']in ['CLOSED_COMPLETED','CLOSED_WITH_TECHNICAL_FAILURES'],'family not closed')
  final=read(C/'FINAL_SCOPE_CLOSURE.json');need(final['all_scope_budget_consumed']==8,'final exact8 closure')
  for ackname,finish in [('ROOT_LAUNCH_ACK.json','EXECUTOR_FINISHED.json'),('ROOT_METADATA_WATCH_LAUNCH_ACK.json','METADATA_WATCH_FINISHED.json')]:
   ack=read(C/ackname);need(not live(ack['pid'],ack['start_ticks']),'supervisor has not naturally ended');need((C/finish).exists(),'missing final process receipt')
  pub=read(C/'REMOTE_PROGRESS_PUBLICATION_RECEIPT.json')
  need(pub['status']=='EXACT_REMOTE_HEAD_AND_EVERY_EXPORTED_BLOB_VERIFIED'and pub['counts']['accepted']+pub['counts']['technical_failure']==8 and pub['counts']['pending']==0,'final remote publication scope')
 status='EXACT8_REQUIREMENT_BY_REQUIREMENT_COMPLETION_EVIDENCE_PASS'if complete and not closed_only else'CLOSED_SUBSET_AUDIT_PASS_GOAL_STILL_INCOMPLETE'
 out=dict(schema='EP_MAIN_PFV5_REQUIREMENT_COMPLETION_AUDIT_V1',status=status,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),goal_complete_proven=complete and not closed_only,manifest_ref=ref(C/'EXACT_EXECUTION_MANIFEST.json'),audited_closed_points=result,pending=pending,all_prior47_EP_rows_exact_unchanged=True,all_eight_original_starts_distinct_UUIDs=True,budgets=BUDGETS,no_retries_or_refunds=True,no_added_models_or_NI=True,Source_KEEP=True,trace_body_rescan=False,additional_Native_restores=0,remaining_scope_count=len(pending),limitations=['application NI not measured','physical PPA not proven','1700MHz diagnostic, not GPU calibrated','numeric application output UNKNOWN','C complete quota unqualified, no C scientific scope'])
 dest=C/('CLOSED_SUBSET_REQUIREMENT_AUDIT_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'if closed_only else'FINAL_REQUIREMENT_COMPLETION_AUDIT.json')
 need(not dest.exists(),'append-only audit destination already exists')
 dest.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print(json.dumps(dict(status=status,closed=len(result),pending=len(pending),audit_ref=ref(dest),goal_complete_proven=out['goal_complete_proven'])))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--closed-only',action='store_true');a=p.parse_args();main(a.closed_only)
