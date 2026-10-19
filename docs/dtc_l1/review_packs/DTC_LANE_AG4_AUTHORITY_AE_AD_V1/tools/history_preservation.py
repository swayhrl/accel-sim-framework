"""Bounded read-only check of published historical receipts; no launch API."""
from common import *


def main():
    rows=[]
    sources=[('AG', 'cc5f51ea068e5a234811d2fbe79a5ccdbab21769',
              'DTC_LANE_AG_OPT_SCREEN_V1',
              Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-ag-opt-screen-174-v1'),
              ['STOP_EVIDENCE.json','RESULT_SUMMARY.json','RUN_ARTIFACT_INDEX.tsv']),
             ('AA5', AA5, 'DTC_LANE_AA5_GAUSSIAN_V1',
              Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa5-gaussian-convergence-174-v1'),
              ['STOP_RECORD.json','LATEST_REPORT.md'])]
    ag_stop=None
    for label,head,name,worktree,files in sources:
        for name_in_pack in files:
            path='docs/dtc_l1/review_packs/'+name+'/'+name_in_pack
            data=blob(FW_REPO,head,path)
            if label=='AG' and name_in_pack=='STOP_EVIDENCE.json':ag_stop=json.loads(data)
            local=worktree/path
            row=dict(label=label,published_commit=head,path=path,published_blob=git(FW_REPO,'rev-parse',head+':'+path),published_sha256=hashlib.sha256(data).hexdigest(),local_path=str(local),local_sha256=sha(local) if local.is_file() else 'UNAVAILABLE_PATH',byte_equal=local.is_file() and local.read_bytes()==data)
            rows.append(row)
            if local.is_file() and not row['byte_equal']:raise ValueError('HISTORICAL_RECEIPT_CHANGED:'+str(local))
    raw=Path(ag_stop['raw']);raw_checks=[]
    for name,expected in [('simulator.stdout',ag_stop['stdout_sha256']),('simulator.stderr',ag_stop['stderr_sha256']),('FILES_SHA256.tsv',ag_stop['raw_index_sha256'])]:
        p=raw/name;actual=sha(p)
        raw_checks.append(dict(path=str(p),frozen_sha256=expected,current_sha256=actual,unchanged=actual==expected))
        if actual!=expected:raise ValueError('HISTORICAL_AG_RAW_CHANGED:'+str(p))
    write(PACK/'HISTORY_PRESERVATION.json',dict(utc=now(),scope='only fixed named receipts and old AG stdout/stderr/raw index; no broad raw scan',receipts=rows,old_AG_raw=raw_checks,AG_actual_starts=1,AG_budget=8,AG_complete_strict_passes=0,AA5_actual_starts=1,AA5_budget=4,AA5_complete_strict_passes=0,retrospective_acceptance=False,old_UUID_reuse=False,old_stop_rewrite=False))


if __name__=='__main__':main()
