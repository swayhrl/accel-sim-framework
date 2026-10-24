"""Read-only scientific replay and archive/restore audit; emits one new report."""
import pathlib,json,hashlib,importlib.util,subprocess,datetime,statistics
from fractions import Fraction
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');A=P('/root/data/dtc_main_20261023_v1/ae_fair_v1')
REQUEST='DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
def gone(row):
 p=P('/proc')/str(row['pid'])
 return not p.exists() or int((p/'stat').read_text().rsplit(')',1)[1].split()[19])!=row['start_ticks']
def main():
 regfile=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';reg=read(regfile);epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');q=reg['registered_future_requests'][REQUEST]
 storage_activation=read(T/'control/STORAGE_FLOOR5_ACTIVATED_V3.json')
 assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE' and epoch['native_registry_sha256']==sha(regfile)
 assert q['state']=='COMPLETE' and len(q['consumed'])==q['budget']==12 and q['remaining']==q.get('sealed_unused',0)==0
 req=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');assert q['spec_request_sha256']==sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 assert q['controller_sha256']==sha(T/'tools'/storage_activation['new_native_source_file'])==storage_activation['new_native_source_sha256']
 assert len(req['matrix_order'])==len(set(req['matrix_order']))==12
 before=read(T/'control/PREIMAGE_NATIVE_SCIENCE_REGISTRY.json')
 for name,row in before['registered_future_requests'].items():assert reg['registered_future_requests'][name]==row,'preexisting request changed:'+name
 assert reg['old_source_history']==before['old_source_history'] and reg['qualification_history']==before['qualification_history']
 strict=load('current_exact_strict_audit',T/'tools/short3_strict_r2.py');native=load('current_exact_native_audit',T/'tools/short3_native.py');outbox=load('current_exact_outbox_audit',T/'tools/short3_result_base.py')
 for row in q['shared_tool_pins']:assert sha(row['path'])==row['sha256']
 for name,h in read(T/'control/QUALIFICATION_R2.json')['tool_sha256'].items():assert sha(T/'tools'/name)==h,'qualified scientific/controller tool changed:'+name
 for name,h in read(T/'control/STORAGE_FLOOR5_QUALIFICATION_V3.json')['source_SHA256'].items():assert sha(T/'tools'/name)==h,'qualified storage source changed:'+name
 for kind,commit in [('core','2e3bef4364e578cddd0e881c0baace2e51c55930'),('framework','cfd3ff56d7ba6642dab6c7710ec4f6065168174e')]:
  assert git(T/kind,'rev-parse','HEAD')==commit and not git(T/kind,'status','--porcelain')
 assert sha(T/'DTC/bin/accel-sim.out')=='ab6c717dcbe7932af8bbb6dfbad0b1df9ec0ba447c067085cb92855fb8628a8e'
 for file in ['CONTROLLER_LAUNCH.json','CONTROLLER_LAUNCH_R2.json','CONTROLLER_LAUNCH_R3.json','CONTROLLER_LAUNCH_R4.json']:assert gone(read(T/'control'/file))
 r4=read(T/'control/CONTROLLER_LAUNCH_R4.json');assert sha(T/'tools/short3_controller_r4.py')==r4['controller_sha256'] and sha(T/'tools/short3_archive_wait.py')==r4['archive_wait_sha256']
 intents=list((T/'control/qualification_ledger').glob('*.INTENT.json'));assert {p.stem.removesuffix('.INTENT') for p in intents}==set(req['matrix_order'])
 rows=[];previous_archive=None;gaps=[];original_inputs=read(T/'control/INPUT_IDENTITIES.json');uuids=set();restored=0;total_archive=0;total_wall=0
 for cohort in req['matrix_order']:
  s=native.spec_for(cohort);native.check_input(s);audit=strict.terminal(cohort)
  intentfile=T/'control/qualification_ledger'/(cohort+'.INTENT.json');intent=read(intentfile);done=read(intentfile.with_name(cohort+'.DONE.json'));out=P(intent['output'])
  assert audit==read(out/'AEFAIR_STRICT.json'),'stored strict mismatch'
  assert q['consumed'][cohort]['uuid']==audit['uuid'] and q['consumed'][cohort]['intent_sha256']==sha(intentfile)
  assert q['consumed'][cohort]['execution_receipt']==done
  assert audit['uuid'] not in uuids;uuids.add(audit['uuid'])
  pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert gone(pid)
  progress=[json.loads(line) for line in (out/'progress.jsonl').read_text().splitlines()]
  assert all(p['input']==s['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==s['original_environment']['DTC_AG7_ROI_SHA'] for p in progress),'authenticated full input/ROI binding'
  archivefile=T/'control'/(cohort+'_ARCHIVE_RECEIPT.json');archive=read(archivefile);bundle=P(archive['target_mount_path'])
  assert archive['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and archive['scientific_status']=='AEFAIR_SCIENCE_QUALIFIED'
  manifest=outbox.manifest_for(cohort);assert manifest==read(bundle/'SOURCE_MANIFEST.json')
  f,v=outbox.libraries(bundle);idx=f.verify_archive(bundle,manifest);proof=f.check_native(P(archive['native_restore']),manifest)
  assert idx['archive_sha256']==archive['archive_sha256'] and len(proof)==len(manifest['entries'])
  assert archive['source_disposition']=='SOURCE_KEEP' and archive['source_release_bytes']==0
  assert read(bundle/'RECEIPT.json')==archive
  if previous_archive is not None:
   gap=(intentfile.stat().st_mtime_ns-previous_archive.stat().st_mtime_ns)/1e9;assert gap>=10,'next model before archive/restore and native admission pair';gaps.append(gap)
  previous_archive=archivefile
  samples=[json.loads(l) for l in (out/'RESOURCE_SAMPLES.jsonl').read_text().splitlines()]
  decisions=[x['DTC_exact_original_policy']['decision'] for x in samples if 'DTC_exact_original_policy' in x]
  resources=[x for x in samples if 'fresh_local_resource_sample' in x]
  times=[x['elapsed_seconds'] for x in resources]
  maxgap=max((b-a for a,b in zip(times,times[1:])),default=0)
  assert maxgap<=30 and decisions and all(x['decision']!='STOP' for x in decisions)
  restored+=len(proof);total_archive+=archive['archive_bytes'];total_wall+=done['elapsed_seconds']
  rows.append({'workload':s['workload'],'cell':s['cell'],'cohort':cohort,'uuid':audit['uuid'],'cycles':audit['cycles'],'instructions':audit['instructions'],'CTA':audit['CTA'],'kernel_count':audit['kernel_count'],'kernels':audit['kernels'],'elapsed_seconds':done['elapsed_seconds'],'raw_sha256':done['raw_sha256'],'strict_sha256':sha(out/'AEFAIR_STRICT.json'),'original_spec_sha256':sha(T/'control'/(cohort+'_SPEC.json')),'resolved_expected_options_sha256':sha(T/'control/RESOLVED_EFFECTIVE_OPTIONS_R2.json'),'resource_decisions':len(decisions),'warning_decisions':[x for x in decisions if x.get('warnings')],'non_continue_decisions':[x for x in decisions if x['decision']!='CONTINUE'],'max_resource_sample_gap_seconds':maxgap,'archive':archive,'native_restore_entries':len(proof),'full_independent_strict_replayed':True,'original_archive_full_SHA_rechecked':True,'independent_native_restore_all_entries_rechecked':True,'simulator_generation_gone':True})
 assert {p.name for p in (T/'DTC/run/results').iterdir()}==uuids
 summaries=[]
 for w in ['NN','DWT2D','MRI-Q']:
  rr={x['cell']:x for x in rows if x['workload']==w};assert set(rr)=={'CM','CH','DM','DH'}
  cycles={k:x['cycles'] for k,x in rr.items()};c=Fraction(cycles['CM'],cycles['CH']);d=Fraction(cycles['DM'],cycles['DH']);r=d/c
  summaries.append({'workload':w,'cycles':cycles,'conventional_speedup':float(c),'conventional_cycle_reduction':float(1-1/c),'DTC_AE_speedup':float(d),'DTC_AE_cycle_reduction':float(1-1/d),'interaction_R':float(r),'exact_fractions':{'C':str(c),'D':str(d),'R':str(r)},'disposition':'DTC_LARGER_WITHIN_DESIGN_GAIN' if r>1 else 'CONVENTIONAL_LARGER_WITHIN_DESIGN_GAIN' if r<1 else 'NO_INTERACTION_DIFFERENCE','selection':'PREREGISTERED_SHORT_HISTORICAL_INPUT_NOT_RANDOM_HOLDOUT'})
 # The source onboarding manifest and completed GEMM scientific pack remain byte-identical.
 originalF=P('/root/data/dtc_main_20261023_v1/accel-sim-framework');O=originalF/'docs/dtc_l1/review_packs/DTC_MAIN_NATIVE_ONBOARDING_20261023_V1'
 manifest_lines=(O/'FILES_SHA256.tsv').read_text().splitlines();unchanged=0
 import csv,io
 tab=list(csv.DictReader(io.StringIO('\n'.join(manifest_lines)),delimiter='\t'))
 if tab:
  for row in tab:
   rel=row.get('path') or row.get('relative_path');h=row.get('sha256')
   if rel and h:
    candidate=O/rel
    if not candidate.exists():candidate=originalF/rel
    assert sha(candidate)==h;unchanged+=1
  assert unchanged>0,'onboarding manifest parser'
 assert sha(A/'analysis/COMPLETE_RESULT.json')=='a26c229e43855e7ebefac6b37868ac9cef8e25c0611fdcae34ba1e17bcdaf4e0','completed GEMM consumer changed'
 # Every preexisting final report file is still its Git-committed content.
 pack='docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1'
 tracked=git(originalF,'ls-tree','-r','--name-only','db58c292d1304a7164587158245ccfbb69334ed9',pack).splitlines()
 for name in tracked:
  p=originalF/name;expected=git(originalF,'rev-parse','db58c292d1304a7164587158245ccfbb69334ed9:'+name)
  b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()==expected
 wrapper=(N/'bin/native').read_text();prior=(T/'control/NATIVE_ENTRY_PREIMAGE').read_text()
 assert wrapper==prior.replace('/root/data/dtc_main_20261023_v1/ae_fair_v1/tools/native_epoch2_frontend.py',str(T/'tools'/storage_activation['new_frontend']))
 assert sha(N/'bin/native')==storage_activation['native_entry_sha256']
 assert sha(T/'tools/short3_frontend.py')==read(T/'control/QUALIFICATION_R2.json')['tool_sha256']['short3_frontend.py']
 result={'schema':'DTC_AEFAIR_SHORT3_COMPLETE_RESULT_V1','status':'ALL_12_WHOLE_INPUT_POINTS_STRICT_ARCHIVE_RESTORE_RECHECKED','request':REQUEST,'budget':12,'consumed':12,'remaining':0,'model_retries':0,'unique_model_UUIDs':len(uuids),'metadata_controllers':{'R1':'pre-fork missing path mapping;0starts;preserved','R2':'one natural completed point;strict metadata HOLD;preserved','R3':'postprocess existing spent NN-DM then exactly11 unused cells;no rerun'},'selection':['NN','DWT2D','MRI-Q'],'summaries':summaries,'points':rows,'total_model_wall_seconds':total_wall,'total_raw_archive_bytes':total_archive,'total_verified_raw_restore_entries':restored,'archive_before_next_INTENT_gaps_seconds':gaps,'historical_peer_requests_and_old_ledgers_unchanged':True,'onboarding_manifest_files_unchanged':unchanged,'completed_GEMM_review_files_unchanged':len(tracked),'same_source_binary_configs_as_GEMM':True,'input_member_SHA_and_body_audit_join':'control/INPUT_PREFLIGHT.json','original_specs_unchanged':'Expected echo metadata correction is separately pinned;actual config/argv bytes unchanged','all_model_and_controller_generations_gone':True,'sole_entry_asset_and_prior_science_fallback_preserved':True,'paper_mother':'Englishv0.23,actual package unavailable,no manuscript promotion','limits':['Three short historical inputs chosen by original OO cycles;not representative suite or statistical holdout','Fixed Volta-basedFAST64;not stockV100','Different cross-design tag/ownership/timing/unified96vs128 geometry;Rdoes not uniquely identify DTC-specific mechanism','Extra hash latency modeled aszero;hardware timing/equalarea/PPA not proven','Whole-trace replay and bounded conservation do not prove native numerical correctness','Historical accepted/negative/HOLD and oldAG8R1 unchanged'],'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 result['user_storage_policy']=read(T/'control/USER_STORAGE_POLICY_FLOOR5_V3.json')
 result['metadata_controllers']['R3']='Continued10unused models after spentNN-DM;11models closed/accepted in total, thenCOPY_ONLY shared-lockEAGAIN;all preserved'
 result['metadata_controllers']['R4']='Skipped11accepted archived modelUUIDs;started only original unusedMRI-Q-CH;bounded COPY_ONLY lock wait,no model retry'
 result['outbox_lock_contention_checkpoint']=read(T/'control/OUTBOX_CONTENTION_CHECKPOINT_R3.json')
 result['storage_profile_activation']=storage_activation
 result['storage_source_qualification_tests']=len(read(T/'control/STORAGE_FLOOR5_QUALIFICATION_V3.json')['tests'])
 for row in rows:
  intent=read(T/'control/qualification_ledger'/(row['cohort']+'.INTENT.json'))
  launch=read(P(intent['output'])/'NATIVE_LAUNCH.json')
  row['native_operational_launcher_sha256']=launch['finite_native_launcher_sha256']
  row['model_storage_profile']='USER5GiB_V3' if launch['finite_native_launcher_sha256']==storage_activation['new_native_source_sha256'] else 'ORIGINAL_NATIVE_TARGET_PROFILE'
  row['observed_native_required_free_at_launch']=launch['resources']['required_free_bytes']
 output=T/'analysis/COMPLETE_RESULT.json'
 with output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['points']},indent=2))
 return result
if __name__=='__main__':main()
