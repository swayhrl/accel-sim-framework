from pathlib import Path as P
import importlib.util,hashlib,json,tempfile,types,os,fcntl,ast,sys
B=P(__file__).parent
sp=importlib.util.spec_from_file_location('cpu_rebind',B/'zero_start_cpu_rebind.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.js(v))
def ck(n,v):assert v,n;checks.append(n)
class Fixture:
 def __init__(self):
  self.tmp=tempfile.TemporaryDirectory();self.r=P(self.tmp.name);self.c='E2-DTCL2MLP-CPU-ONLY-DH-P0-V1';self.sp=self.r/'control/specs'/(self.c+'.json');self.db=self.r/'control/dispatch_bindings'/(self.c+'.json');self.ip=self.r/'control/qualification_ledger'/(self.c+'.INTENT.json');self.ip.parent.mkdir(parents=True);self.s=dict(cohort=self.c,host_cpu=None,scientific_field='unchanged');put(self.sp,self.s);self.q=dict(consumed={},admitted_specs={self.c:sha(self.sp)});put(self.r/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}});self.old=dict(cohort=self.c,canonical_spec_sha256=sha(self.sp),host_cpu=137,resolved_spec_sha256=m.digest(m.js(dict(self.s,host_cpu=137))));put(self.db,self.old);self.original=self.db.read_bytes();self.claims={};self.legal=[448];self.calls=0
  self.e=types.SimpleNamespace(registered=lambda:(None,None,self.q,None),canonical=lambda c:dict(self.s),jsonsha=lambda s:m.digest(m.js(s)))
  # Exact frozen native spec_for body, not a rewritten imitation.
  source=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/tools/l2_native.py');tree=ast.parse(source.read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='spec_for');code=compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec');ns=dict(R=self.r,canonical=self.e.canonical,read=m.read,sha=sha,jsonsha=self.e.jsonsha);exec(code,ns);self.e.spec_for=ns['spec_for'];self.res=types.SimpleNamespace(cpu_candidates=lambda *a:self.legal)
 def run(self):return m.maybe_rebind(self.r,self.e,self.res,dict(cohort=self.c,host_cpu=448),{},self.claims)
f=Fixture();out=f.run();events=[json.loads(x)for x in(f.r/'control/operational_amendments/zero_start_cpu_rebind_v1/AMENDMENTS.jsonl').read_text().splitlines()];pre=P(events[-1]['preimage_path']);ck('positive_native_spec_for_original_body_preimage_journal_and_canonical_unchanged',out is not None and f.e.spec_for(f.c)['host_cpu']==448 and pre.read_bytes()==f.original and sha(f.sp)==f.old['canonical_spec_sha256']and [x['stage']for x in events]==['PREPARED','COMMITTED']and {k:v for k,v in m.read(f.db).items()if k not in['host_cpu','resolved_spec_sha256']}=={k:v for k,v in f.old.items()if k not in['host_cpu','resolved_spec_sha256']})
f=Fixture();f.legal=[137,448];ck('old_cpu_still_legal_unchanged',f.run()is not None and f.db.read_bytes()==f.original)
f=Fixture();f.q['consumed'][f.c]={};ck('spent_never_rebound',f.run()is None and f.db.read_bytes()==f.original)
f=Fixture();f.claims[f.c]={};a=f.run()is None;f.claims={};put(f.r/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{f.c:{}}});ck('inmemory_and_persisted_claims_never_rebound',a and f.run()is None and f.db.read_bytes()==f.original)
f=Fixture();put(f.ip,{});ck('intent_never_rebound',f.run()is None and f.db.read_bytes()==f.original)
f=Fixture()
with(f.ip.parent/(f.c+'.ATTEMPT.lock')).open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);ck('native_attempt_lock_nonblocking_refusal',f.run()is None and f.db.read_bytes()==f.original)
f=Fixture();bad=dict(f.old,resolved_spec_sha256='bad');put(f.db,bad);before=f.db.read_bytes();ck('bad_canonical_or_resolved_identity_rejected',f.run()is None and f.db.read_bytes()==before)
f=Fixture();original=f.e.registered
# Simulates a registry/native consumer winning between preimage and replace.
def changing():
 f.calls+=1
 if f.calls>=2:f.q['consumed'][f.c]={}
 return original()
f.e.registered=changing;ck('recheck_catches_consume_race_before_replace',f.run()is None and f.db.read_bytes()==f.original)
f=Fixture();original=lambda *a:dict(cohort=f.c,host_cpu=448);f.res.choose_dispatch=original;claims={};frame=types.SimpleNamespace(f_locals=dict(res=f.res,engine=f.e,pool=object(),claims=claims));proof=m.install_on_frame(frame,f.r);selected=f.res.choose_dispatch([],{},claims,{});restored=m.restore_in_owner();ck('owner_instance_wrapper_restore_preserves_original_pool_and_claims',selected is not None and f.res.choose_dispatch is original and proof['claims_object_id']==id(claims)and restored['bindings_not_rolled_back'])
qa=dict(status='PASS',schema='ZERO_START_CPU_REBIND_CPU_QUALIFICATION_V1',checks=checks,total_checks=len(checks),source_sha256=sha(B/'zero_start_cpu_rebind.py'),driver_sha256=sha(__file__),actual_frozen_native_spec_for_source_sha256=sha('/root/data/dtc_l2_mlp_exploration_20261027_v1/tools/l2_native.py'),production_mutations=0,production_parent_attached=False,model_starts=0,model_signals=0)
put(B/'CPU_QUALIFICATION.json',qa);print(json.dumps(qa))
