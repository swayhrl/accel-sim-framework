"""Verify fetched immutable HEAD/tree/each pack blob/clean; external receipt only."""
from common import *
import argparse

def main(phase):
 ref='refs/ag4-publication/'+phase
 head=git(FW,'rev-parse','HEAD');fetched=git(FW,'rev-parse',ref);assert head==fetched
 tree=git(FW,'rev-parse','HEAD^{tree}');assert tree==git(FW,'rev-parse',ref+'^{tree}')
 assert not git(FW,'status','--porcelain')
 prefix=str(PACK.relative_to(FW));names=git(FW,'diff','--name-only','2f3a8c4b27780e2bf3818949a6e5356d9fd62327','HEAD').splitlines();assert names and all(n.startswith(prefix+'/') for n in names)
 entries=subprocess.check_output(['git','-C',str(FW),'ls-tree','-rz','HEAD','--',prefix]).split(b'\0');entries=[e for e in entries if e]
 parsed=[]
 for e in entries:
  meta,name=e.split(b'\t',1);mode,kind,obj=meta.split();assert kind==b'blob';parsed.append((obj.decode(),name.decode()))
 proc=subprocess.run(['git','-C',str(FW),'cat-file','--batch'],input=('\n'.join(x[0] for x in parsed)+'\n').encode(),capture_output=True,check=True);data=proc.stdout;offset=0;rows=[]
 for oid,name in parsed:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[0].decode()==oid and header[1]==b'blob';size=int(header[2]);start=end+1;body=data[start:start+size];assert data[start+size:start+size+1]==b'\n';offset=start+size+1
  local=FW/name;assert local.read_bytes()==body,name
  rows.append(dict(path=name,blob=oid,bytes=size,sha256=hashlib.sha256(body).hexdigest(),local_equals_fetched_blob=True))
 assert git(CORE,'rev-parse','HEAD')=='c8090115bd57512b1b23fca7d925301fa620c751' and not git(CORE,'status','--porcelain')
 receipt=dict(status='PASS_PUBLISHED_FETCH_BACK_HEAD_TREE_ALL_PACK_BLOBS_AND_CLEAN',utc=now(),phase=phase,head=head,fetched_head=fetched,tree=tree,reference=ref,blob_count=len(rows),blobs=rows,source_scope_only_AG4_pack=True,Framework_clean=True,Core_clean=True,Core_commit=git(CORE,'rev-parse','HEAD'))
 if (PACK/'EXECUTABLE_PREREGISTRATION.json').exists():receipt['manifest_sha256']=sha(PACK/'EXECUTABLE_PREREGISTRATION.json')
 name='PREREG_PUBLICATION_READBACK.json' if phase=='preregistered' else phase.upper()+'_PUBLICATION_READBACK.json'
 write(RAW/name,receipt,exclusive=True)
 print(json.dumps({k:v for k,v in receipt.items() if k!='blobs'}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--phase',choices=['cpu','preregistered','final'],required=True);main(a.parse_args().phase)
