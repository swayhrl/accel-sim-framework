#!/usr/bin/env python3
import unittest
from comparator import ContractError,analyze
def make(role,m,impl,samples,sha,dtype,weight):return {'role':role,'M':m,'implementation':impl,'samples_ms':samples,'activation_sha256':sha,'activation_dtype':dtype,'weight_dtype':weight,'path_fingerprint':impl+'-path'}
class ComparatorTests(unittest.TestCase):
 def fixture(self):
  rows=[]
  for role,scale in [('q_proj',1),('down_proj',2),('up_proj',3)]:
   for m in (1,256):
    sha=role+str(m);base=scale*(1 if m==1 else 20)
    awq=.9 if role=='down_proj' and m==256 else 1.2
    rows += [make(role,m,'RAW_BF16',[base,base*1.01,base*.99],sha,'BF16','BF16'),make(role,m,'RAW_FP16',[base*1.1,base*1.11,base*1.09],sha,'FP16','FP16'),make(role,m,'AWQ_FP16_INPUT',[base*awq,base*awq*1.01,base*awq*.99],sha,'FP16','INT4')]
  return rows
 def test_recomputes_and_selects(self):
  r=analyze(self.fixture(),True);self.assertEqual(r['status'],'PASS');self.assertEqual(r['ncu_selection']['selected_role'],'down_proj');self.assertEqual(len(r['ratios']),6)
 def test_rejects_noncommon_fp16(self):
  rows=self.fixture();rows[2]['activation_sha256']='different'
  with self.assertRaises(ContractError):analyze(rows,True)
if __name__=='__main__':unittest.main()
