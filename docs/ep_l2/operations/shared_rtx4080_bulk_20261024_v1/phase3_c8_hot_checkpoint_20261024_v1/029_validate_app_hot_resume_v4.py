"""CPU-only complete-kernel validation; all NAS work is in supervised processes."""
import argparse,collections,csv,fcntl,hashlib,json,os,pathlib,shutil,signal,subprocess,sys,time,re
F9='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
F4='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
P55='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
NICE='6e3fd69addd6cff40185a406577b80ca03072588d593387a6a6ef73e9bc36348'
PRLIMIT='a63d6a3b741b085776716c55a23f763280b509095faf43e5d435af7191b5e3e7'
def save(p,o):
 assert not p.exists();tmp=p.with_name(p.name+'.tmp')
 with tmp.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def digest(p,rate_lock=None,dest=None,expected_size=None):
 h=hashlib.sha256();total=0
 with p.open('rb')as inp:
  out=dest.open('xb')if dest else None
  try:
   while True:
    if rate_lock:fcntl.flock(rate_lock,fcntl.LOCK_EX)
    try:
     start=time.monotonic();b=inp.read(2**20)
     if not b:break
     total+=len(b)
     if expected_size is not None:assert total<=expected_size,'source grew beyond reserved bounded copy'
     h.update(b)
     if out:out.write(b)
     if rate_lock:time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-start)))
    finally:
     if rate_lock:fcntl.flock(rate_lock,fcntl.LOCK_UN)
   if out:out.flush();os.fsync(out.fileno())
  finally:
   if out:out.close()
 if expected_size is not None:assert total==expected_size
 return h.hexdigest()
def localsha(p):return digest(p)
def names(root,ctx,stats):
 assert {p.name for p in(root/'traces').glob('kernelslist_ctx_*')}=={ctx.name}
 assert {p.name for p in(root/'traces').glob('stats_ctx_*')}=={stats.name}
 declared=[]
 for line in ctx.read_text().splitlines():
  name=line.strip()
  if not name or name.startswith('Memcpy'):continue
  assert pathlib.PurePosixPath(name).name==name and name.startswith('kernel-')and name.endswith('.trace.xz')
  declared.append(name)
 assert declared and len(set(declared))==len(declared)
 assert {p.name for p in(root/'traces').glob('kernel*.trace.xz')}==set(declared)
 context={re.search(r'ctx_(0x[0-9a-fA-F]+)',n).group(1)for n in declared};assert len(context)==1
 assert ctx.name=='kernelslist_ctx_'+next(iter(context))and stats.name=='stats_ctx_'+next(iter(context))
 with stats.open()as f:rows=list(csv.reader(f))
 header=rows[0];rows=[r for r in rows[1:]if r];assert [r[0].strip()for r in rows]==declared
 return declared,header,dict(zip(declared,rows))
