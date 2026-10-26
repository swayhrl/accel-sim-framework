#!/usr/bin/env python3
"""Persistent CPU real-native metadata decoder. No path opening for trace/aux payload.
feed receives literal stored-object bytes, optionally xz/gzip compressed member bytes.
Does not enter an engine/kernel/scheduler/cycle or any scientific authority.
"""
import pathlib,json,hashlib,subprocess,os,resource,select,struct,sys,collections,re
import format_envelope_v3 as F
D=pathlib.Path(__file__).resolve().parent
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def classify_member(relative_path):
 p=pathlib.PurePosixPath(relative_path);need(not p.is_absolute()and '..'not in p.parts,'safe frozen relative member')
 n=p.name;compression='xz'if n.endswith('.xz')else'gzip'if n.endswith('.gz')else'text'
 base=n[:-3]if compression in ['xz','gzip']else n
 if re.fullmatch(r'kernelslist(?:\.[A-Za-z0-9_-]+)*',base):kind='cmdlist'
 elif base.startswith('kernel')and base.endswith('.traceg'):kind='traceg'
 elif base.startswith('kernel')and base.endswith('.trace'):kind='trace'
 elif base.endswith('.tracez'):kind='UNSUPPORTED_TRACEZ'
 else:kind='aux';compression='literal'
 return {'kind':kind,'compression':compression}
def cpu_only_child_limits():
 os.sched_setaffinity(0,{0,1});n=os.getpriority(os.PRIO_PROCESS,0)
 if n<15:os.nice(15-n)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
def dedicated_cli_parent_limits(budget_bytes):
 need(type(budget_bytes)is int and 128*2**20<=budget_bytes<=16*2**30,'explicit dedicated CLI parent address-space budget')
 soft,hard=resource.getrlimit(resource.RLIMIT_AS);cap=budget_bytes if soft==resource.RLIM_INFINITY else min(soft,budget_bytes)
 resource.setrlimit(resource.RLIMIT_AS,(cap,hard));return cap
