"""PREPARED_NOT_EXECUTED: parent-only finite actual LDST CPU fixture entry.

No CLI, simulator, compiler, discovery/adoption or background entry. Parent
pins registration, this source, classifier and its actual CPUAdmission closure.
"""
import hashlib
import inspect
import json
import os
from pathlib import Path
import resource
import shlex
import signal
import stat
import subprocess
import threading
import time

CORE = 'b1077667f7a2bcc72260733f88f5798f167346d1'
TREE = '0a462efb9a48409064259735108b88dad127a53c'
SOURCE = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-rob1-core-174-v1')
BUILD = Path('/workspace/dtc-evidence-closure-20261019-v1/rob1/ldst-qualification-r1/build')
ELF = BUILD/'dtc_l1_rob1_collector_ldst'
LIBRARY = BUILD/'libcudart.so'
CONFIG = SOURCE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'
ROLE = 'ROB1_ACTUAL_LDST_FIXTURE_RUNTIME_CONTROL'
ORDER = ('omitted','explicit_zero','quota_one','bad_width','bad_mode','nonfinite')
ARGS = (('omitted','3','1'),('0','3','1'),('1','3','1'),
        ('2','3','1'),('1','2','1'),('1','3','0'))
OUTPUT_ROOT = Path('/workspace/dtc-evidence-closure-20261019-v1/rob1/fixture-runtime-v1')
FLOOR = 5*1024**3
OUTPUT_MAX = 32*1024**2
START_FREE = FLOOR + OUTPUT_MAX + 128*1024**2
STREAM_MAX = 512*1024
TOTAL_SECONDS, CASE_SECONDS, CLEANUP_SECONDS = 600, 60, 5
STAT_KEYS = ('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns','st_mode','st_uid','st_gid','st_nlink')


class RuntimeStop(RuntimeError):
    pass


def require(value, reason):
    if not value: raise RuntimeStop(reason)


def stamp(s): return {key:getattr(s,key) for key in STAT_KEYS}


def sha_file(path, *, blob=None):
    path = Path(path); before = path.stat(); digest = hashlib.sha256()
    require(path.is_absolute() and stat.S_ISREG(before.st_mode) and before.st_size <= 64*1024**2,
            'BOUNDED_ABSOLUTE_REGULAR_FILE_REQUIRED:'+str(path))
    git = hashlib.sha1(b'blob '+str(before.st_size).encode()+b'\0')
    count = 0
    with path.open('rb') as stream:
        require(stamp(os.fstat(stream.fileno())) == stamp(before), 'FILE_OPEN_RACE:'+str(path))
        while True:
            data = stream.read(1024**2)
            if not data: break
            count += len(data); require(count <= 64*1024**2, 'FILE_GROWTH_BOUND')
            digest.update(data); git.update(data)
        require(stamp(os.fstat(stream.fileno())) == stamp(before), 'FILE_MUTATED:'+str(path))
    require(count == before.st_size and stamp(path.stat()) == stamp(before), 'FILE_REPLACED:'+str(path))
    if blob is not None: require(git.hexdigest() == blob, 'CORE_GIT_BLOB_CHANGED:'+str(path))
    return digest.hexdigest(), stamp(before)


def read_bound(descriptor):
    path = Path(descriptor['path']); digest, before = sha_file(path)
    require(digest == descriptor['sha256'], 'BOUND_FILE_CHANGED:'+str(path))
    with path.open('rb') as stream: data=stream.read(64*1024**2+1)
    require(len(data)<=64*1024**2 and hashlib.sha256(data).hexdigest() == digest and stamp(path.stat()) == before,
            'BOUND_JSON_CHANGED_DURING_READ')
    return json.loads(data)


def write_new(path, value):
    with Path(path).open('x') as stream: stream.write(json.dumps(value,indent=2)+'\n')


def tree_oid(rows):
    """Verify all652 regular Git leaves against the fixed b107 whole-tree OID."""
    root = {}
    for row in rows:
        parts = row['path'].split('/')
        require(parts and all(p not in ('','.','..') for p in parts), 'CORE_SOURCE_PATH')
        node = root
        for part in parts[:-1]:
            node = node.setdefault(part,{})
            require(isinstance(node,dict), 'CORE_TREE_PATH_COLLISION')
        require(parts[-1] not in node and row['mode'] in ('100644','100755'), 'CORE_TREE_LEAF')
        node[parts[-1]] = (row['mode'], row['blob'])
    def encode(node):
        entries = []
        for name, value in node.items():
            directory = isinstance(value,dict)
            mode, oid = ('40000',encode(value)) if directory else value
            entries.append((name.encode()+ (b'/' if directory else b''),
                            mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(oid)))
        body = b''.join(value for _,value in sorted(entries))
        return hashlib.sha1(b'tree '+str(len(body)).encode()+b'\0'+body).hexdigest()
    return encode(root)


