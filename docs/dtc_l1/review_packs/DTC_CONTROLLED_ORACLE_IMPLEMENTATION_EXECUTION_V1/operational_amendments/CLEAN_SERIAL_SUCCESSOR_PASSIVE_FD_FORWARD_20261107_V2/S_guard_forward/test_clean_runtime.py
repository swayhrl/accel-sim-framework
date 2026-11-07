"""Pure source/metadata CPU qualification. No actual run_released_new96 call."""
from pathlib import Path
import copy,importlib.util,json,unittest
HERE=Path(__file__).resolve().parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load('CPU_ONLY_CLEAN_RUNTIME','oracle_clean_runtime.py');f=load('CPU_ONLY_CLEAN_FINALIZER','oracle_clean_finalizer.py')
class RuntimeTests(unittest.TestCase):
 def setUp(self):
  self.parent=dict(pid=1234,start_ticks=5678,request=r.REQUEST,controller=dict(path='/CPU_MOCK/controller.py',sha256='a'*64))
  self.plan=dict(request=r.REQUEST,stage='remaining24',expected_new_starts=96,authorized_cohorts=['MOCK_'+str(i)for i in range(96)],
   preparation_phase='SCIENCE_FINAL_FROZEN',authority_commit=r.AUTHORITY,parent_pid=1234,parent_start_ticks=5678,
   qualified_modes=['M_DATAREAD','L2_DATAREAD','L1_DATAREADY'],CH_budget=0)
  self.candidate=dict(request=r.REQUEST,budget=96,remaining=96,admitted_specs=dict.fromkeys(self.plan['authorized_cohorts'],'b'*64),
   consumed={},sealed={},ready_for_registration=True,owner_pid=1234,owner_start_ticks=5678,
   approved_contract_commit=r.AUTHORITY,model_automatic_retries=0,new_registration_only=True,old_request_budget_reused=False)
  self.evidence=dict(authority_commit=r.AUTHORITY,exact_candidate_count=96,Gate0_CPU_source_strict_independent_review='PASS',
   Gate2_any_mode_fixed8_and_shared_OFF_accepted_independently_reviewed='PASS',Gate2_released_modes=['M_DATAREAD'])
 def test_pure_register_only_new96_preserves_old32_and_history(self):
  reg=dict(registered_future_requests={'OLD32':dict(uuid='ORIGINAL_MOCK',budget=32,remaining=0,lease='UNCHANGED')},
   old_source_history={'untouched':1},new_scientific_budget_remaining=9)
  original=copy.deepcopy(reg);r.register_exact_request(reg,self.candidate,self.plan,self.parent,self.evidence)
  self.assertEqual(reg['registered_future_requests']['OLD32'],original['registered_future_requests']['OLD32'])
  self.assertEqual({k:v for k,v in reg.items()if k!='registered_future_requests'},
                   {k:v for k,v in original.items()if k!='registered_future_requests'})
  self.assertEqual(reg['registered_future_requests'][r.REQUEST]['budget'],96)
 def test_duplicate_request_never_overwritten(self):
  reg=dict(registered_future_requests={r.REQUEST:{'old':'preserved'}})
  before=copy.deepcopy(reg)
  with self.assertRaises(RuntimeError):r.register_exact_request(reg,self.candidate,self.plan,self.parent,self.evidence)
  self.assertEqual(reg,before)
 def test_cpu_candidate_not_authority(self):
  self.candidate['ready_for_registration']=False
  with self.assertRaises(RuntimeError):r.validate_candidate(self.candidate,self.plan,self.parent)
 def test_old_pid_not_legal_new_parent(self):
  self.parent['pid']=self.plan['parent_pid']=self.candidate['owner_pid']=1498278
  self.parent['start_ticks']=self.plan['parent_start_ticks']=self.candidate['owner_start_ticks']=977758783
  with self.assertRaises(RuntimeError):r.validate_candidate(self.candidate,self.plan,self.parent)
 def test_missing_mode_gate_does_not_register(self):
  self.evidence['Gate2_released_modes']=[];reg=dict(registered_future_requests={})
  with self.assertRaises(RuntimeError):r.register_exact_request(reg,self.candidate,self.plan,self.parent,self.evidence)
  self.assertEqual(reg['registered_future_requests'],{})
 def test_no_extra_scientific_start(self):
  self.candidate['budget']=97
  with self.assertRaises(RuntimeError):r.validate_candidate(self.candidate,self.plan,self.parent)
 def test_parent_binding_is_metadata_only(self):
  before=copy.deepcopy(self.candidate)
  p,q=f.bind_metadata(self.plan,self.candidate,self.parent,{'path':'MOCKLEASE','sha256':'c'*64},[],{'path':'MOCKROUTE','sha256':'d'*64},'e'*64)
  self.assertEqual(q['admitted_specs'],before['admitted_specs']);self.assertEqual(q['consumed'],{})
  self.assertEqual(q['execution_plan_sha256'],'e'*64);self.assertEqual(p['clean_owner_lease']['path'],'MOCKLEASE')
 def test_additive_native_route_keeps_all_old_bytes(self):
  before=b'#!/bin/sh\nset -eu\n# ORIGINAL_MOCK_ROUTE\n';block=b'# DTC_ORACLE_CLEAN_SUCCESSOR_REMAINING24_V1_ROUTE MOCK_ONLY\n'
  after=f.route_projection(before,block);self.assertEqual(after.replace(block,b'',1),before)
  with self.assertRaises(f.Hold):f.route_projection(after,block)
 def test_helpers_extract_only_reviewed_B2_nodes(self):
  pins=json.loads((HERE/'CPU_SOURCE_INPUTS.fixed.json').read_bytes());source=Path(pins['B2']['path']).read_bytes()
  environment={};r.helpers_from_B2(source,environment)
  self.assertTrue({'fresh','harvest','cycle_error'}<=set(environment));self.assertNotIn('apply',environment)
  with self.assertRaises(RuntimeError):r.helpers_from_B2(source+b'\n',{})

if __name__=='__main__':unittest.main()
