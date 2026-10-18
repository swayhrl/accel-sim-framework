"""Read-only exact GitHub source/report/receipt verification after own push."""
from pathlib import Path
import argparse,json,subprocess,base64,hashlib,concurrent.futures,datetime
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--pack',required=True);p.add_argument('--select-json',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();w=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-r3b-owner-cost-v1');prefix='repos/swayhrl/accel-sim-framework/'
def api(path):return json.loads(subprocess.check_output(['gh','api',prefix+path]))
for ref in ('hrl/ep-l2-ft20261016-lane2-v1','hrl/ep-l2-rtl-r3b-owner-cost-v1'):assert api('git/ref/heads/'+ref)['object']['sha']==a.sha
assert api('git/ref/heads/hrl/ep-l2-rtl-r3-metadata-cost-v1')['object']['sha']=='b4d825b4e2cd7808fc5db2bd907d65fb3e1e9676'
tree=subprocess.check_output(['git','rev-parse',a.sha+':'+a.pack],cwd=w,text=True).strip();r=api('git/trees/'+tree+'?recursive=1');assert not r.get('truncated');remote={x['path']:x['sha'] for x in r['tree'] if x['type']=='blob'};local={}
for entry in subprocess.check_output(['git','ls-tree','-rz',a.sha,a.pack],cwd=w).split(b'\0'):
 if not entry:continue
 meta,path=entry.split(b'\t');local[path.decode()[len(a.pack)+1:]]=meta.split()[2].decode()
assert remote==local
paths=json.loads(a.select_json.read_text())
def check(path):
 raw=base64.b64decode(api('contents/'+path+'?ref='+a.sha)['content']);assert raw==(w/path).read_bytes(),path;return {'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,paths))
result={'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'publication':a.sha,'status':'EXACT_TWO_HEADS_ALL_PACK_BLOBS_AND_SELECTED_SOURCE_TABLE_RECEIPT_BYTES_PASS','pack_tree':tree,'pack_blobs':len(remote),'A_original_checkpoint_ref_unchanged':True,'selected_byte_reads':rows};a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'publication':a.sha,'status':result['status'],'pack_blobs':len(remote),'byte_reads':len(rows)}))
