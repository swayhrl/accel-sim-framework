"""Finite exact streamcluster completion; external Root scope mandatory, no publisher/GPU."""
import pathlib,os,sys,json,time,fcntl,resource,socket,argparse,signal,subprocess,ctypes,re
from owned_runtime_v1 import *
import boundary_helpers_v1 as H
import selected_cpu248_v1 as M
import pipelined_protocol_v1 as P
D=pathlib.Path(__file__).resolve().parent
AUTH=M.AUTH
BOOT="import os,sys;f=int(sys.argv[1]);v=os.read(f,1);os.close(f);assert v==b'G';os.execv(sys.argv[2],sys.argv[2:])"
def canon(x):return M.canon(x)
def ref(p):return H.ref(pathlib.Path(p))
def loadref(r):return H.readref(r)
def save(p,x):write(p,x)
def phase(run,label,event,**detail):
 save(run/('PHASE_'+str(time.time_ns())+'.json'),dict(stage=label,event=event,unix=time.time(),monotonic=time.monotonic(),**detail))
def measured_resource(a,run):
 phase(run,'RESOURCE','START');v=H.resource_gate(a);phase(run,'RESOURCE','END');return v
def check_code(pin):
 need(sha(D/'CODE_MANIFEST.json')==pin,'external CodeID')
 for n,r in json.loads((D/'CODE_MANIFEST.json').read_text())['files'].items():need(sha(D/n)==r['sha256']and(D/n).stat().st_size==r['bytes'],'fresh exact code')
def rename_noreplace(a,b):
 # NOREPLACE archive publication, then retire only the exact original inode.
 # Source/Target writer OFDs protect this control namespace from other admitted writers.
 before=M.token(a);os.link(a,b,follow_symlinks=False)
 after=M.token(a);stable=lambda t:t[:4]+t[5:]
 need(stable(after)==stable(before)and sha(a)==sha(b),'source changed: keep both control names HOLD')
 if a.resolve().is_relative_to(P.CONTROL.resolve()):need(M.token(b)[:2]==before[:2],'Native hardlink identity required; NAS qualification inode projection not used')
 os.unlink(a)
def control_publish(raw,target):
 need(len(raw)<=65536,'finite Native control64KiB each')
 tmp=target.with_name(target.name+'.own_'+str(os.getpid())+'_'+str(time.time_ns())+'.tmp')
 fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  need(os.write(fd,raw)==len(raw),'full controlwrite');os.fchmod(fd,0o600);os.fsync(fd)
 finally:os.close(fd)
 os.link(tmp,target,follow_symlinks=False);tmp.unlink()
