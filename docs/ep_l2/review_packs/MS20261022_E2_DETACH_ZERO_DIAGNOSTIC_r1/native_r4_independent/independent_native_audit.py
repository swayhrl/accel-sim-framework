"""Bounded read-only inspection of completed native controls, not execution."""
from pathlib import Path
import json,hashlib,sys,datetime,re,subprocess
OUT=Path('/tmp/e2_A2_r4_native_independent_review');N=Path('/workspace/ep_l2_ms20261019_e_results/A2_DETACH_OBSERVER_NATIVE_r4');BUILD=Path('/workspace/ep_l2_ms20261019_e_results/A2_DETACH_OBSERVER_BUILD_r4/BUILD_ONLY_RECEIPT.json')
R=json.loads((N/'RECEIPT.json').read_text());B=json.loads(BUILD.read_text());SPEC=json.loads((OUT/'BUILD_SPEC_r4.json').read_text());SCHEMA=json.loads((OUT/'COUNTER_SCHEMA.json').read_text());FIELDS=set(SCHEMA['counter_fields'])
sys.path.insert(0,'/tmp/e2_detach_runtime_decoder');from decoder import partitions
checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(condition,label):
 if not condition:raise AssertionError(label)
 checks.append(label)
def safe_read(p,maxbytes=16*2**20):
 p=Path(p);need(p.stat().st_size<=maxbytes,'bounded_read:'+p.name);return p.read_bytes()
need(len(FIELDS)==212,'exact212schema')
need(R['status']=='PRODUCER_FINITE_PASS_PENDING_E_INDEPENDENT_QUALIFICATION','native_scoped_status')
need(R['native_invocations_attempted']==R['native_invocations_completed']==48,'48attempted_completed')
need(R['application_starts']==0 and not R['runtime_ready'] and not R['independent_qualification'],'no_app_or_formal_qualification')
need(R['lease_released'] and R['own_lock_released'],'lease_lock_released')
need(sha(OUT/'BUILD_SPEC_r4.json')==R['spec_sha256']==B['spec_sha256'],'fixed_spec_source_receipt_hash')
need(sha(BUILD)==R['retained_build_receipt']['sha256'],'retained_build_receipt_hash')
for key in ('core_source_commit','framework_source_commit','vendor_commit','binary_sha256'):
 need(R[key]==B[key],'build_native_identity:'+key)
need(R['core_source_commit']=='9243f769620653f2a9d4df5599e9581e9dae6067','exactr4_core')
need(R['binary_sha256']=='d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13','exact_main_from_build_metadata_no_rehash')
tests={t['case']:t for t in R['tests']};plan={t['id']:t for t in R['planned_tests']};need(len(tests)==len(plan)==len(SPEC['cases'])==48,'exact48case_sets')
for p,digest in R['input_sha256'].items():need(sha(p)==digest,'native_input_hash:'+Path(p).relative_to(N).as_posix())
flag_evidence=[]
for name in ('ep_l2_detach_reference','ep_l2_detach_diagnostic'):
 directory=Path(R['build'])/'gpgpu-sim/CMakeFiles'/(name+'.dir');flags=directory/'flags.make';link=directory/'link.txt';ft=safe_read(flags).decode();lt=safe_read(link).decode()
 need(sha(flags)==B['assertion_flags_sha256'][str(flags)],'build_flags_sha:'+name)
 need('-DNDEBUG' not in ft and '-DNDEBUG' not in lt,'native_assertions_enabled:'+name)
 if name.endswith('reference'):
  need('-DEP_L2_DIAG_REFERENCE=1' in ft and '/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r39-own-pending-v1/src' in ft,'reference_compile_old_source_headers')
  need('/workspace/build/ep-l2-ms20261020-a-wad-pending-r40/libgpgpusim.a' in lt,'reference_link_original_d010_archive')
 else:need('src/gpgpu-sim/libgpgpusim.a' in lt,'new_fixture_link_new_archive')
 flag_evidence.append({'target':name,'flags_sha256':sha(flags),'link_sha256':sha(link),'binary_sha256_from_actual_build_receipt':B['test_binary_sha256'][str(Path(R['build'])/'gpgpu-sim'/name)]})
