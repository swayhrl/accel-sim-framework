"""Three caller integrations against actual Lane5 code, PRIVATE test ledgers.

No central register/claim, actual authorization, compiler, or simulation.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import types
import unittest

import engineering_pilot as caller

LANE5 = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/util/ep_l2/ft_lane5')
sys.path.insert(0, str(LANE5))
spec = importlib.util.spec_from_file_location('actual_lane5_pilot_test_module', LANE5/'engineering_pilot.py')
backend = importlib.util.module_from_spec(spec); spec.loader.exec_module(backend)
G = caller.GIB


class ActualPublishedAPI(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)/'private-registry'; root.mkdir()
        state = {'authority_host':socket.gethostname(), 'hosts':{socket.gethostname():{
            'boot_id':caller.boot_id(),'max_build_jobs':4,'max_cpu_units':8,
            'max_reserved_memory_bytes':32*G,'min_available_memory_bytes':64*G,
            'min_disk_free_bytes':48*G}},'runs':{},'resource_leases':{}}
        (root/'RUN_REGISTRY.json').write_text(json.dumps(state)); (root/'REGISTRY.lock').touch()
        pins={'core_source_commit':caller.CORE,'framework_source_commit':caller.FRAMEWORK,
              'vendor_commit':caller.VENDOR,'driver_sha256':'a'*64,
              'build_entry_sha256':caller.OFFICIAL_DRIVER_SHA,'repair_commands_sha256':'b'*64}
        locations={k:str(Path(directory)/k) for k in ['core_repo','framework_repo','vendor_repo',
                       'driver_path','build_entry_path','repair_commands_path']}
        outputs=[{'path':str(Path(directory)/n),'resolved_path':str(Path(directory)/n),
                  'filesystem':'workspace'} for n in ['build','audit']]
        request={'pilot_id':'private-fixture-pilot','host':socket.gethostname(),'boot_id':caller.boot_id(),
            'cpu_units':2,'memory_bytes':8*G,'max_duration_seconds':600,
            'execution_identity':pins,'execution_locations':locations,'output_roots':outputs,
            'audit_control_root':str(Path(directory)/'audit')}
        raw=(json.dumps(request,indent=2)+'\n').encode()
        budget={'probe_path':str(Path(directory)),'device':Path(directory).stat().st_dev,
            'mount_signature':'c'*64,'entry_free_bytes':26*G,'hard_stop_free_bytes':12*G,
            'max_pilot_allocated_growth_bytes':4*G,'external_write_reserve_bytes':8*G,
            'monitor_and_kill_overshoot_bytes':2*G,'minimum_untouched_emergency_bytes':10*G,
            'evidence':'SYNTHETIC PRIVATE UNIT FIXTURE ONLY, NOT A REAL ENVELOPE'}
        auth=copy.deepcopy(request);auth.update(schema_version=backend.SCHEMA,status='APPROVED_ENGINEERING_ONLY',
            issuer='lane5',authority_commit=backend.AUTHORITY,token='d'*64,
            request={'sha256':hashlib.sha256(raw).hexdigest(),'publication_commit':'e'*40,'path':'docs/ep_l2/LOW_SPACE_PILOT_REQUEST.json'},
            issued_at_unix=time.time()-60,expires_at_unix=time.time()+600,monitor_interval_seconds=2,
            term_grace_seconds=3,mount_namespace=os.readlink('/proc/self/ns/mnt'),protected_processes=[],
            external_inventory_complete=True,scientific_use='FORBIDDEN_ENGINEERING_EVIDENCE_ONLY',filesystems={'workspace':budget})
        live={'host':socket.gethostname(),'boot_id':caller.boot_id(),'mount_namespace':auth['mount_namespace'],
            'resources':{'disk_free_bytes':28*G,'available_memory_bytes':100*G},
            'filesystems':{'workspace':{'device':budget['device'],'mount_signature':budget['mount_signature'],'available_bytes':28*G}},
            'allocated_growth_bytes':{'workspace':0},'external_health_known':True,'sample_seconds':.001,
            'pilot_rss_bytes':0,'actual_execution_identity':pins}
        # Dependency injection is explicitly prohibited by this real API for
        # the central path. These test roots are private temporary directories.
        api=backend.PilotRegistry(root,sampler=lambda a:copy.deepcopy(live),publication_verifier=lambda a,p:None)
        api.register(auth,raw,{'commit':'e'*40,'path':'docs/ep_l2/LOW_SPACE_PILOT_AUTHORIZATION.json','sha256':'f'*64})
        measured=types.SimpleNamespace(measure_execution_identity=lambda loc:copy.deepcopy(pins))
        bridge=caller.Lane5PilotAdapter(api,measured,raw,auth)
        return root,request,auth,raw,live,api,bridge

    def test_real_api_claim_release_and_restart_replay_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root,req,auth,raw,live,api,bridge=self.fixture(directory)
            lease=bridge.claim(req,auth,{})
            bridge.heartbeat(lease['lease_id'],req['pilot_id'],{})
            report={'status':'PILOT_STOPPED_PRIVATE_FIXTURE','runtime_ready':False}
            bridge.finish(lease['lease_id'],req['pilot_id'],report)
            state=json.loads((root/'RUN_REGISTRY.json').read_text())
            self.assertEqual('RELEASED',state['resource_leases'][lease['lease_id']]['status'])
            self.assertEqual(caller.digest(report['pre_release_receipt_path']),report['central_lease_receipt_sha256'])
            restarted=backend.PilotRegistry(root,sampler=lambda a:copy.deepcopy(live),publication_verifier=lambda a,p:None)
            with self.assertRaisesRegex(ValueError,'replayed'):
                restarted.claim(auth,raw,req['execution_identity'])

    def test_real_stop_is_latched_and_failed_lease_released(self):
        with tempfile.TemporaryDirectory() as directory:
            root,req,auth,raw,live,api,bridge=self.fixture(directory)
            lease=bridge.claim(req,auth,{})
            live['filesystems']['workspace']['available_bytes']=11*G
            with self.assertRaisesRegex(caller.Stop,'LANE5_STOP_LATCHED'):
                bridge.heartbeat(lease['lease_id'],req['pilot_id'],{})
            report={'status':'PILOT_STOPPED_RESOURCE_TEST','runtime_ready':False}
            bridge.finish(lease['lease_id'],req['pilot_id'],report)
            state=json.loads((root/'RUN_REGISTRY.json').read_text())
            self.assertTrue(state['resource_leases'][lease['lease_id']]['stop_latched'])
            self.assertTrue(state['engineering_pilots'][req['pilot_id']]['consumed'])

    def test_real_api_attaches_actual_owned_child_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root,req,auth,raw,live,api,bridge=self.fixture(directory)
            lease=bridge.claim(req,auth,{})
            process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'],start_new_session=True)
            try:
                bridge.record_process(lease['lease_id'],req['pilot_id'],caller.process_info(process.pid),child=process)
                bridge.heartbeat(lease['lease_id'],req['pilot_id'],{})
            finally:
                caller.stop_owned_group(process); process.wait(timeout=3)
                bridge.finish(lease['lease_id'],req['pilot_id'],{'status':'PILOT_STOPPED_PRIVATE_CHILD_TEST'})
            state=json.loads((root/'RUN_REGISTRY.json').read_text())
            self.assertEqual(process.pid,state['resource_leases'][lease['lease_id']]['child_process']['pid'])


if __name__=='__main__':
    unittest.main()
