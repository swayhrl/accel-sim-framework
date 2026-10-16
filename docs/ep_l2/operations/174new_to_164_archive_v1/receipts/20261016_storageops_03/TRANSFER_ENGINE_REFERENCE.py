import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

META=Path(__file__).resolve().parent
ROOT='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02'
STAGE='/root/share/container-workspaces/hrl-174-new/staging/storage-ops-20261016_storageops_02'
PROBE='/root/share/container-workspaces/hrl-174-new/staging/.storage-ops-20261016_storageops_02.probe'
LOG=META/'storage_ops_runtime_log.jsonl'

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def remote(host,code,label,timeout=50):
    start=now()
    p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',host,
        'timeout -k 5s '+str(timeout)+'s python3 -'],input=textwrap.dedent(code),text=True,
        encoding='utf-8',capture_output=True,timeout=timeout+15)
    record={'label':label,'host':host,'started_at':start,'finished_at':now(),
            'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'python_source':textwrap.dedent(code)}
    with LOG.open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
    if p.returncode:raise RuntimeError(label+': '+p.stderr[:1500])
    data=json.loads(p.stdout)
    (META/(label+'.json')).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(label+': '+json.dumps(data)[:2500],flush=True)
    return data

def probes():
    remote('hrl-174-new',f'''
        import os,json,hashlib,subprocess,datetime,stat
        root={ROOT!r}
        parent='/root/share/mnt164/huangrulin/host174_storage_recovery'
        m=json.loads(subprocess.check_output(['findmnt','-J','-T',parent,'-o','TARGET,SOURCE,FSTYPE'],text=True))['filesystems'][0]
        assert m['target']=='/root/share/mnt164' and m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs',m
        for p in ['/root/share/mnt164','/root/share/mnt164/huangrulin',parent]:
            assert stat.S_ISDIR(os.lstat(p).st_mode) and not os.path.islink(p),p
        ancestor=parent+'/174new_archive'
        if not os.path.lexists(ancestor):os.mkdir(ancestor,0o700)
        assert os.path.isdir(ancestor) and not os.path.islink(ancestor)
        assert not os.path.lexists(root),'Authorized root already exists; require ownership review before writing'
        os.mkdir(root,0o700)
        payload=b'ops-v3\\n';p=root+'/.write_probe'
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        st=os.lstat(p)
        with open(p,'rb') as f:readback=f.read()
        assert readback==payload and hashlib.sha256(readback).hexdigest()==hashlib.sha256(payload).hexdigest()
        assert (os.lstat(p).st_dev,os.lstat(p).st_ino)==(st.st_dev,st.st_ino)
        os.unlink(p)
        assert not os.path.lexists(p)
        receipt={{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':root,'mount':m,'probe_bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'fsync':'PASS','closed_reopened_readback':'MATCH','probe_deleted':True,'probe_residuals':0,'level':'SSHFS_ARCHIVE_WRITE_VERIFIED','server_side_native_verified':False}}
        with open(root+'/AUTHORIZATION_AND_PROBE.json','x') as f:json.dump(receipt,f,indent=2);f.flush();os.fsync(f.fileno())
        print(json.dumps(receipt))
    ''','v3_target_write_probe')
    first=remote('hrl-174-new',f'''
        import os,json,hashlib
        p={PROBE!r};data=b'ops-new\\n'
        assert os.stat('/root/share').st_dev==2431
        assert not os.path.lexists(p)
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        s=os.lstat(p)
        print(json.dumps({{'path':p,'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'sha256':hashlib.sha256(data).hexdigest()}}))
    ''','v3_shared_probe_new_write')
    second=remote('hrl',f'''
        import os,json,hashlib,subprocess
        assert subprocess.check_output(['hostname'],text=True).strip()=='huangrulin-174'
        assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
        assert (os.stat('/workspace').st_dev,os.stat('/workspace').st_ino)==(156,32926662)
        p={PROBE!r};s=os.lstat(p)
        assert (s.st_dev,s.st_ino)==({first['dev']},{first['inode']})
        with open(p,'rb') as f:raw=f.read()
        assert hashlib.sha256(raw).hexdigest()=={first['sha256']!r}
        data=b'ops-old\\n'
        fd=os.open(p,os.O_WRONLY|os.O_TRUNC|os.O_NOFOLLOW)
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        print(json.dumps({{'path':p,'dev':s.st_dev,'inode':s.st_ino,'new_to_old_hash':'MATCH','old_written_sha256':hashlib.sha256(data).hexdigest(),'source_workspace_free_bytes':os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize}}))
    ''','v3_shared_probe_old_read_write')
    remote('hrl-174-new',f'''
        import os,json,hashlib,stat
        p={PROBE!r};s=os.lstat(p)
        assert (s.st_dev,s.st_ino)==({first['dev']},{first['inode']})
        with open(p,'rb') as f:raw=f.read()
        assert hashlib.sha256(raw).hexdigest()=={second['old_written_sha256']!r}
        os.unlink(p);assert not os.path.lexists(p)
        stage={STAGE!r};assert not os.path.lexists(stage)
        os.mkdir(stage,0o700)
        with open(stage+'/OWNER.json','x') as f:json.dump({{'task':'Storage-Ops','run':'20261016_storageops_03','approved_archive_root':{ROOT!r}}},f)
        print(json.dumps({{'old_to_new_hash':'MATCH','shared_probe_deleted':True,'residual_probe_files':0,'stage_root':stage,'stage_dev':os.stat(stage).st_dev,'stage_inode':os.stat(stage).st_ino}}))
    ''','v3_shared_probe_final')
    remote('hrl',f'''
        import os,json
        assert not os.path.lexists({PROBE!r})
        s=os.stat({STAGE!r})
        print(json.dumps({{'shared_probe_absent_from_old':True,'stage_visible_from_old':True,'stage_dev':s.st_dev,'stage_inode':s.st_ino}}))
    ''','v3_shared_stage_verified')

def prepare():
    previous=json.loads((META/'sshfs_v2_source_candidates.json').read_text())
    paths=[x['path'] for x in previous['tmp_packs']]
    remote('hrl',f'''
        import os,json,subprocess,datetime,time,stat,struct
        from pathlib import Path
        assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
        assert (os.stat('/workspace').st_dev,os.stat('/workspace').st_ino)==(156,32926662)
        paths={paths!r}
        refs={{p:[] for p in paths}};writers=[]
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit():continue
            try:
                comm=(proc/'comm').read_text().strip()
                if comm=='git':writers.append({{'pid':int(proc.name),'comm':comm}})
                links=[]
                for kind in ['cwd','exe']:
                    try:links.append(os.readlink(proc/kind))
                    except OSError:pass
                try:
                    for fd in (proc/'fd').iterdir():
                        try:links.append(os.readlink(fd))
                        except OSError:pass
                except OSError:pass
                try:maps=(proc/'maps').read_text(errors='replace')
                except OSError:maps=''
                try:cmd=(proc/'cmdline').read_bytes().decode(errors='replace')
                except OSError:cmd=''
                for p in paths:
                    if p in links or p in maps or p in cmd:refs[p].append({{'pid':int(proc.name),'comm':comm}})
            except OSError:pass
        records=[]
        for p in paths:
            try:
                s=os.lstat(p)
                if not stat.S_ISREG(s.st_mode) or s.st_dev!=156:continue
                with open(p,'rb') as f:header=f.read(12)
                records.append({{'path':p,'size':s.st_size,'allocated_bytes':s.st_blocks*512,'dev':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'mtime_ns':s.st_mtime_ns,'atime_ns':s.st_atime_ns,'open_refs':refs[p],'pack_signature':header[:4].decode(errors='replace'),'pack_version':struct.unpack('>I',header[4:8])[0] if len(header)==12 else None,'declared_objects':struct.unpack('>I',header[8:12])[0] if len(header)==12 else None}})
            except OSError:pass
        locks=[]
        for parent in ['/workspace/.git','/workspace/.git/objects/pack']:
            locks.extend(str(p) for p in Path(parent).glob('*.lock'))
        env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
        r=subprocess.run(['timeout','-k','5s','90s','nice','-n','19','ionice','-c','3','git','--git-dir=/workspace/.git','fsck','--full','--no-dangling'],capture_output=True,text=True,timeout=100,env=env)
        print(json.dumps({{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'locks':locks,'git_processes':writers,'git_fsck':{{'argv':['git','--git-dir=/workspace/.git','fsck','--full','--no-dangling'],'timeout_seconds':90,'exit_code':r.returncode,'stdout':r.stdout[:16000],'stderr':r.stderr[:16000],'stdout_truncated':len(r.stdout)>16000,'stderr_truncated':len(r.stderr)>16000}},'space_before':{{'path':'/workspace','dev':156,'free_bytes':os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize}}}}))
    ''','v3_git_preparation',timeout=110)
    prep=json.loads((META/'v3_git_preparation.json').read_text())
    cutoff=datetime.datetime.now(datetime.timezone.utc).timestamp()-14*86400
    choices=[x for x in prep['records'] if x['size']<=500*1024**2 and x['size']>=200*1024**2
        and x['mtime_ns']/1e9<cutoff and not x['open_refs'] and x['nlink']==1 and x['pack_signature']=='PACK']
    choices.sort(key=lambda x:(x['mtime_ns'],-x['size']))
    selected=[];total=0
    for item in choices:
        selected.append(item);total+=item['size']
        if total>=9*1024**3:break
    plan={'created_at':now(),'status':'COPY_ONLY_USER_APPROVAL_REQUIRED_FOR_SOURCE_DELETION',
          'root':ROOT,'stage':STAGE,'batch_limit_bytes':512*1024**2,
          'source_files':selected,'selected_bytes':total,'source_deletion_authorized':False}
    (META/'v3_transfer_plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print('PLAN: '+json.dumps({'files':len(selected),'bytes':total,'fsck_exit':prep['git_fsck']['exit_code'],'locks':prep['locks'],'git_processes':prep['git_processes']}),flush=True)

def transfer(limit=None):
    plan=json.loads((META/'v3_transfer_plan.json').read_text())
    selected=plan['source_files'][:limit] if limit else plan['source_files']
    for number,item in enumerate(selected,1):
        batch=f'batch{number:03d}'
        completed=META/(batch+'_verified.json')
        if completed.exists():
            print(batch+': previously completed in this run; no new operation',flush=True)
            continue
        src=item['path'];stage=STAGE+'/'+batch+'.pack';index=STAGE+'/'+batch+'.idx'
        destrel='old174/workspace/.git/objects/pack/'+Path(src).name
        wanted={k:item[k] for k in ['dev','inode','size','mtime_ns']}
        print(batch+': BEGIN '+src+' '+str(item['size'])+' bytes',flush=True)
        source=remote('hrl',f'''
            import os,json,hashlib,stat,datetime
            from pathlib import Path
            p={src!r};wanted={wanted!r}
            assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
            assert os.path.realpath(p)==p and p.startswith('/workspace/.git/objects/pack/tmp_pack_')
            def identity(s):return {{'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns}}
            assert identity(os.lstat(p))==wanted
            refs=[]
            for proc in Path('/proc').iterdir():
                if not proc.name.isdigit():continue
                try:
                    for fd in (proc/'fd').iterdir():
                        try:
                            if os.readlink(fd)==p:refs.append(int(proc.name))
                        except OSError:pass
                except OSError:pass
            assert not refs,refs
            h=hashlib.sha256()
            fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as f:
                assert identity(os.fstat(f.fileno()))==wanted
                for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
            assert identity(os.lstat(p))==wanted
            print(json.dumps({{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':p,'identity':wanted,'sha256':h.hexdigest(),'open_refs_before':refs,'source_stable_during_hash':True}}))
        ''',batch+'_source_hash',timeout=90)
        digest=source['sha256']
        staged=remote('hrl',f'''
            import os,json,hashlib,subprocess,time,stat,datetime
            p={src!r};stage={stage!r};index={index!r};wanted={wanted!r}
            def identity(s):return {{'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns}}
            assert identity(os.lstat(p))==wanted
            assert os.stat({STAGE!r}).st_dev==2431 and not os.path.islink({STAGE!r})
            assert json.load(open({STAGE!r}+'/OWNER.json'))['approved_archive_root']=={ROOT!r}
            assert {item['size']}<=512*1024**2
            argv=['nice','-n','19','ionice','-c','3','rsync','-aH','--no-owner','--no-group','--partial','--fsync','--bwlimit=30m']
            dry=subprocess.run(argv+['--dry-run','--itemize-changes','--',p,stage],capture_output=True,text=True,timeout=15)
            assert dry.returncode==0,dry.stderr
            start=time.monotonic();r=subprocess.run(argv+['--',p,stage],capture_output=True,text=True,timeout=150)
            assert r.returncode==0,r.stderr
            h=hashlib.sha256()
            with open(stage,'rb') as f:
                for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
            assert h.hexdigest()=={digest!r} and os.stat(stage).st_size=={item['size']}
            assert identity(os.lstat(p))==wanted,'Source changed during stage copy'
            # Inspect only the archived duplicate. Never write an index beside source.
            index_result={{'status':'NOT_RUN_INDEX_WOULD_EXCEED_512MIB_BATCH_BUDGET'}}
            if {item['size']}+{item['declared_objects']}*32+65536<=512*1024**2:
                ix=subprocess.run(['timeout','-k','3s','35s','nice','-n','19','ionice','-c','3','git','index-pack','--strict','--threads=1','-o',index,stage],text=True,capture_output=True,timeout=40,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
                index_result={{'exit_code':ix.returncode,'stdout':ix.stdout[:1000],'stderr':ix.stderr[:2000],'index_path':index,'complete_pack_indexable':ix.returncode==0,'unique_source_objects':'UNKNOWN_NOT_AUTHORITY_TO_DELETE'}}
            s=os.lstat(stage)
            print(json.dumps({{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'size':s.st_size,'dev':s.st_dev,'inode':s.st_ino,'sha256':h.hexdigest(),'source_stable':True,'dry_run_exit':dry.returncode,'dry_run':dry.stdout,'copy_exit':r.returncode,'copy_argv':argv+['--',p,stage],'elapsed_seconds':time.monotonic()-start,'pack_duplicate_index_analysis':index_result}}))
        ''',batch+'_stage_copy_verify',timeout=205)
        archived=remote('hrl-174-new',f'''
            import os,json,hashlib,subprocess,time,datetime,stat
            root={ROOT!r};stage={stage!r};rel={destrel!r}
            m=json.loads(subprocess.check_output(['findmnt','-J','-T',root,'-o','TARGET,SOURCE,FSTYPE'],text=True))['filesystems'][0]
            assert m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs'
            assert json.load(open(root+'/AUTHORIZATION_AND_PROBE.json'))['level']=='SSHFS_ARCHIVE_WRITE_VERIFIED'
            assert (os.lstat(stage).st_dev,os.lstat(stage).st_ino,os.lstat(stage).st_size)==({staged['dev']},{staged['inode']},{item['size']})
            h=hashlib.sha256()
            with open(stage,'rb') as f:
                for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
            assert h.hexdigest()=={digest!r}
            parent=root
            for component in rel.split('/')[:-1]:
                parent+='/'+component
                if not os.path.lexists(parent):os.mkdir(parent,0o700)
                assert stat.S_ISDIR(os.lstat(parent).st_mode) and not os.path.islink(parent)
            dest=root+'/'+rel
            assert not os.path.lexists(dest),'Destination already exists; do not overwrite without review'
            argv=['nice','-n','19','ionice','-c','3','rsync','-aH','--no-owner','--no-group','--partial','--fsync','--bwlimit=30m']
            dry=subprocess.run(argv+['--dry-run','--itemize-changes','--',stage,dest],capture_output=True,text=True,timeout=15)
            assert dry.returncode==0,dry.stderr
            start=time.monotonic();r=subprocess.run(argv+['--',stage,dest],capture_output=True,text=True,timeout=150)
            assert r.returncode==0,r.stderr
            # rsync exited and closed its destination. Independently reopen through SSHFS.
            h=hashlib.sha256()
            with open(dest,'rb') as f:
                for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
            s=os.lstat(dest)
            assert s.st_size=={item['size']} and h.hexdigest()=={digest!r}
            receipt={{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batch':{batch!r},'source':{src!r},'destination_relative_path':rel,'destination':dest,'size':s.st_size,'source_sha256':{digest!r},'stage_sha256':{digest!r},'sshfs_reopened_sha256':h.hexdigest(),'verification_level':'SSHFS_READBACK_VERIFIED','server_side_native_verified':False,'dry_run_exit':dry.returncode,'dry_run':dry.stdout,'copy_exit':r.returncode,'copy_argv':argv+['--',stage,dest],'elapsed_seconds':time.monotonic()-start,'remote_uid':s.st_uid,'remote_gid':s.st_gid,'remote_mode':stat.S_IMODE(s.st_mode),'source_action':'KEEP_REQUIRES_SEPARATE_USER_APPROVAL'}}
            rd=root+'/receipts'
            if not os.path.lexists(rd):os.mkdir(rd,0o700)
            assert not os.path.islink(rd)
            with open(rd+'/'+{batch!r}+'.json','x') as f:json.dump(receipt,f,indent=2);f.flush();os.fsync(f.fileno())
            print(json.dumps(receipt))
        ''',batch+'_archive_copy_verify',timeout=205)
        stable=remote('hrl',f'''
            import os,json,datetime
            s=os.lstat({src!r});wanted={wanted!r}
            actual={{'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns}}
            assert actual==wanted,'Source changed; retain stage and investigate'
            print(json.dumps({{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':{src!r},'identity_after':actual,'stable':True,'source_action':'KEEP','workspace_free_bytes':os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize}}))
        ''',batch+'_source_after',timeout=20)
        cleaned=remote('hrl-174-new',f'''
            import os,json,hashlib,stat
            p={stage!r};s=os.lstat(p)
            assert (s.st_dev,s.st_ino,s.st_size)==({staged['dev']},{staged['inode']},{item['size']})
            h=hashlib.sha256()
            with open(p,'rb') as f:
                for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
            assert h.hexdigest()=={digest!r}
            os.unlink(p)
            index={index!r};index_deleted=False
            if os.path.lexists(index):
                assert stat.S_ISREG(os.lstat(index).st_mode) and not os.path.islink(index)
                os.unlink(index);index_deleted=True
            assert not os.path.lexists(p)
            print(json.dumps({{'stage_copy_deleted':True,'index_copy_deleted':index_deleted,'original_source_deleted':False,'stage_data_bytes_after':sum(os.lstat({STAGE!r}+'/'+n).st_size for n in os.listdir({STAGE!r}) if n!='OWNER.json')}}))
        ''',batch+'_stage_cleanup',timeout=90)
        result={'batch':batch,'source_metadata':item,'source_hash':source,'stage_verification':staged,
                'archive_verification':archived,'source_after':stable,'stage_cleanup':cleaned}
        completed.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(batch+': VERIFIED '+str(item['size'])+' bytes; SOURCE KEPT; stage cleaned',flush=True)

if __name__=='__main__':
    if sys.argv[1]=='probes':probes()
    elif sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='transfer':transfer(int(sys.argv[2]) if len(sys.argv)>2 else None)
