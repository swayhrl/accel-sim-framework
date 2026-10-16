"""Synthetic isolated-registry tests. Never issues a real central authorization."""
from copy import deepcopy
import json
import multiprocessing
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from engineering_pilot import PilotRegistry, SCHEMA, AUTHORITY, GIB, sha, validate, terminate_owned
from registry import Registry, canonical, process_identity, DEFAULT_ROOT
from test_lane5 import identity


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ep-l2-pilot-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.host = socket.gethostname(); self.boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        self.now = 100
        self.policy = {'boot_id':self.boot,'max_simulators':2,'max_cpu_units':8,
            'max_reserved_memory_bytes':32*GIB,'default_run_memory_bytes':8*GIB,
            'min_available_memory_bytes':64*GIB,'min_disk_free_bytes':48*GIB,
            'max_build_jobs':4,'scan_exclusive':True}
        (self.root/'RUN_REGISTRY.json').write_text(json.dumps({'authority_host':self.host,
            'hosts':{self.host:self.policy},'runs':{},'resource_leases':{}}))
        self.pins = {'core_source_commit':'1'*40,'framework_source_commit':'2'*40,'vendor_commit':'3'*40,
            'driver_sha256':'4'*64,'build_entry_sha256':'5'*64,'repair_commands_sha256':'6'*64}
        output = self.root/'never-built'
        self.request = {'pilot_id':'SYNTHETIC_ONLY_PILOT_01','host':self.host,'boot_id':self.boot,
            'execution_identity':self.pins,'execution_locations':{k:str(self.root/k) for k in ('core_repo','framework_repo','vendor_repo','driver_path','build_entry_path','repair_commands_path')},'output_roots':[{'path':str(output),'resolved_path':str(output.resolve()),'filesystem':'workspace'}],
            'cpu_units':2,'memory_bytes':8*GIB,'max_duration_seconds':120}
        self.raw = canonical(self.request)
        budget = {'probe_path':'/workspace','device':self.root.stat().st_dev,'mount_signature':'a'*64,
            'entry_free_bytes':16*GIB,'hard_stop_free_bytes':9*GIB,'max_pilot_allocated_growth_bytes':2*GIB,
            'external_write_reserve_bytes':2*GIB,'monitor_and_kill_overshoot_bytes':GIB,
            'minimum_untouched_emergency_bytes':8*GIB,'evidence':'SYNTHETIC_TEST_BUDGET_NOT_A_REAL_RESOURCE_FINDING'}
        self.auth = {'schema_version':SCHEMA,'status':'APPROVED_ENGINEERING_ONLY','issuer':'lane5',
            'authority_commit':AUTHORITY,**deepcopy(self.request),'token':'d'*64,
            'request':{'publication_commit':'a'*40,'path':'docs/ep_l2/fixture/LOW_SPACE_PILOT_REQUEST.json','sha256':sha(self.raw)},
            'issued_at_unix':90,'expires_at_unix':1000,'monitor_interval_seconds':2,'term_grace_seconds':1,
            'mount_namespace':'synthetic-test-namespace','scientific_use':'FORBIDDEN_ENGINEERING_EVIDENCE_ONLY',
            'filesystems':{'workspace':budget},'protected_processes':[],'external_inventory_complete':True}
        self.live = {'host':self.host,'boot_id':self.boot,'mount_namespace':'synthetic-test-namespace',
            'resources':{'available_memory_bytes':128*GIB,'disk_free_bytes':20*GIB},
            'filesystems':{'workspace':{'device':self.root.stat().st_dev,'mount_signature':'a'*64,'available_bytes':20*GIB}},
            'allocated_growth_bytes':{'workspace':0},'external_health_known':True,'sample_seconds':0.01,'pilot_rss_bytes':0,'actual_execution_identity':deepcopy(self.pins)}
        self.pub = {'commit':'a'*40,'path':'docs/ep_l2/fixture/LOW_SPACE_PILOT_AUTHORIZATION.json','sha256':'b'*64}
        self.api = self.restart()

    def restart(self):
        def verifier(auth, pub):
            if pub != self.pub:
                raise ValueError('synthetic publication proof mismatch')
        return PilotRegistry(self.root,sampler=lambda auth:deepcopy(self.live),publication_verifier=verifier,clock=lambda:self.now)

    def register(self):
        self.api.register(self.auth,self.raw,self.pub)

    def claim(self):
        return self.api.claim(self.auth,self.raw,self.pins)

    def claim_ready(self):
        self.register(); return self.claim()

    def change_state(self, callback):
        with self.api.registry.locked() as state:
            callback(state)

    def test_01_low_space_pilot_only_ordinary_floor_unchanged(self):
        with patch('registry.local_resources',return_value=self.live['resources']), self.assertRaisesRegex(ValueError,'free-space'):
            Registry(self.root).build_lease('lane1',cpu=2)
        key = self.claim_ready()
        self.assertEqual(self.api.registry.snapshot()['resource_leases'][key]['cpu_units'],2)
        self.api.release(key,self.auth,'COMPLETE_ENGINEERING_ONLY','f'*64)

    def test_02_replay_rejected_after_restart_and_release(self):
        key=self.claim_ready();self.api.release(key,self.auth,'PILOT_STOPPED_TEST','f'*64)
        self.api=self.restart()
        with self.assertRaisesRegex(ValueError,'replayed'):self.claim()
        with self.assertRaisesRegex(ValueError,'already registered'):self.register()

    def test_03_unknown_unregistered_token(self):
        with self.assertRaisesRegex(ValueError,'unknown'):self.claim()

    def test_04_forged_authorization_or_token(self):
        self.register();original=deepcopy(self.auth)
        for field,value in [('token','e'*64),('max_duration_seconds',100)]:
            self.auth=deepcopy(original);self.auth[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'forged'):self.claim()

    def test_05_forged_publication(self):
        bad={**self.pub,'sha256':'c'*64}
        with self.assertRaisesRegex(ValueError,'publication'):self.api.register(self.auth,self.raw,bad)

    def test_06_expired_or_future_permission(self):
        self.register()
        for value in (89,1000,1001):
            self.now=value
            with self.subTest(now=value),self.assertRaisesRegex(ValueError,'expired'):self.claim()

    def test_07_wrong_request_bytes(self):
        with self.assertRaisesRegex(ValueError,'request bytes'):self.api.register(self.auth,self.raw+b' ',self.pub)

    def test_08_each_source_driver_vendor_pin(self):
        self.register()
        for name in self.pins:
            pins=deepcopy(self.pins);pins[name]='f'*len(pins[name])
            with self.subTest(pin=name),self.assertRaisesRegex(ValueError,'pins'):
                self.api.claim(self.auth,self.raw,pins)

    def test_09_wrong_host_boot_namespace(self):
        self.register()
        for name in ('host','boot_id','mount_namespace'):
            original=self.live[name];self.live[name]='wrong'
            with self.subTest(name=name),self.assertRaises(ValueError):self.claim()
            self.live[name]=original

    def test_10_competing_lease_run_and_scan(self):
        self.register()
        for kind in ('resource_leases','runs'):
            self.change_state(lambda s:s[kind].update({'other':{'status':'RESERVED','scan':True}}))
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'competing'):self.claim()
            self.change_state(lambda s:s[kind].clear())

    def test_11_cpu_memory_quota_and_floor(self):
        self.register()
        for name,value in [('max_cpu_units',1),('max_build_jobs',1),('max_reserved_memory_bytes',7*GIB)]:
            self.change_state(lambda s:s['hosts'][self.host].update({name:value}))
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'quota'):self.claim()
            self.change_state(lambda s:s['hosts'][self.host].update({name:self.policy[name]}))
        self.live['resources']['available_memory_bytes']=71*GIB
        with self.assertRaisesRegex(ValueError,'original floor'):self.claim()

    def test_12_budget_terms_positive_and_closed(self):
        for name in ('entry_free_bytes','hard_stop_free_bytes','max_pilot_allocated_growth_bytes','external_write_reserve_bytes','monitor_and_kill_overshoot_bytes','minimum_untouched_emergency_bytes'):
            bad=deepcopy(self.auth);bad['filesystems']['workspace'][name]=0
            with self.subTest(name=name),self.assertRaises(ValueError):validate(bad,self.raw)
        bad=deepcopy(self.auth);bad['filesystems']['workspace']['external_write_reserve_bytes']=40*GIB
        with self.assertRaisesRegex(ValueError,'does not close'):validate(bad,self.raw)

    def test_13_entry_free_and_growth_limit(self):
        self.register();self.live['filesystems']['workspace']['available_bytes']=15*GIB
        with self.assertRaisesRegex(ValueError,'free-space'):self.claim()
        self.live['filesystems']['workspace']['available_bytes']=20*GIB
        self.live['allocated_growth_bytes']['workspace']=2*GIB
        with self.assertRaisesRegex(ValueError,'growth'):self.claim()

    def test_14_device_or_unknown_protected_process(self):
        self.register();self.live['filesystems']['workspace']['device']+=1
        with self.assertRaisesRegex(ValueError,'filesystem'):self.claim()
        self.live['filesystems']['workspace']['device']-=1;self.live['external_health_known']=False
        with self.assertRaisesRegex(ValueError,'project state'):self.claim()

    def test_15_formal_entry_has_priority(self):
        self.register();self.live['resources']['disk_free_bytes']=50*GIB
        with self.assertRaisesRegex(ValueError,'formal build'):self.claim()

    def test_16_pilot_blocks_ordinary_build_and_simulation(self):
        key=self.claim_ready();high={'available_memory_bytes':128*GIB,'disk_free_bytes':100*GIB}
        with patch('registry.local_resources',return_value=high),self.assertRaisesRegex(ValueError,'exclusive'):
            Registry(self.root).build_lease('lane2')
        with self.assertRaisesRegex(ValueError,'exclusive'):
            Registry(self.root).claim(identity(),'lane5','/unused',resources=high)
        with self.assertRaisesRegex(ValueError,'audited release'):Registry(self.root).release_build(key,'lane1')
        self.api.release(key,self.auth,'PILOT_STOPPED_TEST','f'*64)
        with patch('registry.local_resources',return_value=high):ordinary=Registry(self.root).build_lease('lane2')
        Registry(self.root).release_build(ordinary,'lane2')

    def test_17_monitor_reports_each_limit(self):
        key=self.claim_ready();original=deepcopy(self.live)
        self.assertFalse(self.api.monitor(key,self.auth)['stop'])
        mutations=[lambda:self.live['filesystems']['workspace'].update(available_bytes=9*GIB),
            lambda:self.live['allocated_growth_bytes'].update(workspace=2*GIB),
            lambda:self.live['resources'].update(available_memory_bytes=71*GIB),
            lambda:self.live.update(pilot_rss_bytes=8*GIB+1),
            lambda:self.live.update(external_health_known=False),lambda:self.live.update(sample_seconds=3),
            lambda:self.live['filesystems']['workspace'].update(mount_signature='e'*64)]
        for f in mutations:
            self.live=deepcopy(original);f();self.assertTrue(self.api.monitor(key,self.auth)['stop'])
        self.live=deepcopy(original);self.assertTrue(self.api.monitor(key,self.auth)['stop'])

    def test_18_external_reserve_and_heartbeat(self):
        key=self.claim_ready();self.live['filesystems']['workspace']['available_bytes']=17*GIB
        self.assertIn('external reserve exhausted',str(self.api.monitor(key,self.auth)['reasons']))
        self.live['filesystems']['workspace']['available_bytes']=20*GIB;self.now+=3
        self.assertIn('heartbeat',str(self.api.monitor(key,self.auth)['reasons']))
        self.now=221;self.assertIn('deadline',str(self.api.monitor(key,self.auth)['reasons']))

    def test_19_failure_finally_release_and_terminal_immutable(self):
        key=self.claim_ready()
        try:
            raise RuntimeError('synthetic owned command failure')
        except RuntimeError:
            self.api.release(key,self.auth,'PILOT_STOPPED_EXCEPTION','f'*64)
        self.assertEqual(self.api.registry.snapshot()['resource_leases'][key]['status'],'RELEASED')
        with self.assertRaisesRegex(ValueError,'state mismatch'):self.api.release(key,self.auth,'COMPLETE_ENGINEERING_ONLY','f'*64)

    def test_20_no_scientific_promotion_and_no_second_campaign(self):
        key=self.claim_ready()
        with self.assertRaisesRegex(ValueError,'terminal'):self.api.release(key,self.auth,'COMPLETE_VALID','f'*64)
        self.api.release(key,self.auth,'COMPLETE_ENGINEERING_ONLY','f'*64)
        request={**self.request,'pilot_id':'SYNTHETIC_ONLY_PILOT_02'};raw=canonical(request)
        auth={**deepcopy(self.auth),'pilot_id':request['pilot_id']};auth['request']['sha256']=sha(raw)
        with self.assertRaisesRegex(ValueError,'one r8 campaign'):self.api.register(auth,raw,self.pub)

    def test_21_output_existing_symlink_and_wrong_resolution(self):
        self.register();out=Path(self.request['output_roots'][0]['path']);out.mkdir()
        with self.assertRaisesRegex(ValueError,'fresh'):self.claim()
        out.rmdir();out.symlink_to(self.root)
        with self.assertRaisesRegex(ValueError,'resolution|fresh'):self.claim()

    def test_22_real_central_cannot_receive_test_dependencies(self):
        with self.assertRaisesRegex(ValueError,'injection'):PilotRegistry(DEFAULT_ROOT,sampler=lambda a:self.live)

    def test_23_monitor_exception_finally_release(self):
        key=self.claim_ready();self.api.sample=lambda a:(_ for _ in ()).throw(OSError('unreadable FS'))
        with self.assertRaises(OSError):self.api.monitor(key,self.auth)
        self.api.release(key,self.auth,'PILOT_STOPPED_MONITOR_ERROR','f'*64)

    def test_24_reconcile_refuses_live_owner(self):
        key=self.claim_ready()
        with self.assertRaisesRegex(ValueError,'still active'):self.api.reconcile_dead_owner(key,'a'*64)

    def test_25_atomic_multiprocess_one_claim_and_dead_recovery(self):
        self.register();ctx=multiprocessing.get_context('fork');queue=ctx.Queue()
        def worker():
            try:queue.put(('OK',self.claim()))
            except ValueError as e:queue.put(('REFUSED',str(e)))
        children=[ctx.Process(target=worker) for _ in range(3)]
        for c in children:c.start()
        rows=[queue.get(timeout=10) for _ in children]
        for c in children:c.join(timeout=10);self.assertFalse(c.is_alive())
        winners=[v for k,v in rows if k=='OK'];self.assertEqual(len(winners),1)
        self.api.reconcile_dead_owner(winners[0],'b'*64)
        with self.assertRaisesRegex(ValueError,'replayed'):self.claim()

    def test_26_owned_stop_leaves_unrelated_child_alive(self):
        key=self.claim_ready();cmd=[sys.executable,'-c','import time;time.sleep(30)']
        pilot=subprocess.Popen(cmd,start_new_session=True);unrelated=subprocess.Popen(cmd,start_new_session=True)
        try:
            self.api.attach_process(key,self.auth,pilot)
            with self.assertRaisesRegex(ValueError,'child is active'):self.api.release(key,self.auth,'PILOT_STOPPED_TEST','f'*64)
            self.live['filesystems']['workspace']['available_bytes']=8*GIB
            self.assertTrue(self.api.monitor(key,self.auth)['stop'])
            terminate_owned(pilot,process_identity(pilot.pid));self.assertIsNone(unrelated.poll())
            self.api.release(key,self.auth,'PILOT_STOPPED_RESOURCE','f'*64)
        finally:
            for p in (pilot,unrelated):
                if p.poll() is None:p.kill()
                p.wait(timeout=3)

    def test_27_pid_mismatch_refuses_signal(self):
        p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True)
        try:
            bad={**process_identity(p.pid),'start_ticks':0}
            with self.assertRaisesRegex(ValueError,'identity'):terminate_owned(p,bad)
            self.assertIsNone(p.poll())
        finally:
            p.kill();p.wait(timeout=3)

    def test_29_stop_is_latched_and_cannot_report_success(self):
        key=self.claim_ready();self.live['external_health_known']=False
        self.assertTrue(self.api.monitor(key,self.auth)['stop'])
        self.live['external_health_known']=True
        self.assertIn('previous STOP',str(self.api.monitor(key,self.auth)['reasons']))
        with self.assertRaisesRegex(ValueError,'cannot report'):self.api.release(key,self.auth,'COMPLETE_ENGINEERING_ONLY','f'*64)
        self.api.release(key,self.auth,'PILOT_STOPPED_EXTERNAL_STATE','f'*64)

    def test_30_expiry_during_locked_claim(self):
        self.register()
        def slow_sample(auth):
            self.now=1001
            return deepcopy(self.live)
        self.api.sample=slow_sample
        with self.assertRaisesRegex(ValueError,'expired during claim'):self.claim()
        self.assertFalse(self.api.registry.snapshot()['engineering_pilots'][self.auth['pilot_id']]['consumed'])

    def test_31_actual_pins_change_after_registration(self):
        self.register();self.live['actual_execution_identity']['vendor_commit']='e'*40
        with self.assertRaisesRegex(ValueError,'actual source'):self.claim()

    def test_32_each_filesystem_budget_checked(self):
        bad=deepcopy(self.auth)
        bad['filesystems']['second']=deepcopy(bad['filesystems']['workspace'])
        with self.assertRaisesRegex(ValueError,'aliases'):validate(bad,self.raw)
        bad['filesystems']['second']['device']+=1
        bad['filesystems']['second']['external_write_reserve_bytes']=0
        with self.assertRaisesRegex(ValueError,'positive'):validate(bad,self.raw)

    def test_33_hard_stop_must_preserve_emergency_and_overshoot(self):
        bad=deepcopy(self.auth);bad['filesystems']['workspace']['hard_stop_free_bytes']=8*GIB
        with self.assertRaisesRegex(ValueError,'hard-stop'):validate(bad,self.raw)

    def test_34_source_pin_change_stops_running_pilot(self):
        key=self.claim_ready();self.live['actual_execution_identity']['driver_sha256']='e'*64
        self.assertIn('actual source',str(self.api.monitor(key,self.auth)['reasons']))

    def test_28_term_kill_escalation(self):
        p=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print("READY",flush=True);time.sleep(30)'],start_new_session=True,stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(p.stdout.readline().strip(),'READY')
            self.assertEqual(terminate_owned(p,process_identity(p.pid),0.05),-9)
        finally:
            if p.poll() is None:p.kill()
            p.wait(timeout=3);p.stdout.close()


if __name__ == '__main__':
    unittest.main()
