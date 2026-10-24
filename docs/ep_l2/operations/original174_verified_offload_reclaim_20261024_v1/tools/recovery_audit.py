"""Read-only endpoint recovery audit; writes evidence only in this worktree."""
from local_common import *
import concurrent.futures

ENDPOINT = r'''
import os,sys,json,time,pathlib,subprocess,traceback,hashlib
P=pathlib.Path
T=P('/root/data/research_asset_verified_offload_20261024_v1')
sys.path.insert(0,str(T/'tools'))
import server_resources as rr
role='TARGET' if os.uname().nodename=='huangrulin-sshfs-174' else 'SOURCE'
def disk(p):
 s=os.statvfs(p);st=P(p).stat()
 return dict(path=p,dev=st.st_dev,available_bytes=s.f_bavail*s.f_frsize,free_inodes=s.f_favail,mount=json.loads(subprocess.check_output(['findmnt','-J','-T',p],text=True))['filesystems'][0])
def proc(pid):
 p=P('/proc')/str(pid)
 try:
  raw=(p/'stat').read_text().rsplit(')',1)[1].split()
  return dict(pid=int(pid),start_ticks=int(raw[19]),state=raw[0],command=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'),cwd=os.readlink(p/'cwd'),mnt=os.readlink(p/'ns/mnt'),pid_ns=os.readlink(p/'ns/pid'))
 except OSError:return None
processes=[]
for p in P('/proc').iterdir():
 if not p.name.isdigit():continue
 q=proc(p.name)
 if q and any(s in q['command'] for s in ['offload_driver.py','frozen_copy_source.py','copy_engine.py','frozen_readonly_trace_export','v9_transaction.py','v10_sender','v10_receiver']):processes.append(q)
bridge=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
locks=[]
for lock in [bridge/'.TARGET_RECEIVER.lock',bridge/'.TLS_V10_SOURCE_SENDER.lock']:
 st=lock.stat();owners=[]
 for p in P('/proc').iterdir():
  if not p.name.isdigit():continue
  try:fds=list((p/'fd').iterdir())
  except OSError:continue
  for fd in fds:
   try:
    s=fd.stat()
    if (s.st_dev,s.st_ino)==(st.st_dev,st.st_ino):owners.append(dict(process=proc(p.name),fd=fd.name,fdinfo=(p/'fdinfo'/fd.name).read_text()))
   except OSError:pass
 locks.append(dict(path=str(lock),dev=st.st_dev,inode=st.st_ino,open_handles=owners))
try:admission=dict(status='PASS',value=rr.admission(role))
except Exception as e:admission=dict(status='HOLD',reason=str(e),traceback=traceback.format_exc())
regpath=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reg=json.loads(regpath.read_bytes())
summary={}
for k,v in reg.get('registered_future_requests',{}).items():
 summary[k]={z:v.get(z) for z in ['state','reserved_write_bytes','remaining','budget','consumed','controller','controller_path','output','pid','start_ticks','intent_path','intent']}
release={}
for name in ['SOURCE.jsonl','TARGET.jsonl']:
 path=T/'release'/name;rows=[json.loads(z) for z in path.read_text().splitlines()]
 intents={x['path']:x for x in rows if x.get('event')=='INTENT'};done={x['path']:x for x in rows if x.get('event')=='DONE'}
 release[name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),intents=len(intents),done=len(done),unclosed=sorted(set(intents)-set(done)),unexpected_present=[p for p in done if os.path.lexists(p)] if role==name.split('.')[0] else 'other namespace')
for name in ['COMPLETE.json','POLYBENCH_PACKAGE_SOURCE_INTENT.json','POLYBENCH_PACKAGE_SOURCE_DONE.json','POLYBENCH_PACKAGE_COMPLETE.json']:
 p=T/'release'/name;release[name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),content=json.loads(p.read_bytes())) if p.exists() and name!='COMPLETE.json' else dict(exists=p.exists(),sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None)
bridge_controls=[]
for p in bridge.iterdir():
 if p.is_file() and any(z in p.name.lower() for z in ['lease','owner','active','transaction','receiver','sender','lock']):
  bridge_controls.append(dict(name=p.name,size=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,content=p.read_text(errors='replace') if p.stat().st_size<40000 else 'large metadata omitted'))
out=dict(unix=time.time(),host=os.uname().nodename,role=role,mount_namespace=os.readlink('/proc/self/ns/mnt'),pid_namespace=os.readlink('/proc/self/ns/pid'),old_pid=proc(934578),transfer_processes=processes,disks=[disk(p) for p in ['/workspace' if role=='SOURCE' else '/root/workspace','/root/data','/root/share','/root/share/mnt164']],kernel_locks=rr.old_lock_holders(),locks=locks,bridge_controls=bridge_controls,admission=admission,registry_sha256=hashlib.sha256(regpath.read_bytes()).hexdigest(),registry_requests=summary,science_processes=rr.current_science(),releases=release)
print(json.dumps(out))
'''

