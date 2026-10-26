"""Restore the one exact lavaMD trace from genuine164 to old174.

Run on hrl-174-new.  --self-check is local and read-only.  --preflight also
checks the old174 endpoint, readers and the hypothetical post-retirement
capacity gate.  --execute is required for payload writes.
"""
import argparse,fcntl,hashlib,json,os,pathlib,shlex,stat,struct,subprocess,sys,time
P=pathlib.Path;MIB=1024**2;RATE=15*MIB
TASK=P('/root/data/research_asset_verified_offload_20261024_v1')
OUT=TASK/'control/lavamd_exact_retirement_v1'
SOURCE_ROOT=P('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/lavaMD-rodinia-3.1/_boxes1d_10/traces')
BUNDLE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_90174dcf58988a5d')
BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
MANIFEST_SHA='75810b00842cb095dcb837ad5a7a888c192b4db5a06f0b1d23c17cf04ba3ce08'
COMMIT_SHA='a39062e9d39d483f9d517fc496683e8be838c5a8b78047ab51a0ddee1cf61686'

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def need(v,m):
    if not v:raise RuntimeError(m)
def identity(p):
    s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
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
    need(len(traces)==1 and traces[0]['relative_path']=='kernel-1.traceg' and traces[0]['size']==20776255925,'trace whitelist changed')
    need({x['relative_path'] for x in controls}=={'commandlist','kernelslist','kernelslist.g','stats.csv'},'control whitelist changed')
    need(digest((BUNDLE/'RANGE_INDEX.json').read_bytes())==c['range_index_sha256'],'range receipt changed')
    need(digest((BUNDLE/'TREE_VERIFICATION.json').read_bytes())==c['tree_verification_sha256'],'tree receipt changed')
    return m,traces[0],controls,c

