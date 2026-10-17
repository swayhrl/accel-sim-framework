"""Replay only new affected native condition checks; never compile or launch applications."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import time

from registry import Registry,local_resources,process_identity,write_json
from run import digest,require,asset_manifest,content_hash,process_tree_rss,terminate_owned
from headroom_config import EXPERIMENT,OVERRIDES,H0,BINARY,options,validate_runtime_dump

REPO=Path(__file__).resolve().parents[3]
FIXTURE=Path('/workspace/build/ep-l2-ft20261017-lane1-headroom-r19-r4/production_probe')
L1=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1')
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-fixed-r1')
FW=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261017-lane1-a1-fixed-r1')


def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)


def native_options(text):
    section=text.split('R19_NATIVE_EFFECTIVE_OPTIONS_BEGIN\n',1)[1].split('R19_NATIVE_EFFECTIVE_OPTIONS_END',1)[0];out={}
    for line in section.splitlines():
        row=line.split('#',1)[0].strip().split(None,1)
        if row and row[0].startswith('-'):
            value=row[1].strip() if len(row)>1 else ''
            require(row[0] not in out or out[row[0]]==value,'Conflicting repeated native option');out[row[0]]=value
    return out


def safe():
    r=local_resources();s=os.statvfs('/root/share')
    require(r['disk_free_bytes']>=48*2**30 and r['available_memory_bytes']>=64*2**30 and s.f_bavail*s.f_frsize>=40*2**30,'Original resource floor')
    return r


def audit(handoff):
    global FIXTURE
    FIXTURE=Path(handoff['fixture_executable']) if handoff['regime'] in ('D2','L25') else FIXTURE
    pub=handoff['publication'];remote=git('rev-parse','refs/remotes/origin/hrl/ep-l2-ft20261016-lane1-v1').decode().strip()
    require(subprocess.run(['git','merge-base','--is-ancestor',pub,remote],cwd=REPO).returncode==0,'Unpublished Lane1 handoff')
    manifest_path=Path(handoff['producer_manifest_raw_path']);require(digest(manifest_path)==handoff['producer_manifest_sha256'],'Producer manifest bytes changed')
    require(manifest_path.read_bytes()==git('show',pub+':'+handoff['producer_manifest_repository_path']),'Not exact published manifest')
    receipt_bytes=git('show',pub+':'+handoff['producer_receipt_repository_path']);require(hashlib.sha256(receipt_bytes).hexdigest()==handoff['producer_receipt_sha256'],'Published producer receipt changed');receipt=json.loads(receipt_bytes);manifest=json.loads(manifest_path.read_text())
    require(receipt['status']=='AFFECTED_PRODUCTION_CHECKS_PASS_READY_FOR_LANE5_INDEPENDENT_REVIEW' and manifest['identity']==handoff['source_identity'],'Producer source/condition not pass')
    require(receipt['official_binary_sha256']==BINARY==digest(receipt['official_binary']) and manifest['allowed_overlay_values']==OVERRIDES[handoff['regime']],'Different main binary/condition')
    for root,key in ((CORE,'core_source_commit'),(FW,'framework_source_commit')):
        require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==handoff['source_identity'][key],'Moved producing source')
        require(not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root),'Dirty runtime source')
    build=receipt['fixture_build_identity'];fixture_path='util/ep_l2/ft_lane1/'+('headroom_r19_followup' if handoff['regime'] in ('D2','L25') else 'headroom_r19')+'/production_probe.cc';source=git('show',handoff['tool_fixture_source_commit']+':'+fixture_path)
    require(hashlib.sha256(source).hexdigest()==build['fixture_source_sha256']==digest(L1/fixture_path),'Fixture source differs from exact publication')
    require(build['runtime_recompiled'] is False and build['binary_sha256']==handoff['fixture_binary_sha256']==digest(FIXTURE),'Fixture is not official unchanged-archive build')
    for p,h in build['archives_sha256'].items():require(digest(p)==h,'Native production archive changed')
    for row in receipt.get('commands',receipt.get('tests',[]))+build.get('actual_compile_and_link',[]):
        require(row['exit_code']==0 and digest(row['log'])==row['log_sha256'],'Producer compile/test raw missing')
        archived=handoff['producer_receipt_repository_path'].rsplit('/',1)[0]+'/logs/'+Path(row['log']).name
        # L25 reuses the exact fixture compiled and published with D2.
        # Keep the same Git object binding; do not manufacture a second build.
        candidates=git('ls-tree','-r','--name-only',pub,'--',archived).decode().splitlines()
        if not candidates and handoff['regime']=='L25' and row in build.get('actual_compile_and_link',[]):
            archived=archived.replace('FT20261017_LANE1_R19_L25_r1','FT20261017_LANE1_R19_D2_r1')
        require(Path(row['log']).read_bytes()==git('show',pub+':'+archived),'Producer raw is not exact remote evidence')
    for mode,row in manifest['modes'].items():
        configs=asset_manifest(row['configs'],ordered=True);require(configs==row['ordered_config_manifest'],'Frozen config content changed')
        require(content_hash({'ordered_configs':configs[:5],'auxiliary_assets':[],'environment':row['environment']})==H0[mode],'Changed original five config layers')
        require(content_hash({'ordered_configs':configs,'auxiliary_assets':[],'environment':row['environment']})==row['runtime_config_sha256']==handoff['mode_runtime_config_sha256'][mode],'Producer config identity differs')
        require(options([a['path'] for a in row['configs'][5:]])==OVERRIDES[handoff['regime']],'Overlay forbidden fields')
        require(options([a['path'] for a in row['configs']])==row['effective_options'],'Authored effective options differ')
        require(digest(row['production_evidence']['log'])==row['production_evidence']['log_sha256'],'Producer condition log changed')
        old=row['H0_affected_control'];require(digest(old['log'])==old['sha256'] and native_options(Path(old['log']).read_text())==old['options'],'Native H0 affected-control evidence changed')
    return manifest,receipt,{'remote_tip':remote,'condition_publication':pub,'exact_manifest_sha256':digest(manifest_path),'exact_receipt_sha256':hashlib.sha256(receipt_bytes).hexdigest(),'fixture_source_sha256':hashlib.sha256(source).hexdigest(),'fixture_binary_sha256':digest(FIXTURE),'archive_hashes':build['archives_sha256']}


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--handoff',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    handoff=json.loads(args.handoff.read_text());require(handoff['regime'] in ('D4','Q4','D2','L25'),'Affected replay not qualified for additional fixture regimes')
    manifest,producer,binding=audit(handoff);require(not args.out.exists(),'Independent revision exists');args.out.mkdir(parents=True)
    report={'status':'INDEPENDENT_AFFECTED_RUNNING','experiment_id':EXPERIMENT,'regime':handoff['regime'],'identity':handoff['source_identity'],'tooling_source_commit':git('rev-parse','HEAD').decode().strip(),'tool_sha256':digest(__file__),'producer_binding':binding,'producer_receipt':producer,'tests':[],'resources_before':safe(),'compiler_started':False,'full_applications':0}
    r=Registry();lease=None;process=None;resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    def interrupted(signum,frame):raise KeyboardInterrupt('Own affected check interrupted')
    signal.signal(signal.SIGTERM,interrupted)
    try:
        lease=r.build_lease('lane5',cpu=1,memory=4*2**30);report['lease_id']=lease
        for mode,row in manifest['modes'].items():
            safe();command=[str(FIXTURE),handoff['regime'],*[a['path'] for a in row['configs']]];log=args.out/(mode+'.log');case={'mode':mode,'command':command,'log':str(log)};report['tests'].append(case)
            with log.open('xb') as stream:
                process=subprocess.Popen(command,cwd=args.out,stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,**row['environment']),start_new_session=True);case['process']=process_identity(process.pid);start=time.monotonic();peak=0
                while process.poll() is None:
                    safe();peak=max(peak,process_tree_rss(process.pid));require(peak<=4*2**30 and log.stat().st_size<=128*2**20 and time.monotonic()-start<=180,'Owned affected test cap');time.sleep(.2)
            case.update(exit_code=process.returncode,peak_rss_bytes=peak,log_sha256=digest(log));require(process.returncode==0,'Affected native assertion failed')
            text=log.read_text();opts=native_options(text);old=row['H0_affected_control']['options'];require(opts=={**old,**OVERRIDES[handoff['regime']]},'Actual native options not exact H0 plus whitelist')
            require(opts==native_options(Path(row['production_evidence']['log']).read_text()),'Independent native options differ from producer')
            spec={'experiment_id':EXPERIMENT,'regime':handoff['regime'],'identity':{'feature_vector':row['feature_vector']}};case['actual_runtime_options_and_clocks']=validate_runtime_dump(log,spec)
            markers=[l for l in text.splitlines() if l.startswith(('R19_EFFECTIVE|','R19_CLOCK|','R19_DELAY_CAPTURE|','R19_PRODUCTION_PASS|'))]
            end=[l for l in markers if l.startswith('R19_PRODUCTION_PASS|')];require(len(end)==1,'Missing independent native terminal marker')
            values=dict(p.split('=',1) for p in end[0].split('|')[1:]);require(values['regime']==handoff['regime'] and int(values['mode'])==(2 if mode=='U_WB16' else 1),'Wrong native mode/condition')
            for field,value in {'exact_once':'40','wb_lower_accept_and_set_done':'5','two_dirty_sector_versions':'1','cold_sectors':'2','subpartitions_exercised':'2','credit_drained':'1','bank_max_ops_per_physical_cycle':'1','runtime_archives_unchanged':'1'}.items():require(values[field]==value,'Missing production closure '+field)
            if handoff['regime'] in ('D2','L25'):
                require(values['fixed_delay_gpu_cycles']==('25' if handoff['regime']=='L25' else '100') and values['fixed_delay_verified']=='1','Exact latency not independently proved')
            else:
                require(values['fixed_delay_at_least100_gpu_cycles']=='1','Original fixed latency missing')
            case.update(status='PASS',native_markers=markers,native_effective_options=opts);write_json(args.out/'INDEPENDENT_AFFECTED.json',report);print(mode,'INDEPENDENT_AFFECTED_PASS',flush=True);process=None
        audit(handoff);report['status']='INDEPENDENT_AFFECTED_PRODUCTION_PASS';report['scope']='One actual native partition/two subpartitions; detailed DRAM native clock, exact config, five WB lower accept/set_done with two dirty-sector versions, forty responses/cold sectors/real hits, credit/physical bank/condition-specific fixedGPUcycle/drain. Not saturation or64slice full-application proof; unchanged original11 evidence retained within scope.'
    except BaseException as error:report.update(status='INDEPENDENT_AFFECTED_FAILED_RETAIN_RAW_NO_APPLICATION',error=repr(error));raise
    finally:
        if process is not None:terminate_owned(process)
        if lease is not None:r.release_build(lease,'lane5');report['lease_released']=True
        report.update(resources_after=local_resources(),at_utc=datetime.now(timezone.utc).isoformat());write_json(args.out/'INDEPENDENT_AFFECTED.json',report)
    print(json.dumps({'status':report['status'],'regime':handoff['regime'],'executed':len(report['tests']),'lease_released':report['lease_released']}))
if __name__=='__main__':main()
