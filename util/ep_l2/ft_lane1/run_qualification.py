#!/usr/bin/env python3
"""Old-static qualification only; B16/U_WB formal assignments belong to Lane 5."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
ROSTER = {
    'vectorAdd_4M': 'decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000',
    'cfd_097k': 'decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K',
    'sad': 'decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin',
}
ARTIFACTS = ['target_'+name+'.csv' for name in ('summary','slice','kernel','bank','l1','dram','window')]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024**2),b''):h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--core',type=Path,required=True)
    p.add_argument('--core-source',required=True)
    p.add_argument('--framework-source',required=True)
    p.add_argument('--trace-root',type=Path,default=Path('/workspace/worktrees/accel-sim-decoupled-l2/hw_run'))
    p.add_argument('--workload',choices=ROSTER,required=True)
    p.add_argument('--timeout',type=int,default=900)
    args=p.parse_args()
    client=json.loads((SHARED/'CLIENT_CONTRACT.json').read_text())
    assert sha(client['registry_client'])==client['registry_client_sha256']
    sys.path.insert(0,str(Path(client['registry_client']).parent))
    from registry import Registry, process_identity, write_json
    from run import asset_manifest,content_hash,process_tree_rss,local_resources,terminate_owned
    binary=args.binary.resolve(strict=True)
    configs=[args.core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',
             ROOT/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config',
             ROOT/'tests/ep_l2/b0_banked_d512_850.config', ROOT/'tests/ep_l2/m0a_off.config']
    cfgassets=[{'name':f'config-{i}.config','path':str(f)} for i,f in enumerate(configs)]
    auxiliary=[]
    for config in configs:
        for line in config.read_text().splitlines():
            line=line.split('#',1)[0].strip()
            if re.search(r'\.(xml|icnt|config)(?:\s|$)',line):
                raise ValueError('qualification requires explicit auxiliary asset resolution: '+line)
    trace=(args.trace_root/ROSTER[args.workload]/'traces/kernelslist.g').resolve(strict=True)
    files=[{'name':'kernelslist.g','path':str(trace)}]
    names=set()
    for line in trace.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith(('#','MemcpyHtoD,','MemcpyDtoH,','MemcpyDtoD,')):continue
        if not re.fullmatch(r'kernel-[^/\s]+\.traceg(?:\.gz)?',line):raise ValueError('unsupported trace command '+line)
        if line not in names:files.append({'name':line,'path':str((trace.parent/line).resolve(strict=True))});names.add(line)
    cfgmanifest=asset_manifest(cfgassets,ordered=True);tracemanifest=asset_manifest(files)
    environment={'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    identity={'core_source_commit':args.core_source,'framework_source_commit':args.framework_source,
        'binary_sha256':sha(binary),'runtime_config_sha256':content_hash({'ordered_configs':cfgmanifest,'auxiliary_assets':auxiliary,'environment':environment}),
        'trace_content_sha256':content_hash(tracemanifest),'workload':args.workload,
        'epoch_range':{'scope':'full_application','epochs':'all'},
        'feature_vector':{'finite_wbuf':False,'unified_wb':False,'tvd':False,'ro':False,'adaptive_policy':False,
            'wbuf_entries':0,'payload_capacity_per_slice':1152,'bank_count':4,'ops_per_bank_cycle':1},
        'ideal_vector':{'wb':False,'meta':False,'read_hit':False},
        'termination_contract':{'hardware_drained':True,'normal_exit':True,'qualification':'OLD_STATIC_EQUIVALENCE_V1','timeout_seconds':args.timeout}}
    from registry import run_key
    key=run_key(identity);out=Path('/workspace/results/ep_l2_ft20261016')/key
    registry=Registry();fresh,lease=registry.claim(identity,'lane1',out)
    if not fresh:
        print(json.dumps({'status':'DUPLICATE_NOT_LAUNCHED','existing':lease},indent=2));return
    out.mkdir(exist_ok=False)
    write_json(out/'input_identity.json',identity)
    write_json(out/'input_assets.json',{'configs':cfgmanifest,'trace':tracemanifest,'trace_paths':files,'registry_client_source':client['source_commit']})
    snapshot=out/'accel-sim.out';shutil.copyfile(binary,snapshot);snapshot.chmod(0o755)
    assert sha(snapshot)==identity['binary_sha256']
    command=[str(snapshot)]
    for i,source in enumerate(configs):
        f=out/f'config-{i}.config';shutil.copyfile(source,f);command.extend(['-config',str(f)])
    command.extend(['-trace',str(trace)])
    proc=None;status='INCOMPLETE';detail='not launched';started=time.monotonic();peak=0
    try:
        env=os.environ.copy();env.update(environment)
        with (out/'raw.log').open('xb') as f:
            proc=subprocess.Popen(command,cwd=out,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
            registry.update(key,lease['lease_id'],'RUNNING',process=process_identity(proc.pid))
            while proc.poll() is None:
                peak=max(peak,process_tree_rss(proc.pid));resources=local_resources()
                if time.monotonic()-started>args.timeout:status='TIMEOUT';detail='qualification deadline';terminate_owned(proc);break
                if peak>lease['memory_bytes'] or (out/'raw.log').stat().st_size>2*1024**3 or resources['disk_free_bytes']<48*1024**3:
                    status='RESOURCE_LIMIT';detail='own qualification resource limit';terminate_owned(proc);break
                time.sleep(1)
        if proc.returncode:raise RuntimeError(f'process exit {proc.returncode}')
        log=(out/'raw.log').read_text(errors='replace')
        if 'GPGPU-Sim: *** exit detected ***' not in log:raise RuntimeError('no normal simulator exit')
        result=subprocess.run([sys.executable,str(ROOT/'util/ep_l2/parse_epl2_b0.py'),str(out/'raw.log'),'--out',str(out),
            '--framework-commit',args.framework_source,'--core-commit',args.core_source,'--source-log',str(out/'raw.log')],capture_output=True,text=True)
        (out/'parser.stdout').write_text(result.stdout);(out/'parser.stderr').write_text(result.stderr)
        if result.returncode:raise RuntimeError('B0 terminal parser failed: '+result.stderr)
        summary=next(csv.DictReader((out/'target_summary.csv').open()))
        assert summary['invariants_terminal_clean']=='1' and summary['invariants_payload_consistent']=='1'
        assert all((out/name).is_file() for name in ARTIFACTS)
        assert asset_manifest(cfgassets,ordered=True)==cfgmanifest and asset_manifest(files)==tracemanifest
        status='COMPLETE_VALID';detail='qualification old-static terminal/parser/invariants PASS; not a B16 result'
    except (Exception,KeyboardInterrupt) as error:
        if proc is not None:terminate_owned(proc)
        if status not in {'TIMEOUT','RESOURCE_LIMIT'}:status='FAILED'
        detail=f'{type(error).__name__}: {error}'
    finally:
        record={'status':status,'detail':detail,'identity':identity,'command':command,'wall_seconds':time.monotonic()-started,
            'peak_process_tree_rss_bytes':peak,'exit_code':proc.returncode if proc else None,'raw_log_sha256':sha(out/'raw.log') if (out/'raw.log').exists() else None,
            'artifact_sha256':{name:sha(out/name) for name in ARTIFACTS if (out/name).exists()}}
        write_json(out/'run_status.json',record)
        registry.update(key,lease['lease_id'],status,exit_code=record['exit_code'],detail=detail,raw_log_sha256=record['raw_log_sha256'])
        print(json.dumps({'status':status,'directory':str(out),'detail':detail}),flush=True)
    if status!='COMPLETE_VALID':raise SystemExit(1)

if __name__=='__main__':main()
