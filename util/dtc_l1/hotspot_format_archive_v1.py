#!/usr/bin/env python3
from pathlib import Path
import tarfile,hashlib,csv,json,time
import argparse
ap=argparse.ArgumentParser(description='Read-only source archive member identity check; stops after the Hotspot subtree.')
ap.add_argument('--archive',type=Path,required=True)
ap.add_argument('--output-dir',type=Path,required=True)
a=ap.parse_args();archive=a.archive;out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
rows=[];seen=False;count=0;start=time.time();last=0
with tarfile.open(archive,mode='r|gz') as tar:
 for m in tar:
  count+=1
  if time.time()-last>30:
   print(json.dumps(dict(members_seen=count,tar_offset=m.offset,name=m.name,elapsed_s=time.time()-start)),flush=True);last=time.time()
  if '/hotspot-rodinia-3.1/' not in m.name:
   if seen:
    boundary=m.name;break
   continue
  seen=True;h=hashlib.sha256();data=None
  if m.isfile():
   f=tar.extractfile(m)
   if m.size<10000:
    data=f.read();h.update(data)
   else:
    while block:=f.read(1024*1024):h.update(block)
  rows.append(dict(name=m.name,size=m.size,mtime=m.mtime,type=m.type.decode(),linkname=m.linkname,tar_offset=m.offset,sha256=h.hexdigest() if m.isfile() else '',small_text=data.decode() if data else ''))
 else:boundary='EOF'
with (out/'ARCHIVE_HOTSPOT_MEMBERS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
fixed=[r for r in rows if '1024_2_2' in r['name'] and r['name'].endswith('kernel-1.traceg')]
assert len(fixed)==1 and fixed[0]['sha256']=='ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8'
assert not any(r['name'].endswith('.trace') for r in rows)
receipt=dict(archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256='NOT_COMPUTED_FULL_ARCHIVE_NOT_NEEDED_FOR_MEMBER_IDENTITY',members_seen=count,hotspot_members=len(rows),next_member=boundary,elapsed_s=time.time()-start,scope='STOPPED_AFTER_CONTIGUOUS_HOTSPOT_SUBTREE_NOT_FULL_ARCHIVE_AUDIT',fixed_member=fixed[0],original_ungrouped_trace_found=False)
(out/'ARCHIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
