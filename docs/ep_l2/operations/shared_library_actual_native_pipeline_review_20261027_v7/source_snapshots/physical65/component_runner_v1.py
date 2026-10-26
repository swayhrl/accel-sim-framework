#!/usr/bin/env python3
"""Synthetic65MiB component only. NAS preview never constructs Scope or Native slots."""
import pathlib,os,sys,json,hashlib,time,math,stat,signal,importlib.util,contextlib
D=pathlib.Path(__file__).resolve().parent
N=D.parent
V=pathlib.Path('/root/share/mnt164/huangrulin/traces/tools/versions/0c79cd72e34675ba84dbc0b61a4fbb293e4e100f55c0f37b650bcfb464ef9017')
DEC=N/'sm70_consumer_decoder_prepare_20261027_v2'
CODE='0c79cd72e34675ba84dbc0b61a4fbb293e4e100f55c0f37b650bcfb464ef9017'
MANIFEST_SHA='2c6b93cb7a4924a38acd198c162f17a7f0db3062856aabf6973eaf3b4dfd5ac7'
DEC_ENTRY_SHA='b2d345922cdf6caadbaebe59f3204eea381b334258c7f3244495687f40b66cf3'
DEC_ADAPTER_SHA='85c44458f8b8fad5a3adaaa1bccecb2a981bcfab66c670d8eeb3edf79e3aa586'
MIB=2**20;TOTAL=65*MIB;WINDOW=64*MIB;CHUNK=MIB;RATE=8*MIB
EPOCH='SM70_SYNTH65_DECODER_20261027_V1'
PAIRS=[('EP','EP_R5'),('DTC','DTC_DM'),('DTC','DTC_DH'),('DTC','DTC_CM'),('DTC','DTC_CH')]
def need(v,m):
 if not v:raise RuntimeError('COMPONENT_HOLD_'+m)
def digest(b):return hashlib.sha256(b).hexdigest()
def readmeta(p,cap=2*MIB):
 p=pathlib.Path(p);need(p.is_absolute()and '..'not in p.parts,'SAFE_METADATA_PATH')
 for q in [p,*p.parents]:need(not q.is_symlink(),'SYMLINK_METADATA')
 s=p.stat();need(stat.S_ISREG(s.st_mode)and s.st_size<=cap,'METADATA_SIZE')
 with p.open('rb')as f:b=f.read(cap+1)
 need(len(b)==s.st_size and ident(p.stat())==ident(s),'METADATA_STABLE');return b
def ref(p):
 b=readmeta(p,4*MIB);return dict(path=str(p),bytes=len(b),sha256=digest(b))
def obj(p):return json.loads(readmeta(p))
def save(p,v):
 p=pathlib.Path(p);need(p.is_relative_to(D),'NAS_OUTPUT_ONLY');p.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 return dict(path=str(p),bytes=len(b),sha256=digest(b))
def ident(s):return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_uid,s.st_gid]
def check(deadline):need(time.monotonic()<deadline,'ABSOLUTE_DEADLINE')
def cpu():
 os.sched_setaffinity(0,{0,1})
 if os.getpriority(os.PRIO_PROCESS,0)<15:os.nice(15-os.getpriority(os.PRIO_PROCESS,0))
class Pace:
 def __init__(self):self.started=time.monotonic();self.n=0
 def io(self,n,deadline):
  self.n+=n;check(deadline);delay=self.n/RATE-(time.monotonic()-self.started)
  if delay>0:time.sleep(min(delay,max(0,deadline-time.monotonic())))
  check(deadline)
@contextlib.contextmanager
def absolute_alarm(deadline):
 def expire(*args):raise TimeoutError('COMPONENT_ABSOLUTE_DEADLINE')
 old=signal.signal(signal.SIGALRM,expire);signal.setitimer(signal.ITIMER_REAL,max(0.001,deadline-time.monotonic()))
 try:yield
 finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)
