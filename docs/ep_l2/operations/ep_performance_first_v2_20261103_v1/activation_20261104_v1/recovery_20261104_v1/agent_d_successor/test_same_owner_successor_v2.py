#!/usr/bin/env python3
"""Private handoff CPU fixtures. No real native/model/registry/Git invocation."""
import copy,sys,tempfile,json,os,time
from pathlib import Path as P
D=P(__file__).parent;sys.path.insert(0,str(D));import finite_same_owner_successor_v2 as R
E=R.E;A=R.V/'activation_20261104_v1';controls=[]
def ck(name,ok=True):assert ok,name;controls.append(dict(name=name,status='PASS'))
def reject(name,fn):
 try:fn()
 except Exception:ck(name);return
 raise AssertionError(name+' not rejected')
B=P(tempfile.mkdtemp(prefix='CPU_ONLY_',dir=D));prior=E.read(A/'control/EXACT_EXECUTION_MANIFEST.json');idx=E.read(D/'PRIOR_SPEC_BYTES_INDEX.json');snapactual=E.read(A/'recovery_20261104_v1/control/IDLE_HANDOFF_CONSUMED_AND_BUDGET_SNAPSHOT.json')
o=R.Successor.__new__(R.Successor);o.m=copy.deepcopy(prior);o.C=B/'central';o.C.mkdir();o.points=o.m['points'];o.bypoint={p['cohort']:p for p in o.points};o.specs={p['cohort']:E.exact(p['immutable_byte_snapshot_ref'])for p in idx['points']};o.states={};o.running={};o.pending_accept=[];o.initial_consumed=sorted(R.INITIAL);o.session='CPU_ONLY';o.lastpublish=0;o.started=time.monotonic();o.lastresource={};o.phase_cache={};o.failures={};o.fatal=[]
o.manifest_path=B/'manifest.json';o.m['prior_manifest_ref']=E.ref(A/'control/EXACT_EXECUTION_MANIFEST.json');hostq=E.put(B/'hostq.json',dict(TEST_ONLY=True));o.m['host_only_revision_qualification_ref']=hostq;o.m['shared_native_ref']=E.ref(prior['shared_native_ref']['path']);o.m['accept_serial_lock']=str(o.C/'accept.lock')
for g in E.REQUESTS:
 o.m['groups'][g]['data_root']=str(B/g);E.put(B/g/'control/DISPATCH_CLAIMS.json',E.read(A/'recovery_20261104_v1/control'/('IDLE_HANDOFF_'+g.upper()+'_CLAIMS.json')))
