"""Read-only rollout audit; returns evidence only, never restores admission.
Original strict is replayed, then versioned memory/padding/IO AND, natural receipt and archive.
"""
import pathlib,json,hashlib,importlib.util,sys,threading,os,copy,shutil
sys.dont_write_bytecode=True
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';MEM_ID='FUTURE_ONLY_MEMORY_ADMISSION_095_FLOOR10_V1';MEM_STRICT_SHA='78abb1c386e684ab250fb8e78398c79f564796cebc3f486c1e6ecff77a6236cd';CANARY='E2-DTCL2MLP-2b93f70cd0666c51-DH-Q64-V1'
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
 def __init__(self,root):self.root=P(root);self.e=load('future_rollout_actual_native',self.root/'tools/l2_native.py')
 def registry(self):return self.e.registered()[2]
 def base(self,c):return load('future_rollout_original_performance',self.root/'tools/l2_strict.py').terminal(c)
 def memory(self,c,cfg,base):
  assert sha(cfg['extra_strict_path'])==cfg['extra_strict_sha256']==MEM_STRICT_SHA
  return load('future_rollout_qualified_memory_strict',cfg['extra_strict_path']).terminal(c,base)
 def archive(self,c):return load('future_rollout_actual_outbox',self.root/'tools/l2_outbox.py').verify(c)

def canonical_projection(spec):
 value=copy.deepcopy(spec);value.pop('estimated_peak_model_RAM_bytes');value['limits'].pop('max_process_tree_rss_bytes');value['limits'].pop('max_process_tree_vms_bytes');return value

def objsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()

def verify_canonical_bridge(root,c,pre_sha,final_spec,q,intent,dispatch):
 root=P(root);finalsha=sha(root/'control/specs'/(c+'.json'));assert finalsha==q['admitted_specs'][c]==intent['spec_sha256']==dispatch['canonical_spec_sha256'];assert objsha(dict(final_spec,host_cpu=dispatch['host_cpu']))==dispatch['resolved_spec_sha256'];current=copy.deepcopy(final_spec);current_sha=finalsha;steps=[];seen=set()
 while current_sha!=pre_sha:
  assert current_sha not in seen and len(seen)<64,'Ambiguous/cyclic canonical resource history';seen.add(current_sha);mp=root/'control/resource_spec_history'/c/(current_sha+'.AMENDMENT.json');am=read(mp);assert am['cohort']==c and am['new_sha256']==current_sha;oldpath=mp.with_name(am['old_sha256']+'.json');assert sha(oldpath)==am['old_sha256'];old=read(oldpath);assert canonical_projection(old)==canonical_projection(current),'Nonresource science/limit field changed';assert am['forecast']['predicted_peak_RAM_bytes']==current['estimated_peak_model_RAM_bytes']and am['forecast']['proposed_process_tree_rss_cap_bytes']==current['limits']['max_process_tree_rss_bytes'];steps.append(dict(old_sha256=am['old_sha256'],new_sha256=current_sha,amendment_sha256=sha(mp),preimage_sha256=sha(oldpath)));current=old;current_sha=am['old_sha256']
 assert current_sha==pre_sha;return dict(pre_refresh_prediction_bytes=current['estimated_peak_model_RAM_bytes'],final_prediction_bytes=final_spec['estimated_peak_model_RAM_bytes'],status='PASS_EXACT_PRE_REFRESH_TO_INTENT_BRIDGE',pre_refresh_sha256=pre_sha,final_canonical_sha256=finalsha,steps=steps,science_projection_sha256=objsha(canonical_projection(final_spec)))

