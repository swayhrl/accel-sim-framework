from pathlib import Path
import importlib.util,json,gzip,hashlib,tempfile,copy,sys,os
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/agents/A_final_analysis_watcher_preparation_v1');spec=importlib.util.spec_from_file_location('private_waiter_CPU_only',O/'analysis_waiter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checks=[]
def ck(n,v):assert v,n;checks.append(n)
def rejects(n,fun):
 try:fun()
 except (AssertionError,ValueError,FileExistsError):checks.append(n);return
 raise AssertionError('EXPECTED_REJECTION_'+n)
base=dict(schema='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1',request=m.REQ,source_qualified=True,all_registered48_terminal_verified=True,summary=dict(source_qualified=True,request=m.REQ,expected_CH=48,registered_consumed=48,registered_remaining=0,accepted_CH=48,archived_negative_CH=0,verification_hold=0,await_result=0,all_registered48_terminal_verified=True,core32_fixed_input_n=32,expected_six_source_slots=192,observed_utc='CPU_ONLY'))
ck('light48allaccepted_ready',m.light_gate(base)['ready']);q=copy.deepcopy(base);q['summary'].update(accepted_CH=43,archived_negative_CH=5);ck('light43accepted5negative_ready_not_allaccepted_required',m.light_gate(q)['ready'])
for name,change in [('pending',dict(accepted_CH=47,await_result=1)),('HOLD',dict(accepted_CH=47,verification_hold=1)),('unconsumed',dict(registered_consumed=47,registered_remaining=1)),('terminalflag',dict(all_registered48_terminal_verified=False)),('unqualified',dict(source_qualified=False)),('missingfield',dict(await_result=None))]:
 q=copy.deepcopy(base);q['summary'].update(change);ck(name+'_never_ready',not m.light_gate(q)['ready'])
q=copy.deepcopy(base);q['summary']['expected_CH']=49;rejects('wrongbudget_HOLD',lambda:m.light_gate(q));q=copy.deepcopy(base);q['summary']['registered_consumed']=49;rejects('budget_consumedplusremaining_not48_HOLD',lambda:m.light_gate(q));q=copy.deepcopy(base);q['request']='WRONG';rejects('wrong_scientific_request_HOLD',lambda:m.light_gate(q))
fixtures=O/'private_cpu_fixtures';fixtures.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=fixtures)as td:
 td=Path(td);oldofficial=m.OFFICIAL;m.OFFICIAL=td/'B/PUBLICATION_PROVIDER.json';snap=m.OFFICIAL.parent/'snapshots/CPU_ONLY';snap.mkdir(parents=True);expected=m.rd(m.STAGE_PINS[-1][0])['points']
 def payload(accepted=48):
  p=copy.deepcopy(base);p['summary'].update(accepted_CH=accepted,archived_negative_CH=48-accepted);p['observed_utc']='CPU_ONLY';p['snapshot']=str(snap);p['qualification_manifest']=dict(path=str(m.A/'agents/B_runtime_analysis_v1/runtime_adapter_v1/MANIFEST.json'),sha256=m.QUAL_SHA);obs=dict(source_qualified=True,registration_granted=True,registered_consumed=48,registered_remaining=0,request=m.REQ,observations=[])
  for i,e in enumerate(expected):obs['observations'].append(dict(cohort=e['cohort'],input_digest=e['input_digest'],profile=e['profile'],design='CH',status=m.PASS if i<accepted else m.NEG,accepted=i<accepted,cycles=123 if i<accepted else None,uuid='CPU_ONLY_NOT_SCIENTIFIC_UUID_'+str(i)))
  return p,obs
 def freeze(p,obs):
  fs=[]
  for leaf,j in [('SUMMARY.json.gz',p['summary']),('OBSERVATIONS.json.gz',obs),('CORE32_RESULTS.json.gz',{})]:
   f=snap/leaf;f.write_bytes(gzip.compress(json.dumps(j).encode(),mtime=0));fs.append(dict(path=str(f),sha256=m.sha(f)))
  mf=dict(source_qualified=True,schema='DTC_REMAINING48_READONLY_ANALYSIS_SNAPSHOT_V1',adapter=dict(sha256=m.ADAPTER_SHA),runtime_plan=dict(sha256=m.PLAN_SHA),files=fs);fp=snap/'MANIFEST.json';fp.write_text(json.dumps(mf));p['files']=fs;p['manifest']=dict(path=str(fp),sha256=m.sha(fp));return json.dumps(p).encode()
 try:
  p,o=payload(43);raw=freeze(p,o);_,g=m.full_gate(raw);ck('full43plus5_exact48_UUIDs_ready',g['unique_UUIDs']==48 and g['accepted']==43 and g['archived_negative']==5)
  p,o=payload();o['observations'][-1]['uuid']=o['observations'][0]['uuid'];raw=freeze(p,o);rejects('duplicate_UUID_HOLD',lambda:m.full_gate(raw))
  p,o=payload();o['observations'][0]['cohort']='CPU_ONLY_EXTRA';raw=freeze(p,o);rejects('wrongcohortset_HOLD',lambda:m.full_gate(raw))
  p,o=payload(43);o['observations'][-1]['cycles']=0;raw=freeze(p,o);rejects('negative_zero_cycles_not_null_HOLD',lambda:m.full_gate(raw))
  p,o=payload();raw=freeze(p,o);f=snap/'SUMMARY.json.gz';f.write_bytes(b'CPU_ONLY_CORRUPTED');rejects('summary_SHA_drift_HOLD',lambda:m.full_gate(raw))
  p,o=payload();raw=freeze(p,o);p['snapshot']=str(td/'outside_snapshot');raw=json.dumps(p).encode();rejects('snapshot_namespace_escape_HOLD',lambda:m.full_gate(raw))
 finally:m.OFFICIAL=oldofficial
 # Service-level nonblocking flock plus immutable one-attempt marker.
 lock=m.acquire_lock(td/'service.lock');ck('service_first_lock_acquired',lock is not None);ck('duplicate_live_waiter_lock_rejected',m.acquire_lock(td/'service.lock')is None);lock.close();lock2=m.acquire_lock(td/'service.lock');ck('departed_lock_can_be_observed',lock2 is not None);lock2.close()
 claim=td/'ATTEMPT_CLAIM.json';m.claim_attempt(claim,dict(CPU_ONLY=True,run=1));before=m.sha(claim);rejects('cross_restart_duplicate_attempt_O_EXCL',lambda:m.claim_attempt(claim,dict(run=2)));ck('attempt_marker_not_overwritten',m.sha(claim)==before)
 source=td/'CPU_ONLY_SOURCE.py';source.write_text('CPU_ONLY=1\n');wanted=m.sha(source);source.write_text('CPU_ONLY=2\n');rejects('source_drift_exact_production_checker',lambda:m.checked(source,wanted))
 stages=[dict(name=n)for n in ['C_FINAL48','B_FINAL24','ROOT_MATH','ROOT_RENDERER_V2']];calls=[]
 def runner(s):calls.append(s['name']);return dict(stage=s['name'],returncode=0)
 r=m.chain(stages,runner,lambda s:{'CPU_ONLY_VALIDATED':True},lambda:None);ck('oneCPUchain_order_and_allfour_once',r['success']and calls==[s['name']for s in stages])
 calls=[]
 def failC(s):calls.append(s['name']);return dict(stage=s['name'],returncode=2)
 r=m.chain(stages,failC,lambda s:{},lambda:None);ck('C_failure_stops_B_math_renderer',not r['success']and calls==['C_FINAL48'])
 calls=[]
 def failB(s):calls.append(s['name']);return dict(stage=s['name'],returncode=1 if s['name']=='B_FINAL24'else 0)
 r=m.chain(stages,failB,lambda s:{},lambda:None);ck('B_failure_stops_math_renderer',not r['success']and calls==['C_FINAL48','B_FINAL24'])
 calls=[]
 def badresult(s):raise ValueError('CPU_ONLY_MISSING_PASS_ARTIFACT')
 r=m.chain(stages,runner,badresult,lambda:None);ck('exit0_without_PASS_artifact_stops_chain',not r['success']and calls==['C_FINAL48'])
 calls=[]
 def drift():raise ValueError('CPU_ONLY_SOURCE_DRIFT')
 r=m.chain(stages,runner,lambda s:{},drift);ck('source_drift_beforestage_noCPUlaunch',not r['success']and r['reason']=='SOURCE_DRIFT_HOLD'and calls==[])
 hs=td/'hold';hs.mkdir();m.hold(hs,'CPU_ONLY_FIRST_FAILURE');hh=m.sha(hs/'ANALYSIS_HOLD.json');m.hold(hs,'CPU_ONLY_SECOND_FAILURE');ck('first_HOLD_immutable',m.sha(hs/'ANALYSIS_HOLD.json')==hh)
 # Pure CLI plan contains the frozen provider and only the four approved source scripts.
 plan=m.make_plan('CPU_ONLY_NOT_CREATED',td/'CPU_ONLY_PROVIDER.fixed.json');ck('four_exact_argv_scripts_and_frozenprovider',len(plan)==4 and all(str(td/'CPU_ONLY_PROVIDER.fixed.json')in s['argv']for s in plan));ck('C_and_B_output_namespaces',str(m.A/'agents/C_final48_independent_audits_v1')in plan[0]['output']and str(m.BPREP/'updates')in plan[1]['output']);ck('renderer_under_A_snapshots_not_A_provider',str(m.A/'agents/A_figures_v1/snapshots')in plan[-1]['output']and plan[-1]['argv'][2]==str(m.A/'root_figures_v2/plot_core32.py'))
