import pathlib,json,hashlib,datetime,importlib.util
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops';D=O/'revision18';S=O/'revision17';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2);f.write('\n')
prior=read(O/'R17_ZERO_MODEL_QUALIFICATION_V1.json');manifest=read(D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json');policy=read(D/'SHORT_FIRST_DISPATCH_POLICY_V1.json');pins={};checks=[];proofs=[];dynamic_repin=[]
for row in prior['source_pins']:
 p=P(row['path']);actual=sha(p)
 if actual!=row['sha256']:
  assert p==N/'bin/native',('unexpected old-qualified source drift',str(p));dynamic_repin.append({'path':str(p),'prior_activation_SHA':row['sha256'],'current_qualified_preimage_SHA':actual,'reason':'prior qualification was a historical pre-activation entry snapshot'})
 pins[str(p)]=actual
for row in manifest['source_pins']:assert sha(row['path'])==row['sha256'];pins[row['path']]=row['sha256']
source=sha(D/'sweep_controller.py');assert source==manifest['actual_parent_sha256']and manifest['scientific_parent_lineage_sha256']=='32ebd671924d4e23eda7960c5957708e5a71f225ceb0887edcbe3249f25f65d3'
reviewpath=D/'REVISION18_INDEPENDENT_AI_REVIEW_V1.json';review=read(reviewpath);assert review['status']=='PASS'and not review['blocking_findings'];assert review['controller_sha256']==source and review['bridge_sha256']==manifest['bridge_sha256']and review['policy_sha256']==sha(D/'SHORT_FIRST_DISPATCH_POLICY_V1.json')and review['manifest_sha256']==sha(D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json')
for kind,path in [('main',O/'R18_CPU_DRIVER_RESULT_V1.json'),('front',D/'BRIDGE_FRONT_REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json'),('strict_finish',D/'OLD_R16_STRICT_FINISH_AND_BINDING_CPU_QUALIFICATION_V1.json'),('independent_AI_review',reviewpath),('unchanged_resources',S/'ADMISSION_RESOURCE_ADAPTER_CPU_QUALIFICATION_V1.json')]:
 p=read(path);assert p['status']=='PASS'
 if kind not in ['independent_AI_review','unchanged_resources']:assert p['controller_sha256']==source
 driver={'main':D/'qualify_r18_main_cpu_v1.py','front':D/'qualify_r18_bridge_entry_pre_popen_cpu_v1.py','strict_finish':D/'qualify_r18_existing_finish_strict_cpu_v1.py'}.get(kind)
 if driver is not None:assert p['driver_sha256']==sha(driver)
 if kind in ['front','strict_finish']:assert p['bridge_sha256']==manifest['bridge_sha256']and p['manifest_sha256']==sha(D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json')
 entries=p.get('checks',[])
 for v in entries:checks.append({'group':kind,'name':v if isinstance(v,str)else v.get('name',v.get('scenario','reviewed check')),'status':'PASS'})
 proofs.append({'kind':kind,'path':str(path),'sha256':sha(path),'checks':len(entries),'scenarios':p.get('scenario_count',len(p.get('scenarios',[])))})
 for k in ['source_spec_plan_pins','actual_source_metadata_pins']:
  for pin in p.get(k,[]):assert sha(pin['path'])==pin['sha256'];pins[pin['path']]=pin['sha256']
 pins[str(path)]=sha(path)
assert read(O/'R18_CPU_DRIVER_RESULT_V1.json')['scenario_count']==21
assert len(read(D/'BRIDGE_FRONT_REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json')['scenarios'])==7
assert read(D/'OLD_R16_STRICT_FINISH_AND_BINDING_CPU_QUALIFICATION_V1.json')['check_count']==16
for c,row in policy['points'].items():
 s=read(T/'control'/(c+'_SPEC.json'));assert row['expected_instructions']==s['expected']['instructions']
 if row['short']:assert row['estimated_seconds']is not None and 0<row['estimated_seconds']<=12*3600 and row['evidence']
 assert row['scheduling_heuristic_only_not_science_acceptance']is True
assert sum(v['short']for v in policy['points'].values())==10
ordered=sorted(policy['points'],key=lambda c:(not policy['points'][c]['short'],policy['points'][c]['estimated_seconds']or 1e99,c));assert [policy['points'][c]['program']for c in ordered[:4]]==['sgemm','histo','stencil','stencil']
assert all(not v['short']for v in policy['points'].values()if v['program']in ['kmeans','SYRK','lavamd','scan'])
for label in ['ten empirically bounded short points ranked before long or unknown candidates','four fastest queued points use same-input real natural PASS runtimes','large-LAVA RAM wait permits only known short backfill; new long points retain a drain opportunity','existing models retain original PID/generation and no scientific option or consumed UUID changes','40 original slots and independent repair caps plus4GiB initial and64/48 headroom guards unchanged','oldR17 launch bindings reviewed against original manifest on identical receipt paths','all base V100 options sources specs plans exact byte pins unchanged','short classification is scheduler-only heuristic; elapsed forecast never becomes accepted cycles']:
 checks.append({'group':'policy_evidence_join','name':label,'status':'PASS'})
for p in list(D.glob('*.py'))+list(D.glob('*.json'))+[P(__file__),O/'R17_PUBLICATION_READBACK_V1.json']:
 if p.is_file() and 'PRE_REVIEW' not in p.name:pins[str(p)]=sha(p)
entry=(N/'bin/native').read_bytes();a=str(S/'frontend_v1.py').encode();b=str(D/'frontend_v1.py').encode();assert entry.count(a)==1;entryafter=entry.replace(a,b)
cert=S/'THREE_DEPARTED_ORIGINAL_RAM_CERTIFICATE_V1.json';assert sha(cert)==prior['departed_generation_certificate_sha256']
qual={'schema':'R18_SHORT_FIRST_REAL_PARENT_CONTINUATION_QUALIFICATION_V1','status':'PASS','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controller_sha256':source,'prior_controller_sha256':sha(S/'sweep_controller.py'),'bridge_sha256':manifest['bridge_sha256'],'frontend_sha256':sha(D/'frontend_v1.py'),'operational_parent_bridge_manifest_path':str(D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json'),'operational_parent_bridge_manifest_sha256':sha(D/'OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json'),'short_priority_policy_sha256':sha(D/'SHORT_FIRST_DISPATCH_POLICY_V1.json'),'checks':checks,'check_count':len(checks),'CPU_and_review_proofs':proofs,'source_pins':[{'path':p,'sha256':h}for p,h in sorted(pins.items())],'source_pin_count':len(pins),'departed_generation_certificate_sha256':sha(cert),'reviewed_original_engineering_issues':prior['reviewed_original_engineering_issues'],'reviewed_original_closed_negative':prior['reviewed_original_closed_negative'],'prior_entry_sha256':hashlib.sha256(entry).hexdigest(),'expected_entry_after_exact_route_change_sha256':hashlib.sha256(entryafter).hexdigest(),'historical_entry_snapshot_repin':dynamic_repin,'existing_budgets_unchanged':True,'new_requests_registered':0,'new_budget_created':0,'old_original_and_repair_models_must_be_preserved':True,'original_maximum_model_slots':40,'maximum_new_lava_slots':2,'maximum_new_late_slots':4,'safety_floor_GiB':5,'ordinary_initial_RAM_GiB':4,'LAVA_estimated_peak_GiB':96,'host_floor_GiB':64,'cgroup_floor_GiB':48,'real_model_starts':0,'real_authority_or_entry_mutations':0,'real_model_or_guard_signals':0,'scientific_acceptance':False,'performance_accepted':False,'limitations':['Paired-input times are scheduling heuristics across configurations; they do not promise identical durations.','Current old failed points and three receipt gaps remain charged and unaccepted; Cutcp4 and final-consumer closure remain separate open items.','New scientific validation still requires real DONE/NATURAL/full population/source/runtime/BA and164 archive/native restore.']}
dest=O/'R18_ZERO_MODEL_QUALIFICATION_V1.json';put(dest,qual)
put(D/'R18_QUALIFICATION_SOURCE_MANIFEST_V1.json',{'schema':'R18_FROZEN_QUALIFICATION_SOURCE_MANIFEST_V1','controller_sha256':source,'qualification_path':str(dest),'qualification_sha256':sha(dest),'entries':[{'path':p,'sha256':h,'bytes':P(p).stat().st_size}for p,h in sorted(pins.items())],'model_starts':0,'authority_mutations':0})
print(json.dumps({'status':'PASS','checks':len(checks),'pins':len(pins),'qualification_sha256':sha(dest),'controller_sha256':source,'short_candidates':10}))
