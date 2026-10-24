"""Read-only process/partial-transaction audit. Never signals any process."""
import sys
sys.dont_write_bytecode=True
from local_common import *
from t2_closure_audit import OUT,dump
import argparse

REMOTE=r'''
import pathlib,json,os,time,gzip,hashlib,subprocess
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets')
m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(N)],text=True))['filesystems'][0];assert m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs'
q=json.loads(gzip.decompress((T/'control/FROZEN_SCOPES.json.gz').read_bytes()))['scopes'];byid={z['asset_id']:z for z in q};state=json.loads((T/'control/STATE.json').read_bytes());sup=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes());own=[];unreadable=[]
paths=[str(T/'tools'/n).encode() for n in ['offload_driver.py','continuation_supervisor.py','copy_engine.py']]
for proc in P('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  argv=(proc/'cmdline').read_bytes().split(b'\0')
  if not any(path in argv for path in paths):continue
  z=(proc/'stat').read_text().rsplit(')',1)[1].split();own.append(dict(pid=int(proc.name),start_ticks=int(z[19]),state=z[0],argv=[x.decode(errors='replace') for x in argv if x],mnt=os.readlink(proc/'ns/mnt')))
 except FileNotFoundError:pass
 except PermissionError:unreadable.append(int(proc.name))
partials=[];errors=[];commits=[]
for b in N.iterdir():
 if not b.is_dir():continue
 if b.name not in byid:errors.append(dict(asset_id=b.name,reason='OUTSIDE_FROZEN115_NAMESPACE'));continue
 if (b/'COMMIT.json').exists():commits.append(b.name);continue
 try:
  raw=(b/'SOURCE_MANIFEST.json').read_bytes();mf=json.loads(raw);local=(T/'manifests'/(b.name+'.json')).read_bytes();assert raw==local
  files=[];verified_bytes=0;range_count=0
  for row in mf['members']:
   folder=b/'chunks'/hashlib.sha256(row['relative_path'].encode()).hexdigest();end=0
   for p in sorted(folder.glob('*.part.json')):
    part=json.loads(p.read_bytes());assert part['offset']==end and 0<part['size']<=134217728
    data=folder/part['name'];assert data.stat().st_size==part['size'];end+=part['size'];range_count+=1
   assert end<=row['size'];verified_bytes+=end
   for p in folder.glob('*.writing'):
    try:
     frame=p.with_name(p.name.removesuffix('.writing')+'.frame');header=json.loads(frame.read_bytes());size=p.stat().st_size;assert 0<=size<=header['size'] and header['offset']==end
     files.append(dict(relative_path=str(p.relative_to(b)),kind='OWNED_INCOMING_RANGE_PARTIAL',bytes=size,frame=header,resume='Compare exact incoming range prefix; preserve object/manifest/ranges'))
    except FileNotFoundError:files.append(dict(relative_path=str(p.relative_to(b)),kind='LIVE_ATOMIC_RENAME_TRANSITION'))
   tree=b/'tree'/row['relative_path'];writing=tree.with_name(tree.name+'.writing')
   if writing.exists():
    try:files.append(dict(relative_path=str(writing.relative_to(b)),kind='OWNED_TREE_ASSEMBLY_PARTIAL',bytes=writing.stat().st_size,expected_bytes=row['size'],resume='Validate against immutable range concatenation before any continuation; never discard verified ranges'))
    except FileNotFoundError:pass
  partials.append(dict(asset_id=b.name,object_id=mf['object_id'],manifest_sha256=hashlib.sha256(raw).hexdigest(),original_bytes=mf['source_data_bytes'],verified_range_bytes=verified_bytes,verified_ranges=range_count,partial_files=files,range_body_hashes_recomputed_by_this_audit=False,explanation='ACTIVE_OR_HELD_ORIGINAL_TRANSACTION; inspect final classification and exact process ownership'))
 except Exception as e:errors.append(dict(asset_id=b.name,reason=str(e),exception=type(e).__name__))
print(json.dumps(dict(unix=time.time(),state=state,supervisor=sup,own_execution_processes=own,unreadable_proc_entries=unreadable,committed_bundle_ids=sorted(commits),partial_transactions=partials,transaction_metadata_errors=errors,unrelated_processes_signaled=0)))
'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');args=ap.parse_args()
    x=remote('hrl-174-new',REMOTE,240)
    command="Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -like '*original174-verified-offload-reclaim-exec-20261024-v1*publish_continuation.py*' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell','-NoProfile','-Command',command],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    assert r.returncode==0,r.stderr
    publishers=json.loads(r.stdout) if r.stdout.strip() else []
    if isinstance(publishers,dict):publishers=[publishers]
    x['publisher_processes']=publishers
    x['driver_stopped']=not any(str(NATIVE+'/tools/offload_driver.py') in p['argv'] for p in x['own_execution_processes'])
    x['supervisor_stopped']=not any(str(NATIVE+'/tools/continuation_supervisor.py') in p['argv'] for p in x['own_execution_processes'])
    x['publisher_stopped']=not publishers
    x['final_mode_requested']=args.final
    if args.final:
        assert x['driver_stopped'] and x['supervisor_stopped'] and x['publisher_stopped'],'OWN_EXECUTION_OR_PUBLICATION_STILL_LIVE'
        assert not x['own_execution_processes'] and not x['unreadable_proc_entries'],'OWN_HELPER_OR_VISIBILITY_REQUIRES_REVIEW'
        assert not x['transaction_metadata_errors'],'UNEXPLAINED_TRANSACTION_METADATA_ERRORS'
        classifications=load(OUT/'HOLD_CLASSIFICATIONS.json') if (OUT/'HOLD_CLASSIFICATIONS.json').exists() else {}
        for p in x['partial_transactions']:
            c=classifications[p['asset_id']];assert c.get('partial_transaction_explanation') and c.get('evidence'),'UNEXPLAINED_PARTIAL_TRANSACTION'
        dump('FINAL_PROCESS_SHUTDOWN_AUDIT.json',x)
    else:dump('RUNTIME_AND_PARTIAL_TRANSACTION_AUDIT.json',x)
    print(json.dumps(dict(driver_stopped=x['driver_stopped'],supervisor_stopped=x['supervisor_stopped'],publisher_stopped=x['publisher_stopped'],committed_bundles=len(x['committed_bundle_ids']),partial_assets=[p['asset_id'] for p in x['partial_transactions']],errors=x['transaction_metadata_errors'],final_mode=args.final)))

if __name__=='__main__':main()
