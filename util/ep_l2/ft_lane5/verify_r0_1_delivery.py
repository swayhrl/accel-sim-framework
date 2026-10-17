"""Fetch exact own remote branch, verify immutable pair, install current scientific pointer."""
import argparse
from datetime import datetime,timezone
import fcntl
import json
from pathlib import Path
import subprocess

from acceptance import BRANCH,MANIFEST,bind_manifest,load_current_authority,require_current_result
from registry import Registry,ACTIVE,write_json
from run import digest,require

REPO=Path(__file__).resolve().parents[3]
SHARED=Path('/workspace/ep_l2_ft20261016_shared')


def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--since-publication',required=True);ap.add_argument('--workload',required=True);a=ap.parse_args()
    ref='refs/remotes/origin/'+BRANCH
    subprocess.run(['git','-c','gc.auto=0','-c','url.https://github.com/.insteadOf=git@github.com:','-c','credential.helper=!gh auth git-credential','fetch','--no-tags','origin','refs/heads/'+BRANCH+':'+ref],cwd=REPO,check=True)
    head=git('rev-parse','HEAD').decode().strip();require(head==git('rev-parse',ref).decode().strip(),'Remote own branch SHA differs')
    files=git('diff','--name-only',a.since_publication,head).decode().splitlines()
    for name in files:require((REPO/name).read_bytes()==git('show',head+':'+name),'Remote object/file differs '+name)
    prefix='FT20261017_LANE5_R0_1_A1_B1_'+a.workload.upper()
    packs=[REPO/'docs/ep_l2/review_packs'/(prefix+suffix) for suffix in ('_PAIR_r1','_ACCEPTANCE_r1')]
    for pack in packs:
        for line in (pack/'SHA256SUMS').read_text().splitlines():
            sha,name=line.split('  ',1);require(digest(pack/name)==sha,'Immutable pack changed')
    path=REPO/MANIFEST;raw=path.read_bytes();manifest=json.loads(raw);sha=digest(path)
    bind_manifest(raw,{'kind':'FETCHED_GITHUB_BRANCH','publication_commit':head,'manifest_sha256':sha,'generation':manifest['generation'],'revision':manifest['revision']},lambda n:(REPO/n).read_bytes())
    handoff=json.loads((packs[1]/'LANE6_HANDOFF.json').read_text());require(handoff['ledger_generation']==manifest['generation'] and handoff['ledger_sha256']==sha,'Delivery is not current ledger')
    accepted=[r for r in manifest['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'];pairs=len(accepted)//2
    require(not any(r['status'] in ACTIVE for r in Registry().snapshot()['runs'].values()),'Install current pointer at no-active-simulator boundary')
    with (SHARED/'REGISTRY.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);p=SHARED/'CLIENT_CONTRACT.json';client=json.loads(p.read_text());client['scientific_acceptance']={'path':str(path),'sha256':sha,'generation':manifest['generation'],'revision':manifest['revision'],'publication_commit':head};write_json(p,client)
        p=SHARED/'LANE5_CONTINUE_R13.json';m=json.loads(p.read_text());m.update(status=f'ACTIVE_{pairs}_CURRENT_ACCEPTED_PAIRS',verified_publication=head,actual_worker=None,current_accepted_pairs=pairs,latest_pair_delivery=handoff,at_utc=datetime.now(timezone.utc).isoformat());write_json(p,m)
        write_json(SHARED/'coordination_requests'/('LANE5_TO_LANE6_CURRENT_ACCEPTED_R0_1_'+a.workload.upper()+'.json'),{'status':'CURRENT_ACCEPTED','publication_commit':head,'generation':manifest['generation'],'current_manifest_sha256':sha,'handoff':handoff})
    state=load_current_authority()
    for row in handoff['rows']:require_current_result(row['identity'],row['raw_log_sha256'],row['observed_cycles'],row['instructions'],state)
    print(json.dumps({'status':'REMOTE_VERIFIED_AND_CURRENT_SCIENTIFIC_POINTER_INSTALLED','publication_commit':head,'verified_changed_files':len(files),'generation':manifest['generation'],'accepted_pairs':pairs,'workload':a.workload,'cycles':[r['observed_cycles'] for r in handoff['rows']],'speedup':handoff['comparison']['speedup_B16_over_U_WB16']}))


if __name__=='__main__':main()