E.put(o.manifest_path,o.m)
snap=dict(schema='EP_MAIN_V2_SAME_OWNER_CONSUMED_HANDOFF_SNAPSHOT_V1',requests={qid:copy.deepcopy(snapactual[g])for g,qid in E.REQUESTS.items()});snapref=E.put(B/'snapshot.json',snap);registry=dict(registered_future_requests=copy.deepcopy(snap['requests']))
for g,qid in E.REQUESTS.items():registry['registered_future_requests'][qid]['admitted_specs']={p['cohort']:p['spec_ref']['sha256']for p in o.points if p['group']==g}
def rows():return registry,{c:r for q in registry['registered_future_requests'].values()for c,r in q['consumed'].items()}
o.rows=rows
claimsrefs={g:E.put(B/(g+'_claimsnapshot.json'),E.read(B/g/'control/DISPATCH_CLAIMS.json'))for g in E.REQUESTS}
a=dict(schema='EP_MAIN_V2_SAME_OWNER_SUCCESSOR_ACTIVATION_V1',status='MAIN_REVIEWED_IDLE_OWNER_HANDOFF_AND_REMAINING16_AUTHORIZED',approved_by='EP-MAIN',executor_ref=E.ref(R.__file__),manifest_ref=E.ref(o.manifest_path),prior_manifest_ref=o.m['prior_manifest_ref'],host_only_revision_qualification_ref=hostq,prior_started_ref=E.ref(A/'control/EXECUTOR_STARTED.json'),consumed_snapshot_ref=snapref,claims_snapshot_refs=claimsrefs,no_retry=True,no_refund=True);E.put(o.C/'SAME_OWNER_HANDOFF_AUTHORIZATION.json',a)
o.check_activation();ck('actual_check_activation_oldsession_idle_twoDone_twoClaims_original11plus5')
orig=R.same_live;R.same_live=lambda _:True
reject('old_controller_live_same_generation_rejects_handoff',lambda:o.check_activation());R.same_live=orig
q=registry['registered_future_requests'][E.REQUESTS['system']];q['remaining']+=1;reject('refund_or_new_budget_forbidden',lambda:o.check_activation());q['remaining']-=1
saved=copy.deepcopy(q['consumed']);q['consumed']['FAKE_EXTRA_CONSUMED']=copy.deepcopy(next(iter(q['consumed'].values())));reject('extra_consumed_population_rejected',lambda:o.check_activation());q['consumed']=saved
clpath=B/'system/control/DISPATCH_CLAIMS.json';cl=E.read(clpath);oldcl=copy.deepcopy(cl);c=next(iter(cl['claims']));cl['claims'][c]['model_pid']=os.getpid();cl['claims'][c]['model_start_ticks']=E.pid_identity(os.getpid())['start_ticks'];E.put(clpath,cl);a['claims_snapshot_refs']['system']=E.put(B/'liveclaimssnapshot.json',cl);E.put(o.C/'SAME_OWNER_HANDOFF_AUTHORIZATION.json',a)
reject('live_model_generation_in_retained_claim_rejected',lambda:o.check_activation());E.put(clpath,oldcl);a['claims_snapshot_refs']['system']=claimsrefs['system'];E.put(o.C/'SAME_OWNER_HANDOFF_AUTHORIZATION.json',a)
reject('consumed2_cannot_model_refork_even_direct_native',lambda:R.Successor.native(o,'run-native',next(iter(R.INITIAL))))
# Exercise actual two old Done closure sequencing through fake accept leaf only.
calls=[]
def close_accepted(c):
 p=o.bypoint[c];s=o.specs[c];g=p['group'];row=rows()[1][c];folder=B/g/'synthetic'/c;folder.mkdir(parents=True,exist_ok=True)
 ar=dict(status='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS',cohort=c,uuid=row['uuid'],source_keep=True,archive_ref=dict(path='/root/share/mnt164/CPU_ONLY_NEVER_CREATED/'+c,sha256='a'*64),native_restores=[dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS',target='/CPU_ONLY/'+c+'/'+label,restore_label=label,archive_sha256='a'*64)for label in ['FIRST','INDEPENDENT']])
 pt=dict(status='EP_FULL_PERF_APPLICATION_ACCEPTED',hardware_drained=True,cohort=c,uuid=row['uuid'],mode=s['mode'],source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],spec_ref=p['spec_ref'],cycles=100000,instructions=s['expected_instructions'],CTA=s['expected_CTA'],kernel_count=1)
 row.update(state='CLOSED_ACCEPTED',accepted_point_ref=E.put(folder/'point.json',pt),archive_receipt_ref=E.put(folder/'archive.json',ar));claims=E.read(B/g/'control/DISPATCH_CLAIMS.json');claims['claims'].pop(c,None);E.put(B/g/'control/DISPATCH_CLAIMS.json',claims)
class Process:
 def __init__(self,c):self.c=c
 def wait(self):close_accepted(self.c);return 0
def native(op,c,**kw):assert op=='accept'and c in R.INITIAL;calls.append((op,c));return Process(c)
o.native=native;(o.C/'native_logs').mkdir();o.close_handoff_done();ck('two_old_Done_scoped_accept_closures_before_any_new_start',len(calls)==2 and all(r['state']=='CLOSED_ACCEPTED'for r in rows()[1].values()))
o.check_activation();ck('snapshot_pending_to_qualified_closed_and_claim_removal_allowed')
o.close_handoff_done();ck('already_closed_consumed2_not_accepted_again',len(calls)==2)
ck('budget11plus5_unchanged_after_two_closures',registry['registered_future_requests'][E.REQUESTS['system']]['remaining']==11 and registry['registered_future_requests'][E.REQUESTS['highclock']]['remaining']==5)
reg,rr=rows();dec,vv,refs,errs=o.decisions(reg,rr);ck('stage1275_still_waits_missing_newSource850S',dec['EP_PERF_CC_CAM_VECTOR4M_S_1275_V1']['status']=='WAIT')
ck('FWT_single_future_arms_release_without_consumed_retry',all(dec[p['cohort']]['status']=='RELEASE'for p in o.points if p['group']=='system'and E.system_meta(p['cohort'])[0]=='FWT'and E.system_meta(p['cohort'])[1]!='G64W16_FRFCFS256'))
# Local unresolved prior Done prevents only that family's future cells.
hc='EP_PERF_CC_CAM_VECTOR4M_F_850_V1';rr[hc]['state']='NATURAL_COMPLETE_PENDING_VALIDATION';dec,vv,refs,errs=o.decisions(reg,rr);ck('local_old_Done_closure_HOLD_does_not_block_system',dec['EP_PERF_CC_CAM_VECTOR4M_S_850_V1']['status']=='HOLD'and any(dec[c]['status']=='RELEASE'for c in E.SYSTEM));rr[hc]['state']='CLOSED_ACCEPTED'
# Verify unchanged original snapshots and scientific field guard independently.
ck('all18_prior_spec_bytes_match_original_hashes',all(E.sha(p['immutable_byte_snapshot_ref']['path'])==p['old_official_spec_ref']['sha256']for p in idx['points']))
ck('hardware_fields_never_in_Host_revision_allowlist',not({'source_identity','expected_effective_options','observer_env','geometry','input_identity_sha256','ro_qualification_ref','limits','application_budget'}&R.HOST_FIELDS))
# Exercise actual source/publisher owner lock identities inherited unchanged.
ck('same_global_locks_and_single_publication_function',R.ADMISSION==E.ADMISSION and R.RESTORE==E.RESTORE and R.OWNERSHIP==E.OWNERSHIP and 'super().publish' in P(R.__file__).read_text())

# Entire actual successor loop: already accepted2 are retained, only safe future
# cells get fake native leaves, and gates HOLD their conditional descendants.
class Loop(R.Successor):
 def __init__(self):
  self.__dict__=copy.deepcopy({k:v for k,v in o.__dict__.items()if k not in ['native','rows']});self.C=B/'loop';self.C.mkdir();self.m['accept_serial_lock']=str(self.C/'accept.lock');self.m['control_root']=str(self.C);self.session='CPU_ONLY_LOOP';self.running={};self.pending_accept=[];self.states={};self.calls=[];self.archive_done=set(R.INITIAL);self.fake=copy.deepcopy(registry);self.lastpublish=time.monotonic();self.started=time.monotonic();self.lastresource={}
 def rows(self):return self.fake,{c:r for q in self.fake['registered_future_requests'].values()for c,r in q['consumed'].items()}
 def check_activation(self):pass
 def start(self,p):
  c=p['cohort'];assert c not in self.rows()[1]and c not in R.INITIAL;g=p['group'];q=self.fake['registered_future_requests'][E.REQUESTS[g]];q['remaining']-=1;q['consumed'][c]=dict(state='RUNNING');self.running[c]=dict(cpu=self.available_cpu());self.calls.append(c);return True
 def poll(self):
  for c in list(self.running):self.running.pop(c);self.pending_accept.append(c);self.rows()[1][c]['state']='COMPLETED'
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0);assert c not in R.INITIAL;self.rows()[1][c]['state']='CLOSED_UNACCEPTED';self.archive_done.add(c)
 def closed_view(self,c,row):
  if c in R.INITIAL:return E.Executor.closed_view(self,c,row)
  return dict(archived=c in self.archive_done,accepted=False)
 def publish(self,final=False):self.lastpublish=time.monotonic();E.put(self.C/'REMOTE_PUBLICATION_RECEIPT.json',dict(final=final,HEAD='CPU_ONLY',remote_HEAD='CPU_ONLY'))
 def archive_summary(self):pass