rows=[];groups={};record_count=0;frame_count=0;equation_calls=0;raw_total=0;source_nonderived_relations=0;frame_metrics=[]
for case in SPEC['cases']:
 cid=case['id'];t=tests[cid];p=plan[cid];jpath=N/(cid+'.native.json');j=json.loads(safe_read(jpath));raw=safe_read(j['raw_log']);text=raw.decode();raw_total+=len(raw)
 need(sha(jpath)==t['native_evidence_sha256'],'native_json_bound:'+cid)
 need(j['actual_exit']==j['expected_exit']==case['expected_exit']==0 and j['expectation_verified'] is True,'actual_wait_exit0:'+cid)
 need(j['required_terminal']==case['required_terminal'] and text.splitlines().count(case['required_terminal'])==1,'required_terminal_exactly_once:'+cid)
 need(hashlib.sha256(raw).hexdigest()==j['raw_log_sha256'],'actual_native_log_sha:'+cid)
 need(j['command']==p['native_command'],'actual_native_command:'+cid)
 need(j['command'][0]==str(Path(R['build'])/'gpgpu-sim'/case['target']),'native_target_path:'+cid)
 need(j['binary_sha256']==B['test_binary_sha256'][j['command'][0]],'native_binary_origin_build_bound:'+cid)
 wrapper=j['command'];need(t['command'][t['command'].index('--')+1:]==wrapper,'checker_wrapped_actual_command:'+cid)
 need(t['exit_code']==0 and sha(t['log'])==t['log_sha256'],'checker_exit_and_log_sha:'+cid)
 need(type(j['native_pid']) is int and j['native_pid']>0 and j['native_started_unix']>0,'actual_native_pid_start:'+cid)
 sig=[line for line in text.splitlines() if line.startswith('EPL2MS_TEST|SEMANTIC|')];need(len(sig)==1,'one_semantic_signature:'+cid)
 old=[line for line in text.splitlines() if line.startswith(('EPL2ROV1|','EPL2ROC1|'))]
 groups.setdefault(case['control_class'],[]).append({'id':cid,'signature':sig[0],'old':old})
 lines=text.splitlines();frames=[];current=None
 for line in lines:
  if line.startswith('DETACH_NATIVE_FRAME_BEGIN|'):need(current is None,'frame_not_nested:'+cid);current={'id':line.split('|',1)[1],'records':[],'scope_lines':[]};frames.append(current)
  elif line.startswith('DETACH_NATIVE_FRAME_END|'):need(current is not None and current['id']==line.split('|',1)[1],'frame_end_matches:'+cid);current=None
  elif line.startswith('EPL2DETACH_DIAG_V1|'):
   need(current is not None,'diagnostic_in_named_native_frame:'+cid);current['records'].append(json.loads(line.split('|',1)[1]))
  elif current is not None and line.startswith(('SUBCONTROL_PASS|','CONTROL_SCOPE|')):current['scope_lines'].append(line)
 need(current is None,'no_partial_native_frame:'+cid)
 if case['observer']==1 and case['target']!='ep_l2_detach_reference':
  samples=0
  for frame in frames:
   if not frame['records']:continue
   frame_count+=1;record_count+=len(frame['records'])
   selected=[q for q in frame['records'] if q['record']=='SLICE'];glob=[q for q in frame['records'] if q['record']=='GLOBAL'];phases=[q for q in frame['records'] if q['record']=='PHASE'];need(len(glob)==1 and selected,'frame_has_selected_slice_and_global:'+cid+frame['id'])
   for q in selected+glob:
    c=q['counters'];need(set(c)==FIELDS,'frame_exact212:'+cid+frame['id']+q['record'])
    need(all(type(v) is int and 0<=v<2**64 for v in c.values()),'frame_uint64_notbool:'+cid+frame['id']+q['record'])
    partitions(c);equation_calls+=1
    need(c['ro_capacity_population']==c['ro_capacity_consulted']+c['ro_capacity_not_consulted']==c['requester_ro_candidate'],'r3_RO_population:'+cid+frame['id']+q['record'])
    for key in ('ro_descriptor','ro_address','ro_line_probe','ro_line_slots'):
     need(c[key+'_checked']==c[key+'_pass']+c[key+'_fail'] and c['ro_capacity_population']==c[key+'_checked']+c[key+'_unobserved'],'r3_predicate_partition:'+cid+frame['id']+q['record']+key)
    need(c['ro_descriptor_checked']==c['ro_capacity_consulted'] and c['ro_address_checked']==c['ro_descriptor_pass'] and c['ro_line_probe_checked']+c['ro_line_na_M_or_existing']==c['ro_address_pass'] and c['ro_line_slots_checked']==c['ro_line_probe_pass'],'source_short_circuit_coverage:'+cid+frame['id']+q['record'])
    need(c['pressure_eligible']==c['eligible_frontend_admitted']+c['eligible_frontend_denied']==c['eligible_prod_probe_reached']+c['eligible_prod_probe_not_reached']==c['eligible_capacity_consulted']+c['eligible_capacity_not_consulted'],'r3_eligible_joint_populations:'+cid+frame['id']+q['record'])
    need(c['eligible_prod_probe_reached']==sum(c[k] for k in ('eligible_rewrite_miss','eligible_rewrite_hit_reserved','eligible_kept_fail','eligible_relief_not_consulted','eligible_intermediate_other')),'r3_eligible_intermediate_partition:'+cid+frame['id']+q['record'])
    need(q['live_detached']==c['detach_success']-c['detached_retired']==0 and q['closure_ok'] and not q['overflow_invalid'] and not q['output_invalid'],'source_selected_population_and_flags:'+cid+frame['id']+q['record'])
   for q in selected:
    need(q['epoch_closed'],'selected_cache_epoch_closed:'+cid+frame['id'])
    ps=[q2 for q2 in phases if q2['slice']==q['slice']];need(all(sum(z['counters'][k] for z in ps)==q['counters'][k] for k in FIELDS),'all212_phase_rollup:'+cid+frame['id'])
   need(all(sum(z['counters'][k] for z in selected)==glob[0]['counters'][k] for k in FIELDS),'all212_selected_global_residual_zero:'+cid+frame['id'])
   samples+=sum(q['record']=='SAMPLE' for q in frame['records'])
   frame_metrics.append({'case':cid,'frame':frame['id'],'registered_cache_count':glob[0]['slice'],'emitted_selected_slices':[q['slice'] for q in selected],'global_epoch_closed':glob[0]['epoch_closed'],'selected_epochs_closed':True,'actual212_equations_and_rollups':'PASS','scope_lines':frame['scope_lines'],'key_counts':{k:glob[0]['counters'][k] for k in ('ro_capacity_population','ro_capacity_consulted','ro_capacity_not_consulted','ro_descriptor_fail','ro_address_fail','ro_line_slots_fail','denied_capacity','denied_missq','detach_success','detached_retired','eligible_relief_not_consulted')}})
  need(samples<=64,'native_process_sample_cap64:'+cid)
 rows.append({'case':cid,'actual_exit':j['actual_exit'],'native_pid':j['native_pid'],'native_started_unix':j['native_started_unix'],'required_terminal':j['required_terminal'],'native_receipt_sha256':sha(jpath),'actual_raw_sha256':j['raw_log_sha256'],'actual_raw_bytes':len(raw),'actual_binary_sha256_from_native_receipt':j['binary_sha256'],'binary_matches_build_metadata':True,'native_command':j['command'],'control_scope':'FINITE_NATIVE_ONLY_NOT_APPLICATION'})
