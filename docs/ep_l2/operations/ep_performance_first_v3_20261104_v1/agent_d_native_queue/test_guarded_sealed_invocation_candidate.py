import errno,fcntl,hashlib,json,os,tempfile,unittest
from pathlib import Path
import safe_native_candidate as c
import guarded_sealed_invocation_candidate as g
O=Path(__file__).parent
def ref(p):return dict(path=str(p),sha256=c.digest(p.read_bytes()))
class Invocation(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.t=Path(self.tmp.name)
  self.base=O/"shared_native_preimage.sh"
  self.grant=O/"FOREIGN_FINITE_INSERT_GRANT_CANDIDATE.json"
  self.shared=self.t/"shared";self.shared.write_bytes((O/"shared_native_reviewed_current.sh").read_bytes())
  self.entry=self.t/"entry";self.entry.write_bytes(g.CPU_STUB);self.entry_ref=ref(self.entry)
  self.env=dict(os.environ,EP_CPU_STUB_TOKEN="alpha beta",EP_CPU_STUB_EXTRA="line1\nline2")
 def tearDown(self):self.tmp.cleanup()
 def prepare(self):return g.prepare(str(self.shared),ref(self.base),ref(self.grant),self.entry_ref)
 def result(self,p,args=[]):
  r=g.invoke_cpu_stub(p,args,self.env);self.assertEqual(r.returncode,0,r.stderr)
  z=json.loads(r.stdout);self.assertEqual(z["marker"],"APPROVED_SEALED_CPU_STUB");return z
 def test_positive_current_foreign_route(self):
  with self.prepare() as p:
   self.assertEqual(p.shared_route_status,"EXACT_REVIEWED_FOREIGN_INSERT");self.result(p)
 def test_shared_swap_after_validation_never_redirects(self):
  with self.prepare() as p:
   # A malicious shared shell is never executed, even after a successful route review.
   self.shared.write_bytes(b"#!/bin/sh\necho MALICIOUS_ROUTE\nexit 77\n")
   self.result(p)
 def test_EP_mutation_before_pin_rejected(self):
  self.entry.write_bytes(g.CPU_STUB+b"\n# mutation\n")
  with self.assertRaises(c.Hold):self.prepare()
 def test_global_EP_route_mutation_before_pin_rejected(self):
  self.shared.write_bytes(self.shared.read_bytes().replace(b"EP_PERF_*",b"EP_EVIL_*"))
  with self.assertRaises(c.Hold):self.prepare()
 def test_entry_atomic_replacement_after_pin_uses_sealed_bytes(self):
  with self.prepare() as p:
   q=self.t/"replacement";q.write_bytes(b"#!/bin/sh\necho REPLACED_ENTRY\nexit 78\n")
   os.replace(q,self.entry);self.result(p)
 def test_entry_same_inode_mutation_after_pin_uses_sealed_bytes(self):
  with self.prepare() as p:
   self.entry.write_bytes(b"#!/bin/sh\necho MUTATED_ENTRY\nexit 79\n");self.result(p)
 def test_memfd_cannot_be_modified_or_shrunk(self):
  with self.prepare() as p:
   self.assertEqual(fcntl.fcntl(p.fd,fcntl.F_GET_SEALS),g.SEALS)
   with self.assertRaises(OSError)as ctx:os.pwrite(p.fd,b"EVIL",0)
   self.assertEqual(ctx.exception.errno,errno.EPERM)
   with self.assertRaises(OSError):os.ftruncate(p.fd,0)
   self.result(p)
 def test_argv_environment_preserved_no_shell_expansion(self):
  with self.prepare() as p:
   args=["experiment","run-native","EP_CPU_ONLY_STUB","--project","EP_L2",
    "space value","; exit 80","$(touch "+str(self.t/"NEVER")+")","line1\nline2","\u03bb"]
   z=self.result(p,args);self.assertEqual(z["argv"],args)
   self.assertEqual(z["token"],self.env["EP_CPU_STUB_TOKEN"])
   self.assertEqual(z["extra"],self.env["EP_CPU_STUB_EXTRA"])
   self.assertFalse((self.t/"NEVER").exists())
 def test_nonstub_scientific_entry_never_invocable_by_fixture(self):
  # Prepare arbitrary inert bytes to prove execution requires the exact harmless body.
  self.entry.write_bytes(b"#!/bin/sh\necho NONSTUB\n")
  self.entry_ref=ref(self.entry)
  with self.prepare() as p:
   with self.assertRaises(c.Hold):g.invoke_cpu_stub(p,[],self.env)
 def test_closed_handle_not_executable(self):
  p=self.prepare();p.close()
  with self.assertRaises(c.Hold):g.invoke_cpu_stub(p,[],self.env)
 def test_foreign_grant_unknown_or_replaced_rejected(self):
  z=json.loads(self.grant.read_text());z["frontend_ref"]["sha256"]="0"*64
  bad=self.t/"grant";bad.write_text(json.dumps(z))
  with self.assertRaises(c.Hold):g.prepare(str(self.shared),ref(self.base),ref(bad),self.entry_ref)
 def test_base_or_scoped_ref_symlink_failclosed(self):
  q=self.t/"entry_link";q.symlink_to(self.entry)
  with self.assertRaises(OSError):g.prepare(str(self.shared),ref(self.base),ref(self.grant),ref(q))
if __name__=="__main__":unittest.main(verbosity=2)
