"""All data/backend methods here are fake CPU fixtures, never scientific proof."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch

S=Path(__file__).with_name('oracle_closed_postprocess.py')
spec=importlib.util.spec_from_file_location('cpu_mock_closer',S)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v)+'\n')

class Fixtures(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_closed_')
        self.root=Path(self.tmp.name)/'initial8';self.c='MOCK_NOT_SCIENCE_COHORT'
        self.uuid='MOCK_NOT_SCIENCE_UUID'
        self.out=self.root/'DTC/run/results'/self.uuid
        self.out.mkdir(parents=True)
        (self.out/'raw.log.gz').write_bytes(b'MOCK_NOT_SCIENCE_RAW_NOT_GZIP')
        self.i=dict(uuid=self.uuid,cohort=self.c,output=str(self.out))
        ledger=self.root/'control/qualification_ledger'
        put(ledger/(self.c+'.INTENT.json'),self.i)
        self.d=dict(uuid=self.uuid,cohort=self.c,new_attempt_consumed=1,automatic_retry=False,
                    stop_reason=None,launcher_wait_returncode=0,native_simulator_observed=True,
                    raw_sha256=m.sha(self.out/'raw.log.gz'))
        put(ledger/(self.c+'.DONE.json'),self.d);put(self.out/'NATIVE_EXIT.json',self.d)
        put(self.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=999999999,start_ticks=1))
        self.q=dict(request=m.REQUEST,budget=32,remaining=31,consumed={self.c:dict(uuid=self.uuid,
            intent_sha256=m.sha(ledger/(self.c+'.INTENT.json')),execution_receipt=self.d)})

    def tearDown(self):self.tmp.cleanup()

    def identity(self):return m.snapshot_identity(self.root,self.c,self.q['consumed'])

    def test_natural_read_only(self):
        before={str(p):m.sha(p) for p in self.root.rglob('*')if p.is_file()}
        self.assertEqual(self.identity()['uuid'],self.uuid)
        self.assertEqual(before,{str(p):m.sha(p) for p in self.root.rglob('*')if p.is_file()})

    def test_unconsumed_rejected(self):
        with self.assertRaises(m.Hold):m.snapshot_identity(self.root,self.c,{})

    def test_cohort_traversal(self):
        for c in ['../bad','bad/x']:
            with self.assertRaises(m.Hold):m.snapshot_identity(self.root,c,{})

    def test_tampered_intent(self):
        put(self.root/'control/qualification_ledger'/(self.c+'.INTENT.json'),dict(self.i,x=1))
        with self.assertRaises(m.Hold):self.identity()

    def test_mismatched_receipt(self):
        put(self.out/'NATIVE_EXIT.json',dict(self.d,automatic_retry=True))
        with self.assertRaises(m.Hold):self.identity()

    def test_raw_tamper(self):
        (self.out/'raw.log.gz').write_bytes(b'tampered')
        with self.assertRaises(m.Hold):self.identity()

    def test_live_model_rejected(self):
        with patch.object(m,'proc_start',return_value=1):
            with self.assertRaises(m.Hold):self.identity()

    def test_early_stop_not_reclassified(self):
        for change in [dict(stop_reason='MOCK_STOP'),dict(launcher_wait_returncode=1),dict(native_simulator_observed=False),dict(automatic_retry=True),dict(new_attempt_consumed=2)]:
            d=dict(self.d,**change);q=copy.deepcopy(self.q);q['consumed'][self.c]['execution_receipt']=d
            put(self.root/'control/qualification_ledger'/(self.c+'.DONE.json'),d)
            put(self.out/'NATIVE_EXIT.json',d)
            with self.assertRaises(m.Hold):m.snapshot_identity(self.root,self.c,q['consumed'])

    def session(self,verifier_delta=None):
        mutex=self.root.parent/'control/OWNER_RECOVERY_AND_CLOSEOUT.lock'
        plan=self.root/'control/EXECUTION_PLAN.json';put(plan,{'MOCK_NOT_SCIENCE':True})
        verifier=self.root.parent/'MOCK_VERIFIER.py';verifier.write_text('# MOCK_NOT_SCIENCE\n')
        alias=self.root.parent/'MOCK_ALIAS.py';alias.write_text('# MOCK_NOT_SCIENCE\n')
        sparse=self.root.parent/'MOCK_SPARSE.py';sparse.write_text('# MOCK_NOT_SCIENCE\n')
        cfg=dict(stage_root=str(self.root),request=m.REQUEST,execution_mode='OWNER_IMAGE_CLOSEOUT',
                 actual_execution_authorized=True,new_scientific_starts=0,governance_lock=str(mutex),
                 admission_verifier=dict(path=str(verifier),sha256=m.sha(verifier)),
                 alias_hook=dict(path=str(alias),sha256=m.sha(alias)),
                 sparse_hook=dict(path=str(sparse),sha256=m.sha(sparse)))
        auth=self.root.parent/'MOCK_AUTH.json'
        put(auth,dict(status='AUTHORIZED_CLOSED_ONLY',request=m.REQUEST,runner_sha256=m.sha(S),
                      admission_verifier=cfg['admission_verifier'],execution_mode=cfg['execution_mode'],
                      governance_lock=str(mutex),authorized_closed_cohorts=[self.c]))
        cfg['authorization']=dict(path=str(auth),sha256=m.sha(auth))
        def verify(ctx,config):
            value=dict(ctx,status='PASS',original_closer_threads_excluded=True,owner_recovery_excluded=True,
                        new_scientific_starts_permitted=False,independent_quiescence_or_retirement_review='PASS',
                        observed_monotonic_ns=time.monotonic_ns(),valid_until_monotonic_ns=time.monotonic_ns()+10**9)
            value.update(verifier_delta or {});return value
        engine=types.SimpleNamespace(registered=lambda:(None,None,copy.deepcopy(self.q),{}))
        self.calls=[]
        mock_proof=dict(MOCK_NOT_SCIENCE=True,performance_accepted=True,cycles=123)
        mock_archive=dict(MOCK_NOT_SCIENCE=True)
        put(self.out/'L2_STRICT.json',mock_proof)
        result=dict(state='MOCK_NOT_SCIENCE_ACCEPTED',cohort=self.c,uuid=self.uuid,
                    proof=mock_proof,archive=mock_archive,cycles=123)
        def finish(c):
            self.calls.append(('finish',c));rp=self.root/'analysis'/(c+'.RESULT.json')
            if rp.exists():return m.read(rp)
            put(rp,result);return result
        def verify_archive(c):self.calls.append(('verify_archive',c));return dict(MOCK_NOT_SCIENCE=True)
        consumer=types.SimpleNamespace(finish_evidence=finish,load=lambda n,f:engine if f=='oracle_native.py'else types.SimpleNamespace(verify=verify_archive))
        stack=__import__('contextlib').ExitStack()
        stack.enter_context(patch.object(m,'ROOT',self.root));stack.enter_context(patch.object(m,'MUTEX',mutex))
        stack.enter_context(patch.object(m,'PLAN_SHA',m.sha(plan)))
        stack.enter_context(patch.object(m,'_load_consumer',return_value=consumer))
        stack.enter_context(patch.object(m,'load',return_value=types.SimpleNamespace(verify_closeout_admission=verify)))
        return stack,cfg

    def test_mock_close_and_adopt(self):
        stack,cfg=self.session()
        with stack:
            with m.CloseoutSession(cfg) as session:
                session.finish(self.c);before=m.sha(self.root/'analysis'/(self.c+'.RESULT.json'))
                session.finish(self.c)
                self.assertEqual(m.sha(self.root/'analysis'/(self.c+'.RESULT.json')),before)
                self.assertTrue(session.events[-1]['adopted_existing_result'])
        self.assertEqual(len(list((self.root.parent/'control/CLOSED_POSTPROCESS_AUDIT').glob('*.json'))),4)
        self.assertEqual([c[0]for c in self.calls],['finish','verify_archive','finish','verify_archive'])

    def test_no_main_authorization(self):
        stack,cfg=self.session();cfg['actual_execution_authorized']=False
        with stack,self.assertRaises(m.Hold):
            with m.CloseoutSession(cfg):pass
        self.assertFalse(self.calls)

    def test_r24_rejected(self):
        stack,cfg=self.session();cfg['stage_root']=str(self.root.parent/'remaining24')
        with stack,self.assertRaises(m.Hold):
            with m.CloseoutSession(cfg):pass

    def test_governance_mutex_really_exclusive(self):
        stack,cfg=self.session()
        with stack:
            with m.CloseoutSession(cfg):
                with self.assertRaises(BlockingIOError):
                    with m.CloseoutSession(cfg):pass

    def test_stale_verifier_rejected(self):
        stack,cfg=self.session({'valid_until_monotonic_ns':1})
        with stack,self.assertRaises(m.Hold):
            with m.CloseoutSession(cfg):pass

    def test_foreign_thread_rejected(self):
        stack,cfg=self.session();errors=[]
        with stack:
            with m.CloseoutSession(cfg) as session:
                def other():
                    try:session.finish(self.c)
                    except m.Hold as e:errors.append(str(e))
                t=threading.Thread(target=other);t.start();t.join()
        self.assertEqual(errors,['ONE_CLOSEOUT_THREAD_ONLY'])

    def test_unreleased_cohort_rejected(self):
        stack,cfg=self.session()
        with stack:
            with m.CloseoutSession(cfg) as session,self.assertRaises(m.Hold):session.finish('OTHER')
        self.assertFalse(self.calls)

    def receipt_peer(self):
        c='MOCK_NOT_SCIENCE_PEER';u='MOCK_NOT_SCIENCE_PEER_UUID'
        out=self.root/'DTC/run/results'/u;out.mkdir(parents=True)
        (out/'raw.log.gz').write_bytes(b'MOCK_PEER_RAW')
        i=dict(uuid=u,cohort=c,output=str(out));ledger=self.root/'control/qualification_ledger'
        put(ledger/(c+'.INTENT.json'),i)
        d=dict(self.d,cohort=c,uuid=u,raw_sha256=m.sha(out/'raw.log.gz'))
        put(ledger/(c+'.DONE.json'),d);put(out/'NATIVE_EXIT.json',d)
        before=copy.deepcopy(self.q);before['consumed'][c]=dict(uuid=u,intent_sha256=m.sha(ledger/(c+'.INTENT.json')),charged=1)
        after=copy.deepcopy(before);after['consumed'][c]['execution_receipt']=d
        return before,after,c

    def test_existing_peer_natural_receipt_addition_allowed(self):
        before,after,c=self.receipt_peer()
        self.assertEqual(m.verify_request_monotonic(before,after,self.root)[0]['cohort'],c)

    def test_budget_uuid_existing_receipt_and_unproven_additions_rejected(self):
        before,after,c=self.receipt_peer()
        mutations=[]
        x=copy.deepcopy(after);x['budget']+=1;mutations.append(x)
        x=copy.deepcopy(after);x['consumed'][c]['uuid']='OTHER';mutations.append(x)
        x=copy.deepcopy(after);x['consumed'][self.c]['execution_receipt']['raw_sha256']='bad';mutations.append(x)
        x=copy.deepcopy(after);x['consumed'][c]['execution_receipt']['launcher_wait_returncode']=42;mutations.append(x)
        x=copy.deepcopy(after);x['consumed']['NEW']={};mutations.append(x)
        for x in mutations:
            with self.assertRaises(m.Hold):m.verify_request_monotonic(before,x,self.root)

if __name__=='__main__':unittest.main(verbosity=2)