def verify_sources():
 need(ref(V/'CODE_MANIFEST.json')['sha256']==MANIFEST_SHA,'R5_MANIFEST')
 manifest=obj(V/'CODE_MANIFEST.json');need(manifest['code_version_id']==CODE and len(manifest['files'])==21,'R5_CODE_SCOPE')
 for name,r in manifest['files'].items():
  b=readmeta(V/name);need(len(b)==r['bytes']and digest(b)==r['sha256'],'R5_FILE_'+name)
 need(ref(DEC/'ROOT_ENTRY_V2.json')['sha256']==DEC_ENTRY_SHA,'DECODER_ENTRY')
 need(ref(DEC/'sm70_decoder_stream_v2.py')['sha256']==DEC_ADAPTER_SHA,'DECODER_ADAPTER')
 entry=obj(DEC/'ROOT_ENTRY_V2.json')
 for key in ['manifest_ref','literal_byte_contract_ref','callgraph_ref']:
  rr=entry[key];b=readmeta(rr['path']);need(len(b)==rr['bytes']and digest(b)==rr['sha256'],'DECODER_PIN_'+key)
 # Session itself freshly verifies frontend,decoder binaries and bound full configs.
 return dict(R5_manifest=ref(V/'CODE_MANIFEST.json'),decoder_entry=ref(DEC/'ROOT_ENTRY_V2.json'),decoder_adapter=ref(DEC/'sm70_decoder_stream_v2.py'))
def plan():
 H=b'-kernel name = SYNTHETIC_COMPONENT_ONLY\n-kernel id = 1\n-grid dim = (1,1,1)\n-block dim = (32,1,1)\n-shmem = 0\n-nregs = 8\n-binary version = 70\n-cuda stream id = 0\n-shmem base_addr = 0x40000000\n-local mem base_addr = 0x50000000\n-accelsim tracer version = 3\n#traces format = synthetic only\n#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = 9999\n'
 rows=[('IADD3',i*16,65536)for i in range(1023)]
 mem=b'100000 ffffffff 1 R4 LDG.E.32 1 R1 4 0 '+b' '.join(('%x'%(0x1000+4*i)).encode()for i in range(32))+b' 0'
 cut=len(b'100000 ffffffff 1 R4 LDG.')
 filler=WINDOW-cut-len(H)-sum(x[2]for x in rows)
 need(80<=filler<=65536,'PLANNED_SEAM_FILLER');rows.append(('IADD3',0x90000,filler));rows.append(('MEMORY',0x100000,65536))
 tail=b'200000 ffffffff 0 EXIT 0 0 0\n#END_TB\n'
 remaining=TOTAL-len(H)-sum(x[2]for x in rows)-len(tail)
 while remaining>65536:rows.append(('IADD3',0xa0000+len(rows)*16,65536));remaining-=65536
 need(80<=remaining<=65536,'TAIL_FILLER');rows.append(('IADD3',0xb0000,remaining))
 count=len(rows)+1;need(len(str(count))==4,'COUNT_WIDTH');H=H.replace(b'9999',str(count).encode())
 return H,rows,mem,tail,count,cut
