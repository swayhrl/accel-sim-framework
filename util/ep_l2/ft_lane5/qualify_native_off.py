"""Affected original OFF and mode guards after exact official independent21.

No compiler, historical full-suite replay, primary-performance acceptance or
certificate issuance. Long OFF execution owns a canonical simulator slot.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import resource
import signal
import shutil
import subprocess
import sys
import time

from registry import Registry, run_key, write_json, process_identity, local_resources
from run import (RESULT_ROOT, RESULT_DISK_FLOOR, result_disk_free_bytes, digest,
                 asset_manifest, content_hash, validate_config_closure,
                 validate_trace_closure, process_tree_rss, terminate_owned, tree_bytes)
from qualify_r0_1 import audit_producer, require, CORE, FRAMEWORK

BASELINE = RESULT_ROOT / '61a666655f9ef908ef5dbacedb1457acffb26f223940fa4798ded4f7249b66ec'
CSVS = ['target_' + name + '.csv' for name in ('summary', 'slice', 'kernel', 'bank', 'l1', 'dram', 'window')]
ENV = {'OMP_NUM_THREADS':'1', 'OPENBLAS_NUM_THREADS':'1', 'MKL_NUM_THREADS':'1'}


def safe_resources():
    r = local_resources()
    require(r['disk_free_bytes'] >= 48*1024**3 and r['available_memory_bytes'] >= 64*1024**3 and
            result_disk_free_bytes() >= RESULT_DISK_FLOOR, 'Unchanged root/memory/Share floor')


def native_metrics(path):
    totals = {}
    for line in Path(path).open(errors='replace'):
        m = re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
        if m: totals[m[1]] = int(m[2])
    require(set(totals) == {'cycle','insn'}, 'Native totals missing')
    return totals


def main():
    def interrupted(signum, frame):
        raise KeyboardInterrupt('owned qualification control interrupted')
    signal.signal(signal.SIGTERM, interrupted)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--producer-report',required=True,type=Path);ap.add_argument('--producer-publication',required=True)
    ap.add_argument('--published-report-path',required=True);ap.add_argument('--independent-directed',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path);ap.add_argument('--deadline-unix',required=True,type=float)
    args=ap.parse_args();require(time.time()<args.deadline_unix,'CONTINUE expired')
    producer,plan,commands=audit_producer(args.producer_report,args.producer_publication,args.published_report_path)
    independent=json.loads(args.independent_directed.read_text())
    require(independent['status']=='INDEPENDENT21_PASS_REVIEW_ELEVEN_GATES_BEFORE_ANY_APPLICATION' and
            len(independent['tests'])==21 and independent['source_identity']['binary_sha256']==producer['binary_sha256'] and
            independent['producer_report_sha256']==digest(args.producer_report),'Exact actual independent21 required')
    for row in independent['tests']:
        require(row['exit_code']==0 and row['independent_validation']['status']=='PASS' and digest(row['log'])==row['log_sha256'], 'Independent evidence changed')
    args.out.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    report={'status':'INCOMPLETE','producer_publication':args.producer_publication,
            'qualification_runner_sha256':digest(__file__),
            'qualification_runner_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[3],text=True).strip(),
            'producer_report_sha256':digest(args.producer_report),'independent21_sha256':digest(args.independent_directed),
            'mode_legality':[],'off_equivalence':None,'scientific_certificate':False,'primary_accepted_pairs':0}
    registry=Registry();lease=None;process=None;key=None;allocation=None;directory=None;terminal='INCOMPLETE';created_directory=False
    try:
        safe_resources();lease=registry.build_lease('lane5',cpu=1,memory=4*1024**3)
        for mode,cap in [(1,7),(1,0),(2,7),(3,16)]:
            safe_resources();require(time.time()<args.deadline_unix-30,'No mode guard outside CONTINUE')
            executable=str(Path(producer['build'])/'gpgpu-sim/ep_l2_ft_directed')
            require(digest(executable)==producer['test_executables'][executable],'Mode executable changed')
            command=[executable,str(CORE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'),str(CORE/'tests/ep_l2/ft_wbuf.config'),str(mode),str(cap)]
            log=args.out/f'mode_{mode}_capacity_{cap}.log'
            with log.open('x') as stream:
                result=subprocess.run(command,cwd=args.out,env=dict(os.environ,**ENV),stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,timeout=30)
            text=log.read_text();row={'command':command,'exit_code':result.returncode,'log':str(log),'log_sha256':digest(log)};report['mode_legality'].append(row)
            require(result.returncode==-6 and 'EP-L2 FT invalid mode/WBUF/banked/WAD/allocation contract' in text and 'INVALID CONFIG WAS ACCEPTED' not in text,'Mode guard failed')
        registry.release_build(lease,'lane5');lease=None
        baseline=json.loads((BASELINE/'run_status.json').read_text());assets=json.loads((BASELINE/'input_assets.json').read_text())
        require(baseline['status']=='COMPLETE_VALID' and digest(BASELINE/'raw.log')==baseline['raw_log_sha256']=='62dfb0770eb9db4f18b676fcd280abc89d19d0d2993287a44276f179e254052d','Frozen native baseline changed')
        configs=[CORE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',FRAMEWORK/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config',FRAMEWORK/'tests/ep_l2/b0_banked_d512_850.config',FRAMEWORK/'tests/ep_l2/m0a_off.config']
        cfg=[{'name':f'config-{i}.config','path':str(p)} for i,p in enumerate(configs)];traces=assets['trace_paths'];parser=FRAMEWORK/'util/ep_l2/parse_epl2_b0.py';parser_sha=digest(parser)
        cm=asset_manifest(cfg,ordered=True);tm=asset_manifest(traces);require(cm==assets['configs'] and tm==assets['trace'],'Control config/full trace identity differs')
        spec={'configs':cfg,'auxiliary_assets':[],'trace_files':traces,'entry_trace_name':'kernelslist.g'};validate_config_closure(spec);validate_trace_closure(spec)
        identity=dict(baseline['identity']);identity.update({k:producer[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')})
        require(identity['runtime_config_sha256']==content_hash({'ordered_configs':cm,'auxiliary_assets':[],'environment':ENV}) and identity['trace_content_sha256']==content_hash(tm),'Native identity formula mismatch')
        key=run_key(identity);directory=RESULT_ROOT/key;safe_resources();require(time.time()<args.deadline_unix-10,'No native run outside CONTINUE')
        fresh,allocation=registry.claim(identity,'lane5',directory)
        if not fresh:
            report['status']='DUPLICATE_NATIVE_CONTROL_NOT_LAUNCHED';report['existing']=allocation;return
        directory.mkdir(exist_ok=False);created_directory=True
        write_json(directory/'input_identity.json',identity);write_json(directory/'input_assets.json',{'configs':cm,'trace':tm,'trace_paths':traces,'parser_sha256':parser_sha})
        binary=directory/'accel-sim.out';shutil.copyfile(producer['binary'],binary);binary.chmod(0o555);require(digest(binary)==identity['binary_sha256'],'Snapshot binary changed')
        command=[str(binary)]
        for i,source in enumerate(configs):
            target=directory/f'config-{i}.config';shutil.copyfile(source,target);require(digest(target)==cm[i]['sha256'],'Snapshot config changed');command+=['-config',str(target)]
        command+=['-trace',next(r['path'] for r in traces if r['name']=='kernelslist.g')];started=time.monotonic();peak=0
        with (directory/'raw.log').open('xb') as stream:
            safe_resources();process=subprocess.Popen(command,cwd=directory,env=dict(os.environ,**ENV),stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
            registry.update(key,allocation['lease_id'],'RUNNING',process=process_identity(process.pid))
            while process.poll() is None:
                safe_resources();peak=max(peak,process_tree_rss(process.pid))
                require(time.time()<args.deadline_unix-5 and time.monotonic()-started<900,'Native control timeout')
                require(peak<=allocation['memory_bytes'] and (directory/'raw.log').stat().st_size<=2*1024**3 and tree_bytes(RESULT_ROOT)<=8*1024**3,'Native control resource cap')
                time.sleep(1)
        require(process.returncode==0,'Native OFF failed')
        require('GPGPU-Sim: *** exit detected ***' in (directory/'raw.log').read_text(errors='replace'),'Missing native normal exit')
        require(digest(parser)==parser_sha,'Parser changed')
        result=subprocess.run([sys.executable,str(parser),str(directory/'raw.log'),'--out',str(directory),'--framework-commit',producer['framework_source_commit'],'--core-commit',producer['core_source_commit'],'--source-log',str(directory/'raw.log')],cwd=directory,capture_output=True,timeout=60)
        (directory/'parser.stdout').write_bytes(result.stdout);(directory/'parser.stderr').write_bytes(result.stderr);require(result.returncode==0,'Native parser failed')
        summary=next(csv.DictReader((directory/'target_summary.csv').open()))
        require(summary['invariants_terminal_clean']=='1' and summary['invariants_payload_consistent']=='1' and summary['slice_count']=='64' and summary['terminal_invariant_records']=='64','Incomplete native hardware closure')
        metrics=native_metrics(directory/'raw.log');require(metrics==native_metrics(BASELINE/'raw.log')=={'cycle':73873,'insn':56000000},'Affected OFF native totals changed')
        comparison={}
        for name in CSVS:
            h=digest(BASELINE/name);require(h==baseline['artifact_sha256'][name],'Frozen baseline CSV changed');require(digest(directory/name)==h,'OFF_REGRESSION_CSV_'+name);comparison[name]=h
        require(asset_manifest(cfg,ordered=True)==cm and asset_manifest(traces)==tm and digest(producer['binary'])==identity['binary_sha256'],'Inputs changed during OFF')
        terminal='COMPLETE_VALID';report['off_equivalence']={'status':'PASS','run_key':key,'directory':str(directory),'identity':identity,'baseline_run_key':BASELINE.name,'metrics':metrics,'seven_csv_sha256':comparison,'raw_log_sha256':digest(directory/'raw.log'),'scope':'One affected OFF control only; not primary B16/U_WB16 evidence'};report['status']='FOUR_MODE_GUARDS_AND_AFFECTED_OFF_PASS_PENDING_ELEVEN_GATE_REVIEW'
    except BaseException as error:
        report['status']='FAILED_FROZEN_EVIDENCE_NO_CERTIFICATE';report['error']=repr(error);terminal='FAILED';raise
    finally:
        if process is not None:terminate_owned(process)
        if lease is not None:registry.release_build(lease,'lane5')
        if allocation is not None and key is not None and 'existing' not in report:
            raw=digest(directory/'raw.log') if created_directory and (directory/'raw.log').exists() else None
            record={'status':terminal,'identity':allocation['identity'],'raw_log_sha256':raw,'exit_code':process.returncode if process else None,'detail':report['status'],'qualification_control':True}
            if created_directory:write_json(directory/'run_status.json',record)
            registry.update(key,allocation['lease_id'],terminal,exit_code=record['exit_code'],raw_log_sha256=raw,detail=report['status'])
        write_json(args.out/'NATIVE_OFF_AND_MODE_GATES.json',report)
        print(json.dumps({'status':report['status'],'report':str(args.out/'NATIVE_OFF_AND_MODE_GATES.json')}),flush=True)


if __name__=='__main__':main()
