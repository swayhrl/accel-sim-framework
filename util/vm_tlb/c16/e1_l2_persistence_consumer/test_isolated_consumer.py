import copy, csv, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from isolated_consumer import IsolatedConsumerError, analyze_timing_rows, consume_ncu

SHA_A='a'*64; SHA_B='b'*64; RANGE='ISO_TEXT_UP_M1'

def timing_rows():
    return [{"condition":c,"role":"up_proj","M":1,"implementation":"AWQ_FP16_INPUT",
             "rep":r,"timing_ms":10+r+(0 if c.endswith('BASELINE_DENSE') else -1),
             "input_sha256":SHA_A,"output_sha256":SHA_B}
            for c in ('ISO_BASELINE_DENSE','ISO_QWEIGHT_PERSIST_DENSE') for r in range(9)]

class TimingTests(unittest.TestCase):
    def test_pass(self):
        x=analyze_timing_rows(timing_rows()); self.assertEqual(x['status'],'PASS'); self.assertEqual(x['conditions']['ISO_BASELINE_DENSE']['sample_count'],9)
    def test_duplicate(self):
        with self.assertRaises(IsolatedConsumerError): analyze_timing_rows(timing_rows()+[timing_rows()[0]])
    def test_missing_rep(self):
        with self.assertRaises(IsolatedConsumerError): analyze_timing_rows(timing_rows()[:-1])
    def test_sha_drift(self):
        x=timing_rows(); x[-1]['input_sha256']='c'*64
        with self.assertRaises(IsolatedConsumerError): analyze_timing_rows(x)
    def test_nonfinite(self):
        x=timing_rows(); x[0]['timing_ms']='nan'
        with self.assertRaises(IsolatedConsumerError): analyze_timing_rows(x)

class NcuTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.profiles=[]
        for i,c in enumerate(('ISO_BASELINE_DENSE','ISO_QWEIGHT_PERSIST_DENSE')):
            stem=f'p{i}'; base=self.root/(stem+'_BASE.csv'); session=self.root/(stem+'_SESSION.csv'); profile=self.root/(stem+'_PROFILE.log'); policy=self.root/(stem+'_POLICY.json')
            header=['ID','Process ID','Kernel Name','NVTX Push/Pop_Range','profiler__replayer_passes','l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum']
            units=['','','','','','byte','byte','byte']
            with base.open('w',newline='',encoding='utf-8') as f: csv.writer(f).writerows([header,units,['1','7','kernel','7:'+RANGE+':x','2','100','200',str(300-i*100)]])
            session.write_text('ncu --replay-mode application --cache-control none --nvtx-include '+RANGE+'/ --metrics l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum\n')
            profile.write_text(json.dumps({'status':'PASS','condition':c,'role':'up_proj','M':1,'implementation':'AWQ_FP16_INPUT','range':RANGE,'input_sha256':SHA_A,'output_sha256':SHA_B})+'\n')
            policy.write_text(json.dumps({'condition':c}))
            p={'condition':c,'role':'up_proj','M':1,'implementation':'AWQ_FP16_INPUT','range_name':RANGE,
               'input_sha256':SHA_A,'output_sha256':SHA_B,'expected_kernel_names':['kernel'],'expected_pass_count':2,
               'expected_target':'L0_UP','base_path':base.name,'session_path':session.name,'profile_path':profile.name,'policy_receipt_path':policy.name}
            if i: p['expected_budget_bytes']=100
            self.profiles.append(p)
    def tearDown(self): self.tmp.cleanup()
    def validator(self,receipt,**kwargs):
        self.assertEqual(receipt['condition'],kwargs['expected_condition']); self.assertEqual(kwargs['expected_target'],'L0_UP')
        if kwargs['expected_condition'].startswith('ISO_Q'): self.assertEqual(kwargs['expected_budget_bytes'],100)
        return {'status':'PASS','condition':kwargs['expected_condition']}
    def consume(self,profiles=None,validator=None):
        return consume_ncu({'schema_version':1,'profiles':profiles or self.profiles},self.root,policy_validator=validator or self.validator)
    def test_pass_direct_four_source(self):
        x=self.consume(); self.assertEqual(x['status'],'PASS'); self.assertAlmostEqual(x['persist_over_baseline_metric_effects']['dram__bytes.sum']['persist_over_baseline'],2/3)
    def test_duplicate_condition(self):
        with self.assertRaises(IsolatedConsumerError): self.consume([self.profiles[0],copy.deepcopy(self.profiles[0])])
    def test_session_replay_fails(self):
        (self.root/self.profiles[0]['session_path']).write_text('ncu --replay-mode kernel --cache-control none --nvtx-include '+RANGE+'/ --metrics '+','.join(('l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum')))
        with self.assertRaises(IsolatedConsumerError): self.consume()
    def test_unit_mismatch_fails(self):
        p=self.root/self.profiles[0]['base_path']
        with p.open(newline='') as f: rows=list(csv.reader(f))
        rows[1][-1]='Kbyte'
        with p.open('w',newline='') as f: csv.writer(f).writerows(rows)
        with self.assertRaises(IsolatedConsumerError): self.consume()
    def test_kernel_inventory_fails(self):
        p=copy.deepcopy(self.profiles); p[0]['expected_kernel_names']=['other']
        with self.assertRaises(IsolatedConsumerError): self.consume(p)
    def test_profile_sha_fails(self):
        p=self.root/self.profiles[0]['profile_path']; d=json.loads(p.read_text()); d['input_sha256']='c'*64; p.write_text(json.dumps(d))
        with self.assertRaises(IsolatedConsumerError): self.consume()
    def test_policy_fails_closed(self):
        def bad(*args,**kwargs): raise ValueError('bad policy')
        with self.assertRaises(IsolatedConsumerError): self.consume(validator=bad)

if __name__=='__main__': unittest.main()
