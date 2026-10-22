"""Python-only pure candidate tests; not actual Coordinator integration/native evidence."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import detach_scope_core as p

ROOT = Path(__file__).resolve().parent
LIVE = Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
# Read once; all mutations below use a deep copy in /tmp or in memory.
LIVE_BYTES = LIVE.read_bytes()
SNAPSHOT = json.loads(LIVE_BYTES)['mechanism_study_20261019_v1']


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
    return {'path': str(path), 'sha256': p.file_sha(path)}


class ScopeControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fixture_', dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.item = copy.deepcopy(SNAPSHOT)
        self.seal = p.old_seal(self.item)
        self.before_pairs = copy.deepcopy(self.item['accepted_pairs'])
        # Never create a process, invoke a compiler, or touch original registry APIs.
        self.enterContext(patch('subprocess.Popen', side_effect=AssertionError('real Popen forbidden')))
        self.enterContext(patch('subprocess.run', side_effect=AssertionError('native/build subprocess forbidden')))
        for name in ('execv', 'execve', 'execl', 'execlp', 'execvp', 'fork'):
            self.enterContext(patch.object(os, name, side_effect=AssertionError('real exec/fork forbidden')))
        source = dict(core_source_commit='a'*40, framework_source_commit='b'*40,
                      vendor_pybind11_commit='c'*40, binary_sha256='d'*64, archive_sha256='e'*64)
        self.producer = write(self.root/'producer.json', dict(synthetic_fixture=True,
                              status='SYNTHETIC_FORMAL_PRODUCER', source_identity=source))
        self.parser = self.root/'parser.py'
        self.parser.write_text('# SYNTHETIC_FIXTURE no simulator code\n')
        self.config = self.root/'F.config'
        self.config.write_text('# SYNTHETIC_FIXTURE F W1 V1 T1 M1 P1 finite1168\n')
        self.schema = write(self.root/'counter_schema.json', dict(synthetic_fixture=True,
                           schema='SYNTHETIC_OBSERVER_SCHEMA'))
        profile = dict(research_switches=dict.fromkeys(('W','V','T','M'),1),
                       labels={'diagnostic':True}, synthetic_fixture=True)
        self.qref = write(self.root/'qualification.json',dict(synthetic_fixture=True,
            status='INDEPENDENTLY_QUALIFIED', source_identity=source,
            scientific_scope=p.SCI_SCOPE, profile_semantics=profile))
        self.spec = dict(condition_id='SYNTHETIC_OBSERVER_SGEMM_F',
            budget_bucket='SYNTHETIC_ONE_END_BATCH', profile='F',
            scientific_scope=p.SCI_SCOPE, selection_id='D_EXP_SGEMM_MEDIUM_20261022_r1',
            identity=dict(core_source_commit=source['core_source_commit'],
                framework_source_commit=source['framework_source_commit'], binary_sha256=source['binary_sha256'],
                trace_content_sha256='694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb',
                feature_vector={'payload_capacity_per_slice':1168,'ops_per_bank_cycle':1}),
            qualification_id=self.qref['sha256'], profile_semantics=profile,
            configs=[{'path':str(self.config),'sha256':p.file_sha(self.config)}],
            parser={'path':str(self.parser),'sha256':p.file_sha(self.parser)},
            operational_limits_override={'synthetic_fixture':True,'effective_timeout_seconds':None},
            maximum_result_bytes=384*2**20,memory_bytes=12*p.GIB,cpu=1,synthetic_fixture=True)
        binding = dict(source_identity=source,scientific_scope=p.SCI_SCOPE,
            profile='F',selection_id=self.spec['selection_id'],trace_content_sha256=self.spec['identity']['trace_content_sha256'],
            manifest_sha256='853369d8e256d57ff440b88cb31f9b7c5967f3e411eb84c32612021fa1ade6c3',
            ranges_sha256='be570e38e168b59252ac7f4ed041e2b606aed79ea0c9650e94c840f825767aa8',
            qualification=self.qref,producer=self.producer,parser=self.spec['parser'],identity=copy.deepcopy(self.spec['identity']),
            spec_sha256=p.spec_sha(self.spec),content_refs=[self.schema,self.spec['configs'][0]])
        self.manifest = dict(schema='E2_EXACT_DETACH_OBSERVER_FINAL_MANIFEST_V1',
            campaign_id=p.CAMPAIGN,maximum_new_actual_starts=1,baseline_actual_starts=50,
            condition_id=self.spec['condition_id'],batch_id=self.spec['budget_bucket'],
            deployment_state='SYNTHETIC_FIXTURE_NOT_DEPLOYABLE',scientific_binding=binding,
            old_seal=self.seal,pairs=[],prohibited_old_binary_sha256=[
                self.item['final_source_identity']['binary_sha256'],
                self.item['capacity_diagnostic_runtime']['binary_sha256']])
        self.approval = dict(schema='E2_EXACT_DETACH_OBSERVER_USER_APPROVAL_V1',
            campaign_id=p.CAMPAIGN,maximum_new_actual_starts=1,baseline_actual_starts=50,
            condition_id=self.spec['condition_id'],batch_id=self.spec['budget_bucket'],
            manifest_scientific_binding_sha256=p.sha(binding),synthetic_fixture=True)
        self.refresh_authority()
        self.resources = dict(workspace_free_bytes=20*p.GIB,share_free_bytes=44*p.GIB,
            available_memory_bytes=200*p.GIB,reserved_memory_bytes=0,reserved_cpu_units=0,
            new_bytes=8*p.GIB,total_bytes=21*p.GIB,io_pressure='HIGH')

    def refresh_authority(self):
        mref=write(self.root/'manifest.json',self.manifest)
        aref=write(self.root/'approval.json',self.approval)
        self.auth=p.Authority(mref['path'],mref['sha256'],aref['path'],aref['sha256'],fixture_mode=True)

    def reauthorize_spec(self):
        self.manifest['scientific_binding']['spec_sha256']=p.spec_sha(self.spec)
        self.approval['manifest_scientific_binding_sha256']=p.sha(self.manifest['scientific_binding'])
        self.refresh_authority()

    def ready(self):
        self.auth.adopt(self.item)
        self.item['qualifications'][self.spec['qualification_id']] = {
            **self.qref,'qualification':json.loads(Path(self.qref['path']).read_text())}
        self.auth.bind(self.item,self.spec)

    def reserve(self):
        self.ready()
        return self.auth.reserve_synthetic(self.item,self.spec,self.resources)

    def start(self):
        self.reserve()
        return self.auth.start_synthetic(self.item,lambda:dict(synthetic_fixture=True,pid='SYNTHETIC_PID',
            start_ticks='SYNTHETIC_TICKS',boot_id='SYNTHETIC_BOOT'),owns_controller=True)

    def terminal(self):
        return dict(native_process=copy.deepcopy(self.item['attempts'][-1]['process']),
                    exit_code=0,wait_status=0,stop_reason=None,instructions=1658916864,
                    slices=64,drained=True,observer_validation='PASS')

    def test_01_baseline_no_adoption(self):
        self.assertFalse(self.auth.active(self.item))
        self.item['attempts'].append({'state':'FAILED'})
        with self.assertRaisesRegex(ValueError,'unauthorized post50'):self.auth.active(self.item)

    def test_02_exact_once_adoption(self):
        self.assertTrue(self.auth.adopt(self.item))
        self.assertFalse(self.auth.adopt(self.item))
        self.assertEqual(len(self.item['attempts']),50)
        self.assertEqual(self.item['t0_unix'],1792414193)

    def test_03_active_or_uncertain_denied(self):
        for mutate in (lambda x:x['controller'].update(state='ACTIVE'),
                       lambda x:x['attempts'][0].update(state='START_INTENT_UNRECONCILED')):
            x=copy.deepcopy(self.item);mutate(x)
            with self.assertRaises(ValueError):self.auth.adopt(x)
        with self.assertRaises(ValueError):self.auth.adopt(self.item,[{'status':'RUNNING'}])

    def test_04_no_placeholder_or_old_producer(self):
        for field,value in [('binary_sha256',None),('core_source_commit','UNKNOWN'),
                            ('archive_sha256',''),('binary_sha256',self.item['final_source_identity']['binary_sha256'])]:
            with self.subTest(field=field,value=value):
                original=copy.deepcopy(self.manifest)
                self.manifest['scientific_binding']['source_identity'][field]=value
                self.approval['manifest_scientific_binding_sha256']=p.sha(self.manifest['scientific_binding'])
                self.refresh_authority()
                with self.assertRaises(ValueError):self.auth.authority()
                self.manifest=original

    def test_05_exact_q_spec_config_parser_schema(self):
        self.ready()
        for field,value in [('qualification_id','0'*64),('profile','S'),('configs',[]),
                            ('parser',{}),('operational_limits_override',{'effective_timeout_seconds':12})]:
            with self.subTest(field=field):
                s=copy.deepcopy(self.spec);s[field]=value
                with self.assertRaises(ValueError):self.auth.guard(self.item,s)
        for path in (Path(self.qref['path']),self.parser,self.config,Path(self.schema['path']),Path(self.producer['path'])):
            b=path.read_bytes();path.write_bytes(b+b' ')
            with self.assertRaises(ValueError):self.auth.guard(self.item,self.spec)
            path.write_bytes(b)
        self.assertTrue(self.auth.guard(self.item,self.spec))

    def test_06_exact_input_only(self):
        self.ready()
        for field,value in [('selection_id','OTHER'),('scientific_scope','S_F'),('condition_id','OTHER')]:
            s=copy.deepcopy(self.spec);s[field]=value
            with self.assertRaises(ValueError):self.auth.guard(self.item,s)
        s=copy.deepcopy(self.spec);s['identity']['trace_content_sha256']='0'*64
        with self.assertRaises(ValueError):self.auth.guard(self.item,s)

    def test_07_one_reservation(self):
        self.reserve()
        for change in ({},{'condition_id':'OTHER'},{'budget_bucket':'contingency'}):
            s=copy.deepcopy(self.spec);s.update(change)
            with self.assertRaises(ValueError):self.auth.reserve_synthetic(self.item,s,self.resources)
        self.assertEqual(len(self.item['attempts']),51)
        self.assertEqual(self.item['actual_starts'],50)

    def test_08_old_batch_sealed(self):
        self.reserve()
        self.assertEqual(p.sha(self.item['workload_pipeline_batches']),self.seal['old_workload'])
        old=copy.deepcopy(self.spec);old.update(condition_id='V4_SGEMM_MAIN61_EXPLORATORY_F')
        with self.assertRaises(ValueError):self.auth.guard(self.item,old)
        self.assertTrue(self.auth.active(self.item))
        x=copy.deepcopy(self.item)
        x[p.FIELD]['binding']['identity']['binary_sha256']='1'*64
        x['attempts'][-1]['identity']['binary_sha256']='1'*64
        x['attempts'][-1]['run_key']=p.sha(x['attempts'][-1]['identity'])
        with self.assertRaisesRegex(ValueError,'bound identity'):self.auth.active(x)

    def test_09_old50_prefix_immutable(self):
        self.reserve()
        self.assertEqual(p.sha(self.item['attempts'][:50]),self.seal['old50'])
        self.item['attempts'][0]['actual_start']=False
        with self.assertRaisesRegex(ValueError,'old50'):self.auth.active(self.item)

    def test_10_old_records_contracts_immutable(self):
        self.ready()
        for group in ('accepted_results','accepted_pairs','scientific_holds','qualifications','input_selections'):
            x=copy.deepcopy(self.item)
            if self.seal['records'][group]:
                key=next(iter(self.seal['records'][group]));x[group][key]={'changed':True}
                with self.assertRaises(ValueError):self.auth.active(x)
        for group in ('accepted_results','accepted_pairs','input_selections','qualifications','scientific_holds'):
            x=copy.deepcopy(self.item);x[group]['UNAUTHORIZED_NEW_RECORD']={'changed':True}
            with self.assertRaises(ValueError):self.auth.active(x)
        for key in ('reservations','full_system_matrix','capacity_diagnostic_runtime','additional_results_max_bytes'):
            x=copy.deepcopy(self.item);x[key]=None
            with self.assertRaises(ValueError):self.auth.active(x)

    def test_11_single_controller_start_gate(self):
        self.reserve()
        with self.assertRaisesRegex(ValueError,'singleton'):
            self.auth.start_synthetic(self.item,lambda:{'synthetic_fixture':True},owns_controller=False)
        self.assertEqual(self.item['actual_starts'],50)

    def test_12_fake_actual_start_failure_charged(self):
        self.start()
        self.assertEqual(self.item['actual_starts'],51)
        self.auth.finish_synthetic(self.item,'RESOURCE_LIMIT',{})
        self.assertEqual(self.item['actual_starts'],51)
        with self.assertRaises(ValueError):self.auth.reserve_synthetic(self.item,self.spec,self.resources)
        self.item['attempts'][-1]['actual_start']=False
        with self.assertRaisesRegex(ValueError,'refund'):self.auth.active(self.item)

    def test_13_spawn_intent_and_crash(self):
        self.reserve()
        def fail():raise OSError('SYNTHETIC failed spawn')
        self.assertIsNone(self.auth.start_synthetic(self.item,fail,owns_controller=True))
        self.assertEqual(self.item['actual_starts'],50)
        with self.assertRaises(ValueError):self.auth.guard(self.item,self.spec)
        self.item['attempts'][-1]['state']='START_INTENT_UNRECONCILED'
        with self.assertRaises(ValueError):self.auth.start_synthetic(self.item,lambda:{'synthetic_fixture':True},owns_controller=True)

    def test_14_resources_guard_and_high_io_allowed(self):
        self.ready()
        self.auth.resource_guard(self.spec,self.resources)
        for field,value in [('workspace_free_bytes',6*p.GIB),('share_free_bytes',39*p.GIB),
            ('available_memory_bytes',63*p.GIB),('reserved_cpu_units',8),
            ('reserved_memory_bytes',32*p.GIB),('new_bytes',10*p.GIB),('total_bytes',24*p.GIB)]:
            r=copy.deepcopy(self.resources);r[field]=value
            with self.assertRaises(ValueError):self.auth.resource_guard(self.spec,r)

    def test_15_queue_no_union(self):
        self.ready();single={'specs':[{'sha256':p.spec_sha(self.spec)}],'pairs':[]}
        self.auth.queue_guard(self.item,single,self.spec)
        for q in ({**single,'pairs':[{}]},{**single,'specs':single['specs']*2},
                  {**single,'specs':[{'sha256':'0'*64}]}):
            with self.assertRaises(ValueError):self.auth.queue_guard(self.item,q,self.spec)

    def test_16_diagnostic_validator_required(self):
        self.start()
        t=self.terminal();t['observer_validation']='UNKNOWN_OVERFLOW'
        with self.assertRaises(ValueError):self.auth.finish_synthetic(self.item,'COMPLETE_VALID',t)
        t['observer_validation']='PASS';t['observed_detached']=0
        self.auth.finish_synthetic(self.item,'COMPLETE_VALID',t)
        self.assertEqual(self.item['attempts'][-1]['state'],'COMPLETE_VALID')

    def test_17_diagnostic_point_not_pair(self):
        self.start();self.auth.finish_synthetic(self.item,'COMPLETE_VALID',self.terminal())
        point=self.item['accepted_results']['SYNTHETIC_E051']
        with self.assertRaises(ValueError):self.auth.reject_pair({'scientific_scope':'OLD'},point)
        self.assertEqual(self.item['accepted_pairs'],self.before_pairs)

    def test_18_durable_exit_and_full_closure_required(self):
        self.start()
        for field,value in [('exit_code',1),('wait_status',15),('stop_reason',{'RESOURCE':'stop'}),
                            ('instructions',1),('slices',63),('drained',False),('native_process',{})]:
            t=self.terminal();t[field]=value
            with self.assertRaises(ValueError):self.auth.finish_synthetic(self.item,'COMPLETE_VALID',t)

    def test_19_failure_hold_and_delivery_scope(self):
        self.start();self.auth.finish_synthetic(self.item,'FAILED',{})
        self.assertIn('qualification:'+self.spec['qualification_id'],self.item['scientific_holds'])
        self.assertEqual(self.item['actual_starts'],51)
        self.assertNotIn('SYNTHETIC_E051',self.item['accepted_results'])
        self.assertEqual(self.item['accepted_pairs'],self.before_pairs)

    def test_20_authority_and_production_synthetic_refusal(self):
        production=p.Authority(self.auth.manifest_path,self.auth.manifest_sha256,
            self.auth.approval_path,self.auth.approval_sha256)
        with self.assertRaisesRegex(ValueError,'cannot activate production'):production.authority()
        path=self.auth.manifest_path;b=path.read_bytes();path.write_bytes(b+b' ')
        with self.assertRaisesRegex(ValueError,'manifest bytes'):self.auth.authority()
        path.write_bytes(b)
        path=self.auth.approval_path;path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'approval bytes'):self.auth.authority()

    def test_22_coordinated_refund_with_retained_witness_rejected(self):
        self.start()
        self.auth.finish_synthetic(self.item,'RESOURCE_LIMIT',{})
        a=self.item['attempts'][-1]
        a.update(state='CANCELLED_BEFORE_START',actual_start=False)
        self.item['actual_starts']=50
        with self.assertRaisesRegex(ValueError,'witness|refund'):self.auth.active(self.item)
        for key in ('process','started_unix','started_identity','immutable_started_marker'):
            a.pop(key,None)
        with self.assertRaisesRegex(ValueError,'witness'):self.auth.active(self.item)

    def test_23_witness_identity_and_terminal_retention(self):
        self.start()
        witness=copy.deepcopy(self.item[p.FIELD]['start_witness'])
        self.auth.finish_synthetic(self.item,'FAILED',{})
        self.assertEqual(witness,self.item[p.FIELD]['start_witness'])
        self.assertEqual(self.item['attempts'][-1]['process'],witness['process'])
        self.item['attempts'][-1]['process']['start_ticks']='CHANGED'
        with self.assertRaisesRegex(ValueError,'witness'):self.auth.active(self.item)

    def test_24_production_rejects_synthetic_Q_and_producer(self):
        self.manifest['deployment_state']='E_SEALED_FORMAL_RELEASE'
        self.manifest['producer_publication_commit']='f'*40
        self.approval['synthetic_fixture']=False
        self.refresh_authority()
        prod=p.Authority(self.auth.manifest_path,self.auth.manifest_sha256,
                         self.auth.approval_path,self.auth.approval_sha256)
        m=prod.authority()
        with self.assertRaisesRegex(ValueError,'synthetic Q/producer'):prod.check_spec(m,self.spec)
        qpath=Path(self.qref['path']);q=json.loads(qpath.read_text());q['synthetic_fixture']=False
        self.qref=write(qpath,q);self.spec['qualification_id']=self.qref['sha256']
        self.manifest['scientific_binding']['qualification']=self.qref
        self.manifest['scientific_binding']['spec_sha256']=p.spec_sha(self.spec)
        self.approval['manifest_scientific_binding_sha256']=p.sha(self.manifest['scientific_binding'])
        self.refresh_authority()
        prod=p.Authority(self.auth.manifest_path,self.auth.manifest_sha256,
                         self.auth.approval_path,self.auth.approval_sha256)
        with self.assertRaisesRegex(ValueError,'synthetic Q/producer'):prod.check_spec(prod.authority(),self.spec)

    def test_21_no_side_effects_no_real_process(self):
        self.start();self.auth.finish_synthetic(self.item,'COMPLETE_VALID',self.terminal())
        self.assertEqual(LIVE.read_bytes(),LIVE_BYTES)
        self.assertEqual(p.old_seal(self.item)['old50'],self.seal['old50'])
        with self.assertRaises(AssertionError):
            import subprocess
            subprocess.Popen(['SYNTHETIC_DO_NOT_EXECUTE'])
        write(self.root/'synthetic_registry.json',self.item)
        self.assertTrue(str(self.root).startswith('/tmp/e2_detach_central_candidate/'))


if __name__=='__main__':unittest.main(verbosity=2)
