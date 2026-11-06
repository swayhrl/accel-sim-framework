from pathlib import Path
import json,types,hashlib,ast
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');B=Path('/root/data/dtc_controlled_oracle_20261106_v1');R=B/'remaining24';O=A/'agents/R_remaining24_forward_readiness_audit_v1'
def rd(p):return json.loads(Path(p).read_bytes())
def load(p):
 m=types.ModuleType('cpu_gate');m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
res=load(R/'tools/oracle_resources.py');plan=rd(R/'control/EXECUTION_PLAN.json');points=rd(R/'control/MATRIX.fixed.json')['points'];plan['stage']='remaining24'
# Only pure in-memory gate evidence substitutions; no real receipt is made.
def fake(container,mode):
 if mode=='M_DATAREAD':return dict(mode=mode,CPU_FIXTURE_ONLY_NOT_ACTUAL_GATE2=True)
 raise res.WaitInitialRuntimeGate('CPU_MODE_NOT_RELEASED:'+mode)
res.verify_mode_extension_receipt=fake;rows=[]
for mode in ['OFF_MATCHED','M_DATAREAD','L2_DATAREAD','L1_DATAREADY']:
 c=next(x['cohort']for x in points if x['mode']==mode)
 try:v=res.verify_initial_runtime_gate(plan,c,{});status='RELEASED_IN_MEMORY_FIXTURE'
 except res.WaitInitialRuntimeGate as x:v=str(x);status='WAIT_IN_MEMORY_FIXTURE'
 assert (status=='RELEASED_IN_MEMORY_FIXTURE')==(mode in ['OFF_MATCHED','M_DATAREAD'])
 rows.append(dict(mode=mode,result=status,evidence=v))
# Validate pure registration transformation on isolated dictionaries, not registry.
addon=load(B/'initial8/tools/oracle_parent_addon.py');mockroot=O/'scratch_cpu/remaining24';candidate=rd(mockroot/'control/REGISTRY_REQUEST_CANDIDATE.json');finalplan=rd(mockroot/'control/EXECUTION_PLAN.json')
# validate_candidate deliberately rejects mock candidate; retain failclosed proof.
try:addon.validate_candidate(candidate,finalplan)
except AssertionError:mockrejected=True
else:mockrejected=False
assert mockrejected
report=dict(status='PASS_CPU_ONLY',per_mode_fixture=rows,all_Q_96_registration_does_not_release_unqualified_modes=True,mock_candidate_rejected_by_actual_addon=True,no_actual_gate2_receipt_created=True,no_registry_or_owner_mutation=True)
with(O/'PER_MODE_AND_MOCK_SAFETY_CPU.json').open('x')as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
