import pathlib,importlib.util,json,types,hashlib
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/finite8_archive_current_gate_v1';s=importlib.util.spec_from_file_location('finite8_current_gate_cpu',D/'dtc_archive_operator.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
for scope in['current original8','other namespace unchanged']:
 base=types.SimpleNamespace(ROOT='ORIGINAL',NAS='NAS',COHORTS={'C':'DTC'},gate=lambda:False);old=lambda path,name:base;truthful=lambda *x,**y:dict(PASS=True);loader=m.adapted_loader(old,truthful);path=m.T/'tools/sweep_outbox.py'if scope=='current original8'else P('/other/tool.py');got=loader(path,'CPU');assert got is base and got.ROOT=='ORIGINAL'and got.NAS=='NAS'and got.COHORTS=={'C':'DTC'}and(got.gate is truthful)==(scope=='current original8');checks.append(scope)
base=types.SimpleNamespace(ROOT='A',NAS='B',COHORTS={'C':'DTC'},gate=lambda:False)
def hold(*x,**y):raise RuntimeError('RESOURCE_HOLD')
m.install(base,hold)
try:base.gate(123)
except RuntimeError:checks.append('truthful resource HOLD propagated')
else:raise AssertionError('HOLD bypassed')
calls=[]
def gate(*args,**kwargs):calls.append((args,kwargs));return dict(native_floor=5*1024**3)
m.install(base,gate);assert base.gate(123,other_reservation=None)==dict(native_floor=5*1024**3)and calls==[((123,),{'other_reservation':None})];checks.append('exact reserve args and new gate result preserved')
actual,sample=m.actual_gate();assert sample['physical_disk_pass']and sample['host_MemAvailable_bytes']>=64*1024**3 and sample['native_free_bytes']>sample['required_free_bytes']and sample['copy_overlay_sha256']==m.GATE_SHA;checks.append('actual read-only published R19 gate passes with current known writes and genuine164')
q=dict(status='PASS',operator_sha256=m.sha(D/'dtc_archive_operator.py'),driver_sha256=m.sha(__file__),checks=checks,check_count=len(checks),real_COPY_calls=0,scientific_starts=0,actual_read_only_resource_sample=sample,finite8_frozen_review_qualification=m.sha(F/'ops/EIGHT_ORIGINAL_EXPECTED_GROWTH_REVIEW_CPU_QUALIFICATION_V1.json'))
with(D/'CPU_QUALIFICATION.json').open('x')as f:json.dump(q,f,indent=2);f.write('\n')
print(json.dumps(dict(status='PASS',checks=len(checks),operator_sha256=q['operator_sha256'],qualification_sha256=m.sha(D/'CPU_QUALIFICATION.json'))))
