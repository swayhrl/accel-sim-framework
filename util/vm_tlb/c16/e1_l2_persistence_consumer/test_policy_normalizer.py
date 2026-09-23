#!/usr/bin/env python3
from __future__ import annotations
import copy, unittest
from policy_normalizer import PolicyNormalizationError, normalize_raw_policy_receipt

Q=33_947_648; PTR=0x70000000
SHA_A='a'*64; SHA_B='b'*64

def capability():
 return {'status':'PASS','runtime_execution_authority':{'runtime_version':12040,'driver_version':13000,'device_ordinal':0,'device_name':'NVIDIA GeForce RTX 4080','l2_bytes':67_108_864,'max_persisting_l2_bytes':46_137_344,'max_access_policy_window_bytes':134_213_632},'runtime_matches_accepted':{'l2_bytes':True,'max_persisting_l2_bytes':True,'max_access_policy_window_bytes':True}}

def region():
 return {'bytes':Q,'contiguous':True,'data_ptr':PTR,'storage_nbytes':Q,'storage_offset_bytes':0,'storage_offset_elements':0,'exact_tensor_span_begin':PTR,'exact_tensor_span_end_exclusive':PTR+Q}

def operations(target=False):
 before=[{'operation':'clear stream access-policy before condition','status':0},{'operation':'reset persisting L2 before condition','status':0},{'operation':'set persisting-L2 limit','status':0}]
 if target: before.append({'operation':'set stream access-policy window','status':0})
 after=[{'operation':'clear stream access-policy after condition','status':0},{'operation':'reset persisting L2 after condition','status':0},{'operation':'clear persisting-L2 limit after condition','status':0}]
 return before,after

def carrier(condition='PERSIST_L0_UP',budget=Q,actual=None):
 target=condition not in {'BASELINE','SETASIDE_ONLY','ISO_BASELINE_DENSE'}
 if condition=='BUDGET_L0_UP': target=True
 if condition in {'BASELINE','ISO_BASELINE_DENSE'}: budget=0
 before,after=operations(target)
 low={'condition':condition,'requested_setaside_bytes':budget,'actual_setaside_bytes':budget if actual is None else actual,'actual_setaside_after_reset_bytes':0,'stream_value':0,'access_policy_window':({'base_ptr':PTR,'num_bytes':Q,'hit_ratio':min(1,budget/Q),'hit_property':'cudaAccessPropertyPersisting','miss_property':'cudaAccessPropertyStreaming'} if target else None),'reset_before':True,'reset_after':True,'operations_before':before,'operations_after':after}
 return {'status':'PASS','condition':condition,'policy_receipt':low,'qweight_regions':{'L0_UP':region(),'L14_UP':region(),'L0_DOWN':region()}}

def prov(): return [{'label':'capability','path':'RAW_CAP.json','sha256':SHA_A},{'label':'carrier','path':'RAW_RUN.json','sha256':SHA_B}]

class Tests(unittest.TestCase):
 def norm(self,c,condition,target=None,budget=None):
  return normalize_raw_policy_receipt(capability(),c,expected_condition=condition,expected_target=target,expected_budget_bytes=budget,source_provenance=prov())
 def test_full_target_runtime_rounding(self):
  x=self.norm(carrier(actual=37_748_736),'PERSIST_L0_UP','L0_UP',Q)
  self.assertTrue(x['runtime_setaside_rounding_observed']); self.assertEqual(x['qweight']['pointer'],PTR)
 def test_baseline_has_no_invented_qweight(self):
  x=self.norm(carrier('BASELINE'),'BASELINE'); self.assertNotIn('qweight',x); self.assertEqual(x['actual_setaside_bytes'],0)
 def test_setaside_only_matched_budget_no_window(self):
  x=self.norm(carrier('SETASIDE_ONLY',actual=37_748_736),'SETASIDE_ONLY',budget=Q)
  self.assertNotIn('qweight',x); self.assertFalse(x['access_window_enabled'])
 def test_budget_alias_exact_formula(self):
  b=16*1024*1024; x=self.norm(carrier('BUDGET_L0_UP',b),'PERSIST_L0_UP_BUDGET_16MIB','L0_UP',b)
  self.assertEqual(x['raw_condition'],'BUDGET_L0_UP'); self.assertAlmostEqual(x['hit_ratio'],b/Q)
 def test_source_provenance_required(self):
  with self.assertRaises(PolicyNormalizationError):
   normalize_raw_policy_receipt(capability(),carrier(),expected_condition='PERSIST_L0_UP',expected_target='L0_UP',expected_budget_bytes=Q,source_provenance=[])
 def test_qweight_span_mismatch_fails(self):
  c=carrier(); c['qweight_regions']['L0_UP']['exact_tensor_span_end_exclusive']-=1
  with self.assertRaises(PolicyNormalizationError): self.norm(c,'PERSIST_L0_UP','L0_UP',Q)
 def test_window_pointer_mismatch_fails(self):
  c=carrier(); c['policy_receipt']['access_policy_window']['base_ptr']+=1
  with self.assertRaises(PolicyNormalizationError): self.norm(c,'PERSIST_L0_UP','L0_UP',Q)
 def test_failed_operation_or_reset_fails(self):
  c=carrier(); c['policy_receipt']['operations_after'][1]['status']=1
  with self.assertRaises(PolicyNormalizationError): self.norm(c,'PERSIST_L0_UP','L0_UP',Q)
  c=carrier(); c['policy_receipt']['reset_before']=False
  with self.assertRaises(PolicyNormalizationError): self.norm(c,'PERSIST_L0_UP','L0_UP',Q)
 def test_budget_string_relabel_alone_cannot_pass(self):
  c=carrier('BUDGET_L0_UP',16*1024*1024); c['policy_receipt']['access_policy_window']['hit_ratio']=1.0
  with self.assertRaises(PolicyNormalizationError): self.norm(c,'PERSIST_L0_UP_BUDGET_16MIB','L0_UP',16*1024*1024)
 def test_runtime_capability_mismatch_fails(self):
  cap=capability(); cap['runtime_execution_authority']['l2_bytes']-=1
  with self.assertRaises(PolicyNormalizationError):
   normalize_raw_policy_receipt(cap,carrier(),expected_condition='PERSIST_L0_UP',expected_target='L0_UP',expected_budget_bytes=Q,source_provenance=prov())

if __name__=='__main__': unittest.main()