TRANSACTIONS = r'''
import os,json,time,pathlib,hashlib,gzip,collections
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1')
h=lambda b:hashlib.sha256(b).hexdigest()
raw=(T/'control/FROZEN_SCOPES.json.gz').read_bytes();queue=json.loads(gzip.decompress(raw))['scopes'];byid={x['asset_id']:x for x in queue}
ledger=[json.loads(x) for x in (T/'control/LEDGER.jsonl').read_text().splitlines()];latest={x['asset_id']:x for x in ledger};committed={x['asset_id']:x for x in ledger if x['status']=='ARCHIVED_CONTENT_VERIFIED'}
assets=[]
for bundle in sorted((N/'assets').iterdir()):
 if not bundle.is_dir():continue
 assert bundle.name in byid, 'OUTSIDE_FROZEN_QUEUE'
 mr=(bundle/'SOURCE_MANIFEST.json').read_bytes();m=json.loads(mr);local=(T/'manifests'/(bundle.name+'.json')).read_bytes();assert mr==local
 a=dict(asset_id=bundle.name,source=byid[bundle.name]['source_root'],kind=m['kind'],object_id=m['object_id'],source_data_bytes=m['source_data_bytes'],members=len(m['members']),manifest_sha256=h(mr),commit_exists=(bundle/'COMMIT.json').exists(),metadata_paths=[str(p.relative_to(bundle)) for p in bundle.iterdir() if p.is_file()])
 if a['commit_exists']:
  cr=(bundle/'COMMIT.json').read_bytes();c=json.loads(cr);r=(bundle/'RANGE_INDEX.json').read_bytes();t=(bundle/'TREE_VERIFICATION.json').read_bytes();e=json.loads((bundle/'SOURCE_CURRENT_EOF_SHA_PROOFS.json').read_bytes());receipt=json.loads((bundle/'RECEIPT.json').read_bytes())
  assert c['manifest_sha256']==h(mr) and c['range_index_sha256']==h(r) and c['tree_verification_sha256']==h(t) and c['object_id']==m['object_id']
  assert bundle.name in committed and committed[bundle.name]['commit_sha256']==h(cr)
  assert [(x['path'],x['size'],x['sha256']) for x in e]==[(x['relative_path'],x['size'],x['sha256']) for x in m['members']]
  assert receipt['object_id']==m['object_id'] and receipt['Source_full_SHA_matches'] and receipt['true164_closed_reopen_whole_SHA_matches']
  a.update(commit_sha256=h(cr),control_hash_links_verified=True,source_EOF_full_SHA_proofs_verified=True,closed_reopen_full_SHA_receipt=True,restore_status=json.loads((T/'restore'/(bundle.name+'.json')).read_bytes())['status'],current_body_rehash=False)
 else:
  ranges=[]
  for folder in sorted((bundle/'chunks').iterdir()):
   offset=0
   for p in sorted(folder.glob('*.part.json')):
    x=json.loads(p.read_bytes());d=folder/x['name'];assert d.stat().st_size==x['size'] and x['offset']==offset;offset+=x['size'];ranges.append(dict(folder=folder.name,**x))
  partials=[dict(path=str(p.relative_to(bundle)),size=p.stat().st_size) for p in bundle.rglob('*.writing')]
  orphan_parts=[dict(path=str(p.relative_to(bundle)),size=p.stat().st_size,frame_exists=p.with_name(p.name+'.frame').exists()) for p in bundle.rglob('*.part') if not p.with_name(p.name+'.json').exists()]
  a.update(verified_ranges=ranges,verified_range_bytes=sum(x['size'] for x in ranges),partials=partials,orphan_parts=orphan_parts,range_bodies_rehashed=False,tree_files=[dict(path=str(p.relative_to(bundle/'tree')),size=p.stat().st_size) for p in (bundle/'tree').rglob('*') if p.is_file()])
 assets.append(a)
assert len(committed)==sum(a['commit_exists'] for a in assets)
pending=[x for x in queue if x['asset_id'] not in committed]
print(json.dumps(dict(unix=time.time(),frozen_sha256=h(raw),frozen_scope=len(queue),frozen_file_rows=sum(len(x['files']) for x in queue),frozen_bytes=sum(x['expected_bytes'] for x in queue),completed=len(committed),pending=len(pending),held_latest=sum(latest.get(x['asset_id'],{}).get('status')=='HOLD_EXACT_ASSET' for x in pending),unique_committed_payload_bytes=sum(byid[x]['expected_bytes'] for x in committed),held_reasons=dict(collections.Counter(latest[x['asset_id']]['reason'] for x in pending if x['asset_id'] in latest)),assets=assets,state=json.loads((T/'control/STATE.json').read_bytes()),ledger=ledger,task_control_inventory=[dict(path=str(p.relative_to(T/'control')),size=p.stat().st_size,sha256=h(p.read_bytes())) for p in (T/'control').iterdir() if p.is_file()])))
'''

def main():
    jobs = [('SOURCE', 'hrl', ENDPOINT), ('TARGET', 'hrl-174-new', ENDPOINT), ('TRANSACTIONS', 'hrl-174-new', TRANSACTIONS)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(remote, alias, code, 180): name for name, alias, code in jobs}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            result = future.result()
            save('checkpoint/recovery_20261025/' + name + '.json', result)
            print(json.dumps(dict(audit=name,keys=list(result),admission=result.get('admission',{}).get('status'),completed=result.get('completed'),pending=result.get('pending')), ensure_ascii=False))

if __name__ == '__main__':
    main()
