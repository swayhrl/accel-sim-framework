"""One finite existing-lock Source->Target binary stream; no Windows temp payload."""
import base64,gzip,hashlib,json,pathlib,shlex,subprocess,sys,threading,time

D=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent));import tls_target as t
tag=sys.argv[1];assert tag in ['463600cb','46bf3a69']
handoff=json.loads((D/'SOURCE_HANDOFF.json').read_bytes())
b=next(x for x in handoff['batches'] if x['batch']=='V3_'+tag)
config=dict(tag=b['batch'],source_root=b['source_root'],manifest_sha256=b['manifest_sha256'],
            target_root=b['target_native164_root_PROPOSED_NOT_RESERVED'].replace('/home/shared','/root/share/mnt164',1),
            files=b['counts']['regular'],directories=b['counts']['directory'],
            entries=sum(b['counts'].values()),logical_bytes=b['logical_regular_bytes'],
            zstd=json.loads((D/'ZSTD_TOOL.json').read_bytes())['path'])
metadata=(D/('V3_'+tag+'_METADATA.jsonl.gz')).read_bytes()
assert hashlib.sha256(metadata).hexdigest()==b['manifest_sha256']
assert hashlib.sha256(gzip.decompress(metadata)).hexdigest()==b['metadata_stream_sha256']
rows=[json.loads(x) for x in gzip.decompress(metadata).splitlines()]
config['sample_paths']=[x[0] for x in rows if x[1]=='regular' and x[8]<=65536 and
                        any(y in x[0] for y in ['8h_status_summary.md','stop_report.md','continuous_runner_status.md'])][:4]
assert b['source_identity_challenge']['frozen_metadata_row'][0] in config['sample_paths']
(D/(tag+'_CONFIG.json')).write_bytes((json.dumps(config,indent=2)+'\n').encode())
manifest64=base64.b64encode(metadata).decode()
prepare=r'''
import pathlib,os,json,hashlib,base64,fcntl,subprocess
C=__CONFIG__;B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');root=pathlib.Path(C['target_root'])
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(root.parent.parent.parent),'-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
assert (mount['target'],mount['source'],mount['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs')
locks=[]
try:
 for name in ['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock']:
  f=os.open(B/name,os.O_RDONLY|os.O_NOFOLLOW);locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not [p for p in B.glob('*/files') if any(q.is_file() for q in p.rglob('*'))]
 assert not root.exists(),'Existing cold root must be independently reconciled, never rebuilt'
 root.parent.mkdir(parents=True,mode=0o700,exist_ok=True);root.mkdir(mode=0o700)
 assert root.stat().st_dev==39
 raw=base64.b64decode(__MANIFEST__);assert hashlib.sha256(raw).hexdigest()==C['manifest_sha256']
 for name,data in [('SOURCE_MANIFEST.jsonl.gz',raw),('SOURCE_BINDING.json',(json.dumps(__BINDING__,indent=2)+'\n').encode())]:
  with (root/name).open('xb') as out:out.write(data);out.flush();os.fsync(out.fileno())
 print(json.dumps({'status':'ABSENT_TRUE164_ROOT_RESERVED','root':str(root),'manifest_sha256':hashlib.sha256((root/'SOURCE_MANIFEST.jsonl.gz').read_bytes()).hexdigest(),'mount':mount}))
finally:
 for f in locks:os.close(f)
'''
binding=dict(b,source_handoff_commit='ed5c1c48e73c70927dfc3c909e3a096a90913b07',source_originals='SOURCE_KEEP',target_source_deletion_authority=False)
for k,v in [('__CONFIG__',config),('__MANIFEST__',manifest64),('__BINDING__',binding)]:prepare=prepare.replace(k,repr(v))
t.remote(prepare,'COLD_'+tag+'_TARGET_ROOT_RESERVED',timeout=60,save_receipt=False)

def ssh_command(host,script,args):
    command='python3 -B -c '+shlex.quote('import base64;exec(compile(base64.b64decode('+repr(base64.b64encode(script).decode())+'),"<cold_stream>","exec"))')
    command+=' '+ ' '.join(shlex.quote(x) for x in args)
    return ['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',host,'timeout -k 10s 5400s '+command]

target=subprocess.Popen(ssh_command('hrl-174-new',(D/'cold_receive.py').read_bytes(),[json.dumps(config,separators=(',',':'))]),
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
first=target.stderr.readline();assert first.startswith(b'COLD_TARGET_READY '),first.decode(errors='replace')
print(first.decode().strip(),flush=True)
target_stderr=[]
def drain(stream,out,store=None):
    with out.open('wb') as f:
        for line in iter(stream.readline,b''):
            f.write(line);f.flush()
            if store is not None:store.append(line)
tt=threading.Thread(target=drain,args=(target.stderr,D/(tag+'_TARGET_STDERR.log'),target_stderr));tt.start()
source=subprocess.Popen(ssh_command('hrl',(D/'cold_stream_source.py').read_bytes(),[tag]),
                        stdin=subprocess.PIPE,stdout=target.stdin,stderr=subprocess.PIPE)
source_lines=[];st=threading.Thread(target=drain,args=(source.stderr,D/(tag+'_SOURCE_STDERR.log'),source_lines));st.start()
target.stdin.close()
source.stdin.write(metadata);source.stdin.close()
print('READONLY_SOURCE_STREAM_STARTED '+tag+'; payload has no local or overlay temporary file',flush=True)
while source.poll() is None:
    time.sleep(5)
    if target.poll() is not None and target.returncode!=0:
        source.terminate();break
src=source.wait();st.join()
out=target.stdout.read();trc=target.wait();tt.join()
(D/(tag+'_TARGET_STDOUT.json')).write_bytes(out)
assert src==trc==0, 'Source/Target failed: preserve partial. '+str((src,trc))+' '+(b''.join(source_lines)+b''.join(target_stderr))[-2200:].decode(errors='replace')
done=[json.loads(x[len(b'COLD_SOURCE_DONE '):]) for x in source_lines if x.startswith(b'COLD_SOURCE_DONE ')]
assert len(done)==1;source_result=done[0];target_result=json.loads(out)
for k in ['archive_sha256','compressed_bytes']:
    target_key='archive_bytes' if k=='compressed_bytes' else k
    assert source_result[k]==target_result[target_key],k
for k in ['tar_stream_sha256','tar_stream_bytes']:assert source_result[k]==target_result[k]
assert source_result['frozen_metadata_before_after_exact'] is True
assert source_result['frozen_metadata_entries']==config['entries']
challenge=b['source_identity_challenge']
sample=next(x for x in target_result['samples'] if x['relative_path']==challenge['frozen_metadata_row'][0])
assert sample['sha256']==challenge['sha256']
result=dict(source=source_result,target=target_result,config=config,source_handoff_commit='ed5c1c48e73c70927dfc3c909e3a096a90913b07',
            source_and_target_archive_and_decoded_tar_SHA_equal=True,source_originals='SOURCE_KEEP',source_actual_released_bytes=0)
(D/(tag+'_CROSS_VERIFIED.json')).write_bytes((json.dumps(result,indent=2)+'\n').encode())
print('BATCH_CROSS_VERIFIED '+json.dumps({'tag':tag,'archive_bytes':target_result['archive_bytes'],'sha256':target_result['archive_sha256'],'files':config['files'],'directories':config['directories']}),flush=True)