def plan(a):
 root=pathlib.Path(a.root).resolve();work=pathlib.Path(a.work);mapfile=pathlib.Path(a.map).resolve();parser=pathlib.Path(a.parser);helper=pathlib.Path(a.helper)
 assert localsha(helper)==F9 and localsha(parser)==F4
 assert localsha(pathlib.Path('/usr/bin/nice'))==NICE and localsha(pathlib.Path('/usr/bin/prlimit'))==PRLIMIT
 execution=json.loads((root/'EXECUTION.json').read_text());m=json.loads(mapfile.read_text())
 assert execution['exit_code']==0 and execution['binary_sha256']==m['binary_sha256']and execution['tool_sha256']==P55
 ctx=list((root/'traces').glob('kernelslist_ctx_*'));stats=list((root/'traces').glob('stats_ctx_*'));assert len(ctx)==len(stats)==1;ctx=ctx[0];stats=stats[0]
 declared,header,rows=names(root,ctx,stats)
 proof=pathlib.Path(a.raw_manifest);assert localsha(proof)==a.raw_manifest_sha256
 source=json.loads(proof.read_text());entries=source.get('raw_members',source.get('files'));assert isinstance(entries,list)
 known={}
 for x in entries:
  p=pathlib.PurePosixPath(x['path'])
  if len(p.parts)==2 and p.parts[0]=='traces'and p.name in declared:
   assert p.name not in known;known[p.name]=x
 assert set(known)==set(declared),'frozen source/committed manifest exact raw set'
 fingerprints={}
 for name in declared:
  p=root/'traces'/name;s=p.stat();x=known[name];assert s.st_size==x['bytes']
  if 'mtime_ns'in x:assert s.st_mtime_ns==x['mtime_ns']
  fingerprints[name]=[s.st_size,s.st_mtime_ns,x['sha256']]
 controls={str(p):localsha(p)for p in [root/'EXECUTION.json',mapfile,ctx,stats]}
 original=helper.read_text();needle="H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')";assert original.count(needle)==1
 portable=work/'delegated_validator_portable.py';portable.write_text(original.replace(needle,'H=pathlib.Path('+repr(str(parser))+')'))
 cache={}
 if a.reuse_manifest:
  cp=pathlib.Path(a.reuse_manifest);assert localsha(cp)==a.reuse_manifest_sha256
  cm=json.loads(cp.read_text());assert cm['root']==str(root)and cm['source_control_files']==controls
  assert cm['schema']=='ADA7_EXACT_CLOSED_KERNEL_RECEIPT_CACHE_V1'and cm['map_sha256']==localsha(mapfile)
  assert cm['delegated_original_validator_sha256']==F9 and cm['frozen_parser_sha256']==F4 and cm['delegated_portable_validator_sha256']==localsha(portable)
  for row in cm['kernels']:
   assert row['name']in declared and row['name']not in cache
   assert row['raw_fingerprint']==fingerprints[row['name']];cache[row['name']]=row
 save(work/'PLAN.json',{'root':str(root),'map':str(mapfile),'map_sha256':localsha(mapfile),'parser':str(parser),'portable':str(portable),'portable_sha256':localsha(portable),'ctx':str(ctx),'stats':str(stats),'header':header,'statrows':rows,'declared':declared,'fingerprints':fingerprints,'source_controls':controls,'cache':cache,'source_fullSHA_provenance':{'manifest':str(proof),'sha256':localsha(proof)},'helper_sha256':F9,'parser_sha256':F4,'source_KEEP':True})
def pinned(plan):
 assert localsha(pathlib.Path(plan['portable']))==plan['portable_sha256']and localsha(pathlib.Path(plan['parser']))==F4
 assert localsha(pathlib.Path('/usr/bin/nice'))==NICE and localsha(pathlib.Path('/usr/bin/prlimit'))==PRLIMIT
