"""Preserve full derived lifecycle locally; publish per-image SHA/map anchors."""
from common import *

def main():
 path=PACK/'ACTUAL_LOADER_LIFECYCLE_EVIDENCE.json';full=RAW/'ACTUAL_LOADER_LIFECYCLE_FULL_DETAIL.json'
 with full.open('xb') as f:f.write(path.read_bytes())
 data=json.loads(path.read_text())
 for row in data['rows']:
  for image in row['images']:
   for key in ['initial_exec','first_cache_present','first_cache_removed','first_startup_closed','last_snapshot']:
    if image[key]:image[key]={k:v for k,v in image[key].items() if k in ['utc','stage','maps','maps_sha256','cache_present','removed_files','startup_closed']}
 data.update(full_local_detail=dict(path=str(full),sha256=sha(full),bytes=full.stat().st_size),compact_anchors_only=True,final_executor_qualification='STOP_PRELAUNCH_CPU_QUALIFICATION_INCOMPLETE',cohort_performance_claims_eligible=False)
 write(path,data);print('COMPACT_LOADER_EVIDENCE',path.stat().st_size)
if __name__=='__main__':main()
