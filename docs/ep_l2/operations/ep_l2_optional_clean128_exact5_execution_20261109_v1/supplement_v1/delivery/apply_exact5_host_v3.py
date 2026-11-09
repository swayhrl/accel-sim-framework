#!/usr/bin/env python3
"""Version only unconsumed exact5 host pins and its two existing owner rows."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
FILES = ('ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py',
         'ep_perf_archive.py','resources_exact5_v2.py')
FAMILIES = {
    'gemm': ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
             ['EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1',
              'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1',
              'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1']),
    'stencil': ('EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
                ['EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
                 'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1']),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    host = ROOT/'runtime/host_gemm_bound_v2'
    common = load(host/'ep_perf_common_v2.py','exact5_amend_common')
    results = []
    with common.locked(common.GLOBAL_MAIN_ADMISSION_LOCK):
        reg, unused = common.authority()
        assert common.read(ROOT/'control/DISPATCH_CLAIMS.json') == {'claims':{}}
        for family,(request,cases) in FAMILIES.items():
            q=reg['registered_future_requests'][request]
            assert not q['consumed'] and q['remaining']==len(cases)
            host=ROOT/'runtime'/('host_'+family+'_bound_v2')
            old={case:common.ref(ROOT/'cases'/case/'control/FROZEN_SPEC.json') for case in cases}
            assert q['admitted_specs']=={case:old[case]['sha256'] for case in cases}
            for filename in FILES:
                current=host/filename
                prior=host/(filename+'.version2')
                candidate=host/(filename+'.candidate_v3')
                assert not prior.exists() and candidate.exists()
                assert candidate.stat().st_size and sha(current)!=sha(candidate)
                prior.write_bytes(current.read_bytes())
                assert sha(prior)==sha(current)
                os.replace(candidate,current)
            qual_path=ROOT/'documents'/('HOST_QUALIFICATION_EXACT5_'+family.upper()+'.json')
            qual_v3=qual_path.with_name(qual_path.stem+'_V3.json')
            assert not qual_v3.exists()
            qual=copy.deepcopy(common.read(qual_path))
            for item in qual['modules']:
                if item['path'] in [str(host/f) for f in FILES]:
                    item['sha256']=sha(item['path'])
            qual['modules'].append(common.ref(host/'resources_exact5_v2.py'))
            qual['supplement']='EP_L2_NATIVE_STORAGE_AND_109_CONTEXT_SUPPLEMENT_20261109_V1'
            common.put(qual_v3,qual,True)
            new_specs={}
            for case in cases:
                p=ROOT/'cases'/case/'control/FROZEN_SPEC.json'
                prior=p.with_name('FROZEN_SPEC.version2.json')
                assert not prior.exists()
                prior.write_bytes(p.read_bytes())
                assert sha(prior)==old[case]['sha256']
                value=copy.deepcopy(common.read(p))
                for field,filename in [('host_common_ref','ep_perf_common_v2.py'),
                                       ('host_engine_ref','ep_perf_native_wv_modes_draft.py'),
                                       ('archive_module_ref','ep_perf_archive.py'),
                                       ('resource_module_ref','resources_exact5_v2.py')]:
                    assert value[field]['path']==str(host/filename)
                    value[field]=common.ref(host/filename)
                value['host_qualification_ref']=common.ref(qual_v3)
                new_specs[case]=value
            local_common=load(host/'ep_perf_common_v2.py','exact5_amend_'+family)
            def amend(registry):
                row=registry['registered_future_requests'][request]
                assert row['admitted_specs']=={case:old[case]['sha256'] for case in cases}
                for case in cases:
                    p=ROOT/'cases'/case/'control/FROZEN_SPEC.json'
                    local_common.put(p,new_specs[case])
                    row['admitted_specs'][case]=sha(p)
                engine_ref=local_common.ref(host/'ep_perf_native_wv_modes_draft.py')
                common_ref=local_common.ref(host/'ep_perf_common_v2.py')
                row['runtime_versions'][engine_ref['sha256']]=dict(engine_ref=engine_ref,common_ref=common_ref)
                row['reserved_write_bytes']=len(cases)*64*1024**2+130*1024**2
                return dict(admitted_specs=row['admitted_specs'],
                            reserved_write_bytes=row['reserved_write_bytes'],
                            engine_ref=engine_ref,common_ref=common_ref)
            changed=local_common.transaction('EXACT5_V3_128M_SHARED_WINDOW_AND_POINT_STAGE_KEEP_BUDGET',amend)
            for case in cases:
                p=ROOT/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'
                if p.exists():
                    version=p.with_name('NATIVE_PRELAUNCH_QUALIFICATION.version2.json')
                    assert not version.exists()
                    p.rename(version)
            amendment=dict(schema='EP_L2_EXACT5_UNCONSUMED_HOST_V3_AMENDMENT',
                request=request,old_specs=old,new=changed,host_qualification_ref=local_common.ref(qual_v3),
                old_host_versions_retained=True,consumed_at_amendment=0,other_owner_rows_unchanged=True)
            local_common.put(ROOT/'control'/('HOST_BINDING_AMENDMENT_'+family.upper()+'_V3.json'),amendment,True)
            results.append(amendment)
            reg,unused=local_common.authority()
    print(json.dumps(results,sort_keys=True))


if __name__=='__main__':
    main()