def freeze_check(reg):
    frozen = read_bound(reg['static_freeze'])
    require(frozen['core_commit'] == CORE and frozen['core_tree'] == TREE, 'MATCHING_B107_ABI_REQUIRED')
    rows = read_bound(frozen['core_source_manifest'])
    require(len(rows) == 652 and tree_oid(rows) == TREE, 'WHOLE_CORE_SOURCE_TREE_REQUIRED')
    signatures = {}
    for row in rows:
        path = SOURCE/row['path']
        require(not path.is_symlink() and path.resolve().is_relative_to(SOURCE), 'CORE_SOURCE_ESCAPE')
        digest, current = sha_file(path, blob=row['blob'])
        require(digest == row['sha256'] and bool(current['st_mode'] & 0o111) == (row['mode']=='100755'),
                'CORE_SOURCE_BYTES_OR_MODE_CHANGED')
        signatures[str(path)] = current
    build = read_bound(frozen['actual_build_receipt'])
    require(build['phase']=='build' and build['exit']==0 and build['reason'] is None and
            build['core']==CORE and build['root_terminal']['reaped'] is True and
            not build['current_group_instances_after_reap'], 'SUCCESSFUL_FRESH_ABI_BUILD_REQUIRED')
    commands = read_bound(frozen['compile_commands'])
    required = ('tests/dtc_l1_rob1_collector_ldst_test.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/gpu-sim.cc')
    for suffix in required:
        matches = [r for r in commands if r['file'].endswith('/'+suffix)]
        require(bool(matches), 'ACTUAL_ASSERT_ENABLED_COMPILER_RECIPE_REQUIRED:'+suffix)
        for row in matches:
            command = row.get('arguments') or shlex.split(row['command'])
            require('-O1' in command and '-g0' in command and
                    not any(p=='-DNDEBUG' or p.startswith('-DNDEBUG=') or
                            p=='-DROB1_ORIGINAL_CORE' or p.startswith('-DROB1_ORIGINAL_CORE=') for p in command),
                    'ASSERTION_OR_ABI_FLAGS_CHANGED')
            if suffix.startswith('tests/'):
                require('-UNDEBUG' in command and '-fno-access-control' in command, 'FIXTURE_SETUP_FLAGS_CHANGED')
    manifests = read_bound(frozen['mapping_manifests'])
    require(set(manifests)=={str(ELF)}, 'ONE_EXACT_FIXTURE_MAPPING_CLOSURE_REQUIRED')
    manifest = manifests[str(ELF)]
    require(manifest['target']==str(ELF) and manifest['cache_mode']=='PRESENT_REQUIRED_EARLY', 'LOADER_CONTRACT_CHANGED')
    files = {r['path']:r for r in manifest['files']}
    require(len(files)==len(manifest['files']) and str(LIBRARY) in files and
            manifest['interpreter'] in files and '/etc/ld.so.cache' in files and str(ELF) in files,
            'COMPLETE_ELF_LIBRARY_LOADER_CACHE_FREEZE_REQUIRED')
    fields = dict(device='st_dev',inode='st_ino',size='st_size',mtime_ns='st_mtime_ns',ctime_ns='st_ctime_ns',
                  mode='st_mode',uid='st_uid',gid='st_gid',nlink='st_nlink')
    for path, row in files.items():
        digest, current = sha_file(path)
        require(digest==row['sha256'] and all(current[v]==row['identity'][k] for k,v in fields.items()) and
                os.major(current['st_dev'])==row['identity']['major'] and os.minor(current['st_dev'])==row['identity']['minor'],
                'STATIC_RUNTIME_BYTES_OR_IDENTITY_CHANGED:'+path)
        signatures[path] = current
    require(files[str(ELF)]['sha256']==frozen['fixture_sha256'] and
            files[str(LIBRARY)]['sha256']==frozen['library_sha256'], 'WHOLE_LIBRARY_ELF_FREEZE_JOIN')
    config_sha, config_stat = sha_file(CONFIG)
    require(config_sha=='8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3', 'CONFIG_CHANGED')
    signatures[str(CONFIG)] = config_stat
    return frozen, signatures