class Session(F.Session):
 def __init__(self,profile,configuration_profile,parent_budget_bytes=None):
  self.caller_RLIMIT_AS_snapshot=resource.getrlimit(resource.RLIMIT_AS);self.declared_parent_budget=parent_budget_bytes
  if parent_budget_bytes is not None:
   need(type(parent_budget_bytes)is int and parent_budget_bytes>0,'declared caller memory budget')
   soft=self.caller_RLIMIT_AS_snapshot[0];need(soft!=resource.RLIM_INFINITY and soft<=parent_budget_bytes,'caller must establish its declared parent budget; Session does not modify it')
  projections=json.loads((D/'CONFIG_PROJECTIONS_V2.json').read_text())
  need(configuration_profile in projections,'fixed configuration profile required')
  cfg=projections[configuration_profile];need(cfg['decoder_binary_profile']==profile,'cross-profile config forbidden')
  self.configuration_profile=configuration_profile;self.projection=cfg
  config=D/configuration_profile/'decoder_reachable.config'
  empty=D/profile/'metadata.fixture.traceg'
  need(empty.is_file()and not empty.is_symlink()and empty.stat().st_size==0,'only empty private metadata header carrier allowed')
  need(re.fullmatch(r'[A-Za-z0-9_./-]+',str(empty))is not None,'native carrier pipe path safety')
  need(sha(config)==cfg['projection_sha256'],'projected config drift')
  for row in cfg['configuration_sources']:
   need(sha(D/configuration_profile/pathlib.Path(row['snapshot']).name)==row['sha256'],'full bound configuration snapshot drift')
  pins=json.loads((D/'DECODER_BINARY_PINS_V2.json').read_text());binary=D/profile/'decoder_frontend';need(sha(binary)==pins[profile],'native decoder binary drift')
  super().__init__(profile)
  self.decoder_binary_sha256=pins[profile];self.config_manifest_sha256=sha(D/'CONFIG_PROJECTIONS_V2.json');self.decoder_adapter_sha256=sha(__file__)
  self.p2=subprocess.Popen([str(binary),str(config)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=cpu_only_child_limits)
  self.rx=b'';self.last_batch=[];self.active_object=False;self.current_header_context=None;self.reset()
 def reset(self):
  self.decoded_records=0;self.classifications=collections.Counter();self.metadata_hash=hashlib.sha256();self.header_attached=False
 def read_line(self):
  while b'\n'not in self.rx:
   need(select.select([self.p2.stdout],[],[],30)[0],'decoder channel timeout')
   b=os.read(self.p2.stdout.fileno(),65536)
   if not b:
    err=self.p2.stderr.read(4096)if self.p2.poll()is not None else b''
    raise ValueError('real native decoder ended before complete metadata: '+err.decode(errors='replace'))
   self.rx+=b;need(len(self.rx)<=2**20,'decoder response line cap')
  line,self.rx=self.rx.split(b'\n',1);return line.decode('ascii')
 def configure_headers(self,headers):
  def h(name):
   v=headers.get(name,'0');need(len(v)<=18 and re.fullmatch(r'(?:0x)?[0-9a-fA-F]+',v)is not None,'native header address syntax')
   n=int(v,16);need(0<=n<2**64,'native header address range');return n
  self.p2.stdin.write(('H %x %x\n'%(h('shmem base_addr'),h('local mem base_addr'))).encode());self.p2.stdin.flush()
  need(self.read_line()=='HEADER_OK','real metadata header attachment');self.header_attached=True;self.current_header_context=dict(headers)
 def records(self,lines,version,lineinfo):
  # The prior stricter token/envelope guard executes the original record parser.
  # Then the actual unmodified decoder executes on precisely the same records.
  super().records(lines,version,lineinfo)
  if not lines:return
  need(self.header_attached,'decoder header context must precede first record')
  raw=('%d %d %d\n'%(version,lineinfo,len(lines))+''.join(x+'\n'for x in lines)).encode()
  self.p2.stdin.write(raw);self.p2.stdin.flush();self.last_batch=[]
  for _ in lines:
   x=json.loads(self.read_line())
   need(x['instruction_uid']==0 and x['issued']is False and x['generated_transactions']==0 and x['clock_advanced']is False,'metadata-only invariant')
   root=x['opcode'].split('.')[0]
   key=(root,x['op_category'],x['memory_op'],x['space'],x['cache_op'],x['data_size'],x['bar_type'])
   self.classifications[key]+=1;self.decoded_records+=1
   self.metadata_hash.update(json.dumps(x,sort_keys=True,separators=(',',':')).encode()+b'\n');self.last_batch.append(x)
  need(self.read_line()=='BATCH_OK '+str(len(lines)),'native decoded batch count/EOF')
 def begin(self,meta):
  need(not self.active_object,'previous object not closed; no interleaved decoder contexts')
  need(meta.get('stream_completion_profile',F.PROFILE_ID)==F.PROFILE_ID,'unknown stream completion profile')
  need(meta.get('configuration_profile',self.configuration_profile)==self.configuration_profile,'object configuration binding')
  if 'relative_path'in meta:
   c=classify_member(meta['relative_path']);need(c['kind']==meta['kind'],'frozen member kind mismatch')
   if meta['kind']!='aux':need(c['compression']==meta.get('compression','text'),'stored-member compression mismatch')
  self.reset();self.active_object=True
  return Auxiliary(self,meta)if meta['kind']=='aux'else ObjectStream(self,meta)
 def close(self):
  try:
   if hasattr(self,'p2'):
    try:self.p2.stdin.close()
    except BrokenPipeError:pass
    try:self.p2.wait(timeout=10)
    except subprocess.TimeoutExpired:self.p2.kill();self.p2.wait(timeout=5)
  finally:super().close()
class ObjectStream(F.ObjectStream):
 def __init__(self,s,m):self.decoded_hash=hashlib.sha256();super().__init__(s,m)
 def text(self,b):self.decoded_hash.update(b);super().text(b)
 def geometry(self):super().geometry();self.s.configure_headers(self.headers)
 def end(self):
  r=super().end();need(self.s.decoded_records==r['records'],'every complete record real-decoded exactly once')
  r.update(schema='SM70_REAL_NATIVE_METADATA_DECODER_STREAM_RESULT_V3',configuration_profile=self.s.configuration_profile,
   literal_native_bytes_sha256=r['wire_sha256'],decoded_text_sha256=self.decoded_hash.hexdigest(),
   stored_object_compression=self.encoding,complete_compressed_stream_EOF_CRC_checked=self.encoding!='text',
   decoder_binary_sha256=self.s.decoder_binary_sha256,decoder_adapter_source_sha256=self.s.decoder_adapter_sha256,
   configuration_manifest_sha256=self.s.config_manifest_sha256,
   actual_native_decoder_records=self.s.decoded_records,decoded_metadata_sha256=self.s.metadata_hash.hexdigest(),
   native_decoder_classifications=[{'root':k[0],'op_category':k[1],'memory_op':k[2],'space':k[3],'cache_op':k[4],'data_size':k[5],'bar_type':k[6],'records':n}for k,n in sorted(self.s.classifications.items())],
   ISA_semantic_status='REAL_NATIVE_METADATA_DECODER_ACCEPTED_BOUND_PROFILE'if r['records']else'COMMANDLIST_ENVELOPE_ONLY_REQUIRES_MEMBER_JOIN',
   semantic_boundaries=['Metadata classification/input parsing only; no issue/coalescing/cycle or instruction execution',
   'Native suffix/texture/barrier/generic-fallback behavior is exposed, not hardware or full-SASS semantic qualification',
   'Caller must join commandlist members/object identity/full125 graph and keep scientific acceptance separate'],
   header_context_sha256=hashlib.sha256(json.dumps(self.headers,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
   decoder_attached_header_fields=['shmem base_addr','local mem base_addr'],
   instruction_suffixes_fully_validated_by_native_decoder=False,hardware_timing_or_numerical_qualification=False,
   kernel_scheduler_clock_or_scientific_authority_called=False)
  self.s.active_object=False
  return r
class Auxiliary:
 def __init__(self,s,m):
  need(m.get('compression','literal')in ['literal','text'],'unknown auxiliary literal compression');self.s=s;self.m=dict(m);self.n=0;self.h=hashlib.sha256();self.done=False
  need(type(m['size'])is int and 0<=m['size']<=2**41,'aux literal size')
 def feed(self,b):
  need(not self.done and isinstance(b,bytes)and len(b)<=64*2**20,'aux feed state/frame')
  self.n+=len(b);need(self.n<=self.m['size'],'aux size exceeds frozen');self.h.update(b)
 def end(self):
  need(not self.done,'aux duplicate end');self.done=True
  need(self.n==self.m['size']and self.h.hexdigest()==self.m['sha256'],'aux whole literal size/SHA')
  self.s.active_object=False
  return {'schema':'SM70_REAL_NATIVE_METADATA_DECODER_STREAM_RESULT_V3','kind':'aux','literal_native_bytes_sha256':self.h.hexdigest(),'wire_bytes':self.n,'configuration_profile':self.s.configuration_profile,'actual_native_decoder_records':0,'ISA_semantic_status':'AUX_LITERAL_HASH_ONLY_NO_TRACE_QUALIFICATION','decoded_text_sha256':None,'kernel_scheduler_clock_or_scientific_authority_called':False,'hardware_timing_or_numerical_qualification':False}
def framed_main(parent_memory_budget_bytes=2*2**30):
 dedicated_cli_parent_limits(parent_memory_budget_bytes)
 # Frame length counts tag+payload: B=JSON meta,D=literal native member bytes,E=EOF,Q=quit.
 sessions={};obj=None
 def read(n):
  b=sys.stdin.buffer.read(n);need(len(b)==n,'framed EOF');return b
 try:
  while True:
   h=sys.stdin.buffer.read(4)
   if not h:break
   need(len(h)==4,'frame header EOF');n=struct.unpack('!I',h)[0];need(1<=n<=64*2**20+1,'frame cap')
   b=read(n);tag,payload=b[:1],b[1:]
   if tag==b'B':
    need(obj is None and len(payload)<=65536,'begin state/meta cap');m=json.loads(payload);key=(m['profile'],m['configuration_profile'])
    if key not in sessions:sessions[key]=Session(*key)
    obj=sessions[key].begin(m)
   elif tag==b'D':need(obj is not None,'data without begin');obj.feed(payload)
   elif tag==b'E':need(obj is not None and not payload,'end state');print(json.dumps(obj.end()),flush=True);obj=None
   elif tag==b'Q':need(obj is None and not payload,'quit state');break
   else:raise ValueError('unknown frame tag')
  need(obj is None,'object left open at framed EOF')
 finally:
  for s in sessions.values():s.close()
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--parent-memory-bytes',type=int,default=2*2**30);args=parser.parse_args();framed_main(args.parent_memory_bytes)