def generate():
 cpu();deadline=time.monotonic()+180;pace=Pace();p=D/'SYNTHETIC_ONLY_65MiB.traceg';need(not p.exists(),'SOURCE_ALREADY_EXISTS')
 H,rows,mem,tail,count,cut=plan();h=hashlib.sha256();n=0
 with p.open('xb',buffering=0)as f:
  def write(b):
   nonlocal n
   need(f.write(b)==len(b),'SOURCE_SHORT_WRITE');h.update(b);n+=len(b);pace.io(len(b),deadline)
  write(H)
  for kind,pc,length in rows:
   base=mem if kind=='MEMORY'else('%x ffffffff 1 R1 IADD3 2 R2 R3 0 0'%pc).encode()
   need(len(base)+1<=length<=65536,'RECORD_LINE_CAP');write(base+b' '*(length-len(base)-1)+b'\n')
  write(tail);os.fsync(f.fileno());s=os.fstat(f.fileno())
 need(n==TOTAL and s.st_size==TOTAL,'SOURCE_EXACT_SIZE')
 info=dict(schema='SM70_SYNTHETIC65_SOURCE_V1',path=str(p),size=n,sha256=h.hexdigest(),identity=ident(s),synthetic_only=True,kind='traceg',compression='text',records=count,physical_warps=1,physical_lanes=32,grid=[1,1,1],block=[32,1,1],windows=[dict(offset=0,length=WINDOW),dict(offset=WINDOW,length=MIB)],boundary=dict(offset=WINDOW,record='LDG.E.32',split_after_literal='100000 ffffffff 1 R4 LDG.',partial_record_must_survive=True),padding='Whitespace inside valid instruction lines <=65535 bytes, not blank-line approximation; every synthetic instruction passed original parser+decoder in preview',source_KEEP=True)
 save(D/'SYNTHETIC_SOURCE_MANIFEST_V1.json',info);return info
def source_open(info):
 p=pathlib.Path(info['path']);need(p==D/'SYNTHETIC_ONLY_65MiB.traceg'and not p.is_symlink(),'EXACT_SYNTHETIC_SOURCE')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);s=os.fstat(fd);need(ident(s)==info['identity']==ident(p.stat()),'SOURCE_FD_PATH_IDENTITY');return os.fdopen(fd,'rb',buffering=0)
def decoder_sessions(info):
 sys.path.insert(0,str(DEC));import sm70_decoder_stream_v2 as decoder
 stack=contextlib.ExitStack();sessions=[];objects=[]
 try:
  for profile,cfg in PAIRS:
   s=stack.enter_context(decoder.Session(profile,cfg));sessions.append(s)
   objects.append(s.begin(dict(profile=profile,configuration_profile=cfg,kind='traceg',compression='text',relative_path='kernel-SYNTHETIC_COMPONENT.traceg',size=info['size'],sha256=info['sha256'],max_decoded_bytes=info['size'],max_state_keys=10)))
  return stack,objects
 except BaseException:stack.close();raise
def binding(info):
 ctx=dict(binding_id='SYNTHETIC65_LITERAL_COMPONENT_ONLY',canonical_path=info['path'],catalog_id='SYNTHETIC_NATIVE_RESOURCE_COMPONENT_ONLY',overlay_id='NOT_PUBLIC_CATALOG',profile='REAL_DECODER_COMPONENT_ONLY_NOT125_RESTORE',sha256=info['sha256'],size=info['size'])
 return dict(binding_id=ctx['binding_id'],size=ctx['size']),ctx
def finish_decoders(objects,info,deadline):
 results=[]
 for o in objects:
  check(deadline);r=o.end()
  need(r['literal_native_bytes_sha256']==info['sha256']==r['decoded_text_sha256'],'DECODER_LITERAL_DECODED_IDENTITY')
  need(r['actual_native_decoder_records']==info['records']and r['kernel_scheduler_clock_or_scientific_authority_called']is False,'COMPLETE_RECORDS_NO_SCHEDULER')
  results.append(r)
 return results
