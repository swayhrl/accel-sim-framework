"""Exact closed consumer count+signed metadata fix. Original Spec/raw/consumer stay intact."""
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
def ref(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def load(p,label):
 sp=importlib.util.spec_from_file_location(label,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def patched_scan(c,proof):
 text=Path(PLAN['old_frozen_source_ref']['path']).read_text();need(sha(c.__file__)==PLAN['old_frozen_source_ref']['sha256'],'original frozenC pin')
 node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='scan');before=ast.get_source_segment(text,node)
 need(hashlib.sha256(before.encode()).hexdigest()==PLAN['old_scan_sha256'],'original scan identity')
 after=before.replace('len(options)==282','len(options)==283').replace("'all282 actual options mismatch'","'all283 actual options mismatch'")
 old_expr="identity[field].startswith(t)";need(after.count(old_expr)==1,'nonexact banner predicate')
 after=after.replace(old_expr,'_Main_exact_closed_banner_token(key,t,identity)')
 a,b=ast.parse(before),ast.parse(after);changes=[]
 class Normalize(ast.NodeTransformer):
  def visit_Call(self,n):
   if isinstance(n.func,ast.Name)and n.func.id=='_Main_exact_closed_banner_token':
    return ast.parse(old_expr,mode='eval').body
   return self.generic_visit(n)
 b=Normalize().visit(b)
 for x,y in zip(ast.walk(a),ast.walk(b)):
  if isinstance(x,ast.Constant)and isinstance(y,ast.Constant)and x.value!=y.value:changes.append([x.value,y.value]);y.value=x.value
 need(ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)and len(changes)==2,'unreviewed scan logic changed')
 def token(kind,t,identity):
  need(identity==proof['canonical_Source5'],'no Source relabel')
  return t in (proof['actual_core_tokens']if kind=='core'else proof['actual_framework_tokens'])
 c.__dict__['_Main_exact_closed_banner_token']=token
 exec(compile(after,str(HERE/'closed_consumer_283_banner_v2.py')+'::Main_signed_exact_closed_scan','exec'),c.__dict__)
 return c
def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha,approval_ref=None):
 s=json.loads(Path(spec).read_bytes())if isinstance(spec,(str,Path))else dict(spec)
 need(s['source_identity']==PLAN['Source5']and s.get('source_feature_profile')in PLAN['allowed_profiles']and len(s['expected_effective_options'])==283,'outside exact closed Source283')
 if approval_ref is None:
  p=HERE/'MAIN_EXACT_BANNER_COMPATIBILITY_APPROVAL_REF.json';need(p.exists(),'Main exact closed consumer approval absent');approval_ref=json.loads(p.read_bytes())
 helper=load(HERE/'exact_banner_compatibility.py','A_exact_Main_banner_verifier')
 proof=helper.check(s,raw,approval_ref,ref(__file__))
 count=load(HERE/'closed_consumer_283.py','A_original_count_contract_helpers');schema=count.full43(s)
 base=count.load_ref(PLAN['old_adapter_ref'],'A_original_closed_adapter');configured=base.configured_base
 def configured_base():
  b,mc=configured();factory=b.frozen_c
  b.frozen_c=lambda:patched_scan(factory(),proof)
  return b,mc
 base.configured_base=configured_base
 result=base.validate_case(raw,s,qualification,sourceq_path,sourceq_sha)
 need(result['math_binding']['numeric_body_sha256']=='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817'and result['math_binding']['frozen_final_suffix_sha256']=='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432','unchanged numeric body/final suffix')
 need(result['scientific_acceptance_granted']is False,'pure closed consumer cannot grant acceptance')
 result['closed_consumer_amendment']=dict(schema='EP_PFV5_A_EXACT283_BANNER_SIGNED_CLOSED_CONSUMER_PROOF_V2',new_consumer_ref=ref(__file__),old_adapter_ref=PLAN['old_adapter_ref'],strict43=schema,full_283_actual_map_retained=True,actual_options_count=len(result['application']['actual_options']),banner_metadata_compatibility=proof,original_Spec_raw_oldHOLD_unchanged=True,model_starts=0,official_outer_join_and_archive_still_required=True,scientific_permission=False)
 return result
