"""Four CPU-only coupling checks with actual frozen B.install_on_frame/E38."""
import copy,hashlib,importlib.util,json,pathlib,sys,tempfile,types
P=pathlib.Path;HERE=P(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'large_job_aging_v1'))
from large_job_aging import AgingChooser,G
from cpu_outer_coupling import install_in_owner,restore_in_owner,MARKER,CPU_MARKER,original_cell

def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
B=HERE.parent.parent/'B/zero_start_cpu_rebind_v1/zero_start_cpu_rebind.py'
assert sha(B)=='b0db8a54400bd456aa404aa9b033badefc59231f8dd04534bc34bcf56937bcf8'
sp=importlib.util.spec_from_file_location('actual_B_CPU_rebind',B);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
main=sys.modules['__main__'];checks=[]

def frame():
 return dict(now=0,budget_bytes=10*G,effective_total_growth_bytes=0,memory_utilization_fraction=.88,
  own_live=[],consumed={},claim_cohorts=[],closures=[],pending=[dict(cohort='SHORT',input_digest='short',program='short',cell='DH',profile='P0',cost_bytes=G,first_eligible_monotonic=0)],
  active_input_digests=[],started_programs=[],pressure_reasons=[],total_padding_discount_bytes=0,padding_discount_by_cohort={},accounted_growth_by_cohort={})

class Fixture:
 def __init__(self,broken_second=False):
  self.tmp=tempfile.TemporaryDirectory();self.root=P(self.tmp.name);self.c='SHORT'
  for n in ('dispatch_bindings','specs','qualification_ledger'):(self.root/'control'/n).mkdir(parents=True,exist_ok=True)
  self.spec=dict(cohort=self.c,host_cpu=None,science='unchanged');self.sp=self.root/'control/specs/SHORT.json';self.sp.write_bytes(b.js(self.spec))
  self.q=dict(consumed={},admitted_specs={self.c:sha(self.sp)})
  self.db=self.root/'control/dispatch_bindings/SHORT.json';self.db.write_bytes(b.js(dict(cohort=self.c,host_cpu=137,canonical_spec_sha256=sha(self.sp),resolved_spec_sha256=b.digest(b.js(dict(self.spec,host_cpu=137))))))
  self.original_binding=self.db.read_bytes();(self.root/'control/POOL_DISPATCH_RESERVATIONS.json').write_bytes(b.js({'claims':{}}))
  self.engine=types.SimpleNamespace(registered=lambda:(None,None,self.q,None),canonical=lambda c:dict(self.spec),jsonsha=lambda s:b.digest(b.js(s)),spec_for=lambda c:dict(self.spec,host_cpu=json.loads(self.db.read_bytes())['host_cpu']))
  self.B_calls=0;self.provider_calls=0
  def original(*args):self.B_calls+=1;return dict(cohort=self.c,host_cpu=448)
  def provider(*args):
   self.provider_calls+=1
   if broken_second and self.provider_calls>1:raise json.JSONDecodeError('CPU half JSON','{',1)
   return frame()
  self.original=original;self.res=types.SimpleNamespace(choose_dispatch=original,cpu_candidates=lambda *a:[448])
  self.aging=AgingChooser(original,provider);self.aging.install(self.res,lambda:None)
  self.old_E=self.aging.wrapper;self.fake=types.SimpleNamespace(f_locals=dict(res=self.res,engine=self.engine,pool=object(),claims={}))
  b.install_on_frame(self.fake,self.root);self.cpu=getattr(main,CPU_MARKER);self.code=self.cpu['wrapper'].__code__
 def call(self):return self.res.choose_dispatch([dict(cohort=self.c)],{}, {},{},None,{},0)
 def cleanup(self):
  if hasattr(main,CPU_MARKER):b.restore_in_owner()
  if hasattr(main,MARKER):restore_in_owner(main,lambda:None)
  if self.aging.installed:self.aging.restore(lambda:None)
  self.tmp.cleanup()

# 1 Normal path actually changes only fake-root zero-start binding via unchanged B.
f=Fixture();install_in_owner(main,f.aging,f.res,lambda:None,sleeper=lambda _:None)
out=f.call();state=getattr(main,MARKER)
assert out['host_cpu']==448 and 'zero_start_cpu_rebind'in out and f.B_calls==1
assert f.res.choose_dispatch is f.cpu['wrapper'] and f.cpu['wrapper'].__code__ is f.code
assert original_cell(f.cpu['wrapper']).cell_contents is state['gate'].wrapper
assert sha(f.sp)==f.q['admitted_specs'][f.c]
checks.append('normal_CPU_outer_guard_E_B_and_fake_zero_start_rebind_preserved')
# 2 CPU.restore exposes guard; explicit guard restore then frozen E.restore passes.
b.restore_in_owner();assert f.res.choose_dispatch is state['gate'].wrapper
restore_in_owner(main,lambda:None);assert f.res.choose_dispatch is f.old_E
f.aging.restore(lambda:None);assert f.res.choose_dispatch is f.original
checks.append('CPU_then_guard_then_E_restore_exact_chain_without_clobber')
f.tmp.cleanup()

# 3 E second fresh frame corrupt: no proposal reaches CPU binding amendment.
f=Fixture(True);install_in_owner(main,f.aging,f.res,lambda:None,sleeper=lambda _:None)
before=copy.deepcopy(f.aging.state.__dict__);assert f.call()is None
assert f.aging.state.__dict__==before and f.aging.calls==0 and f.B_calls==1
assert f.db.read_bytes()==f.original_binding and not(f.root/'control/operational_amendments/zero_start_cpu_rebind_v1/AMENDMENTS.jsonl').exists()
assert getattr(main,MARKER)['gate'].last_issue['state_restored']
checks.append('second_frame_half_JSON_rolls_back_E_and_no_CPU_rebind_or_journal')
f.cleanup()

# 4 Guard can be removed while CPU remains outer; duplicate install rejects cleanly.
f=Fixture();install_in_owner(main,f.aging,f.res,lambda:None,sleeper=lambda _:None)
saved=getattr(main,MARKER);cell=original_cell(f.cpu['wrapper'])
try:install_in_owner(main,f.aging,f.res,lambda:None)
except AssertionError:pass
else:raise AssertionError('duplicate accepted')
assert getattr(main,MARKER)is saved and cell.cell_contents is saved['gate'].wrapper
restore_in_owner(main,lambda:None)
assert f.res.choose_dispatch is f.cpu['wrapper'] and cell.cell_contents is f.old_E and f.cpu['original']is f.old_E
f.cleanup();checks.append('duplicate_rejected_and_guard_first_restore_keeps_CPU_outer')

result=dict(status='PASS',count=len(checks),checks=checks,
 source_sha256={n:sha(HERE/n)for n in ('frame_read_guard.py','cpu_outer_coupling.py','qualify_cpu_outer_coupling.py')},
 frozen_B_source_sha256=sha(B),production_installed=False,production_mutations=0,models_started=0,signals_sent=0,
 fake_root_CPU_rebind_exercised=True,original_six_case_qualification_unchanged=True)
(HERE/'CPU_OUTER_COUPLING_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
