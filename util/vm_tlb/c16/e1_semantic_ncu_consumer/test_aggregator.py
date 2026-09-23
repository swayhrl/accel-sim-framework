#!/usr/bin/env python3
import unittest
from aggregator import AggregationError,aggregate
POLICY={'additive_metrics':{'dram__bytes.sum':'byte','lts__bytes.sum':'byte'},'non_additive_metrics':{'sm__throughput.avg.pct_of_peak_sustained_elapsed':'%'}}
def row(point,rng,occ,kid,name,metric,unit,value):return {'semantic_point':point,'range_name':rng,'range_occurrence':str(occ),'kernel_id':str(kid),'kernel_name':name,'metric_name':metric,'metric_unit':unit,'metric_value':str(value),'input_elements':'10','output_elements':'20','dense_weight_bytes':'100','packed_weight_bytes':'25'}
def kernel(point,rng,occ,kid,name,dram,l2,util):return [row(point,rng,occ,kid,name,'dram__bytes.sum','byte',dram),row(point,rng,occ,kid,name,'lts__bytes.sum','byte',l2),row(point,rng,occ,kid,name,'sm__throughput.avg.pct_of_peak_sustained_elapsed','%',util)]
class Tests(unittest.TestCase):
 def test_single_raw_kernel(self):
  x=aggregate(kernel('M1_RAW','TARGET',0,1,'dense',100,50,20),'M1_RAW','TARGET',POLICY);self.assertEqual(x['kernel_count'],1);self.assertEqual(x['SEMANTIC_MODULE_SUM']['dram__bytes.sum']['value'],100)
 def test_multi_kernel_awq_adds_bytes_not_util(self):
  rows=kernel('M1_AWQ','TARGET',0,1,'dequant',100,50,20)+kernel('M1_AWQ','TARGET',0,2,'gemm',300,150,40)
  x=aggregate(rows,'M1_AWQ','TARGET',POLICY);self.assertEqual(x['SEMANTIC_MODULE_SUM']['dram__bytes.sum']['value'],400);self.assertNotIn('sm__throughput.avg.pct_of_peak_sustained_elapsed',x['SEMANTIC_MODULE_SUM']);self.assertEqual(len(x['non_additive_per_kernel']['sm__throughput.avg.pct_of_peak_sustained_elapsed']),2)
 def test_warmup_excluded(self):
  rows=kernel('M1_RAW','WARMUP',0,9,'warm',999,999,99)+kernel('M1_RAW','TARGET',0,1,'dense',100,50,20);x=aggregate(rows,'M1_RAW','TARGET',POLICY);self.assertEqual(x['kernel_count'],1)
 def test_ambiguous_range_fails(self):
  rows=kernel('M1_RAW','TARGET',0,1,'a',1,1,1)+kernel('M1_RAW','TARGET',1,2,'b',1,1,1)
  with self.assertRaises(AggregationError):aggregate(rows,'M1_RAW','TARGET',POLICY)
 def test_unit_mismatch_fails(self):
  rows=kernel('M1_RAW','TARGET',0,1,'a',1,1,1);rows[0]['metric_unit']='kbyte'
  with self.assertRaises(AggregationError):aggregate(rows,'M1_RAW','TARGET',POLICY)
if __name__=='__main__':unittest.main()
