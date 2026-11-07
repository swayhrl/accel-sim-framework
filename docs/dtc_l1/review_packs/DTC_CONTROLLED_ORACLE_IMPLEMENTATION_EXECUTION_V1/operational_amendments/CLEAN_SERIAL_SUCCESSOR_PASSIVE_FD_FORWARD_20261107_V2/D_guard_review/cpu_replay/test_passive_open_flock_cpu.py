"""Real temporary multi-process FLOCK fixtures; no production locks/processes."""
from pathlib import Path
import fcntl,importlib.util,json,os,subprocess,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=='--peer':
 paths=json.loads(sys.argv[2]);handles=[open(p,'r+b')for p in paths]
 mode=sys.argv[3]
 if mode!='PASSIVE':fcntl.flock(handles[0],(fcntl.LOCK_SH if mode=='SH'else fcntl.LOCK_EX)|fcntl.LOCK_NB)
 print('READY',flush=True)
 for command in sys.stdin:
  command=command.strip()
  if command=='EXIT':break
  successes=[]
  for h in handles:
   try:
    fcntl.flock(h,(fcntl.LOCK_SH if command=='SH'else fcntl.LOCK_EX)|fcntl.LOCK_NB)
    successes.append(True);fcntl.flock(h,fcntl.LOCK_UN)
   except BlockingIOError:successes.append(False)
  print(json.dumps(successes),flush=True)
 for h in handles:h.close()
 raise SystemExit(0)
s=importlib.util.spec_from_file_location('CPU_GUARD_V2',HERE/'oracle_clean_owner_guard.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
class PassiveFDTests(unittest.TestCase):
 def test_unlocked_reference_is_not_permission_or_owner(self):
  row=dict(pid=111,fd=3,path='TEMP_ONLY',fdinfo='pos: 0\nino: 1\n')
  v=g.classify_open_references([row],222)
  self.assertEqual(v['passive_unlocked_open_references'],[row]);self.assertTrue(v['passive_FDs_confer_no_scientific_permission'])
 def test_any_foreign_lock_record_is_hold(self):
  for text in ['lock: 1: FLOCK ADVISORY READ 111 00:01:2 0 EOF','lock: 1: FLOCK ADVISORY WRITE 111 00:01:2 0 EOF','lock: unknown','lock: 1: POSIX ADVISORY WRITE 111 00:01:2 0 EOF']:
   with self.assertRaises(g.Hold):g.classify_open_references([dict(pid=111,fdinfo=text)],222)
 def fixture(self,mode):
  with tempfile.TemporaryDirectory(prefix='DTC_ONLY_MOCK_PASSIVE_FLOCK_')as d:
   paths={k:str(Path(d)/(k+'.lock'))for k in ['governance','owner','qualification','shared']}
   for p in paths.values():Path(p).write_bytes(b'CPU_FIXTURE_ONLY')
   identities={k:(Path(p).stat().st_dev,Path(p).stat().st_ino)for k,p in paths.items()}
   old=(g.FIXED_LOCK_PATHS,g.FIXED_LOCK_IDENTITIES,g.retired_processes)
   # Fixture scope only: same frozen guard bytes, genuine kernel operations on
   # temporary files. No production paths or target process are operated.
   g.FIXED_LOCK_PATHS=paths;g.FIXED_LOCK_IDENTITIES=identities;g.retired_processes=lambda *a:[]
   peer=subprocess.Popen(['/usr/bin/python3','-B',str(Path(__file__).resolve()),'--peer',json.dumps(list(paths.values())),mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
   try:
    self.assertEqual(peer.stdout.readline().strip(),'READY')
    if mode=='PASSIVE':
     with g.CleanMainLocks(paths)as locks:
      self.assertEqual(len(locks.references),4)
      self.assertEqual(len(locks.bootstrap_open_reference_evidence['before']['passive_unlocked_open_references']),4)
      for request in ['EX','SH']:
       peer.stdin.write(request+'\n');peer.stdin.flush();self.assertEqual(json.loads(peer.stdout.readline()),[False]*4)
      for row in locks.references:g.verify_lock(row,os.getpid())
     peer.stdin.write('EX\n');peer.stdin.flush();self.assertEqual(json.loads(peer.stdout.readline()),[True]*4)
    else:
     held=g.CleanMainLocks(paths)
     with self.assertRaises(g.Hold):held.__enter__()
     self.assertEqual(held.handles,[])
     refs=g.all_references(paths.values());self.assertTrue(any('FLOCK'in x['fdinfo']for x in refs if x['pid']==peer.pid))
   finally:
    peer.stdin.write('EXIT\n');peer.stdin.flush();out,err=peer.communicate(timeout=10)
    g.FIXED_LOCK_PATHS,g.FIXED_LOCK_IDENTITIES,g.retired_processes=old
    self.assertEqual(peer.returncode,0,err)
 def test_passive_peer_all_four_FDs_cannot_lock_during_real_EX(self):self.fixture('PASSIVE')
 def test_foreign_shared_lock_refused_without_touching_peer(self):self.fixture('SH')
 def test_foreign_exclusive_lock_refused_without_touching_peer(self):self.fixture('EX')
 def test_partial_acquisition_failure_releases_only_our_FDs(self):
  with tempfile.TemporaryDirectory(prefix='DTC_ONLY_MOCK_PARTIAL_FLOCK_')as d:
   paths={k:str(Path(d)/(k+'.lock'))for k in ['governance','owner','qualification','shared']}
   for p in paths.values():Path(p).write_bytes(b'MOCK')
   old=(g.FIXED_LOCK_PATHS,g.FIXED_LOCK_IDENTITIES,g.retired_processes,g.all_references)
   g.FIXED_LOCK_PATHS=paths;g.FIXED_LOCK_IDENTITIES={k:(Path(p).stat().st_dev,Path(p).stat().st_ino)for k,p in paths.items()};g.retired_processes=lambda *a:[]
   foreign=open(paths['shared'],'r+b');fcntl.flock(foreign,fcntl.LOCK_EX|fcntl.LOCK_NB)
   # Explicitly simulate a lock taken after pre-scan; true kernel NB acquisition
   # must still fail and clean only the candidate's partial descriptors.
   g.all_references=lambda *a:[];obj=g.CleanMainLocks(paths)
   try:
    with self.assertRaises(BlockingIOError):obj.__enter__()
    self.assertEqual(obj.handles,[])
    g.lock_record(Path('/proc/self/fdinfo/'+str(foreign.fileno())).read_text(),os.getpid(),os.fstat(foreign.fileno()).st_dev,os.fstat(foreign.fileno()).st_ino)
    for role in ['governance','owner','qualification']:
     with open(paths[role],'r+b')as h:fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
   finally:
    foreign.close();g.FIXED_LOCK_PATHS,g.FIXED_LOCK_IDENTITIES,g.retired_processes,g.all_references=old
if __name__=='__main__':unittest.main()