def identity(pid, with_status=True):
    q=Path('/proc')/str(pid); fields=(q/'stat').read_text().rsplit(')',1)[1].split()
    row=dict(pid=pid,start_ticks=int(fields[19]),ppid=int(fields[1]),state=fields[0],pgid=int(fields[2]),sid=int(fields[3]))
    if with_status:
        status=dict(line.split(':',1) for line in (q/'status').read_text().splitlines() if ':' in line)
        row.update(tgid=int(status['Tgid']),tracer_pid=int(status['TracerPid']))
    return row


def own_group(root):
    if root is None: return []
    rows=[]
    for path in Path('/proc').iterdir():
        if path.name.isdigit():
            try: row=identity(int(path.name),with_status=False)
            except (FileNotFoundError,ProcessLookupError): continue
            if row['pgid']==root['pgid'] and row['sid']==root['sid']: rows.append(row)
    return rows


def limits():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_CPU,(30,31))
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(STREAM_MAX,STREAM_MAX))


def output_bytes(output):
    return sum(p.stat().st_size for p in output.rglob('*') if p.is_file() and not p.is_symlink())


def free_bytes(output):
    info=os.statvfs(output); return info.f_bavail*info.f_frsize


def cleanup(proc,pidfd,root):
    if proc.returncode is not None: return dict(reaped=True,signal_sent=False)
    sent=False; error=None;deadline=time.monotonic()+CLEANUP_SECONDS
    try:
        current=identity(proc.pid)
        require(root is not None and all(current[k]==root[k] for k in ('pid','start_ticks','tgid','pgid','sid')),
                'UNRESOLVED_OWN_ROOT_IDENTITY_NO_SIGNAL')
        if current['state']!='Z':
            require(pidfd is not None,'OWN_PIDFD_REQUIRED')
            signal.pidfd_send_signal(pidfd,signal.SIGTERM);sent=True
    except (OSError,ValueError,RuntimeStop) as exc: error=repr(exc)
    try:
        proc.wait(timeout=max(.001,deadline-time.monotonic()))
        return dict(reaped=True,signal_sent=sent,identity_error=error)
    except (subprocess.TimeoutExpired,RuntimeStop) as exc:
        return dict(reaped=False,signal_sent=sent,reason='CLEANUP_UNRESOLVED_NO_FALLBACK_SIGNAL',error=error or repr(exc))