RECEIVER=r'''
import fcntl,hashlib,json,os,pathlib,stat,struct,sys,time
P=pathlib.Path;MIB=1024**2;RATE=15*MIB;T=P('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'));import server_resources as rr
def need(v,m):
 if not v:raise RuntimeError(m)
def identity(p):
 s=P(p).lstat();return dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink,type='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special')
def same_numeric(a,b):return all(a[k]==b[k] for k in ['size','uid','gid','mode','mtime_ns'])
def same_exact(a,b):return all(a[k]==b[k] for k in ['dev','inode','size','allocated','mtime_ns','ctime_ns','uid','gid','mode','nlink','type'])
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
request=json.loads(sys.stdin.buffer.readline());mode=request['mode'];root=P(request['source_root']);trace=request['trace'];controls=request['controls'];root_meta=request['source_root_identity'];frozen=request['source_trace_identity']
need(mode in ['preflight','execute'],'bad mode');need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-174','mnt:[4026534768]'),'wrong old174 endpoint');need(root.is_dir() and not root.is_symlink(),'source root changed')
lease=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock','rb');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
control_ids=[]
for row in controls:
 p=safe(root,row['relative_path']);need(p.is_file() and not p.is_symlink() and same_numeric(identity(p),row) and full_hash(p)==row['sha256'],'control changed '+str(p));control_ids.append(identity(p))
names={p.name for p in root.iterdir()};allowed={x['relative_path'] for x in controls}|{'kernel-1.traceg'};need(names<=allowed and {x['relative_path'] for x in controls}<=names,'unexpected destination membership')
p=safe(root,'kernel-1.traceg');temp=p.with_name(p.name+'.LAVAMD_restore.writing');need(not os.path.lexists(temp),'owned restore partial requires review')
existing=p.exists()
if existing:need(p.is_file() and not p.is_symlink() and same_exact(identity(p),frozen),'existing trace identity differs')
selected=control_ids+[identity(root)]+([identity(p)] if existing else []);rw=rr.selected_readers_writers(selected,[])
gate=rr.admission('SOURCE',include_activity=False,allowed_lock_pids=(os.getpid(),),metadata_only=True);disk=os.statvfs('/root/data');free=disk.f_bavail*disk.f_frsize;allocated=((trace['size']+4095)//4096)*4096
projected=free+(frozen['allocated'] if existing else 0);required=gate['SSD_required_bytes']+allocated;capacity_pass=(projected>=required and disk.f_favail>=100000)
pre=dict(event='PREFLIGHT',mode=mode,trace_present=existing,source_trace_identity_match=existing,controls_verified=4,reader_writer_check=rw,SSD_available_bytes=free,hypothetical_post_retirement_available_bytes=projected,SSD_contract_required_bytes=gate['SSD_required_bytes'],restore_payload_allocated_estimate=allocated,required_available_before_restore_bytes=required,hypothetical_restore_capacity_pass=capacity_pass,resource_gate=gate,safety={'partial_collision_absent':True,'unexpected_members_absent':True,'no_overwrite_publish':'hard-link publication'})
reply(pre)
if mode=='preflight':sys.exit(0)
need(not existing,'execute requires retired trace to be absent');need(capacity_pass,'RESOURCE_HOLD_FULL_LAVAMD_RESTORE_CAPACITY')
length=struct.unpack('!Q',exact(8))[0];need(length<=MIB,'header too large');header=json.loads(exact(length));need(header=={'event':'FILE','relative_path':trace['relative_path'],'size':trace['size'],'sha256':trace['sha256']},'unexpected restore frame')
h=hashlib.sha256();left=trace['size']
with temp.open('xb') as out:
 while left:
  b=exact(min(MIB,left));out.write(b);h.update(b);left-=len(b)
 out.flush();os.fsync(out.fileno())
need(h.hexdigest()==trace['sha256'] and temp.stat().st_size==trace['size'],'streamed restore SHA mismatch');need(full_hash(temp)==trace['sha256'],'closed restore SHA mismatch')
os.chown(temp,trace['uid'],trace['gid']);os.chmod(temp,trace['mode']);os.utime(temp,ns=(trace['mtime_ns'],trace['mtime_ns']));need(same_numeric(identity(temp),trace),'restored numeric metadata mismatch');os.link(temp,p);temp.unlink();need(same_numeric(identity(p),trace),'published restore metadata mismatch')
length=struct.unpack('!Q',exact(8))[0];header=json.loads(exact(length));need(header=={'event':'DONE'},'missing DONE frame')
os.chown(root,root_meta['uid'],root_meta['gid']);os.chmod(root,root_meta['mode']);os.utime(root,ns=(root_meta['mtime_ns'],root_meta['mtime_ns']));reply(dict(event='RESTORE_DONE',restored='kernel-1.traceg',bytes=trace['size'],sha256=trace['sha256'],root_numeric_metadata_restored=True,ctime_not_restorable=True))
'''

