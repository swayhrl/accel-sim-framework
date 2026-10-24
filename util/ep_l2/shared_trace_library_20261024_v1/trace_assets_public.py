"""Project-independent read-only catalog and explicit local materialization."""
from pathlib import Path
import argparse,json,os,hashlib,shutil,time,sys
LIB=Path(__file__).resolve().parents[1]
def load():
 p=LIB/'catalog/CURRENT';d=json.loads(p.read_text());assert d['schema']=='SHARED_SM70_TRACE_LIBRARY_V1'
 cid=d['catalog_id'];body={k:v for k,v in d.items() if k!='catalog_id'}
 actual=hashlib.sha256((json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
 if cid!=actual:raise ValueError('immutable catalog content ID mismatch')
 return d
def storage(p):
 if p.startswith('/home/shared/') and str(LIB).startswith('/root/share/mnt164/'):return Path(p.replace('/home/shared','/root/share/mnt164',1))
 return Path(p)
def safe(root,n):
 q=Path(n)
 if q.is_absolute() or '..' in q.parts or '\\' in n:raise ValueError('unsafe manifest member')
 return root/q
def whole(p,rate=30*1024**2):
 h=hashlib.sha256();start=time.monotonic();done=0
 with p.open('rb') as f:
  while True:
   b=f.read(1024**2)
   if not b:break
   h.update(b);done+=len(b)
   if rate:time.sleep(max(0,done/rate-(time.monotonic()-start)))
 return h.hexdigest()
def select(d,ident):
 rows=[a for a in d['assets'] if a['bundle_id']==ident or a['bundle_id'].startswith(ident) or ident in a.get('aliases',[])]
 if len(rows)!=1:raise ValueError('asset ID is unknown or ambiguous; use list and a full bundle ID')
 return rows[0]
def verify(d,a,full=False):
 checked=[]
 for m in a['members']:
  o=d['objects'][m['sha256']];p=storage(o['true164_path']);s=p.stat()
  if s.st_size!=m['size'] or not p.is_file():raise ValueError('member absent/type/size drift: '+str(p))
  if os.uname().nodename=='huangrulin-sshfs-174' and [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]!=o['verified_identity']:raise ValueError('sealed member identity changed: '+str(p))
  if full:
   if whole(p)!=m['sha256']:raise ValueError('full SHA mismatch: '+str(p))
  else:
   with p.open('rb') as f:first=f.read(min(128,s.st_size));f.seek(max(0,s.st_size-32));tail=f.read(32)
   with p.open('rb') as f:
    if f.read(len(first))!=first:raise ValueError('reopen mismatch')
  checked.append({'relative_path':m['relative_path'],'sha256':m['sha256'],'size':s.st_size})
 return {'bundle_id':a['bundle_id'],'status':'PASS_FULL_SHA' if full else 'PASS_SEALED_IDENTITY_OPEN_REOPEN','members':len(checked),'full_sha_recomputed':full,'scientific_qualification_granted':False}
def materialize(d,a,dest,max_bytes,dry):
 if not dest.is_absolute() or '..' in dest.parts or os.path.lexists(dest):raise ValueError('destination must be absolute and ABSENT')
 parent=dest.parent
 while not parent.exists():parent=parent.parent
 if parent.resolve().is_relative_to(LIB.resolve()) or str(parent.resolve()).startswith(('/root/share/','/home/shared/')):raise ValueError('materialization destination must be local, outside public/164 storage')
 if os.uname().nodename!='huangrulin-sshfs-174' or parent.stat().st_dev!=Path('/root/data').stat().st_dev:raise ValueError('use a new destination on verified174-new native /root/data filesystem')
 receipt_path=dest.with_name(dest.name+'.MATERIALIZATION_RECEIPT.json')
 if os.path.lexists(receipt_path):raise ValueError('adjacent materialization receipt must also be ABSENT')
 free=shutil.disk_usage(parent).free;size=sum(m['size'] for m in a['members']);reserve=6*1024**3+64*1024**2
 n=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 if n.exists():reserve+=sum(x.get('reserved_write_bytes',0) for x in json.loads(n.read_text()).get('registered_future_requests',{}).values())
 admit=size<=max_bytes and free>=size+reserve
 receipt={'bundle_id':a['bundle_id'],'destination':str(dest),'required_payload_bytes':size,'max_bytes':max_bytes,'free_bytes':free,'reserved_other_headroom_bytes':reserve,'admitted':admit,'dry_run':dry,'source_keep':True,'scientific_qualification_granted':False}
 if dry:return receipt
 if not admit:raise ValueError('local materialization exceeds explicit byte budget or shared headroom; use dry-run')
 verify(d,a);dest.parent.mkdir(parents=True,exist_ok=True);dest.mkdir(mode=0o700);rows=[]
 for m in a['members']:
  src=storage(d['objects'][m['sha256']]['true164_path']);p=safe(dest,m['relative_path']);p.parent.mkdir(exist_ok=True,parents=True);h=hashlib.sha256();start=time.monotonic();done=0
  with src.open('rb') as f,p.open('xb') as out:
   while True:
    b=f.read(1024**2)
    if not b:break
    out.write(b);h.update(b);done+=len(b);time.sleep(max(0,done/(30*1024**2)-(time.monotonic()-start)))
   out.flush();os.fsync(out.fileno())
  if h.hexdigest()!=m['sha256'] or whole(p,rate=0)!=m['sha256']:raise ValueError('closed local restore SHA mismatch')
  rows.append({'relative_path':m['relative_path'],'sha256':m['sha256'],'bytes':done})
 receipt.update(status='PASS_COMPLETE_LOCAL_MATERIALIZATION',files=rows)
 with receipt_path.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 return receipt
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['list','show','verify','materialize']);p.add_argument('asset',nargs='?');p.add_argument('--suite');p.add_argument('--kind',choices=['regular','fraction','all'],default='all');p.add_argument('--full',action='store_true');p.add_argument('--all',action='store_true');p.add_argument('--destination');p.add_argument('--max-bytes',type=int,default=256*1024**2);p.add_argument('--dry-run',action='store_true');a=p.parse_args();d=load()
 if a.operation=='list':
  rows=[{k:x[k] for k in ['bundle_id','suite','version','program','kind','architecture','view_path','kernel_launches','logical_bytes']} for x in d['assets'] if (not a.suite or x['suite']==a.suite) and (a.kind=='all' or x['kind']==a.kind)]
  return {'catalog_id':d['catalog_id'],'access_scope':'ALL_PROJECTS','assets':rows,'issues_path':d.get('issues_path'),'coverage_path':d.get('coverage_path'),'scientific_qualification_granted':False}
 if a.operation=='verify' and a.all:return {'results':[verify(d,x,a.full) for x in d['assets']]}
 asset=select(d,a.asset or '')
 if a.operation=='show':return asset
 if a.operation=='verify':return verify(d,asset,a.full)
 if not a.destination:raise ValueError('materialize requires --destination')
 return materialize(d,asset,Path(a.destination),a.max_bytes,a.dry_run)
if __name__=='__main__':
 try:print(json.dumps(main(),indent=2))
 except Exception as e:print(json.dumps({'status':'ASSET_OPERATION_REFUSED','reason':str(e),'scientific_starts':0}),file=sys.stderr);sys.exit(2)
