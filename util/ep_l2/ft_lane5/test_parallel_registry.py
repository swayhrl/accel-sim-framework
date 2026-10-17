"""Synthetic campaign/concurrency boundaries; never simulator qualification."""
from copy import deepcopy
import multiprocessing
import unittest
from unittest.mock import patch
from registry import Registry, PARALLEL, R19, R19_DEADLINE, PARALLEL_ABSOLUTE_DEADLINE
from test_lane5 import RegistryTests, identity


def distinct_worker(root, number, queue):
    row=identity();row['trace_content_sha256']=f'{number:064x}'
    try:
        fresh,_=Registry(root).claim(row,'lane5','/unused',resources={'disk_free_bytes':2**50,'available_memory_bytes':2**50})
        queue.put(fresh)
    except ValueError:queue.put(False)


class ParallelRegistry(unittest.TestCase):
    claim = RegistryTests.claim
    tearDown = RegistryTests.tearDown
    def setUp(self):
        RegistryTests.setUp(self)
        with self.registry.locked() as d:d['hosts'][self.host]['max_simulators']=4
        self.cells=[{'cell_id':f'I{i:03d}','experiment_id':PARALLEL,'workload_alias':'sad','condition':'H0','mode':'I_WB'} for i in range(50)]
        with patch('registry.time.time',return_value=1792236000):
            self.campaign=self.registry.register_parallel_campaign(self.cells,'a'*40)
        self.exp={'experiment_id':PARALLEL,'regime':'H0','profile':'I_WB','cell_id':'I000','deadline_unix':self.campaign['deadline_unix']}

    def test_four_global_admissions_atomic(self):
        ctx=multiprocessing.get_context('fork');q=ctx.Queue()
        ps=[ctx.Process(target=distinct_worker,args=(str(self.root),i,q)) for i in range(12)]
        for p in ps:p.start()
        result=[q.get(timeout=10) for p in ps]
        for p in ps:p.join(10);self.assertEqual(p.exitcode,0)
        self.assertEqual(sum(result),4)
        self.assertEqual(sum(r['memory_bytes'] for r in self.registry.snapshot()['runs'].values()),32*2**30)

    def test_registration_t0_frozen(self):
        with patch('registry.time.time',return_value=1792250000):
            again=self.registry.register_parallel_campaign(self.cells,'a'*40)
        self.assertEqual(again,self.campaign)
        self.assertEqual(again['deadline_unix'],min(again['t0_unix']+86400,PARALLEL_ABSOLUTE_DEADLINE))
        changed=deepcopy(self.cells);changed[0]['condition']='wrong'
        with self.assertRaises(ValueError):self.registry.register_parallel_campaign(changed,'a'*40)

    def test_counters_independent_and_failure_counts(self):
        d=self.registry.snapshot()
        for i in range(24):d['runs'][str(i)]={'experiment_id':R19,'status':'FAILED'}
        with self.assertRaisesRegex(ValueError,'cap'):
            Registry.check_experiment(d,{'experiment_id':R19,'regime':'D2','deadline_unix':R19_DEADLINE},identity(),'lane5')
        Registry.check_experiment(d,self.exp,identity(),'lane5')
        for i in range(72):d['runs']['new'+str(i)]={'experiment_id':PARALLEL,'cell_id':'other'+str(i),'status':'TIMEOUT'}
        with self.assertRaisesRegex(ValueError,'cap'):Registry.check_experiment(d,self.exp,identity(),'lane5')

    def test_wrong_cell_profile_deadline_and_owner(self):
        for fields in ({'cell_id':'absent'},{'profile':'not-qualified'},{'regime':'D4'},{'deadline_unix':self.exp['deadline_unix']+1}):
            with self.subTest(fields=fields),self.assertRaises(ValueError):
                Registry.check_experiment(self.registry.snapshot(),{**self.exp,**fields},identity(),'lane5')
        with self.assertRaises(ValueError):Registry.check_experiment(self.registry.snapshot(),self.exp,identity(),'lane1')
        with patch('registry.time.time',return_value=self.exp['deadline_unix']):
            with self.assertRaises(ValueError):Registry.check_experiment(self.registry.snapshot(),self.exp,identity(),'lane5')

    def test_old_r19_deadline_cannot_extend(self):
        with self.assertRaises(ValueError):Registry.check_experiment(self.registry.snapshot(),{'experiment_id':R19,'regime':'D2','deadline_unix':R19_DEADLINE+1},identity(),'lane5')

    def test_old_lease_terminal_after_policy_update_and_new_deadline(self):
        fresh,row=self.claim();self.assertTrue(fresh)
        before=deepcopy(self.registry.snapshot()['runs'])
        self.registry.register_parallel_campaign(self.cells,'a'*40)
        self.assertEqual(before,self.registry.snapshot()['runs'])
        with patch('registry.time.time',return_value=PARALLEL_ABSOLUTE_DEADLINE+100):
            self.registry.update(row['run_key'],row['lease_id'],'FAILED',detail='synthetic existing client terminal')
        self.assertEqual(self.registry.snapshot()['runs'][row['run_key']]['status'],'FAILED')

    def test_new_same_cell_wrong_identity_cannot_evade_dedup(self):
        fresh,row=self.registry.claim(identity(),'lane5','/unused',resources=self.resources,experiment=self.exp)
        self.assertTrue(fresh)
        self.registry.update(row['run_key'],row['lease_id'],'FAILED')
        other=identity();other['runtime_config_sha256']='9'*64
        with self.assertRaisesRegex(ValueError,'already attempted'):
            self.registry.claim(other,'lane5','/unused',resources=self.resources,experiment=self.exp)

    def test_native_off_registration_preserves_count_and_pins_identity(self):
        from registry import write_json
        import hashlib
        proof=self.root/'checkpoint.json';proof.write_text('{}')
        binding={'path':str(proof),'sha256':hashlib.sha256(proof.read_bytes()).hexdigest()}
        cell=self.registry.register_native_off_control(identity(),binding)
        self.assertEqual(len(self.registry.snapshot()['runs']),0)
        exp={'experiment_id':PARALLEL,'regime':'H0','profile':'NATIVE_OFF_CONTROL',
             'cell_id':cell['cell_id'],'deadline_unix':self.campaign['deadline_unix']}
        bad=identity();bad['binary_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'exact runtime identity'):
            self.registry.claim(bad,'lane5','/unused',resources=self.resources,experiment=exp)
        fresh,row=self.registry.claim(identity(),'lane5','/unused',resources=self.resources,experiment=exp)
        self.assertTrue(fresh)
        self.assertEqual(sum(v.get('experiment_id')==PARALLEL for v in self.registry.snapshot()['runs'].values()),1)
        proof.write_text('{"changed":true}')
        with self.assertRaisesRegex(ValueError,'checkpoint changed'):
            self.registry.register_native_off_control(identity(),binding)


if __name__=='__main__':unittest.main()