def verify_lease(root,c,expected,final_spec,q,intent,dispatch,memlib):
 required=expected['priority_lease']['required'];assert required is True,'This canary auditor requires the explicitly evidenced priority-lease dispatch';ep=expected['priority_lease'];authority=q['additional_operational_overlays']['FINITE_MEMORY_ENGINEERING_CANARY_PRIORITY_LEASE_V1'];assert authority['status']=='ACTIVE_PRIORITY_ONLY'and authority['allowed_cohorts']==[c]
 for k in ['source_sha256','QA_sha256','readback_sha256','memory_active_sha256']:assert authority[k]==ep[k]
 for path,digest in authority['dependency_pins'].items():assert sha(path)==digest,'Priority lease dependency source drift'
 assert sha(ep['source_path'])==ep['source_sha256'];assert sha(ep['QA_path'])==ep['QA_sha256']and sha(ep['readback_path'])==ep['readback_sha256'];qa=read(ep['QA_path']);back=read(ep['readback_path']);assert qa['status']=='PASS'and qa['owner_integration_qualified']and qa['complete_memory_generic_B_exercised']and back['verified']is True and back['QA_sha256']==ep['QA_sha256'];assert qa['source_sha256']==back['source_sha256']==ep['source_sha256']and qa['dependency_pins']==back['dependency_pins']==authority['dependency_pins'];path=P(ep['cpu_returned_receipt_path']);assert sha(path)==ep['CPU_RETURNED_sha256'];receipt=read(path);assert receipt['schema']=='FINITE_MEMORY_ENGINEERING_CANARY_PRIORITY_LEASE_V1'and receipt['stage']=='CPU_RETURNED_DURABLE_BEFORE_CLAIM_INTENT';link=receipt['reservation'];tokenpath=P(link['path']);assert sha(tokenpath)==link['sha256']==ep['RESERVED_sha256'];token=read(tokenpath);assert receipt['cohort']==token['cohort']==link['cohort']==c;assert path.name==link['attempt']+'.CPU_RETURNED.json'and tokenpath.name==link['attempt']+'.RESERVED.json'and token['attempt']==link['attempt'];assert token['stage']=='RESERVED_BEFORE_CPU_RETURN'and token['schema']==receipt['schema'];assert token['source_sha256']==receipt['source_sha256']==ep['source_sha256'];assert token['QA_sha256']==ep['QA_sha256']and token['readback_sha256']==ep['readback_sha256']and token['memory_active_sha256']==ep['memory_active_sha256'];assert receipt['priority_only']is True and receipt['no_grant_or_R_change']is True and token['priority_only']is True and token['R_mutated']is False and token['natural_release_credit_bytes']==0;assert receipt['canonical_spec_sha256']==token['canonical_spec_sha256'];assert receipt['host_cpu']==dispatch['host_cpu'];proofs=[]
 for k in ['first','second']:
  point=token[k];p=point['memory_proof'];proofs.append(memlib.verify_memory_proof(p));assert point['full_candidate_cost_bytes']>0 and point['prospective_growth_bytes']==p['growth_unchanged_bytes']+point['full_candidate_cost_bytes']<=p['effective_decision']['admission_RAM_budget_bytes']
 bridge=verify_canonical_bridge(root,c,token['canonical_spec_sha256'],final_spec,q,intent,dispatch);assert all(token[k]['full_candidate_cost_bytes']>=bridge['pre_refresh_prediction_bytes']for k in ['first','second']);return dict(status='PASS_PRIORITY_LEASE_AND_EXACT_CANONICAL_BRIDGE',CPU_RETURNED_sha256=sha(path),RESERVED_sha256=sha(tokenpath),source_sha256=ep['source_sha256'],fresh_proofs=proofs,bridge=bridge,refresh_bridge_sha256=objsha(bridge))

