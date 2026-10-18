#!/usr/bin/env python3
"""Reproduce published AF header safety evidence, never merge AF or launch trace."""
from common import *

AF_FW='001e569f146db4a7ef759ba2c3ce574a74d0d70f'
AF_CORE='19dafca6b5636ee26f4c35e566c24e17e645edaf'
AF_PACK='docs/dtc_l1/review_packs/DTC_LANE_AF_VICTIM_FALLBACK_V1'


def main():
    assert git(FW_REPO,'rev-parse','refs/ag-inputs/AF-framework')==AF_FW
    assert git(CORE_REPO,'rev-parse','refs/ag-inputs/AF-core')==AF_CORE
    records=[]
    for name in ['LATEST_REPORT.md','GO_NO_GO.md','CPU_CASES.json','CPU_CHECKS.json',
        'MECHANISM_AND_REACHABILITY.md','RESOURCE_COST_AND_LIMITS.md','SOURCE_SCOPE_AUDIT.json',
        'REQUIRED_EVENT_FIELDS.tsv','CORE_FETCH_BACK.json','FILES_SHA256.tsv']:
        records.append(copy_blob(FW_REPO,AF_FW,AF_PACK+'/'+name,'inputs/AF/'+name))
    root=BUILD/'af-independent-cpu'
    root.mkdir(exist_ok=False)
    paths=['src/gpgpu-sim/dtc-l1-common.h','tests/dtc_l1_reclaimable_victim_fallback_test.cc']
    source=[]
    for name in paths:
        data=blob(CORE_REPO,AF_CORE,name);dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        source.append(dict(path=name,commit=AF_CORE,sha256=sha(dest)))
    exe=root/'af-state-safety-cpu-test'
    argv=['/usr/bin/g++','-std=c++17','-O2','-UNDEBUG','-I'+str(root/'src/gpgpu-sim'),
          str(root/paths[1]),'-o',str(exe)]
    c=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    (root/'compile.stdout').write_bytes(c.stdout);(root/'compile.stderr').write_bytes(c.stderr)
    assert c.returncode==0,c.stderr.decode()[-2000:]
    raw=RAW/'cpu-qualification'/'af-independent';raw.mkdir(parents=True,exist_ok=False)
    r=subprocess.run([str(exe)],cwd=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    (raw/'stdout').write_bytes(r.stdout);(raw/'stderr').write_bytes(r.stderr)
    assert r.returncode==0,r.stderr.decode()[-2000:]
    cases=[json.loads(l) for l in r.stdout.decode().splitlines() if l.startswith('{')]
    assert cases and all(x['status']=='PASS' for x in cases)
    write(PACK/'AF_INDEPENDENT_CPU_CONSUMPTION.json',dict(status='PASS_REPRODUCED_PUBLISHED_BOUNDED_HEADER_SAFETY_ONLY',
        framework_commit=AF_FW,core_commit=AF_CORE,source=source,imported_files=records,compile_argv=argv,
        binary_sha256=sha(exe),cases=cases,stdout_sha256=sha(raw/'stdout'),stderr_sha256=sha(raw/'stderr'),
        scope='SYNTHETIC_OPPORTUNITY_AND_STATE_SAFETY_NOT_FULL_LDST_WB_OR_REAL_INPUT_REACHABILITY',
        producer_verdict='NO_GO_REAL_INPUT_PERFORMANCE',AF_merged_into_screen_Core=False,
        AF_performance_arm=False,new_simulation_attempts=0))
    print(json.dumps(dict(status='AF_BOUNDED_CPU_REPRODUCTION_PASS_NOT_MERGED',cases=len(cases),simulation_attempts=0)))


if __name__=='__main__':main()
