import pathlib,json,hashlib,importlib.util,tempfile,types,copy,os,subprocess,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('isolated_workingset40_binding_QA',T/'tools/sweep_host_execution_v2.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
with tempfile.TemporaryDirectory(prefix='dtc40_zero_model_binding_') as tmp:
 root=P(tmp);a.T=root;(root/'control/qualification_ledger').mkdir(parents=True);(root/'control/input_bindings').mkdir();(root/'tools').mkdir();(root/'tools/sweep_native_cap1m.py').write_text('CPU_FIXTURE_ONLY');cell='NEW';uid='FIXTURE_UUID';out=root/uid;out.mkdir();bind=root/'control/input_bindings/DIGEST.json';bind.write_text(json.dumps({'qualification':{'rows':[{'full_SHA_current_size_mtime':[64*1024**2,0]}]}}));orig={'cohort':cell,'host_cpu':4,'input_digest':'DIGEST','input_binding_sha256':sha(bind),'limits':{'max_process_tree_rss_bytes':16*G},'scientific_options':['SAME']};(root/'control'/(cell+'_SPEC.json')).write_text(json.dumps(orig));claims={'claims':{cell:{'host_cpu':64}}};cp=root/'control/POOL_DISPATCH_RESERVATIONS.json';cp.write_text(json.dumps(claims));fq={'consumed':{cell:{'uuid':uid}}};profile={'preserved_prefix_cells':['OLD'],'allowed_CPUs':[4,64],'control_CPUs':sorted(os.sched_getaffinity(0)),'plan_sha256':'FIXTURE'}
 def save(p,r):
  with P(p).open('x') as f:json.dump(r,f)
 base={'cgroup_memory_max':str(256*G),'cgroup_memory_current':40*G,'host_MemAvailable_bytes':300*G,'reserved_additional_live_and_candidate_RAM_bytes':16*G,'physical_RAM_pass':True,'physical_disk_pass':True}
 fake=types.SimpleNamespace(spec_for=lambda c:copy.deepcopy(dict(orig,cohort=c)),resources=lambda s,f=False:dict(base),exclusive=save,child_info=lambda pid:{'pid':pid},read_current_authority=lambda:({'registered_future_requests':{'FIXTURE':fq}},{}),REQUEST='FIXTURE');a.plan=lambda n:(fq,profile);fake=a.install(fake)
 assert fake.spec_for(cell)['host_cpu']==64 and orig['host_cpu']==4 and fake.spec_for('OLD')['host_cpu']==4
 r=fake.resources(fake.spec_for(cell),True);assert r['physical_RAM_pass'] and r['reserved_additional_live_and_candidate_RAM_bytes']==4*G and r['RAM_reservation_entries'][0]['hard_cap_bytes']==16*G and len(r['cgroup_memory_stat_for_credit'])==6
 fake.exclusive(root/'control/qualification_ledger'/(cell+'.INTENT.json'),{'cohort':cell,'uuid':uid});i=read(root/'control/qualification_ledger'/(cell+'.INTENT.json'));fake.exclusive(out/'NATIVE_LAUNCH.json',{'scientific_qualification_uuid':uid});assert read(out/'NATIVE_LAUNCH.json')['host_execution_binding']==i['host_execution_binding'] and i['host_execution_binding']['profile']=='HOST_WORKINGSET40_V2'
 child=subprocess.Popen(['/usr/bin/python3','-c','import time;time.sleep(2)'],preexec_fn=lambda:os.sched_setaffinity(0,{64}))
 try:
  obs=fake.child_info(child.pid);assert obs['host_cpu_affinity_actual']==[64];fake.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',obs)
  try:fake.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(obs,host_cpu_affinity_actual=[65]));raise RuntimeError('wrong_CPU_not_rejected')
  except AssertionError:pass
 finally:child.wait(timeout=4)
qp=T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json';q=read(qp);q['checks']+=['V2_only_future_CPU_override_preserves_original_fields_and_legacy_CPU','actual_V2_resource_sample_records4GiB_estimate16GiB_hard_and_raw_credit_inputs','V2_INTENT_launch_actual_PID_CPU_binding_and_wrong_CPU_rejection'];q['check_count']=len(q['checks']);q['CPU_fixture_only_no_scientific_simulator']=True;q['qualification_extension_source_sha256']=sha(T/'tools/working_set40_cpu_binding_qualification.py');qp.rename(T/'control/draft_preimages/R9_QUAL_BEFORE_CPU_BINDING_EXTENSION.json')
with qp.open('x') as f:json.dump(q,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','checks':q['check_count'],'model_starts':0,'controller_sha256':q['controller_sha256']}))
