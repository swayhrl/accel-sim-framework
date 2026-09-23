#!/usr/bin/env python3
import unittest
from capacity_consumer import CapacityError,census
def tensor(name,shape,size=2,dtype='torch.float16'):return {'name':name,'shape':shape,'element_size':size,'dtype':dtype}
def doc():
 roles={}
 for role in ('q_proj','down_proj','up_proj'):roles[role]={'raw_fp16':[tensor('weight',[4,8]),tensor('bias',[4])],'awq_state_dict':[tensor('qweight',[4,1],4,'torch.int32'),tensor('qzeros',[1,1],4,'torch.int32'),tensor('scales',[1,4])]}
 return {'device_l2_bytes':100,'roles':roles}
class Tests(unittest.TestCase):
 def test_exact_bytes_and_relations(self):
  r=census(doc())[0];self.assertEqual(r['raw_total_bytes'],72);self.assertEqual(r['awq_state_dict_bytes'],28);self.assertEqual((r['raw_vs_l2'],r['awq_vs_l2']),('LT','LT'))
 def test_extra_awq_state_counted(self):
  d=doc();d['roles']['q_proj']['awq_state_dict'].append(tensor('g_idx',[8],4,'torch.int32'));self.assertEqual(census(d)[0]['awq_state_dict_bytes'],60)
 def test_duplicate_fails(self):
  d=doc();d['roles']['q_proj']['awq_state_dict'].append(dict(d['roles']['q_proj']['awq_state_dict'][0]));self.assertRaises(CapacityError,census,d)
 def test_missing_role_fails(self):
  d=doc();del d['roles']['up_proj'];self.assertRaises(CapacityError,census,d)
 def test_bad_shape_fails(self):
  d=doc();d['roles']['q_proj']['raw_fp16'][0]['shape']=[0,8];self.assertRaises(CapacityError,census,d)
 def test_dtype_fails(self):
  d=doc();d['roles']['q_proj']['raw_fp16'][0]['dtype']='torch.float32';self.assertRaises(CapacityError,census,d)
if __name__=='__main__':unittest.main()
