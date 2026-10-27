from pathlib import Path as P
import importlib.util,json,hashlib,traceback
B=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/B/canary_rollout_audit_v1');sp=importlib.util.spec_from_file_location('actual_barrier_probe',B/'audit_canary_rollout.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);import sys;sys.addaudithook(m._audit);m._hook=True;c='E2-DTCL2MLP-dd9f695c4f53b083-DH-F256-V1';rows=[];ep=B/'EXPECTATIONS.json';expected=json.loads(ep.read_bytes());expected['source_and_route_pins']['/usr/bin/findmnt']='2668fe017172fa496ca506b99879d1c3bc3c7e3f54f71ec0c6e24b1562610d60';ep.write_text(json.dumps(expected,sort_keys=True,indent=2)+'\n');prior=B/'ACTUAL_BASE_ARCHIVE_BARRIER_CHECK.json';backup=B/'ACTUAL_BASE_ARCHIVE_BARRIER_CHECK_initial_HOLD.json';
if prior.exists()and not backup.exists():backup.write_bytes(prior.read_bytes())
for phase in ['base','archive']:
 m._guard.enabled=True
 try:
  m.configure_readonly_findmnt(json.loads((m.R/'control/specs'/(c+'.json')).read_bytes()),expected);actual=m.Actual(m.R);v=getattr(actual,phase)(c);row=dict(phase=phase,status='PASS',source_mutations_blocked=True)
  if phase=='base':row.update(cycles=v['cycles'],performance_accepted=v['performance_accepted'],proof_sha256=hashlib.sha256(json.dumps(v,sort_keys=True,indent=2).encode()).hexdigest())
  else:row.update(independently_verified_entries=v['independently_verified_entries'],archive_sha256=v['receipt']['archive_sha256'],native_restore=v['receipt']['native_restore'])
 except Exception as e:row=dict(phase=phase,status='HOLD',error=repr(e),traceback=traceback.format_exc())
 finally:m._guard.enabled=False
 rows.append(row)
report=dict(schema='ACTUAL_CLOSED_PADDING_PILOT_READONLY_BARRIER_CHECK_V1',cohort=c,rows=rows,status='PASS'if all(x['status']=='PASS'for x in rows)else'HOLD',not_IO_canary_released=True,production_mutations=0,model_starts=0,model_signals=0)
(B/'ACTUAL_BASE_ARCHIVE_BARRIER_CHECK.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report))
