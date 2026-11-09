#!/usr/bin/env python3
"""Copy only this exact5 supplement's small, already bound evidence into its review tree."""
import hashlib
import json
import pathlib
import shutil

ROOT=pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
DEST=ROOT/'review/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/supplement_v1'

def main():
    files=[]
    for family in ('gemm','stencil'):
        host='host_'+family+'_bound_v2'
        for name in ('ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py',
                     'ep_perf_archive.py','resources_exact5_v2.py'):
            files.append('runtime/'+host+'/'+name)
        files.extend(('control/RESOURCE_BINDING_AMENDMENT_'+family.upper()+'_V5.json',
                      'control/HOST_BINDING_AMENDMENT_'+family.upper()+'_V3.json',
                      'documents/HOST_QUALIFICATION_EXACT5_'+family.upper()+'_V5.json'))
    files += ['runtime/stage_dispatch_exact5_v2.py',
              'control/NATIVE_ENTRY_ROUTE_EXACT5.json',
              'control/NATIVE_ENTRY_ROUTE_EXACT5.version2.json',
              'control/STAGED_ADMISSION_GEMM_59551b01-ac15-4600-9b3d-8e0071fd802c.json',
              'control/STAGED_ADMISSION_STENCIL_5ee40e2f-97e8-4dc8-9543-2a3fa6887e10.json']
    for spec in sorted(ROOT.glob('cases/*/control/FROZEN_SPEC.json')):
        if 'EP_PERF_CLEAN128_' in str(spec):
            files.append(str(spec.relative_to(ROOT)))
            prep=spec.parent/'NATIVE_PRELAUNCH_QUALIFICATION.json'
            files.append(str(prep.relative_to(ROOT)))
    assert len(files)==29, len(files)
    records=[]
    for rel in files:
        source=ROOT/rel
        target=DEST/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        records.append(dict(path=rel,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size))
    index=dict(schema='EP_L2_EXACT5_SUPPLEMENT_BOUND_FILES_V1',
               prior_review_commit='f9f05065b277c3f01f74f9fa27c96ff9337d5168',
               source_root=str(ROOT),files=records,
               rule='Current bound files only; historical versions remain in execution tree and prior review commit')
    (DEST/'BOUND_FILE_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print(DEST,len(files))

if __name__=='__main__':main()
