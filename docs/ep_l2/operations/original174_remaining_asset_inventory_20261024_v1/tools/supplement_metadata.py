from audit_local import *
from collect_audit import SNAP
import time
code=Path(__file__).with_name('metadata_scan.py').read_text()
old=json.loads((P/'SOURCE_COLD_CENSUS_SCAN_COVERAGE.json').read_text(encoding='utf8'))
shared=[r['target'] for r in old['symlink_roots'] if r['target'].startswith('/root/share/workspace_migrated_20260905/')]
target=json.loads((R/'evidence/CURRENT_OWNER_HEADS_AND_NATIVE_SCIENCE.json').read_text(encoding='utf8'))
awma=[r['path'] for r in target['awma_local_roots'] if r.get('type')=='dir']
ds=json.loads((R/'evidence/SOURCE_ENDPOINT_ACTIVITY_START.json').read_text(encoding='utf8'))
data=[r['path'] for r in ds['discovery'] if r['path'].startswith('/root/data/c16')]
for label,alias,roots in [('SOURCE_SHARED','hrl',shared),('TARGET_AWMA','hrl-174-new',awma),('SHARED_SSD_C16','hrl',data)]:
 pending=roots
 for i in range(4):
  if not pending:break
  x=remote(alias,code+'\nprint(json.dumps(scan('+repr(pending)+',seconds=16,max_entries=100000)))',35)
  save('evidence/%s_METADATA_BATCH_%02d.json'%(label,i+1),x)
  pending=[r['path'] for r in x['roots'] if r['status']=='BATCH_BUDGET_NOT_SCANNED']
  print(label,i+1,x['entries'],'pending',len(pending),flush=True)
 save('evidence/'+label+'_SCAN_REMAINDER.json',pending)