for name,g in groups.items():
 need(len(g)==3 and len({x['signature'] for x in g})==1,'reference_off_on_cycles_events_state_exact:'+name)
 need(all(x['old']==g[0]['old'] for x in g),'reference_off_on_old_counters_exact:'+name)
subcontrols={'PRESSURE_STICKY_REUSE':'SUBCONTROL_PASS|M1_ADDRESS32_MERGE_CAPACITY|line_gate=NA','DETACH_THEN_LATER_DENIAL':'SUBCONTROL_PASS|MERGE_MISSQ_AND_ZERO_MISSING|finite_real_queue_full=1|zero_missing_admitted=1','ROLLUP_RESIDUAL':'SUBCONTROL_PASS|M0_LINE128|original_line_probe_and_capacity=REAL'}
for case,marker in subcontrols.items():
 for mode in ('reference','off','on'):
  txt=Path(json.loads((N/(case+'_'+mode+'.native.json')).read_text())['raw_log']).read_text();need(txt.splitlines().count(marker)==1,'real_subcontrol_terminal:'+case+'_'+mode)
for name in ('T1M1.config','T1M0.config'):
 txt=(N/'inputs/C_NATIVE'/name).read_text();need('-gpgpu_l2_rop_latency 0' in txt,'actual_native_ROP0:'+name)
