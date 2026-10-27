"""One exact engineering-negative evidence transaction. Default is read-only inventory.

Never writes DONE, NATIVE_EXIT, execution_receipt, scientific RESULT, or authority.
Only Main may invoke --execute after reviewing/qualifying the pinned source.
"""
import sys
sys.dont_write_bytecode=True
import os, pathlib, json, hashlib, stat, gzip, time, datetime, re, fcntl, importlib.util, subprocess, tarfile, uuid, argparse, copy
P=pathlib.Path;G=1024**3;M=1024**2
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
C='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';U='19105d9d-7522-498e-bf1d-73fbf7aba766'
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';OUT=R/'DTC/run/results'/U
BOOT='59e1e1a4-84b6-431f-ac2d-03e340207019';NS='mnt:[4026535153]'
RECEIVER=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock')
PROD=A/'engineering_negative_evidence_v1'/C
RESTORE=R/'analysis/engineering_negative_restore_v1'
PROC=P('/proc')
PREFIX='_ENGINEERING_CONTEXT'
SCHEMA='L2_MLP_ENGINEERING_NEGATIVE_COPY_MANIFEST_V1'
CERT='L2_MLP_ENGINEERING_TERMINAL_NEGATIVE_V1'
PIN_SELF=None
def need(v,msg):
    if not v:raise RuntimeError('HOLD: '+msg)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with P(p).open('rb')as f:
        for b in iter(lambda:f.read(M),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity():
    need(os.uname().nodename=='huangrulin-sshfs-174','host')
    need(P('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT,'boot')
    need(os.readlink('/proc/self/ns/mnt')==NS,'namespace')
    need(R.stat().st_dev==2128,'native2128')
    need(subprocess.check_output(['findmnt','-n','-T',str(R),'-o','FSTYPE'],text=True).strip()=='ext4','native ext4')
    mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(A)],text=True))['filesystems'][0]
    need(mount['fstype']=='fuse.sshfs'and mount['source']=='admin-wcx@10.208.130.164:/home/shared','true164')
    return dict(host=os.uname().nodename,boot_id=BOOT,mnt_namespace=NS,native_device=2128,true164=mount)
def no_symlink_parents(path):
    for p in [P(path),*P(path).parents]:need(not p.is_symlink(),'symlink path '+str(p))
