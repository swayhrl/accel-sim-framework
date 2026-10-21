"""Bounded synthetic classification controls, never native qualification."""
import ast,copy,importlib.util,pathlib,sys,tempfile,unittest
P=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('new_tag_capacity_validation',P/'candidate/capacity_validation.py');cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
# Reuse the already inspected synthetic full-summary fixture, never native raw.
tree=ast.parse((P.parent.parent/'acceptance_preparation/test_capacity_validation.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='example');g=dict(copy=copy,AUTHORITY=cv.AUTHORITY,SLICE_ZERO=cv.SLICE_ZERO);exec(compile(ast.Module(body=[node],type_ignores=[]),'<synthetic-summary>','exec'),g)
def example():
 s,i,q=g['example']();old=s['profile'];s['profile']=cv.ON;q['profiles'][cv.ON]=q['profiles'].pop(old)
 off,_,oq=g['example'](0);q['profiles'][cv.OFF]=oq['profiles'][off['profile']]
 q['source_identity']['vendor_pybind11_commit']='5'*40;q['input_selection_id']='D_V1_convolutionSeparable'
 for row in s['capacity_diagnostic']['slices'].values():
  for resource in row['resources'].values():resource.update(coverage_kind='EXACT_EVENT_HIGHWATER')
  row['resources']['tag_slots'].update(valid_victim_replacements=0,replacement_counter_covered=True,replacement_breakdown=dict(timed_clean=0,timed_dirty=0,host_prefill_clean=0),replacement_scope='SUCCESSFUL_VALID_VICTIM_REPLACEMENTS')
 return s,i,q

class Controls(unittest.TestCase):
 def tag(self,s):return s['capacity_diagnostic']['slices']['0']['resources']['tag_slots']
 def test_complete_zero_replacement_allows_near(self):self.assertTrue(cv.validate_summary(*example())['capacity_classification']['near_unbounded'])
 def test_low_global_hwm_timed_clean_is_valid_finite(self):
  s,i,q=example();r=self.tag(s);r['highwater']=1;r['valid_victim_replacements']=1;r['replacement_breakdown']['timed_clean']=1
  result=cv.validate_summary(s,i,q);self.assertEqual(result['status'],'PASS');self.assertEqual(result['capacity_classification']['label'],'LARGE_FINITE')
 def test_timed_dirty_valid_finite(self):
  s,i,q=example();r=self.tag(s);r['valid_victim_replacements']=1;r['replacement_breakdown']['timed_dirty']=1
  self.assertEqual(cv.validate_summary(s,i,q)['capacity_classification']['label'],'LARGE_FINITE')
 def test_hostprefill_valid_finite_not_timed_stall(self):
  s,i,q=example();r=self.tag(s);r['valid_victim_replacements']=1;r['replacement_breakdown']['host_prefill_clean']=1
  c=cv.validate_summary(s,i,q)['capacity_classification'];self.assertEqual(c['label'],'LARGE_FINITE');self.assertIn('not a timed GPU stall',c['binding_resources'][0]['interpretation'])
 def test_observed_replacement_even_incomplete_othercoverage_finite(self):
  s,i,q=example();r=self.tag(s);r['valid_victim_replacements']=1;r['replacement_breakdown']['host_prefill_clean']=1;r['replacement_counter_covered']=False;r['counter_covered']=False
  self.assertEqual(cv.validate_summary(s,i,q)['capacity_classification']['label'],'LARGE_FINITE')
 def test_missing_replacement_unknown(self):
  s,i,q=example();r=self.tag(s);r['valid_victim_replacements']=None;r['replacement_breakdown']=None
  self.assertEqual(cv.validate_summary(s,i,q)['capacity_classification']['label'],'UNKNOWN')
 def test_zero_incomplete_replacement_coverage_unknown(self):
  s,i,q=example();self.tag(s)['replacement_counter_covered']=False
  self.assertEqual(cv.validate_summary(s,i,q)['capacity_classification']['label'],'UNKNOWN')
 def test_wrong_scope_rejected(self):
  s,i,q=example();self.tag(s)['replacement_scope']='GLOBAL_LOW_OCCUPANCY'
  with self.assertRaises(ValueError):cv.validate_summary(s,i,q)
 def test_mismatched_provenance_rejected(self):
  s,i,q=example();self.tag(s)['replacement_breakdown']['timed_clean']=1
  with self.assertRaises(ValueError):cv.validate_summary(s,i,q)
 def test_negative_count_rejected(self):
  s,i,q=example();self.tag(s)['valid_victim_replacements']=-1
  with self.assertRaises(ValueError):cv.validate_summary(s,i,q)
 def test_no_duplicate_definitions(self):
  t=ast.parse((P/'candidate/capacity_validation.py').read_text());names=[x.name for x in t.body if isinstance(x,ast.FunctionDef)];self.assertEqual(len(names),len(set(names)))

if __name__=='__main__':unittest.main()
