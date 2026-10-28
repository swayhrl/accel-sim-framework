from pathlib import Path
import os,json,hashlib
NATIVE='/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1'
REMOTE='/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2'
def need(v,m):
 if not v:raise RuntimeError(m)
def remote(p):
 p=Path(p);need(p.is_relative_to(Path(NATIVE)),'EXACT_NAS_SOURCE_DOMAIN');return Path(REMOTE)/p.relative_to(NATIVE)
def exact_existing_ST_alias(a,H):
 r=a['Root_existing_ST_alias_contract_ref'];b=H.raw(remote(r['path']),2*2**20)
 need(len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],'ROOT_EXISTING_ST_ALIAS_RAW')
 x=json.loads(b)
 need(x['schema']=='ROOT_EXACT3_EXISTING_SINGLETHREAD_ST_ALIAS_V1'and x['status']=='ROOT_APPROVED_EXISTING_ALIAS_NO_NEW_MOUNT','ROOT_EXISTING_ST_ALIAS_STATUS')
 need(x['alias']==REMOTE and x['Native_base']==NATIVE and x['provider_source']=='hrl174new:'+NATIVE and x['filesystem']=='fuse.sshfs','EXACT_EXISTING_ST_DOMAIN')
 rows=[]
 for line in Path('/proc/self/mountinfo').read_text().splitlines():
  left,right=line.split(' - ',1);f=left.split()
  if f[4]==REMOTE:rows.append((f,right.split()))
 need(len(rows)==1 and rows[0][1][:2]==['fuse.sshfs',x['provider_source']],'ACTUAL_ST_PROVIDER_BACKEND')
 dev=os.stat(REMOTE).st_dev;need(dev==x['st_dev']and rows[0][0][2]==str(os.major(dev))+':'+str(os.minor(dev)),'EXACT_EXISTING_MOUNT_DEV')
 owner=x['sshfs_owner'];p=Path('/proc',str(owner['pid']))
 ticks=lambda:p.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]
 need(ticks()==owner['start_ticks']and p.stat().st_uid==1004,'EXACT_EXISTING_ST_DAEMON')
 raw=p.joinpath('cmdline').read_bytes();args=[v.decode()for v in raw.split(b'\0')if v]
 need(hashlib.sha256(raw).hexdigest()==owner['cmdline_sha256']and Path(args[0]).name=='sshfs'and '-s'in args and REMOTE in args and ticks()==owner['start_ticks'],'ST_DAEMON_SINGLETHREAD_AND_CURRENT_IDENTITY')
 return dict(existing_alias_only=True,st_dev=dev,provider_source=x['provider_source'],daemon_owner=owner,no_new_mount=True)
