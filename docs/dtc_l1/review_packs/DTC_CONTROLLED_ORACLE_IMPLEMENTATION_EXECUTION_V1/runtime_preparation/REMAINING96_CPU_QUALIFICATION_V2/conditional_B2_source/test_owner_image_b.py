"""Pure projections and real temporary inherited OFDs; zero scientific action."""
from pathlib import Path
import ast,copy,fcntl,hashlib,importlib.util,json,os,tempfile,unittest
from unittest.mock import patch
P=Path(__file__).with_name('oracle_owner_image_b.py')
s=importlib.util.spec_from_file_location('MOCK_OWNER_B',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class CPUFixtures(unittest.TestCase):
 def data(self):
  q=dict(request=m.REQUEST8,budget=32,remaining=0,consumed={},admitted_specs={})
  specs={};bindings={};proofs={};prior={}
  for i in range(32):
   c='MOCK_NOT_SCIENCE_C'+str(i);u='MOCK_NOT_SCIENCE_UUID'+str(i)
   spec=dict(cohort=c,host_cpu=None,workload='MOCK',limits=dict(max_process_tree_rss_bytes=4*1024**3,max_result_directory_bytes=256*1024**2))
   sh=hashlib.sha256(m.encoded(spec)).hexdigest()
   binding=dict(cohort=c,host_cpu=200+i,canonical_spec_sha256=sh,
        resolved_spec_sha256=hashlib.sha256(m.encoded(dict(spec,host_cpu=200+i))).hexdigest())
   specs[c]=spec;bindings[c]=binding;q['consumed'][c]=dict(uuid=u,intent_sha256='MOCK');q['admitted_specs'][c]=sh
   proofs[c]=dict(state='EXACT_CLOSED_NONLIVE_RETAIN_ARCHIVE_BACKLOG'if i<24 else'LIVE_OR_UNCERTAIN_RETAIN_CLAIM',uuid=u,actual_simulator_live=i<28)
   if i>=24:prior[c]=dict(cohort=c,uuid=u,host_cpu=200+i,predicted_peak_RAM_bytes=2*1024**3)
  return q,prior,specs,bindings,proofs

 def test_live_and_uncertain_all_retained_closed_backlog_explicit(self):
  q,prior,specs,bindings,proofs=self.data()
  claims,report=m.adoption_claims(q,prior,specs,bindings,lambda c,r:proofs[c])
  self.assertEqual(len(claims),8);self.assertEqual(len(report),32)
  self.assertEqual({x['host_cpu']for x in claims.values()},set(range(224,232)))
  self.assertTrue(all(x['uuid']for x in claims.values()))

 def test_missing_old_claim_conservatively_uses_real_spec_cap(self):
  q,prior,specs,bindings,proofs=self.data()
  claims,_=m.adoption_claims(q,{},specs,bindings,lambda c,r:proofs[c])
  self.assertTrue(all(x['predicted_peak_RAM_bytes']==4*1024**3 for x in claims.values()))

 def test_identity_and_budget_mutations_rejected(self):
  q,prior,specs,bindings,proofs=self.data()
  for field,new in [('budget',33),('remaining',1),('request','NEW_FAKE_REQUEST')]:
   x=copy.deepcopy(q);x[field]=new
   with self.assertRaises(m.Hold):m.adoption_claims(x,prior,specs,bindings,lambda c,r:proofs[c])
  p=copy.deepcopy(proofs);p['MOCK_NOT_SCIENCE_C25']['uuid']='other'
  with self.assertRaises(m.Hold):m.adoption_claims(q,prior,specs,bindings,lambda c,r:p[c])

 def test_prior_cpu_uuid_conflict_rejected(self):
  q,prior,specs,bindings,proofs=self.data()
  for field,value in [('host_cpu',4),('uuid','foreign')]:
   p=copy.deepcopy(prior);p['MOCK_NOT_SCIENCE_C25'][field]=value
   with self.assertRaises(m.Hold):m.adoption_claims(q,p,specs,bindings,lambda c,r:proofs[c])

 def test_spec_and_resolved_binding_tamper_rejected(self):
  q,prior,specs,bindings,proofs=self.data()
  x=copy.deepcopy(specs);x['MOCK_NOT_SCIENCE_C25']['workload']='TAMPER'
  with self.assertRaises(m.Hold):m.adoption_claims(q,prior,x,bindings,lambda c,r:proofs[c])
  b=copy.deepcopy(bindings);b['MOCK_NOT_SCIENCE_C25']['host_cpu']=2
  with self.assertRaises(m.Hold):m.adoption_claims(q,prior,specs,b,lambda c,r:proofs[c])

 def test_unknown_liveness_cannot_vanish(self):
  q,prior,specs,bindings,proofs=self.data();proofs['MOCK_NOT_SCIENCE_C25']['state']='UNKNOWN'
  with self.assertRaises(m.Hold):m.adoption_claims(q,prior,specs,bindings,lambda c,r:proofs[c])

 def test_inherited_same_ofd_validated_without_relocking_or_closing(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_B_OFD_')as d:
   p=Path(d)/'SHARED.lock'
   with p.open('a+b')as held:
    fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);fd=os.dup(held.fileno());st=os.fstat(fd)
    row=dict(device=st.st_dev,inode=st.st_ino,target=str(p))
    before=Path('/proc/self/fdinfo',str(fd)).read_text()
    self.assertTrue(m.shared_fd_verify(fd,row)['no_new_open_or_flock'])
    self.assertEqual(before,Path('/proc/self/fdinfo',str(fd)).read_text())
    with p.open('a+b')as foreign:
     with self.assertRaises(BlockingIOError):fcntl.flock(foreign,fcntl.LOCK_EX|fcntl.LOCK_NB)
    self.assertEqual(os.fstat(fd).st_ino,st.st_ino);os.close(fd)

 def test_wrong_ofd_identity_rejected(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_B_FD_')as d:
   p=Path(d)/'x'
   with p.open('a+b')as held:
    fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);st=os.fstat(held.fileno())
    with self.assertRaises(m.Hold):m.shared_fd_verify(held.fileno(),dict(device=st.st_dev,inode=st.st_ino+1,target=str(p)))

 def test_fresh_normal_interpreter_real_cpu_pool_probe(self):
  value=m.fresh_pool_preflight()
  self.assertFalse(value['private_flags_written']);self.assertFalse(value['actual']['scientific_model'])

 def test_actual_29a_source_derivation_compiles_and_keeps_contract(self):
  p=Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8/tools/oracle_ops.py')
  source=p.read_text();changed,proof=m.derive_ops_source(source)
  self.assertEqual(proof['original_source_sha256'],m.OLD_OPS_SHA)
  self.assertEqual(len(proof['anchors']),25)
  self.assertIn("if ctx['plan']['stage']=='remaining24':sync_stage_reservation",changed)
  self.assertNotIn("with(BASE/'control/SHARED_DISPATCH_OWNER.lock').open",changed)
  self.assertIn("max_workers=1,thread_name_prefix='DTC_ORACLE_ARCHIVE'",changed)
  self.assertIn('verify_initial_runtime_gate',changed)
  self.assertIn('with _B_review_scope()as _B_review_held:',changed)
  self.assertIn('pass_fds=(_B_review_held.fileno(),)',changed)
  self.assertIn("if not state.get('B_admission_paused_in_memory')and",changed)
  self.assertIn("if state.get('B_admission_paused_in_memory')or not all_pending",changed)
  ast.parse(changed)

 def test_nonexact_dispatcher_refused(self):
  with self.assertRaises(m.Hold):m.derive_ops_source('MOCK_NOT_SCIENCE_TAMPER')

 def test_import_is_inert_and_no_execute_cli(self):
  tree=ast.parse(P.read_text())
  for node in tree.body:
   if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call):
    self.assertNotIn(ast.unparse(node.value.func),['apply','run_native','prepare','update_authority'])
  self.assertEqual(m.REQUEST24,'DTC_ORACLE_REMAINING24_20261106_V1')

 def transition(self):
  once=dict(release_sha256='MOCK_RELEASE',image_manifest_sha256='MOCK_MANIFEST',actual_image_PID=m.OWNER,actual_image_start=m.START)
  resolution=dict(status='RESOLVED_BY_FULLY_VALIDATED_NEW_IMAGE_ACK',once_sha256='MOCK_ONCE',ACK_sha256='MOCK_ACK',
      release_sha256='MOCK_RELEASE',image_source_sha256='MOCK_IMAGE',manifest_sha256='MOCK_MANIFEST')
  ack=dict(schema='DTC_OWNER_IMAGE_CLOSEOUT_A_STATUS_V1',phase='BOOTSTRAPPED_NO_CLOSURE_ADMISSION_YET',pid=m.OWNER,
      start_ticks=m.START,image_source_sha256='MOCK_IMAGE',manifest_sha256='MOCK_MANIFEST',entry_threads=1,
      new_scientific_starts=0,registrations=0,model_signals=0)
  journal=dict(schema='DTC_PRODUCTION_NATIVE_RAW_EXEC_JOURNAL_V1',status='EXECVE_ACCEPTED_AWAIT_NEW_IMAGE_BOOTSTRAP',
      owner_pid=m.OWNER,owner_start_ticks=m.START,stages=['KERNEL_REPLACED_IMAGE_SAME_PID_START'],
      inferior_C_or_Python_function_calls=0,post_exec_cmdline_sha256='MOCK_CMD',environment_sha256='MOCK_ENV',
      selected_fd_journal=[dict(fd=3,device=1,inode=2,before_FD_flags=1,after_FD_flags=0)])
  outcome=dict(status='VALIDATED_NEW_OWNER_IMAGE_BOOTSTRAP_ACK',validated_ACK_sha256='MOCK_ACK',image_source_sha256='MOCK_IMAGE',
      manifest_sha256='MOCK_MANIFEST',tracer_killed=False,automatic_retry=False)
  kwargs=dict(once_sha='MOCK_ONCE',ack_sha='MOCK_ACK',image_sha='MOCK_IMAGE',manifest_sha='MOCK_MANIFEST',
      cmdline_sha='MOCK_CMD',environment_sha='MOCK_ENV',preserve_fds=[dict(fd=3,device=1,inode=2)])
  return [once,resolution,ack,journal,outcome],kwargs

 def test_full_raw_exec_ack_resolution_links(self):
  args,kwargs=self.transition();self.assertEqual(m.transition_projection(*args,**kwargs)['status'],'PASS_BOUND_RAW_EXEC_RESOLUTION_ACK')

 def test_pending_wrong_image_or_fake_ack_and_raw_paths_refused(self):
  args,kwargs=self.transition()
  for index,field,value in [(1,'status','UNCERTAIN'),(1,'once_sha256','other'),(2,'entry_threads',3),
      (2,'new_scientific_starts',1),(3,'status','PRE_EXEC_ERROR_FORWARD_ONLY'),(3,'environment_sha256','other'),
      (3,'inferior_C_or_Python_function_calls',1),(4,'automatic_retry',True)]:
   bad=copy.deepcopy(args);bad[index][field]=value
   with self.assertRaises(m.Hold):m.transition_projection(*bad,**kwargs)

 def test_fd_replacement_cannot_be_hidden_by_ack(self):
  args,kwargs=self.transition();args[3]['selected_fd_journal'][0]['inode']=5
  with self.assertRaises(m.Hold):m.transition_projection(*args,**kwargs)

 def test_duplicate_inherited_shared_references_same_real_OFD(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_B2_DUP_')as tmp:
   p=Path(tmp)/'shared'
   with p.open('a+b')as held:
    fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);dup=os.dup(held.fileno());st=os.fstat(dup)
    rows=[dict(fd=fd,device=st.st_dev,inode=st.st_ino,target=str(p),role='shared_lock')for fd in[held.fileno(),dup]]
    result=m.shared_scope_references(rows,p)
    self.assertEqual(len(result['all_reference_proofs']),2)
    self.assertTrue(result['no_open_dup_flock_unlock_or_close'])
    self.assertEqual(os.fstat(dup).st_ino,st.st_ino)
    with p.open('a+b')as unlocked:
     bad=copy.deepcopy(rows);bad[1]['fd']=unlocked.fileno()
     with self.assertRaises(m.Hold):m.shared_scope_references(bad,p)
    os.close(dup)

 def test_manifest_disk_or_real_entry_dict_drift_rejected(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_B2_ENTRY_')as tmp:
   p=Path(tmp)/'manifest.json';p.write_text(json.dumps(dict(MOCK=True))+'\n')
   entry=dict(manifest_path=str(p),manifest_sha256=m.sha(p),manifest=dict(MOCK=True))
   self.assertTrue(m.verify_actual_entry_manifest(entry)['actual_ENTRY_dict_exact'])
   bad=copy.deepcopy(entry);bad['manifest']['MOCK']=False
   with self.assertRaises(m.Hold):m.verify_actual_entry_manifest(bad)
   p.write_text(json.dumps(dict(MOCK=False))+'\n')
   with self.assertRaises(m.Hold):m.verify_actual_entry_manifest(entry)

 def test_unreviewed_RSS_helper_refused_before_any_loader_call(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_RSS_REVIEW_')as tmp:
   p=Path(tmp)/'helper.py';p.write_text('# MOCK_NOT_SCIENCE\n')
   cfg=dict(RSS_history_adapter=dict(path=str(p),sha256=m.sha(p)))
   with patch.object(m,'load')as loader:
    with self.assertRaises(m.Hold):m.load_reviewed_RSS_adapter(cfg,dict(RSS_history_adapter_sha256='wrong'))
    loader.assert_not_called()
    m.load_reviewed_RSS_adapter(cfg,dict(RSS_history_adapter_sha256=m.sha(p)));loader.assert_called_once()

if __name__=='__main__':unittest.main(verbosity=2)