loop=Loop();oldlock=R.OWNERSHIP;oldadmission=E.ADMISSION;R.OWNERSHIP=B/'private-owner.lock';E.ADMISSION=B/'private-admission.lock';sleep=R.time.sleep;R.time.sleep=lambda _:None
try:loop.run()
finally:R.OWNERSHIP=oldlock;E.ADMISSION=oldadmission;R.time.sleep=sleep
ck('actual_successor_runloop_keeps2_accepted_never_reforks',not(set(loop.calls)&R.INITIAL)and all(loop.rows()[1][c]['state']=='CLOSED_ACCEPTED'for c in R.INITIAL))
ck('actual_successor_runloop_same_budget_not_refund',len(loop.calls)==8 and loop.fake['registered_future_requests'][E.REQUESTS['system']]['remaining']==4 and loop.fake['registered_future_requests'][E.REQUESTS['highclock']]['remaining']==4)
ck('actual_successor_runloop_records16_remaining_ceiling',E.read(loop.C/'RESULTS_CURRENT.json')['maximum_remaining_new_starts']==16)
ck('actual_successor_runloop_stages_and_localHOLD',bool((loop.C/'EXECUTOR_FINISHED.json').exists())and any('_GEMM_'in c for c in loop.calls))
reject('actual_successor_duplicate_run_receipt_blocks_refork',lambda:loop.run())


