import json,pathlib,hashlib,sys,subprocess,datetime,math,fcntl
REPO=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1');sys.path.insert(0,str(REPO/'util/ep_l2/ft_lane5'))
from acceptance import load_current_authority,current_manifest
from registry import attempt_count,run_key,PARALLEL,R19
from run import GATES
root=pathlib.Path('/workspace/ep_l2_ft20261016_shared');pack=REPO/'docs/ep_l2/review_packs/FT20261018_LANE5_R19_GOAL_COMPLETION_AUDIT_r1';pack.mkdir(exist_ok=True)
cache={}
def digest(path):
 p=pathlib.Path(path)
 if str(p) not in cache:cache[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[str(p)]
def load(path):return json.loads(pathlib.Path(path).read_text())
def save(name,value):(pack/name).write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def checksums(directory):
 n=0
 for line in (directory/'SHA256SUMS').read_text().splitlines():
  sha,name=line.split('  ',1);assert digest(directory/name)==sha,(directory,name);n+=1
 return n
state=load_current_authority();m=current_manifest(state);accepted={v['run_key']:v for v in m['rows'] if v['scientific_acceptance']=='CURRENT_ACCEPTED'}
with (root/'REGISTRY.lock').open('r') as lock:
 fcntl.flock(lock,fcntl.LOCK_SH);raw=(root/'RUN_REGISTRY.json').read_bytes();r=json.loads(raw)
registry_sha=hashlib.sha256(raw).hexdigest();client_sha=digest(root/'CLIENT_CONTRACT.json');rows=[v for v in r['runs'].values() if v.get('experiment_id')==R19]
assert len(rows)==20 and sum(attempt_count(v) for v in rows)==21
expected={(h,w,u) for h in ['D4','Q4','D2','L25'] for w in ['convolutionSeparable','FWT_7_21'] for u in [False,True]}|{('D4',w,u) for w in ['vectorAdd_4M','sad'] for u in [False,True]}
assert {(v['regime'],v['identity']['workload'],v['identity']['feature_vector']['unified_wb']) for v in rows}==expected
T0=1792220956;DEADLINE=T0+36000;assert DEADLINE==1792256956
source={'core_source_commit':'7b8e6ac70b8fe0f1bd37efca11acb5284938825d','framework_source_commit':'9bd17f9db3e8cbbc3fdad7283d1e292918546fd5','binary_sha256':'23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee'}
selection_path=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_R19_INITIAL8_AND_SELECTION_r1/SELECTION_CHECKPOINT.json';selection=load(selection_path);selected_time=datetime.datetime.fromisoformat(selection['at_utc']).timestamp();assert [v['regime'] for v in selection['selected_followup_conditions']]==['D2','L25'];assert selection['selected_robustness_condition']['regime']=='D4';assert selection['selected_robustness_condition']['workloads']==['vectorAdd_4M','sad']
run_evidence=[];intervals=[];qualification_reviews={}
for row in rows:
 d=pathlib.Path(row['result_directory']);terminal=load(d/'run_status.json');spec=load(d/'input_spec.json');summary=load(d/'terminal_summary.json');audit=load(d/'input_audit.json');ident=row['identity'];key=run_key(ident)
 assert row['status']==terminal['status']=='COMPLETE_VALID' and terminal['exit_code']==0
 assert key==row['run_key']==terminal['run_key'] and ident==terminal['identity']==spec['identity']==accepted[key]['identity']
 assert all(ident[k]==v for k,v in source.items()) and ident['epoch_range']=={'epochs':'all','scope':'full_application'}
 assert not any(ident['ideal_vector'].values()) and not ident['feature_vector']['tvd'] and not ident['feature_vector']['ro']
 assert terminal['audit']==audit and terminal['summary']==summary and terminal['validation']['status']=='PASS'
 assert summary['slices']==64 and summary['hardware_drained'] and summary['responses']==summary['unique_requesters']
 for field in ['live_descriptors','live_line_mshrs','live_wad','pending_lower_reads','pending_responses','pending_returns','transient_payloads']:assert summary[field]==0,(key,field)
 assert summary['wb_created']==summary['wb_completed']==summary['wb_lower_accepted']
 assert digest(d/'raw.log')==terminal['raw_log_sha256']==accepted[key]['raw_log_sha256']
 assert digest(d/'accel-sim.out')==ident['binary_sha256']
 assert digest(spec['qualified_release'])==audit['qualified_release_sha256']
 q=load(spec['qualified_release']);assert q['status']=='INDEPENDENTLY_QUALIFIED' and q['qualified_by']=='lane5' and q['evidence_kind']=='PRODUCTION_DRIVEN' and q['gates'].keys()>=GATES
 for gate in GATES:
  g=q['gates'][gate];assert g['status']=='PASS' and g['production_driven'] and digest(g['evidence_path'])==g['evidence_sha256']
 binding=q['downstream_config_qualification'];assert digest(binding['path'])==binding['sha256'];review=load(binding['path']);assert review['status']=='INDEPENDENT_CONFIG_PASS' and review['independent_affected_production_pass'] and not review['runtime_binary_recompiled']
 qualification_reviews[str(binding['path'])]={'sha256':binding['sha256'],'status':review['status'],'regime':review['regime'],'independent_affected_executions':review.get('independent_affected_executions'),'lane1_publication':review.get('lane1_publication'),'runtime_binary_recompiled':review['runtime_binary_recompiled']}
 for item in audit['configs']+audit['auxiliary_assets']:assert digest(d/item['name'])==item['sha256']
 begin=datetime.datetime.fromisoformat(row['created_at']).timestamp();end=datetime.datetime.fromisoformat(row['updated_at']).timestamp();assert T0<=begin<=end<=DEADLINE
 if row['regime'] in ['D2','L25'] or ident['workload'] in ['vectorAdd_4M','sad']:assert selected_time<begin
 intervals.append((begin,1));intervals.append((end,-1))
 for old in row.get('attempt_history',[]):
  olddir=pathlib.Path(old['result_directory']);assert olddir!=d and (olddir/'raw.log').is_file() and (olddir/'run_status.json').is_file();assert old['status']=='RESOURCE_LIMIT';ob=datetime.datetime.fromisoformat(old['created_at']).timestamp();oe=datetime.datetime.fromisoformat(old['updated_at']).timestamp();assert T0<=ob<=oe<=DEADLINE;intervals.extend([(ob,1),(oe,-1)])
 run_evidence.append({'run_key':key,'regime':row['regime'],'workload':ident['workload'],'mode':spec['mode'],'directory':str(d),'cycles':summary['cycles'],'instructions':summary['instructions'],'raw_sha256':terminal['raw_log_sha256'],'identity':ident,'created_at':row['created_at'],'terminal_updated_at':row['updated_at'],'attempts':attempt_count(row),'validation':terminal['validation'],'scope':'Existing full-native symbolic sector/request/WB/drain qualification; no numerical SASS-output claim'})
max_live=0;live=0
for when,delta in sorted(intervals):live+=delta;max_live=max(max_live,live)
# The later user-invoked parallel contract explicitly changed the shared limit2->4,
# while preserving R19 identity/count/deadline. Verify both historical phases.
amendment_commit='a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900'
amendment_path='docs/ep_l2/chatgpt_handoff/parallel_potential_2026_10_17_v1/PARALLEL_CONTRACT.md'
amendment=git('show',amendment_commit+':'+amendment_path)
assert '把中央长模拟并发从 2 提高到 4' in amendment.decode()
amendment_time=int(git('show','-s','--format=%ct','fa1a2e76d80ff50ddbbf45158e4d86ccf069bef6'))
global_intervals=[]
for current in r['runs'].values():
 for attempt in current.get('attempt_history',[])+[current]:
  b=datetime.datetime.fromisoformat(attempt['created_at']).timestamp()
  e=datetime.datetime.fromisoformat(attempt['updated_at']).timestamp()
  if attempt.get('validation_revisions'):
   e=min(e,datetime.datetime.fromisoformat(attempt['validation_revisions'][0]['updated_at']).timestamp())
  if b>=DEADLINE or e<=T0:continue
  global_intervals.extend([(max(b,T0),1),(min(e,DEADLINE),-1)])
live=0;before_peak=0;after_peak=0
for when,delta in sorted(global_intervals):
 live+=delta
 if when<amendment_time:before_peak=max(before_peak,live);assert live<=2
 else:after_peak=max(after_peak,live);assert live<=4
save('CONCURRENCY_AUTHORITY_AUDIT.json',{'initial_assumption_finding':'A strict2-simulator assertion found R19 peak3; this is checked against the later explicit user-approved global4 amendment, not ignored.','R19_peak':max_live,'shared_peak_before_amendment':before_peak,'shared_peak_after_amendment':after_peak,'authority_commit':amendment_commit,'authority_path':amendment_path,'guard_source_publication':'fa1a2e76d80ff50ddbbf45158e4d86ccf069bef6','guard_publication_unix':amendment_time,'outcome':'PASS_BOTH_AUTHORIZED_PHASES','R19_count_and_deadline_preserved':True})
# D4 primary pairs finish before Q4 primary launch, as specified.
main=lambda h:[v for v in rows if v['regime']==h and v['identity']['workload'] in ['convolutionSeparable','FWT_7_21']]
assert max(datetime.datetime.fromisoformat(v['updated_at']).timestamp() for v in main('D4'))<min(datetime.datetime.fromisoformat(v['created_at']).timestamp() for v in main('Q4'))
pairs=[]
conditions=[(h,w) for h in ['D4','Q4','D2','L25'] for w in ['convolutionSeparable','FWT_7_21']]+[('D4',w) for w in ['vectorAdd_4M','sad']]
remote='refs/remotes/origin/hrl/ep-l2-ft20261016-lane5-v1'
for h,w in conditions:
 pair=REPO/'docs/ep_l2/review_packs'/('FT20261017_LANE5_R19_'+h+'_'+w.upper()+'_PAIR_r1');accept=pathlib.Path(str(pair).replace('_PAIR_r1','_ACCEPTANCE_r1'));review=load(pair/'SCIENTIFIC_REVIEW.json');hand=load(accept/'LANE6_HANDOFF.json');event=load(root/'coordination_requests'/('LANE5_TO_LANE6_R19_'+h+'_'+w.upper()+'.json'));pub=event['publication_commit'];assert event['status'] and event['handoff']==hand;assert len(hand['rows'])==2
 pairkeys={v['run_key'] for v in hand['rows']};assert pairkeys<={v['run_key'] for v in rows} and pairkeys<=accepted.keys();assert {v['mode'] for v in hand['rows']}=={'B16_BANKED','U_WB16'}
 assert all(v['identity']==accepted[v['run_key']]['identity'] for v in hand['rows']);assert hand['diagnostic_only'] and hand['comparison']['same_binary'] and hand['comparison']['instructions_equal']
 assert review['status']=='INDEPENDENT_CURRENTNESS_PASS_NATIVE_TERMINAL_REPLAY' or 'PASS' in review['status']
 timestamp=int(git('show','-s','--format=%ct',pub));assert T0<=timestamp<=DEADLINE
 subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',pub,remote],check=True)
 metadata=[accept/'LANE6_HANDOFF.json',accept/'SCIENTIFIC_ACCEPTANCE_V2.json',pair/'SOURCE_MANIFEST.json',pair/'SCIENTIFIC_REVIEW.json',pair/'COMPARISON.json',pair/'SHA256SUMS',accept/'SHA256SUMS']
 for f in metadata:
  relative=str(f.relative_to(REPO));assert git('show',pub+':'+relative)==f.read_bytes();assert git('show',remote+':'+relative)==f.read_bytes()
 checked=checksums(pair)+checksums(accept);pairs.append({'regime':h,'workload':w,'pair_pack':str(pair.relative_to(REPO)),'acceptance_pack':str(accept.relative_to(REPO)),'publication_commit':pub,'publication_utc':datetime.datetime.fromtimestamp(timestamp,datetime.timezone.utc).isoformat(),'generation':hand['ledger_generation'],'both_current_accepted':True,'packet_checksums_verified':checked,'comparison':hand['comparison'],'Lane6_event':str(root/'coordination_requests'/('LANE5_TO_LANE6_R19_'+h+'_'+w.upper()+'.json'))})
# Original H0 row identities/cycles/raw hashes are retained in current authority.
h0=load(REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_R0_1_A1_B1_PRIMARY_COHORT_r1/SCIENTIFIC_ACCEPTANCE_V2_SNAPSHOT.json');h0rows=[v for v in h0['rows'] if v['scientific_acceptance']=='CURRENT_ACCEPTED' and not v.get('experiment_id')];assert len(h0rows)==10
for v in h0rows:
 current=accepted[v['run_key']]
 for field in ['identity','raw_log_sha256','observed_cycles','instructions']:assert v[field]==current[field]
ratios=[]
for w in {v['workload'] for v in h0rows}:
 b=next(v for v in h0rows if v['workload']==w and v['mode']=='B16_BANKED');u=next(v for v in h0rows if v['workload']==w and v['mode']=='U_WB16');ratios.append(b['observed_cycles']/u['observed_cycles'])
mean=math.exp(sum(map(math.log,ratios))/len(ratios));assert math.isclose(mean,1.0016002037656606,rel_tol=1e-14)
assert m['withdrawn_releases']==h0['withdrawn_releases']
requirements=[{'requirement':'D4 thenQ4 Conv/FWT B/U initial8','status':'PASS','evidence':'20_RUN_INTEGRITY.json;10_PAIR_PUBLICATION_AUDIT.json;4+4 original-key matrix and ordering assertions'}, {'requirement':'At most2 evidence-triggered followups and1 robustness condition','status':'PASS','evidence':str(selection_path.relative_to(REPO)),'selected':['D2','L25'],'robustness':'D4 vectorAdd_4M andsad;4runs; noholdoutclaim'}, {'requirement':'Exact official identities/config whitelist, independent affected producer checks, original11 gates','status':'PASS','evidence':'CONDITION_QUALIFICATION_AUDIT.json; per-run qualification/config artifact SHA checks'}, {'requirement':'Independent full-native64slice request/WB/sector/quiescence acceptance and currentV2','status':'PASS','evidence':'20_RUN_INTEGRITY.json; currentV2 exact loader/hash plus original scientific-review+frozen packet checksum checks'}, {'requirement':'24 total-start cap, original10h, authorized2-to4 shared concurrency; preserve failedattempt','status':'PASS','actual_starts':21,'cap':24,'max_concurrent_R19':max_live,'shared_peak_before_amendment':before_peak,'shared_peak_after_amendment':after_peak,'evidence':'CONCURRENCY_AUTHORITY_AUDIT.json; Run/history and publicationtimestamps checked; oldRESOURCE_LIMITrawretained'}, {'requirement':'Preserve H0 and currentV2/withdrawals; do notreplace originalgeomean','status':'PASS','H0_five_geomean':mean,'evidence':'Original10 accepted source/cycles/raw hashes equal current row identities; withdrawalreleaseobjects equal'}, {'requirement':'Publish each pair with exact identities, Lane6handoff, originalbranch push/readback','status':'PASS','evidence':'10_PAIR_PUBLICATION_AUDIT.json; originalpublication+freshremote identicalpacketmetadata andchecksum manifests'}, {'requirement':'No Lane5 runtime recompile/migration/duplicate watcher/repeated unaffected qualification','status':'PASS_RECORDED_SCOPE','evidence':'All20exactoldofficialbinary hashes; independent config reviews runtime_binary_recompiled=false and existing11gate artifacts reused. Completionaudit is read-only; no execution/lease/migration performed.'}]
save('20_RUN_INTEGRITY.json',run_evidence);save('10_PAIR_PUBLICATION_AUDIT.json',pairs);save('CONDITION_QUALIFICATION_AUDIT.json',qualification_reviews);save('REQUIREMENT_AUDIT.json',requirements)
receipt={'status':'R19_FULL_OBJECTIVE_INDEPENDENT_COMPLETION_AUDIT_PASS','objective_scope':'Exact active r19 bounded Goal; does not claim later parallel/microopt experiment completion','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'goal_original_T0_unix':T0,'goal_original_deadline_unix':DEADLINE,'formal_results_current_accepted':20,'complete_pairs_remote_verified':10,'total_starts_with_retained_failed_retry':21,'maximum_starts':24,'selected_followups':['D2','L25'],'robustness_condition':'D4 onvectorAdd_4M andsad','max_concurrent_R19_from_intervals':max_live,'initial8_order':'Both D4 primary pairs beforeQ4primary launches','H0_five_geomean_unchanged':mean,'current_V2':state['binding'],'requirements':requirements,'later_work':'Parallel campaign32/72 andMQ2/RG1stage0/24 remain separate, incomplete/stopped. No controller/run started by this audit. Existing uncommittedR6preparations preserved,notcommitted. OPSV8receipt413d7300821f2d623ce8f638b866dd85fc6d729d unchanged.','read_only_state_checks':{'registry_unchanged':hashlib.sha256((root/'RUN_REGISTRY.json').read_bytes()).hexdigest()==registry_sha,'client_unchanged':digest(root/'CLIENT_CONTRACT.json')==client_sha},'original_last_pair_publication':max(pairs,key=lambda v:v['generation'])['publication_commit']}
assert all(receipt['read_only_state_checks'].values());save('RECEIPT.json',receipt)
print(json.dumps({'status':receipt['status'],'formal_results':20,'pairs':10,'starts':21,'max_concurrent_R19':max_live,'original_last_pair_publication':receipt['original_last_pair_publication'],'requirements':len(requirements),'verified_local_files':len(cache)}))
