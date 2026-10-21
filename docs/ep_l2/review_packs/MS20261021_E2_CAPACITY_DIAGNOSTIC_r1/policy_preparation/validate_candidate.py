"""Bounded synthetic policy controls. Never uses canonical Coordinator writes."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'candidate_runtime'))
import capacity_policy as p
import coordinator as c
import policy_v2

ORIGINAL=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
CANONICAL_BEFORE=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
BASE=json.loads(ORIGINAL.read_bytes())[c.FIELD]

class Controls(unittest.TestCase):
 def setUp(self):self.item=copy.deepcopy(BASE)
 def adopt(self):return p.amend(self.item,HERE/'USER_APPROVAL.json',1792576500)
 def test_exact_original_ledger_preserved(self):
  before=copy.deepcopy(self.item);self.assertTrue(self.adopt())
  for k in ('attempts','accepted_results','accepted_pairs','qualifications','input_selections',
            'scientific_holds','t0_unix','full_system_matrix','final_source_identity','workspace_disk_policy'):
   self.assertEqual(before.get(k),self.item.get(k),k)
  self.assertEqual({k:v for k,v in self.item['reservations'].items() if k!=p.BUCKET},before['reservations'])
  self.assertEqual(self.item['actual_starts'],36);c.counts(self.item)
  self.assertEqual(self.item['remaining_start_capacity'],10)
 def test_idempotent(self):
  self.adopt();after=copy.deepcopy(self.item);self.assertFalse(self.adopt());self.assertEqual(after,self.item)
 def test_old_adopt_v2_is_safe_after_capacity(self):
  self.adopt();self.assertFalse(policy_v2.amend(self.item,1792576600))
 def test_reject_cap_47(self):
  self.adopt();self.item['maximum_actual_starts']=47
  with self.assertRaisesRegex(ValueError,'limits changed'):p.effective_limits(self.item)
 def test_reject_result_11g(self):
  self.adopt();self.item['additional_results_max_bytes']=11*p.GIB
  with self.assertRaisesRegex(ValueError,'limits changed'):p.effective_limits(self.item)
 def test_reject_deadline_extension(self):
  self.adopt();self.item['intake_deadline_unix']+=1
  with self.assertRaisesRegex(ValueError,'limits changed'):p.effective_limits(self.item)
 def test_reject_old_contingency_expansion(self):
  self.adopt();self.item['reservations']['contingency']+=1
  with self.assertRaisesRegex(ValueError,'old allocation'):p.effective_limits(self.item)
 def test_reject_new_bucket_11(self):
  self.adopt();self.item['reservations'][p.BUCKET]=11
  with self.assertRaisesRegex(ValueError,'exactly ten'):p.effective_limits(self.item)
 def test_no_refund_or_new_counter(self):
  self.item['actual_starts']=35
  with self.assertRaisesRegex(ValueError,'charged36'):self.adopt()
 def test_running_original_controller_blocks(self):
  self.item['controller']['state']='ACTIVE'
  with self.assertRaisesRegex(ValueError,'safe boundary'):self.adopt()
 def test_uncertain_original_attempt_blocks(self):
  self.item['attempts'][0]['state']='START_INTENT_UNRECONCILED'
  with self.assertRaisesRegex(ValueError,'uncertain'):self.adopt()
 def test_46_global_actual_ceiling(self):
  self.adopt()
  self.item['attempts'] += [dict(actual_start=True,state='FAILED',budget_bucket=p.BUCKET) for _ in range(10)]
  c.counts(self.item);self.assertEqual(self.item['remaining_start_capacity'],0)
  self.item['attempts'].append(dict(actual_start=True,state='FAILED',budget_bucket=p.BUCKET))
  with self.assertRaisesRegex(ValueError,'46 actual'):c.counts(self.item)
 def test_no_11th_capacity_slot_even_if_global_remaining(self):
  self.adopt();self.item['attempts']=[dict(actual_start=True,state='FAILED',budget_bucket=p.BUCKET) for _ in range(10)]
  with self.assertRaisesRegex(ValueError,'ten actual'):p.bucket_guard(self.item,dict(budget_bucket=p.BUCKET))
 def test_original40_cannot_borrow_new10(self):
  self.adopt();self.item['attempts']=[dict(actual_start=True,state='FAILED',budget_bucket='contingency') for _ in range(40)]
  with self.assertRaisesRegex(ValueError,'cannot borrow'):p.bucket_guard(self.item,dict(budget_bucket='contingency'))
 def test_original_unstarted_four_frozen_for_this_batch(self):
  self.adopt()
  with self.assertRaisesRegex(ValueError,'old unstarted four frozen'):p.bucket_guard(self.item,dict(budget_bucket='contingency'))
 def test_exact_five_inputs_ten_unique_conditions(self):
  rows=p.matrix()['conditions'];self.assertEqual(len(rows),10)
  self.assertEqual(len({r['condition_id'] for r in rows}),10)
  self.assertEqual({r['workload'] for r in rows},set(p.INPUTS))
 def test_no_qualification_means_no_condition(self):
  self.adopt();r=p.matrix()['conditions'][0]
  s=dict(r,identity=dict(workload=r['workload'],trace_content_sha256=r['trace_content_sha256'],
      epoch_range={'epochs':'all','scope':'full_application'}),qualification_id='NOT_QUALIFIED')
  with self.assertRaises(KeyError):p.condition_check(self.item,s,c.digest)
 def test_old_main61_qualification_cannot_be_inherited(self):
  q=dict(capacity_diagnostic=dict(authority_commit=p.AUTHORITY,master_option=p.MASTER),
         source_identity=dict(binary_sha256=p.MAIN61))
  with self.assertRaisesRegex(ValueError,'main61'):p.qualification(q,c.digest)
 def test_existing_qualification_not_capacity_grant(self):
  q=next(iter(self.item['qualifications'].values()))['qualification']
  with self.assertRaisesRegex(ValueError,'contract missing'):p.qualification(q,c.digest)
 def test_old_default_limit_still_closed_original_day(self):
  self.assertEqual(p.effective_limits(self.item)['start_deadline_unix'],1792576800)
 def test_pinned_approval_bytes_only(self):
  with tempfile.TemporaryDirectory(prefix='e2_capacity_control_') as d:
   bad=Path(d)/'changed.json';bad.write_text('{}')
   with self.assertRaisesRegex(ValueError,'bytes changed'):p.amend(self.item,bad,1792576500)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
 after=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
 report=dict(status='PASS' if result.wasSuccessful() else 'FAIL',bounded_synthetic_controls=True,
   tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
   complete_application_starts=0,native_tests=0,controller_actions=0,registry_writes=0,
   canonical_registry_before_sha256=CANONICAL_BEFORE,canonical_registry_after_sha256=after,
   canonical_registry_unchanged=CANONICAL_BEFORE==after,
   qualifier='Synthetic controls validate engineering guards only, never native correctness or scientific qualification')
 (HERE/'BOUNDED_CONTROL_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
 sys.exit(0 if result.wasSuccessful() else 1)