# Passive recovery schema/semantic validator against the still-original Host
# specs; this is a private checker fixture, not new Host/native qualification.
pm=copy.deepcopy(prior);pm.update(schema='EP_MAIN_V2_SAME_OWNER_RECOVERY_EXECUTION_MANIFEST_V1',control_root=str(R.RECOVERY_CONTROL),prior_manifest_ref=E.ref(A/'control/EXACT_EXECUTION_MANIFEST.json'),prior_spec_byte_index_ref=E.ref(D/'PRIOR_SPEC_BYTES_INDEX.json'),shared_native_ref=E.ref(prior['shared_native_ref']['path']),postrun_only_entry_ref=E.ref(A/'recovery_20261104_v1/control/postrun_exact_two.py'))
qual=dict(schema='EP_MAIN_V2_HOST_ONLY_SPEC_REVISION_QUALIFICATION_V1',status='MAIN_REVIEWED_SAME_SOURCE_INPUT_282_OBSERVERS_REMAINING16_HOST_ONLY',approved_by='EP-MAIN',allowed_host_only_fields=sorted(R.HOST_FIELDS),TEST_ONLY=True);pm['host_only_revision_qualification_ref']=E.put(B/'checker_only_hostqual.json',qual)
candidate_root=A/'recovery_20261104_v1/agent_b_native';entry_candidates={g:candidate_root/g/'native_recovery_20261104_v1'for g in E.REQUESTS}
entry_sha={g:E.sha(p)for g,p in entry_candidates.items()}
for g in E.REQUESTS:pm['groups'][g]['native_entry_ref']=dict(path=str(R.VERSIONED_NATIVE_PATHS[g]),sha256=entry_sha[g])
def private_entry_digest(path):
 for g,p in R.VERSIONED_NATIVE_PATHS.items():
  if P(path)==p:return E.sha(entry_candidates[g])
 return E.sha(path)
original_helper=R.validate_versioned_entries;R.validate_versioned_entries=lambda m,pr:original_helper(m,pr,digest=private_entry_digest)
R.validate_recovery_manifest(pm);ck('actual_passive_recovery_manifest_validator_18_prior_bytes_with_versioned_native')
wrong=copy.deepcopy(pm);wrong['groups']['system']['native_entry_ref']['path']+='_FOREIGN';reject('versioned_Native_wrong_path_rejected',lambda:R.validate_recovery_manifest(wrong))
wrong=copy.deepcopy(pm);wrong['groups']['highclock']['native_entry_ref']['sha256']='0'*64;reject('versioned_Native_wrong_SHA_rejected',lambda:R.validate_recovery_manifest(wrong))
wrong_prior=copy.deepcopy(prior);wrong_prior['groups']['system']['native_entry_ref']['sha256']='0'*64;reject('accepted_canonical_Native_oldbytes_must_remain',lambda:original_helper(pm,wrong_prior,digest=private_entry_digest))
ck('two_exact_versioned_native_paths_are_separate_from_accepted_canonical',all(R.VERSIONED_NATIVE_PATHS[g]!=P(prior['groups'][g]['native_entry_ref']['path'])for g in E.REQUESTS))
orig_exact=R.exact;target=next(p['spec_ref']for p in pm['points']if p['cohort']not in R.INITIAL)
def wrong_science(ref):
 z=orig_exact(ref)
 if ref==target:z=copy.deepcopy(z);z['expected_effective_options']['-dram_latency']='101'
 return z
R.exact=wrong_science;reject('actual_manifest_GPU_option_change_rejected',lambda:R.validate_recovery_manifest(pm));R.exact=orig_exact
consumed_target=next(p['spec_ref']for p in pm['points']if p['cohort']in R.INITIAL)
def changed_consumed_host(ref):
 z=orig_exact(ref)
 if ref==consumed_target:z=copy.deepcopy(z);z['native_entry_ref']=dict(path='/CPU_ONLY_REVISED_CONSUMED_NATIVE',sha256='0'*64)
 return z
R.exact=changed_consumed_host;reject('consumed2_even_Host_native_entry_ref_cannot_change',lambda:R.validate_recovery_manifest(pm));R.exact=orig_exact
qual['allowed_host_only_fields'].append('expected_effective_options');E.put(B/'checker_only_badqual.json',qual);bad=copy.deepcopy(pm);bad['host_only_revision_qualification_ref']=E.ref(B/'checker_only_badqual.json');reject('Main_Host_allowlist_cannot_authorize_science_field',lambda:R.validate_recovery_manifest(bad))

out=dict(schema='EP_MAIN_SAME_OWNER_RECOVERY_PRIVATE_CPU_V1',status='PASS',controls=controls,count=len(controls),successor_ref=E.ref(R.__file__),private_fixture=str(B),scientific_starts=0,native_invocations=0,registry_writes=0,Git_writes=0,synthetic_acceptance_not_science=True);E.put(D/'ACTUAL_RECOVERY_V2_CPU_CONTROLS.json',out);print(json.dumps(dict(status='PASS',count=len(controls))))
