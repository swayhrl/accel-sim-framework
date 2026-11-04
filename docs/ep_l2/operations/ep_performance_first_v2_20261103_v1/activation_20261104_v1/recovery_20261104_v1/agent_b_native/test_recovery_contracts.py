import pathlib,json,hashlib,importlib.util,copy,sys,subprocess,ast
P=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
rows=[]
def check(name,fn,negative=False):
 try:
  fn()
  if negative:raise AssertionError('negative accepted')
 except Exception as e:
  if not negative:raise
  rows.append(dict(name=name,status='PASS_EXPECTED_REJECT',reason=str(e)));return
 rows.append(dict(name=name,status='PASS'))
gs=read(P/'RECOVERY_GROUPS.json')['groups']
for tag,g in gs.items():
 r=pathlib.Path(g['new_runtime_root']);old=pathlib.Path(g['old_runtime_root']);root=pathlib.Path(g['data_ROOT'])
 m=load(r/'mode_contract.py','contract_'+tag); oldexact=m.exact
 q=read(P/tag/'HOST_QUALIFICATION_CANDIDATE.json');q['status']='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED';q['approved_by']='EP-MAIN'
 # In-memory CPU-only HostQ fixture; not written as a signed Main artifact.
 fake=dict(path='CPU_ONLY_IN_MEMORY_HOSTQ',sha256='CPU_ONLY')
 m.exact=lambda z:copy.deepcopy(q)if z==fake else oldexact(z)
 specs={}
 for case in g['original_admitted_specs']:
  a=read(root/'cases'/case/'control/FROZEN_SPEC.json');b=copy.deepcopy(a)
  for k,f in {'host_common_ref':'ep_perf_common_v2.py','host_engine_ref':'ep_perf_native_wv_modes_draft.py','archive_module_ref':'ep_perf_archive.py','postprocess_module_ref':'ep_perf_postprocess.py','validation_module_ref':'mode_aware_terminal.py','mode_contract_ref':'mode_contract.py'}.items():b[k]=ref(r/f)
  b['host_qualification_ref']=fake
  specs[case]=b if case in g['unconsumed']else a
  if case in g['unconsumed']:check(tag+' static '+case,lambda b=b:m.validate_static(b))
 for case in g['unconsumed']:
  b=specs[case];peer=specs[b['same_background_peer_cohort']]
  check(tag+' mixed_or_new_fair_peer '+case,lambda b=b,peer=peer:m.validate_fair_pair(b,peer))
 b=copy.deepcopy(specs[g['unconsumed'][0]])
 for key,value in [('source_identity',dict(b['source_identity'],binary_sha256='0'*64)),('observer_env',dict(b['observer_env'],BOGUS='1')),('expected_effective_options',dict(b['expected_effective_options'],**{'-dram_latency':'101'}))]:
  z=copy.deepcopy(b);z[key]=value;check(tag+' reject '+key,lambda z=z:m.check_background(z),True)
 if tag=='system':
  z=copy.deepcopy(b);z['ordered_configs'][-1]['path']='/tmp/unauthorized_samebytes/final_system850.config';z['system_final_overlay_ref']=copy.deepcopy(z['ordered_configs'][-1]);check('system reject arbitrary overlay path',lambda:m.check_background(z),True)
 # Native scope negative controls never enter a real accepted cohort/engine.
 native=P/tag/'native_recovery_20261104_v1'
 for case in ['UNKNOWN','EP_PERF_VECTOR4M_F_REF_V1','E2-DTC2A16-NOT-AUTHORIZED']+g['consumed']:
  check(tag+' native reject '+case,lambda case=case:(_ for _ in ()).throw(ValueError('rejected expected'))if subprocess.run([str(native),'experiment','prepare',case,'--project','EP_L2'],capture_output=True).returncode==2 else None,True)
 # All production math / stage functions stay byte-identical except the isolated System overlay check.
 oldtext=(old/'ep_perf_native_wv_modes_draft.py').read_text();newtext=(r/'ep_perf_native_wv_modes_draft.py').read_text()
 def funcs(t):
  lines=t.splitlines(keepends=True);return {n.name:''.join(lines[n.lineno-1:n.end_lineno])for n in ast.parse(t).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 aa,bb=funcs(oldtext),funcs(newtext)
 assert [k for k in aa if aa[k]!=bb[k]]==['prepare']
 rows.append(dict(name=tag+' engine all functions except native prepare byte-identical',status='PASS',unchanged_functions=len(aa)-1))
 n=load(r/'native_recovery_review.py','native_'+tag);review=read(P/'APPROVED_NATIVE_INSERT_REVIEW.json');current=(P/'APPROVED_CURRENT_GLOBAL_2f5b59.bytes').read_bytes()
 check(tag+' Native actual2f exact proof',n.validate_current)
 for name,data in [('old46',(P/'HISTORICAL_GLOBAL_46c69.bytes').read_bytes()),('onebyte',current+b'\n'),('delete',current[1:]),('routealter',current.replace(b'E2-DTC2A16-',b'E2-XXX2A16-',1))]:check(tag+' Native reject '+name,lambda data=data:n.validate_bytes(data,review),True)
result=dict(schema='EP_MAIN_NATIVE_HOST_RECOVERY_CPU_V1',status='PASS',checks=len(rows),rows=rows,hostq_fixture='In-memory ONLY. Main signatures not fabricated/adopted. Full actual signed Spec engine review still Main activation.',scientific_starts=0,registry_writes=0,old_spec_native_source_writes=0)
(P/'RECOVERY_CPU_CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='PASS',checks=len(rows))))
