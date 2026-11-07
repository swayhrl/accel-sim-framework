"""Isolated CPU fixtures only; no production lock, registry, model, archive."""
from pathlib import Path
import copy,fcntl,importlib.util,json,os,subprocess,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=module('fixture_clean_guard','oracle_clean_owner_guard.py')
e=module('fixture_clean_engine','oracle_successor_engine.py')
def source_ref(p):return dict(path=str(p),sha256=g.sha(p))
if len(sys.argv)>1 and sys.argv[1]=='--child':
 # Isolated test process explicitly substitutes retired old identities. All
 # current parent PID/start/source/cmdline/fdinfo/real ancestry remain real.
 g.retired_processes=lambda *unused:[]
 plan=g.read(sys.argv[2]);original_read=g.read
 def read_inside_EX(path):
  if str(path)!=plan['clean_owner_lease']['path']:raise AssertionError('CPU_EX_SENTINEL_UNEXPECTED_JSON_OR_REGISTRY_READ')
  return original_read(path)
 g.read=read_inside_EX
 g.require_old32_closed=lambda *a:(_ for _ in()).throw(AssertionError('CPU_EX_SENTINEL_FULL32_READ_FORBIDDEN'))
 g.all_references=lambda *a:(_ for _ in()).throw(AssertionError('CPU_EX_SENTINEL_FULL_PROC_FD_SCAN_FORBIDDEN'))
 value=g.verify_parent_lease(plan,allow_cpu_fixture=True)
 print(json.dumps(dict(status='CPU_CHILD_REAL_ANCESTRY_PASS',pid=os.getpid(),owner=value['pid'],
    EX_sentinel_no_registry_full32_or_fullFDscan=True)))
 raise SystemExit(0)

