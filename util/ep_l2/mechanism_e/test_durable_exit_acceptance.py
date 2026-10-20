"""New transport acceptance controls; isolated JSON fixtures, no simulator."""
import copy,json
from pathlib import Path
import unittest
import coordinator as c
import test_coordinator as fixtures

class DurableAcceptanceTests(unittest.TestCase):
    setUp=fixtures.ControlTests.setUp
    save=fixtures.ControlTests.save
    read=fixtures.ControlTests.read
    def endpoint(self):
        self.directory=self.output/'endpoint';self.directory.mkdir();(self.directory/'raw.log').write_text('native raw fixture')
        self.native={'pid':99999997,'start_ticks':2,'boot_id':self.ledger['boot_id']};self.guard={'pid':99999998,'start_ticks':1,'boot_id':self.ledger['boot_id']}
        self.attempt=dict(attempt_id='X',run_key='K',state='RUNNING',actual_start=True,identity=self.identity,process=self.native,exit_collector_process=self.guard,result_directory=str(self.directory),qualification_id='q')
        self.ledger['attempts']=[self.attempt];self.data['runs']['K']=dict(lease_id='X',status='RUNNING');self.save()
        self.exit=dict(native_process=self.native,guardian_process=self.guard,exit_code=0,wait_status=0,stop_reason=None,released_to_native=True,binding=dict(attempt_id='X',run_key='K',identity=self.identity))
        self.record=dict(attempt_id='X',run_key='K',identity=self.identity,status='COMPLETE_VALID',independent_acceptance='PASS',complete_input_verified=True,validation=dict(status='PASS'),raw_log_sha256=c.digest(self.directory/'raw.log'),detail='fixture valid',native_exit_evidence=self.exit)
        return self.record
    def commit(self):
        c.write_json(self.directory/'NATIVE_EXIT.json',self.exit);self.record['native_exit_receipt_sha256']=c.digest(self.directory/'NATIVE_EXIT.json');c.write_json(self.directory/'run_status.json',self.record)
        return self.directory/'run_status.json'
    def test_bound_native_exit0_accepts(self):
        self.endpoint();self.coord.finish_application('X','COMPLETE_VALID',self.commit());self.assertIn('X',self.coord.snapshot()['accepted_results'])
    def test_missing_native_receipt_rejected(self):
        self.endpoint();self.record.pop('native_exit_evidence');p=self.commit()
        with self.assertRaisesRegex(ValueError,'durable native exit receipt missing'):self.coord.finish_application('X','COMPLETE_VALID',p)
    def test_nonzero_kernel_exit_rejected(self):
        self.endpoint();self.exit.update(exit_code=7,wait_status=1792);p=self.commit()
        with self.assertRaisesRegex(ValueError,'exit/owner/start'):self.coord.finish_application('X','COMPLETE_VALID',p)
    def test_wrong_native_start_identity_rejected(self):
        self.endpoint();self.exit['native_process']=dict(self.native,start_ticks=3);p=self.commit()
        with self.assertRaisesRegex(ValueError,'exit/owner/start'):self.coord.finish_application('X','COMPLETE_VALID',p)
    def test_wrong_collector_rejected(self):
        self.endpoint();self.exit['guardian_process']=dict(self.guard,pid=99999996);p=self.commit()
        with self.assertRaisesRegex(ValueError,'exit/owner/start'):self.coord.finish_application('X','COMPLETE_VALID',p)
    def test_wrong_run_binding_rejected(self):
        self.endpoint();self.exit['binding']['run_key']='OTHER';p=self.commit()
        with self.assertRaisesRegex(ValueError,'binding mismatch'):self.coord.finish_application('X','COMPLETE_VALID',p)
    def test_guarded_exit0_never_scientific_pass(self):
        self.endpoint();self.exit['stop_reason']={'kind':'TIMEOUT'};p=self.commit()
        with self.assertRaisesRegex(ValueError,'exit/owner/start'):self.coord.finish_application('X','COMPLETE_VALID',p)
    def test_modified_durable_receipt_rejected(self):
        self.endpoint();p=self.commit();c.write_json(self.directory/'NATIVE_EXIT.json',dict(self.exit,exit_code=7))
        with self.assertRaisesRegex(ValueError,'durable native exit changed'):self.coord.finish_application('X','COMPLETE_VALID',p)
if __name__=='__main__':unittest.main()
