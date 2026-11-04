"""Bounded pure Host controls; no registry writes, model forks or CPU fixtures."""
from pathlib import Path
import json,hashlib,copy,importlib.util,sys
A=Path(__file__).resolve().parent;V=A.parent.parent;E=V/'agent_b_vector_modes';H=A/'runtime'
J=V.parent.parent;F=J/'execution_vector1700_decomposition_v3_20261104_v1/vector1700';T=A/'sandbox';T.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def mod(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
mc=mod('formal_mc_controls',H/'mode_contract.py');sys.path.insert(0,str(H));eng=mod('formal_engine_controls',H/'ep_perf_native_wv_modes_draft.py');rows=[]
def check(label,fn,reject=False,contains=None):
 try:fn();ok=not reject;err=None
 except Exception as e:err=type(e).__name__+': '+str(e);ok=reject and(contains is None or contains in err)
 rows.append(dict(label=label,PASS=ok,error=err,expected='REJECT'if reject else'PASS'))
for mode in ['W_ONLY','WV_ZERO_RO']:
 s=read(E/'specs'/(mode+'.json'));s.update(mode_contract_ref=ref(H/'mode_contract.py'),mode_cpu_review_ref=ref(A/'qualification/REVIEW_DRAFTS/MODE_CPU_REVIEW.json'),approved_launches=1,application_budget=1,scientific_scope_activated=True,Main_scientific_launch_authorization=ref(F/'control/USER_AUTHORIZATION.json'))
 check(mode+'_background',lambda:mc.check_background(s));check(mode+'_mode',lambda:eng.authorized_scope_mode(s))
 check(mode+'_authorized2',lambda:eng.enforce_stage_gates(s,dict(authorization_ref=ref(F/'control/USER_AUTHORIZATION.json')),{}))
 check(mode+'_draft_Main_blocks',lambda:mc.validate_static(s),True,'Main review missing')
 mutations=[
 ('oldSource78',lambda z:z['source_identity'].__setitem__('core_source_commit','78f4b59e865b136eede74df74c44c210f5b4ca04'),'Source5'),
 ('clock850',lambda z:z['expected_effective_options'].__setitem__('-gpgpu_clock_domains','1132.0:1132.0:1132.0:850.0'),'exact282'),
 ('B0off',lambda z:z['expected_effective_options'].__setitem__('-gpgpu_ep_l2_b0_stats','0'),'exact282'),
 ('ROon',lambda z:z['expected_effective_options'].__setitem__('-gpgpu_ep_l2_ro_line_mshr_bypass','1'),'exact282'),
 ('budget2',lambda z:z.__setitem__('application_budget',2),'one-start'),
 ('approved0',lambda z:z.__setitem__('approved_launches',0),'one-start')]
 for name,mut,why in mutations:
  z=copy.deepcopy(s);mut(z);check(mode+'_'+name,lambda z=z:mc.validate_static(z),True,why)
 for name,mut,why in [
 ('empty_CPU',lambda z:z.__setitem__('pairs',[]),'nonempty'),
 ('wrong_CPU_ELF',lambda z:z['Source5'].__setitem__('binary_sha256','0'*64),'CPU Source5'),
 ('missing111',lambda z:z.__setitem__('rows',[r for r in z['rows']if not(r['mode']==mode and r['observer']=='111')]),'000/111')]:
  c=read(s['mode_cpu_qualification_ref']['path']);mut(c);p=T/(mode+'_'+name+'.json');p.write_text(json.dumps(c)+'\n');z=copy.deepcopy(s);z['mode_cpu_qualification_ref']=ref(p);check(mode+'_'+name,lambda z=z:mc.validate_static(z),True,why)
 az=read(F/'control/USER_AUTHORIZATION.json');az['approved_launches']=3;p=T/(mode+'_wrongAuth.json');p.write_text(json.dumps(az)+'\n');z=copy.deepcopy(s);z['Main_scientific_launch_authorization']=ref(p);check(mode+'_wrongAuth',lambda:eng.enforce_stage_gates(z,dict(authorization_ref=ref(p)),{}),True,'two point')
out=dict(schema='EP_VECTOR1700_FORMAL_HOST_NEGATIVE_CONTROLS_V1',status='PASS'if all(r['PASS']for r in rows)else'PARTIAL',rows=rows,real_registry_writes=0,global_native_writes=0,models_started=0,Main_review_status='DRAFT_BLOCKED_AS_REQUIRED')
(A/'FORMAL_HOST_NEGATIVE_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],passed=sum(r['PASS']for r in rows),total=len(rows))));assert out['status']=='PASS'
