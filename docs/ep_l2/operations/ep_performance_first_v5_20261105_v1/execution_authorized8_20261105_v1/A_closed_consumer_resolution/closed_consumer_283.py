"""Read-only closed-result consumer amendment candidate; no state/start/write APIs."""
from pathlib import Path
import ast,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'EXACT_CAUSE_AND_AST_DELTA.json').read_bytes())
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def doc(v):return json.loads(Path(v).read_bytes())if isinstance(v,(str,Path))else dict(v)
def exact(r):need(sha(r['path'])==r['sha256'],'immutable closed consumer dependency drift');return doc(r['path'])
def load_ref(r,label):
 need(sha(r['path'])==r['sha256'],'closed consumer module drift')
 sp=importlib.util.spec_from_file_location(label,r['path']);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def compile_exact_scan(c):
 r=PLAN['old_frozen_source_ref'];need(str(Path(c.__file__).resolve())==str(Path(r['path']).resolve())and sha(r['path'])==r['sha256'],'unexpected frozen-C Source')
 text=Path(r['path']).read_text();node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='scan');before=ast.get_source_segment(text,node)
 need(hashlib.sha256(before.encode()).hexdigest()==PLAN['old_scan_sha256'],'original scan identity')
 need(before.count('len(options)==282')==1 and before.count("'all282 actual options mismatch'")==1,'nonexact option gate')
 after=before.replace('len(options)==282','len(options)==283').replace("'all282 actual options mismatch'","'all283 actual options mismatch'")
 need(hashlib.sha256(after.encode()).hexdigest()==PLAN['new_scan_sha256'],'repaired scan identity')
 a,b=ast.parse(before),ast.parse(after);changes=[]
 for x,y in zip(ast.walk(a),ast.walk(b)):
  if isinstance(x,ast.Constant)and isinstance(y,ast.Constant)and x.value!=y.value:changes.append([x.value,y.value]);y.value=x.value
 need(ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)and len(changes)==2 and [282,283]in changes and ['all282 actual options mismatch','all283 actual options mismatch']in changes,'scan delta exceeds count+message')
 exec(compile(after,r['path']+'::EXACT283_COUNT_AMENDMENT','exec'),c.__dict__)
 return c
def full43(s):
 r=s['host_engine_ref'];need(sha(r['path'])==r['sha256'],'original sealed Host engine drift')
 tree=ast.parse(Path(r['path']).read_text());values={}
 for n in tree.body:
  if isinstance(n,ast.Assign):
   for target in n.targets:
    if isinstance(target,ast.Name)and target.id in ['_SCHEMA_MODULE','_SCHEMA_REFS']:values[target.id]=ast.literal_eval(n.value)
 need(set(values)=={'_SCHEMA_MODULE','_SCHEMA_REFS'},'original strict43 refs absent')
 m=load_ref(values['_SCHEMA_MODULE'],'A_closed_original_strict43')
 return m.validate_spec_contract(s,**values['_SCHEMA_REFS'],require_bound_cpu=False,check_current_domain=True,check_current_dependencies=True)
def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 s=doc(spec);q=doc(qualification)
 need(s['source_identity']==PLAN['Source5']and s.get('source_feature_profile')in PLAN['allowed_profiles'],'outside exact closed Source283 profiles')
 need(len(s['expected_effective_options'])==283,'sealed Spec is not exact283')
 need(s['validation_module_ref']==PLAN['old_adapter_ref'],'sealed original consumer changed')
 schema=full43(s)
 base=load_ref(PLAN['old_adapter_ref'],'A_closed_original_adapter')
 configured=base.configured_base
 def patched_configured():
  b,mc=configured();factory=b.frozen_c
  def patched_factory():return compile_exact_scan(factory())
  b.frozen_c=patched_factory
  return b,mc
 base.configured_base=patched_configured
 result=base.validate_case(raw,s,q,sourceq_path,sourceq_sha)
 need(result['math_binding']['numeric_body_sha256']=='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817','original numeric body drift')
 need(result['math_binding']['frozen_final_suffix_sha256']=='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432','original final suffix drift')
 need(result['scientific_acceptance_granted']is False,'consumer cannot grant acceptance')
 result['closed_consumer_count_amendment']=dict(schema='EP_PFV5_A_EXACT283_CLOSED_CONSUMER_PROOF_V1',entry_ref=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),cause_ref=dict(path=str(HERE/'EXACT_CAUSE_AND_AST_DELTA.json'),sha256=sha(HERE/'EXACT_CAUSE_AND_AST_DELTA.json')),original_adapter_ref=PLAN['old_adapter_ref'],frozen_source_ref=PLAN['old_frozen_source_ref'],old_scan_sha256=PLAN['old_scan_sha256'],new_scan_sha256=PLAN['new_scan_sha256'],AST_only_changes=PLAN['AST_only_changes'],strict43_and_dependencies=schema,actual_options_count=len(result['application']['actual_options']),Source5=s['source_identity'],original_Spec_raw_HOLD_preserved=True,science_permission=False,new_model_starts=0)
 return result
