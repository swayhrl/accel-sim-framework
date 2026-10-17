import importlib.util,json,pathlib,sys,subprocess,hashlib,os,resource
fw=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane3-v1');sp=importlib.util.spec_from_file_location('cfg',fw/'util/ep_l2/parallel_potential_lane3/check_l1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
c=json.loads(pathlib.Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());data=subprocess.check_output(['git','show',c['registry_source_commit']+':util/ep_l2/ft_lane5/registry.py'],cwd='/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1');assert hashlib.sha256(data).hexdigest()==c['registry_client_sha256'];p=m.RAW/'.published_registry'/c['registry_client_sha256']/'registry.py';assert p.read_bytes()==data;sys.path.insert(0,str(p.parent));from registry import Registry,local_resources
r=Registry();out=m.RAW/'L1_32_H0_r4'/'guards';out.mkdir(exist_ok=False);rows=[];lease=None
try:
 live=local_resources();assert live['disk_free_bytes']>=50*2**30 and live['available_memory_bytes']-4*2**30>=64*2**30
 lease=r.build_lease('lane3',cpu=1,memory=4*2**30)
 for mode in ('B16_BANKED','U_WB16'):
  s=json.loads((m.ORIGINAL/('convolutionSeparable_'+mode+'.json')).read_text());base=[x['path'] for x in s['configs']]
  l1='-gpgpu_cache:dl1 S:4:128:64,L:T:m:L:L,A:512:8,16:0,32\n'
  cases=[('old_runtime_rejects32','/workspace/build/ep-l2-potential20261017-lane3-r2/probe',l1,False,'ROP40_H0'),('new_default_rejects32',str(m.BUILD/'probe'),l1,False,'H0'),('new_default128_control',str(m.BUILD/'probe'),'',True,'H0'),('new_illegal_expect32',str(m.BUILD/'probe'),l1+'-gpgpu_ep_l2_expected_l1_assoc 32\n',False,'H0'),('new_rejects_adaptive',str(m.BUILD/'probe'),l1+'-gpgpu_ep_l2_expected_l1_assoc 64\n-gpgpu_adaptive_cache_config 1\n',False,'H0')]
  for name,exe,text,success,regime in cases:
   cfg=out/(mode+'_'+name+'.config');cfg.write_text(text);log=cfg.with_suffix('.log');cmd=[exe,regime,*base,str(cfg)]
   with log.open('x') as f:proc=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=30,preexec_fn=m.limits)
   row={'mode':mode,'case':name,'exit':proc.returncode,'expected_success':success,'command':cmd,'log_sha256':m.digest(log),'log':str(log)};rows.append(row);assert (proc.returncode==0)==success,row
finally:
 if lease:r.release_build(lease,'lane3')
 m.write(out/'RECEIPT.json',{'lease':lease,'lease_released':bool(lease),'cases':rows,'apps':0,'scope':'Actual old/new configuration init and H0 production controls; new executable only recompiled gpu-sim.cc for directed test'})
print(json.dumps(rows,indent=2))
