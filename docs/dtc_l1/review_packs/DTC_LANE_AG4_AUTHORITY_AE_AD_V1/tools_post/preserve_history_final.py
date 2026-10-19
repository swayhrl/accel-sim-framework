"""Read-only named historical checks only; never changes old branches/raw/locks."""
from common import *
import re

def main():
 assert (RAW/'COHORT_TERMINAL.json').is_file()
 initial=json.loads((PACK/'HISTORY_PRESERVATION.json').read_text());checks=[]
 for row in initial['receipts']:
  p=Path(row['local_path']);actual=sha(p);expected=row['published_sha256'];checks.append(dict(path=str(p),frozen_sha256=expected,current_sha256=actual,unchanged=actual==expected))
 for row in initial['old_AG_raw']:
  actual=sha(row['path']);checks.append(dict(path=row['path'],frozen_sha256=row['frozen_sha256'],current_sha256=actual,unchanged=actual==row['frozen_sha256']))
 old=PACK.parent/'DTC_LANE_AG3_AE_AD_SCREEN_V1'
 for row in csv.DictReader((old/'RUN_ARTIFACT_INDEX.tsv').open(),delimiter='\t'):
  for n,k in [('FILES_SHA256.tsv','raw_index_sha256'),('STRICT.json','strict_sha256'),('ENGINE/TERMINAL.json','engine_terminal_sha256')]:
   p=Path(row['raw'])/n;actual=sha(p);checks.append(dict(path=str(p),frozen_sha256=row[k],current_sha256=actual,unchanged=actual==row[k]))
 oldwt=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-ag3-aead-screen-174-v1');assert git(oldwt,'rev-parse','HEAD')=='2f3a8c4b27780e2bf3818949a6e5356d9fd62327' and not git(oldwt,'status','--porcelain')
 known=set();regex=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
 for commit in ['2f3a8c4b27780e2bf3818949a6e5356d9fd62327','cc5f51ea068e5a234811d2fbe79a5ccdbab21769',AA5]:
  r=subprocess.run(['git','-C',str(FW_REPO),'grep','-hoE',regex,commit,'--','docs/dtc_l1'],capture_output=True,text=True);assert r.returncode in (0,1);known.update(re.findall(regex,r.stdout))
 rows=json.loads((PACK/'UUID_RESERVATIONS.json').read_text())['rows'];new={r['attempt_uuid'] for r in rows};assert len(new)==5 and not (new&known)
 passed=all(c['unchanged'] for c in checks)
 write(PACK/'HISTORY_FINAL_PRESERVATION.json',dict(status='PASS_HISTORY_AND_FRESH_UUID_PRESERVATION' if passed else 'STOP_HISTORY_CHANGED',checks=checks,AG3_Framework_HEAD=git(oldwt,'rev-parse','HEAD'),AG3_Framework_clean=True,AG3_actual_starts=2,AG3_full_strict_passes=1,AG3_failed_Gaussian_retrospectively_promoted=False,AG_actual_starts=1,AG_full_strict_passes=0,AA5_actual_starts=1,AA5_full_strict_passes=0,new_five_UUIDs=sorted(new),known_fixed_history_UUID_count=len(known),known_UUID_set_sha256=hashlib.sha256('\n'.join(sorted(known)).encode()).hexdigest(),new_UUID_intersection_old=[],old_UUID_reuse=False,old_branch_raw_stop_writes=False))
 assert passed
 print('PASS_HISTORY_AND_FRESH_UUID_PRESERVATION',len(checks),len(known))
if __name__=='__main__':main()
