"""Affected policy controls only: never compile, simulate or modify real shared state."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch,Mock
import coordinator as c
import disk_policy as d
import runner
import test_coordinator as f

class WorkspacePolicyTests(unittest.TestCase):
    setUp=f.ControlTests.setUp
    save=f.ControlTests.save
    read=f.ControlTests.read
    row=f.ControlTests.row
    def amend(self):
        self.ledger['t0_unix']=1792414193
        self.save();return self.coord.adopt_workspace_5g('User explicitly changes 48GiB to5GiB for existing EP-L2 campaign.')
    def gate(self,kind='build',growth=c.GIB):
        return c.resource_gate(self.read(),kind,1,c.GIB,growth,self.live,self.usage)
    def test_exact_forecast_boundary_pass(self):
        self.amend();self.live['disk_free_bytes']=8*c.GIB;self.gate()
    def test_one_byte_below_forecast_rejected(self):
        self.amend();self.live['disk_free_bytes']=8*c.GIB-1
        with self.assertRaisesRegex(ValueError,'monitor reserve'):self.gate()
    def test_other_clients_keep48g(self):
        self.amend();self.live['disk_free_bytes']=20*c.GIB
        with self.assertRaisesRegex(ValueError,'workspace'):
            c.Registry.admission(self.read(),c.socket.gethostname(),1,c.GIB,False,'build',self.live)
        self.gate();self.assertEqual(self.read()['hosts'],self.data['hosts'])
    def test_legacy_named_records_not_modified(self):
        self.ledger['disk_authorizations']={'old':{'status':'CONSUMED','expires_unix':1,'disk_floor_bytes':47*c.GIB}}
        self.amend();self.assertEqual(self.read()[c.FIELD]['disk_authorizations'],self.ledger['disk_authorizations'])
    def test_t0_budget_deadlines_and_old_results_preserved(self):
        before=copy.deepcopy(self.data);self.amend();after=self.read()
        for key in ('attempts','reservations','maximum_actual_starts','start_deadline_unix','additional_results_max_bytes','old_plus_new_results_max_bytes'):
            self.assertEqual(before[c.FIELD][key],after[c.FIELD][key])
        self.assertEqual(after[c.FIELD]['t0_unix'],1792414193)
        self.assertEqual(before['campaigns'],after['campaigns'])
    def test_idempotent_no_second_history(self):
        self.amend();self.assertFalse(self.coord.adopt_workspace_5g('5GiB explicit user')['changed']);self.assertEqual(len(self.coord.snapshot()['resource_user_amendments']),1)
    def test_adoption_requires_retired_own_leases(self):
        self.data['resource_leases']['own']=self.row();self.save()
        with self.assertRaisesRegex(ValueError,'safe boundary'):self.amend()
    def test_all_host_pending_growth_and_monitor_reserved(self):
        self.amend();data=self.read();data['resource_leases']['other']=self.row(experiment_id='OTHER',disk_growth_bytes=2*c.GIB,monitor_reserve_bytes=c.GIB)
        self.live['disk_free_bytes']=11*c.GIB-1
        with self.assertRaisesRegex(ValueError,'monitor reserve'):
            c.resource_gate(data,'test',1,c.GIB,c.GIB,self.live,self.usage)
    def test_share40_remains(self):
        self.amend();self.live['share_disk_free_bytes']=40*c.GIB-1
        with self.assertRaisesRegex(ValueError,'Share'):self.gate()
    def test_monitor_cannot_be_waived(self):
        self.amend()
        with self.assertRaisesRegex(ValueError,'cannot be waived'):
            c.resource_gate(self.read(),'test',1,c.GIB,c.GIB,self.live,monitor_reserve_bytes=0)
    def test_wrong_campaign_rejected(self):
        self.amend();row=self.read()[c.FIELD];row['campaign_id']='C16'
        with self.assertRaisesRegex(ValueError,'campaign-scoped'):d.policy(row)
    def test_wrong_floor_or_host_rejected(self):
        self.amend();row=self.read()[c.FIELD];row['workspace_disk_policy']['host']='OTHER'
        with self.assertRaisesRegex(ValueError,'campaign-scoped'):d.policy(row)
    def test_lease_freezes_new_policy(self):
        self.amend();r=self.coord.reserve_work('A','build',2,8*c.GIB,c.GIB,self.root/'build')
        self.assertEqual(r['disk_floor_bytes'],5*c.GIB);self.assertEqual(r['monitor_reserve_bytes'],2*c.GIB)
        self.assertEqual(r['policy_id'],d.POLICY_ID)
    def test_native_lease_same_policy(self):
        self.amend();r=self.coord.reserve_work('E','test',1,4*c.GIB,c.GIB,self.output/'native')
        self.assertEqual(r['disk_floor_bytes'],5*c.GIB)
    def test_application_lease_same_policy(self):
        self.amend();r=self.coord.reserve_application(self.spec)
        self.assertEqual(r['disk_floor_bytes'],5*c.GIB)
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_monitor_stops_before_floor(self):
        p=d.amendment('h','b');r=d.stop_detail({'disk_free_bytes':7*c.GIB},p)
        self.assertEqual(r['status'],'RESOURCE_LIMIT');self.assertGreater(r['observed_free_bytes'],5*c.GIB)
        self.assertIsNone(d.stop_detail({'disk_free_bytes':7*c.GIB+1},p))
    def test_old_lease_still_uses_old_frozen_policy(self):
        r=d.stop_detail({'disk_free_bytes':47*c.GIB},{'disk_floor_bytes':48*c.GIB,'monitor_reserve_bytes':0})
        self.assertEqual(r['disk_floor_bytes'],48*c.GIB)
    def test_runner_resource_limit_retains_evidence_only_stops_owned_process(self):
        self.amend();directory=self.output/'retained_failure'
        attempt=dict(attempt_id='CONTROL',run_key='key',result_directory=str(directory),maximum_result_bytes=c.GIB,**d.lease_policy(self.coord.snapshot()))
        proc=Mock();proc.poll.return_value=None;proc.returncode=-15;proc.pid=123
        fake=Mock();fake.reserve_application.return_value=attempt;fake.start_application.return_value=proc
        q=self.coord.snapshot()['qualifications'];fake.snapshot.return_value={'qualifications':q,'attempts':[dict(attempt_id='CONTROL',state='RUNNING')]}
        spec=dict(self.spec,configs=[],auxiliary_assets=[],trace_files=[dict(name='entry',path=str(self.bin))],entry_trace_name='entry',environment={},timeout_seconds=60)
        audit={'identity':self.identity,'comparison_invariants_sha256':'same','configs':[]}
        live=dict(self.live,disk_free_bytes=7*c.GIB)
        with patch.object(runner,'process_identity',return_value={'pid':123,'start_ticks':77,'boot_id':'controlled-test'}),patch.object(runner,'inspect',return_value=audit),patch.object(runner,'local_resources',return_value=live),patch.object(runner,'output_usage',return_value=self.usage),patch.object(runner.legacy,'process_tree_rss',return_value=1),patch.object(runner.legacy,'terminate_owned') as stop:
            result=runner.execute(spec,fake)
        self.assertEqual(result['status'],'RESOURCE_LIMIT');stop.assert_called_once_with(proc)
        incident=json.loads((directory/'RESOURCE_LIMIT.json').read_text())
        self.assertEqual(incident['process']['start_ticks'],77);self.assertEqual(incident['lease_id'],'CONTROL')
        self.assertEqual(incident['run_key'],'key');self.assertEqual(incident['source_identity'],q['q']['qualification']['source_identity'])
        self.assertEqual(incident['raw_log_sha256'],c.digest(directory/'raw.log'));self.assertEqual(incident['exit_code'],-15)
        self.assertTrue((directory/'raw.log').exists());self.assertTrue((directory/'RESOURCE_LIMIT.json').exists())
        self.assertEqual(json.loads((directory/'run_status.json').read_text())['independent_acceptance'],'NOT_ACCEPTED')
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)

if __name__=='__main__':unittest.main()
