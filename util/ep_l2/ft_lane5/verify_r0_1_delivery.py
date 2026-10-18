"""Fetch exact own remote branch, verify immutable pair, install current scientific pointer."""
import argparse
from datetime import datetime,timezone
import fcntl
import json
from pathlib import Path
import subprocess

from acceptance import BRANCH,MANIFEST,bind_manifest,load_current_authority,require_current_result,require_publication_boundary
from registry import Registry,ACTIVE,write_json
from run import digest,require

REPO=Path(__file__).resolve().parents[3]
SHARED=Path('/workspace/ep_l2_ft20261016_shared')


def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--since-publication',required=True);ap.add_argument('--workload');ap.add_argument('--regime',choices=('D4','Q4','D2','D8','L25','ROP40_H0','ICNT2_H0','WAD256_Q4','LOCAL_IDEALS_ORDINARY','LOCAL_IDEALS_LEGACY','UNIFIED_ORDINARY','UNIFIED_LEGACY','SERVICE_MQ2','SERVICE_RG1','P2'));ap.add_argument('--qualification-pack',type=Path);ap.add_argument('--qualification-only',action='store_true');ap.add_argument('--single-pack',type=Path);ap.add_argument('--single-acceptance-pack',type=Path);a=ap.parse_args()
    if a.single_pack and a.regime is None:a.regime=json.loads((a.single_pack/'SCIENTIFIC_REVIEW.json').read_text()).get('regime','H0')
    ref='refs/remotes/origin/'+BRANCH
    subprocess.run(['git','-c','gc.auto=0','-c','url.https://github.com/.insteadOf=git@github.com:','-c','credential.helper=!gh auth git-credential','fetch','--no-tags','origin','refs/heads/'+BRANCH+':'+ref],cwd=REPO,check=True)
    head=git('rev-parse','HEAD').decode().strip();require(head==git('rev-parse',ref).decode().strip(),'Remote own branch SHA differs')
    files=git('diff','--name-only',a.since_publication,head).decode().splitlines()
    for name in files:require((REPO/name).read_bytes()==git('show',head+':'+name),'Remote object/file differs '+name)
    require(a.workload or (a.qualification_only and a.qualification_pack is not None),'Workload or qualification-only pack required')
    is_parallel=bool(a.single_pack) or a.regime in ('ROP40_H0','ICNT2_H0','WAD256_Q4','LOCAL_IDEALS_ORDINARY','LOCAL_IDEALS_LEGACY','UNIFIED_ORDINARY','UNIFIED_LEGACY','SERVICE_MQ2','SERVICE_RG1','P2')
    prefix=(('FT20261017_LANE5_PARALLEL_' if is_parallel else 'FT20261017_LANE5_R19_')+a.regime+'_' if a.regime else 'FT20261017_LANE5_R0_1_A1_B1_')+(a.workload or '').upper()
    packs=[REPO/'docs/ep_l2/review_packs'/(prefix+suffix) for suffix in ('_PAIR_r1','_ACCEPTANCE_r1')] if not a.qualification_only else []
    if a.single_pack:
        require(a.single_acceptance_pack is not None and not a.qualification_only,'Explicit single endpoint pack pair required');packs=[a.single_pack,a.single_acceptance_pack]
        require(all(p.resolve().is_relative_to(REPO/'docs/ep_l2/review_packs') for p in packs),'Noncanonical single endpoint packs')
    for pack in packs+([a.qualification_pack] if a.qualification_pack else []):
        for line in (pack/'SHA256SUMS').read_text().splitlines():
            sha,name=line.split('  ',1);require(digest(pack/name)==sha,'Immutable pack changed')
    path=REPO/MANIFEST;raw=path.read_bytes();manifest=json.loads(raw);sha=digest(path)
    bind_manifest(raw,{'kind':'FETCHED_GITHUB_BRANCH','publication_commit':head,'manifest_sha256':sha,'generation':manifest['generation'],'revision':manifest['revision']},lambda n:(REPO/n).read_bytes())
    handoff=None
    if not a.qualification_only:
        handoff=json.loads((packs[1]/'LANE6_HANDOFF.json').read_text());require(handoff['ledger_generation']==manifest['generation'] and handoff['ledger_sha256']==sha,'Delivery is not current ledger')
    else:
        q=json.loads((a.qualification_pack/'RECEIPT.json').read_text());require(q['generation']==manifest['generation'] and q['manifest_sha256']==sha,'Qualification is not current ledger')
    accepted=[r for r in manifest['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'];pairs=sum(not r.get('experiment_id') for r in accepted)//2;diagnostic_pairs=sum(r.get('experiment_id')=='EPL2_DOWNSTREAM_HEADROOM_R19' for r in accepted)//2
    require_publication_boundary(Registry())
    with (SHARED/'REGISTRY.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);p=SHARED/'CLIENT_CONTRACT.json';client=json.loads(p.read_text());client['scientific_acceptance']={'path':str(path),'sha256':sha,'generation':manifest['generation'],'revision':manifest['revision'],'publication_commit':head,'snapshot_path':str((a.qualification_pack if a.qualification_only else packs[1])/'SCIENTIFIC_ACCEPTANCE_V2.json')};write_json(p,client)
        if a.qualification_only:
            p=SHARED/('LANE5_CONTINUE_PARALLEL.json' if is_parallel else 'LANE5_CONTINUE_R19.json');m=json.loads(p.read_text()) if p.exists() else {};m.update(status='ACTIVE_'+a.regime+'_CONDITION_QUALIFIED_READY',verified_publication=head,at_utc=datetime.now(timezone.utc).isoformat());write_json(p,m)
        elif a.regime or a.single_pack:
            p=SHARED/('LANE5_CONTINUE_PARALLEL.json' if is_parallel else 'LANE5_CONTINUE_R19.json');m=json.loads(p.read_text()) if p.exists() else {};m.update(status=('ROLLING_PARALLEL_CURRENT_ACCEPTED' if is_parallel else 'ROLLING_R19_CURRENT_ACCEPTED'),verified_publication=head,actual_worker=None,latest_pair_delivery=handoff,at_utc=datetime.now(timezone.utc).isoformat());write_json(p,m)
            event_name=(('LANE5_TO_LANE6_PARALLEL_' if is_parallel else 'LANE5_TO_LANE6_R19_')+(a.regime or 'H0')+'_'+a.workload.upper()+('_'+handoff['profile'] if a.single_pack else '')+'.json')
            event={'status':'CURRENT_ACCEPTED','experiment_id':'EPL2_PARALLEL_POTENTIAL_20261017_V1' if is_parallel else 'EPL2_DOWNSTREAM_HEADROOM_R19','regime':a.regime,'publication_commit':head,'generation':manifest['generation'],'current_manifest_sha256':sha,'handoff':handoff}
            write_json(SHARED/'coordination_requests'/event_name,event)
            if is_parallel:
                write_json(SHARED/'coordination_requests'/event_name.replace('TO_LANE6_','TO_LANE3_',1),event)
        else:
            p=SHARED/'LANE5_CONTINUE_R13.json';m=json.loads(p.read_text());m.update(status=f'ACTIVE_{pairs}_CURRENT_ACCEPTED_PAIRS',verified_publication=head,actual_worker=None,current_accepted_pairs=pairs,latest_pair_delivery=handoff,at_utc=datetime.now(timezone.utc).isoformat());write_json(p,m)
            write_json(SHARED/'coordination_requests'/('LANE5_TO_LANE6_CURRENT_ACCEPTED_R0_1_'+a.workload.upper()+'.json'),{'status':'CURRENT_ACCEPTED','publication_commit':head,'generation':manifest['generation'],'current_manifest_sha256':sha,'handoff':handoff})
    state=load_current_authority()
    if a.qualification_only:
        print(json.dumps({'status':'REMOTE_VERIFIED_CONDITION_QUALIFICATION_POINTER_INSTALLED','publication_commit':head,'verified_changed_files':len(files),'generation':manifest['generation'],'regime':a.regime}));return
    for row in handoff['rows']:require_current_result(row['identity'],row['raw_log_sha256'],row['observed_cycles'],row['instructions'],state)
    print(json.dumps({'status':'REMOTE_VERIFIED_AND_CURRENT_SCIENTIFIC_POINTER_INSTALLED','publication_commit':head,'verified_changed_files':len(files),'generation':manifest['generation'],'accepted_H0_pairs':pairs,'accepted_r19_pairs':diagnostic_pairs,'workload':a.workload,'cycles':[r['observed_cycles'] for r in handoff['rows']],'speedup':handoff['comparison'].get('speedup_B16_over_U_WB16')}))


if __name__=='__main__':main()
