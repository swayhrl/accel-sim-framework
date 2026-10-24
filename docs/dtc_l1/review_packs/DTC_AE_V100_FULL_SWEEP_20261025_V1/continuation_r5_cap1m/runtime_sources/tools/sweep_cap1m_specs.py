"""Exact derived runtime specs for never-spent original cells; old specs persist."""
import pathlib,json,hashlib,copy,os,importlib.util
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');ID='OBSERVABILITY_CAP1M_WALL90_V1';REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,sort_keys=True,indent=2)+chr(10)).encode()
 if p.exists():assert p.read_bytes()==b,'immutable effective spec collision'
 else:
  with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def derive(original,candidate):
 s=copy.deepcopy(original);binary=candidate['framework_binary'];s.update(schema='DTC_AEV100_OBSERVATIONAL_EFFECTIVE_SPEC_V1',original_spec_sha256=sha(T/'control'/(original['cohort']+'_SPEC.json')),operational_runtime_profile=ID,binary_sha256=binary['sha256'],framework_commit=candidate['framework_commit'],source_worktrees=candidate['source_worktrees'])
 s['native_simulator_argv'][0]=binary['path'];replaced=0
 for r in s['runtime_files']:
  if r['target']=='DTC/bin/accel-sim.out':r.update(target=str(P(binary['path']).relative_to(T)),actual_realpath=str(P(binary['path']).resolve()),sha256=binary['sha256']);replaced+=1
 assert replaced==1
 allowed={'schema','original_spec_sha256','operational_runtime_profile','binary_sha256','framework_commit','source_worktrees','native_simulator_argv','runtime_files'}
 assert all(s[k]==v for k,v in original.items() if k not in allowed)
 assert s['native_simulator_argv'][1:]==original['native_simulator_argv'][1:] and s['configs']==original['configs'] and s['expected_options']==original['expected_options'] and s['expected']==original['expected']
 return s
def register_input(result,native):
 q=native.read_current_authority()[0]['registered_future_requests'][REQ];profile=native.registered_profile(q);candidate=read(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json');entries={}
 for cell in result['cells']:
  if cell in q['consumed']:
   if cell in q.get('effective_specs',{}):native.spec_for(cell)
   continue
  original=read(T/'control'/(cell+'_SPEC.json'));assert sha(T/'control'/(cell+'_SPEC.json'))==q['admitted_specs'][cell]
  derived=derive(original,candidate);dest=T/'control/effective_specs'/(cell+'.json');put(dest,derived);entries[cell]={'path':str(dest),'sha256':sha(dest),'original_spec_sha256':derived['original_spec_sha256'],'profile':ID}
 def amend(reg):
  actual=reg['registered_future_requests'][REQ];actual.setdefault('effective_specs',{})
  for cell,row in entries.items():
   assert cell not in actual['consumed'] and cell not in actual['sealed'] and actual['admitted_specs'][cell]==row['original_spec_sha256']
   if cell in actual['effective_specs']:assert actual['effective_specs'][cell]==row
   else:actual['effective_specs'][cell]=row
 if any(q.get('effective_specs',{}).get(c)!=v for c,v in entries.items()):native.update_authority(amend)
 return result
