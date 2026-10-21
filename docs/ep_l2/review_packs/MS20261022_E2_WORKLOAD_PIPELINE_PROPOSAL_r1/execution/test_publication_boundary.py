"""Bounded temporary metadata controls; not scientific/native qualification."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,tempfile,types,unittest
E=Path(__file__).resolve().parent;P=E.parent;ROOT=P.parents[3]
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
# Candidate policy is used only in this isolated process; no active tool edit.
if not (ROOT/'util/ep_l2/mechanism_e/workload_policy.py').exists():load('workload_policy',P/'central_adoption/candidate/workload_policy.py')
r=load('publication_under_test',E/'report.py')
class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='epl2-workload-publication-control-');self.t=Path(self.tmp.name)
  self.originals={k:getattr(r,k) for k in ('E','P','ROOT')};r.E=self.t/'pack/execution';r.P=self.t/'pack';r.ROOT=self.t;r.E.mkdir(parents=True)
  self.saved={k:getattr(r.c,k) for k in ('Coordinator','output_usage','local_resources','SHARED','HANDOFF')}
  self.active=r.policy.active;self.validator=r.runner.validate_terminal_summary;r.policy.active=lambda s:True
  r.c.SHARED=self.t/'shared';r.c.SHARED.mkdir();r.c.HANDOFF=self.t/'handoff';r.c.HANDOFF.mkdir()
  (self.t/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e').mkdir(parents=True)
  (r.c.SHARED/'RUN_REGISTRY.json').write_text(json.dumps(dict(runs={},resource_leases={})))
  self.d=self.t/'result';self.d.mkdir();self.q=self.t/'Q.json';self.q.write_text('{}')
  self.n=dict(exit_code=0,wait_status=0,stop_reason=None,native_process=dict(pid=1,start_ticks=2,boot_id='control'))
  self.x=dict(attempt_id='NEW',status='COMPLETE_VALID',independent_acceptance='PASS',complete_input_verified=True,
   source_identity={'binary_sha256':r.policy.MAIN61},selection_id='INPUT',summary=dict(instructions=100,slices=64,cycles=10),native_exit_evidence=self.n,
   process=self.n['native_process'],qualification_id='Q',validation=dict(status='PASS'),input_audit={},profile='S',labels={})
  for name,value in [('NATIVE_EXIT.json',self.n),('input_spec.json',{}),('terminal_summary.json',self.x['summary'])]:
   (self.d/name).write_text(json.dumps(value))
  (self.d/'raw.log').write_text('bounded synthetic control\n');self.x['native_exit_receipt_sha256']=r.c.digest(self.d/'NATIVE_EXIT.json')
  self.pair=dict(pair_id='PAIR',status='CURRENT_ACCEPTED',endpoints={})
  self.s=dict(attempts=[{} for _ in range(46)]+[dict(attempt_id='NEW',condition_id='CID',state='COMPLETE_VALID',result_directory=str(self.d))],
   qualifications={'Q':dict(path=str(self.q),sha256=r.c.digest(self.q))},input_selections={'INPUT':dict(selection=dict(full_input_identity=dict(expected_full_instructions=100)))},
   accepted_pairs={'PAIR':self.pair},t0_unix=1792414193,actual_starts=47,remaining_start_capacity=None,reservations={},controller=dict(state='STOPPED'),additional_results_max_bytes=10*2**30,old_plus_new_results_max_bytes=24*2**30)
  self.plan=dict(pairs=[dict(pair_id='PAIR')],source_identity=self.x['source_identity'],conditions=[dict(condition_id='CID',qualification_id='Q')])
  r.c.Coordinator=lambda:types.SimpleNamespace(snapshot=lambda:self.s,require_no_hold=lambda s,q:None)
  r.c.output_usage=lambda:dict(new_bytes=100,total_bytes=200);r.c.local_resources=lambda:{}
  r.runner.validate_terminal_summary=lambda *a:dict(status='PASS')
 def tearDown(self):
  for k,v in self.originals.items():setattr(r,k,v)
  for k,v in self.saved.items():setattr(r.c,k,v)
  r.policy.active=self.active;r.runner.validate_terminal_summary=self.validator;self.tmp.cleanup()
 def collect(self):
  path=self.d/'run_status.json';path.write_text(json.dumps(self.x));self.pair['endpoints']={k:dict(path=str(path),sha256=r.c.digest(path)) for k in ('left','right')}
  return r.collect('CONTROL',self.plan,self.pair)
 def test_real_zero_closed_metadata(self):self.assertEqual(len(self.collect()[0]['accepted_pairs']),1)
 def test_exit_nonzero_denied(self):
  self.x['native_exit_evidence']=dict(self.n,exit_code=-15)
  with self.assertRaises(AssertionError):self.collect()
 def test_wait_nonzero_denied(self):
  self.x['native_exit_evidence']=dict(self.n,wait_status=-15)
  with self.assertRaises(AssertionError):self.collect()
 def test_pid_identity_changed_denied(self):
  self.x['process']=dict(pid=1,start_ticks=999,boot_id='control')
  with self.assertRaises(AssertionError):self.collect()
 def test_incomplete_instructions_denied(self):
  self.x['summary']['instructions']=99
  with self.assertRaises(AssertionError):self.collect()
 def test_wrong_binary_denied(self):
  self.x['source_identity']={'binary_sha256':'0'*64}
  with self.assertRaises(AssertionError):self.collect()
 def test_old_attempt_denied(self):
  self.x['attempt_id']='OLD'
  with self.assertRaises(AssertionError):self.collect()
 def test_scientific_validator_disagreement_denied(self):
  r.runner.validate_terminal_summary=lambda *a:dict(status='FAIL')
  with self.assertRaises(AssertionError):self.collect()
 def test_63slice_denied(self):
  self.x['summary']['slices']=63
  with self.assertRaises(AssertionError):self.collect()
if __name__=='__main__':unittest.main(verbosity=2)
