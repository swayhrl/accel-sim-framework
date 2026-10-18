"""RG1 needs separate ON qualification, real ready witnesses and an exclusive flag."""
import copy,unittest
from service_rg1_scope import IDENTITY,expected,features,validate
from service_scope import features as mq_features
from independent_rg1 import validate as validate_witness

class RG1(unittest.TestCase):
 def identity(self):
  f,i=expected('S64_rg1_1');return {**IDENTITY,'feature_vector':f,'ideal_vector':i}
 def test_separate_rg1_vector_cannot_inherit_mq2_or_cross_binary(self):
  i=self.identity();features(i,'S64_rg1_1')
  with self.assertRaises(ValueError):mq_features(i,'S64_rg1_1')
  for key,value in [('mq2',True),('rg1',False),('ops_per_bank_cycle',2),('wb_local_cap',16),('static_wb_capacity',16)]:
   wrong=copy.deepcopy(i);wrong['feature_vector'][key]=value
   with self.assertRaises(ValueError):features(wrong,'S64_rg1_1')
  wrong=copy.deepcopy(i);wrong['binary_sha256']='0'*64
  with self.assertRaises(ValueError):features(wrong,'S64_rg1_1')
 def test_mq2_review_cannot_qualify_an_rg1_spec(self):
  spec={'producer_profile':'S64_rg1_1','identity':self.identity(),'scientific_scope':'FINITE_SERVICE_RG1_NATIVE_V1'}
  with self.assertRaises(ValueError):validate(spec,{},[],[],{'qualification_kind':'FINITE_SERVICE_NATIVE_V1'})
 def test_actual_samebank_ready_service_and_physical_p1_required(self):
  cmd=['fixture','base','overlay','1','16','0','0','1','1','4096'];text='RG1 real partition response FIFO full, retained response bank3, ReturnQ fill ready, services=1 enabled=1 PASS\nRG1 actual partition exact-once/sector-version/physical-P1/drain PASS\nEPL2STRUCTV1|BANK_PEAK|slice=0|ops_per_physical_cycle=1|bank0=1|bank1=1|bank2=1|bank3=1\n';validate_witness('RG1_B16_partition_4096',cmd,text)
  for before,after in [('services=1 enabled=1','services=0 enabled=1'),('bank3=1','bank3=2'),('sector-version','sector-bad')]:
   with self.assertRaises(ValueError):validate_witness('RG1_B16_partition_4096',cmd,text.replace(before,after))

if __name__=='__main__':unittest.main()