def ident(s):return dict(dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,allocated=s.st_blocks*512,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
def inventory_tree(root,allow_perf=True):
    root=P(root);no_symlink_parents(root);rows=[];stack=[root]
    while stack:
        p=stack.pop();s=p.lstat();rel=p.relative_to(root).as_posix();r=dict(ident(s),path=rel)
        if stat.S_ISDIR(s.st_mode):
            r['type']='directory';stack.extend(sorted(p.iterdir(),reverse=True))
        elif stat.S_ISREG(s.st_mode):
            r['type']='file';r['sha256']=sha(p);need(ident(p.lstat())==ident(s),'source changed during hash '+rel)
        elif stat.S_ISLNK(s.st_mode):
            target=os.readlink(p);need(allow_perf and rel=='perf_counter.csv.gz' and '/'not in target and target.startswith('perf_counter_')and target.endswith('.csv.gz'),'unqualified symlink '+rel)
            dst=root/target;need(dst.is_file()and not dst.is_symlink(),'perf link target');r.update(type='symlink',target=target)
        else:need(False,'special source entry '+rel)
        need(rel!=PREFIX and not rel.startswith(PREFIX+'/'),'reserved context collision')
        rows.append(r)
    return sorted(rows,key=lambda r:r['path'])
def gzip_evidence(root):
    out={}
    required=['raw.log.gz','progress.jsonl.gz','RESOURCE_SAMPLES.jsonl.gz']
    names=required+sorted(p.relative_to(root).as_posix()for p in P(root).rglob('*.gz')if p.is_file()and p.relative_to(root).as_posix()not in required)
    for name in names:
        h=hashlib.sha256();n=0;lines=[]
        with gzip.open(P(root)/name,'rb')as f:
            for b in iter(lambda:f.read(M),b''):h.update(b);n+=len(b);lines.append(b)
        # Closing/read-to-EOF validates complete gzip member CRC/trailers.
        raw=b''.join(lines);item=dict(uncompressed_bytes=n,uncompressed_sha256=h.hexdigest(),gzip_crc_valid=True)
        if name in ['progress.jsonl.gz','RESOURCE_SAMPLES.jsonl.gz']:
            parsed=[json.loads(line)for line in raw.splitlines()];need(parsed,'empty JSONL '+name)
            item['records']=len(parsed)
            if name=='progress.jsonl.gz':
                need(all(x['generation']==U for x in parsed),'progress generation')
                need(all(x['seq']==i+1 for i,x in enumerate(parsed)),'progress sequence')
                need(not any(x.get('end')=='NATURAL'for x in parsed),'unexpected natural closure')
                item['last']=parsed[-1];item['natural_terminal_count']=0
        out[name]=item
    return out
def context():
    identity();e=load('engineering_negative_readonly_native',R/'tools/l2_native.py');reg,ep,q,plan=e.registered()
    need(C in q['consumed'],'unconsumed cohort');row=q['consumed'][C]
    need(row['uuid']==U and row['charged']==1 and 'execution_receipt'not in row,'exact spent/no receipt')
    ip=R/'control/qualification_ledger'/(C+'.INTENT.json');i=read(ip)
    need(sha(ip)==row['intent_sha256']and i['uuid']==U and i['cohort']==C and i['output']==str(OUT),'exact intent')
    need(not ip.with_name(C+'.DONE.json').exists()and not(OUT/'NATIVE_EXIT.json').exists(),'no native closure')
    need(not(R/'control'/(C+'_ARCHIVE_RECEIPT.json')).exists(),'no standard archive alias')
    need(not(R/'analysis'/(C+'.RESULT.json')).exists(),'no original accepted/normal result')
    s=e.canonical(C);need(s['input_digest']=='6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39'and s['cell']=='DH'and s['profile']=='M16','fixed scan/M16')
    logs=sorted((R/'logs').glob(C+'.run-native.*.json'));need(len(logs)==1,'exact frontend failure log')
    failure=read(logs[0]);need(failure['returncode']==2 and failure['stdout']=='','frontend returncode')
    err=json.loads(failure['stderr']);need(err==dict(status='HOLD',reason='Unterminated string starting at: line 20 column 11 (char 3203)',science_retry=False),'frontend exact JSON error')
    pid=read(OUT/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=read(OUT/'NATIVE_LAUNCH.json')
    need(pid['pid']==1775705 and pid['start_ticks']==985330216 and launch['launcher_pid']==1775700,'actual handles')
    need(launch['scientific_qualification_uuid']==U and launch['environment']['DTC_AG7_GENERATION']==U,'actual generation')
    need(pid['mnt_namespace']==NS and pid['l2_mlp_execution_binding']==launch['l2_mlp_execution_binding'],'native execution bindings')
    pins={}
    paths=[ip,R/'control/specs'/(C+'.json'),R/'control'/(C+'_SPEC.json'),R/'control/dispatch_bindings'/(C+'.json'),logs[0],R/'analysis'/(C+'.ENGINEERING_GUARD.json'),R/'control/EXECUTION_PLAN.json',R/'control/FREEZE_MANIFEST.json',R/'control/SCIENCE_AUTHORIZATION.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',P(__file__).resolve()]
    paths += [P(x['path'])for x in plan['source_pins']]
    paths += [P(x['path'])for x in s['configs']]+[P(x['actual_realpath'])for x in s['runtime_files']]
    for p in paths:
        # Runtime source links are permitted only when exact spec realpath pins bind them.
        need(p.is_file(),'missing source pin '+str(p));b=p.read_bytes();pins[str(p)]=dict(sha256=digest(b),bytes=len(b))
    for x in plan['source_pins']:need(pins[x['path']]['sha256']==x['sha256'],'plan source pin')
    for x in s['configs']:need(pins[x['path']]['sha256']==x['sha256'],'config pin')
    for x in s['runtime_files']:need(pins[x['actual_realpath']]['sha256']==x['sha256'],'runtime pin')
    return dict(native=e,plan=plan,spec=s,row=row,intent=i,pid=pid,launch=launch,pins=pins,frontend_log=logs[0],frontend=failure)
def pid_start(p):return int((p/'stat').read_text().rsplit(')',1)[1].split()[19])
def related_trace_pids():
    data=(OUT/'actual_file_process_network.log').read_text();ids={1775705,1775700}
    for line in data.splitlines():
        match=re.match(r'^(\d+)\s+',line)
        if match:ids.add(int(match.group(1)))
        m=re.search(r'\b(?:clone|clone3|fork|vfork)\(.*\)\s+=\s+(\d+)\s*$',line)
        if m:ids.add(int(m.group(1)))
    return sorted(ids)
def departure_scan(source_entries,known_pids):
    identity();selected={(r['dev'],r['inode'])for r in source_entries if r['type']=='file'};matches=[];writers=[];observed=0;vanished=[];known=[]
    for d in sorted(PROC.iterdir(),key=lambda x:x.name):
        if not d.name.isdigit():continue
        try:
            before=pid_start(d);env=(d/'environ').read_bytes();observed+=1
            if b'DTC_AG7_GENERATION='+U.encode()in env.split(b'\0'):matches.append(dict(pid=int(d.name),start_ticks=before))
            if int(d.name)in known_pids:known.append(dict(pid=int(d.name),start_ticks=before))
            for fd in (d/'fd').iterdir():
                try:
                    st=fd.stat()
                    if (st.st_dev,st.st_ino)in selected:
                        info=(d/'fdinfo'/fd.name).read_text();flag=int(next(x.split()[1]for x in info.splitlines()if x.startswith('flags:')),8)
                        if (flag & os.O_ACCMODE)in [os.O_WRONLY,os.O_RDWR]:writers.append(dict(pid=int(d.name),start_ticks=before,fd=int(fd.name),flags=flag))
                except (FileNotFoundError,ProcessLookupError):continue
            need(pid_start(d)==before,'PID reused during process scan '+d.name)
        except (FileNotFoundError,ProcessLookupError):vanished.append(int(d.name))
        # Any permission, malformed proc, unknown environment/FD error propagates HOLD.
    need(not matches,'generation still live');need(not writers,'original source has writer FDs')
    need(not known,'known related PID present; no guessed reuse exclusion')
    return dict(utc=utc(),monotonic_ns=time.monotonic_ns(),boot_id=BOOT,mnt_namespace=NS,observed_processes=observed,transient_vanished_pids=vanished,known_related_pids=known_pids,known_related_pids_present=known,exact_generation_pids=matches,source_writer_fds=writers,proc_scan_complete=True,permission_or_other_holes=0)
def departures(entries):
    known=related_trace_pids();a=departure_scan(entries,known);time.sleep(1.05);b=departure_scan(entries,known)
    need(b['monotonic_ns']-a['monotonic_ns']>=10**9,'departure observation interval');return [a,b]
def atomic_immutable(path,b):
    path=P(path);no_symlink_parents(path.parent);need(not path.is_symlink(),'immutable destination symlink')
    if path.exists():need(path.is_file()and path.read_bytes()==b,'immutable collision '+str(path));return
    tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.writing')
    with tmp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
    try:
        os.link(tmp,path)
    except FileExistsError:need(path.is_file()and path.read_bytes()==b,'raced immutable mismatch')
    finally:tmp.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def immutable_json(path,v):atomic_immutable(path,canon(v))
def libraries():
    p=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_outbox.py');b=load('engineering_negative_original_lowlevel_outbox',p)
    need(sha(p)==read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['outbox_sha256'],'outbox library pin')
    b.ROOT=R;f,v=b.libraries();return b,f,v
def source_check(m,ctx):
    identity();need(inventory_tree(OUT)==m['original_entries'],'original source drift')
    fresh=context();need(fresh['pins']==ctx['pins'],'source pins drift')
    return True
def resource_gate(ctx,raw_bytes,restore_allocated=0):
    identity();n=ctx['native'];res=n.resources({'request':REQ,'cohort':C},False)
    need(res['physical_RAM_pass']and res['physical_disk_pass'],'native current resource gate')
    need(raw_bytes+16*M<=2*ctx['spec']['limits']['max_result_directory_bytes']-sum(r['size']for r in inventory_tree(OUT)if r['type']=='file'),'existing failed-generation restore reservation insufficient')
    need(res['native_free_bytes']>res['required_free_bytes']+16*M,'all peer writes plus metadata floor')
    cg=P('/sys/fs/cgroup');maximum=(cg/'memory.max').read_text().strip();cur=int((cg/'memory.current').read_text())
    need(maximum=='max'or int(maximum)-cur>=512*M,'archive buffer raw cgroup headroom')
    need(os.statvfs(A).f_bavail*os.statvfs(A).f_frsize>raw_bytes+16*M,'164 full archive capacity')
    return dict(required_free_bytes=res['required_free_bytes'],native_free_bytes=res['native_free_bytes'],new_native_restore_bound=raw_bytes+16*M,already_inside_failed_generation_write_reservation=True,source_disposition='SOURCE_KEEP')
def context_payloads(ctx):
    raw={}
    for name,p in [('INTENT.json',P(ctx['row']['intent'])),('CANONICAL_SPEC.json',R/'control/specs'/(C+'.json')),('DISPATCH_BINDING.json',R/'control/dispatch_bindings'/(C+'.json')),('FRONTEND_FAILURE.json',ctx['frontend_log']),('ENGINEERING_GUARD.json',R/'analysis'/(C+'.ENGINEERING_GUARD.json')),('IMPLEMENTATION.py',P(__file__).resolve())]:raw[name]=p.read_bytes()
    raw['PINNED_SOURCES.json']=canon(ctx['pins']);return raw
def scientific_identity(ctx):
    s=ctx['spec'];binary=P(s['native_simulator_argv'][0]).resolve()
    return dict(input_digest=s['input_digest'],trace_entry=s['native_simulator_argv'][2],core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_realpath=str(binary),binary_sha256=sha(binary),configs=s['configs'],expected_options_sha256=digest(canon(s['expected_options'])),cell='DH',target_profile='M16')
def build_manifest(ctx,entries,context_dir,tx):
    extra=inventory_tree(context_dir,allow_perf=False)
    projected=[]
    for row in extra:
        row=dict(row,path=PREFIX if row['path']=='.'else PREFIX+'/'+row['path']);projected.append(row)
    union=sorted(entries+projected,key=lambda x:x['path'])
    return dict(schema=SCHEMA,cohort=C,request=REQ,uuid=U,txid=tx,source_root=str(OUT),context_source_root=str(context_dir),original_entries=entries,entries=union,reused_objects={},source_disposition='SOURCE_KEEP',scientific_status='ENGINEERING_NEGATIVE_UNACCEPTED',original_native_execution_receipt_present=False,selector_sha256=digest(canon(union)),original_selector_sha256=digest(canon(entries)),pins=ctx['pins'],scientific_identity=scientific_identity(ctx),source_identity=dict(host='huangrulin-sshfs-174',boot_id=BOOT,mnt_namespace=NS,native_device=2128))
def archive_stream(b,f,v,bundle,m,ctx):
    raw=sum(r['size']for r in m['entries']if r['type']=='file');b.gate=lambda *a,**k:resource_gate(ctx,raw)
    need(m['schema']==SCHEMA,'distinct engineering manifest')
    if (bundle/'COMMIT.json').exists():return f.verify_archive(bundle,m)
    w=b.RangeWriter(bundle,m,v,f)
    with tarfile.open(fileobj=w,mode='w|',format=tarfile.PAX_FORMAT)as tar:
        for r in m['entries']:
            rel=r['path'];root=OUT
            if rel==PREFIX or rel.startswith(PREFIX+'/'):root=P(m['context_source_root']);rel='.'if rel==PREFIX else rel[len(PREFIX)+1:]
            p=f.safe(root,rel);t=tarfile.TarInfo(r['path']);t.uid=r['uid'];t.gid=r['gid'];t.uname=t.gname='';t.mode=r['mode'];t.mtime=r['mtime_ns']//10**9;t.pax_headers={'mtime':str(r['mtime_ns']//10**9)+'.'+str(r['mtime_ns']%10**9).zfill(9)}
            if r['type']=='directory':t.type=tarfile.DIRTYPE;tar.addfile(t)
            elif r['type']=='symlink':t.type=tarfile.SYMTYPE;t.linkname=r['target'];tar.addfile(t)
            else:
                need(sha(p)==r['sha256'],'prearchive file SHA');t.size=r['size']
                with p.open('rb')as stream:tar.addfile(t,stream)
    index=w.finish();source_check(m,ctx)
    immutable_json(bundle/'ARCHIVE_INDEX.json',index)
    immutable_json(bundle/'COMMIT.json',dict(txid=m['txid'],manifest_sha256=digest(canon(m)),archive_index_sha256=digest(canon(index)),policy='EXCLUSIVE_CREATE_COMMIT_MARKER_LAST'))
    return f.verify_archive(bundle,m)
def validate_certificate(c,m,index,archive_receipt,departure):
    need(c['schema']==CERT and c['state']=='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY','typed negative')
    need(c['cohort']==C and c['request']==REQ and c['uuid']==U,'certificate identity')
    need(c['accepted_cycles']is None and c['launcher_wait_returncode']is None and c['performance_accepted']is False and c['scientific_acceptance']is False,'no invented scientific/wait values')
    need(c['actual_signal_delivery']=='NOT_DIRECTLY_OBSERVED' and c['observed_frontend_returncode']==2,'separate frontend facts')
    need(c['original_done_present']is False and c['original_exit_present']is False and c['original_registry_execution_receipt_present']is False,'explicit missing closure')
    need(c['scientific_identity']==m['scientific_identity']and c['source_identity']==m['source_identity'],'scientific/source identity binding')
    need(c['original_spent_starts']==1 and c['refunded_starts']==0 and c['automatic_retry']is False and c['source_disposition']=='SOURCE_KEEP','spent/source invariants')
    need(c['manifest_sha256']==digest(canon(m))and c['archive_sha256']==index['archive_sha256']and c['archive_receipt_sha256']==digest(canon(archive_receipt))and c['departure_proof_sha256']==digest(canon(departure)),'certificate evidence bindings')
    need(archive_receipt['schema']=='ENGINEERING_NEGATIVE_EVIDENCE_COPY_RECEIPT_V1'and archive_receipt['scientific_acceptance']is False,'archive distinct type')
    need(len(departure)==2 and departure[-1]['monotonic_ns']-departure[0]['monotonic_ns']>=10**9,'departure interval')
    for s in departure:need(s['boot_id']==BOOT and s['mnt_namespace']==NS and s['proc_scan_complete']is True and s['permission_or_other_holes']==0 and not s['exact_generation_pids']and not s['known_related_pids_present']and not s['source_writer_fds'],'complete departure proof')
def run_execute(expected_self_sha,new_restore_attempt=False):
    need(expected_self_sha and sha(__file__)==expected_self_sha,'Main must supply reviewed self SHA')
    ctx=context();entries=inventory_tree(OUT);gz=gzip_evidence(OUT);proof=departures(entries)
    tx=digest(canon(dict(cohort=C,uuid=U,original_selector_sha256=digest(canon(entries)),pins=ctx['pins'])))
    no_symlink_parents(PROD.parent);PROD.parent.mkdir(parents=True,exist_ok=True)
    with RECEIVER.open('rb')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        PROD.mkdir(exist_ok=True);bundle=PROD/tx;bundle.mkdir(exist_ok=True);(bundle/'chunks').mkdir(exist_ok=True);context_dir=bundle/'context';context_dir.mkdir(exist_ok=True)
        for name,data in context_payloads(ctx).items():atomic_immutable(context_dir/name,data)
        need(set(p.name for p in context_dir.iterdir())==set(context_payloads(ctx)),'unexpected context entry')
        m=build_manifest(ctx,entries,context_dir,tx);immutable_json(bundle/'SOURCE_MANIFEST.json',m);immutable_json(bundle/'GZIP_CRC_PROOF.json',gz)
        if (bundle/'DEPARTURE_PROOF.json').exists():initial=read(bundle/'DEPARTURE_PROOF.json')
        else:immutable_json(bundle/'DEPARTURE_PROOF.json',proof);initial=proof
        b,f,v=libraries();raw=sum(r['size']for r in m['entries']if r['type']=='file');resource_gate(ctx,raw);source_check(m,ctx);index=archive_stream(b,f,v,bundle,m,ctx)
        # Preserve all interrupted restore attempts. Never overwrite or recursively delete.
        no_symlink_parents(RESTORE.parent);RESTORE.mkdir(exist_ok=True);attempt_record=bundle/'NATIVE_RESTORE_ATTEMPT.json'
        if attempt_record.exists():
            ar=read(attempt_record);dst=P(ar['destination']);need(dst.parent==RESTORE and ar['txid']==tx,'restore attempt ownership')
            try:nativeproof=f.check_native(dst,m)
            except Exception:
                recovered=False
                for record in sorted(bundle.glob('RESTORE_RECOVERY_*.json')):
                    rec=read(record);candidate=P(rec['destination']);need(rec['txid']==tx and candidate.parent==RESTORE,'recovery attempt ownership')
                    try:nativeproof=f.check_native(candidate,m);dst=candidate;recovered=True;break
                    except (RuntimeError,FileNotFoundError):continue
                if not recovered:
                    need(new_restore_attempt,'interrupted native restore retained; Main may explicitly --new-restore-attempt')
                    dst=RESTORE/(tx+'.recovery.'+uuid.uuid4().hex);immutable_json(bundle/('RESTORE_RECOVERY_'+dst.name+'.json'),dict(txid=tx,destination=str(dst),previous_destination=ar['destination']))
                    resource_gate(ctx,raw);nativeproof=f.restore(bundle,m,dst,v,gate=lambda:resource_gate(ctx,raw))
        else:
            dst=RESTORE/(tx+'.initial');immutable_json(attempt_record,dict(txid=tx,destination=str(dst)))
            resource_gate(ctx,raw);nativeproof=f.restore(bundle,m,dst,v,gate=lambda:resource_gate(ctx,raw))
        need(dst.stat().st_dev==2128,'restore actual device');nativeproof=f.check_native(dst,m);need(gzip_evidence(dst)==gz,'restored gzip CRC/JSON provenance')
        source_check(m,ctx);fresh=departures(entries)
        native_record=dict(schema='ENGINEERING_NEGATIVE_NATIVE_RESTORE_V1',txid=tx,destination=str(dst),native_device=2128,proof=nativeproof)
        nr=bundle/('RESTORE_VERIFIED_'+digest(canon(native_record))+'.json');immutable_json(nr,native_record)
        # A pre-existing final receipt/certificate must verify against its original restore,
        # never be rewritten with a later observation or recovery attempt.
        rp=bundle/'ENGINEERING_ARCHIVE_RECEIPT.json';cp=bundle/'ENGINEERING_TERMINAL_NEGATIVE.json'
        if rp.exists():
            receipt=read(rp);old=read(P(receipt['native_restore_proof_path']));need(old['txid']==tx,'old restore proof tx');f.check_native(P(old['destination']),m)
        else:
            receipt=dict(schema='ENGINEERING_NEGATIVE_EVIDENCE_COPY_RECEIPT_V1',cohort=C,uuid=U,txid=tx,true164_root=str(bundle),true164_source='admin-wcx@10.208.130.164:/home/shared',native_restore=str(dst),native_device=2128,native_restore_proof_path=str(nr),native_restore_proof_sha256=sha(nr),all_entries_sha_verified=True,archive_sha256=index['archive_sha256'],manifest_sha256=digest(canon(m)),source_disposition='SOURCE_KEEP',source_released_bytes=0,scientific_acceptance=False)
            immutable_json(rp,receipt)
        certificate=dict(schema=CERT,state='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY',request=REQ,cohort=C,uuid=U,intent_sha256=ctx['row']['intent_sha256'],canonical_spec_sha256=ctx['pins'][str(R/'control/specs'/(C+'.json'))]['sha256'],observed_frontend_returncode=2,launcher_wait_returncode=None,actual_signal_delivery='NOT_DIRECTLY_OBSERVED',observed_failure='SUPERVISOR_JSON_PARSE_EXCEPTION',accepted_cycles=None,performance_accepted=False,scientific_acceptance=False,original_spent_starts=1,refunded_starts=0,automatic_retry=False,source_disposition='SOURCE_KEEP',manifest_sha256=digest(canon(m)),archive_sha256=index['archive_sha256'],archive_receipt_sha256=digest(canon(receipt)),departure_proof_sha256=digest(canon(initial)),original_native_execution_receipt_created=False,original_done_present=False,original_exit_present=False,original_registry_execution_receipt_present=False,scientific_identity=m['scientific_identity'],source_identity=m['source_identity'],source_pins_sha256=digest(canon(ctx['pins'])))
        validate_certificate(certificate,m,index,receipt,initial);immutable_json(cp,certificate)
        return verify_bundle(bundle,expected_self_sha,already_locked=True)
def verify_bundle(bundle,expected_self_sha,already_locked=False):
    need(expected_self_sha and sha(__file__)==expected_self_sha,'reviewed self SHA');ctx=context();bundle=P(bundle);no_symlink_parents(bundle)
    need(bundle.parent==PROD,'exact engineering archive scope');m=read(bundle/'SOURCE_MANIFEST.json');need(m['schema']==SCHEMA and m['cohort']==C and m['uuid']==U and m['request']==REQ,'manifest identity')
    need(m['pins']==ctx['pins']and m['txid']==bundle.name,'manifest pins/tx')
    expected_tx=digest(canon(dict(cohort=C,uuid=U,original_selector_sha256=digest(canon(m['original_entries'])),pins=ctx['pins'])))
    need(m['txid']==expected_tx,'deterministic exact transaction identity')
    need(m==build_manifest(ctx,m['original_entries'],bundle/'context',m['txid']),'full original plus context manifest closure')
    need(m['selector_sha256']==digest(canon(m['entries']))and m['original_selector_sha256']==digest(canon(m['original_entries'])),'selectors')
    source_check(m,ctx);need(gzip_evidence(OUT)==read(bundle/'GZIP_CRC_PROOF.json'),'original CRC proof')
    b,f,v=libraries();index=f.verify_archive(bundle,m);receipt=read(bundle/'ENGINEERING_ARCHIVE_RECEIPT.json');cert=read(bundle/'ENGINEERING_TERMINAL_NEGATIVE.json');initial=read(bundle/'DEPARTURE_PROOF.json')
    validate_certificate(cert,m,index,receipt,initial)
    need(cert['intent_sha256']==ctx['row']['intent_sha256']and cert['canonical_spec_sha256']==ctx['pins'][str(R/'control/specs'/(C+'.json'))]['sha256']and cert['source_pins_sha256']==digest(canon(ctx['pins']))and cert['original_native_execution_receipt_created']is False,'certificate current exact source pins')
    for path in [bundle/'SOURCE_MANIFEST.json',bundle/'ARCHIVE_INDEX.json',bundle/'COMMIT.json',bundle/'ENGINEERING_ARCHIVE_RECEIPT.json',bundle/'ENGINEERING_TERMINAL_NEGATIVE.json',bundle/'DEPARTURE_PROOF.json',bundle/'GZIP_CRC_PROOF.json']:
        need(stat.S_ISREG(path.lstat().st_mode),'nonregular archive control evidence')
    need(receipt['true164_root']==str(bundle)and receipt['true164_source']=='admin-wcx@10.208.130.164:/home/shared'and receipt['native_device']==2128 and receipt['all_entries_sha_verified']is True,'archive location claims')
    nr=P(receipt['native_restore_proof_path']);need(nr.parent==bundle and stat.S_ISREG(nr.lstat().st_mode)and sha(nr)==receipt['native_restore_proof_sha256'],'native proof file binding')
    nd=read(nr);dst=P(receipt['native_restore']);no_symlink_parents(dst);need(dst.parent==RESTORE and nd['destination']==str(dst)and nd['txid']==m['txid']and dst.stat().st_dev==2128,'exact native restore identity')
    actual=f.check_native(dst,m);need(actual==nd['proof'],'native numeric identity proof');need(gzip_evidence(dst)==read(bundle/'GZIP_CRC_PROOF.json'),'native restored gzip CRC')
    fresh=departures(m['original_entries']);source_check(m,ctx)
    return dict(status='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED',cohort=C,uuid=U,certificate=str(bundle/'ENGINEERING_TERMINAL_NEGATIVE.json'),certificate_sha256=sha(bundle/'ENGINEERING_TERMINAL_NEGATIVE.json'),archive_manifest_sha256=sha(bundle/'SOURCE_MANIFEST.json'),actual_archive_sha256=index['archive_sha256'],native_restore=str(dst),native_restore_entries=len(actual),verified_future_model_growth_bytes=0,accepted_cycles=None,performance_accepted=False,fresh_departure_proof=fresh,original_spent_starts=1,refunds=0,DONE_or_EXIT_or_registry_writes=0,source_disposition='SOURCE_KEEP',original_native_execution_receipt_present=False)
def dry_inventory():
    ctx=context();entries=inventory_tree(OUT);gz=gzip_evidence(OUT);d=departures(entries);b,f,v=libraries()
    return dict(schema='ENGINEERING_NEGATIVE_READONLY_INVENTORY_V1',utc=utc(),cohort=C,uuid=U,source_root=str(OUT),source_entries=entries,source_selector_sha256=digest(canon(entries)),pins=ctx['pins'],gzip_crc=gz,departure=d,lowlevel_bundle_sha256=sha(f.__file__),resource_gate=resource_gate(ctx,sum(r['size']for r in entries if r['type']=='file')),production_ready=False,models_started=0,signals=0,authority_writes=0,archive_or_certificate_writes=0)
def verify_certificate(certificate_path,expected_self_sha):
    p=P(certificate_path);need(p.name=='ENGINEERING_TERMINAL_NEGATIVE.json','exact typed certificate basename')
    return verify_bundle(p.parent,expected_self_sha)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inventory',action='store_true');parser.add_argument('--execute',action='store_true');parser.add_argument('--verify-bundle');parser.add_argument('--expected-self-sha');parser.add_argument('--new-restore-attempt',action='store_true');a=parser.parse_args()
    need(sum([bool(a.inventory),bool(a.execute),bool(a.verify_bundle)])<=1,'one mode')
    if a.execute:v=run_execute(a.expected_self_sha,a.new_restore_attempt)
    elif a.verify_bundle:v=verify_bundle(a.verify_bundle,a.expected_self_sha)
    else:v=dry_inventory()
    print(json.dumps(v,indent=2,sort_keys=True))
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),automatic_retry=False,models_started=0,authority_writes=0)),file=sys.stderr);sys.exit(2)