readiness=m.verify_source_contract();mount=m.verify_true164(O);actual=m.light_gate(json.loads(m.OFFICIAL.read_bytes()));ck('actual_source_and_genuine164_contract_PASS',readiness['status']=='SOURCE_CONTRACT_PINS_PASS'and mount['source']=='admin-wcx@10.208.130.164:/home/shared');ck('no_service_state_or_attempt_created',not m.STATE.exists())
result=dict(schema='DTC_FINAL_ANALYSIS_WAITER_CPU_QUALIFICATION_V1',status='PASS_PREPARATION_ONLY_NO_WAITER_OR_ACTUAL_CPU_CHAIN_STARTED',watcher_source_sha256=m.sha(O/'analysis_waiter.py'),independent_check_families=['Qualified fullterminal gate including archivednegative/null','Source and snapshot integrity/identity/namespace','fcntl live-duplicate barrier','Persistent O_EXCL one-attempt barrier','Strict C→B→math→v2 order and fail-stop results','Forward source drift stops before CPU','Actual frozen source/mount readiness; no service startup'],assertions=len(checks),checks=checks,synthetic_fixtures_private_and_not_results=True,actual_current_provider_light_gate=actual,actual_stage_source_contract=readiness,source_paths_unchanged=True,actual_subprocess_analysis_calls=0,actual_service_starts=0,new_simulator_starts=0,manual_Root_visual_narrative_D_signoff_required=True);(O/'CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');(O/'CONTRACT_READINESS.json').write_text(json.dumps(dict(status=readiness['status'],stage_pins=readiness['pins'],genuine164_mount=mount,service_started=False,CPU_chain_started=False),indent=2)+'\n');print(json.dumps(dict(status=result['status'],assertions=len(checks),source_sha256=result['watcher_source_sha256'],actual_light_gate=actual)))
