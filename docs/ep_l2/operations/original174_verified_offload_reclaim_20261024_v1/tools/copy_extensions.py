"""Adapters appended to the qualified b93fc0db raw-range implementation.

Only frozen file selection, fresh resource/reader gates, directory metadata and
generic research records are added. There is one finite sender and receiver.
"""
import server_resources as rr
ACTIVE_SENDER=None

class Resources:
    def __init__(self,testing=False):self.last=0;self.last_value=None;self.samples=[]
    def __call__(self,force=False):
        if not force and self.last_value and time.monotonic()-self.last<10:return self.last_value
        value=rr.admission('TARGET',include_activity=False)
        self.last=time.monotonic();self.last_value=value;self.samples.append(value)
        self.samples=self.samples[-100:]
        return value

_qualified_hash_file=hash_file
def hash_file(path,rate=None,gate=None):
    if rate is None:rate=15*MIB if ACTIVE_SENDER is not None and ACTIVE_SENDER.poll() is None else 30*MIB
    return _qualified_hash_file(path,rate=rate,gate=gate)

_qualified_publish_bytes=publish_bytes
def publish_bytes(path,blob,v):
    _qualified_publish_bytes(path,blob,v)
    if P(path).name=='trace_copy.py':
        _qualified_publish_bytes(P(path).parent/'server_resources.py',P(rr.__file__).read_bytes(),v)

