"""Restore the exact 502 SRAD .traceg files from genuine164 to old174.

Run on hrl-174-new. Requires --execute for payload writes. No destination
overwrite, no full 174-new staging, 1 MiB buffers, closed-reopen SHA on old174.
"""
import argparse,fcntl,hashlib,json,os,pathlib,shlex,stat,struct,subprocess,sys,time
P=pathlib.Path;MIB=1024**2;RATE=15*MIB
TASK=P('/root/data/research_asset_verified_offload_20261024_v1')
SOURCE_ROOT=P('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/srad_v1-rodinia-3.1/100_0_5_502_458/traces')
BUNDLE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_300274ed6041b087')
BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
MANIFEST_SHA='b8007329860a36de022edb70c2a29ea6570502c5f307d47a1d515f73796432b3'
COMMIT_SHA='7937f45865f94b07a1634f48fe551ca312f6296d42386e3722f809f6fb4377ce'

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def need(v,m):
    if not v:raise RuntimeError(m)
def identity(p):
    s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
def same_numeric(a,b):return all(a[k]==b[k] for k in ['size','uid','gid','mode','mtime_ns'])
def safe(root,name):
    rel=P(name);need(not rel.is_absolute() and '..' not in rel.parts and '\\' not in name,'unsafe member');dest=P(root)/rel
    for parent in [dest.parent,*dest.parent.parents]:
        if parent==P(root).parent:break
        need(not parent.is_symlink(),'symlink destination ancestor')
    return dest