def validate_rows(rows,snapshot,qual,check,allowed_root):
 for row in rows:
  check();name=row['name'];need(name in snapshot['declared_order'],'frozen name')
  e=loadref(row['execution_ref']);r=e['result'];g=loadref(row['receipt_ref']);q=snapshot['per_kernel'][name]
  need(e['schema']=='SELECTED_CPU_POST_CLOSED_V2'and e['name']==name and e['qualification_only']is qual and e['observed_helper_exitcode']==0 and e['owned_session_empty']is True and e['postprocessor_sha256']==M.POST_SHA and e['original_f9_metadata']==snapshot['metadata'],'full actual execution closure')
  need(r==row['result']and all(g[k]==r[k]for k in ['source_sha256','grouped_sha256','grouped_bytes','records','ctas','warps','status','source_keep','closed_reopened_full_xz_crc']),'inner receipt result binding')
  need(r['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and r['source_sha256']==snapshot['known_raw_sha256'][name]and[r['records'],r['ctas'],r['warps']]==[q['records'],q['ctas'],q['warps']],'exact sourceSHA counts proof')
  p=pathlib.Path(row['grouped_path']);M.no_links(p);need(p.resolve().is_relative_to(allowed_root.resolve())and pathlib.Path(row['execution_ref']['path']).resolve().is_relative_to(allowed_root.resolve()),'closed output namespace')
  before=M.regular(p);need(M.payload_sha(p,check)==r['grouped_sha256']and p.stat().st_size==r['grouped_bytes']and M.token(p)==before,'current complete grouped fullSHA')
 return rows
def closed_batch(br,snapshot,qual,check,allowed_root):
 b=loadref(br);need(b['schema']=='STREAMCLUSTER_SELECTED_CPU_POST_BATCH_CLOSED_V2'and b['qualification_only']is qual and b['all_own_sessions_empty']is True and b['source_KEEP']is True,'actual closed batch only')
 names=b['processed_selected'];need(0<len(names)<=8 and len(set(names))==len(names)and not b['reused_names'],'strict complete selected batch')
 rows=b['per_kernel'];need({x['name']for x in rows}==set(names)and len(rows)==len(names),'exact batch names')
 validate_rows(rows,snapshot,qual,check,allowed_root);return b
def closed_seed_kernel(seed,snapshot,qual,check):
 z=loadref(seed['outer_closed_ref']);birth=loadref(seed['outer_owner_ref'])['owner']
 need(z['status']=='ALL_OWNED_CLOSED_BEFORE_LAST_FD_CLOSE'and M.ticks(birth[0])!=birth[1],'seed failed/successful parent allowned closed and original owner gone')
 e=loadref(seed['execution_ref']);root=pathlib.Path(seed['work_root']);need(pathlib.Path(seed['execution_ref']['path']).resolve().is_relative_to(root.resolve()),'seed exact work scope')
 row=dict(name=e['name'],result=e['result'],execution_ref=seed['execution_ref'],receipt_ref=seed['receipt_ref'],grouped_path=e['result']['grouped'],origin='CLOSED_KERNEL_PARENT_FAILED_ALL_OWNED_REAPED')
 validate_rows([row],snapshot,qual,check,root);return row
def retire(expected,runtime,tag):
 need(AUTH.exists(),'expected exact inner authority missing')
 g=loadref(expected);need(ref(AUTH)==expected,'same exact currently installed grant')
 raw=AUTH.read_bytes();need(len(raw)==expected['bytes']and hashlib.sha256(raw).hexdigest()==expected['sha256'],'retire exact original raw bytes')
 target=runtime/('RETIRED_AUTH_'+tag+'.raw.json')
 with target.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 need(sha(target)==expected['sha256'],'retained raw bytes SHA')
 dest=AUTH.with_name(AUTH.name+'.retired.'+tag)
 rename_noreplace(AUTH,dest)
 need(ref(dest)['sha256']==expected['sha256'],'retired original rawSHA; unknown mismatch HOLD')
 save(runtime/('RETIRED_NATIVE_'+tag+'.json'),dict(ref=ref(dest),original=expected,global_path_now_absent=not AUTH.exists()))
def fresh_owned_terminal(a,ad,leases):
 import fresh_terminal_probe_v1 as probe
 M.lease_check(leases);actual=probe.observe(os.getpid());save(ad/'FRESH_TERMINAL_RAW.json',actual);rr=ref(ad/'FRESH_TERMINAL_RAW.json')
 need(actual['closed']is True,'fresh original owned terminal; raw retained')
 e=loadref(a['terminal_base_ref']);t=e['terminal'];t.update(audit_age_seconds=0,observed_unix=actual['unix'],root_terminal_receipt_raw_sha256=rr['sha256'],root_terminal_receipt_ref=rr,root_did_not_reap_original=True,current_SOURCE_TARGET_owner=ident(os.getpid()))
 save(ad/'TERMINAL_EVIDENCE.json',e);return ref(ad/'TERMINAL_EVIDENCE.json')
def main():
 global AUTH
 p=argparse.ArgumentParser();p.add_argument('--scope',required=True);p.add_argument('--scope-sha',required=True);p.add_argument('--code-sha',required=True);p.add_argument('--qualification',action='store_true');x=p.parse_args()
 check_code(x.code_sha);scope=pathlib.Path(x.scope);a=loadref(dict(path=str(scope),bytes=scope.stat().st_size,sha256=x.scope_sha));qual=x.qualification
 need(a['schema']==('CPU_PRIVATE_COMPLETION_FIXTURE_V1'if qual else'ROOT_STREAMCLUSTER_COMPLETION_SCOPE_V1'),'disjoint authority')
 if qual:need(a['CPU_ONLY']is True and scope.resolve().is_relative_to((D/'fixtures').resolve()),'CPU private only')
 else:need(a['status']=='ROOT_APPROVED_PIPELINED_FINITE_COMPLETION_V1'and a['authorize_exact_dynamic_inner_grants']is True and scope.stat().st_uid==0 and scope.stat().st_mode&0o022==0,'external Root authorization')
 need(re.fullmatch('[A-Za-z0-9_]{1,80}',a['scope_id'])and a['code_sha256']==x.code_sha,'exact scope id code')
 need(a['host']==socket.gethostname()and a['boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'same Native hostboot')
 profile=a['selected_profile'];workers={'CPU2':2,'CPU4':4,'CPU8':8}[profile];need(profile in a['approved_profile_matrix']and a['approved_profile_matrix'][profile]['workers']==workers,'Root profile matrix')
 base=a['base_spec'];need(base['workers']==workers and len(base['cpu_ids'])==workers and a['approved_profile_matrix'][profile]['cpu_ids']==base['cpu_ids'],'fixed CPU profile')
 ownRAM=(4+3*workers)*2**30
 need(a['approved_profile_matrix'][profile]['worst_AS_bytes']==ownRAM,'outer2+runner2+Python/sort each1.5 perworker')
 if not qual:need(loadref(a['resource_ref'])['own_RAM_bytes']>=ownRAM,'full AS envelope')
 now=time.time();need(a['not_before_unix']<=now<a['original_72h_absolute_deadline_unix'],'unchanged absolute deadline')
 until=time.monotonic()+a['original_72h_absolute_deadline_unix']-now;wall=a['original_72h_absolute_deadline_unix']
 if not qual:need(loadref(a['original_deadline_authority_ref'])['original_72h_absolute_deadline_unix']==wall,'exact original deadline cannot extend')
 need(0<a['attempt_seconds']<=7200 and a['max_kernels_per_attempt']==8,'max8/2h')
 os.setpriority(os.PRIO_PROCESS,0,15);os.sched_setaffinity(0,set(base['cpu_ids']));resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));resource.setrlimit(resource.RLIMIT_CORE,(0,0));set_subreaper()
 if os.getsid(0)!=os.getpid():os.setsid()
 run=D/('fixtures'if qual else'runs')/a['scope_id'];run.mkdir(parents=True,exist_ok=True);M.no_links(run)
 if not qual:
  need(a['expected_initial_global_AUTH']=='ABSENT'and a['seed_authority_retirements']==[],'new scope expects no old global authority')
  if not list(run.glob('OWNER_*.json')):need(not pathlib.Path(a['private_inner_AUTH_path']).exists(),'initial private AUTH must remain absent; foreign KEEP')
 if qual:
  AUTH=pathlib.Path(a.get('fixture_shared_AUTH',str(run/'PRIVATE_AUTH.json')))
  need(AUTH.resolve().is_relative_to((D/'fixtures').resolve())and(AUTH.name=='PRIVATE_AUTH.json'or AUTH.name.startswith('SHARED_INNER_AUTH_')),'private CPU authority only')
 need(qual or pathlib.Path(base['source_root'])==M.PROD_ROOT,'fixed production source')
 snapshot=loadref(base['snapshot_ref']);need(a['frozen_order']==snapshot['declared_order']and base['reuse']==[],'fixed complete1611 matrix')
 scope_ref=dict(path=str(scope),bytes=scope.stat().st_size,sha256=x.scope_sha)
 if not qual:
  P.outer_admit(a,scope_ref,False,run);AUTH=pathlib.Path(a['private_inner_AUTH_path']);M.AUTH=AUTH
 stop=[False];fds=[];last_resource=[0.];term=[None]
 def stopped(sig,frame):stop[0]=True
 for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP):signal.signal(sig,stopped)
 def check():
  need(not stop[0]and time.time()<wall and time.monotonic()<until,'nonrenewed Rootwall+localmono')
  if not qual and time.monotonic()-last_resource[0]>=5:domain=P.periodic(a);phase(run,'LEASE_DOMAIN','PASS',evidence=domain);measured_resource(a,run);need(M.own_tree_size(run)<=base['own_output_limit_bytes'],'whole completion own NAS output cap');last_resource[0]=time.monotonic()
  if fds:M.lease_check(leases)
 try:
  if not qual:
   measured_resource(a,run)
  leasepaths={'RTX_SOURCE_174':str(run/'PRIVATE_SOURCE.lock'),'RTX_TARGET_174':str(run/'PRIVATE_TARGET.lock')}if qual else P.expected_asset_leases(a)
  leases=[]
  for role,sp in leasepaths.items():
   path=pathlib.Path(sp)
   if qual and not path.exists():save(path,{})
   fd=os.open(path,os.O_RDWR|os.O_CLOEXEC|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);fds.append(fd);leases.append(dict(role=role,path=str(path),fd=fd,identity=M.token(path),owner_pid=os.getpid(),owner_start_ticks=M.ticks(os.getpid())))
  save(run/('OWNER_'+str(time.time_ns())+'.json'),dict(owner=ident(os.getpid()),leases=leases,scope_sha256=x.scope_sha))
  phase(run,'CLOSED_ADOPTION','START');seen={};batchrefs=[]
  def accept(br,root):
   b=closed_batch(br,snapshot,qual,check,root)
   for row in b['per_kernel']:need(row['name']not in seen,'duplicate effective closed object');seen[row['name']]=row
   batchrefs.append(br)
  for br in a['seed_batch_refs']:accept(br,pathlib.Path(br['path']).parent)
  rootseed=None
  if a.get('seed_partial_parent_ref')is not None:
   rootseed=loadref(a['seed_partial_parent_ref']);need(rootseed['schema']=='ROOT_EXACT_CLOSED_POST_KERNEL_SEEDS_V1'and rootseed['job_id']==snapshot['job_id']and rootseed['source_snapshot_ref']['sha256']==base['snapshot_ref']['sha256']and rootseed['batch_complete']is False,'exact failed-parent kernel adoption authority')
   z=loadref(rootseed['outer_closed_ref']);loadref(rootseed['outer_failure_ref']);birth=loadref(a['seed_partial_parent_owner_ref'])['owner'];need(z['status']=='ALL_OWNED_CLOSED_BEFORE_LAST_FD_CLOSE'and M.ticks(birth[0])!=birth[1],'original parent dead and allowned closed')
   rows=rootseed['per_kernel'];validate_rows(rows,snapshot,qual,check,pathlib.Path(a['seed_partial_parent_work_root']))
   for row in rows:need(row['name']not in seen,'duplicate closed seed');seen[row['name']]=row
  for seed in a.get('seed_kernel_refs',[]):
   row=closed_seed_kernel(seed,snapshot,qual,check);need(row['name']not in seen,'duplicate effective seed kernel');seen[row['name']]=row
  initial_missing=[n for n in snapshot['declared_order']if n not in seen];derived_matrix=[initial_missing[i:i+8]for i in range(0,len(initial_missing),8)]
  matrix=derived_matrix if qual else a['approved_batch_matrix'];need(matrix==derived_matrix,'exact Root-approved remaining batch matrix')
  for p in sorted(run.glob('CLOSED_*.json')):
   rr=loadref(ref(p));need(rr['scope_sha256']==x.scope_sha,'own recovery scope');accept(rr['batch_ref'],pathlib.Path(rr['batch_ref']['path']).parent)
  # Crash after BATCH closure but before durable ledger may be recovered only from
  # exact own INTENT + actual runner closure, never from a partial output file.
  ledger_names={n for n in seen}
  for ad in sorted(run.glob('attempt_*')):
   intent=loadref(ref(ad/'ATTEMPT_INTENT.json'));need(intent['scope_sha256']==x.scope_sha,'own attempt intent')
   br=ref(ad/'payload/BATCH_CLOSED.json')if(ad/'payload/BATCH_CLOSED.json').exists()else None
   if br and all(n in ledger_names for n in intent['selected']):continue
   need(br is not None and(ad/'RUNNER_CLOSED.json').exists(),'unknown/failed previous attempt retained HOLD')
   z=loadref(ref(ad/'RUNNER_CLOSED.json'));need(z['status']=='OWNED_ALL_CLOSED_BEFORE_FD_COPIES_CLOSE'and M.ticks(z['owner'][0])!=z['owner'][1],'previous own runner gone+closed')
   accept(br,ad/'payload');ledger_names.update(intent['selected'])
   save(run/('CLOSED_recovered_'+ad.name+'.json'),dict(scope_sha256=x.scope_sha,batch_ref=br,recovered=True))
  if AUTH.exists():
   old=ref(AUTH);g=loadref(old)
   authorizations=a['seed_authority_retirements']
   match=next((r for r in authorizations if r['grant_ref']==old),None)
   if match:
    z=loadref(match['outer_closed_ref']);birth=loadref(match['outer_owner_ref'])['owner']
    need(z['status']=='ALL_OWNED_CLOSED_BEFORE_LAST_FD_CLOSE'and M.ticks(birth[0])!=birth[1]and (match.get('batch_ref')in a['seed_batch_refs']or match['outer_closed_ref']in [r['outer_closed_ref']for r in a.get('seed_kernel_refs',[])]or rootseed is not None and match['outer_closed_ref']==rootseed['outer_closed_ref'])and g['original_72h_absolute_deadline_unix']==wall,'seed exact owner gone+closed grant')
   else:
    need(g['completion_scope_raw_sha256']==x.scope_sha and pathlib.Path(g['work_root']).parent.parent==run,'foreign/unclosed grant cannot retire')
    work=pathlib.Path(g['work_root']);need(any(r['path']==str(work/'BATCH_CLOSED.json')for r in batchrefs)and(work.parent/'RUNNER_CLOSED.json').exists(),'own grant closed before retirement')
   retire(old,run,a['scope_id']+'_recovery_'+str(time.time_ns()))
  phase(run,'CLOSED_ADOPTION','END',closed_kernels=len(seen))
  while len(seen)<len(snapshot['declared_order']):
   check()
   stopfile=run/'STOP_AFTER_CURRENT_BATCH.json'
   if stopfile.exists():
    M.no_links(stopfile);z=loadref(ref(stopfile));need(z==dict(scope_sha256=x.scope_sha,stop_after_current_batch=True),'exact own boundary stop; unknown request HOLD')
    need(not AUTH.exists()and not children(ident(os.getpid())),'boundary only after grant retirement and owned closure')
    save(run/'STOPPED_AT_CLOSED_BATCH_BOUNDARY.json',dict(status='OWN_STOP_AT_CLOSED_BATCH_BOUNDARY',scope_sha256=x.scope_sha,closed_names=[n for n in snapshot['declared_order']if n in seen],remaining_names=[n for n in snapshot['declared_order']if n not in seen],all_own_sessions_closed=True,source_KEEP=True,private_AUTH_absent=True))
    return
   selected=[n for n in snapshot['declared_order']if n not in seen][:8];need(selected in matrix,'unapproved batch selection');ordinal=len(list(run.glob('attempt_*')));need(ordinal<=202,'finite maximum203 attempts including one failed retained');ad=run/('attempt_'+str(ordinal).zfill(4));ad.mkdir(exist_ok=False);work=ad/'payload'
   phase(run,'BATCH_ADMIT','START',ordinal=ordinal,selected=selected)
   spec=dict(base,selected=selected,leases=leases,pipelined_root_scope_ref=scope_ref,timeout_seconds=min(a['attempt_seconds'],max(1,int(wall-time.time()))))
   save(ad/'SPEC.json',spec)
   attempt_wall=min(wall,time.time()+a['attempt_seconds']);attempt_mono=min(until,time.monotonic()+a['attempt_seconds'])
   grant=dict(schema='ROOT_STREAMCLUSTER_PIPELINED_CPU_POST_V1',status='ROOT_APPROVED_REMAINING_BATCH_V1',spec_sha256=sha(ad/'SPEC.json'),code_manifest_sha256=x.code_sha,work_root=str(work),host=a['host'],boot_id=a['boot_id'],not_before_unix=time.time(),absolute_deadline_unix=attempt_wall,original_72h_absolute_deadline_unix=wall,resource_policy='NAS_ONLY_CPU248_AS1536M_FROZEN_ASSET_POST_V1',pipelined_root_scope_ref=scope_ref,terminal_evidence_ref=term[0],completion_scope_raw_sha256=x.scope_sha,owner=ident(os.getpid()),profile=profile)
   # Fresh readonly terminal reflects original absent workers, while current
   # SOURCE/TARGET locks now belong to this exact completion owner.
   if not qual:
    term[0]=a['frozen_source_proof_ref']
    grant['terminal_evidence_ref']=term[0]
    P.periodic(a)
   check();need(not AUTH.exists(),'foreign/stale authority cannot overwrite');control_publish(canon(grant),AUTH);gr=ref(AUTH);save(ad/'INNER_AUTHORITY_EXACT.json',grant)
   save(ad/'ATTEMPT_INTENT.json',dict(scope_sha256=x.scope_sha,selected=selected,spec_ref=ref(ad/'SPEC.json'),inner_grant_ref=gr,attempt_wall=attempt_wall,attempt_seconds=a['attempt_seconds'],owner=ident(os.getpid())))
   args=['--spec',str(ad/'SPEC.json'),'--spec-sha',sha(ad/'SPEC.json'),'--work',str(work)]
   args+=['--qualification']if qual else['--grant',str(AUTH),'--grant-sha',gr['sha256']]
   argv=[sys.executable,'-B',str(D/'selected_runner_v1.py'),'POST',str(D/'selected_cpu248_v1.py'),str(ad),json.dumps(fds),*args]
   rf,wf=os.pipe()
   with(ad/'stdout.log').open('xb')as out,(ad/'stderr.log').open('xb')as err:
    child=subprocess.Popen([sys.executable,'-B','-c',BOOT,str(rf),*argv],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,pass_fds=(*fds,rf),env=dict(PATH='/usr/bin:/bin',LC_ALL='C',TMPDIR=str(ad),PYTHONDONTWRITEBYTECODE='1'))
   phase(run,'BATCH_ADMIT','END',ordinal=ordinal);phase(run,'POST','START',ordinal=ordinal)
   os.close(rf);birth=ident(child.pid);need(birth,'owned runner birth')
   save(ad/'PROCESS_START_ACK.json',dict(owner=birth,argv=argv,unreleased=True,leases=leases));check();os.write(wf,b'G');os.close(wf)
   while child.poll()is None:
    check();need(time.time()<attempt_wall and time.monotonic()<attempt_mono,'fixed2h attempt');time.sleep(.05)
   child.wait();phase(run,'POST','END',ordinal=ordinal,returncode=child.returncode);phase(run,'BATCH_VERIFY','START',ordinal=ordinal);reap();need(not children(ident(os.getpid()))and child.returncode==0,'owned runner failed/unknown')
   close=loadref(ref(ad/'RUNNER_CLOSED.json'));need(close['status']=='OWNED_ALL_CLOSED_BEFORE_FD_COPIES_CLOSE','runner real closure')
   br=ref(work/'BATCH_CLOSED.json');accept(br,work)
   if qual and a.get('fixture_crash_after_batch_close')is True and ordinal==0:
    save(ad/'QUAL_BEFORE_LEDGER.json',dict(owner=ident(os.getpid()),CPU_ONLY=True))
    while time.time()<attempt_wall:time.sleep(.02)
    raise RuntimeError('CPU fixture crash marker timeout')
   save(run/('CLOSED_'+str(ordinal).zfill(4)+'.json'),dict(scope_sha256=x.scope_sha,batch_ref=br,runner_closed_ref=ref(ad/'RUNNER_CLOSED.json'),attempt_grant_ref=gr))
   need(not children(ident(os.getpid())),'retire only after true own closure')
   retire(gr,run,a['scope_id']+'_'+str(ordinal).zfill(4));phase(run,'BATCH_VERIFY','END',ordinal=ordinal,closed_kernels=len(seen))
  if (run/'COMPLETION_CLOSED.json').exists():
   old=loadref(ref(run/'COMPLETION_CLOSED.json'));need(old['scope_sha256']==x.scope_sha and old['ordered_names']==snapshot['declared_order'],'idempotent exact completed run');return
  save(run/'COMPLETION_CLOSED.json',dict(schema='EXACT_STREAMCLUSTER_POST_COMPLETION_CLOSED_V1',scope_sha256=x.scope_sha,ordered_names=snapshot['declared_order'],batch_refs=batchrefs,seed_kernel_refs=a.get('seed_kernel_refs',[]),seed_partial_parent_ref=a.get('seed_partial_parent_ref'),records=sum(seen[n]['result']['records']for n in seen),all_grouped_current_full_SHA_reopened=True,source_KEEP=True,archive_CURRENT_complete=False,qualified_GPU_science=False))
 except BaseException as error:
  stop[0]=True
  try:
   if children(ident(os.getpid())):cleanup(ident(os.getpid()))
   reap();need(not children(ident(os.getpid())),'unknown own cleanup')
   save(run/('FAILED_RETAINED_'+str(time.time_ns())+'.json'),dict(error=repr(error),partial_KEEP=True,inner_AUTH_KEEP=True))
  except BaseException as unknown:hold(run/'HOLD_UNKNOWN.json',unknown,fds)
  raise
 finally:
  try:need(not children(ident(os.getpid())),'unknown final own subtree')
  except BaseException as unknown:hold(run/'HOLD_FINAL_UNKNOWN.json',unknown,fds)
  for fd in fds:os.close(fd)
  save(run/('CONTROLLER_CLOSED_'+str(os.getpid())+'_'+str(time.time_ns())+'.json'),dict(status='ALL_OWNED_CLOSED_BEFORE_LAST_FD_CLOSE',owner=ident(os.getpid()),selected_success=(run/'COMPLETION_CLOSED.json').exists(),source_KEEP=True))
if __name__=='__main__':main()