def source_boot(action,request):
    if request.get('source_role')=='TARGET':
        p=subprocess.Popen(['/usr/bin/python3','-B',str(P(__file__)),action+'-local'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p.stdin.write(canon(request));p.stdin.close();p.stdin=None;return p
    code=P(__file__).read_text();resources=P(rr.__file__).read_text()
    prefix='import types,sys\nr=types.ModuleType("server_resources");r.__file__="authorized_in_memory_source_resources.py"\nexec('+repr(resources)+',r.__dict__);sys.modules["server_resources"]=r\n'
    payload=prefix+code+'\n'+('source_send' if action=='source' else 'prepare_source')+'(json.loads(sys.stdin.buffer.readline()))\n'
    boot='import sys,json;exec(compile(json.loads(sys.stdin.buffer.readline()),"frozen_copy_source.py","exec"),{"__name__":"copy_source"})'
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174']
    p=subprocess.Popen(ssh+['python3 -B -c '+shlex.quote(boot)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.stdin.write((json.dumps(payload)+'\n').encode()+canon(request));p.stdin.close();p.stdin=None;return p

def source_gate(role,last,metadata_only=False):
    if time.monotonic()-last[0]>=10:
        last[1]=rr.admission(role,include_activity=False,allowed_lock_pids=(os.getppid(),) if role=='TARGET' else (),metadata_only=metadata_only)
        last[0]=time.monotonic()
    return last[1]

def check_source_role(role):
    expected=('huangrulin-174','mnt:[4026534768]') if role=='SOURCE' else ('huangrulin-sshfs-174','mnt:[4026535153]')
    need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==expected,'SOURCE_ENDPOINT_IDENTITY_HOLD')
    try:os.nice(19)
    except OSError:pass
    if P('/usr/bin/ionice').exists():subprocess.run(['/usr/bin/ionice','-c','3','-p',str(os.getpid())],check=True,stdout=subprocess.DEVNULL)

def normalize_frozen(row):
    row=dict(row)
    if isinstance(row['mode'],str):row['mode']=int(row['mode'],8)
    return row

def prepare_source(request):
    scope=request['scope'];role=request.get('source_role','SOURCE');check_source_role(role)
    root=P(scope['source_root']);need(root.is_absolute() and str(root).startswith(('/workspace/','/root/share/accel-sim/','/root/share/workspace_migrated_20260905/','/root/workspace/')),'SOURCE_NAMESPACE_SCOPE_HOLD')
    need(root.is_dir() and not root.is_symlink(),'SOURCE_ROOT_NOT_REGULAR_DIRECTORY_HOLD')
    expected=[normalize_frozen(x) for x in scope['files']]
    metadata_only=bool(request.get('metadata_only'))
    if metadata_only:
        need(all(isinstance(x.get('sha256'),str) and len(x['sha256'])==64 for x in expected),'METADATA_ONLY_REQUIRES_PRIOR_FULL_SHA_EVERY_FILE')
        need(sum(min(128,x['size']) for x in expected)<=4*MIB,'BOUNDED_METADATA_PREFIX_READ_LIMIT')
    last=[0,None];before=source_gate(role,last,metadata_only)
    if not metadata_only:
        lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for row in expected:
        path=safe(root,row['relative_path']);need(same_source(identity(path),row),'PREHASH_FROZEN_IDENTITY_CHANGED '+str(path))
    source_root_before=identity(root)
    directories={'.':source_root_before};parents={'.'}
    for row in expected:
        rel=P(row['relative_path']).parent
        while str(rel)!='.':parents.add(rel.as_posix());rel=rel.parent
    # Finite metadata traversal of this exact frozen research root only.
    # Never follow symlinks or admit additional file bodies.
    visited=0;symlinks=[];limit=max(4096,4*len(expected)+4096)
    for base,ds,fs in os.walk(root,followlinks=False):
        visited+=len(ds)+len(fs);need(visited<=limit,'BOUNDED_SCOPE_METADATA_LIMIT_HOLD')
        rel=P(base).relative_to(root).as_posix()
        if rel in parents or not ds and not fs:directories[rel]=identity(base)
        for name in list(ds)+fs:
            q=P(base)/name
            if q.is_symlink():symlinks.append(dict(path=q.relative_to(root).as_posix(),target=os.readlink(q),identity=identity(q),copied=False))
    for rel in parents:
        q=safe(root,rel) if rel!='.' else root
        need(q.is_dir() and not q.is_symlink(),'SELECTED_DIRECTORY_SYMLINK_HOLD')
        directories[rel]=identity(q)
    rr.selected_readers_writers([identity(safe(root,x['relative_path'])) for x in expected],list(directories.values()))
    rows=[];new_sha_bytes=0;reused_sha_bytes=0;last_progress=0
    for row in sorted(expected,key=lambda x:x['relative_path']):
        path=safe(root,row['relative_path']);a=identity(path);h=hashlib.sha256();count=0;prefix=b'';known=row.get('sha256');begin=time.monotonic()
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
        with os.fdopen(fd,'rb',buffering=0) as f:
            if known:prefix=f.read(min(128,a['size']));reused_sha_bytes+=a['size']
            else:
                while True:
                    b=f.read(MIB)
                    if not b:break
                    if not prefix:prefix=b[:128]
                    h.update(b);count+=len(b);new_sha_bytes+=len(b)
                    time.sleep(max(0,count/(30*MIB)-(time.monotonic()-begin)));source_gate(role,last,metadata_only)
                    if time.monotonic()-last_progress>=10:
                        emit(dict(event='PREHASH_PROGRESS',asset=scope['asset_id'],file=row['relative_path'],current_file_bytes=count,new_hashed_bytes=new_sha_bytes));last_progress=time.monotonic()
        need(same_source(a,identity(path)) and (known or count==row['size']),'SOURCE_CHANGED_DURING_PREHASH')
        b=dict(a,relative_path=row['relative_path'],sha256=known or h.hexdigest(),header_prefix_hex=prefix.hex());rows.append(b);source_gate(role,last,metadata_only)
    need(same_source(source_root_before,identity(root)),'SOURCE_DIRECTORY_CHANGED_DURING_PREHASH')
    entry='__NO_SELECTED_COMMANDLIST__';commandlist=b'';ordered=[]
    for x in rows:
        if x['relative_path']=='kernelslist.g':
            entry='kernelslist.g';need(x['size']<=4*MIB,'BOUNDED_COMMANDLIST_SIZE_HOLD');commandlist=(root/entry).read_bytes()
            need(digest(commandlist)==x['sha256'],'COMMANDLIST_SHA_CHANGED')
            ordered=[z.strip() for z in commandlist.decode(errors='strict').splitlines() if z.strip().endswith(('.trace','.traceg'))]
    object_id=digest(canon(dict(root=str(root),members=rows,selected_directories=directories,source_symlink_metadata=symlinks)))
    manifest=dict(schema='FROZEN_GENERIC_RESEARCH_FILE_BUNDLE_V2_SYMLINK_META',primary_asset_id=scope['asset_id'],kind=scope['kind'],source_role=role,source_root=str(root),source_root_identity=source_root_before,members=rows,directory_metadata=directories,source_unselected_symlink_references=symlinks,source_data_bytes=sum(x['size'] for x in rows),entry_name=entry,commandlist_bytes_hex=commandlist.hex(),ordered_kernel_members=ordered,freeze_status='FROZEN_EXACT_SOURCE_METADATA_AND_FULL_SHA',object_id=object_id,reuse=None,new_true164_bundle=request['true164_bundle'],authorization='USER_20261024_COPY_AND_VERIFIED_LOCAL_RETIREMENT',base_frozen_scope=scope['asset_id'],base_contract='ff9ce679174461450bdcba7e84c19de65c2a9c02',source_disposition='SOURCE_KEEP_UNLESS_SEPARATELY_ADMITTED_VERIFIED_RETIREMENT')
    emit(dict(event='PREPARED',manifest=manifest,source_new_hashed_bytes=new_sha_bytes,prior_full_SHA_reused_bytes=reused_sha_bytes,metadata_only=metadata_only,resources_before=before,resources_after=source_gate(role,[0,None],metadata_only),source_writes=0))

def source_send(request,testing=False):
    m=request['manifest'];role=m.get('source_role','SOURCE');check_source_role(role);last=[0,None];source_gate(role,last)
    lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    rr.selected_readers_writers(m['members'],[m['source_root_identity']])
    def frame(x):b=canon(x);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
    for row in m['members']:
        path=safe(m['source_root'],row['relative_path']);a=identity(path);need(same_source(a,row),'FROZEN_SOURCE_CHANGED_BEFORE_TRANSFER');h=hashlib.sha256();offset=0
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
        with os.fdopen(fd,'rb',buffering=0) as f:
            while True:
                source_gate(role,last);b=f.read(CHUNK)
                if not b:break
                h.update(b)
                if offset>=request['skip'][row['relative_path']]:
                    frame(dict(event='CHUNK',path=row['relative_path'],offset=offset,size=len(b),sha256=digest(b)))
                    for j in range(0,len(b),MIB):
                        part=memoryview(b)[j:j+MIB];time.sleep(len(part)/RATE);sys.stdout.buffer.write(part);sys.stdout.buffer.flush();source_gate(role,last)
                offset+=len(b)
        need(offset==row['size'] and same_source(a,identity(path)) and h.hexdigest()==row['sha256'],'SOURCE_EOF_SHA_OR_IDENTITY_MISMATCH')
        frame(dict(event='FILE_END',path=row['relative_path'],size=offset,sha256=h.hexdigest(),source_before_after_identity_unchanged=True,source_disposition='SOURCE_KEEP'))
    frame(dict(event='SOURCE_DONE',Source_simulator_starts=0,source_disposition='SOURCE_KEEP'))

def spawn_sender(manifest,skip,testing=False):
    global ACTIVE_SENDER
    ACTIVE_SENDER=source_boot('source',dict(manifest=manifest,skip=skip,source_role=manifest.get('source_role','SOURCE')))
    return ACTIVE_SENDER

_qualified_restore=restore_native
_qualified_verify_tree=verify_tree
def verify_tree(tree,manifest,gate,rehash=False):
    root=P(tree);committed=(root.parent/'COMMIT.json').exists()
    for rel in manifest.get('directory_metadata',{}):
        p=root if rel=='.' else safe(root,rel)
        if committed:need(p.is_dir() and not p.is_symlink(),'COMMITTED_EMPTY_DIRECTORY_MISSING')
        else:p.mkdir(parents=True,exist_ok=True)
    for link in manifest.get('source_unselected_symlink_references',[]):
        p=safe(root,link['path']);target=P(link['target']);need(not target.is_absolute() and '..' not in target.parts,'EXTERNAL_SYMLINK_REQUIRES_SEPARATE_RECOVERY_DEPENDENCY_HOLD')
        resolved=p.parent/target;need(resolved.is_file() and not resolved.is_symlink(),'INTERNAL_SYMLINK_TARGET_NOT_IN_ARCHIVED_PAYLOAD')
        if not committed and not os.path.lexists(p):os.symlink(link['target'],p)
        need(p.is_symlink() and os.readlink(p)==link['target'],'ARCHIVED_SYMLINK_SEMANTICS_CHANGED')
    return _qualified_verify_tree(tree,manifest,gate,rehash)

def restore_native(tree,manifest,destination,gate=None):
    gate=gate or Resources();a=gate(True);allocated=sum(((x['size']+4095)//4096)*4096 for x in manifest['members'])+8*MIB
    need(a['SSD_available_bytes']>=a['SSD_required_bytes']+allocated,'RESOURCE_HOLD_EXTRA_NATIVE_RESTORE_DISK')
    out=_qualified_restore(tree,manifest,destination,gate)
    dest=P(destination);directories=[];symlinks=[]
    for link in manifest.get('source_unselected_symlink_references',[]):
        p=safe(dest,link['path']);row=link['identity'];need(not os.path.lexists(p),'RESTORE_SYMLINK_PATH_ALREADY_EXISTS');os.symlink(link['target'],p);os.lchown(p,row['uid'],row['gid']);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']),follow_symlinks=False);now=identity(p)
        need(os.readlink(p)==link['target'] and all(now[k]==row[k] for k in ['uid','gid','mode','mtime_ns']),'RESTORED_SYMLINK_METADATA_MISMATCH');symlinks.append(dict(relative_path=link['path'],target=link['target'],identity=now))
    for rel,row in sorted(manifest.get('directory_metadata',{'.':manifest['source_root_identity']}).items(),key=lambda x:(-len(P(x[0]).parts),x[0])):
        p=dest if rel=='.' else safe(dest,rel);p.mkdir(parents=True,exist_ok=True);os.chown(p,row['uid'],row['gid']);p.chmod(row['mode']);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']));current=identity(p)
        need(all(current[k]==row[k] for k in ['uid','gid','mode','mtime_ns']),'RESTORED_DIRECTORY_METADATA_MISMATCH');directories.append(dict(relative_path=rel,identity=current))
    out['directories']=directories;out['symlinks']=symlinks;out['all_selected_directory_metadata_verified']=True
    return out

def extension_main():
    if sys.argv[1]=='source-local':source_send(read('/dev/stdin'))
    elif sys.argv[1]=='prepare-local':prepare_source(read('/dev/stdin'))
    elif sys.argv[1]=='migrate':emit(migrate(read(sys.argv[2])))
    elif sys.argv[1]=='verify':emit(verify_committed(P(sys.argv[2]),rehash='--full' in sys.argv[3:]))
    elif sys.argv[1]=='restore':
        bundle=P(sys.argv[2]);m=read(bundle/'SOURCE_MANIFEST.json');verify_committed(bundle);emit(restore_native(bundle/'tree',m,P(sys.argv[3])))
    else:raise RuntimeError('finite qualified copy operation required')

if __name__=='__main__':
    try:extension_main()
    except (RuntimeError,OSError,ValueError,KeyError) as error:print(json.dumps(dict(status='HOLD_EXACT_ASSET_NO_SCIENTIFIC_ACTION',reason=str(error))),file=sys.stderr);sys.exit(2)
