"""Read-only rollout audit; returns evidence only, never restores admission.
Original strict is replayed, then padding, IO AND, natural receipt and archive.
"""
import pathlib,json,hashlib,importlib.util,sys,threading,os,copy,shutil
sys.dont_write_bytecode=True
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';EXTRA={'additional_padding_admission_strict','additional_shared_json_io_strict'}
_guard=threading.local();_hook=False
def _audit(event,args):
 if not getattr(_guard,'enabled',False):return
 if event=='open':
  flags=args[2]if len(args)>2 else 0
  if isinstance(flags,int)and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):raise PermissionError('READONLY_AUDIT_WRITE_BLOCKED '+str(args[0]))
 if event=='subprocess.Popen':
  permit=getattr(_guard,'findmnt',None);executable,argv,cwd,env=args;assert permit is not None,'READONLY_AUDIT_UNAPPROVED_SUBPROCESS'
  assert executable=='findmnt'and argv==['findmnt','-J','-T',permit['entry']]and cwd is None and env is None,'READONLY_AUDIT_FINDMNT_ARGV_MISMATCH'
  actual=shutil.which(executable);assert actual and str(P(actual).resolve())==permit['binary_path']and sha(actual)==permit['binary_sha256'],'READONLY_AUDIT_FINDMNT_BINARY_DRIFT'
  frame=sys._getframe(1);matched=False
  while frame is not None:
   if frame.f_code.co_name=='check_input'and str(P(frame.f_code.co_filename))==permit['source_path']:
    assert sha(permit['source_path'])==permit['source_sha256'];matched=True;break
   frame=frame.f_back
  assert matched,'READONLY_AUDIT_FINDMNT_UNPINNED_CALLER';return
 if event in {'os.mkdir','os.remove','os.rename','os.rmdir','os.link','os.symlink','os.truncate','os.chmod','os.chown','os.utime','os.kill','os.killpg','os.fork','os.posix_spawn'}:raise PermissionError('READONLY_AUDIT_MUTATION_BLOCKED '+event)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def configure_readonly_findmnt(spec,expected):
 binding=P(spec['input_binding_path']);assert sha(binding)==spec['input_binding_sha256'];entry=read(binding)['qualification']['trace_entry'];binary='/usr/bin/findmnt';source='/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py';pins=expected['source_and_route_pins'];assert sha(binary)==pins[binary]and sha(source)==pins[source]
 _guard.findmnt=dict(entry=entry,binary_path=binary,binary_sha256=pins[binary],source_path=source,source_sha256=pins[source])
class Actual:
 def __init__(self,root):self.root=P(root);self.e=load('rollout_actual_native',self.root/'tools/l2_native.py')
 def registry(self):return self.e.registered()[2]
 def base(self,c):return load('rollout_unchanged_base_strict',self.root/'tools/l2_strict.py').terminal(c)
 def padding(self,c,cfg,base):return load('rollout_unchanged_padding_strict',cfg['extra_strict_path']).terminal(c,cfg,base)
 def io(self,c,cfg,proof):return load('rollout_unchanged_io_strict',cfg['extra_strict_path']).terminal(c,proof)
 def archive(self,c):return load('rollout_actual_archive_verify',self.root/'tools/l2_outbox.py').verify(c)
