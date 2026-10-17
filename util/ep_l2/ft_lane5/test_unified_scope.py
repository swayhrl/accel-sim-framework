"""Hostile scope/reference mutations; unit coverage is not application qualification."""
import copy,json,tempfile,unittest
from pathlib import Path
from unified_scope import IDENTITY,expected,features,runtime_dump
from parse_all_data_terminal import references

REPO=Path(__file__).resolve().parents[3]
ACTUAL=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_UNIFIED_RUNTIME_AFFECTED_REPLAY_r1/independent_replay/ALL_DATA_native_ldst.log'

class UnifiedScopeTests(unittest.TestCase):
 def identity(self,profile):
  f,i=expected(profile);return {**IDENTITY,'feature_vector':f,'ideal_vector':i}
 def test_exact_finite_resource_boundaries(self):
  self.assertEqual(expected('S64')[0]['bypass_capacity'],80);self.assertEqual(expected('S64')[0]['static_wb_capacity'],64);self.assertEqual(expected('S64')[0]['payload_capacity_per_slice'],1168)
  self.assertEqual(expected('U_CAP16')[0]['wb_local_cap'],16);self.assertEqual(expected('P2_U_WB16')[0]['ops_per_bank_cycle'],2)
 def test_other_source_capacity_and_undeclared_combination_rejected(self):
  cases=[]
  for path,value in [('binary_sha256','0'*64),('bank_count',8),('payload_capacity_per_slice',1216),('wb_local_cap',17),('mem_all_data',True),('ro',True)]:
   x=self.identity('S64')
   if path=='binary_sha256':x[path]=value
   elif path=='mem_all_data':x['ideal_vector'][path]=value
   else:x['feature_vector'][path]=value
   cases.append(x)
  for x in cases:
   with self.assertRaises(ValueError):features(x,'S64')
  with self.assertRaises(ValueError):expected('I_BANK')
 def test_all_data_uses_explicit_physical_NA(self):
  x=self.identity('I_MEM_ALL_DATA');features(x,'I_MEM_ALL_DATA');self.assertIsNone(x['feature_vector']['bank_count']);self.assertEqual(x['feature_vector']['data_hierarchy'],'NOT_APPLICABLE');self.assertFalse(x['feature_vector']['numerical_SASS_output_validated'])
 def test_actual_native_reference_closes(self):
  r=references(ACTUAL);self.assertEqual(r['numeric_records']['MAIN']['instructions'],12);self.assertEqual(r['numeric_records']['MAIN']['requests'],11);self.assertEqual(r['measured_residual']['SM_register_writeback_wait_attempts'],1)
 def test_incomplete_store_request_snapshot_and_uid_fail_closed(self):
  source=ACTUAL.read_text()
  for old,new in [('pending_requests=0','pending_requests=1'),('store_reference_commits=2','store_reference_commits=1'),('native_stores_committed=2','native_stores_committed=1'),('consumed=11','consumed=10'),('original_instructions=12','original_instructions=13'),('duplicate_policy=FAIL_CLOSED','duplicate_policy=IGNORE')]:
   with self.subTest(old=old),tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'raw.log';self.assertIn(old,source);path.write_text(source.replace(old,new))
    with self.assertRaises(ValueError):references(path)
 def test_duplicate_reference_terminal_refused(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'raw.log';p.write_text(ACTUAL.read_text()*2)
   with self.assertRaises(ValueError):references(p)

class DerivedAnchorTests(unittest.TestCase):
 def test_extra_anchor_is_pinned_and_does_not_reset_seed_or_count(self):
  from test_parallel_registry import ParallelRegistry
  from test_lane5 import identity
  from registry import write_json
  import hashlib
  f=ParallelRegistry();f.setUp();self.addCleanup(f.tearDown)
  row=identity();row.update(IDENTITY,workload='vectorAdd_4M');row['feature_vector'],row['ideal_vector']=expected('B16_OFF')
  p=f.root/'anchor.json';write_json(p,{'identity':row});b={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  before=f.registry.snapshot();cell=f.registry.register_unified_vector_anchor(row,b);again=f.registry.register_unified_vector_anchor(row,b);after=f.registry.snapshot()
  self.assertEqual(cell,again);self.assertEqual(before['runs'],after['runs']);self.assertEqual(before['campaigns']['EPL2_PARALLEL_POTENTIAL_20261017_V1']['seed_cells'],after['campaigns']['EPL2_PARALLEL_POTENTIAL_20261017_V1']['seed_cells'])
  other=copy.deepcopy(row);other['trace_content_sha256']='8'*64
  with self.assertRaises(ValueError):f.registry.register_unified_vector_anchor(other,b)
if __name__=='__main__':unittest.main()