def qcheck(q,n,plan):
 assert q['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and q['kernels']==1 and q['all_declared_warps_terminate']
 assert q['kernel_commandlist_exact_set']and q['stats_record_counts_match']and q['capture_map_binary_binding']and q['strict_single_stream_ordinary']
 assert q['map_sha256']==plan['map_sha256']and q['frozen_parser_sha256']==F4 and q['validator_sha256']==plan['portable_sha256']
 assert len(q['source_files'])==1 and next(iter(q['source_files'].values()))==plan['fingerprints'][n][2]
 assert len(q['per_kernel'])==1 and q['per_kernel'][0]['name']==n and q['counts']['sass_records']==int(plan['statrows'][n][-1])
def kernel(a):
 work=pathlib.Path(a.work);plan=json.loads((work/'PLAN.json').read_text());pinned(plan);n=a.name;assert n in plan['declared']
 root=pathlib.Path(plan['root']);raw=root/'traces'/n;finger=plan['fingerprints'][n];r=work/'kernels'/n.replace('.trace.xz','');r.mkdir(parents=True)
 lock=open(work/'AGGREGATE_NAS_READ.lock','a');assert [raw.stat().st_size,raw.stat().st_mtime_ns]==finger[:2]
 row=plan['cache'].get(n);hot=None;stage='NEW_F9_PROCESS_OBSERVED_EXIT0'
 if row:
  assert digest(raw,lock,expected_size=finger[0])==finger[2]
  for path,h in row['proof_files'].items():assert localsha(pathlib.Path(path))==h
  q=json.loads(pathlib.Path(row['receipt']).read_text());assert q==json.loads(pathlib.Path(row['stdout']).read_text());qcheck(q,n,plan)
  v=pathlib.Path(row['receipt']).parent;assert(v/'EXECUTION.json').read_bytes()==(root/'EXECUTION.json').read_bytes()
  assert(v/'traces'/pathlib.Path(plan['ctx']).name).read_text()==n+'\n'
  with(v/'traces'/pathlib.Path(plan['stats']).name).open()as f:assert list(csv.reader(f))==[plan['header'],plan['statrows'][n]]
  assert (v/'traces'/n).resolve()==raw.resolve()
  stage='TERMINAL_RESULT_ADOPTION_OLD_EXIT_NOT_SEPARATELY_RECORDED'
 else:
  hot=work/'hot'/n;assert finger[0]<a.hot_limit
  # Native advisory reservation enforces the sum of all controlled expected copy sizes.
  reslock=open(work/'HOT_RESERVATIONS.lock','a');fcntl.flock(reslock,fcntl.LOCK_EX)
  try:
   reservations=json.loads((work/'HOT_RESERVATIONS.json').read_text());assert n not in reservations
   assert sum(reservations.values())+finger[0]<=a.hot_limit
   reservations[n]=finger[0];tmp=work/'HOT_RESERVATIONS.tmp';tmp.write_text(json.dumps(reservations));os.replace(tmp,work/'HOT_RESERVATIONS.json')
  finally:fcntl.flock(reslock,fcntl.LOCK_UN)
  assert digest(raw,lock,hot,finger[0])==finger[2]and localsha(hot)==finger[2]
  (r/'traces').mkdir();(r/'EXECUTION.json').write_bytes((root/'EXECUTION.json').read_bytes());(r/'traces'/pathlib.Path(plan['ctx']).name).write_text(n+'\n');(r/'traces'/n).symlink_to(hot)
  with(r/'traces'/pathlib.Path(plan['stats']).name).open('x',newline='')as f:csv.writer(f).writerows([plan['header'],plan['statrows'][n]])
  with(r/'stdout.log').open('x')as out,(r/'stderr.log').open('x')as err:
   # Same PGID as supervised kernel worker; no nested session may escape its guard.
   cp=subprocess.run(['/usr/bin/nice','-n','15','/usr/bin/prlimit','--as='+str(1536*2**20),'--','python3','-B',plan['portable'],str(r),plan['map']],stdout=out,stderr=err)
  assert cp.returncode==0,('new delegated process exit',cp.returncode)
  q=json.loads((r/'stdout.log').read_text());qcheck(q,n,plan)
  assert localsha(hot)==finger[2]
  save(r/'F9_OBSERVED_EXIT0.json',{'returncode':cp.returncode,'f9_original_sha256':F9,'portable_sha256':plan['portable_sha256'],'parser_sha256':F4})
 assert [raw.stat().st_size,raw.stat().st_mtime_ns]==finger[:2];pinned(plan)
 save(r/'CANDIDATE.json',{'name':n,'result':q,'validation_provenance':stage,'old_exit_not_separately_recorded':bool(row),'raw_fingerprint':finger,'hot_path':str(hot)if hot else None,'hot_sha256':finger[2]if hot else None,'map_sha256':plan['map_sha256'],'worker_sha256':localsha(pathlib.Path(__file__)),'source_KEEP':True})
def final(a):
 work=pathlib.Path(a.work);plan=json.loads((work/'PLAN.json').read_text());root=pathlib.Path(plan['root']);pinned(plan)
 declared,header,rows=names(root,pathlib.Path(plan['ctx']),pathlib.Path(plan['stats']));assert declared==plan['declared']and header==plan['header']and rows==plan['statrows']
 for p,h in plan['source_controls'].items():assert localsha(pathlib.Path(p))==h
 lock=open(work/'AGGREGATE_NAS_READ.lock','a');counts=collections.Counter();per=[];streams=set();ctas=warps=adopted=0
 for n in declared:
  p=root/'traces'/n;finger=plan['fingerprints'][n];assert[p.stat().st_size,p.stat().st_mtime_ns]==finger[:2];assert digest(p,lock,expected_size=finger[0])==finger[2];assert[p.stat().st_size,p.stat().st_mtime_ns]==finger[:2]
  r=work/'kernels'/n.replace('.trace.xz','');complete=json.loads((r/'COMPLETE.json').read_text());assert complete['observed_worker_returncode']==0
  assert localsha(r/'CANDIDATE.json')==complete['candidate_sha256'];candidate=json.loads((r/'CANDIDATE.json').read_text());q=candidate['result'];qcheck(q,n,plan)
  counts.update(q['counts']);per+=q['per_kernel'];streams.update(q['stream_ids']);ctas+=q['ctas'];warps+=q['warps'];adopted+=candidate['old_exit_not_separately_recorded']
 assert len(streams)==1
 assert {p.name for p in(root/'traces').glob('kernel*.trace.xz')}==set(declared)
 for p,h in plan['source_controls'].items():assert localsha(pathlib.Path(p))==h
 pinned(plan)
 result={'schema':'ADA7_HOT_WINDOW_PARALLEL_RESUME_VALIDATION_V4','status':'ADA7_ORDINARY_FULL_RECORD_PASS','kernels':len(declared),'ctas':ctas,'warps':warps,'counts':dict(counts),'per_kernel':per,'stream_ids':sorted(streams),'context_count':1,'all_declared_warps_terminate':True,'kernel_commandlist_exact_set':True,'stats_record_counts_match':True,'source_files':{str(root/'traces'/n):plan['fingerprints'][n][2]for n in declared},'source_control_files':plan['source_controls'],'map_sha256':plan['map_sha256'],'capture_map_binary_binding':True,'validator_sha256':localsha(pathlib.Path(__file__)),'delegated_original_validator_sha256':F9,'delegated_portable_validator_sha256':plan['portable_sha256'],'frozen_parser_sha256':F4,'reused_terminal_results_old_exit_not_separately_recorded':adopted,'observed_exit0_COMPLETE_per_current_worker':True,'all_NAS_IO_in_supervised_processes':True,'aggregate_NAS_large_read_bytes_per_sec':15*2**20,'hot_window_reserved_limit_bytes':a.hot_limit,'no_GPU_execution':True,'source_KEEP':True}
 save(pathlib.Path(a.output),result)
def proc(pid):
 p=pathlib.Path('/proc',str(pid));s=(p/'stat').read_text().split(') ',1)[1].split();return {'pid':pid,'ticks':s[19],'pgid':int(s[2]),'rss':int(s[21])*4096}
def descendants(pid):
 result={};todo=[pid]
 while todo:
  n=todo.pop()
  if n in result:continue
  try:
   result[n]=proc(n)
   for t in pathlib.Path('/proc',str(n),'task').iterdir():
    try:todo.extend(map(int,(t/'children').read_text().split()))
    except FileNotFoundError:pass
  except (FileNotFoundError,ProcessLookupError):pass
 return list(result.values())
def controller(a):
 def interrupted(signum,frame):raise InterruptedError('supervisor received signal '+str(signum))
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 work=pathlib.Path(a.work);assert not work.exists()and not pathlib.Path(a.output).exists();work.mkdir(parents=True);(work/'hot').mkdir();save(work/'HOT_RESERVATIONS.json',{})
 assert a.max_workers in(1,2,8,16)and a.hot_limit<=4*2**30
 deadline=time.time()+a.deadline;active={};known={};peak=0;peakrss=0
 # Every phase, including preflight and final NAS SHA, is guarded with a real process group.
 def launch(mode,name=None):
  cmd=[sys.executable,'-B',str(pathlib.Path(__file__).resolve()),*sys.argv[1:],'--mode',mode]
  if name:cmd+=['--name',name]
  label=mode+'_'+(name or 'app');f=(work/(label+'.log')).open('x');p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close();active[p.pid]=(p,proc(p.pid),name,mode);return p
 def guard():
  nonlocal peak,peakrss
  ps=descendants(os.getpid());rss=sum(x['rss']for x in ps);peakrss=max(peakrss,rss)
  for x in ps:known[x['pid']]=x
  with(work/'RESOURCE_EVENTS.jsonl').open('a')as f:f.write(json.dumps({'unix':time.time(),'rss':rss,'processes':ps,'active_workers':len(active)})+'\n')
  assert time.time()<deadline,'whole workflow deadline'
  assert rss<16*2**30,'aggregate recursive RSS polled threshold'
  assert shutil.disk_usage(work).free>a.free_floor,'free SSD includes foreign reservations'
  hot=sum(p.stat().st_size for p in(work/'hot').iterdir()if p.is_file());assert hot<=a.hot_limit,'total actual controlled hot files'
 def wait_phase(p):
  while p.poll()is None:guard();time.sleep(.5)
  active.pop(p.pid);assert p.returncode==0,('phase failed',p.args,p.returncode)
 try:
  wait_phase(launch('plan'));plan=json.loads((work/'PLAN.json').read_text());pending=list(plan['declared'])
  while pending or active:
   while pending and len(active)<a.max_workers:launch('kernel',pending.pop(0));peak=max(peak,len(active))
   guard()
   for pid,(p,identity,name,mode)in list(active.items()):
    if p.poll()is None:continue
    active.pop(pid);assert p.returncode==0,(name,'worker failed',p.returncode)
    r=work/'kernels'/name.replace('.trace.xz','');q=json.loads((r/'CANDIDATE.json').read_text());assert q['name']==name
    # This COMPLETE is written only after the controller actually observes exit0.
    save(r/'COMPLETE.json',{'observed_worker_pid':pid,'observed_worker_start_ticks':identity['ticks'],'observed_worker_returncode':p.returncode,'candidate_sha256':localsha(r/'CANDIDATE.json'),'utc_unix':time.time()})
    if q['hot_path']:
     hot=pathlib.Path(q['hot_path']);assert hot.parent==work/'hot'and hot.name==name;size=hot.stat().st_size;hot.unlink()
     with(work/'HOT_RESERVATIONS.lock').open('a')as f:
      fcntl.flock(f,fcntl.LOCK_EX);res=json.loads((work/'HOT_RESERVATIONS.json').read_text());assert res.pop(name)==size;tmp=work/'HOT_RESERVATIONS.tmp';tmp.write_text(json.dumps(res));os.replace(tmp,work/'HOT_RESERVATIONS.json')
     save(r/'HOT_CLEANUP.json',{'path':str(hot),'bytes':size,'sha256':q['hot_sha256'],'validated_against_true164_source_SHA_before_release':True,'released_temporary_read_buffer_only':True,'source_KEEP':True})
   time.sleep(.25)
  wait_phase(launch('final'))
  save(work/'CONTROLLER_COMPLETE.json',{'observed_all_phase_returncodes':0,'peak_kernel_workers':peak,'aggregate_recursive_RSS_peak_bytes':peakrss,'hot_limit_bytes':a.hot_limit,'free_floor_bytes':a.free_floor,'polled_RSS_free_not_quota':True,'validator_sha256':localsha(pathlib.Path(__file__)),'output_sha256':localsha(pathlib.Path(a.output)),'no_GPU_execution':True})
 except BaseException as e:
  # TERM/KILL every still exact own group, including original-f9 descendants.
  for sig in(signal.SIGTERM,signal.SIGKILL):
   groups=set()
   for x in known.values():
    try:
     now=proc(x['pid'])
     if now['ticks']==x['ticks']and now['pgid']==x['pgid']and x['pid']!=os.getpid():groups.add(x['pgid'])
    except (FileNotFoundError,ProcessLookupError):pass
   for p,identity,_,_ in active.values():
    if p.poll()is None:groups.add(identity['pgid'])
   for pgid in groups:
    assert pgid!=os.getpgrp()
    try:os.killpg(pgid,sig)
    except ProcessLookupError:pass
   time.sleep(3)
  unresolved=[]
  for x in known.values():
   if x['pid']==os.getpid():continue
   try:
    now=proc(x['pid'])
    if now['ticks']==x['ticks']:unresolved.append(now)
   except (FileNotFoundError,ProcessLookupError):pass
  save(work/'FAILURE.json',{'status':'FAILED_RETAINED_NO_COMPLETE','error':repr(e),'own_processes_not_yet_reaped_or_signal_pending':unresolved,'source_KEEP':True});raise
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('map');ap.add_argument('--helper',required=True);ap.add_argument('--parser',required=True);ap.add_argument('--work',required=True);ap.add_argument('--output',required=True);ap.add_argument('--raw-manifest',required=True);ap.add_argument('--raw-manifest-sha256',required=True);ap.add_argument('--reuse-manifest');ap.add_argument('--reuse-manifest-sha256');ap.add_argument('--max-workers',type=int,default=8);ap.add_argument('--hot-limit',type=int,default=4*2**30);ap.add_argument('--free-floor',type=int,default=9*2**30);ap.add_argument('--deadline',type=int,default=86400);ap.add_argument('--mode',choices=['controller','plan','kernel','final'],default='controller');ap.add_argument('--name');a=ap.parse_args()
 assert pathlib.Path(a.work).is_absolute();{'controller':controller,'plan':plan,'kernel':kernel,'final':final}[a.mode](a)
if __name__=='__main__':main()