class GuardTests(unittest.TestCase):
 def test_old_running_refused(self):
  with self.assertRaises(g.Hold):g.terminal(dict(pid=1,start_ticks=2,state='S'),1,2)
 def test_old_terminal_and_missing(self):
  self.assertEqual(g.terminal(None,1,2)['state'],'ABSENT')
  self.assertEqual(g.terminal(dict(pid=1,start_ticks=2,state='Z'),1,2)['state'],'ZOMBIE_NO_USERSPACE')
 def test_unrelated_pid_reuse_does_not_block_or_touch_foreign_process(self):
  self.assertEqual(g.terminal(dict(pid=1,start_ticks=3,state='S'),1,2)['state'],
    'OLD_GENERATION_ABSENT_UNRELATED_PID_REUSE')
 def test_foreign_lock_reference_refused(self):
  with self.assertRaises(g.Hold):g.require_exclusive_references([dict(pid=123)],124)
 def test_wrong_lock_kind_refused(self):
  with self.assertRaises(g.Hold):g.lock_record('lock: 1: FLOCK ADVISORY READ 3 00:01:2 0 EOF',3,1,2)
 def test_original_global_lock_inodes_mandatory(self):
  rows=[dict(role=k,device=v[0],inode=v[1])for k,v in g.FIXED_LOCK_IDENTITIES.items()]
  self.assertTrue(g.require_fixed_lock_identities(rows));rows[0]['inode']+=1
  with self.assertRaises(g.Hold):g.require_fixed_lock_identities(rows)
 def test_science_projection_exact_except_layout(self):
  a=dict(input_digest='a'*64,core_commit='e6',expected_options={'x':['1']},host_launcher_layout={'old':1})
  b=copy.deepcopy(a);b['host_launcher_layout']={'newCPU':1};self.assertTrue(e.require_science_equal(a,b))
  b['expected_options']['x']=['2']
  with self.assertRaises(e.Hold):e.require_science_equal(a,b)
 def test_inert_import_no_model_api(self):
  self.assertFalse(hasattr(e,'apply'));self.assertFalse(hasattr(g,'register'))
 def test_guard_source_tamper(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'s';p.write_text('x')
   with self.assertRaises(g.Hold):g.pin(dict(path=str(p),sha256='0'*64))
 def test_real_four_temp_locks_child_ancestry_and_foreign_scope(self):
  with tempfile.TemporaryDirectory(prefix='DTC_PURE_CPU_CLEAN_LOCKS_')as d:
   root=Path(d);handles=[];refs=[]
   try:
    for role in ['governance','owner','qualification','shared']:
     p=root/(role+'.lock');h=p.open('a+b');handles.append(h);fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
     st=os.fstat(h.fileno());r=dict(role=role,path=str(p),fd=h.fileno(),device=st.st_dev,inode=st.st_ino)
     g.verify_lock(r,os.getpid());refs.append(r)
    lease=dict(schema='DTC_ORACLE_CLEAN_MAIN_PRIVATE_LEASE_V1',pid=os.getpid(),
       start_ticks=g.process(os.getpid())['start_ticks'],controller=source_ref(Path(__file__).resolve()),
       request=g.REQUEST,budget=96,old32_new_starts=0,guard_sha256=g.sha(g.__file__),locks=refs)
    lp=root/'lease.json';lp.write_bytes(g.encoded(lease))
    plan=dict(request=g.REQUEST,expected_new_starts=96,clean_owner_lease=source_ref(lp),parent_pid=lease['pid'],
       parent_start_ticks=lease['start_ticks'],parent_controller_path=lease['controller']['path'],
       parent_controller_sha256=lease['controller']['sha256'])
    pp=root/'plan.json';pp.write_bytes(g.encoded(plan))
    completed=subprocess.run(['/usr/bin/python3','-B',str(Path(__file__).resolve()),'--child',str(pp)],capture_output=True,text=True,timeout=10)
    self.assertEqual(completed.returncode,0,completed.stderr)
    self.assertEqual(json.loads(completed.stdout)['status'],'CPU_CHILD_REAL_ANCESTRY_PASS')
    # Actual second OFD acquisition fails while original holder is healthy.
    peer=subprocess.run(['/usr/bin/python3','-c',"import fcntl,sys;h=open(sys.argv[1],'a+b');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)",refs[-1]['path']],capture_output=True,text=True)
    self.assertNotEqual(peer.returncode,0)
    changed=copy.deepcopy(lease);changed['locks'][0]['fd']=99999;lp.write_bytes(g.encoded(changed));plan['clean_owner_lease']=source_ref(lp);pp.write_bytes(g.encoded(plan))
    refused=subprocess.run(['/usr/bin/python3','-B',str(Path(__file__).resolve()),'--child',str(pp)],capture_output=True,text=True,timeout=10)
    self.assertNotEqual(refused.returncode,0)
   finally:
    for h in handles:h.close()
 def test_real_unrelated_process_is_not_owner_descendant(self):
  # Parent PID cannot descend from its direct child; no process signalling.
  with self.assertRaises(g.Hold):g.ancestry(os.getpid(),99999999,1)

class SourceTests(unittest.TestCase):
 def test_actual_source_transforms(self):
  pins=json.loads((HERE/'CPU_SOURCE_INPUTS.fixed.json').read_bytes())
  for ref in pins.values():g.pin(ref)
  native,nativeproof=e.derive_native(Path(pins['native']['path']).read_bytes())
  ops,opsproof=e.derive_ops(Path(pins['ops']['path']).read_bytes(),Path(pins['B2']['path']).read_bytes())
  self.assertTrue(nativeproof['unchanged_original_model_loop'])
  self.assertNotIn('1498278',ops);self.assertNotIn('977758783',ops)
  self.assertIn('_B_cycle_error',ops);self.assertIn('_B_launch_phase_ready',ops)
  self.assertIn('_B_refresh_RSS_history',ops);self.assertIn('max_workers=1',ops)
  self.assertNotIn("command[1]='run-native'",ops)
  with self.assertRaises(e.Hold):e.derive_native(Path(pins['native']['path']).read_bytes()+b'\n')
  (HERE/'DERIVED_PRIVATE_NATIVE.CPU_PREVIEW.py').write_text(native)
  (HERE/'DERIVED_PRIVATE_OPS.CPU_PREVIEW.py').write_text(ops)
  (HERE/'EXACT_TRANSFORMS.CPU_PROOF.json').write_bytes(g.encoded(dict(native=nativeproof,ops=opsproof)))

if __name__=='__main__':unittest.main()
