import pathlib,importlib.util,tempfile,gzip,json,unittest,copy
P=pathlib.Path;HERE=P(__file__).parent;s=importlib.util.spec_from_file_location('live',HERE/'oracle_live_consumer.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
MATRIX=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/control/authority/FUTURE_DH_ORACLE_MATRIX.json')
class CPU(unittest.TestCase):
 def test_slowdown_retained(self):
  v=c.stat([{'S_oracle':.5,'H':-1}],32);self.assertEqual(v['slower'],1);self.assertAlmostEqual(v['GM_S_oracle'],.5);self.assertEqual(v['missing'],31)
 def test_empty_unknown(self):self.assertIsNone(c.stat([],32)['GM_S_oracle'])
 def test_repeated_kernel_raw_blocks_missing_is_null(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_ORACLE_RAW_') as td:
   p=P(td)/'MOCK.log.gz';p.write_bytes(gzip.compress(b'kernel_name = repeated\ngpu_sim_cycle = 120\ngpu_tot_sim_cycle = 120\nDTC_L1_oo_valid_hits = 0\nkernel_name = repeated\ngpu_sim_cycle = 80\ngpu_tot_sim_cycle = 200\nDTC_L1_oo_valid_hits = 3\n'))
   out=c.raw_kernel_evidence(p,c.sha(p),[{'ordinal':1},{'ordinal':2}]);self.assertEqual(len(out),2);self.assertEqual(out[0]['as_printed_counters']['DTC_L1_oo_valid_hits'],0);self.assertEqual(out[1]['as_printed_counters']['DTC_L1_oo_valid_hits'],3);self.assertIsNone(out[0]['as_printed_counters']['DTC_L1_oo_pending_hits'])
 def test_raw_sha_corruption(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_ORACLE_RAW_') as td:
   p=P(td)/'MOCK.log.gz';p.write_bytes(gzip.compress(b''))
   with self.assertRaisesRegex(ValueError,'SHA'):c.raw_kernel_evidence(p,'0'*64,[])
 @unittest.skipUnless(MATRIX.exists(),'requires frozen metadata only')
 def test_128_plan_without_stages(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_ORACLE_PLAN_') as td:
   r=c.snapshot(P(td)/'no_native_stages',MATRIX,P(td)/'derived');self.assertEqual(len(r['rows']),128);self.assertEqual(r['closed_result_count'],0)
   self.assertTrue(all(x['uuid'] is None and x['cycles'] is None and x['S_oracle'] is None and x['H'] is None for x in r['rows']))
 @unittest.skipUnless(MATRIX.exists(),'requires frozen metadata only')
 def test_negative_closed_fingerprint_and_mutation_hold(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_ORACLE_NEGATIVE_NOT_SCIENCE_') as td:
   root=P(td)/'base';stage=root/'initial8';(stage/'control').mkdir(parents=True);(stage/'analysis').mkdir();frozen=next(x for x in c.read(MATRIX)['rows'] if x['initial_fixed8']);point={k:frozen[k] for k in ('plan_id','program','suite','input_digest','mode')};point.update(cohort='MOCK_NOT_SCIENCE',request='MOCK_NOT_REGISTERED')
   c.put(stage/'control/MATRIX.fixed.json',{'points':[point]});c.put(stage/'control/EXECUTION_PLAN.json',{'preparation_phase':'CPU_DRAFT_NO_REGISTRATION','MOCK_NOT_SCIENTIFIC':True})
   rp=stage/'analysis/MOCK_NOT_SCIENCE.RESULT.json';c.put(rp,{'state':'MOCK_NEGATIVE_NOT_SCIENTIFIC','uuid':'MOCK_NOT_REAL_UUID','cycles':123,'proof':{'MOCK_NOT_SCIENTIFIC':True}})
   out=P(td)/'derived';r=c.snapshot(root,MATRIX,out);self.assertEqual(r['closed_result_count'],1);row=next(x for x in r['rows'] if x['result_path']);self.assertEqual(row['classification'],'negative_or_hold');self.assertIsNone(row['cycles']);self.assertEqual(row['observed_cycles_not_accepted'],123)
   fp=r['closed_fingerprint_sha256'];rr=c.snapshot(root,MATRIX,out);self.assertEqual(rr['closed_fingerprint_sha256'],fp)
   v=c.read(rp);v['cycles']=456;c.put(rp,v);rr=c.snapshot(root,MATRIX,out);row=next(x for x in rr['rows'] if x['result_path']);self.assertEqual(row['status'],'HOLD_EVIDENCE_VALIDATION');self.assertIsNone(row['S_oracle']);self.assertNotEqual(rr['closed_fingerprint_sha256'],fp)
 @unittest.skipUnless(MATRIX.exists(),'requires frozen metadata only')
 def test_frozen_point_changed_rejected(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_ORACLE_POINT_') as td:
   stage=P(td)/'base/initial8';(stage/'control').mkdir(parents=True);p=next(x for x in c.read(MATRIX)['rows'] if x['initial_fixed8']);point={k:p[k] for k in ('plan_id','program','suite','input_digest','mode')};point['input_digest']='0'*64;c.put(stage/'control/MATRIX.fixed.json',{'points':[point]})
   with self.assertRaisesRegex(ValueError,'frozen full input'):c.snapshot(P(td)/'base',MATRIX,P(td)/'derived')
if __name__=='__main__':unittest.main(verbosity=2)