def receiver(mode,m,trace,controls,source_identity):
    target_lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(target_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    request=dict(mode=mode,source_root=str(SOURCE_ROOT),source_root_identity=m['source_root_identity'],trace=trace,controls=controls,source_trace_identity=source_identity)
    boot='import sys,json;exec(compile(json.loads(sys.stdin.buffer.readline()),"lavamd_restore_receiver.py","exec"),{"__name__":"lavamd_restore_receiver"})'
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174']
    p=subprocess.Popen(ssh+['python3 -B -c '+shlex.quote(boot)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.stdin.write((json.dumps(RECEIVER)+'\n').encode()+canon(request));p.stdin.flush();pre=json.loads(p.stdout.readline());need(pre['event']=='PREFLIGHT','old174 preflight failed '+p.stderr.read().decode(errors='replace')[-2000:])
    if mode=='preflight':
        p.stdin.close();rc=p.wait(timeout=60);need(rc==0,'preflight receiver failed '+p.stderr.read().decode(errors='replace')[-2000:]);return pre
    src=safe(BUNDLE/'tree',trace['relative_path']);before=identity(src);header=canon(dict(event='FILE',relative_path=trace['relative_path'],size=trace['size'],sha256=trace['sha256']));p.stdin.write(struct.pack('!Q',len(header))+header);h=hashlib.sha256();count=0;started=time.monotonic()
    with src.open('rb') as f:
        while True:
            b=f.read(MIB)
            if not b:break
            p.stdin.write(b);h.update(b);count+=len(b);time.sleep(max(0,count/RATE-(time.monotonic()-started)))
    need(identity(src)==before and count==trace['size'] and h.hexdigest()==trace['sha256'],'true164 changed during restore');done=canon({'event':'DONE'});p.stdin.write(struct.pack('!Q',len(done))+done);p.stdin.flush();final=json.loads(p.stdout.readline());p.stdin.close();rc=p.wait(timeout=60);need(rc==0,'restore receiver failed '+p.stderr.read().decode(errors='replace')[-3000:]);need(final['event']=='RESTORE_DONE','restore ACK mismatch');return dict(preflight=pre,final=final)

def safety_tests():
    passed=[]
    for value in ['../escape','/absolute','x\\y']:
        try:safe(BUNDLE/'tree',value)
        except RuntimeError:passed.append(value)
    need(len(passed)==3,'unsafe path rejection failed');compile(RECEIVER,'lavamd_restore_receiver.py','exec')
    return dict(unsafe_paths_rejected=passed,receiver_compiles=True,exclusive_no_overwrite_publish=True,owned_partial_collision_fails_closed=True)
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--self-check',action='store_true');g.add_argument('--preflight',action='store_true');g.add_argument('--execute',action='store_true');args=ap.parse_args()
    mount=mount_check();m,trace,controls,c=load_scope();tests=safety_tests();actual={x.relative_to(BUNDLE/'tree').as_posix() for x in (BUNDLE/'tree').rglob('*') if x.is_file() and not x.is_symlink()};need(actual=={x['relative_path'] for x in m['members']},'true164 tree membership changed')
    source=json.loads((OUT/'SOURCE_FULL_SHA_REVERIFY.json').read_bytes());need(source['status']=='PASS' and source['all_manifest_SHA_identity_match'],'Source SHA receipt changed');srows={x['relative_path']:x for x in source['rows']};need(all(srows[x['relative_path']]['sha256']==x['sha256'] for x in m['members']),'Source receipt scope changed');row=srows['kernel-1.traceg']
    target=json.loads((OUT/'TARGET_FULL_SHA_REVERIFY.json').read_bytes());need(target['status']=='PASS' and target['all_manifest_SHA_identity_match'],'target SHA receipt changed');trows={x['relative_path']:x for x in target['rows']}
    for member in m['members']:
        trow=trows[member['relative_path']];current_target=identity(BUNDLE/'tree'/member['relative_path']);need(trow['sha256']==member['sha256'] and all(current_target[k]==trow['identity'][k] for k in current_target),'true164 SHA receipt identity changed '+member['relative_path'])
    result=dict(status='SELF_CHECK_PASS',asset_id=m['primary_asset_id'],trace=trace['relative_path'],bytes=trace['size'],controls=[x['relative_path'] for x in controls],mount=mount,manifest_sha256=MANIFEST_SHA,commit_sha256=COMMIT_SHA,safety_tests=tests,buffer_bytes=MIB,rate_limit_bytes_per_second=RATE,full_native_restore_performed=False)
    if args.self_check:print(json.dumps(result,sort_keys=True));return
    mode='preflight' if args.preflight else 'execute';result['old174']=receiver(mode,m,trace,controls,row['identity']);result['status']=('PREFLIGHT_PASS' if result['old174']['hypothetical_restore_capacity_pass'] else 'PREFLIGHT_CAPACITY_HOLD') if mode=='preflight' else 'RESTORE_DONE';print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