def nas_preview():
 cpu();sources=verify_sources();info=obj(D/'SYNTHETIC_SOURCE_MANIFEST_V1.json')
 deadline=time.monotonic()+240;pace=Pace();whole=hashlib.sha256();windows=[];stack,objects=decoder_sessions(info)
 try:
  with absolute_alarm(deadline),source_open(info)as f:
   for w in info['windows']:
    h=hashlib.sha256();n=0;need(f.tell()==w['offset'],'SOURCE_WINDOW_OFFSET')
    while n<w['length']:
     check(deadline);b=f.read(min(CHUNK,w['length']-n));need(bool(b),'SOURCE_SHORT_READ')
     n+=len(b);whole.update(b);h.update(b);pace.io(len(b),deadline)
     for o in objects:check(deadline);o.feed(b);check(deadline)
    windows.append(dict(**w,sha256=h.hexdigest(),NAS_only=True))
   need(not f.read(1)and ident(os.fstat(f.fileno()))==info['identity'],'SOURCE_CLOSED_IDENTITY')
   need(whole.hexdigest()==info['sha256'],'SOURCE_WHOLE_SHA')
   results=finish_decoders(objects,info,deadline)
  report=dict(schema='SM70_SYNTHETIC65_NAS_PREVIEW_V1',status='NAS_CPU_ONLY_ALL5_LITERAL_STREAM_PASS_NOT_NATIVE_PHYSICAL_QUALIFICATION',source=info,sources=sources,windows=windows,decoder_results=results,aggregate_literal_bytes_read=TOTAL,pacing_limit_combined_IO_bytes_sec=RATE,Native_written_bytes=0,physical_Scope_constructed=False,Root_grant_created=False,profiles=[cfg for _,cfg in PAIRS],source_KEEP=True,qualification_granted=False,completed_unix=time.time())
  save(D/'NAS_CPU_PREVIEW_RESULT_V1.json',report);return report
 finally:stack.close()
def templates():
 info=obj(D/'SYNTHETIC_SOURCE_MANIFEST_V1.json');b,ctx=binding(info)
 br=save(D/'bindings.json',dict(schema='SM70_EXACT_BOUND_RESOURCE_BINDINGS_R5',scope_epoch=EPOCH,catalog_pins={'qualification':'SYNTHETIC65_LITERAL_DECODER_COMPONENT_ONLY'},bindings={info['sha256']:dict(**b,context=ctx)}))
 policy=dict(schema='SM70_EXPLICIT_RESOURCE_POLICY_R5',kind='EXACT_SINGLE_SLOT_READBACK',allowed_operation='SM70_EXACT_BOUND_RESTORE_WINDOW_ONLY',allowed_operations=[],base_code_version_id='e2b1a814a201f7f5dd95c55c61a94f04069690dd18ecfabd89c9f88dc7ae19c7',code_version_id=CODE,provider_sha256=obj(V/'CODE_MANIFEST.json')['files']['bounded_resources_r5.py']['sha256'],scope_epoch=EPOCH,integration_id=EPOCH,binding_set_ref=br,catalog_pins={'qualification':'SYNTHETIC65_LITERAL_DECODER_COMPONENT_ONLY'},native_floor_bytes=5*2**30,own_native_cap_bytes=256*MIB,native_window_cap_bytes=WINDOW,slot_count=1,control_margin_bytes=16*MIB,native_work_root=obj(V/'PROFILE.json')['native_work_root'],nas_evidence_root=str(D/'physical_evidence'))
 (D/'physical_evidence').mkdir(exist_ok=True);pr=save(D/'policy.json',policy)
 grant=dict(status='UNAPPROVED_TEMPLATE_NOT_AUTHORITY',schema='ROOT_SYNTHETIC65_DECODER_COMPONENT_GRANT_V1',kind=policy['kind'],scope_epoch=EPOCH,code_version_id=CODE,policy_sha256=pr['sha256'],component_runner_sha256=ref(pathlib.Path(__file__))['sha256'],decoder_entry_sha256=DEC_ENTRY_SHA,synthetic_source_sha256=info['sha256'],exact_bytes=TOTAL,exact_windows=info['windows'],attempts=1,boot_id='ROOT_MUST_FILL_CURRENT_BOOT_ID',absolute_deadline_monotonic=None,max_duration_seconds=600,scientific_starts_authorized=False,generic_materialize_authorized=False,actual_public_asset_or_source2_read_authorized=False,source_payload_deletion_authorized=False,public_activation_authorized=False,resource_primitive_synthetic_qualification_only=True,authority_path_required=str(pathlib.Path(policy['native_work_root'])/'authority'/('R5_'+EPOCH+'.json')))
 save(D/'ROOT_GRANT_UNAPPROVED_TEMPLATE.json',grant)
 save(D/'PROFILE_UNMODIFIED_REFERENCE.json',obj(V/'PROFILE.json'))
 return grant
