"""Pure mutations of actual read-only facts + temporary real governor OFDs.

No execution of the single-pass driver or any scientific consumer occurs.
"""
from pathlib import Path
import copy,fcntl,importlib.util,json,os,tempfile,unittest
HERE=Path(__file__).parent
def load(name):
 p=HERE/(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=load('oracle_external31_gate');d=load('oracle_external31_once')

class Tests(unittest.TestCase):
 def data(self):
  basis=json.loads((HERE/'ACTUAL_READONLY_RETIREMENT_BASIS.fixed.json').read_bytes())
  cfg=json.loads((HERE/'CONFIG_TEMPLATE.fixed.json').read_bytes())
  boundary=json.loads(Path(cfg['kernel_boundary_proof']['path']).read_bytes())
  return copy.deepcopy(basis['facts']),boundary,cfg['original_tracer']

 def test_actual_readonly_kernel_fact_positive(self):
  f,b,t=self.data();self.assertEqual(g.validate_kernel_snapshot(f,b,t)['old_python_tasks_zombie'],102)

 def test_old_closer_or_any_python_thread_runnable_refused(self):
  for tid in [408874,1498284]:
   f,b,t=self.data();row=next((x for x in f['tasks']if x['tid']==tid),next(x for x in f['tasks']if x['tid']!=g.OWNER));row['state']='S'
   with self.assertRaises(g.Hold):g.validate_kernel_snapshot(f,b,t)

 def test_task_add_remove_or_snapshot_drift_refused(self):
  for kind in ['extra','missing','drift']:
   f,b,t=self.data()
   if kind=='extra':f['tasks'].append(dict(tid=999999999,state='Z'))
   elif kind=='missing':f['tasks'].pop()
   else:f['task_ids_after'].pop()
   with self.assertRaises(g.Hold):g.validate_kernel_snapshot(f,b,t)

 def test_wrong_owner_start_syscall_payload_or_stack_refused(self):
  for key,value in [('owner_start_ticks',1),('syscall','202 0x0 0x0 0x0'),('syscall','59 0x1 0x2 0x3'),('kernel_stack','futex_wait'),('kernel_release','unknown')]:
   f,b,t=self.data();f[key]=value
   with self.assertRaises(g.Hold):g.validate_kernel_snapshot(f,b,t)

 def test_wrong_tracer_identity_refused(self):
  for key,value in [('owner_tracer_pid',1),('tracer_start_ticks',1),('tracer_cmdline_sha256','wrong')]:
   f,b,t=self.data();f[key]=value
   with self.assertRaises(g.Hold):g.validate_kernel_snapshot(f,b,t)

 def test_tracer_sleep_wchan_is_only_supplemental(self):
  f,b,t=self.data();f['tracer_wchan']='0';self.assertFalse(g.validate_kernel_snapshot(f,b,t)['tracer_sleep_park_supplemental'])

 def test_real_temporary_EX_governor_and_foreign_peer_conflict(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_EXTERNAL_GOV_')as tmp:
   p=Path(tmp)/'gov'
   with p.open('a+b')as held:
    fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);st=os.fstat(held.fileno())
    ctx=dict(governance_lock=str(p),governance_lock_fd=held.fileno(),governance_lock_device_inode=[st.st_dev,st.st_ino])
    self.assertTrue(g.verify_governance_fd(ctx,p)['actual_EX_flock'])
    with p.open('a+b')as peer:
     with self.assertRaises(BlockingIOError):fcntl.flock(peer,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ctx['governance_lock_device_inode'][1]+=1
    with self.assertRaises(g.Hold):g.verify_governance_fd(ctx,p)

 def test_shared_or_unlocked_fd_not_admitted(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_EXTERNAL_UNLOCKED_')as tmp:
   p=Path(tmp)/'gov'
   with p.open('a+b')as held:
    st=os.fstat(held.fileno());ctx=dict(governance_lock=str(p),governance_lock_fd=held.fileno(),governance_lock_device_inode=[st.st_dev,st.st_ino])
    with self.assertRaises(g.Hold):g.verify_governance_fd(ctx,p)
    fcntl.flock(held,fcntl.LOCK_SH|fcntl.LOCK_NB)
    with self.assertRaises(g.Hold):g.verify_governance_fd(ctx,p)

 def snapshot(self):return json.loads((HERE/'FIXED31_NATURAL_DONE_SNAPSHOT.fixed.json').read_bytes())
 def test_exact31_and_original8_preserved(self):
  snap=self.snapshot();auth=dict(authorized_closed_cohorts=[x['cohort']for x in snap['rows']]);rows=d.validate_fixed31(snap,auth)
  self.assertEqual(len(rows),31);self.assertEqual(sum(x['existing_result_sha256']is not None for x in rows),8)

 def test_no_new_tail_or_missing_existing_result(self):
  for kind in ['tail','new32','existing','duplicates']:
   snap=self.snapshot()
   if kind=='tail':snap['excluded_live_or_not_DONE_cohort']='other'
   elif kind=='new32':snap['rows'].append(copy.deepcopy(snap['rows'][0]))
   elif kind=='existing':next(x for x in snap['rows']if x['existing_result_sha256']is not None)['existing_result_sha256']=None
   else:snap['rows'][1]=copy.deepcopy(snap['rows'][0])
   auth=dict(authorized_closed_cohorts=[x['cohort']for x in snap['rows']])
   with self.assertRaises(d.Hold):d.validate_fixed31(snap,auth)

 def test_same_release_cannot_start_a_second_pass(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_ONCE31_')as tmp:
   path=d.claim_pass_directory(tmp,'0'*64);self.assertTrue(path.is_dir())
   with self.assertRaises(FileExistsError):d.claim_pass_directory(tmp,'0'*64)
   with self.assertRaises(d.Hold):d.claim_pass_directory(tmp,'../bad')

 def test_draft_cannot_reach_any_consumer_or_lock(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_UNARMED31_')as tmp:
   p=Path(tmp)/'draft.json';p.write_text(json.dumps(dict(actual_execution_authorized=False))+'\n')
   with self.assertRaises(d.Hold):d.run(p,d.sha(p))
   self.assertEqual([x.name for x in Path(tmp).iterdir()],['draft.json'])

if __name__=='__main__':unittest.main(verbosity=2)
