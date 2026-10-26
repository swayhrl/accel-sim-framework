#!/usr/bin/env python3
"""Finite ordinary whole-job CPU2 candidate. No GPU, publication or lease acquisition."""
import sys
if sys.flags.optimize:raise RuntimeError('OPTIMIZED_PYTHON_UNSUPPORTED')
import pathlib,os,json,hashlib,collections,csv,re,time,struct,resource,signal,multiprocessing,traceback,math
from multiprocessing.connection import wait
from frozen_loader_v1 import load,VALIDATOR_SHA,HELPER_SHA,PRE
from shared_io_v1 import Pace,OpenGuard,read_bytes,token,verify_lease,need,ticks,MIB
HERE=pathlib.Path(__file__).resolve().parent
PROFILE='ORDINARY_WHOLEJOB_VALIDATOR_CPU2_CANDIDATE_V1'
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,value):
 raw=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
 with pathlib.Path(p).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def child_loop(conn,indexes,cfg):
 for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,signal.SIG_DFL)
 os.close(cfg['parent_pace_fd'])
 os.setpriority(os.PRIO_PROCESS,0,15);os.sched_setaffinity(0,cfg['affinity'])
 resource.setrlimit(resource.RLIMIT_AS,(2**31,2**31));pace=Pace(cfg['pace'],cfg['rate'],cfg['deadline'],cfg['lease'])
 checker=load()
 try:
  for ix in indexes:
   name=cfg['declared'][ix];p=pathlib.Path(cfg['work'])/('kernel_'+str(ix));(p/'traces').mkdir(parents=True)
   (p/'EXECUTION.json').write_bytes(cfg['execution'])
   (p/'traces'/cfg['ctxname']).write_text('\n'.join(cfg['memcpy']+[name])+'\n')
   import io
   out=io.StringIO();w=csv.writer(out);w.writerow(cfg['stats_header']);w.writerow(cfg['named_stats'][name]);(p/'traces'/cfg['statsname']).write_text(out.getvalue())
   rawpath=pathlib.Path(cfg['raw'][name]);alias=p/'traces'/name;alias.symlink_to(rawpath)
   targets={str(alias.absolute()):str(rawpath),str(pathlib.Path(cfg['map']).absolute()):cfg['map'],str(PRE/'validate_v7_frozen.py'):str(PRE/'validate_v7_frozen.py'),str(PRE/'validate_v7_stream_v3.py'):str(PRE/'validate_v7_stream_v3.py')}
   for f in [p/'EXECUTION.json',p/'traces'/cfg['ctxname'],p/'traces'/cfg['statsname']]:targets[str(f.absolute())]=str(f)
   begin=time.monotonic();before=pace.actual
   with OpenGuard(targets,pace):result=checker.validate(p,pathlib.Path(cfg['map']))
   need(token(rawpath.lstat())==tuple(cfg['raw_tokens'][name]),'RAW_SOURCE_CHANGED')
   need(result['kernels']==1 and result['per_kernel'][0]['name']==name,'ONE_KERNEL_RESULT')
   need(len(json.dumps(result))<=2*MIB,'BOUNDED_KERNEL_RESULT_METADATA')
   conn.send(dict(status='PASS',index=ix,name=name,result=result,source_sha256=result['source_files'][str(alias)],started=begin,ended=time.monotonic(),worker=dict(pid=os.getpid(),start_ticks=ticks(os.getpid())),paced_read_bytes=pace.actual-before))
  conn.send(dict(status='DONE',worker_pid=os.getpid(),actual_read_bytes=pace.actual,read_calls=pace.reads))
 except BaseException as error:
  try:conn.send(dict(status='FAILED_RETAINED',error=repr(error),traceback=traceback.format_exc()[-6000:]))
  except BaseException:pass
 finally:conn.close();os.close(pace.fd)
def cleanup(children,identities):
 actions=[]
 for sig,seconds in [(signal.SIGTERM,2),(signal.SIGKILL,2)]:
  for p in children:
   if p.exitcode is not None:continue
   expected=identities[p.pid]
   try:fd=os.pidfd_open(p.pid,0)
   except ProcessLookupError:continue
   try:
    if ticks(p.pid)==expected:signal.pidfd_send_signal(fd,sig,None,0);actions.append(dict(pid=p.pid,start_ticks=expected,signal=int(sig)))
   except ProcessLookupError:pass
   finally:os.close(fd)
  until=time.monotonic()+seconds
  for p in children:p.join(max(0,until-time.monotonic()))
  if all(not p.is_alive()for p in children):break
 need(all(not p.is_alive()for p in children),'OWN_WORKERS_UNRESOLVED')
 return actions
