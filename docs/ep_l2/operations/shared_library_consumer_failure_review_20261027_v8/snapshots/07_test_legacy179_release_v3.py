#!/usr/bin/env python3
"""Finite actual native-metadata decoder CPU regressions, no source trace bodies."""
import pathlib,sys,os,resource,json,hashlib,copy,lzma,gzip,struct,subprocess,time,shutil
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D))
os.nice(15);os.sched_setaffinity(0,{0,1});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648))
import sm70_decoder_stream_v3 as A
rows=[];started=time.monotonic();F=D/'cpu_fixtures_v3_release179';F.mkdir(exist_ok=False)
def case(name,ok,**extra):
 assert ok,name;rows.append({'case':name,'status':'PASS',**extra})
def reject(name,fn):
 try:fn()
 except (ValueError,RuntimeError,KeyError,TypeError,BrokenPipeError)as e:case(name,True,reason=str(e));return
 raise AssertionError('unexpected accepted '+name)
def line(op,mem=None,imm=0,dst='R1',src='R2'):
 pre='0 3 '+('1 '+dst if dst else'0')+' '+op+' '+('1 '+src if src else'0')
 return pre+(' '+str(mem[0])+' '+str(mem[1])+' '+' '.join(mem[2])if mem else' 0')+' '+str(imm)
def decode(s,l,sh=0x40000000,lo=0x50000000):
 s.reset();s.configure_headers({'shmem base_addr':hex(sh),'local mem base_addr':hex(lo)});s.records([l],3,0);return s.last_batch[0]
for profile,cfg in [('DTC','DTC_DM'),('DTC','DTC_DH'),('DTC','DTC_CM'),('DTC','DTC_CH'),('EP','EP_R5')]:
 with A.Session(profile,cfg)as s:
  p=cfg+':'
  x=decode(s,line('IADD3'));case(p+'integer_operands_real_native',x['op_category']==6 and x['operand_type']==0 and x['dst']==[2]and x['src']==[3]and x['latency_assignment']==2)
  x=decode(s,line('FFMA'));case(p+'FP32_real_config',x['op_category']==5 and x['latency_assignment']==2 and x['initiation_assignment']==2)
  x=decode(s,line('DADD'));case(p+'DP_real_config',x['op_category']==4 and x['latency_assignment']==8 and x['initiation_assignment']==4)
  x=decode(s,line('MUFU.SIN'));case(p+'MUFU_real_variant',x['special_op']==11 and x['latency_assignment']==20)
  x=decode(s,line('HFMA2'));case(p+'half_precision_native_initiation_assignment',x['initiation_assignment']==1)
  for op,space,load,store in [('LDG.E.32',11,True,False),('LDL.32',2,True,False),('LDS.32',3,True,False),('STG.E.32',11,False,True),('STL.32',2,False,True),('STS.32',3,False,True)]:
   x=decode(s,line(op,(4,0,['1000','1004'])));case(p+op+':actual_memory_class',x['space']==space and x['is_load']==load and x['is_store']==store and x['data_size']==4 and x['addresses']==[4096,4100])
  x=decode(s,line('LDG.E.STRONG.GPU',(4,0,['1000','1004'])));case(p+'LDG_native_bypass_cache',x['cache_op']==6)
  x=decode(s,line('STG.STRONG.GPU',(4,0,['1000','1004'])));case(p+'store_profile_specific_scope',x['cache_op']==(6 if profile=='DTC'else 1))
  for op,space in [('ATOMG.ADD',11),('ATOMS.ADD',3)]:
   x=decode(s,line(op,(4,0,['1000','1004'])));case(p+op+':atomic_class_no_atomic_execution',x['is_atomic']and x['is_load']and x['space']==space and x['generated_transactions']==0)
  x=decode(s,line('LDC'));case(p+'constant_native_descriptor',x['const_operand']and x['space']==8 and x['data_size']==4)
  for addr,space in [('1000',11),('40000000',3),('50000000',2)]:
   x=decode(s,line('LD',(4,0,[addr,addr])));case(p+'generic_'+addr,x['space']==space)
  x=decode(s,line('LD',(4,0,['1000','1004'])),0,0);case(p+'generic_native_missing_base_fallback_exposed',x['space']==3)
  x=decode(s,line('BAR.SYNC',imm=3,dst='',src=''));case(p+'named_barrier_exact_historical_difference',x['bar_type']==1 and x['bar_id']==(3 if profile=='DTC'else 0))
  x=decode(s,line('BAR.ARV',imm=3,dst='',src=''));case(p+'arrive_profile_exact_difference',x['bar_type']==(2 if profile=='DTC'else 1)and x['bar_id']==(3 if profile=='DTC'else 0))
  for op,category in [('BRA',100),('CALL',100),('RET',100),('EXIT',17)]:
   x=decode(s,line(op,dst='',src=''));case(p+op+':control_metadata_only',x['op_category']==category and not x['issued'])
  x=decode(s,line('LDG.E.32',(4,0,['1000','1004'])))
  if profile=='EP':case(p+'actual_EP_plain_LDG_predicate',x['ep_plain_ldg']is True)
  x=decode(s,line('LDG.BOGUS',(4,0,['1000','1004'])));case(p+'native_suffix_validation_limit_recorded',x['space']==11,scope='Actual native method accepts this suffix; not full-SASS/hardware qualification.')
  reject(p+'undefined_opcode',lambda:decode(s,line('NOT_AN_OPCODE')))
  reject(p+'unmodeled_register_namespace',lambda:decode(s,line('IADD3',dst='UR1')))
  reject(p+'missing_required_memory_descriptor',lambda:decode(s,line('LDG.E.32')))
  reject(p+'foreign_trailing_schema',lambda:decode(s,line('IADD3')+' ADA8'))
