"""Independent AG evidence helpers. No inherited AA5 write paths or launches."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

PACK=Path(__file__).resolve().parents[1]
FW=PACK.parents[3]
CORE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-ag3-aead-core-174-v1')
FW_REPO=Path('/workspace/repos/accel-sim-framework')
CORE_REPO=Path('/workspace/repos/gpgpu-sim_distribution')
RAW=Path('/workspace/dtc-lane-ag5-retired-pid-repair-174-v1/raw')
BUILD=Path('/workspace/dtc-lane-ag5-retired-pid-repair-174-v1/build')
X2='e32afdcf44be3374ff36d22568ed01a075459b6f'
FRAMEWORK_BUILD='8e43c75a5e2eb60a8466084602b7df8117111e89'
AA5='2d740ece2f5dbb6d99040a64f421e940687a48fa'
AA5_PACK='docs/dtc_l1/review_packs/DTC_LANE_AA5_GAUSSIAN_V1'
AB='59a2bf0bfee404965ce56736333bbbf6b0d95259'
AB_PACK='docs/dtc_l1/review_packs/DTC_LANE_AB_OLD_DISPATCH_AUTHORITY_AUDIT_V1'
T='f520a445436b57c0a0f2494fb858a1636f04d2bc'
T_PACK='docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):
            h.update(data)
    return h.hexdigest()


def write(path,value,exclusive=False):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    with path.open('x' if exclusive else 'w') as f:
        f.write(data)


def table(path,rows):
    rows=list(rows)
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def blob(repo,commit,path):
    return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path])


def copy_blob(repo,commit,path,destination):
    data=blob(repo,commit,path)
    dest=PACK/destination
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    return dict(repo=str(repo),commit=commit,path=path,blob=git(repo,'rev-parse',commit+':'+path),
                destination=destination,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
