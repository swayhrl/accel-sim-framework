"""Finite private resource-scope wiring. No Main authority, mutation or actors."""
from pathlib import Path
import hashlib,json,importlib.util
HERE=Path(__file__).resolve().parent
V5=HERE.parent.parent
DROOT=HERE.parent
BASE_REF={'path':str(DROOT/'resources_a2_v5.py'),'sha256':'68eceb9b98cc0b82303a5534633101d1111c5aebb4d18743b188fc5395619042'}
REQUEST_A='EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1'
REQUEST_B='EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1'
REQUEST_D='EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1'
EXACT_ROOTS={REQUEST_A:V5/'track_a_wv/host_private_candidate_v1/execution',REQUEST_B:V5/'track_b_fullf/host_private_candidate_v1/execution',REQUEST_D:DROOT/'three_mm/execution'}
ROOT_BINDINGS=HERE/'ROOT_BINDINGS_V1.json'
ROOT_BINDINGS_SHA='e9b88bf134c1af1d06d8a2a28078a6c13fc7f50ff8df2a824a20d9058570c3a0'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def checked_roots(binding_ref=None):
 r=binding_ref or dict(path=str(ROOT_BINDINGS),sha256=ROOT_BINDINGS_SHA)
 need(type(r)is dict and type(r.get('path'))is str and len(r.get('sha256',''))==64,'invalid explicit scope reference')
 need(sha(r['path'])==r['sha256'],'resource scope binding drift')
 q=read(r['path']);need(q.get('schema')=='EP_V5_EXACT_PRIVATE_RESOURCE_ROOT_BINDINGS_V1' and q.get('scientific_permission')is False,'resource binding is not science authority')
 roots=q['request_roots'];need(set(roots)==set(EXACT_ROOTS),'scope set changed')
 out={}
 for request,root in roots.items():
  p=Path(root);need(p.is_absolute() and str(p)==str(p.resolve()),'scope ROOT must be exact resolved absolute path')
  if request==REQUEST_A:
   base=V5/'track_a_wv/host_private_candidate_v1'
   need(p==EXACT_ROOTS[request] or p.is_relative_to(base/'main_materialized') and p.name=='execution','outside owned A materialized execution ROOT')
  else:need(p==EXACT_ROOTS[request],'unexpected exact B/3MM ROOT')
  need(p.is_dir(),'execution ROOT not present');out[request]=p
 return out,r
class ScopeAdapter:
 def __init__(self,request,binding_ref=None):
  need(request in EXACT_ROOTS,'unknown exact V5 request')
  self.request=request;self.roots,self.binding_ref=checked_roots(binding_ref)
 def _impl(self):
  current,ref=checked_roots(self.binding_ref);need(current==self.roots and ref==self.binding_ref,'mutable resource scope binding changed')
  need(sha(BASE_REF['path'])==BASE_REF['sha256'],'verified D resource source drift')
  sp=importlib.util.spec_from_file_location('v5_private_scope_'+self.request,BASE_REF['path']);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  # Only this isolated module object's exact request/root and SCOPES are rebound.
  m.REQUEST=self.request;m.ROOT=self.roots[self.request]
  prior=m.shared
  roots=dict(self.roots)
  def shared():
   b=prior()
   for request,root in roots.items():
    if request in b.SCOPES:need(b.SCOPES[request]==root,'resource scope collision')
    b.SCOPES[request]=root
   return b
  m.shared=shared;return m
 def snapshot(self):
  s=self._impl().snapshot();need(s['current_request']==self.request,'cross-request snapshot')
  s['V5_Main_exact_scope_binding_ref']=self.binding_ref
  s['V5_private_resource_root_bindings']={k:str(v)for k,v in self.roots.items()}
  s['resource_admission_is_not_science_permission']=True
  return s
 def admit(self,s,additional,writes,policy=None):
  need(s.get('current_request')==self.request,'cross-request resource admission')
  need(s.get('V5_Main_exact_scope_binding_ref')==self.binding_ref,'snapshot scope binding mismatch')
  need(s.get('current_scope_registered')is True,'V5_EXACT_SCOPE_NOT_REGISTERED')
  return self._impl().admit(s,additional,writes,policy)
 def forecast(self,*a,**k):return self._impl().forecast(*a,**k)
def for_scope(request,binding_ref=None):return ScopeAdapter(request,binding_ref)