def _run(path,expected_sha,CPUAdmission,classify,deadline):
    reg=read_bound(dict(path=str(path),sha256=expected_sha))
    require(reg['status']=='RELEASED_ROB1_SIX_ACTUAL_LDST_CPU_CASES_ONLY' and
            reg['ordered_cases']==list(ORDER) and reg['runtime_role']['name']==ROLE and
            reg['admission']['disk_floor_exclusive_bytes']==FLOOR, 'EXACT_RUNTIME_RELEASE_REQUIRED')
    require(CPUAdmission.__name__=='CPUAdmission' and classify.__name__=='classify', 'EXACT_PARENT_INTERFACES_REQUIRED')
    for callable_ in (CPUAdmission,classify):
        source=str(Path(inspect.getfile(callable_)).resolve())
        require(source in reg['source_sha256'], 'UNBOUND_PARENT_CALLABLE')
    for source, digest in reg['source_sha256'].items():
        require(sha_file(source)[0]==digest, 'RUNTIME_SOURCE_CLOSURE_CHANGED:'+source)
    require(str(Path(__file__).resolve()) in reg['source_sha256'], 'LAUNCHER_SOURCE_NOT_BOUND')
    require(Path(reg['output']).is_absolute(),'ABSOLUTE_ATTEMPT_OUTPUT_REQUIRED')
    output=Path(reg['output']).resolve()
    require(output.is_relative_to(OUTPUT_ROOT) and output!=OUTPUT_ROOT, 'ISOLATED_ATTEMPT_OUTPUT_REQUIRED')
    output.mkdir(parents=True,exist_ok=False)
    write_new(output/'START.json',dict(registration_sha256=expected_sha,core=CORE,order=ORDER,
              boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),simulator_starts=0))
    results=[];failure=None
    for case,args in zip(ORDER,ARGS):
        proc=None;pidfd=None;root=None;reason=None;terminal=None;leftovers=[];closed=None
        dest=output/case;dest.mkdir();(dest/'tmp').mkdir()
        try:
            require(time.monotonic()<deadline, 'COHORT_TOTAL_BOUND_NO_START')
            frozen, signatures=freeze_check(reg)  # matching whole library/ELF before every Popen
            gate=CPUAdmission(reg,[reg['runtime_role']])
            if not gate.admit(dest/'admission'):
                reason='WAIT_RESOURCE_OR_AUTHORITY_NO_FIXTURE_START'
            else:
                second=json.loads((dest/'admission/SECOND.json').read_text())
                require(second['output_filesystem_device']==output.stat().st_dev, 'ADMISSION_NOT_ACTUAL_OUTPUT_MOUNT')
                require(free_bytes(output)>=START_FREE and output_bytes(output)<=OUTPUT_MAX, 'START_OUTPUT_FOOTPRINT_RESERVE')
                for file,saved in signatures.items():
                    require(stamp(Path(file).stat())==saved,'STATIC_FREEZE_CHANGED_AFTER_ADMISSION:'+file)
                for source,digest in reg['source_sha256'].items():
                    require(sha_file(source)[0]==digest,'RUNTIME_SOURCE_CHANGED_AFTER_ADMISSION')
                require(0<=time.monotonic_ns()-second['monotonic_ns']<=5*10**9,'STALE_PAIR_NO_FIXTURE_START')
                argv=[str(ELF),str(CONFIG),*args]
                env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',
                         LD_LIBRARY_PATH=str(BUILD),TMPDIR=str(dest/'tmp'))
                write_new(dest/'START.json',dict(argv=argv,env=env,cwd=str(dest),static_freeze_sha256=reg['static_freeze']['sha256'],
                          admission_sha256=sha_file(dest/'admission/ADMISSION.json')[0],monotonic_ns=time.monotonic_ns()))
                began=time.monotonic();case_deadline=min(deadline,began+CASE_SECONDS)
                with (dest/'stdout').open('xb') as stdout,(dest/'stderr').open('xb') as stderr:
                    try:
                        proc=subprocess.Popen(argv,cwd=dest,env=env,stdin=subprocess.DEVNULL,stdout=stdout,
                              stderr=stderr,close_fds=True,start_new_session=True,preexec_fn=limits)
                        pidfd=os.pidfd_open(proc.pid);root=identity(proc.pid)
                        require(root['pgid']==root['sid']==proc.pid,'OWN_NEW_SESSION_REQUIRED')
                        attributes=None
                        try:
                            q=Path('/proc')/str(proc.pid)
                            attributes=dict(exe=os.readlink(q/'exe'),cwd=os.readlink(q/'cwd'),
                                            argv=[v.decode() for v in (q/'cmdline').read_bytes().split(b'\0') if v])
                            after=identity(proc.pid)
                            require(all(after[k]==root[k] for k in ('pid','start_ticks','tgid','pgid','sid')),
                                    'CURRENT_ROOT_INSTANCE_CHANGED')
                            if after['state']=='Z': attributes=None
                            else: require(attributes==dict(exe=str(ELF),cwd=str(dest),argv=argv),'CURRENT_ROOT_ATTRIBUTES_CHANGED')
                        except (FileNotFoundError,ProcessLookupError): attributes=None
                        write_new(dest/'CHILD.json',dict(root=root,actual_Popen=True,live_attributes=attributes,
                            boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                            live_observation_available=attributes is not None))
                        next_sample=0.0
                        while proc.poll() is None:
                            now=time.monotonic()
                            require(now<case_deadline,'CASE_OR_COHORT_TIMEOUT')
                            require(free_bytes(output)>FLOOR and output_bytes(output)<=OUTPUT_MAX,'RUNTIME_OUTPUT_DISK_BOUND')
                            require(all((dest/name).stat().st_size<=STREAM_MAX for name in ('stdout','stderr')),'STREAM_OUTPUT_BOUND')
                            require(all(r['pid']==proc.pid for r in own_group(root)),'UNEXPECTED_OWN_GROUP_DESCENDANT')
                            q=Path('/proc')/str(proc.pid)
                            if q.exists():
                                try:
                                    status=(q/'status').read_text().splitlines()
                                    rss=next((int(s.split()[1])*1024 for s in status if s.startswith('VmRSS:')),0)
                                    require(rss<=1024**3 and len(list((q/'task').iterdir()))<=4,'ROOT_RSS_OR_TASK_BOUND')
                                except FileNotFoundError: pass
                            if now>=next_sample:
                                sample=gate.sample();checks=gate.checks(sample)
                                checks['no_new_host_oom']=sample['host_oom_kill']==second['host_oom_kill']
                                checks['no_new_cgroup_oom']=all(sample['cgroup_events'][k]==second['cgroup_events'][k] for k in ('oom','oom_kill'))
                                with (dest/'RUNTIME_RESOURCES.jsonl').open('a') as stream: stream.write(json.dumps(dict(sample=sample,checks=checks))+'\n')
                                require(all(checks.values()),'RUNTIME_RESOURCE_OR_AUTHORITY_STOP')
                                next_sample=now+1.0
                            time.sleep(.05)
                        terminal=dict(returncode=proc.returncode,reaped=True,wait_monotonic_ns=time.monotonic_ns())
                    except BaseException as exc: reason=repr(exc)
                    finally:
                        if proc is not None and proc.returncode is None: closed=cleanup(proc,pidfd,root)
                        if proc is not None: terminal=dict(returncode=proc.returncode,reaped=proc.returncode is not None,wait_monotonic_ns=time.monotonic_ns())
                        if pidfd is not None: os.close(pidfd)
                        leftovers=own_group(root)  # AFTER reap: inspect/report only, never signal a group
                        if leftovers or (proc is not None and proc.returncode is None): reason=reason or 'CLEANUP_UNRESOLVED'
                final=gate.sample();checks=gate.checks(final)
                checks['no_new_host_oom']=final['host_oom_kill']==second['host_oom_kill']
                checks['no_new_cgroup_oom']=all(final['cgroup_events'][k]==second['cgroup_events'][k] for k in ('oom','oom_kill'))
                write_new(dest/'FINAL_RESOURCES.json',dict(sample=final,checks=checks))
                require(all(checks.values()),'FINAL_RESOURCE_OR_AUTHORITY_STOP')
                require(free_bytes(output)>FLOOR and output_bytes(output)<=OUTPUT_MAX,'FINAL_OUTPUT_DISK_BOUND')
        except BaseException as exc: reason=reason or repr(exc)
        if proc is None:
            result=dict(case=case,status='NO_FIXTURE_START',reason=reason,actual_starts=0)
        else:
            stdout=(dest/'stdout').read_bytes();stderr=(dest/'stderr').read_bytes()
            classification=classify(case,proc.returncode,stdout,stderr,execution_failure_reason=reason)
            result=dict(case=case,status=classification['status'],classification=classification,reason=reason,
                actual_starts=1,root=root,terminal=terminal,cleanup=closed,group_instances_after_reap=leftovers,
                stdout_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest(),
                static_library_observation='STATIC_FREEZE_ONLY_NO_PER_CASE_MAPPING_OR_DLADDR_CLAIM')
        write_new(dest/'TERMINAL.json',result);results.append(result)
        if not result['status'].startswith('PASS_'):
            failure=reason or result['status'];break
    report=dict(status='PASS_SIX_ACTUAL_LDST_CPU_CASES_ONLY' if len(results)==6 and not failure else 'ROB1_RUNTIME_INCOMPLETE',
        results=results,failure=failure,actual_starts=sum(r['actual_starts'] for r in results),
        simulator_starts=0,retries=0,whole_binary_OFF_equivalence=False,production_authority=False)
    write_new(output/'RESULT.json',report)
    return report


