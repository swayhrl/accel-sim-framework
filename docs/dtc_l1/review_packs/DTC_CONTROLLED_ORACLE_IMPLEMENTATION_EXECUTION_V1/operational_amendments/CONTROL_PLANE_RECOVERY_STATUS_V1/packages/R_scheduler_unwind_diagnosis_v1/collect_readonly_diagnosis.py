from pathlib import Path
import json,hashlib,ast
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');B=Path('/root/data/dtc_controlled_oracle_20261106_v1');R=B/'initial8';O=A/'agents/R_scheduler_unwind_diagnosis_v1';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_bytes())
exception=B/'control/owner_unwind_exception_readonly_v1/EXCEPTION_AND_LOCALS.fixed.json';flow=B/'control/owner_live_flow_readonly_diagnostic_v1/ACTUAL_OWNER_FLOW.fixed.json';v=rd(exception)
assert any('oracle_ops.py\\", line 175' in json.dumps(x)or 'line 175' in x['exception']for x in v['exceptions'])
registry=rd(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json'));q=registry['registered_future_requests']['DTC_ORACLE_INITIAL8_20261106_V1'];pending=[]
for p in sorted((R/'control/specs').glob('*.json')):
 s=rd(p);c=s['cohort']
 if c in q['consumed']:continue
 b=R/'control/dispatch_bindings'/(c+'.json');value=rd(b)if b.exists()else None
 resolved=hashlib.sha256((json.dumps(dict(s,host_cpu=value['host_cpu']),sort_keys=True,indent=2)+'\n').encode()).hexdigest()if value else None
 pending.append(dict(cohort=c,program=s['program'],canonical_sha256=sha(p),binding_path=str(b),binding_sha256=sha(b)if value else None,binding=value,canonical_match=value is None or value['canonical_spec_sha256']==sha(p),resolved_match=value is None or value['resolved_spec_sha256']==resolved,INTENT_exists=(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()))
assert all(x['canonical_match']and x['resolved_match']and not x['INTENT_exists']for x in pending)
report=dict(schema='DTC_ORACLE_SCHEDULER_UNWIND_ROOT_CAUSE_READONLY_V1',status='EXACT_EXCEPTION_IDENTIFIED_NO_MUTATION',cause='EXPECTED_RESOURCE_HOLD_NOT_CAUGHT_IN_DISPATCH_LOOP',actual_exception_ref=dict(path=str(exception),sha256=sha(exception)),actual_flow_ref=dict(path=str(flow),sha256=sha(flow)),source=dict(path=str(R/'tools/oracle_ops.py'),sha256=sha(R/'tools/oracle_ops.py'),uncaught_sites=[175,185],context_manager_unwind_line=108),triggering_cohort=v['scheduler_locals'][0]['c'],failure='RESOURCE_HOLD_PEER_RESERVATION -> REGISTRY_CHANGED_DURING_ADMISSION_PAUSE_NEW',dispatch_binding_assertion_ruled_out=True,pending_unused=pending,mechanism='Exception crosses ThreadPoolExecutor context-manager; review/archive pools shut down, model pool shutdown(wait=True) waits healthy model futures before outer OWNER_THREAD_ERROR writer runs.',minimal_engineering_direction=['Catch only typed expected RESOURCE_HOLD at preclaim resource call: record defer/cooldown, do not consume or change frozen binding.','At postclaim typed resource HOLD: remove never-submitted claim, sync reservation and defer without UUID/model.','Preserve non-resource/schema/identity exceptions as fail-closed engineering events.','Already unwinding old scheduler cannot simply resume. Any same-owner transfer must independently prove no competing admission loop, continuous lease/flock, unchanged healthy futures/UUIDs and exactly one archive worker; no shutdown-flag reset or model retry.'],owner_registry_source_identity_writes=0,model_starts=0,healthy_model_signals=0)
with(O/'ROOT_CAUSE_READONLY.json').open('x')as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