r3=Path('/workspace/ep_l2_ms20261019_e_results/A2_DETACH_OBSERVER_NATIVE_r3/RECEIPT.json');r3j=json.loads(r3.read_text());need(r3j['status']!='PRODUCER_FINITE_PASS_PENDING_E_INDEPENDENT_QUALIFICATION','r3_failed_not_upgraded')
report={'schema':'E2_A2_R4_ACTUAL_NATIVE_INDEPENDENT_REVIEW_V1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_NATIVE_SCOPE_ONLY_PENDING_FORMAL_PRODUCER_AND_E_APPLICATION_QUALIFICATION','native_receipt':{'path':str(N/'RECEIPT.json'),'sha256':sha(N/'RECEIPT.json')},'build_receipt':{'path':str(BUILD),'sha256':sha(BUILD)},'fixed_Framework_commit':'5d137275143976c5e31a73cebae3e3c98559168d','actual_core_commit':R['core_source_commit'],'main_sha256_from_build_native_metadata':R['binary_sha256'],'main_physical_bytes_rehashed':False,'test_binary_origin':flag_evidence,'actual_native_invocations_reviewed':len(rows),'native_reruns':0,'reference_off_on_groups':len(groups),'all_cycles_event_state_old_RO_counters_exact':True,'source212_equation_calls_SLICE_and_GLOBAL':equation_calls,'diagnostic_native_frames_reviewed':frame_count,'diagnostic_record_count':record_count,'native_raw_bytes_read_for48cases':raw_total,'checks_passed':len(checks),'source_checker_provenance':{'path':str(OUT/'verify_detach_controls.py'),'sha256':sha(OUT/'verify_detach_controls.py'),'copied_from_fixed_Git':True,'actual_pure_log_verifier_exit':0},'cases':rows,'frame_evidence':frame_metrics,'r3_failure_preserved':{'path':str(r3),'sha256':sha(r3),'status':r3j['status']},'scope_limits':['Finite directed native controls, not complete application64slices or performance equivalence.','Inactive constructed cache instances remain unprinted/unclosed in native GLOBAL; all212 eventcount residuals are0 but missing slice records are not invented. Full GPU/application decoder was not used to accept these fixture frames.','Some native fixture processes construct several sequential cache owners, so framed source-native assertions and equivalence are used; no cross-fixture cumulative run identity is fabricated.','New main actual file/archive physical hashes and formal A2 producer publication/release remain root final intake obligations; native testbinary hashes were cross-bound to actual buildreceipt and compile/link provenance, without duplicating full ELF/archive hashing.','No existing main61 blanket qualification or old-S/new-F performance baseline is inherited.'],'real_remaining_gaps':['Formal A2 producer delivery not yet assumed by this review.','E exact new main/archive/build/schema212/config/input/oracle/Q and original runtime resource admission remain required.','Actual future singleSGEMM nativewait0/fullinstructions/64slice/globalclosed/drain and scientific diagnosis must independently close; this48native PASS is not CURRENT_ACCEPTED.'],'actions':{'native_build_app_processes_started':0,'A2_artifacts_or_repo_changed':False,'central_state_changed':False,'all_new_outputs_under_tmp':True}}
(OUT/'INDEPENDENT_NATIVE_REVIEW.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(OUT/'INDEPENDENT_CHECK_LOG.json').write_text(json.dumps({'passed':checks},indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','actual_native_invocations_reviewed','reference_off_on_groups','source212_equation_calls_SLICE_and_GLOBAL','diagnostic_native_frames_reviewed','diagnostic_record_count','native_raw_bytes_read_for48cases','checks_passed')}))