def run_registered(registration_path, expected_registration_sha256, *, cpu_admission_class, classify_output):
    """Parent-only call; parent retains an outer receipt even for pre-output errors.

    Inject the exact source-bound latest CPUAdmission and this pack's classifier.
    Every case gets a NEW full pair; no old admission, helper rerun or baseline.
    """
    require(threading.active_count()==1 and signal.getsignal(signal.SIGCHLD)==signal.SIG_DFL,
            'SINGLE_THREAD_SOLE_DIRECT_CHILD_WAITER_REQUIRED')
    require(hasattr(os,'pidfd_open') and hasattr(signal,'pidfd_send_signal'),'PIDFD_RUNTIME_REQUIRED')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0),'DO_NOT_REPLACE_PARENT_TIMER')
    def stop(number,frame): raise RuntimeStop('PARENT_SIGNAL_OR_TOTAL_BOUND:'+str(number))
    previous={number:signal.signal(number,stop) for number in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP,signal.SIGALRM)}
    deadline=time.monotonic()+TOTAL_SECONDS-CLEANUP_SECONDS
    signal.setitimer(signal.ITIMER_REAL,TOTAL_SECONDS-CLEANUP_SECONDS)
    try:
        return _run(registration_path,expected_registration_sha256,cpu_admission_class,classify_output,deadline)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        for number,handler in previous.items(): signal.signal(number,handler)