def validate_grant(path,info,started):
 g=obj(path);need(g.get('status')=='ROOT_APPROVED_R5_EXACT_RESOURCE_SCOPE','NO_ROOT_APPROVAL')
 q=obj(D/'policy.json');profile=obj(V/'PROFILE.json')
 need(pathlib.Path(path)==pathlib.Path(profile['native_work_root'])/'authority'/('R5_'+EPOCH+'.json'),'ROOT_AUTHORITY_PATH')
 s=pathlib.Path(path).stat();need(s.st_uid==0 and s.st_mode&0o022==0,'ROOT_AUTHORITY_OWNER')
 need(g['schema']=='ROOT_SYNTHETIC65_DECODER_COMPONENT_GRANT_V1'and g['scope_epoch']==EPOCH and g['kind']==q['kind']and g['code_version_id']==CODE,'ROOT_EXACT_COMPONENT')
 need(g['policy_sha256']==ref(D/'policy.json')['sha256']and g['component_runner_sha256']==ref(pathlib.Path(__file__))['sha256']and g['decoder_entry_sha256']==DEC_ENTRY_SHA,'ROOT_CODE_POLICY_PINS')
 need(g['synthetic_source_sha256']==info['sha256']and g['exact_bytes']==TOTAL and g['exact_windows']==info['windows']and g['attempts']==1,'ROOT_EXACT_BYTES_WINDOWS')
 need(g['boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'ROOT_BOOT_ID')
 duration=g['max_duration_seconds'];absolute=g['absolute_deadline_monotonic']
 need(type(duration)is int and 1<=duration<=600 and type(absolute)in[int,float]and math.isfinite(absolute)and started<absolute<=started+600,'ROOT_FINITE_DEADLINE')
 for key in ['scientific_starts_authorized','generic_materialize_authorized','actual_public_asset_or_source2_read_authorized','source_payload_deletion_authorized','public_activation_authorized']:need(g.get(key)is False,'ROOT_OVERBROAD_'+key)
 need(g.get('resource_primitive_synthetic_qualification_only')is True,'ROOT_COMPONENT_ONLY')
 return g,min(absolute,started+duration)
def resource_module():
 s=importlib.util.spec_from_file_location('component_exact_R5',V/'bounded_resources_r5.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def physical(grant_path):
 cpu();started=time.monotonic();info=obj(D/'SYNTHETIC_SOURCE_MANIFEST_V1.json');g,deadline=validate_grant(grant_path,info,started)
 # Nothing that can create Native bytes is reached before the exact live Root grant.
 sources=verify_sources();r=resource_module();os.environ[r.DEADLINE_ENV]=str(deadline)
 save(D/'PHYSICAL_ONCE_INTENT.json',dict(schema='SM70_SYNTHETIC65_PHYSICAL_ONCE_INTENT_V1',grant_ref=ref(pathlib.Path(grant_path)),policy_ref=ref(D/'policy.json'),deadline_monotonic=deadline,pid=os.getpid(),start_ticks=pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],source_KEEP=True))
 scope=r.Scope(obj(V/'PROFILE.json'),ref(D/'policy.json'),ref(pathlib.Path(grant_path)),CODE,'EXACT_SINGLE_SLOT_READBACK',deadline=deadline)
 b,ctx=binding(info);pace=Pace();nativewhole=hashlib.sha256();sourcewhole=hashlib.sha256();proofs=[];stack,objects=decoder_sessions(info)
 try:
  with absolute_alarm(deadline),scope.operation(),source_open(info)as f:
   begin=scope.observe(True)
   def consume(part):
    check(deadline);nativewhole.update(part);pace.io(len(part),deadline)
    for o in objects:check(deadline);o.feed(part);check(deadline)
   for w in info['windows']:
    check(deadline);need(f.tell()==w['offset'],'EXACT_SOURCE_WINDOW');slot=scope.slot(b,ctx,w['offset'],w['length']);h=hashlib.sha256();n=0
    while n<w['length']:
     check(deadline);part=f.read(min(CHUNK,w['length']-n));need(bool(part),'SOURCE_SHORT_READ');pace.io(len(part),deadline);sourcewhole.update(part);h.update(part);n+=len(part)
     slot.write(part);pace.io(len(part),deadline)
    proof=slot.finish(h.hexdigest(),readback_consume=consume);check(deadline)
    need(proof['owner']['preallocation']=='POSIX_FALLOCATE_CLOSED_NATIVE_EXT4'and proof['qualification_only']is False,'REAL_PHYSICAL_BRANCH_ONLY')
    closed_ref=slot.proof_ref;clean=slot.cleanup()
    proofs.append(dict(window=w,closed_proof_ref=closed_ref,cleanup_ref=clean))
   need(not f.read(1)and ident(os.fstat(f.fileno()))==info['identity'],'SOURCE_COMPLETE_CLOSED')
   need(sourcewhole.hexdigest()==nativewhole.hexdigest()==info['sha256'],'LITERAL_WHOLE_SAME_BYTES')
   results=finish_decoders(objects,info,deadline);end=scope.observe(True);check(deadline)
   save(D/'ROOT_PHYSICAL_COMPONENT_RESULT_V1.json',dict(schema='SM70_SYNTHETIC65_PHYSICAL_DECODER_COMPONENT_RESULT_V1',status='PHYSICAL_NATIVE_LITERAL_DECODER_COMPONENT_PASS_NOT125_RESTORE',source=info,sources=sources,grant_ref=ref(pathlib.Path(grant_path)),windows=proofs,source_SHA=sourcewhole.hexdigest(),literal_native_SHA=nativewhole.hexdigest(),decoder_results=results,begin_foreign_and_resources=begin,end_foreign_and_resources=end,R5_counters=scope.counters,aggregate_IO_pacing_bytes_sec=RATE,source_payload_released_bytes=0,source_KEEP=True,public_activation=False,scientific_qualification=False,full125_qualification=False,completed_unix=time.time()))
 except BaseException as exc:
  # Scope.operation preserves any exact owned active partial; do not discover/delete slots.
  save(D/'PHYSICAL_FAILURE_RETAINED_V1.json',dict(schema='SM70_SYNTHETIC65_COMPONENT_FAILURE_RETAINED_V1',error=repr(exc),scope_epoch=EPOCH,owned_partial_receipt_directory=str(D/'physical_evidence'),expected_owned_slot_directory=str(scope.work/'bounded_readback_r5'/EPOCH),source_KEEP=True,automatic_recovery_or_deletion=False,Root_new_exact_recovery_required=True,completed_unix=time.time()))
  raise
 finally:stack.close()
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['generate','templates','nas-preview','physical']);p.add_argument('--grant');args=p.parse_args()
 if args.mode=='generate':x=generate()
 elif args.mode=='templates':x=templates()
 elif args.mode=='nas-preview':x=nas_preview()
 else:
  need(bool(args.grant),'ROOT_GRANT_ARGUMENT')
  outer=time.monotonic()+600
  inherited=os.environ.get('SM70_R5_STAGE_DEADLINE_MONOTONIC')
  if inherited is not None:
   inherited=float(inherited);need(math.isfinite(inherited)and inherited>0,'INVALID_INHERITED_ABSOLUTE_DEADLINE');outer=min(outer,inherited)
  # Cover grant/source/pin metadata stalls before the inner finite Scope exists.
  check(outer)
  with absolute_alarm(outer):physical(args.grant)
  x={'completed':True}
 print(json.dumps({k:x[k]for k in ['status','size','sha256']if k in x}))
if __name__=='__main__':main()
