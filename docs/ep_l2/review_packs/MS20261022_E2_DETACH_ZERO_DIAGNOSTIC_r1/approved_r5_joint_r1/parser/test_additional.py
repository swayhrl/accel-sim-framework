import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import decoder
from decoder import Feed,AuditError,OLD,PREFIX
from native_selected import validate_selected_old212
from test_controls import PACK,R4_SCHEMA,BIND,snapshot,scope,old_frame,old_result,encode,run

class NativeControls(unittest.TestCase):
 def make(self,globalbad=True):
  f=snapshot(registered=2);f[-1]['closure_ok']=not globalbad
  feed=Feed(expected_slices=[0],registered_slice_count=2,expected_kernels=[],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=BIND,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=False,allow_incomplete_native_global=True)
  # Explicit synthetic declarations, NOT actual native process evidence.
  raw=encode(f)+b'EPL2ROV1|SUMMARY|slice=0|detached=0|transactions=0|merges=0|responses=0\n'
  for line in raw.splitlines(keepends=True):feed.feed(line)
  sp=importlib.util.spec_from_file_location('r4_native_equations',PACK/'parser_recovery/decoder_samecycle_close.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  return feed,m,f
 def test_native_global_incomplete_scope_preserved(self):
  feed,m,f=self.make();old=validate_selected_old212(feed,m,R4_SCHEMA);r=feed.finish(old);self.assertEqual(r['status'],'VALID_R5_SELECTED_NATIVE_DECLARATIONS_ONLY',r);self.assertFalse(r['global_closure_declared']);self.assertFalse(r['global_epoch_closed_declared']);self.assertFalse(r['scientific_acceptance_granted']);self.assertFalse(old['unprinted_slice_records_synthesized'])
 def test_native_selected_malformed_old_equation_reject(self):
  feed,m,f=self.make();feed.old[('SLICE',0,-1,100)]['counters']['detach_success']=1
  with self.assertRaises(Exception):validate_selected_old212(feed,m,R4_SCHEMA)
 def test_native_independent_legacy_summary_wrong(self):
  feed,m,f=self.make();feed.old_summaries[(0,100)]['transactions']='1'
  with self.assertRaises(AuditError):validate_selected_old212(feed,m,R4_SCHEMA)
 def test_native_selected_old_missing_phase(self):
  feed,m,f=self.make();del feed.old[('PHASE',0,1,100)]
  with self.assertRaises(AuditError):validate_selected_old212(feed,m,R4_SCHEMA)
 def test_no_native_allow_global_relax_full(self):
  with self.assertRaises(AuditError):Feed(expected_slices=list(range(64)),registered_slice_count=64,expected_kernels=[],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=BIND,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=True,allow_incomplete_native_global=True)
 def test_native_helper_not_accept_general_old_invalid(self):
  feed,m,f=self.make();old=old_result(f,False);old['status']='INVALID';self.assertEqual(feed.finish(old)['status'],'INVALID_R5')

class ReauditControls(unittest.TestCase):
 def result(self):
  f=snapshot(n=64);r=run(f,n=64,full=True,synth=False);self.assertEqual(r['status'],'VALID_R5_OBSERVER_DECLARATIONS_ONLY',r);return r,old_result(f,False)
 def test_full64_normalized_reaudit(self):r,old=self.result();self.assertEqual(decoder.audit_normalized_result(r,old)['status'],'NORMALIZED_R5_MATH_SCOPE_VALID_ONLY')
 def test_normalized_slice_label_cannot_lie(self):
  r,old=self.result();r['slice_records']['63']['slice']=62
  with self.assertRaises(AuditError):decoder.audit_normalized_result(r,old)
 def test_normalized_phase_label_cannot_lie(self):
  r,old=self.result();r['phase_records']['63:1']['phase']=0
  with self.assertRaises(AuditError):decoder.audit_normalized_result(r,old)
 def test_normalized_missing_old_projection(self):
  r,old=self.result();r['old212_scope_projection'].pop()
  with self.assertRaises(AuditError):decoder.audit_normalized_result(r,old)
 def test_normalized_na_not_zero(self):
  r,old=self.result();r['phase_records']['0:0']['histograms'].pop('ways_raw_reserved_predmask')
  with self.assertRaises(AuditError):decoder.audit_normalized_result(r,old)
 def test_phase_uid_bool_rejected_even_uid0(self):
  f=snapshot(catalog=[0]);f[3]['kernel_uid']=False;self.assertEqual(run(f)['status'],'INVALID_R5')
 def test_old4_source_cannot_bind_new_prod(self):
  b=copy.deepcopy(BIND);b['core_source_commit']=decoder.CONTRACT['base_core']
  with self.assertRaises(AuditError):Feed(expected_slices=list(range(64)),registered_slice_count=64,expected_kernels=[],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=b,old212_decoder_sha256=decoder.FIXED_R4_SHA256)

if __name__=='__main__':unittest.main(verbosity=2)