def mount_check():
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-sshfs-174','mnt:[4026535153]'),'wrong restore endpoint')
    m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(BUNDLE)],text=True))['filesystems'][0]
    need(m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs','not genuine164')
    return m
def load_scope():
    raw=(BUNDLE/'SOURCE_MANIFEST.json').read_bytes();need(digest(raw)==MANIFEST_SHA,'manifest changed');m=json.loads(raw)
    commit=(BUNDLE/'COMMIT.json').read_bytes();need(digest(commit)==COMMIT_SHA,'COMMIT changed');c=json.loads(commit);need(c['manifest_sha256']==MANIFEST_SHA,'COMMIT selector changed')
    traces=[x for x in m['members'] if x['relative_path'].endswith('.traceg')];controls=[x for x in m['members'] if not x['relative_path'].endswith('.traceg')]
    need(len(traces)==502 and {x['relative_path'] for x in controls}=={'commandlist','kernelslist','kernelslist.g','stats.csv'},'restore whitelist changed')
    return m,traces,controls

RECEIVER=r'''
import fcntl,hashlib,json,os,pathlib,stat,struct,sys,time
P=pathlib.Path;MIB=1024**2;RATE=15*MIB;T=P('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'));import server_resources as rr
def need(v,m):
 if not v:raise RuntimeError(m)
def identity(p):
 s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
def same_numeric(a,b):return all(a[k]==b[k] for k in ['size','uid','gid','mode','mtime_ns'])
def safe(root,name):
 rel=P(name);need(not rel.is_absolute() and '..' not in rel.parts and '\\' not in name,'unsafe member');p=root/rel
 for parent in [p.parent,*p.parent.parents]:
  if parent==root.parent:break
  need(not parent.is_symlink(),'symlink destination ancestor')
 return p
def full_hash(p,rate=30*MIB):
 h=hashlib.sha256();n=0;started=time.monotonic()
 with P(p).open('rb') as f:
  while True:
   b=f.read(MIB)
   if not b:break
   h.update(b);n+=len(b);time.sleep(max(0,n/rate-(time.monotonic()-started)))
 return h.hexdigest()
def exact(n):
 out=bytearray()
 while len(out)<n:
  b=sys.stdin.buffer.read(n-len(out));need(b,'sender EOF');out.extend(b)
 return bytes(out)
def reply(x):sys.stdout.write(json.dumps(x,separators=(',',':'))+'\n');sys.stdout.flush()
request=json.loads(sys.stdin.buffer.readline());root=P(request['source_root']);traces=request['traces'];controls=request['controls'];root_meta=request['source_root_identity']
need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'wrong old174 endpoint');need(root.is_dir() and not root.is_symlink(),'source root changed')
lease=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock','rb');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
control_ids=[]
for row in controls:
 p=safe(root,row['relative_path']);need(p.is_file() and not p.is_symlink() and same_numeric(identity(p),row) and full_hash(p)==row['sha256'],'control changed '+str(p));control_ids.append(identity(p))
actual_trace={p.relative_to(root).as_posix() for p in root.rglob('*.traceg') if p.is_file() and not p.is_symlink()};allowed={x['relative_path'] for x in traces};need(actual_trace<=allowed,'unexpected traceg at restore destination')
missing=[];existing=[]
for row in traces:
 p=safe(root,row['relative_path']);temp=p.with_name(p.name+'.SRAD_restore.writing');need(not os.path.lexists(temp),'owned restore partial requires review '+str(temp))
 if p.exists():need(p.is_file() and not p.is_symlink() and same_numeric(identity(p),row) and full_hash(p)==row['sha256'],'existing trace differs '+str(p));existing.append(row['relative_path'])
 else:missing.append(row)
gate=rr.admission('SOURCE',include_activity=False,allowed_lock_pids=(os.getpid(),));allocated=sum(((x['size']+4095)//4096)*4096 for x in missing);disk=os.statvfs('/root/data');need(disk.f_bavail*disk.f_frsize>=gate['SSD_required_bytes']+allocated,'RESOURCE_HOLD_FULL_SRAD_RESTORE_CAPACITY')
rr.selected_readers_writers(control_ids+[identity(root)],[]);reply(dict(event='READY',missing=[x['relative_path'] for x in missing],existing_verified=len(existing),missing_bytes=sum(x['size'] for x in missing),resource_gate=gate))
byname={x['relative_path']:x for x in traces}
for expected in missing:
 length=struct.unpack('!Q',exact(8))[0];need(length<=MIB,'header too large');header=json.loads(exact(length));need(header=={'event':'FILE','relative_path':expected['relative_path'],'size':expected['size'],'sha256':expected['sha256']},'unexpected restore frame')
 p=safe(root,expected['relative_path']);need(not os.path.lexists(p),'destination appeared');temp=p.with_name(p.name+'.SRAD_restore.writing');h=hashlib.sha256();left=expected['size']
 with temp.open('xb') as out:
  while left:
   b=exact(min(MIB,left));out.write(b);h.update(b);left-=len(b)
  out.flush();os.fsync(out.fileno())
 need(h.hexdigest()==expected['sha256'] and temp.stat().st_size==expected['size'],'streamed restore SHA mismatch');need(full_hash(temp)==expected['sha256'],'closed restore SHA mismatch')
 os.chown(temp,expected['uid'],expected['gid']);os.chmod(temp,expected['mode']);os.utime(temp,ns=(expected['mtime_ns'],expected['mtime_ns']));need(same_numeric(identity(temp),expected),'restored numeric metadata mismatch');os.link(temp,p);temp.unlink();need(same_numeric(identity(p),expected),'published restore metadata mismatch');reply(dict(event='FILE_RESTORED',relative_path=expected['relative_path'],sha256=expected['sha256'],bytes=expected['size']))
length=struct.unpack('!Q',exact(8))[0];header=json.loads(exact(length));need(header=={'event':'DONE'},'missing DONE frame')
for row in traces:
 p=safe(root,row['relative_path']);need(p.is_file() and not p.is_symlink() and same_numeric(identity(p),row),'final trace identity mismatch')
for row in controls:
 p=safe(root,row['relative_path']);need(p.is_file() and not p.is_symlink() and same_numeric(identity(p),row),'final control identity mismatch')
os.chown(root,root_meta['uid'],root_meta['gid']);os.chmod(root,root_meta['mode']);os.utime(root,ns=(root_meta['mtime_ns'],root_meta['mtime_ns']));reply(dict(event='RESTORE_DONE',traceg=502,restored=len(missing),preexisting_verified=len(existing),root_numeric_metadata_restored=True,ctime_not_restorable=True))
'''

def execute(m,traces,controls):
    target_lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(target_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    request=dict(source_root=str(SOURCE_ROOT),source_root_identity=m['source_root_identity'],traces=traces,controls=controls)
    boot='import sys,json;exec(compile(json.loads(sys.stdin.buffer.readline()),"srad_restore_receiver.py","exec"),{"__name__":"srad_restore_receiver"})'
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174']
    p=subprocess.Popen(ssh+['python3 -B -c '+shlex.quote(boot)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.stdin.write((json.dumps(RECEIVER)+'\n').encode()+canon(request));p.stdin.flush();ready=json.loads(p.stdout.readline());need(ready['event']=='READY','old174 restore preflight failed '+p.stderr.read().decode(errors='replace')[-2000:]);missing=set(ready['missing'])
    for i,row in enumerate(traces):
        if row['relative_path'] not in missing:continue
        src=safe(BUNDLE/'tree',row['relative_path']);before=identity(src);need(src.is_file() and not src.is_symlink() and src.stat().st_size==row['size'],'true164 source changed');header=canon(dict(event='FILE',relative_path=row['relative_path'],size=row['size'],sha256=row['sha256']));p.stdin.write(struct.pack('!Q',len(header))+header);h=hashlib.sha256();count=0;started=time.monotonic()
        with src.open('rb') as f:
            while True:
                b=f.read(MIB)
                if not b:break
                p.stdin.write(b);h.update(b);count+=len(b);time.sleep(max(0,count/RATE-(time.monotonic()-started)))
        p.stdin.flush();need(identity(src)==before and count==row['size'] and h.hexdigest()==row['sha256'],'true164 changed during restore');ack=json.loads(p.stdout.readline());need(ack['event']=='FILE_RESTORED' and ack['sha256']==row['sha256'],'restore ACK mismatch');print(json.dumps(dict(progress=i+1,restored=ack['relative_path'],bytes=ack['bytes'])),flush=True)
    done=canon({'event':'DONE'});p.stdin.write(struct.pack('!Q',len(done))+done);p.stdin.flush();final=json.loads(p.stdout.readline());p.stdin.close();rc=p.wait(timeout=60);need(rc==0,'old174 receiver failed '+p.stderr.read().decode(errors='replace')[-3000:]);print(json.dumps(final,sort_keys=True))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-check',action='store_true');ap.add_argument('--execute',action='store_true');args=ap.parse_args();need(args.self_check!=args.execute,'choose exactly one mode')
    mount=mount_check();m,traces,controls=load_scope();compile(RECEIVER,'srad_restore_receiver.py','exec')
    actual={x.relative_to(BUNDLE/'tree').as_posix() for x in (BUNDLE/'tree').rglob('*') if x.is_file() and not x.is_symlink()};need(actual=={x['relative_path'] for x in m['members']},'true164 tree membership changed')
    result=dict(status='SELF_CHECK_PASS',asset_id=m['primary_asset_id'],traceg=len(traces),controls=[x['relative_path'] for x in controls],bytes=sum(x['size'] for x in traces),mount=mount,buffer_bytes=MIB,rate_limit_bytes_per_second=RATE,full_native_restore_performed=False)
    if args.self_check:print(json.dumps(result,sort_keys=True));return
    execute(m,traces,controls)

if __name__=='__main__':main()
