from pathlib import Path as P
import importlib.util,json,hashlib,traceback,sys,datetime
B=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/B/future_memory_canary_rollout_audit_v1');sp=importlib.util.spec_from_file_location('actual_memory_auditor_barrier_probe',B/'audit_future_memory_canary.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);sys.addaudithook(m._audit);m._hook=True;expected=json.loads((B/'actual_expectations/ACTUAL_EXPECTATIONS_V1.json').read_bytes());c='E2-DTCL2MLP-dd9f695c4f53b083-DH-F256-V1';rows=[]
for phase in ['base','archive']:
 m._guard.enabled=True
 try:
  m.configure_readonly_findmnt(json.loads((m.R/'control/specs'/(c+'.json')).read_bytes()),expected);actual=m.Actual(m.R);v=getattr(actual,phase)(c);row=dict(phase=phase,status='PASS',writebarrier_enabled=True)
  if phase=='base':row.update(cycles=v['cycles'],performance_accepted=v['performance_accepted'])
  else:row.update(independently_verified_entries=v['independently_verified_entries'],archive_sha256=v['receipt']['archive_sha256'],native_restore=v['receipt']['native_restore'])
 except Exception as e:row=dict(phase=phase,status='HOLD',error=repr(e),traceback=traceback.format_exc())
 finally:m._guard.enabled=False;m._guard.findmnt=None
 rows.append(row)
report=dict(schema='FUTURE_MEMORY_AUDITOR_ACTUAL_READONLY_BASE_ARCHIVE_COMPATIBILITY_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),cohort=c,status='PASS'if all(x['status']=='PASS'for x in rows)else'HOLD',rows=rows,new_memory_canary_not_passed_by_this_check=True,production_mutations=0,model_starts=0,signals=0,source_sha256=hashlib.sha256((B/'audit_future_memory_canary.py').read_bytes()).hexdigest());(B/'ACTUAL_BASE_ARCHIVE_BARRIER_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
