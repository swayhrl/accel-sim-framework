#!/usr/bin/env python3
"""In-memory ownership checks; no Native entry or model is invoked."""
import importlib.util
import hashlib
import os
import pathlib
import sys
import tempfile

HERE=pathlib.Path(__file__).resolve().parent
M=1024**2
FAMILIES={
    'gemm':('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
            'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'),
    'stencil':('EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
               'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1'),
}


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_family(family):
    own,peer=FAMILIES[family]
    runtime_root=os.environ.get('EP_L2_TEST_RUNTIME_ROOT')
    host=(pathlib.Path(runtime_root)/('host_'+family+'_bound_v2') if runtime_root
          else HERE/('host_'+family))
    common=load(host/'ep_perf_common_v2.py','test_common_'+family)
    sys.modules['ep_perf_common_v2']=common
    engine=load(host/'ep_perf_native_wv_modes_draft.py','test_engine_'+family)
    claims={'OWN':dict(request=own,cohort='OWN',state='CLAIMED',host_cpu=128,
                       spec_sha256='hash',estimated_peak_RAM_bytes=5*M,
                       remaining_write_bytes=64*M),
            'PEER':dict(request=peer,cohort='PEER',state='RUNNING',host_cpu=129,
                        spec_sha256='peerhash',estimated_peak_RAM_bytes=7*M,
                        remaining_write_bytes=32*M)}
    updated=[]
    def transaction(op,fn):
        registry={'registered_future_requests':{own:{'reserved_write_bytes':0},
                                                peer:{'reserved_write_bytes':999}}}
        fn(registry)
        updated.append(registry['registered_future_requests'])
    common.transaction=transaction
    reserve=common.publish_own_write_carrier(claims)
    assert reserve==194*M and updated[-1][own]['reserved_write_bytes']==194*M
    assert updated[-1][peer]['reserved_write_bytes']==999
    observed={}
    class Resource:
        @staticmethod
        def snapshot():return {'registry_sha256':'sample'}
        @staticmethod
        def admit(snapshot,ram,writes,policy):
            observed.update(ram=ram,writes=writes,policy=policy)
            return {'pass_admission':True,'hold_reasons':[]}
    engine.module=lambda *args:Resource
    engine.exact=lambda *args:{}
    engine.read=lambda *args:{'claims':claims}
    engine.sha=lambda *args:'hash'
    engine.spec_path=lambda *args:pathlib.Path('unused')
    engine.put=lambda *args,**kwargs:{'path':'in-memory','sha256':'hash'}
    engine.now=lambda :'fixed'
    engine.resource_gate({'cohort':'OWN','resource_module_ref':{},'resource_policy_ref':{}},
                         {'host_cpu':128})
    assert observed['ram']==5*M and observed['writes']==194*M
    assert observed['policy']['requested_request_id']==own
    return {'family':family,'mixed_claims':2,'own_carrier_bytes':reserve,
            'peer_carrier_unchanged':True,'own_pending_RAM_bytes':observed['ram'],
            'own_admission_write_bytes':observed['writes']}


def check_unknown_owner():
    runtime_root=os.environ.get('EP_L2_TEST_RUNTIME_ROOT')
    host=(pathlib.Path(runtime_root)/'host_gemm_bound_v2' if runtime_root
          else HERE/'host_gemm')
    adapter=load(host/'resources_exact5_v2.py','test_unknown_owner_adapter')
    with tempfile.TemporaryDirectory() as folder:
        root=pathlib.Path(folder)
        (root/'control').mkdir()
        (root/'control/DISPATCH_CLAIMS.json').write_text(
            '{"claims":{"X":{"request":"INTRUDER","cohort":"X"}}}')
        reg=root/'registry.json'
        reg.write_text('{"registered_future_requests":{}}')
        digest=hashlib.sha256(reg.read_bytes()).hexdigest()
        epoch=root/'epoch.json'
        epoch.write_text('{"native_registry_sha256":"'+digest+'"}')
        class Prior:
            @staticmethod
            def snapshot():return {'registry_sha256':digest,'foreign_metadata_errors':[]}
        adapter.ROOT=root
        adapter.REG=reg
        adapter.EPOCH=epoch
        adapter.original=lambda :Prior
        result=adapter.snapshot()
        assert result['foreign_metadata_errors']==['unknown exact5 shared claim owner/cohort']
    return {'unknown_shared_claim_owner':'HOLD'}


if __name__=='__main__':
    import json
    print(json.dumps({'family_checks':[check_family(f) for f in ('gemm','stencil')],
                      'unknown_owner':check_unknown_owner()}))
