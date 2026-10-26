#!/usr/bin/env python3
"""UNINSTALLED finite native runtime candidate. Import performs no action.
Only explicit dispatch() mutates authority or launches a process after exact guards.
Main must independently review/freeze/install this file and the sole-entry leaf.
"""
from __future__ import annotations
import contextlib,fcntl,hashlib,importlib.util,json,os,pathlib,uuid
import copy,datetime,time,subprocess,resource as rl,signal,selectors,stat,sys,shutil,re
P=pathlib.Path;M=1<<20;G=1<<30
J=P('/root/data/ep_tag_reservation_lifetime_20261026_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
BASE=P('/root/data/ep_l2_main_vector_r5_20261023_v1')
REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
LED=N/'control/qualification_ledger'
OFF='EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2'
ON='EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2'
CASES=(OFF,ON)
SOURCEQ_SHA='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814'
FRESH_SHA='de0e6db73adb59de9804b57d6f925537fcf9429a50249d82cd2a309df90862ce'
IDENTITY={
 'core_source_commit':'11c02df1034112013523429894f1f931323adbef',
 'framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
 'vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b',
 'binary_sha256':'8d55f19bbe74c72e5da688f0ede6c2de1c3aa13040015475f23c9c6c521b9bef',
 'archive_sha256':'685b497b50328deff4b96741c9a770b4b37e5d4bb2c8a1b5db90558b90be73c4'}
TRACE_PINS={
 str(N/'tools/bin/strace'):'38a5c75cb29dd85ddd7780d54f5bf595554d7a1b5c42524b23065f5dc4c4b01d',
 str(N/'tools/lib/liblzma.so.5'):'493cb401ab4aa3bba611ca464d12996afb3b327940d29476f535f999e167439b',
 str(N/'tools/lib/libunwind-ptrace.so.0'):'f791a9b0b01faa13a65ee066d2351d2e38a23d6c3752f75eebeaf0fc5c7d56f4',
 str(N/'tools/lib/libunwind-x86_64.so.8'):'1077e265bdd76ed4f2d628ea29150eb98f5c7c8f5a30004a561e6e93a2a6f097',
 str(N/'tools/lib/libunwind.so.8'):'5d1f6f104f79698e137c9f17c4b0317dfd96816c0eb6a87c50619a41472ca382',
 str(N/'common-lib/ld-linux-x86-64.so.2'):'9eb34cb2da3ae2a9398cc09b3cd2d069563ec40d9858cb711af15cd23fa80abf',
 str(N/'common-lib/libc.so.6'):'c53819710b163d3f1d2541778590d58d3ef31cb0ed75adcbe059faac68c1e72d',
 str(N/'common-lib/libm.so.6'):'00830df310aac5023e10bd7b715149ab8ddc682277fd8ae3539a7a44fcdd6c38'}
class Hold(RuntimeError):pass
def need(ok,why):
 if not ok:raise Hold(why)
def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb') as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()
def read(path):return json.loads(P(path).read_text())
def exact(path,expected):
 need(isinstance(expected,str) and len(expected)==64,'missing immutable SHA')
 need(sha(path)==expected,'immutable SHA drift: '+str(path));return read(path)
def load_frozen(path,expected,name):
 need(sha(path)==expected,'module drift: '+str(path))
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate_static(case):
 """Read-only after main materialization. Never repairs missing pins/proofs."""
 need(case in CASES,'unknown exact cohort');b=J/'cases'/case
 p=b/'control/FROZEN_SPEC.json';s=read(p);join=read(b/'control/SPEC_AUTHORIZATION_BINDING.json')
 need(join['spec_path']==str(p) and join['spec_sha256']==sha(p),'spec/auth join drift')
 a=exact(b/'control/USER_AUTHORIZATION.json',join['authorization_sha256'])
 need(a['cohort']==case and a['spec_sha256']==sha(p),'authorization/spec mismatch')
 need(a['explicit_user_approval'] is True and a['maximum_complete_application_starts']==2,'exact current scope missing')
 need(a['budgets']=={OFF:1,ON:1} and a['this_case_new_budget']==1,'fresh exact one-per-arm scope missing')
 need(a['execution_order']==list(CASES) and a['registration_mode']=='SERIAL_EXACT_ONE_AT_A_TIME','serial scope missing')
 need(not a['automatic_retry'] and not a['refund'] and a['baseline_reruns']==0,'forbidden retry/refund/baseline')
 need(sha(a['user_request_path'])==a['user_request_sha256']==join['user_request_sha256'],'saved user request drift')
 need(s['schema']=='EP_L2_TAG_LIFETIME_FROZEN_SPEC_V1' and s['cohort']==case,'scope drift')
 need(s['source_identity']==IDENTITY==a['source_identity'],'new-source identity mismatch')
 need(s['application_budget']==1 and s['automatic_retry'] is False and not s['refund'],'fresh1 no retry')
 need(s['pair_order']==list(CASES) and s['pair_role']==('OFF' if case==OFF else 'ON'),'pair order')
 need(s['registration_mode']=='SERIAL_EXACT_ONE_AT_A_TIME','no simultaneous double reservation')
 need(s['common_pair_lock_path']==str(J/'control/TWO_ARM_WHOLE_OPERATION.lock'),'common pair lock')
 need(s['source_qualification_sha256']==SOURCEQ_SHA,'wrong SourceQ')
 need(P(s['source_qualification_path'])==J/'control/SOURCE_QUALIFICATION_V2.json','V2 SourceQ path required')
 q=exact(s['source_qualification_path'],SOURCEQ_SHA)
 need(q['schema']=='EP_L2_TAG_LIFETIME_SOURCE_QUALIFICATION_V1' and q['status']=='SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED','source engineering qualification missing')
 need(q['source_identity']==IDENTITY and not q['scientific_acceptance_granted'],'SourceQ identity/scope')
 for label,e in q['evidence_refs'].items():need(sha(e['path'])==e['sha256'],'SourceQ evidence drift '+label)
 ri=exact(s['runtime_artifact_identity_path'],s['runtime_artifact_identity_sha256'])
 need(ri['source_identity']==IDENTITY and ri['status']=='CANONICAL_RUNTIME_ARTIFACTS_GENUINE164_AND_TWO_NATIVE_RESTORES_PASS','runtime artifact release missing')
 release=exact(s['source_release_receipt_path'],s['source_release_receipt_sha256'])
 need(release['status']=='GENUINE164_SOURCE_RELEASE_CLOSED_REOPEN_SHA_AND_TWO_NATIVE_RESTORES_PASS','source release missing')
 # Old source-copy receipt names its source TAR. It is not canonical lib identity.
 need(release['source_identity']['archive_sha256']==s['source_tar_sha256']!=IDENTITY['archive_sha256'],'tar/library alias')
 proof=exact(s['input_binding_path'],s['input_binding_sha256'])
 need(s['input_binding_sha256']==FRESH_SHA and proof['status']=='FRESH_GENUINE164_INPUT_CLOSED_REOPEN_FULL_SHA_PASS','fresh input proof missing')
 for field in ('pinned_files','env_hashes'):
  for path,h in s[field].items():need(sha(path)==h,'frozen file drift '+path)
 need(sha(s['binary_path'])==IDENTITY['binary_sha256'] and sha(s['static_library_path'])==IDENTITY['archive_sha256'],'ELF/staticlib identity')
 configs=s['ordered_configs']
 need(s['config_count']==4 and s['config4_forbidden'] and len(configs)==4,'exact four baseline configs only')
 for i,c in enumerate(configs):
  need(P(c['path'])==b/'env'/('config-'+str(i)+'.config') and sha(c['path'])==c['sha256'],'ordered baseline config drift')
 need(s['expected_effective_options']=={},'no sensitivity config delta')
 need(s['observer_env']=={'EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1','EPL2_TAG_LIFETIME':'0' if case==OFF else '1'},'unexpected observer env')
 need(s['host_cpu']==16 and s['nice']==10 and s['memory_cap_bytes']==9*G and s['wall_timeout_seconds']==7200,'model caps drift')
 need(s['reserved_write_bytes']==512*M and s['advertised_peer_reservation_bytes']==3584*M,'write guarantee drift')
 need(s['shared_floor_compatibility_margin_bytes']==3*G,'floor compatibility margin')
 need(s['result_cap_bytes']==128*M and s['metadata_charged_to_result_cap'],'metadata charged inside result cap')
 need(s['tmp_cache_aggregate_cap_bytes']==128*M and s['local_archive_staging_cap_bytes']==0,'aggregate tmp/staging cap')
 need(s['native_restore_count']==2 and s['native_restore_per_target_cap_bytes']==128*M,'restore caps')
 need(s['archive_chunk_bytes']==16*M,'copy-memory bound')
 need(sum(s['write_components_bytes'].values())==512*M,'whole operation512MiB')
 for path,h in TRACE_PINS.items():need(s['pinned_files'].get(path)==h and sha(path)==h,'required tracer/loader/library pin missing or drift '+path)
 need(s['runtime_module_sha256'] is not None,'main-frozen engine missing')
 need(s['runtime_module_path']==str(J/'tools_v2/finite_native_runtime.py') and sha(s['runtime_module_path'])==s['runtime_module_sha256'],'main installed frozen engine mismatch')
 need(s['help_loading_max_invocations']==1,'at most one bounded help-loading operation')
 return b,s,a,q,proof
def environment(s,out):
 """Exact whitelist; observer single delta and no accidental inherited GPU/lib vars."""
 return dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',
  LD_LIBRARY_PATH=str(N/'common-lib'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
  MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(J/'cases'/s['cohort']/'run/tmp'),
  XDG_CACHE_HOME=str(J/'cases'/s['cohort']/'run/cache'),**s['observer_env'])
def command(s,out=None):
 args=[str(N/'common-lib/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(N/'EP/env/lib'),s['binary_path'],'-trace',s['trace_entry']]
 for c in s['ordered_configs']:args+=['-config',str(P(out)/P(c['path']).name) if out is not None else c['path']]
 return args

def launch_command(s,out):
 return [str(N/'common-lib/ld-linux-x86-64.so.2'),'--library-path',str(N/'tools/lib')+':'+str(N/'common-lib'),str(N/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(P(out)/'actual_file_process_network.log'),'--',*command(s,out)]
def syscall_proof(path,s,model_pid=None):
 expected={str(P(s['trace_entry'])):0,str(P(s['trace_entry']).parent/'kernel-1.traceg'):0}
 successful_open_lines=0;execs=0;forks=0
 with P(path).open(errors='replace') as stream:
  for line in stream:
   need('connect(' not in line,'unexpected traced network connect')
   if re.search(r'\bexecve(?:at)?\(',line):
    execs+=1
    need(not re.search(r'(?i)(?:^|[/ ])ssh(?:[ .,/]|$)',line.replace(chr(34),' ').replace(chr(39),' ')),'unexpected traced ssh exec')
   if re.search(r'\b(?:fork|vfork|clone|clone3)\(',line):forks+=1
   if re.search(r'\bopen(?:at|at2)?\(',line) and re.search(r'\)\s*=\s*[0-9]+(?:\s|$)',line):
    for filename in expected:
     if json.dumps(filename) in line:expected[filename]+=1;successful_open_lines+=1
 need(all(expected.values()),'actual successful kernelslist.g/kernel-1.traceg opens missing')
 return {'status':'CLOSED_LOCAL_SYSCALL_INPUT_NETWORK_PROOF_PASS','syscall_log_sha256':sha(path),
  'successful_input_opens':expected,'no_connect':True,'no_ssh_exec':True,'traced_exec_calls':execs,'traced_fork_calls':forks,
  'model_pid':model_pid,'input_open_scope':'model and traced local descendant decompressor; actual successful open returns required'}
def resources(s,case,phase):
 m=load_frozen(s['resource_module_path'],s['resource_module_sha256'],'fresh_lifetime_resource')
 snap=None
 for _ in range(4):
  snap=m.snapshot(J,case,phase=phase,own_write_bytes=512*M,own_memory_cap_bytes=9*G)
  if snap['consistent_snapshot']:break
  time.sleep(.1)
 return snap
def require_resource(s,case,phase):
 r=resources(s,case,phase)
 need(r['consistent_snapshot'] and r['resource_pass'] and r['decision']=='PASS','RESOURCE_HOLD:'+json.dumps({k:r.get(k) for k in ('decision','free_bytes','required_bytes','host_RAM_deficit_bytes','cgroup_RAM_deficit_bytes','errors')}))
 return r
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write((json.dumps(v,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def put_same(p,v):
 p=P(p)
 if p.exists():need(read(p)==v,'immutable collision '+str(p))
 else:put(p,v)
def replace(p,v):
 p=P(p);tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex+'.tmp');put(tmp,v);os.replace(tmp,p)
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
@contextlib.contextmanager
def lease(path):
 f=P(path).open('a+b')
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);yield f
 finally:f.close()
@contextlib.contextmanager
def writer():
 # Same shared short writer primitive as peers; never acquire batch qualification.
 f=(REG.parent/'REGISTRY_UPDATE.lock').open('rb')
 try:fcntl.flock(f,fcntl.LOCK_EX);yield
 finally:f.close()
def mutate(case,tag,fn):
 with writer():
  reg=read(REG);epoch=read(EPOCH);oldsha=sha(REG);oldesh=sha(EPOCH)
  need(epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE' and epoch['holder']==os.uname().nodename and epoch['native_registry_sha256']==oldsha,'authority pair mismatch')
  before=copy.deepcopy(reg);fn(reg)
  # Own exact row and budget only; no peer or unrelated registry policy edits.
  oldrest=copy.deepcopy(before);newrest=copy.deepcopy(reg)
  oldrest['registered_future_requests'].pop(case,None);newrest['registered_future_requests'].pop(case,None)
  oldrest.pop('new_scientific_budget_remaining');newrest.pop('new_scientific_budget_remaining')
  need(oldrest==newrest,'attempted peer registry mutation')
  hist=REG.parent/'request_history';need(hist.is_dir(),'missing authority history directory')
  event_path=hist/(case+'.'+tag+'.'+uuid.uuid4().hex+'.json')
  tracker=J/'cases'/case/'control/OWN_SHARED_METADATA_PATHS.json'
  prior_tracker=read(tracker) if tracker.exists() else {'cohort':case,'paths':[]}
  need(prior_tracker['cohort']==case,'shared metadata tracker scope')
  prospective=[str(hist/(p.stem+'.'+h+'.json')) for p,h in ((REG,oldsha),(EPOCH,oldesh)) if not (hist/(p.stem+'.'+h+'.json')).exists()]+[str(event_path)]
  paths=list(dict.fromkeys(prior_tracker['paths']+prospective))
  need(len(paths)<=32,'own finite metadata history exceeded32 files')
  new_bytes=sum(p.stat().st_size+4096 for p,h in ((REG,oldsha),(EPOCH,oldesh)) if str(hist/(p.stem+'.'+h+'.json')) in prospective)+16384
  transient_atomic_bytes=len((json.dumps(reg,sort_keys=True,indent=2)+'\n').encode())+EPOCH.stat().st_size+65536
  need(metadata_footprint(J/'cases'/case)+new_bytes+transient_atomic_bytes<=16*M,'own shared journal/atomic temporary would exceed existing metadata16MiB envelope')
  replace(tracker,{'cohort':case,'paths':paths,'scope':'only immutable history files newly created by this own finite case; no peer cleanup'})
  for p,h in ((REG,oldsha),(EPOCH,oldesh)):
   dest=hist/(p.stem+'.'+h+'.json')
   if dest.exists():need(sha(dest)==h,'history collision')
   else:
    with dest.open('xb') as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
  replace(REG,reg)
  epoch=copy.deepcopy(epoch);epoch.update(native_registry_sha256=sha(REG),
   new_budget_remaining=reg['new_scientific_budget_remaining'],
   request_revision={'request_id':case,'operation':tag,'utc':now(),
    'prior_registry_sha256':oldsha,'prior_current_epoch_sha256':oldesh})
  replace(EPOCH,epoch)
  put(event_path,
   {'request':case,'operation':tag,'prior_registry_sha256':oldsha,'new_registry_sha256':sha(REG),
    'new_epoch_sha256':sha(EPOCH),'authorization_sha256':sha(J/'cases'/case/'control/USER_AUTHORIZATION.json')})
  return copy.deepcopy(reg['registered_future_requests'][case])
def identity():
 need(os.uname().nodename=='huangrulin-sshfs-174','wrong host')
 need(os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','wrong native mount namespace')
 need(P('/proc/sys/kernel/random/boot_id').read_text().strip()=='59e1e1a4-84b6-431f-ac2d-03e340207019','native boot drift')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(J)],text=True))['filesystems'][0]
 need(fs['fstype']=='ext4' and J.stat().st_dev==2128,'native ext4/device drift')
 return {'hostname':os.uname().nodename,'mount_namespace':os.readlink('/proc/self/ns/mnt'),
  'boot_id':P('/proc/sys/kernel/random/boot_id').read_text().strip(),'device':J.stat().st_dev,'filesystem':fs}
def current_assets(s,proof):
 mount=json.loads(subprocess.check_output(['findmnt','-J','-T',proof['native_mirror_mount_path']],text=True))['filesystems'][0]
 need(mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs','genuine164 source drift')
 need(P(proof['source_root']).resolve()==P(proof['native_mirror_mount_path']).resolve(),'input alias drift')
 for row in proof['members']:
  p=P(row['path']);t=p.stat()
  need([t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns]==row['identity'] and os.access(p,os.R_OK),'fresh input stat drift; separate fresh proof required; frozen spec never rewritten')
 return {'input_binding_sha256':s['input_binding_sha256'],'mount':mount,'members_stat_matched':len(proof['members'])}
def entry_route():
 candidate=J/'tools_v2/native_entry_candidate.sh';review=read(J/'control/NATIVE_ENTRY_CANDIDATE_ROUTING_REVIEW_V2.json')
 need(review['status']=='MAIN_REVIEWED_V2_BYTE_PRESERVING_ROUTING_PASS' and review['qualified_by']=='EP-MAIN','V2 routing review incomplete')
 need(sha(candidate)==review['candidate_sha256'] and sha(J/'tools_v2/prior_native_entry.sh')==review['prior_copy_sha256'],'frozen main routing candidate changed')
 data=(N/'bin/native').read_bytes();actual=hashlib.sha256(data).hexdigest()
 if actual==review['candidate_sha256']:
  return {'entry_sha256':actual,'candidate_sha256':review['candidate_sha256'],'mode':'EXACT_MAIN_CANDIDATE'}
 # Legal new peer prefixes are supported by a separate exact reviewed attestation.
 # A mere matching suffix is insufficient. Unknown prefix => HOLD; no rollback.
 path=J/'control'/('ENTRY_ROUTE_CONTINUATION_V2.'+actual+'.json');p=read(path)
 need(p['status']=='MAIN_REVIEWED_EXACT_PREFIX_DELEGATION_PASS' and p['qualified_by']=='EP-MAIN','unreviewed entry prefix')
 need(p['current_entry_sha256']==actual and p['retained_candidate_sha256']==sha(candidate),'continuation identity drift')
 offset=p['retained_candidate_offset'];need(type(offset) is int and offset>0 and data[offset:]==candidate.read_bytes(),'original candidate not exact suffix')
 need(p['prefix_sha256']==hashlib.sha256(data[:offset]).hexdigest() and p['new_exact_cohorts_reach_candidate'] is True,'prefix routing not reviewed')
 return {'entry_sha256':actual,'candidate_sha256':sha(candidate),'mode':'EXACT_REVIEWED_PEER_PREFIX',
  'continuation_review_path':str(path),'continuation_review_sha256':sha(path)}
def entry_required():
 need(os.environ.get('EP_TAG_LIFETIME_NATIVE_ENTRY')=='1','main exact sole-entry dispatcher required')
def qualification(case,s):
 p=J/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json';q=read(p)
 need(q['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED' and q['qualified_by']=='EP-MAIN','fresh native qualification missing')
 need(q['cohort']==case and q['source_identity']==IDENTITY and q['spec_sha256']==sha(J/'cases'/case/'control/FROZEN_SPEC.json'),'native Q scope drift')
 need(q['source_qualification_sha256']==SOURCEQ_SHA and q['runtime_module_sha256']==s['runtime_module_sha256'],'native Q engine drift')
 need(sha(q['actual_native_loading']['output_path'])==q['actual_native_loading']['output_sha256'],'help log drift')
 need(q['actual_native_loading']['full_trace_or_kernel_executed'] is False,'help scope violation')
 need(q['actual_native_loading'].get('producer_banner_verified') is True,'native Q lacks actual producer banner verification')
 help_text=P(q['actual_native_loading']['output_path']).read_text(errors='replace')
 need('gpgpu-sim_git-commit-11c02df' in help_text and 'accelsim-commit-9dd1ee57' in help_text,'stored actual help producer banner missing or stale')
 return q
def tree_bytes(root,limit=20000):
 root=P(root);total=0;count=0
 if not root.exists():return 0
 for parent,dirs,files in os.walk(root,followlinks=False):
  for d in dirs:need(not (P(parent)/d).is_symlink(),'unexpected directory link')
  for name in files:
   p=P(parent)/name;t=p.lstat();count+=1
   need(count<=limit and stat.S_ISREG(t.st_mode),'unbounded/nonregular output')
   total+=t.st_size
 return total
def footprint(root):
 root=P(root);logical=0;allocated=0;count=0
 if not root.exists():return 0
 for parent,dirs,files in os.walk(root,followlinks=False):
  for d in dirs:need(not (P(parent)/d).is_symlink(),'unexpected footprint directory link')
  for name in files:
   q=P(parent)/name;t=q.lstat();count+=1
   need(count<=20000 and stat.S_ISREG(t.st_mode),'unbounded/nonregular footprint')
   logical+=t.st_size;allocated+=t.st_blocks*512
 return max(logical,allocated)
def metadata_footprint(b):
 total=footprint(b/'env')+footprint(b/'control')+footprint(b/'run/log')
 tracker=b/'control/OWN_SHARED_METADATA_PATHS.json'
 if tracker.exists():
  data=read(tracker);need(data['cohort']==b.name and len(data['paths'])<=32,'metadata tracker scope/bound')
  for name in data['paths']:
   p=P(name);need(p.parent==REG.parent/'request_history','metadata path escaped shared history')
   if p.exists():
    t=p.lstat();need(stat.S_ISREG(t.st_mode),'shared metadata not regular')
    total+=max(t.st_size,t.st_blocks*512)
 return total
def operational_footprint(b,out=None):
 metadata=metadata_footprint(b);tmp=footprint(b/'run/tmp')+footprint(b/'run/cache')
 result=0 if out is None else footprint(out)
 need(metadata<=16*M,'env/control/help metadata cap16MiB')
 need(tmp<=128*M,'tmp/cache allocated aggregate cap128MiB')
 need(result<=112*M,'closed result allocated cap112MiB')
 return {'result_bytes':result,'metadata_env_help_bytes':metadata,'tmp_cache_bytes':tmp,
  'hot_total_bytes':result+metadata+tmp}
def engineering_resources():
 """Help-only actual headroom. No application admission/budget claims."""
 v=os.statvfs(J);mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 c=P('/sys/fs/cgroup');cur=int((c/'memory.current').read_text());maximum=(c/'memory.max').read_text().strip()
 ms={a:int(b) for a,b in (x.split() for x in (c/'memory.stat').read_text().splitlines())}
 clean=max(0,ms.get('file',0)-ms.get('shmem',0)-ms.get('file_mapped',0)-ms.get('file_dirty',0)-ms.get('file_writeback',0))
 credit=max(0,min(ms.get('inactive_file',0),clean)-8*G)
 head=None if maximum=='max' else int(maximum)-cur+credit
 need(v.f_bavail*v.f_frsize>8*G+256*M and v.f_favail>=100000,'bounded help disk HOLD')
 need(mem>=64*G+256*M and (head is None or head>=48*G+256*M),'bounded help RAM HOLD')
 return {'phase':'BOUNDED_NATIVE_HELP_ENGINEERING_ONLY','process_AS_cap_bytes':256*M,'wall_seconds':20,
  'free_bytes':v.f_bavail*v.f_frsize,'host_MemAvailable_bytes':mem,'cgroup_effective_headroom_bytes':head,
  'model_admission_granted':False}
def _prepare(case,engineering=False,launch_route=True):
 b,s,a,q,proof=validate_static(case);ident=identity();assets=current_assets(s,proof)
 need(s['host_cpu'] in os.sched_getaffinity(0),'qualified CPU unavailable')
 for kind,expected in [('core',IDENTITY['core_source_commit']),('framework',IDENTITY['framework_source_commit'])]:
  repo=P(s['source_worktrees'][kind])
  need(subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==expected,'source HEAD drift')
  need(not subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--untracked-files=no'],text=True).strip(),'tracked source changed')
 for i in range(4):
  need((b/'env'/('config-'+str(i)+'.config')).read_bytes()==(BASE/'env'/('config-'+str(i)+'.config')).read_bytes(),'original baseline config drift')
 operational_footprint(b)
 route=entry_route() if launch_route else None
 r=engineering_resources() if engineering else require_resource(s,case,'admission')
 return {'status':'PREPARED_ENGINEERING_ONLY_NO_APPLICATION_START' if engineering else 'PREPARED_NO_APPLICATION_START',
  'cohort':case,'spec_sha256':sha(b/'control/FROZEN_SPEC.json'),'identity':ident,'assets':assets,'entry_route':route,'resources':r}
def prepare(case):return _prepare(case)
def qualify(case):
 entry_required()
 with lease(J/'control/TWO_ARM_WHOLE_OPERATION.lock'),lease(J/'cases'/case/'control/CASE_RUN.lock'):
  prep=_prepare(case,True);b,s,*_=validate_static(case)
  p=b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'
  if p.exists():qualification(case,s);return read(p)
  need(not (b/'control/NATIVE_HELP_INTENT.json').exists(),'help already consumed; no retry')
  for d in ('run/log','run/tmp','run/cache','run/results','run/recovery'):(b/d).mkdir(parents=True,exist_ok=True)
  loader=N/'common-lib/ld-linux-x86-64.so.2'
  args=[str(loader),'--inhibit-cache','--library-path',str(N/'EP/env/lib'),s['binary_path'],'-h']
  log=b/'run/log/ELF_HELP.log'
  put(b/'control/NATIVE_HELP_INTENT.json',{'utc':now(),'argv':args,'max_invocations':1,'full_application':False,'engineering_resources':prep['resources']})
  env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','TMPDIR':str(b/'run/tmp'),'XDG_CACHE_HOME':str(b/'run/cache')}
  def limits():
   os.setsid();os.sched_setaffinity(0,{s['host_cpu']});os.setpriority(os.PRIO_PROCESS,0,10)
   rl.setrlimit(rl.RLIMIT_CORE,(0,0));rl.setrlimit(rl.RLIMIT_AS,(256*M,256*M));rl.setrlimit(rl.RLIMIT_FSIZE,(M,M))
  with log.open('xb') as f:
   cp=subprocess.Popen(args,cwd=b/'run/tmp',env=env,stdout=f,stderr=subprocess.STDOUT,preexec_fn=limits)
   try:rc=cp.wait(timeout=20)
   except subprocess.TimeoutExpired:os.killpg(cp.pid,signal.SIGKILL);cp.wait();raise Hold('help wall cap; no retry')
   f.flush();os.fsync(f.fileno())
  text=log.read_text(errors='replace')
  need(rc in (0,1) and ('usage' in text.lower() or 'option' in text.lower()),'actual help loading failed')
  need('gpgpu-sim_git-commit-11c02df' in text and 'accelsim-commit-9dd1ee57' in text,'actual help producer banner missing or stale')
  need('gpu_tot_sim_insn' not in text and 'kernel_name =' not in text,'help unexpectedly executed model')
  q={'status':'NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','qualified_by':'EP-MAIN','cohort':case,
   'source_identity':IDENTITY,'source_qualification_path':s['source_qualification_path'],'source_qualification_sha256':SOURCEQ_SHA,
   'spec_sha256':sha(b/'control/FROZEN_SPEC.json'),'runtime_module_sha256':s['runtime_module_sha256'],
   'native_identity':prep['identity'],'assets':prep['assets'],'entry_route':prep['entry_route'],
   'resources':prep['resources'],'expected_effective_options':{},'observer_env':s['observer_env'],
   'actual_native_loading':{'argv':args,'returncode':rc,'output_path':str(log),'output_sha256':sha(log),'simulator_help_invocations':1,'producer_banner_verified':True,'full_trace_or_kernel_executed':False},
   'scientific_acceptance_granted':False,'semantic_scope':'exact fresh same-new-source OFF/ON; full natural application and terminal checks remain required'}
  put(p,q);return q
def assert_off_closed():
 reg=read(REG);epoch=read(EPOCH);need(sha(REG)==epoch['native_registry_sha256'],'authority pair mismatch')
 row=reg['registered_future_requests'][OFF]
 need(row['state']=='CLOSED' and row['consumed']==1 and row['reserved_write_bytes']==0,'OFF not fully archive CLOSED reserve0')
 b,s,*_=validate_static(OFF);done,out=closed_done(OFF,s)
 point=read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
 need(point['status']=='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED' and point['raw_sha256']==done['raw_sha256'] and point['source_identity']==IDENTITY,'OFF scientific closure')
 need(row['accepted_point_sha256']==sha(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json'),'OFF accepted binding')
 for field in ('archive_receipt_path','independent_restore_path'):
  need(sha(row[field])==row[field.replace('_path','_sha256')],'OFF archive receipt drift')
 need(read(row['archive_receipt_path'])['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','OFF first restore incomplete')
 need(read(row['independent_restore_path'])['status']=='INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS','OFF second restore incomplete')
 return point
def _register(case):
 prep=_prepare(case);b,s,*_=validate_static(case);qualification(case,s)
 if case==ON:assert_off_closed()
 def f(reg):
  rows=reg['registered_future_requests']
  need(case not in rows,'exact case already registered; no refund/retry')
  other=ON if case==OFF else OFF
  if case==OFF:need(other not in rows,'ON registered before OFF')
  else:need(rows[OFF]['state']=='CLOSED' and rows[OFF]['reserved_write_bytes']==0,'OFF closure raced')
  row={'project':'EP_L2','owner':'EP-MAIN','state':'AUTHORIZED_UNUSED','budget':1,'remaining':1,'consumed':0,
   'pair_id':s['pair_id'],'pair_role':s['pair_role'],'automatic_retry':False,'refund':False,
   'reserved_write_bytes':s['advertised_peer_reservation_bytes'],'actual_write_restore_envelope_bytes':512*M,
   'shared_floor_compatibility_margin_bytes':3*G,'spec_path':str(b/'control/FROZEN_SPEC.json'),'spec_sha256':sha(b/'control/FROZEN_SPEC.json'),
   'authorization_path':str(b/'control/USER_AUTHORIZATION.json'),'authorization_sha256':sha(b/'control/USER_AUTHORIZATION.json'),
   'native_qualification_sha256':sha(b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json')}
  rows[case]=row;reg['new_scientific_budget_remaining']+=1
 row=mutate(case,'LIFETIME_FRESH_REGISTER',f)
 return {'status':'NEW_EXACT_FRESH_EP_REQUEST_REGISTERED','cohort':case,'row':row,'preparation':prep}
def register(case):
 entry_required();need(case in CASES,'exact cohort')
 with lease(J/'control/TWO_ARM_WHOLE_OPERATION.lock'),lease(J/'cases'/case/'control/CASE_RUN.lock'):return _register(case)
def info(pid):
 p=P('/proc')/str(pid);parts=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'parent_pid':int(parts[1]),'start_ticks':int(parts[19]),'process_state':parts[0],
  'boot_id':P('/proc/sys/kernel/random/boot_id').read_text().strip(),
  'mnt_namespace':os.readlink(p/'ns/mnt'),'exe':os.readlink(p/'exe'),
  'cmdline':(p/'cmdline').read_bytes().split(b'\0')[:-1],
  'environment':dict(x.split(b'=',1) for x in (p/'environ').read_bytes().split(b'\0') if b'=' in x),
  'maps':(p/'maps').read_text(),'limits':(p/'limits').read_text(),
  'affinity':sorted(os.sched_getaffinity(pid)),'nice':os.getpriority(os.PRIO_PROCESS,pid)}
def serializable_info(v):
 return {**v,'cmdline':[x.decode(errors='replace') for x in v['cmdline']],
  'environment':{a.decode():b.decode() for a,b in v['environment'].items()}}
def process_tree(pid):
 stack=[pid];seen=set()
 while stack:
  n=stack.pop()
  if n in seen:continue
  seen.add(n);need(len(seen)<=32,'unexpected process tree')
  p=P('/proc')/str(n)/'task'/str(n)/'children'
  try:stack += [int(x) for x in p.read_text().split()]
  except (FileNotFoundError,ProcessLookupError):pass
 return sorted(seen)
def rss(pid):
 try:return int(next(x.split()[1] for x in (P('/proc')/str(pid)/'status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
 except (FileNotFoundError,ProcessLookupError,StopIteration):return 0
def pid_generation_live(v):
 try:
  parts=(P('/proc')/str(v['pid'])/'stat').read_text().rsplit(')',1)[1].split()
  return int(parts[19])==v['start_ticks'] and parts[0] not in ('Z','X')
 except (FileNotFoundError,ProcessLookupError):return False
def verify_actual(v,s,args,env):
 need(v['mnt_namespace']=='mnt:[4026535153]' and v['boot_id']=='59e1e1a4-84b6-431f-ac2d-03e340207019','actual native domain drift')
 need(v['cmdline']==[x.encode() for x in args] and v['environment']=={k.encode():v.encode() for k,v in env.items()},'actual command/environment drift')
 need(v['affinity']==[16] and v['nice']==10,'actual CPU/nice drift')
 need(s['binary_path'] in v['maps'],'new ELF not mapped')
 need('/root/data/ep_l2_dtc_l1_native_v2/EP/src/' not in v['maps'],'protected old core unexpectedly mapped')
 mapped=[]
 for line in v['maps'].splitlines():
  fields=line.split(maxsplit=5)
  if len(fields)==6 and fields[5].startswith('/'):
   path=fields[5]
   if path.endswith(' (deleted)'):raise Hold('deleted mapped file')
   if path not in mapped:mapped.append(path)
 allowed={s['binary_path']:IDENTITY['binary_sha256']}
 # Exact loader/libs, old copies remain read-only runtime assets, not old Core.
 allowed.update({p:h for p,h in s['pinned_files'].items() if '/env/lib/' in p or '/common-lib/' in p})
 for path in mapped:need(path in allowed and sha(path)==allowed[path],'unqualified actual mapped ELF/library '+path)
 need('9663676416' in next(x for x in v['limits'].splitlines() if x.startswith('Max address space')),'actual AS cap drift')
 return {'mapped_file_sha256':{p:allowed[p] for p in mapped},'actual_environment_exact':True}
def closed_done(case,s):
 done=read(LED/(case+'.DONE.json'));intent=read(LED/(case+'.INTENT.json'));out=P(done['output'])
 need(out==J/'cases'/case/'run/results'/done['uuid'] and intent['uuid']==done['uuid'],'DONE exact output/UUID')
 need(done==read(out/'NATIVE_EXIT.json') and done['cohort']==case and done['new_attempt_consumed']==1,'DONE join')
 need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'natural exit0+native observation required')
 need(done['source_identity']==IDENTITY and done['spec_sha256']==sha(J/'cases'/case/'control/FROZEN_SPEC.json'),'DONE source/spec drift')
 need(intent['spec_sha256']==done['spec_sha256'] and intent['consumed_before_launcher_fork']==1,'intent identity mismatch')
 need(done['raw_sha256']==sha(out/'raw.log'),'closed raw drift')
 pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 need(not pid_generation_live(pid),'exact native model still alive')
 need(sha(out/'NATIVE_LAUNCH.json')==done['native_launch_sha256'] and sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')==done['native_pid_maps_sha256'],'actual launch identity drift')
 launch=read(out/'NATIVE_LAUNCH.json')
 need(launch['source_identity']==IDENTITY and launch['spec_sha256']==done['spec_sha256'] and launch['runtime_module_sha256']==s['runtime_module_sha256'],'actual launch scope mismatch')
 need(launch['launcher_argv']==launch['argv']==intent['launcher_argv']==intent['argv']==launch_command(s,out) and launch['model_argv']==intent['model_argv']==command(s,out) and launch['environment']==intent['environment']==environment(s,out),'actual launcher/model command/environment join')
 need(pid['cmdline']==launch['model_argv'] and pid['environment']==launch['environment'] and pid['actual_environment_exact'],'actual PID command/environment join')
 for name,item in launch['launch_capsule'].items():need(sha(out/name)==item['sha256'],'sealed launch capsule drift '+name)
 need(sha(out/'actual_file_process_network.log')==done['syscall_log_sha256'],'closed syscall log drift')
 need(syscall_proof(out/'actual_file_process_network.log',s,pid['pid'])==done['syscall_proof'],'closed syscall proof drift')
 return done,out
def seal_launch_capsule(b,s,out):
 need(not any(out.glob('config-*.config')),'output capsule already exists')
 env_paths={str(x) for x in (b/'env').iterdir() if x.is_file() and not x.is_symlink()}
 need(env_paths==set(s['env_hashes']) and len(env_paths)==9,'exact nine env inputs required')
 members={}
 for source,expected in s['env_hashes'].items():
  src=P(source);dst=out/src.name
  need(sha(src)==expected,'source env drift before seal')
  shutil.copy2(src,dst);need(sha(dst)==expected,'sealed env copy mismatch')
  members[dst.name]={'source':str(src),'sha256':expected}
 inputs={
  'FROZEN_SPEC.json':b/'control/FROZEN_SPEC.json',
  'USER_AUTHORIZATION.json':b/'control/USER_AUTHORIZATION.json',
  'SPEC_AUTHORIZATION_BINDING.json':b/'control/SPEC_AUTHORIZATION_BINDING.json',
  'NATIVE_PRELAUNCH_QUALIFICATION.json':b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',
  'SOURCE_QUALIFICATION_V2.json':P(s['source_qualification_path']),
  'RUNTIME_ARTIFACT_IDENTITY.json':P(s['runtime_artifact_identity_path']),
  'FRESH_INPUT_ASSET_BINDING.json':P(s['input_binding_path']),
  'RESULT_ENGINE_PIN.json':b/'control/RESULT_ENGINE_PIN.json'}
 for name,src in inputs.items():
  expected=sha(src);dst=out/name;shutil.copy2(src,dst);need(sha(dst)==expected,'launch evidence copy drift')
  members[name]={'source':str(src),'sha256':expected}
 put(out/'SOURCE_IDENTITY.json',IDENTITY)
 members['SOURCE_IDENTITY.json']={'sha256':sha(out/'SOURCE_IDENTITY.json')}
 need(tree_bytes(out)<M,'sealed metadata exceeds1MiB prelaunch bound')
 return members
def _launch(case):
 prep=_prepare(case);b,s,*_=validate_static(case);q=qualification(case,s)
 if case==ON:assert_off_closed()
 uid=str(uuid.uuid4());out=b/'run/results'/uid
 args=command(s,out);launcher_args=launch_command(s,out);env=environment(s,out)
 def consume(reg):
  row=reg['registered_future_requests'][case]
  need(row['state']=='AUTHORIZED_UNUSED' and row['consumed']==0 and row['remaining']==1 and row['budget']==1,'no exact fresh unused budget')
  need(row['spec_sha256']==sha(b/'control/FROZEN_SPEC.json') and row['authorization_sha256']==sha(b/'control/USER_AUTHORIZATION.json') and row['native_qualification_sha256']==sha(b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),'registered pins drift')
  need(reg['new_scientific_budget_remaining']>0 and not (LED/(case+'.INTENT.json')).exists(),'already consumed; no retry')
  out.mkdir(parents=True)
  put(LED/(case+'.INTENT.json'),{'cohort':case,'uuid':uid,'utc':now(),'output':str(out),
   'spec_sha256':sha(b/'control/FROZEN_SPEC.json'),'authorization_sha256':sha(b/'control/USER_AUTHORIZATION.json'),
   'source_identity':IDENTITY,'native_qualification_sha256':sha(b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),
   'argv':launcher_args,'launcher_argv':launcher_args,'model_argv':args,'environment':env,'consumed_before_launcher_fork':1,'new_attempt_consumed':1,'automatic_retry':False})
  row.update(state='CONSUMED_RUNNING_OR_UNRESOLVED',remaining=0,consumed=1,uuid=uid,output=str(out))
  reg['new_scientific_budget_remaining']-=1
 mutate(case,'LIFETIME_CONSUME_BEFORE_FORK',consume)
 # No model Popen has occurred above. Failures now retain consumed intent.
 rawpath=out/'raw.log';observed=None;reason=None;p=None;rc=None;start=time.monotonic()
 peak=0;peakrss=0;lastsample=-5;lastconsistent=0
 def limits():
  os.setsid();os.sched_setaffinity(0,{16});os.setpriority(os.PRIO_PROCESS,0,10)
  rl.setrlimit(rl.RLIMIT_CORE,(0,0));rl.setrlimit(rl.RLIMIT_AS,(9*G,9*G))
  rl.setrlimit(rl.RLIMIT_FSIZE,(128*M,128*M))
 try:
  with rawpath.open('xb') as raw,(out/'RESOURCE_SAMPLES.jsonl').open('xb') as samples:
   capsule=seal_launch_capsule(b,s,out)
   p=subprocess.Popen(launcher_args,cwd=out,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limits,bufsize=0)
   os.set_blocking(p.stdout.fileno(),False);sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
   put(out/'NATIVE_LAUNCH.json',{'utc':now(),'launcher_pid':p.pid,'argv':launcher_args,'launcher_argv':launcher_args,'model_argv':args,'environment':env,
    'identity':identity(),'prepared':prep,'source_identity':IDENTITY,'spec_sha256':sha(b/'control/FROZEN_SPEC.json'),
    'runtime_module_sha256':s['runtime_module_sha256'],'entry_route':prep['entry_route'],'launch_capsule':capsule,
    'limits':{'CPU':16,'nice':10,'AS_RSS_bytes':9*G,'wall_seconds':7200,'result_including_metadata_bytes':128*M,'closed_out_bytes':112*M,'env_control_help_bytes':16*M,'tmp_cache_bytes':128*M},
    'independent_EP_case_lease':True,'DTC_parent_lease_borrowed':False})
   eof=False
   while p.poll() is None or not eof:
    for key,_ in sel.select(.05):
     try:data=os.read(key.fd,65536)
     except BlockingIOError:continue
     if not data:eof=True;sel.unregister(key.fileobj);continue
     # Never write raw past remaining result cap; metadata retains1MiB headroom.
     current=footprint(out)
     if current+len(data)>111*M:reason='RESULT_CAP';break
     raw.write(data)
    if reason:break
    if observed is None:
     for child in process_tree(p.pid):
      if child==p.pid:continue
      try:
       v=info(child)
       if s['binary_path'] in v['maps']:
        proof=verify_actual(v,s,args,env);observed=serializable_info(v);observed.update(proof)
        put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',observed);break
      except (FileNotFoundError,ProcessLookupError):pass
    elapsed=time.monotonic()-start
    if elapsed-lastsample>=1:
     lastsample=elapsed;raw.flush()
     temp=footprint(b/'run/tmp')+footprint(b/'run/cache')
     result=footprint(out);metadata=metadata_footprint(b);total=result+temp+metadata;peak=max(peak,result)
     usedrss=sum(rss(n) for n in process_tree(p.pid));peakrss=max(peakrss,usedrss)
     r=resources(s,case,'runtime')
     row={k:r.get(k) for k in ('phase','decision','consistent_snapshot','disk_pass','RAM_pass','free_bytes','required_bytes','host_MemAvailable_bytes','cgroup_effective_headroom_bytes','resample_required','errors')}
     row.update(elapsed_seconds=elapsed,process_tree_RSS_bytes=usedrss,result_bytes=result,tmp_cache_bytes=temp)
     samples.write((json.dumps(row,sort_keys=True)+'\n').encode());samples.flush()
     if r['consistent_snapshot']:
      lastconsistent=elapsed
      if r['abort_recommended']:reason='STABLE_ACTUAL_RESOURCE_FLOOR'
     elif elapsed-lastconsistent>30:reason='RESOURCE_SNAPSHOT_UNSTABLE_30S'
     if temp>128*M:reason='TMP_CACHE_AGGREGATE_CAP'
     if result>111*M:reason='RESULT_CAP'
     if usedrss>9*G:reason='PROCESS_TREE_RSS_CAP'
     if metadata>16*M:reason='ENV_CONTROL_HELP_CAP'
     if total>256*M:reason='WHOLE_HOT_WRITE_CAP'
    if elapsed>7200:reason='WALL_CAP'
    if (b/'control/ABORT').exists():reason='EXPLICIT_OWN_ABORT'
    if p.poll() is not None and eof:break
   if reason and p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
   try:rc=p.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
   # On normal exit drain any remaining PIPE bytes with cap, not a new process.
   if reason is None and not eof:
    while True:
     try:data=os.read(p.stdout.fileno(),65536)
     except BlockingIOError:continue
     if not data:break
     if footprint(out)+len(data)>111*M:reason='RESULT_CAP';break
     raw.write(data)
   sel.close();p.stdout.close();raw.flush();os.fsync(raw.fileno());samples.flush();os.fsync(samples.fileno())
 except BaseException as e:
  reason=reason or 'LAUNCH_OR_MONITOR_EXCEPTION:'+type(e).__name__+':'+str(e)
 finally:
  if p is not None and p.poll() is None:
   os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
  # Child process tree must be gone after loader/model wait. No foreign kills.
  if observed and pid_generation_live(observed):
   reason=reason or 'NATIVE_GENERATION_STILL_LIVE'
   # A failed tracer may exit before its model. Kill only the exact observed
   # native generation still in this launch's private process group.
   if p is not None and os.getpgid(observed['pid'])==p.pid:
    os.killpg(p.pid,signal.SIGKILL)
    for _ in range(30):
     if not pid_generation_live(observed):break
     time.sleep(.1)
 syscalls=None
 if rc==0 and reason is None and observed:
  try:syscalls=syscall_proof(out/'actual_file_process_network.log',s,observed['pid'])
  except (Hold,OSError,ValueError) as e:reason='CLOSED_SYSCALL_GATE:'+str(e)
 receipt={'schema':'NATIVE_QUALIFICATION_EXECUTION_RECEIPT_V1','cohort':case,'uuid':uid,'output':str(out),
  'launcher_wait_returncode':rc,'stop_reason':reason,'elapsed_seconds':time.monotonic()-start,
  'native_simulator_observed':observed is not None,'peak_observed_rss_bytes':peakrss,'peak_result_logical_bytes':peak,
  'new_attempt_consumed':1,'automatic_retry':False,'source_disposition':'SOURCE_KEEP','source_identity':IDENTITY,
  'spec_sha256':sha(b/'control/FROZEN_SPEC.json'),'native_launch_sha256':sha(out/'NATIVE_LAUNCH.json') if (out/'NATIVE_LAUNCH.json').exists() else None,
  'native_pid_maps_sha256':sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json') if observed else None,
  'syscall_log_sha256':sha(out/'actual_file_process_network.log') if (out/'actual_file_process_network.log').exists() else None,'syscall_proof':syscalls,
  'raw_sha256':sha(rawpath) if rawpath.exists() else None,'scientific_acceptance':'PENDING_INDEPENDENT_NATIVE_EP_TERMINAL'}
 put(out/'NATIVE_EXIT.json',receipt);put(LED/(case+'.DONE.json'),receipt)
 def finish(reg):
  row=reg['registered_future_requests'][case];need(row['consumed']==1 and row['uuid']==uid,'own row drift')
  row.update(state='NATURAL_COMPLETE_PENDING_ACCEPTANCE_ARCHIVE' if rc==0 and reason is None and observed else 'STOP_UNACCEPTED_PENDING_ARCHIVE',
   done_sha256=sha(LED/(case+'.DONE.json')))
 mutate(case,'LIFETIME_NATURAL_OR_STOPPED_DONE',finish)
 return receipt

def acceptance_module(s):
 path=P(s['validation_module_path']);old_path=list(sys.path)
 expected=path.parent/'lifetime_parser.py'
 cached=sys.modules.get('lifetime_parser')
 if cached is not None:need(P(cached.__file__).resolve()==expected.resolve(),'foreign cached lifetime_parser')
 try:
  sys.path.insert(0,str(path.parent))
  m=load_frozen(path,s['validation_module_sha256'],'new_lifetime_application_validation')
  need(P(m.life.__file__).resolve()==expected.resolve(),'lifetime parser resolved outside pinned sibling')
  m.verify_pins()
  return m
 finally:sys.path[:]=old_path
def put_result(out,path,value):
 path=P(path);out=P(out)
 need(path.parent==out,'result metadata must be direct child')
 if path.exists():need(read(path)==value,'immutable result collision '+str(path));return
 encoded=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
 actual=footprint(out)
 need(actual+len(encoded)+4096<=112*M,'result metadata cap; no partial write')
 put(path,value)
def _accept(case):
 b,s,*_=validate_static(case);qualification(case,s);done,out=closed_done(case,s)
 row=read(REG)['registered_future_requests'][case]
 need(row['consumed']==1 and row['uuid']==done['uuid'] and row['done_sha256']==sha(LED/(case+'.DONE.json')),'accepted attempt registry join')
 pointpath=out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json'
 if pointpath.exists():
  p=read(pointpath)
  need(p['status']=='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED' and p['raw_sha256']==done['raw_sha256'] and p['source_identity']==IDENTITY,'existing accepted point collision')
  need(p['cohort']==case and p['uuid']==done['uuid'] and p['native_spec_sha256']==done['spec_sha256'] and p['native_done_sha256']==sha(LED/(case+'.DONE.json')),'existing point native identity drift')
  need(p['validation_bundle_sha256']==sha(out/'VALIDATED_APPLICATION_BUNDLE.json'),'existing validation bundle drift')

  if case==ON:
   ni=read(out/'OFF_ON_NONINTERFERENCE.json')
   need(ni['status']=='PASS_COMPLETE_OFF_ON_NONINTERFERENCE' and sha(out/'OFF_ON_NONINTERFERENCE.json')==p['noninterference_sha256'],'existing ON NI drift')
   for role,item in ni['normalized_semantics'].items():need(sha(item['path'])==item['sha256'],'snapshot drift')
  if row['state'] in ('ACCEPTED_PENDING_ARCHIVE','CLOSED'):
   need(row['accepted_point_sha256']==sha(pointpath),'registered accepted point drift');return p
 need(row['state']=='NATURAL_COMPLETE_PENDING_ACCEPTANCE_ARCHIVE','not natural pending acceptance')
 require_resource(s,case,'postrun')
 v=acceptance_module(s)
 bundle=v.validate_case(out/'raw.log',b/'control/FROZEN_SPEC.json',b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',
  P(s['source_qualification_path']),s['source_qualification_sha256'])
 need(bundle['status']=='NEW_SOURCE_APPLICATION_VALIDATED_PENDING_MAIN_ACCEPTANCE','complete numerical/observer validation failed')
 references={}
 if case==ON:
  assert_off_closed()
  ob,ospec,*_=validate_static(OFF);od,oo=closed_done(OFF,ospec)
  # Read-only revalidation; OFF out is already archived and immutable.
  off=v.validate_case(oo/'raw.log',ob/'control/FROZEN_SPEC.json',ob/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',
   P(ospec['source_qualification_path']),ospec['source_qualification_sha256'])
  pair=v.compare_pair(off,bundle)
  need(pair['noninterference']['status']=='PASS_COMPLETE_OFF_ON_NONINTERFERENCE','complete scoped OFF/ON NI failed')
  for role,snapshot in pair['normalized_snapshots'].items():
   path=out/('NORMALIZED_SEMANTICS_'+role+'.json');put_result(out,path,snapshot)
   references[role]={'path':str(path),'sha256':sha(path)}
  ni=copy.deepcopy(pair['noninterference']);ni['normalized_semantics']=references
  ni['accepted_by']='EP-MAIN';ni['scientific_acceptance_granted_by_C']=False
  put_result(out,out/'OFF_ON_NONINTERFERENCE.json',ni)
 # Every output write precedes archive manifest; never append to OFF frozen out.
 put_result(out,out/'VALIDATED_APPLICATION_BUNDLE.json',bundle)
 point={'status':'EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED','qualified_by':'EP-MAIN',
  'observer_header_sha256':'d88efa5012f1bd24c0b55be42504c1b8e3727bcabdf46a2c96385ee61082b8e1',
  'goal':'EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1','cohort':case,'uuid':done['uuid'],'source_identity':IDENTITY,'raw_sha256':done['raw_sha256'],
  'native_spec_sha256':sha(b/'control/FROZEN_SPEC.json'),'native_qualification_sha256':sha(b/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),
  'source_qualification_sha256':SOURCEQ_SHA,'native_done_sha256':sha(LED/(case+'.DONE.json')),
  'cycles':bundle['cycles'],'instructions':bundle['instructions'],'CTA':bundle['CTA'],'slices':bundle['slices'],
  'kernel_count':bundle['kernel_count'],'hardware_drained':bundle['hardware_drained'],'observer_enabled':bundle['observer_enabled'],
  'clock_domains_MHz':bundle['clock_domains_MHz'],'semantic_config_sha256':bundle['semantic_config_sha256'],
  'validation_bundle_sha256':sha(out/'VALIDATED_APPLICATION_BUNDLE.json'),
  'validation_module_sha256':s['validation_module_sha256'],'noninterference': 'PASS' if case==ON else 'PENDING_ON_NO_PAIR_CLAIM',
  'noninterference_sha256':sha(out/'OFF_ON_NONINTERFERENCE.json') if case==ON else None,
  'normalized_semantics':references,'source_disposition':'SOURCE_KEEP','old_acceptance_inherited':False,
  'claim_boundary':'frozen trace model only; CPU SourceQ alone does not establish application equivalence; pair evidence only when explicit PASS'}
 need(footprint(out)+len(json.dumps(point))<112*M,'accepted metadata exceeds result cap')
 put_result(out,pointpath,point)
 def f(reg):
  r=reg['registered_future_requests'][case];need(r['uuid']==done['uuid'] and r['consumed']==1,'own row join')
  r.update(state='ACCEPTED_PENDING_ARCHIVE',accepted_point_path=str(pointpath),accepted_point_sha256=sha(pointpath))
 mutate(case,'LIFETIME_ACCEPTED_PENDING_ARCHIVE',f)
 return point
def accept(case):
 entry_required();need(case in CASES,'exact cohort')
 with lease(J/'control/TWO_ARM_WHOLE_OPERATION.lock'),lease(J/'cases'/case/'control/CASE_RUN.lock'):return _accept(case)
def _archive(case):
 b,s,*_=validate_static(case);done,out=closed_done(case,s)
 accepted=_accept(case);row=read(REG)['registered_future_requests'][case]
 if row['state']=='CLOSED':
  need(row['reserved_write_bytes']==0 and row['accepted_point_sha256']==sha(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json'),'closed row drift')
  for key in ('archive_receipt','independent_restore'):
   need(sha(row[key+'_path'])==row[key+'_sha256'],'closed archive binding drift')
  return {'status':'CLOSED_REUSED_NO_NEW_OPERATION','row':row}
 need(row['state']=='ACCEPTED_PENDING_ARCHIVE' and row['reserved_write_bytes']>=512*M,'held guarantee missing')
 operational_footprint(b,out)
 require_resource(s,case,'postrun')
 tool=J/'tools_v2/archive_lifetime_results.py'
 need(str(tool) in s['pinned_files'],'archive helper absent from frozen pins')
 need(sha(tool)==s['pinned_files'][str(tool)],'archive helper drift')
 # Archive helper sets a384MiB process AS cap. Run as separate bounded subprocess,
 # keeping this runtime's data/NI decoder state and limits isolated.
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'}
 code="import importlib.util,json; p="+repr(str(tool))+";s=importlib.util.spec_from_file_location('lifetime_storage',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.archive("+repr(case)+")))"
 def limits():
  rl.setrlimit(rl.RLIMIT_AS,(384*M,384*M));rl.setrlimit(rl.RLIMIT_CORE,(0,0));os.setpriority(os.PRIO_PROCESS,0,10)
 cp=subprocess.run(['/usr/bin/python3','-B','-c',code],env=env,capture_output=True,text=True,timeout=1200,preexec_fn=limits)
 need(cp.returncode==0,'storage-only archive HOLD '+cp.stderr[-4000:])
 result=json.loads(cp.stdout);first=result['archive']['receipt'];second=result['independent_restore']
 need(first['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','first native restore incomplete')
 need(second['status']=='INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS' and second['runtime_or_controller_imported'] is False,'second native restore incomplete')
 ar=b/'control'/(case+'_ARCHIVE_RECEIPT.json');ir=b/'control/INDEPENDENT_NATIVE_TARGET_RESTORE.json'
 need(read(ar)==first and read(ir)==second,'archive receipt storage mismatch')
 target1=P(first['native_restore']);target2=P(second['target'])
 need(target1!=target2,'independent restore target alias')
 need(footprint(target1)<=128*M and footprint(target2)<=128*M,'native restore target cap')
 hot=operational_footprint(b,out)
 need(hot['hot_total_bytes']+footprint(target1)+footprint(target2)<=512*M,'whole operation cap')
 frozen_raw=sha(out/'raw.log')
 def f(reg):
  r=reg['registered_future_requests'][case]
  need(r['state']=='ACCEPTED_PENDING_ARCHIVE' and r['consumed']==1 and r['uuid']==done['uuid'],'closure ownrow phase drift')
  need(r['accepted_point_sha256']==sha(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json') and frozen_raw==done['raw_sha256'],'closure acceptance/raw drift')
  r.update(state='CLOSED',reserved_write_bytes=0,actual_write_restore_envelope_bytes=0,
   archive_receipt_path=str(ar),archive_receipt_sha256=sha(ar),
   independent_restore_path=str(ir),independent_restore_sha256=sha(ir),source_disposition='SOURCE_KEEP',
   closed_utc=now(),new_attempts_consumed=1,automatic_retry=False)
 mutate(case,'LIFETIME_ARCHIVE_CLOSED_RESERVE0',f)
 return {'status':'LIFETIME_APPLICATION_ARCHIVE_CLOSED_RESERVE0','cohort':case,'archive':result}
def archive(case):
 entry_required();need(case in CASES,'exact cohort')
 with lease(J/'control/TWO_ARM_WHOLE_OPERATION.lock'),lease(J/'cases'/case/'control/CASE_RUN.lock'):return _archive(case)
def run_native(case):
 """Single model attempt and complete accepted/archive lifecycle, locks held."""
 entry_required();need(case in CASES,'exact cohort')
 with lease(J/'control/TWO_ARM_WHOLE_OPERATION.lock'),lease(J/'cases'/case/'control/CASE_RUN.lock'):
  receipt=_launch(case)
  need(receipt['launcher_wait_returncode']==0 and receipt['stop_reason'] is None and receipt['native_simulator_observed'],'model did not naturally complete; consumed attempt retained, no retry')
  point=_accept(case);archived=_archive(case)
  return {'execution':receipt,'accepted':point,'archive':archived}
def status(case):
 need(case in CASES,'exact cohort')
 reg=read(REG);epoch=read(EPOCH)
 need(sha(REG)==epoch['native_registry_sha256'],'authority pair mismatch')
 row=reg['registered_future_requests'].get(case)
 phase='admission'
 if row and row.get('consumed')==1:
  phase='postrun' if row.get('state') in ('NATURAL_COMPLETE_PENDING_ACCEPTANCE_ARCHIVE','ACCEPTED_PENDING_ARCHIVE') else 'runtime'
 b,s,*_=validate_static(case)
 return {'cohort':case,'registered':row,'resources':resources(s,case,phase) if not row or row.get('state')!='CLOSED' else None,
  'actual_application_starts':int(bool(row and row.get('consumed')==1)),'old_budget_inherited':False}
def dispatch(operation,case):
 need(case in CASES,'unknown finite cohort')
 actions={'prepare':prepare,'qualify':qualify,'register':register,'run-native':run_native,'accept':accept,'archive':archive,'inspect':status,'status':status}
 need(operation in actions,'unsupported finite operation')
 return actions[operation](case)
if __name__=='__main__':
 # Main installs/imports this explicit draft only after independent code review
 # and freezing its final path/SHA in both specs. No self-install/entry mutation.
 import argparse
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('operation');a.add_argument('case',choices=CASES)
 x=a.parse_args()
 try:print(json.dumps(dispatch(x.operation,x.case),sort_keys=True,indent=2))
 except (Hold,OSError,ValueError,KeyError,TypeError) as e:
  print(json.dumps({'status':'HOLD_NO_AUTOMATIC_RETRY','error':str(e)}),file=sys.stderr);raise SystemExit(2)
