"""Bounded control-tool tests. No simulator, compiler or scientific fixture runs."""
import copy
import fcntl
import json
import os
from pathlib import Path
import tempfile
import shutil
import multiprocessing
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import coordinator as c

class ControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="ep_l2_ms_control_test_",dir="/workspace");self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/c.FIELD).mkdir()
        self.output=self.root/'output';self.output.mkdir()
        self.bin=self.root/'binary';self.bin.write_bytes(b'control fixture, not a simulator')
        self.identity={'core_source_commit':'1'*40,'framework_source_commit':'2'*40,'binary_sha256':c.digest(self.bin),
          'runtime_config_sha256':'4'*64,'trace_content_sha256':'5'*64,'workload':'fixture',
          'epoch_range':{'scope':'full_application'},'feature_vector':{'finite_wbuf':True},
          'ideal_vector':{'copy_free':False},'termination_contract':{'full':True}}
        self.ledger={'campaign_id':c.CAMPAIGN,'authority_commit':c.AUTHORITY,'maximum_actual_starts':24,
          'start_deadline_unix':c.START_DEADLINE,'additional_results_max_bytes':6*c.GIB,'old_plus_new_results_max_bytes':20*c.GIB,
          'host':c.socket.gethostname(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
          'attempts':[],'reservations':{'local_diagnostics':10,'new_input_controls':4,'victim':3,'readonly':4,'contingency':3},
          'input_selections':{},'qualifications':{},'accepted_results':{},'accepted_pairs':{},'controller':None}
        self.policy={'boot_id':self.ledger['boot_id'],'max_simulators':4,'max_cpu_units':8,
          'max_reserved_memory_bytes':32*c.GIB,'min_available_memory_bytes':64*c.GIB,
          'min_disk_free_bytes':48*c.GIB,'max_build_jobs':4,'scan_exclusive':True}
        self.data={'authority_host':c.socket.gethostname(),'hosts':{c.socket.gethostname():self.policy},
          'runs':{},'resource_leases':{},'campaigns':{'OLD':{'maximum_starts':72,'used':51}},c.FIELD:self.ledger}
        self.live={'available_memory_bytes':160*c.GIB,'disk_free_bytes':80*c.GIB,'share_disk_free_bytes':41*c.GIB}
        self.usage={'old_bytes':13*c.GIB,'new_bytes':0,'total_bytes':13*c.GIB}
        selection={'campaign_id':c.CAMPAIGN,'selected_by':'D','selection_unix':1792410000,
          'selection_id':'fixture','rationale':'control tool test','full_input_identity':{'trace_content_sha256':'5'*64,
          'runtime_independent_input_source':'fixture','expected_full_instructions':10,'comparison_groups':['g']}}
        sp=self.root/'selection.json';sp.write_text(json.dumps(selection));self.ledger['input_selections']['fixture']={
          'path':str(sp),'sha256':c.digest(sp),'selection':selection}
        q={'source_identity':{k:self.identity[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')},
           'supported_profiles':{'S':{'diagnostic':False}}}
        qp=self.root/'q.json';qp.write_text(json.dumps(q));self.ledger['qualifications']['q']={'path':str(qp),'sha256':c.digest(qp),'qualification':q}
        self.spec={'identity':self.identity,'campaign_id':c.CAMPAIGN,'launch_owner':'E','selection_id':'fixture',
          'qualification_id':'q','profile':'S','profile_semantics':{'diagnostic':False},'comparison_group':'g',
          'budget_bucket':'local_diagnostics','labels':{'diagnostic':False,'subset':None,'oracle':False},'binary':str(self.bin),
          'input_audit':{'identity':self.identity}}
        self.save();self.coord=c.Coordinator(self.root)
        for target,value in [('OUTPUT',self.output)]:self.enterContext(patch.object(c,target,value))
        self.enterContext(patch.object(c,'local_resources',return_value=self.live))
        self.enterContext(patch.object(c,'output_usage',return_value=self.usage))

    def save(self): (self.root/'RUN_REGISTRY.json').write_text(json.dumps(self.data))
    def read(self):return json.loads((self.root/'RUN_REGISTRY.json').read_text())
    def gate(self,kind='simulation',cpu=1,memory=8*c.GIB,growth=c.FULL_GROWTH):
        c.resource_gate(self.data,kind,cpu,memory,growth,self.live,self.usage)
    def row(self,**kw):
        value={'host':c.socket.gethostname(),'status':'RUNNING','cpu_units':1,'memory_bytes':8*c.GIB,
          'scan':False,'experiment_id':c.CAMPAIGN,'result_directory':str(self.output/'missing'),'disk_growth_bytes':c.FULL_GROWTH}
        value.update(kw);return value

    def test_physical_48g_floor(self):
        self.live['disk_free_bytes']=48*c.GIB-1
        with self.assertRaisesRegex(ValueError,'workspace'):self.gate()
    def test_floor_does_not_waive_future_growth(self):
        self.live['disk_free_bytes']=50*c.GIB
        with self.assertRaisesRegex(ValueError,'output growth'):self.gate()
    def test_share40g_floor(self):
        self.live['share_disk_free_bytes']=40*c.GIB-1
        with self.assertRaisesRegex(ValueError,'Share'):self.gate()
    def test_64g_memory_after_reservations(self):
        self.data['resource_leases']['b']=self.row(memory_bytes=8*c.GIB)
        self.live['available_memory_bytes']=79*c.GIB
        with self.assertRaisesRegex(ValueError,'64GiB'):self.gate()
    def test_cpu_includes_build_test_and_sim(self):
        self.data['resource_leases']['b']=self.row(cpu_units=8)
        with self.assertRaisesRegex(ValueError,'CPU quota'):self.gate()
    def test_32g_reserved_memory(self):
        self.data['resource_leases']['b']=self.row(memory_bytes=32*c.GIB)
        with self.assertRaisesRegex(ValueError,'memory reservation'):self.gate()
    def test_build_j2(self):
        with self.assertRaisesRegex(ValueError,'-j2'):self.gate('build',3)
    def test_default_two_simulators(self):
        self.data['runs']={str(i):self.row() for i in range(2)}
        with self.assertRaisesRegex(ValueError,'E campaign'):self.gate()
    def test_third_possible_without_build(self):
        self.ledger['target_simulators']=3;self.data['runs']={str(i):self.row(disk_growth_bytes=c.GIB) for i in range(2)};self.gate()
    def test_three_unknown_default_output_reserves_exceed6g(self):
        self.ledger['target_simulators']=3;self.data['runs']={str(i):self.row() for i in range(2)}
        with self.assertRaisesRegex(ValueError,'6GiB'):self.gate()
    def test_third_rejects_pending_build(self):
        self.ledger['target_simulators']=3
        self.data['resource_leases']['b']=self.row(kind='MECHANISM_BUILD')
        with self.assertRaisesRegex(ValueError,'public build'):self.gate()
    def test_global_four_simulators(self):
        self.data['runs']={str(i):self.row(experiment_id='other') for i in range(4)}
        with self.assertRaisesRegex(ValueError,'shared simulator'):self.gate()
    def test_new6g_ceiling(self):
        self.usage.update(new_bytes=5*c.GIB,total_bytes=18*c.GIB)
        with self.assertRaisesRegex(ValueError,'6GiB'):self.gate()
    def test_total20g_ceiling(self):
        self.usage.update(old_bytes=18*c.GIB,total_bytes=18*c.GIB)
        with self.assertRaisesRegex(ValueError,'20GiB'):self.gate()
    def test_exact6g_boundary_is_legal(self):
        self.usage.update(new_bytes=6*c.GIB-c.FULL_GROWTH,total_bytes=19*c.GIB-c.FULL_GROWTH);self.gate()
    def test_forecast_includes_existing_build(self):
        self.data['resource_leases']['b']=self.row(kind='MECHANISM_BUILD',disk_growth_bytes=31*c.GIB)
        with self.assertRaisesRegex(ValueError,'output growth'):self.gate()
    def test_exact_identity_duplicate_not_relaunched(self):
        first=self.coord.reserve_application(self.spec)
        with self.assertRaisesRegex(ValueError,'duplicate'):self.coord.reserve_application(self.spec)
        item=self.coord.snapshot();self.assertEqual(item['actual_starts'],0);self.assertEqual(item['remaining_start_capacity'],23)
    def test_reservation_does_not_charge_actual_start(self):
        self.coord.reserve_application(self.spec);item=self.coord.snapshot();self.assertEqual(item['actual_starts'],0)
        self.assertEqual(len(item['attempts']),1)
    def test_old_campaign_objects_preserved(self):
        self.coord.reserve_application(self.spec);self.assertEqual(self.read()['campaigns'],self.data['campaigns'])
        self.assertEqual(self.read()['hosts'],self.data['hosts'])
    def test_no_old_key_rewrite(self):
        key=c.run_key(self.identity);self.data['runs'][key]=self.row(experiment_id='OLD');self.save()
        with self.assertRaisesRegex(ValueError,'historical key'):self.coord.reserve_application(self.spec)
    def test_actual24_boundary_includes_failures(self):
        self.ledger['attempts']=[{'actual_start':True,'state':'FAILED'} for _ in range(24)];self.save()
        with self.assertRaisesRegex(ValueError,'24 actual'):self.coord.reserve_application(self.spec)
    def test_uncertain_start_is_not_refunded(self):
        self.ledger['attempts']=[{'actual_start':True,'state':'FAILED'} for _ in range(23)]+[{'actual_start':False,'state':'START_INTENT_UNRECONCILED'}];self.save()
        with self.assertRaisesRegex(ValueError,'ambiguous previous start'):self.coord.reserve_application(self.spec)
    def test_expired_deadline(self):
        with patch.object(c.time,'time',return_value=c.START_DEADLINE):
            with self.assertRaisesRegex(ValueError,'deadline'):self.coord.reserve_application(self.spec)
    def test_wrong_source_or_binary(self):
        self.spec['identity']=dict(self.identity,core_source_commit='9'*40)
        with self.assertRaisesRegex(ValueError,'cross-binary'):self.coord.reserve_application(self.spec)
    def test_modified_d_input(self):
        Path(self.ledger['input_selections']['fixture']['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError,'preregistration changed'):self.coord.reserve_application(self.spec)
    def test_wrong_d_trace(self):
        self.spec['identity']=dict(self.identity,trace_content_sha256='9'*64)
        with self.assertRaisesRegex(ValueError,'D input mismatch'):self.coord.reserve_application(self.spec)
    def test_unqualified_mode(self):
        self.spec['profile']='UNQUALIFIED'
        with self.assertRaisesRegex(ValueError,'not independently qualified'):self.coord.reserve_application(self.spec)
    def test_preserve_critical_control_reservations(self):
        self.ledger['attempts']=[{'actual_start':True,'state':'FAILED','run_key':str(i),'budget_bucket':'local_diagnostics'} for i in range(10)];self.save()
        with self.assertRaisesRegex(ValueError,'preserve other controls'):self.coord.reserve_application(self.spec)
    def test_no_automatic_failed_key_retry(self):
        first=self.coord.reserve_application(self.spec);d=self.read();d[c.FIELD]['attempts'][0].update(state='FAILED',actual_start=True)
        d['runs'][first['run_key']]['status']='FAILED';(self.root/'RUN_REGISTRY.json').write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'same-key retry'):self.coord.reserve_application(self.spec)
        self.spec.update(retry_previous_attempt=first['attempt_id'],retry_reason='fixture packaging repair')
        second=self.coord.reserve_application(self.spec);self.assertNotEqual(first['result_directory'],second['result_directory'])
        self.assertEqual(self.coord.snapshot()['actual_starts'],1)
    def test_singleton_controller_lock(self):
        with self.coord.unique_controller():
            with self.assertRaisesRegex(ValueError,'already active'):
                with self.coord.unique_controller():pass
        self.assertEqual(self.coord.snapshot()['controller']['state'],'STOPPED')
    def test_wrong_host(self):
        self.ledger['host']='different-host';self.save()
        with self.assertRaisesRegex(ValueError,'different host'):self.coord.snapshot()
    def test_old_quota_cannot_be_resized(self):
        self.ledger['maximum_actual_starts']=72;self.save()
        with self.assertRaisesRegex(ValueError,'budget/deadline'):self.coord.snapshot()
    def test_output_exception_rejected(self):
        self.ledger['additional_results_max_bytes']=16*c.GIB;self.save()
        with self.assertRaisesRegex(ValueError,'output budget'):self.coord.snapshot()
    def frozen_command(self, attempt):
        path=Path(attempt['result_directory']);path.mkdir()
        shutil.copyfile(self.bin,path/'accel-sim.out')
        return [str(path/'accel-sim.out')],path
    def test_successful_popen_charged_once(self):
        attempt=self.coord.reserve_application(self.spec);cmd,path=self.frozen_command(attempt)
        with self.coord.unique_controller():
            with patch.object(c,'process_identity',side_effect=lambda p: {'pid':p,'start_ticks':42,'boot_id':self.ledger['boot_id']}):
                # Bind the fixture's controller to this mocked stable identity.
                with self.coord.locked() as (_,item):item['controller']['process']=c.process_identity(os.getpid())
                process=self.coord.start_application(attempt['attempt_id'],cmd,path,{},None,
                    lambda *a,**k:SimpleNamespace(pid=99999999))
                self.assertEqual(process.pid,99999999)
                with self.assertRaisesRegex(ValueError,'already started'):
                    self.coord.start_application(attempt['attempt_id'],cmd,path,{},None,lambda *a,**k:None)
        self.assertEqual(self.coord.snapshot()['actual_starts'],1)
        self.assertEqual(self.coord.snapshot()['remaining_start_capacity'],23)
    def test_os_spawn_failure_is_retained_not_charged(self):
        attempt=self.coord.reserve_application(self.spec);cmd,path=self.frozen_command(attempt)
        def fail(*a,**k):raise OSError('fixture spawn failure')
        with self.coord.unique_controller():
            self.assertIsNone(self.coord.start_application(attempt['attempt_id'],cmd,path,{},None,fail))
        item=self.coord.snapshot();self.assertEqual(item['actual_starts'],0)
        self.assertEqual(item['remaining_start_capacity'],24);self.assertEqual(item['attempts'][0]['state'],'FAILED_SPAWN')
        self.assertTrue(path.exists())
    def test_crash_after_durable_intent_is_ambiguous(self):
        attempt=self.coord.reserve_application(self.spec);cmd,path=self.frozen_command(attempt)
        def crash(*a,**k):raise RuntimeError('fixture crash in Popen interval')
        with self.coord.unique_controller():
            with self.assertRaisesRegex(RuntimeError,'Popen interval'):
                self.coord.start_application(attempt['attempt_id'],cmd,path,{},None,crash)
        item=self.coord.snapshot();self.assertEqual(item['actual_starts'],0)
        self.assertEqual(item['uncertain_start_intents'],1);self.assertEqual(item['remaining_start_capacity'],23)
        with self.assertRaisesRegex(ValueError,'ambiguous previous start'):self.coord.reserve_application(self.spec)
    def test_original_permanent_lock_serializes_six_same_key_clients(self):
        # Isolated JSON fixture, production Registry.locked implementation.
        ctx=multiprocessing.get_context('fork');queue=ctx.Queue()
        def claim():
            try:self.coord.reserve_application(self.spec);queue.put('reserved')
            except ValueError as error:queue.put(str(error))
        workers=[ctx.Process(target=claim) for _ in range(6)]
        for worker in workers:worker.start()
        for worker in workers:worker.join(10);self.assertEqual(worker.exitcode,0)
        replies=[queue.get(timeout=2) for _ in workers]
        self.assertEqual(replies.count('reserved'),1)
        self.assertEqual(len(self.coord.snapshot()['attempts']),1)
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_build_lease_shared_and_child_cannot_release_live(self):
        claimed=self.coord.reserve_work('A','build',2,8*c.GIB,c.GIB,self.root/'build')
        key=claimed['lease_id'];self.coord.bind_work_process(key,'A',os.getpid())
        with self.assertRaisesRegex(ValueError,'still alive'):self.coord.release_work(key,'A','fixture completion rejected')
        self.assertEqual(self.read()['resource_leases'][key]['status'],'RESERVED')
    def test_wrong_work_lease_owner_rejected(self):
        claimed=self.coord.reserve_work('A','build',2,8*c.GIB,c.GIB,self.root/'build')
        with self.assertRaisesRegex(ValueError,'wrong lease owner'):
            self.coord.release_work(claimed['lease_id'],'B','not my lease',True)
    def test_never_spawned_work_can_be_cancelled_without_charge(self):
        claimed=self.coord.reserve_work('A','build',2,8*c.GIB,c.GIB,self.root/'build')
        self.coord.release_work(claimed['lease_id'],'A','fixture no child created',True)
        self.assertEqual(self.read()['resource_leases'][claimed['lease_id']]['status'],'RELEASED')
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_build_owner_is_A(self):
        with self.assertRaisesRegex(ValueError,'sole formal build'):self.coord.reserve_work('B','build',2,8*c.GIB,c.GIB,self.root/'build')

if __name__=='__main__':unittest.main()