def authorize(root,mapfile,work,qualification,grant_file,grant_sha,rate,deadline_sec):
 need(type(rate)is int and 1<=rate<=256*MIB and 0<deadline_sec<=86400,'FINITE_RATE_OR_TIME')
 if qualification:
  need(root.resolve().is_relative_to(HERE.parent/'fixtures')and work.resolve().is_relative_to(HERE.parent),'QUALIFICATION_PRIVATE_PATHS')
  return deadline_sec
 need(work.resolve().is_relative_to(root.resolve()),'PRODUCTION_WORK_WITHIN_EXACT_ATTEMPT')
 need(root.name!='ORD_Rodinia_streamcluster_1be5fda1aa60_A001','CURRENT_ACTIVE_JOB_FORBIDDEN')
 need(grant_file is not None and grant_sha is not None,'ROOT_EXACT_GRANT_REQUIRED_BEFORE_BODY')
 p=pathlib.Path(grant_file);need(p.is_file()and not p.is_symlink()and p.stat().st_size<=65536 and digest(p)==grant_sha,'ROOT_GRANT_PIN')
 g=json.loads(p.read_text());need(root.resolve().is_relative_to(pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/inflight').resolve()),'PRODUCTION_NAS_ATTEMPT_ONLY')
 need(g['schema']=='ROOT_EXACT_ORDINARY_VALIDATOR_CPU2_V1'and g['approved']is True and g['profile']==PROFILE,'ROOT_GRANT_PROFILE')
 need(g['root']==str(root.resolve())and g['rate_bytes_sec']==rate and g['max_workers']==2,'ROOT_EXACT_JOB_AND_RATE')
 need(mapfile.stat().st_size<=16*MIB,'ROOT_MAP_METADATA_LIMIT');mapped=json.loads(mapfile.read_text())
 if g['map_binding']=='RAW_SHA256':need(g['map_sha256']==digest(mapfile),'ROOT_MAP_RAW_SHA')
 elif g['map_binding']=='CANONICAL_CHECKER_ROWS_V1':
  canonical=dict(binary_sha256=mapped['binary_sha256'],instructions=sorted([{k:x[k]for k in ['function','pc','sass','src','dst']}for x in mapped['instructions']],key=lambda x:(x['function'],x['pc'])))
  raw=json.dumps(canonical,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
  need(hashlib.sha256(raw).hexdigest()==g['map_semantics_sha256'],'ROOT_MAP_SEMANTIC_ROWS')
 else:raise RuntimeError('ROOT_MAP_BINDING_MODE')
 need(mapped['binary_sha256']==g['binary_sha256'],'ROOT_BINARY_SCOPE')
 need(g['code_manifest_sha256']==digest(HERE/'CODE_MANIFEST.json')and g['science_authorized']is False and g['publication_authorized']is False,'ROOT_CODE_AND_DATA_ONLY')
 manifest=json.loads((HERE/'CODE_MANIFEST.json').read_text())
 for relative,row in manifest['files'].items():
  member=HERE.parent/relative;need(member.resolve().is_relative_to(HERE.parent.resolve())and not member.is_symlink()and member.stat().st_size==row['bytes']and digest(member)==row['sha256'],'ROOT_FRESH_CODE_PIN')
 need(math.isfinite(g['absolute_deadline_unix'])and math.isfinite(g['not_before_unix'])and g['not_before_unix']<=time.time()<g['absolute_deadline_unix']and 0<g['absolute_deadline_unix']-g['not_before_unix']<=86400,'ROOT_ABSOLUTE_JOB_WINDOW')
 remaining=g['absolute_deadline_unix']-time.time();need(remaining>0 and deadline_sec<=g['maximum_validator_seconds']<=86400,'ROOT_FINITE_DEADLINE')
 return min(deadline_sec,remaining)
def verify_production_caller(owner,root,grant_file,grant_sha):
 p=pathlib.Path(grant_file);need(digest(p)==grant_sha,'ROOT_GRANT_CHANGED');g=json.loads(p.read_text())
 cmd=pathlib.Path('/proc',str(owner),'cmdline').read_bytes().split(bytes([0]))
 scripts=[pathlib.Path(x.decode())for x in cmd if x.endswith(b'.py')]
 need(len(scripts)==1 and scripts[0].is_file()and not scripts[0].is_symlink()and digest(scripts[0])==g['worker_sha256'],'ROOT_PINNED_CALLING_MOTHER')
 jobs=[pathlib.Path(x.decode())for x in cmd if x.endswith(b'.json')]
 need(len(jobs)==1 and jobs[0].stat().st_size<=2*MIB,'EXACT_MOTHER_JOB_ARGUMENT')
 job=json.loads(jobs[0].read_text());need(job['id']==root.name and job['task']['binary_sha256']==g['binary_sha256'],'MOTHER_JOB_SCOPE')
def run(root,mapfile,work,leasefd,owner,start,rate,workers=2,deadline_sec=86400,qualification=False,grant_file=None,grant_sha=None):
 root=pathlib.Path(root).absolute();mapfile=pathlib.Path(mapfile).absolute();work=pathlib.Path(work).absolute()
 need(mapfile.resolve().is_relative_to(root.resolve()),'MAP_WITHIN_EXACT_ATTEMPT')
 need(workers in (1,2),'MAX_TWO_CHILDREN');need(not work.exists(),'NEW_PRIVATE_WORK_ATTEMPT')
 duration=authorize(root,mapfile,work,qualification,grant_file,grant_sha,rate,deadline_sec);deadline=time.monotonic()+duration
 expected_path=os.readlink('/proc/self/fd/'+str(leasefd))
 if qualification:need(pathlib.Path(expected_path).resolve().is_relative_to(HERE.parent/'fixtures'),'QUALIFICATION_LEASE_PATH')
 else:need(expected_path=='/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','EXACT_WHOLEJOB_LEASE_PATH')
 lease=(leasefd,int(owner),str(start),expected_path);verify_lease(*lease)
 if not qualification:verify_production_caller(owner,root,grant_file,grant_sha)
 work.mkdir(parents=True);pacepath=work/'AGGREGATE_RATE.state'
 pacepath.write_bytes(struct.pack('<QQ',time.monotonic_ns(),0));pace=Pace(pacepath,rate,deadline,lease)
 oldsignals={};stop=[False];children=[];identities={};cleanup_actions=[];conns=[]
 def closed_ack():
  need(all(not p.is_alive()for p in children),'OWN_WORKERS_UNRESOLVED')
  value=dict(schema='ORDINARY_VALIDATOR_OWNED_WORKERS_CLOSED_V1',status='ALL_OWNED_WORKERS_REAPED',workers=[dict(pid=p.pid,start_ticks=identities[p.pid],exitcode=p.exitcode)for p in children],lease_unlocked=False,source_KEEP=True)
  path=work/'OWNED_WORKERS_CLOSED.json'
  if path.exists():need(json.loads(path.read_text())==value,'CLEANUP_ACK_CHANGED')
  else:save(path,value)

 try:
  for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:oldsignals[sig]=signal.signal(sig,lambda *a:stop.__setitem__(0,True))
  def meta(p):
   p=pathlib.Path(p);before=token(p.lstat());b=read_bytes(p,pace,16*MIB);need(token(p.lstat())==before,'METADATA_STABLE');return b,dict(path=str(p),token=before,sha256=hashlib.sha256(b).hexdigest())
  mapraw,mapref=meta(mapfile);m=json.loads(mapraw);rows={(x['function'],x['pc']):x for x in m['instructions']};need(len(rows)==len(m['instructions']),'duplicate static function/PC')
  execution,eref=meta(root/'EXECUTION.json');ex=json.loads(execution);need(ex['binary_sha256']==m['binary_sha256']and ex['tool_sha256']=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73','capture/map/tool binding')
  ctx=sorted((root/'traces').glob('kernelslist_ctx_*'));need(len(ctx)==1,'ordinary domain requires exactly one context commandlist');cmdraw,cref=meta(ctx[0]);declared=[];memcpy=[]
  for line in cmdraw.decode().splitlines():
   n=line.strip()
   if not n:continue
   if n.startswith('Memcpy'):memcpy.append(n);continue
   need(pathlib.PurePosixPath(n).name==n and n.startswith('kernel-')and n.endswith('.trace.xz'),'invalid raw command member');declared.append(n)
  need(declared and len(declared)==len(set(declared))and len(declared)<=65536,'zero or duplicate declared kernel')
  raw={p.name:p.absolute()for p in(root/'traces').glob('kernel*.trace.xz')};need(set(raw)==set(declared),'missing or undeclared raw kernel')
  contexts={re.search(r'ctx_(0x[0-9a-fA-F]+)',p).group(1)for p in declared};need(len(contexts)==1,'multiple CUDA contexts')
  raw_tokens={}
  for n,p in raw.items():need(p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(root.resolve()),'REGULAR_RAW_SOURCE');raw_tokens[n]=token(p.lstat())
  stats=sorted((root/'traces').glob('stats_ctx_*'));need(len(stats)==1,'ONE_STATS_FILE');statsraw,sref=meta(stats[0])
  import io
  table=list(csv.reader(io.StringIO(statsraw.decode())));named={x[0].strip():x for x in table[1:]if x};need(len([x for x in table[1:]if x])==len(declared)and set(named)==set(declared),'WHOLE_APP_STATS_NAMES')
  cfg=dict(root=str(root),map=str(mapfile),work=str(work),pace=str(pacepath),rate=rate,deadline=deadline,lease=lease,affinity=sorted(os.sched_getaffinity(0))[:2],parent_pace_fd=pace.fd,declared=declared,raw={k:str(v)for k,v in raw.items()},raw_tokens=raw_tokens,execution=execution,memcpy=memcpy,ctxname=ctx[0].name,statsname=stats[0].name,stats_header=table[0],named_stats=named)
  context=multiprocessing.get_context('fork');count=min(workers,len(declared))
  for k in range(count):
   parent,child=context.Pipe(duplex=False);p=context.Process(target=child_loop,args=(child,list(range(k,len(declared),count)),cfg));p.start();child.close();children.append(p);identities[p.pid]=ticks(p.pid);conns.append(parent)
  completed={};done=set();completion_order=[];result_bytes=0
  while len(done)<count:
   pace.check();need(not stop[0],'OWN_VALIDATOR_STOP_REQUESTED')
   for conn in wait([c for i,c in enumerate(conns)if i not in done],timeout=.1):
    index=conns.index(conn)
    try:message=conn.recv()
    except EOFError:raise RuntimeError('WORKER_CHANNEL_EOF_BEFORE_DONE')
    if message['status']=='DONE':done.add(index);continue
    need(message['status']=='PASS','CHILD_VALIDATION_FAILED '+message.get('error',''))
    result_bytes+=len(json.dumps(message));need(result_bytes<=512*MIB,'WHOLEJOB_METADATA_MEMORY_BOUND')
    ix=message['index'];need(type(ix)is int and ix in range(len(declared))and ix not in completed and message['name']==declared[ix],'WRONG_OR_DUPLICATE_WORKER_RESULT')
    result=message['result'];need(result['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and result['map_sha256']==mapref['sha256']and result['frozen_parser_sha256']==HELPER_SHA and result['validator_sha256']==VALIDATOR_SHA,'FROZEN_CHILD_PROVENANCE')
    completed[ix]=message;completion_order.append(ix)
  for p in children:p.join(max(0,min(5,deadline-time.monotonic())));need(p.exitcode==0,'CHILD_NONZERO_OR_UNJOINED')
  need(set(completed)==set(range(len(declared))),'WHOLE_APP_RESULT_SET');closed_ack()
  total=collections.Counter();per=[];files={};streams=set();peak=0
  for ix,name in enumerate(declared):
   message=completed[ix];one=message['result'];k=one['per_kernel'][0];need(k['name']==name and int(named[name][-1])==k['counts']['sass_records'],'reported record count mismatch')
   total.update(k['counts']);per.append(k);files[str(raw[name])]=message['source_sha256'];streams.update(one['stream_ids']);peak=max(peak,one['peak_live_warp_states'])
  need(len(streams)==1,'PENDING_CONCURRENT_STREAM_ORDERING')
  for p,snapshot in [(mapfile,mapref),(root/'EXECUTION.json',eref),(ctx[0],cref),(stats[0],sref)]:
   after,proof=meta(p);need(proof==snapshot,'WHOLE_JOB_METADATA_CHANGED')
  for n,p in raw.items():need(token(p.lstat())==raw_tokens[n],'WHOLE_JOB_RAW_CHANGED')
  pace.check();result=dict(schema='ADA7_STREAM_FULL_RECORD_VERIFICATION_V1',status='ADA7_ORDINARY_FULL_RECORD_PASS',counts=dict(total),ctas=sum(k['ctas']for k in per),warps=sum(k['warps']for k in per),kernels=len(per),all_declared_warps_terminate=True,kernel_commandlist_exact_set=True,stats_record_counts_match=True,context_count=1,stream_ids=sorted(streams),per_kernel=per,peak_live_warp_states=peak,source_files=files,map_sha256=mapref['sha256'],frozen_parser_sha256=HELPER_SHA,validator_sha256=digest(HERE/'parallel_ordinary_validator_v1.py'),frozen_validator_sha256=VALIDATOR_SHA,lane_address_lists_retained=False,capture_map_binary_binding=True,frozen_parser_identity_asserted=True,direct_cbank_static_and_lane_offsets_verified=True,strict_single_stream_ordinary=True,validation_deadline_monotonic=deadline)
  proof=dict(schema='ORDINARY_WHOLEJOB_VALIDATOR_CPU2_CANDIDATE_CLOSED_V1',status='CPU_CHECKS_CLOSED_ROOT_ADMISSION_REQUIRED',profile=PROFILE,workers=count,worker_identities=identities,completion_order=completion_order,declared_fold_order=list(range(len(declared))),per_kernel=[completed[i]for i in range(len(declared))],aggregate_rate_bytes_sec=rate,aggregate_1MiB_maximum_read_ahead_burst=MIB,rate_state=struct.unpack('<QQ',pacepath.read_bytes()),inherited_wholejob_lease_verified=True,lease_acquired_or_unlocked_by_adapter=False,raw_source_before_after_tokens=raw_tokens,metadata_refs=[mapref,eref,cref,sref],source_KEEP=True,science_qualified=False,consumer_qualified=False,GPU_executed=False)
  save(work/'PARALLEL_CLOSED.json',proof);pace.check();return result
 except BaseException as error:
  cleanup_actions=cleanup(children,identities);closed_ack()
  save(work/'FAILED_RETAINED.json',dict(status='FAILED_RETAINED',error=repr(error),owned_cleanup=cleanup_actions,source_KEEP=True,qualification_granted=False));raise
 finally:
  for c in conns:c.close()
  if any(p.is_alive()for p in children):cleanup(children,identities)
  for sig,handler in oldsignals.items():signal.signal(sig,handler)
  os.close(pace.fd)
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('map');p.add_argument('--work',required=True);p.add_argument('--lease-fd',type=int,required=True);p.add_argument('--owner-pid',type=int,required=True);p.add_argument('--owner-start-ticks',required=True);p.add_argument('--rate-bytes-sec',type=int,required=True);p.add_argument('--workers',type=int,default=2);p.add_argument('--deadline-sec',type=float,required=True);p.add_argument('--qualification',action='store_true');p.add_argument('--grant-file');p.add_argument('--grant-sha');p.add_argument('--admission-only',action='store_true');p.add_argument('--output',default='FULL_RECORD_STREAM_VALIDATION.json');a=p.parse_args()
 os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);resource.setrlimit(resource.RLIMIT_AS,(2**31,2**31))
 if a.admission_only:
  root=pathlib.Path(a.root).absolute();mp=pathlib.Path(a.map).absolute();work=pathlib.Path(a.work).absolute()
  authorize(root,mp,work,a.qualification,a.grant_file,a.grant_sha,a.rate_bytes_sec,a.deadline_sec)
  expected=os.readlink('/proc/self/fd/'+str(a.lease_fd))
  if not a.qualification:need(expected=='/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','EXACT_WHOLEJOB_LEASE_PATH')
  verify_lease(a.lease_fd,a.owner_pid,a.owner_start_ticks,expected)
  if not a.qualification:verify_production_caller(a.owner_pid,root,a.grant_file,a.grant_sha)
  print(json.dumps(dict(status='ROOT_EXACT_CPU2_ADMISSION_ONLY_PASS',trace_body_read=False,lease_acquired_or_unlocked=False)));return
 need(pathlib.PurePosixPath(a.output).name==a.output and a.output.endswith('.json'),'EXACT_RESULT_BASENAME')
 result=run(a.root,a.map,a.work,a.lease_fd,a.owner_pid,a.owner_start_ticks,a.rate_bytes_sec,a.workers,a.deadline_sec,a.qualification,a.grant_file,a.grant_sha)
 dest=pathlib.Path(a.root)/a.output;need(time.monotonic()<result['validation_deadline_monotonic'],'VALIDATOR_RESULT_DEADLINE');save(dest,result);need(time.monotonic()<result['validation_deadline_monotonic'],'VALIDATOR_RESULT_DEADLINE');print(json.dumps(result));need(time.monotonic()<result['validation_deadline_monotonic'],'VALIDATOR_RESULT_DEADLINE')
if __name__=='__main__':main()
