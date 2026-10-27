from pathlib import Path as P
import json,hashlib,tempfile,types,copy,importlib.util,os
B=P(__file__).parent;sp=importlib.util.spec_from_file_location('rollout_cpu',B/'audit_canary_rollout.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(js(v))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):assert v,n;checks.append(n)
with tempfile.TemporaryDirectory()as td:
 r=P(td);c='CPU_CANARY';u='CPU_UUID';out=r/'DTC/run/results'/u;out.mkdir(parents=True);ip=r/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');sp=r/'control/specs'/(c+'.json');rp=r/'analysis'/(c+'.RESULT.json');ap=r/'control'/(c+'_ARCHIVE_RECEIPT.json');pin=r/'source.pin';pin.write_text('pinned');restore=r/'native_restore';restore.mkdir();put(sp,{'input':'CPU_ONLY'});put(ip,dict(uuid=u,output=str(out)));done=dict(uuid=u,stop_reason=None,launcher_wait_returncode=0,native_simulator_observed=True,new_attempt_consumed=1);put(dp,done);put(out/'NATIVE_EXIT.json',done);base=dict(performance_accepted=True,cycles=7,original_detail='must compare entire dict');put(out/'PADDING_EXTRA_STRICT.json',{'status':'PASS_PADDING_ADMISSION_AND_ORIGINAL_STRICT'});pad=dict(status='PASS_PADDING_ADMISSION_AND_ORIGINAL_STRICT',sidecar_sha256=sha(out/'PADDING_EXTRA_STRICT.json'));put(out/'SHARED_JSON_IO_EXTRA_STRICT.json',{'status':'PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT'});io=dict(status='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT',sidecar_sha256=sha(out/'SHARED_JSON_IO_EXTRA_STRICT.json'));proof=dict(base,additional_padding_admission_strict=pad,additional_shared_json_io_strict=io);receipt=dict(status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',native_restore=str(restore));archive=dict(receipt=receipt,independently_verified_entries=12);result=dict(state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE',uuid=u,cohort=c,cycles=7,proof=proof,archive=archive);put(rp,result);put(ap,receipt);put(out/'L2_STRICT.json',proof)
 for name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','PADDING_ADMISSION_EVIDENCE.json']:put(out/name,{})
 put(out/'PADDING_ACTIVATION_CONFIG.json',{});put(out/'SHARED_JSON_IO_SNAPSHOT.json',{'config':{}})
 q=dict(consumed={c:dict(uuid=u,intent_sha256=sha(ip),execution_receipt=done)},admitted_specs={c:sha(sp)});expected=dict(uuid=u,canonical_spec_sha256=sha(sp),source_and_route_pins={str(pin):sha(pin)});ops=types.SimpleNamespace(registry=lambda:copy.deepcopy(q),base=lambda c:copy.deepcopy(base),padding=lambda c,cfg,b:copy.deepcopy(pad),io=lambda c,cfg,p:copy.deepcopy(proof),archive=lambda c:copy.deepcopy(archive))
 audit=lambda:m.audit_canary(c,expected,r,_ops=ops);yes=audit();ck('CPU_positive_exact_chain_returns_evidence_but_not_production_permission',yes['status']=='PASS_CANARY_ROLLOUT_READONLY_REPLAY'and yes['production_release_eligible']is False)
 dp.unlink();missing=audit();put(dp,dict(done,launcher_wait_returncode=-15));failed=audit();put(dp,done);ck('missing_or_non_natural_receipt_HOLD',missing['status']==failed['status']=='HOLD_CANARY_ROLLOUT')
 old=ops.base;ops.base=lambda c:dict(base,original_detail='changed');bad=audit();ops.base=old;ck('any_original_strict_difference_HOLD',bad['status']=='HOLD_CANARY_ROLLOUT'and bad['stage']=='original_strict_exact_replay')
 old=ops.padding;ops.padding=lambda *a:dict(pad,extra='tampered');badpad=audit();ops.padding=old;old=ops.io;ops.io=lambda *a:dict(proof,cycles=8);badio=audit();ops.io=old;ck('padding_replay_or_IO_AND_mismatch_HOLD',badpad['status']==badio['status']=='HOLD_CANARY_ROLLOUT')
 old=ops.archive;ops.archive=lambda c:dict(archive,independently_verified_entries=0);bad=audit();ops.archive=old;ck('archive_restore_independent_verification_mismatch_HOLD',bad['status']=='HOLD_CANARY_ROLLOUT'and bad['stage']=='actual_archive_native_restore')
 pin.write_text('drift');bad=audit();pin.write_text('pinned');ck('source_or_route_drift_HOLD',bad['status']=='HOLD_CANARY_ROLLOUT'and bad['stage']=='current_source_route_pins')
 marker=r/'FORBIDDEN';old=ops.base
 def forbidden(c):marker.write_text('must not be created');return base
 ops.base=forbidden;bad=audit();ops.base=old;ck('read_only_write_barrier_blocks_side_effects',bad['status']=='HOLD_CANARY_ROLLOUT'and'READONLY_AUDIT_WRITE_BLOCKED'in bad['error']and not marker.exists())
m._guard.findmnt=dict(entry='/pinned/trace',binary_path='/usr/bin/findmnt',binary_sha256=sha(P('/usr/bin/findmnt')),source_path='/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py',source_sha256=sha(P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py')));m._guard.enabled=True;denied=[]
for eventargs in [('sh',['sh','-c','true'],None,None),('findmnt',['findmnt','-J','-T','/other'],None,None),('findmnt',['findmnt','-J','-T','/pinned/trace'],None,None)]:
 try:m._audit('subprocess.Popen',eventargs);denied.append(False)
 except (AssertionError,PermissionError):denied.append(True)
m._guard.enabled=False;m._guard.findmnt=None;ck('nonfindmnt_wrongentry_and_unpinned_caller_all_blocked',all(denied))
qa=dict(schema='READONLY_CANARY_ROLLOUT_AUDIT_CPU_QUALIFICATION_V1',status='PASS',checks=checks,total_checks=len(checks),source_sha256=sha(B/'audit_canary_rollout.py'),driver_sha256=sha(P(__file__)),production_mutations=0,model_starts=0,model_signals=0,CPU_positive_never_production_release_eligible=True,original_strict_and_archive_callbacks_are_explicit_CPU_fixtures=True)
(B/'CPU_QUALIFICATION.json').write_bytes(js(qa));print(json.dumps(qa))