def audit_canary(cohort,expected,root=R,_ops=None):
 global _hook
 if not _hook:sys.addaudithook(_audit);_hook=True
 assert not getattr(_guard,'enabled',False),'Nested rollout audit not supported'
 _guard.enabled=True;stage='start';backend='ACTUAL_READONLY'if _ops is None else'CPU_FIXTURE'
 try:
  root=P(root)
  def pins():
   for path,digest in expected['source_and_route_pins'].items():assert sha(path)==digest,'Current source/route drift: '+path
  stage='current_source_route_pins';pins();ops=_ops or Actual(root);q=ops.registry();c=cohort;stage='required_closed_files';ip=root/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);row=q['consumed'][c];out=P(i['output']);rp=root/'analysis'/(c+'.RESULT.json');dp=ip.with_name(c+'.DONE.json')
  for p in[dp,rp,out/'NATIVE_EXIT.json',out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',out/'L2_STRICT.json',out/'PADDING_EXTRA_STRICT.json',out/'SHARED_JSON_IO_EXTRA_STRICT.json',out/'PADDING_ADMISSION_EVIDENCE.json',out/'SHARED_JSON_IO_SNAPSHOT.json',root/'control'/(c+'_ARCHIVE_RECEIPT.json')]:assert p.is_file(),'Required artifact missing: '+str(p)
  stage='identity_natural_receipt';d=read(dp);result=read(rp);assert row['uuid']==i['uuid']==d['uuid']==result['uuid']==expected['uuid'];assert row['intent_sha256']==sha(ip);assert d==row['execution_receipt']==read(out/'NATIVE_EXIT.json');assert d['stop_reason']is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed']is True and d['new_attempt_consumed']==1
  assert result['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and result['cohort']==c;assert sha(root/'control/specs'/(c+'.json'))==q['admitted_specs'][c]==expected['canonical_spec_sha256'];assert read(out/'L2_STRICT.json')==result['proof']
  stage='original_strict_exact_replay'
  if backend=='ACTUAL_READONLY':configure_readonly_findmnt(read(root/'control/specs'/(c+'.json')),expected)
  base=ops.base(c);assert base['performance_accepted']is True;stored={k:v for k,v in result['proof'].items()if k not in EXTRA};assert base==stored,'Original strict changed beyond exactly two allowed additional fields';assert result['cycles']==base['cycles'];assert EXTRA<=set(result['proof'])
  stage='padding_full_replay';pcfg=read(out/'PADDING_ACTIVATION_CONFIG.json');padding=ops.padding(c,pcfg,base);assert padding==result['proof']['additional_padding_admission_strict'];assert padding['sidecar_sha256']==sha(out/'PADDING_EXTRA_STRICT.json')and padding['status']=='PASS_PADDING_ADMISSION_AND_ORIGINAL_STRICT'
  stage='IO_full_AND_replay';iocfg=read(out/'SHARED_JSON_IO_SNAPSHOT.json')['config'];combined=ops.io(c,iocfg,dict(base,additional_padding_admission_strict=padding));assert combined==result['proof'],'IO AND replay differs from stored RESULT proof';io=combined['additional_shared_json_io_strict'];assert io['sidecar_sha256']==sha(out/'SHARED_JSON_IO_EXTRA_STRICT.json')and io['status']=='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT'
  stage='actual_archive_native_restore';archive=ops.archive(c);assert archive==result['archive'];assert archive['receipt']==read(root/'control'/(c+'_ARCHIVE_RECEIPT.json'));assert archive['independently_verified_entries']>0;receipt=archive['receipt'];assert receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and receipt['source_disposition']=='SOURCE_KEEP';assert P(receipt['native_restore']).is_dir()
  stage='final_identity_pin_recheck';pins();again=ops.registry()['consumed'][c];assert again==row and sha(ip)==row['intent_sha256'];return dict(status='PASS_CANARY_ROLLOUT_READONLY_REPLAY',production_release_eligible=backend=='ACTUAL_READONLY',backend=backend,cohort=c,uuid=i['uuid'],cycles=base['cycles'],RESULT_sha256=sha(rp),DONE_sha256=sha(dp),padding_sidecar_sha256=padding['sidecar_sha256'],IO_sidecar_sha256=io['sidecar_sha256'],archive=archive,source_and_route_pins=expected['source_and_route_pins'],admission_changed=False,models_started=0,model_signals=0,read_only_write_barrier=True)
 except Exception as e:return dict(status='HOLD_CANARY_ROLLOUT',production_release_eligible=False,backend=backend,cohort=cohort,stage=stage,error=repr(e),admission_changed=False,models_started=0,model_signals=0,read_only_write_barrier=True)
 finally:_guard.enabled=False;_guard.findmnt=None
if __name__=='__main__':
 assert len(sys.argv)==3;print(json.dumps(audit_canary(sys.argv[1],read(sys.argv[2])),sort_keys=True,indent=2))
