import concurrent.futures, copy, hashlib, json, os, tempfile, threading, unittest
from pathlib import Path
import safe_native_candidate as c
ROOT=Path(__file__).parent
class Native(unittest.TestCase):
 def setUp(self):
  self.base=(ROOT/'shared_native_preimage.sh').read_bytes()
  self.current=(ROOT/'shared_native_reviewed_current.sh').read_bytes()
  self.grant=json.loads((ROOT/'FOREIGN_FINITE_INSERT_GRANT_CANDIDATE.json').read_text())
 def test_exact_and_authorized_insert(self):
  self.assertEqual(c.validate_global(self.base,self.base),"EXACT_BASE")
  self.assertEqual(c.validate_global(self.current,self.base,self.grant),"EXACT_REVIEWED_FOREIGN_INSERT")
  self.assertTrue(c.validate_grant(self.grant))
 def test_whole_route_mutation_deletion_replacement(self):
  for bad in [self.current.replace(b'EP_PERF_*',b'EP_EVIL_*'), self.current[:-1],
    self.current.replace(b'ep_perf_frontend.py',b'ep_fake_frontend.py'),
    self.current+b'exit 0\n', self.current.replace(b'EP_FULL_PERF_NATIVE_ENTRY=1',b'EP_FULL_PERF_NATIVE_ENTRY=0')]:
   with self.assertRaises(c.Hold):c.validate_global(bad,self.base,self.grant)
 def test_shadow_and_general_insert_rejected(self):
  for block in [b'exit 0\n',b'exec /bin/true "$@"\n',
    b'case "$3" in EP_*) exec /bin/true;; esac\n',
    b'export PYTHONPATH=/tmp/inject\n',b'. /tmp/evil\n',
    b'trap "exit 0" EXIT\n',b'cd /tmp\n',b'# harmless but unreviewed\n']:
   bad=c.HEADER+block+self.current[len(c.HEADER):]
   with self.assertRaises(c.Hold):c.validate_global(bad,self.base,self.grant)
 def test_no_grant_no_broad_insertion(self):
  with self.assertRaises(c.Hold):c.validate_global(self.current,self.base)
 def test_foreign_namespaces_duplicates_wildcards(self):
  for case in ['EP_PERF_TEST','E2-DTC2A48-*','E2-DTC2A48-abcdef0123456789-CH-F128-V1;id','*']:
   x=copy.deepcopy(self.grant);x['cohorts']=[case]
   with self.assertRaises(c.Hold):c.render_foreign(x)
  x=copy.deepcopy(self.grant);x['cohorts']*=2
  with self.assertRaises(c.Hold):c.render_foreign(x)
 def test_handler_authority_scope_pins(self):
  for key in ['authorization_ref','science_authorization_ref','frontend_ref']:
   x=copy.deepcopy(self.grant);x[key]['sha256']='0'*64
   with self.assertRaises(c.Hold):c.validate_grant(x)
  x=copy.deepcopy(self.grant);x['approved_commit']='f'*40
  with self.assertRaises(c.Hold):c.validate_grant(x)
  x=copy.deepcopy(self.grant);x['cohorts']=x['cohorts'][:-1]
  with self.assertRaises(c.Hold):c.validate_grant(x)
 def test_finite_route_no_EP_overlap(self):
  # Exact foreign labels do not match any protected EP cohort; no glob is permitted.
  import re,fnmatch,subprocess
  eps=set(re.findall(r'EP_[A-Z0-9_]+',self.base.decode()))
  patterns=[verb+':'+x for x in self.grant['cohorts'] for verb in ['experiment','result']]
  self.assertTrue(eps)
  for ep in eps:
   for verb in ['experiment','result']:
    self.assertFalse(any(fnmatch.fnmatchcase(verb+':'+ep,p) for p in patterns))
  # Execute only finite reviewed foreign prefix + inert fallback, never shared Native.
  inert=c.HEADER+c.render_foreign(self.grant)+b'printf "EP_FALLTHROUGH\\n"\n'
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'prefix';f.write_bytes(inert)
   for ep in sorted(eps):
    for op in ['prepare','inspect','run-native','accept']:
     out=subprocess.check_output(['/bin/sh',str(f),'experiment',op,ep,'--project','EP_L2'],text=True)
     self.assertEqual(out.strip(),'EP_FALLTHROUGH')
 def test_scoped_Source5_input_spec_frontend(self):
  x=json.loads((ROOT/'SCOPED_IDENTITY_CPU_FIXTURE.json').read_text())
  entry=Path(x['entry_ref']['path']).read_bytes();spec=Path(x['spec_ref']['path']).read_bytes()
  runtime=Path(x['runtime_ref']['path']).read_bytes()
  self.assertTrue(c.validate_scoped(entry,x['entry_ref']['sha256'],x['binding'],spec,runtime))
  for name in ['source_identity','input_identity_sha256','cohort']:
   binding=copy.deepcopy(x['binding'])
   binding[name]={} if name=='source_identity' else 'wrong'
   with self.assertRaises(c.Hold):c.validate_scoped(entry,x['entry_ref']['sha256'],binding,spec,runtime)
  for e,s,r in [(entry+b'\n',spec,runtime),(entry,spec+b' ',runtime),(entry,spec,runtime+b' ')]:
   with self.assertRaises(c.Hold):c.validate_scoped(e,x['entry_ref']['sha256'],x['binding'],s,r)
 def test_TOCTOU_same_bytes_atomic_replace(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'artifact';p.write_bytes(b'approved')
   b,token=c.stable_read(p);snap=[dict(path=str(p),sha256=c.digest(b),token=token)]
   q=Path(t)/'replacement';q.write_bytes(b'approved');os.replace(q,p)
   with self.assertRaises(c.Hold):c.recheck(snap)
 def test_TOCTOU_concurrent_mutation_and_snapshot(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'artifact';p.write_bytes(b'approved')
   b,token=c.stable_read(p);snap=[dict(path=str(p),sha256=c.digest(b),token=token)]
   th=threading.Thread(target=lambda:p.write_bytes(b'evil'));th.start();th.join()
   with self.assertRaises(c.Hold):c.recheck(snap)
   self.assertEqual(b,b'approved') # consume must use frozen bytes, never reread pathname
 def test_symlink_and_oversize(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'f';p.write_bytes(b'content');q=Path(t)/'link';q.symlink_to(p)
   with self.assertRaises(OSError):c.stable_read(q)
   with self.assertRaises(c.Hold):c.stable_read(p,limit=2)
 def test_concurrent_readonly_validation(self):
  def run(_):return c.validate_global(self.current,self.base,self.grant)
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
   self.assertTrue(all(x=='EXACT_REVIEWED_FOREIGN_INSERT' for x in ex.map(run,range(800))))
class Resources(unittest.TestCase):
 def setUp(self):self.kw=dict(active_ep=0,available_ram=100,cgroup_remaining=100,new_ram=10,
  pending_growth=20,ssd_free=100,new_writes=10,committed_writes=20,restore_increment=5,
  foreign_floor=5,emergency=1,unknown_owner=False,scope_authorized=True)
 def test_pass_and_local_holds(self):
  self.assertTrue(c.admission_math(**self.kw)[0])
  for changed in [dict(active_ep=2),dict(available_ram=20),dict(cgroup_remaining=20),
    dict(ssd_free=20),dict(foreign_floor=70),dict(unknown_owner=True),dict(scope_authorized=False)]:
   self.assertFalse(c.admission_math(**dict(self.kw,**changed))[0])
 def test_loader_models_exclude_strace_wrapper(self):
  elf="/a/accel-sim.out";loader="/a/ld-linux-x86-64.so.2"
  self.assertEqual(c.classify_simulator_argv([elf,"-trace","x"]),"MODEL_CANDIDATE")
  self.assertEqual(c.classify_simulator_argv([loader,"--library-path","lib",elf,"-trace","x"]),"MODEL_CANDIDATE")
  self.assertEqual(c.classify_simulator_argv([loader,"/a/strace","--",loader,elf]),"WRAPPER_NOT_MODEL")
  self.assertEqual(c.classify_simulator_argv(["python3","tool.py"]),"NOT_MODEL")
 def test_no_double_charge_existing_bytes(self):
  # Inputs are future increments; current usage is already reflected by available/df.
  self.assertTrue(c.admission_math(**dict(self.kw,ssd_free=40))[0])
 def test_unbounded_negative_rejected(self):
  with self.assertRaises(c.Hold):c.admission_math(**dict(self.kw,new_writes=-1))
 def test_single_owner_atomic_claim_cap2_no_retry(self):
  lock=threading.Lock();active=set();consumed=set();seen=[];terminal=[]
  def claim(i):
   with lock:
    if i in consumed or not c.admission_math(**dict(self.kw,active_ep=len(active)))[0]:return False
    consumed.add(i);active.add(i);seen.append(len(active));return True
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
   got=list(ex.map(claim,[0,0,1,2,3,4]))
  self.assertEqual(sum(got),2);self.assertEqual(max(seen),2)
  with lock:terminal.extend(active);active.clear()
  self.assertFalse(claim(0)) # failed or accepted terminal is still consumed, no retry/refund
  self.assertEqual(len(consumed),2)
if __name__=='__main__':unittest.main(verbosity=2)
