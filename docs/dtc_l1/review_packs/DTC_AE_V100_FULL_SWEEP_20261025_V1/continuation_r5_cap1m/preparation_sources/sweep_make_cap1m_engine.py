import pathlib,ast,json
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');source=T/'tools/sweep_native.py';s=source.read_text()
def replace(a,b,n=1):
 global s
 assert s.count(a)==n,(a,s.count(a));s=s.replace(a,b)
replace('from sweep_storage_guard import NativeDTCGuard','from sweep_guard_cap1m import NativeDTCGuard')
replace("q['controller_sha256']==sha(__file__)","registered_profile(q)['engine_sha256']==sha(__file__)",2)
count=s.count("str(ROOT/s['project']/'bin/accel-sim.out')");assert count==2;s=s.replace("str(ROOT/s['project']/'bin/accel-sim.out')","s['native_simulator_argv'][0]")
replace("'old_ledger_mutations':0,'output':str(out)","'old_ledger_mutations':0,'operational_resource_profile':prepared['operational_resource_profile'],'output':str(out)")
replace("'finite_native_launcher_sha256':sha(__file__)","'finite_native_launcher_sha256':sha(__file__),'operational_resource_profile':prepared['operational_resource_profile']")
replace("'request':REQUEST,'scientific_starts':0}","'request':REQUEST,'operational_resource_profile':registered_profile(q),'scientific_starts':0}")
replace("for kind,commit in [('core',s['core_commit']),('framework',s['framework_commit'])]:\n  require(subprocess.check_output(['git','-C',str(ROOT/kind),'rev-parse','HEAD'],text=True).strip()==commit,'source HEAD drift')\n  require(not subprocess.check_output(['git','-C',str(ROOT/kind),'status','--porcelain'],text=True).strip(),'source worktree dirty')","for kind,commit in [('core',s['core_commit']),('framework',s['framework_commit'])]:\n  repo=P(s.get('source_worktrees',{}).get(kind,str(ROOT/kind)))\n  require(subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==commit,'source HEAD drift')\n  require(not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip(),'source worktree dirty')")
s+='''
PROFILE_ID='OBSERVABILITY_CAP1M_WALL90_V1'
def registered_profile(q):
 p=q.get('operational_engine_profiles',{}).get(PROFILE_ID)
 require(isinstance(p,dict) and p.get('engine_sha256')==sha(__file__),'precise observational engine not registered')
 candidate=ROOT/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json'
 require(p['candidate_sha256']==sha(candidate),'runtime candidate changed')
 c=read(candidate)
 require(p['source_pins']==c['source_pins'] and p['strict_sha256']==c['strict_sha256'] and p['framework_binary']==c['framework_binary'] and p['framework_commit']==c['framework_commit'],'runtime profile/source membership changed')
 require(c['profile_id']==PROFILE_ID and c['max_records']==1048576 and c['wall_seconds']==7776000 and c['finite_budget']==356 and c['model_retries']==0,'runtime amendment outside finite scope')
 for r in p['source_pins']:require(sha(r['path'])==r['sha256'],'pinned runtime amendment dependency changed')
 require(q['controller_sha256']==sha(ROOT/'tools/sweep_native.py'),'original engine history changed')
 return p
_original_scientific_spec_for=spec_for
def spec_for(cohort):
 original=_original_scientific_spec_for(cohort);reg,_=read_current_authority();q=reg['registered_future_requests'][REQUEST];entry=q.get('effective_specs',{}).get(cohort)
 if entry is None:return original
 profile=registered_profile(q);path=ROOT/'control/effective_specs'/(cohort+'.json')
 require(entry['path']==str(path) and entry['sha256']==sha(path) and entry['original_spec_sha256']==sha(ROOT/'control'/(cohort+'_SPEC.json')) and entry['profile']==PROFILE_ID,'effective spec identity changed')
 import sweep_cap1m_specs as effective
 derived=read(path);require(derived==effective.derive(original,read(ROOT/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json')),'effective spec changed outside allowed observational runtime fields')
 return derived
'''
dest=T/'tools/sweep_native_cap1m.py';ast.parse(s)
with dest.open('x') as f:f.write(s)
front=(T/'tools/sweep_frontend.py').read_text().replace("T/'tools/sweep_native.py'","T/'tools/sweep_native_cap1m.py'")
with (T/'tools/sweep_frontend_cap1m.py').open('x') as f:f.write(front)
strict=(T/'tools/sweep_strict.py').read_text();a="s=read(T/'control'/(cohort+'_SPEC.json'));req=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')";assert strict.count(a)==1
strict=strict.replace(a,"s=cap_engine.spec_for(cohort);req=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')")
a="need(sha(__file__)==req['strict_sha256'],'qualified strict source changed')";assert strict.count(a)==1
strict=strict.replace(a,"q=cap_engine.read_current_authority()[0]['registered_future_requests'][cap_engine.REQUEST];need(cap_engine.registered_profile(q)['strict_sha256']==sha(__file__),'qualified runtime strict source changed')")
a="need(str(T/'DTC/bin/accel-sim.out') in pid['maps'],'actual mapped simulator')";assert strict.count(a)==1;strict=strict.replace(a,"need(s['native_simulator_argv'][0] in pid['maps'],'actual exact versioned mapped simulator')")
strict+='''
def _load_cap_component(name,file):
 spec=importlib.util.spec_from_file_location(name,T/'tools'/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
cap_engine=_load_cap_component('cap1m_exact_spec_and_source','sweep_native_cap1m.py')
old_strict=_load_cap_component('untouched_original_whole_strict','sweep_strict.py')
_versioned_terminal=terminal
def terminal(cohort):
 q=cap_engine.read_current_authority()[0]['registered_future_requests'][cap_engine.REQUEST]
 return _versioned_terminal(cohort) if cohort in q.get('effective_specs',{}) else old_strict.terminal(cohort)
'''
ast.parse(strict)
with (T/'tools/sweep_strict_cap1m.py').open('x') as f:f.write(strict)
print('CAP1M_ENGINE_FRONTEND_STRICT_PREPARED_NO_AUTHORITY_MUTATION')