# Native BAR assertion must be tested in its own owned child (never suppress or modify it).
r=subprocess.run([str(D/'DTC/decoder_frontend'),str(D/'DTC_DH/decoder_reachable.config')],input='H 0 0\n3 0 1\n'+line('BAR.SYNC',imm=16,dst='',src='')+'\n',capture_output=True,text=True,timeout=10)
case('DTC_actual_native_invalid_barrier16_asserts',r.returncode!=0 and 'bar_id < 16'in r.stderr,returncode=r.returncode,stderr=r.stderr)
reject('EP_with_DTC_configuration_refused',lambda:A.Session('EP','DTC_DH'))
# Actual Session checks private copied fullconfig/projection bytes before any child launch.
Q=F/'tamper_package';Q.mkdir();shutil.copyfile(D/'CONFIG_PROJECTIONS_V2.json',Q/'CONFIG_PROJECTIONS_V2.json');shutil.copytree(D/'DTC_DH',Q/'DTC_DH')
p=Q/'DTC_DH/decoder_reachable.config';p.write_bytes(p.read_bytes()+b'# changed\n')
old=A.D;A.D=Q
try:reject('projected_config_hash_drift_refused_before_decode',lambda:A.Session('DTC','DTC_DH'))
finally:A.D=old
H=b'-kernel name = CPU_fixture\n-kernel id = 1\n-grid dim = (1,1,1)\n-block dim = (2,1,1)\n-shmem = 0\n-nregs = 8\n-binary version = 70\n-cuda stream id = 0\n-shmem base_addr = 0x40000000\n-local mem base_addr = 0x50000000\n-accelsim tracer version = 3\n#traces format = synthetic only\n'
body=H+b'#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = 3\n0 3 1 R1 IADD3 2 R2 R3 0 0\n10 3 1 R4 LDG.E.32 1 R1 4 0 1000 1004 0\n20 3 0 EXIT 0 0 0\n#END_TB\n'
def meta(b,cfg,kind='traceg',comp='text',rel=None):
 x={'profile':'EP'if cfg=='EP_R5'else'DTC','configuration_profile':cfg,'kind':kind,'compression':comp,'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'max_decoded_bytes':2**30}
 if rel:x['relative_path']=rel
 return x
for profile,cfg in [('DTC','DTC_DH'),('EP','EP_R5')]:
 with A.Session(profile,cfg)as s:
  results=[]
  for enc,b in [('text',body),('xz',lzma.compress(body)),('gzip',gzip.compress(body))]:
   o=s.begin(meta(b,cfg,comp=enc))
   for i in range(0,len(b),7):o.feed(b[i:i+7])
   x=o.end();results.append(x)
   case(cfg+':literal_'+enc+'_to_real_decoded_metadata',x['actual_native_decoder_records']==3 and x['decoded_text_sha256']==hashlib.sha256(body).hexdigest()and x['literal_native_bytes_sha256']==hashlib.sha256(b).hexdigest()and x['kernel_scheduler_clock_or_scientific_authority_called']is False)
  case(cfg+':decoded_metadata_digest_container_independent',len({x['decoded_metadata_sha256']for x in results})==1)
  o=s.begin(meta(body,cfg));reject(cfg+':interleaved_object_context_refused',lambda:s.begin(meta(body,cfg)));o.feed(body);o.end()
  b=b'MemcpyHtoD,0x1000,8\nkernel-1.traceg\n';o=s.begin(meta(b,cfg,kind='cmdlist',rel='kernelslist.g'));o.feed(b);x=o.end();case(cfg+':commandlist_not_turned_into_decoder_proof',x['actual_native_decoder_records']==0 and x['ISA_semantic_status'].startswith('COMMANDLIST'))
  b=b'\x00\xffaux literal only\n';o=s.begin(meta(b,cfg,kind='aux',rel='tools/source.bin'));o.feed(b);x=o.end();case(cfg+':binary_aux_literal_hash_only',x['actual_native_decoder_records']==0 and x['decoded_text_sha256']is None)
  reject(cfg+':member_kind_mismatch',lambda:s.begin(meta(body,cfg,kind='aux',rel='kernel-1.traceg')))
  b=lzma.compress(body)[:-8];o=s.begin(meta(b,cfg,comp='xz'));o.feed(b);reject(cfg+':incomplete_XZ_EOF_not_decoder_acceptance',o.end)
# Persistent stdin framing across objects and actual64MiB stored-byte window.
with A.Session('DTC','DTC_DH')as s:
 blank=b'\n'*65536;count=1024;h=hashlib.sha256()
 for _ in range(count):h.update(blank)
 h.update(body);m=meta(body,'DTC_DH');m.update(size=count*len(blank)+len(body),sha256=h.hexdigest())
 o=s.begin(m)
 for _ in range(count):o.feed(blank)
 for i in range(0,len(body),7):o.feed(body[i:i+7])
 x=o.end();case('actual64MiB_literal_window_decoder_context_survives',x['actual_native_decoder_records']==3 and x['wire_bytes']>2**26)
def frame(t,b=b''):return struct.pack('!I',len(b)+1)+t+b
wire=b''
for enc,b in [('text',body),('xz',lzma.compress(body))]:
 wire+=frame(b'B',json.dumps(meta(b,'DTC_DH',comp=enc)).encode())+frame(b'D',b[:17])+frame(b'D',b[17:])+frame(b'E')
wire+=frame(b'Q');r=subprocess.run(['/usr/bin/python3','-B',str(D/'sm70_decoder_stream_v3.py')],input=wire,capture_output=True,timeout=20);case('two_stored_objects_one_framed_session',r.returncode==0 and len(r.stdout.splitlines())==2,stderr=r.stderr.decode())
out={'schema':'SM70_REAL_EP_R5_DTC_CAP1M_METADATA_DECODER_CPU_FIXTURES_V2','status':'PASS','case_count':len(rows),'cases':rows,'elapsed_seconds':time.monotonic()-started,'profiles_completed':['DTC_DM','DTC_DH','DTC_CM','DTC_CH','EP_R5'],'actual_original_parser_decoder_Core_setactive_OptionParser_setlatency_executed':True,'any_model_clock_cycle_issue_kernel_scheduler_scientific_budget_or_GPU_driver_execution':False,'source_trace_body_or_new_header_reads':0,'all_payload_bytes_synthetic':True,'CPU_affinity':[0,1],'nice':os.getpriority(os.PRIO_PROCESS,0),'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'adapter_sha256':hashlib.sha256((D/'sm70_decoder_stream_v3.py').read_bytes()).hexdigest()}
p=D/'LEGACY179_RELEASE_RESULT_V3.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(rows),'receipt_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