def audit_canary(cohort,expected,root=R,_ops=None):
 global _hook
 if not _hook:sys.addaudithook(_audit);_hook=True
 assert not getattr(_guard,'enabled',False),'Nested rollout audit not supported'
 _guard.enabled=True;stage='start';backend='ACTUAL_READONLY'if _ops is None else'CPU_FIXTURE'
 try:
  root=P(root);assert expected['auditor_source_sha256']==sha(__file__),'Auditor source not pinned';assert cohort==CANARY,'Only the exact registered scalarProd DH-Q64 memory canary is eligible';assert expected['cohort']==cohort;assert expected['schema']=='FUTURE_MEMORY_ACTUAL_CANARY_EXPECTATIONS_V1'
  def pins():
   for path,digest in expected['source_and_route_pins'].items():assert sha(path)==digest,'Current source/route drift: '+path
  stage='current_source_route_pins'
  if backend=='ACTUAL_READONLY':
   mandatory=[str(root/'tools/l2_native.py'),str(root/'tools/l2_strict.py'),str(root/'tools/l2_outbox.py'),'/usr/bin/findmnt','/root/data/ep_l2_dtc_l1_native_v2/bin/native','/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py'];assert set(mandatory)<=set(expected['source_and_route_pins']),'Incomplete actual source/route pins'
  pins();ops=_ops or Actual(root);q=ops.registry();c=cohort
  stage='expected_birth_identity'
  if expected['uuid']is None or c not in q['consumed']:return dict(status='PENDING_NOT_BORN_OR_EXPECTATIONS_UNSEALED',production_release_eligible=False,backend=backend,cohort=c,stage=stage,admission_changed=False,models_started=0,model_signals=0,read_only_write_barrier=True)
  stage='required_closed_files';ip=root/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);row=q['consumed'][c];out=P(i['output']);rp=root/'analysis'/(c+'.RESULT.json');dp=ip.with_name(c+'.DONE.json');launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');ms=out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json';snap=read(ms);cfg=snap['config'];pad=snap['padding_optin'];extras={'additional_future_memory_admission_strict'}|({'additional_future_memory_padding_strict','additional_future_memory_io_strict'}if pad else{'additional_shared_json_io_strict'})
  sidecar_names=['FUTURE_MEMORY_EXTRA_STRICT.json']+(['FUTURE_MEMORY_PADDING_EXTRA_STRICT.json','FUTURE_MEMORY_IO_EXTRA_STRICT.json']if pad else['SHARED_JSON_IO_EXTRA_STRICT.json'])
  for p in[dp,rp,out/'NATIVE_EXIT.json',out/'L2_STRICT.json',out/'SHARED_JSON_IO_SNAPSHOT.json',root/'control'/(c+'_ARCHIVE_RECEIPT.json'),*[out/n for n in sidecar_names]]:assert p.is_file(),'Required artifact missing: '+str(p)
  stage='memory_three_bindings_snapshot_identity';binding=i['additional_future_memory_admission_binding'];assert all(doc['additional_future_memory_admission_binding']==binding for doc in[launch,pid]);assert binding['schema']==snap['schema']==MEM_ID and binding['request']==REQ;assert binding['snapshot_sha256']==sha(ms);assert binding['padding_optin']==pad;assert cfg['extra_strict_sha256']==MEM_STRICT_SHA;assert expected['memory_sources']==binding['qualified_sources']=={r:cfg[r+'_sha256']for r in ['library','frontend','owner','extra_strict','joint_padding','joint_io']}
  assert cfg['request']==REQ and c in cfg['allowed_cohorts'];assert objsha(cfg)==binding['config_sha256'];assert expected['memory_config_sha256']==binding['config_sha256'];assert 'additional_shared_json_io_binding'in i and all(doc['additional_shared_json_io_binding']==i['additional_shared_json_io_binding']for doc in[launch,pid]);assert pad==('additional_padding_admission_binding'in i)
  if pad:assert all(doc['additional_padding_admission_binding']==i['additional_padding_admission_binding']for doc in[launch,pid])
  for r,digest in expected['memory_sources'].items():assert expected['source_and_route_pins'][cfg[r+'_path']]==digest and sha(cfg[r+'_path'])==digest and snap['source_snapshots'][r]['sha256']==digest==hashlib.sha256(snap['source_snapshots'][r]['utf8'].encode()).hexdigest()
  stage='identity_natural_receipt';d=read(dp);result=read(rp);assert row['uuid']==i['uuid']==d['uuid']==result['uuid']==expected['uuid'];assert row['intent_sha256']==sha(ip);assert d==row['execution_receipt']==read(out/'NATIVE_EXIT.json');assert d['stop_reason']is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed']is True and d['new_attempt_consumed']==1;assert result['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and result['cohort']==c;assert read(out/'L2_STRICT.json')==result['proof'];specpath=root/'control/specs'/(c+'.json');spec=read(specpath);assert spec['cohort']==c and spec['program']=='scalarProd'and spec['cell']=='DH'and spec['profile']=='Q64';assert sha(specpath)==q['admitted_specs'][c]==i['spec_sha256'];dbpath=root/'control/dispatch_bindings'/(c+'.json');db=read(dbpath);assert sha(dbpath)==i['dispatch_binding_sha256']==pid['dispatch_binding_sha256']
  stage='original_strict_exact_replay'
  if backend=='ACTUAL_READONLY':configure_readonly_findmnt(spec,expected)
  base=ops.base(c);assert base['performance_accepted']is True;assert extras.isdisjoint(base);assert extras<=set(result['proof']);assert set(result['proof'])==set(base)|extras,'Unrecognized or missing proof field';assert base=={k:v for k,v in result['proof'].items()if k not in extras},'Original strict changed beyond explicit new additional fields';assert result['cycles']==base['cycles']
  stage='qualified_memory_padding_IO_full_AND_replay';combined=ops.memory(c,cfg,base);assert combined==result['proof'],'New memory/padding/IO AND replay differs from stored RESULT proof';memory=combined['additional_future_memory_admission_strict'];assert memory['status']=='PASS_FUTURE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'and memory['old_B5_strict_PASS_claimed']is False;assert memory['sidecar_sha256']==sha(out/'FUTURE_MEMORY_EXTRA_STRICT.json');assert {k:v for k,v in memory.items()if k not in ['sidecar_path','sidecar_sha256']}==read(out/'FUTURE_MEMORY_EXTRA_STRICT.json');assert memory['snapshot_sha256']==sha(ms)
  for key,name,status in ([('additional_future_memory_padding_strict','FUTURE_MEMORY_PADDING_EXTRA_STRICT.json','PASS_PADDING_MEMORY_AND_ORIGINAL_PERFORMANCE'),('additional_future_memory_io_strict','FUTURE_MEMORY_IO_EXTRA_STRICT.json','PASS_FUTURE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE')]if pad else[('additional_shared_json_io_strict','SHARED_JSON_IO_EXTRA_STRICT.json','PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT')]):
   extra=combined[key];assert extra['status']==status and extra['sidecar_sha256']==sha(out/name);assert {k:v for k,v in extra.items()if k not in ['sidecar_path','sidecar_sha256']}==read(out/name)
  stage='priority_lease_pre_refresh_to_INTENT_bridge';lib=load('future_rollout_memory_math',cfg['library_path']);assert sha(lib.__file__)==cfg['library_sha256'];lease=verify_lease(root,c,expected,spec,q,i,db,lib)
  stage='actual_archive_native_restore';archive=ops.archive(c);assert archive==result['archive'];assert archive['receipt']==read(root/'control'/(c+'_ARCHIVE_RECEIPT.json'));assert archive['independently_verified_entries']>0;receipt=archive['receipt'];assert receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and receipt['source_disposition']=='SOURCE_KEEP';assert P(receipt['native_restore']).is_dir()
  stage='final_identity_pin_recheck';pins();again=ops.registry()['consumed'][c];assert again==row and sha(ip)==row['intent_sha256'];return dict(status='PASS_FUTURE_MEMORY_CANARY_ROLLOUT_READONLY_REPLAY',production_release_eligible=backend=='ACTUAL_READONLY',backend=backend,cohort=c,uuid=i['uuid'],cycles=base['cycles'],RESULT_sha256=sha(rp),DONE_sha256=sha(dp),memory_snapshot_sha256=sha(ms),memory_sidecar_sha256=memory['sidecar_sha256'],lease=lease,archive=archive,source_and_route_pins=expected['source_and_route_pins'],admission_changed=False,models_started=0,model_signals=0,read_only_write_barrier=True)
 except Exception as e:return dict(status='HOLD_FUTURE_MEMORY_CANARY_ROLLOUT',production_release_eligible=False,backend=backend,cohort=cohort,stage=stage,error=repr(e),admission_changed=False,models_started=0,model_signals=0,read_only_write_barrier=True)
 finally:_guard.enabled=False;_guard.findmnt=None
if __name__=='__main__':
 assert len(sys.argv)==3;print(json.dumps(audit_canary(sys.argv[1],read(sys.argv[2])),sort_keys=True,indent=2))
