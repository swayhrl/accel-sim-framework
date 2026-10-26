#!/usr/bin/env python3
"""CPU format adapter; never invokes an engine/GPU or opens trace paths.
begin/feed/end consumes caller-owned bytes once. Native record methods are reused.
No full decoder, timing, scheduling, application or scientific qualification.
"""
import pathlib,json,subprocess,hashlib,re,math,lzma,zlib,struct,sys,collections
from compact_completion_v3 import CompactWarpCompletion,uint,PROFILE_ID,MAX_KEYS,MAX_STATE_BYTES
class StreamResourceHold(ValueError):
 def __init__(self,limit):
  self.code='SM70_STREAM_RESOURCE_HOLD_XZ_MEMORY';self.limit_bytes=limit
  super().__init__(self.code+': approved liblzma memory limit '+str(limit)+' bytes (includes overhead; not dictionary bytes or ISA support)')
D=pathlib.Path(__file__).resolve().parent
def need(v,m):
 if not v:raise ValueError(m)
class Session:
 def __init__(self,profile):
  need(profile in ['EP','DTC'],'fixed profile');self.profile=profile
  binding=D/'CURRENT_EFFECTIVE_CONSUMER_PINS_V1.json';self.binding_sha256=hashlib.sha256(binding.read_bytes()).hexdigest();bound=json.loads(binding.read_text())[profile]
  self.consumer_binary_sha256=bound['framework_binary']['sha256']if profile=='DTC'else bound['binary']['sha256']
  self.adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
  pins=json.loads((D/'FRONTEND_BINARY_PINS_V1.json').read_text());p=D/profile/'record_frontend'
  need(hashlib.sha256(p.read_bytes()).hexdigest()==pins[profile],'CPU frontend binary pin')
  self.p=subprocess.Popen([str(p)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1);self.batch=[];self.batchbytes=0;self.objects=0
 def records(self,lines,version,lineinfo):
  if not lines:return
  self.p.stdin.write('%d %d %d\n'%(version,lineinfo,len(lines))+''.join(s+'\n'for s in lines));self.p.stdin.flush()
  reply=self.p.stdout.readline(65537).strip();need(reply=='OK '+str(len(lines)),'native parser frontend '+reply)
 def begin(self,meta):return ObjectStream(self,meta)
 def close(self):
  self.p.stdin.close();self.p.wait(timeout=10);need(self.p.returncode==0,'frontend exit')
 def __enter__(self):return self
 def __exit__(self,*a):self.close()
class ObjectStream:
 def __init__(self,session,meta):
  self.s=session;self.m=dict(meta);self.kind=meta['kind'];need(self.kind in ['cmdlist','trace','traceg'],'member kind')
  self.encoding=meta.get('compression','text');need(self.encoding in ['text','xz','gzip'],'unsupported compressed container; use caller-decoded callback for zstd/tracez')
  self.max_keys=meta.get('max_state_keys',1000000);need(type(self.max_keys)is int and 0<self.max_keys<=MAX_KEYS,'explicit state-key cap');self.max_state_bytes=meta.get('max_state_bytes',MAX_STATE_BYTES);need(type(self.max_state_bytes)is int and 0<self.max_state_bytes<=MAX_STATE_BYTES,'explicit compact-state byte cap');self.expected=meta['size'];need(type(self.expected)is int and 0<=self.expected<=2**41,'wire size bound')
  self.cap=meta.get('max_decoded_bytes',self.expected if self.encoding=='text'else None);need(type(self.cap)is int and 0<self.cap<=2**41,'explicit decoded cap')
  self.sha=hashlib.sha256();self.size=0;self.decoded=0;self.pending=b'';self.lines=0;self.ended=False;self.headers={};self.body=False;self.batch=[];self.bbytes=0;self.version=0;self.li=0;self.state=None;self.current_key=None;self.coord=None;self.warp=None;self.declared=None;self.seen=0;self.last=None;self.intb=False;self.ops=collections.Counter();self.commands=[];self.command_bytes=0;self.max_command_bytes=meta.get('max_command_bytes',4*2**20);need(type(self.max_command_bytes)is int and 0<self.max_command_bytes<=16*2**20,'explicit bounded commandlist metadata bytes <=16MiB');self.record_count=0;self.holds=set()
  self.max_xz_decoder_bytes=meta.get('max_xz_decoder_bytes',64*2**20);need(type(self.max_xz_decoder_bytes)is int and 0<self.max_xz_decoder_bytes<=256*2**20,'explicit Root-selected bounded liblzma memory policy <=256MiB');self.decoder=lzma.LZMADecompressor(memlimit=self.max_xz_decoder_bytes)if self.encoding=='xz'else zlib.decompressobj(31)if self.encoding=='gzip'else None
 def decompress(self,b):
  try:return self.decoder.decompress(b,max_length=2**20)if self.encoding=='xz'else self.decoder.decompress(b,2**20)
  except lzma.LZMAError as exc:
   if self.encoding=='xz'and 'Memory usage limit exceeded'in str(exc):raise StreamResourceHold(self.max_xz_decoder_bytes)from exc
   raise
 def feed(self,b):
  need(not self.ended and isinstance(b,bytes)and len(b)<=64*2**20,'feed type/state/64MiB frame bound');self.size+=len(b);need(self.size<=self.expected,'wire exceeds frozen size');self.sha.update(b)
  if self.encoding=='text':self.text(b);return
  part=self.decompress(b);self.text(part)
  while (not self.decoder.needs_input if self.encoding=='xz'else bool(self.decoder.unconsumed_tail))and not self.decoder.eof:
   part=self.decompress(b''if self.encoding=='xz'else self.decoder.unconsumed_tail);self.text(part)
  need(not self.decoder.unused_data,'trailing/concatenated compressed stream unsupported')
 def text(self,b):
  self.decoded+=len(b);need(self.decoded<=self.cap,'decoded cap')
  # Bound split/list temporaries even when caller feeds one literal64MiB window.
  view=memoryview(b)
  for start in range(0,len(view),65536):
   parts=(self.pending+bytes(view[start:start+65536])).split(b'\n');self.pending=parts.pop()
   for line in parts:
    need(len(line)<=65536,'line cap');self.line(line.decode('ascii'))
   need(len(self.pending)<=65536,'unterminated line cap')
 def flush(self):
  self.s.records(self.batch,self.version,self.li);self.batch=[];self.bbytes=0
 def geometry(self):
  for k in ['kernel name','kernel id','grid dim','block dim','shmem','nregs','binary version','cuda stream id']:need(k in self.headers,'missing header '+k)
  need(self.headers['binary version']=='70','only observed SM70')
  def dims(k):
   v=self.headers[k];need(re.fullmatch(r'\([1-9][0-9]*,[1-9][0-9]*,[1-9][0-9]*\)',v),'dimension grammar')
   return tuple(uint(x,2**31-1,k)for x in v[1:-1].split(','))
  self.grid=dims('grid dim');self.block=dims('block dim')
  need(math.prod(self.block)<=1024,'block limit')
  uint(self.headers['kernel id'],2**32-1,'kernel id')
  uint(self.headers['cuda stream id'],2**64-1,'stream id')
  need(0<uint(self.headers['nregs'],255,'nregs') and uint(self.headers['shmem'],98304,'shmem')<=98304,'SM70 register/shared envelope')
  self.version=uint(self.headers.get('accelsim tracer version','0'),4,'trace version');self.li=uint(self.headers.get('enable lineinfo','0'),1,'lineinfo')
  self.state=CompactWarpCompletion(self.grid,self.block,self.max_keys,self.max_state_bytes)
  if 'accelsim tracer version'not in self.headers:self.holds.add('LEGACY_VERSION0_HEADER_NO_EXPLICIT_SCHEMA; exact record parser still required')
 def closewarp(self):
  if self.warp is not None:
   need(self.declared is not None,'missing declared instruction count')
   need(self.seen==self.declared,'declared instruction count mismatch')
   self.state.require_warp_complete(self.current_key)
  self.warp=None;self.current_key=None;self.declared=None
 def record(self,line):
  t=line.split();offset=(4 if self.version<3 else 0)+self.li
  need(len(t)>offset+3,'record prefix')
  pc=uint(t[offset],2**64-1,'pc',16);mask=uint(t[offset+1],0xffffffff,'mask',16);nd=uint(t[offset+2],1,'dst count')
  oi=offset+3+nd;need(len(t)>oi,'opcode position');root=t[oi].split('.')[0];need(0<len(root)<=64,'opcode root bound')
  if self.kind=='traceg':
   need(self.intb and self.warp is not None and self.declared is not None,'record outside declared warp')
   if self.version<3:need(tuple(uint(x,2**31-1,'legacy CTA')for x in t[:3])==self.coord and uint(t[3],31,'legacy warp')==self.warp,'legacy record CTA/warp join')
   self.seen+=1;need(self.seen<=self.declared,'warp extra record');key=self.current_key
  else:
   need(self.version<3,'raw version>=3 has no inline CTA/warp and needs exact postprocessor route')
   coord=tuple(uint(x,2**31-1,'raw CTA')for x in t[:3]);w=uint(t[3],31,'raw warp');key=self.state.touch_warp(coord,w)
  self.state.apply(key,mask,root);self.ops[root]+=1;self.last=root;self.record_count+=1
  if root in ['TEX','TLD','TLD4','TMML','TXD','TXQ','LDC','LD','ST','ATOM','ATOMG','ATOMS','RED','BAR','MEMBAR','DEPBAR','WARPSYNC','BSSY','BSYNC','BREAK','BRX','JMX','CALL','RET','HMMA','IMMA']:self.holds.add(root+': native metadata decoder is separate from full hardware/model semantics')
  self.batch.append(line);self.bbytes+=len(line)
  if len(self.batch)>=256 or self.bbytes>=2**20:self.flush()
 def line(self,line):
  self.lines+=1
  if self.kind=='cmdlist':
   if not line:return
   self.command_bytes+=len(line)+1;need(self.command_bytes<=self.max_command_bytes,'V3_RESOURCE_COMMANDLIST_BYTES_LIMIT_NOT_ISA_UNSUPPORTED')
   if line.startswith('MemcpyHtoD,'):
    need(re.fullmatch(r'MemcpyHtoD,0x[0-9a-fA-F]+,[0-9]+',line),'memcpy command grammar');need(len(self.commands)<100000,'command count cap');self.commands.append(line)
   elif line.startswith('kernel'):
    need('/'not in line and '\\'not in line and re.fullmatch(r'kernel[A-Za-z0-9_.-]*\.(?:traceg|trace)(?:\.xz)?',line),'unsafe/unsupported kernel command');need(line not in self.commands,'duplicate kernel command');need(len(self.commands)<100000,'command count cap');self.commands.append(line)
   else:raise ValueError('unknown command, native silently ignores; strict adapter refuses')
   return
  if not self.body:
   if not line:return
   if line.startswith('-'):
    need(' = 'in line,'header assignment');k,v=line[1:].split(' = ',1);need(k not in self.headers,'duplicate header');need(len(self.headers)<32,'header field cap');self.headers[k]=v;return
   need(line.startswith('#'),'missing header delimiter');self.geometry();self.body=True
   if line.startswith('#traces'):return
  if not line:return
  if self.kind=='traceg':
   if line=='#BEGIN_TB':
    need(not self.intb,'nested TB');self.intb=True;self.coord=None;self.warp=None;self.current_key=None;return
   if line=='#END_TB':
    need(self.intb and self.coord is not None,'TB closure');self.closewarp();self.intb=False;return
   if line.startswith('thread block = '):
    need(self.intb and self.coord is None,'TB coordinate state');parts=line.split(' = ',1)[1].split(',');need(len(parts)==3,'CTA coordinate dimension')
    self.coord=tuple(uint(x,2**31-1,'CTA')for x in parts);self.state.touch_cta(self.coord,unique=True);return
   if line.startswith('warp = '):
    self.closewarp();w=uint(line.split(' = ',1)[1],31,'warp')
    need(self.intb and self.coord is not None,'warp before CTA');self.current_key=self.state.touch_warp(self.coord,w,unique=True);self.warp=w;return
   if line.startswith('insts = '):
    need(self.warp is not None and self.declared is None,'instruction-count state');self.declared=uint(line.split(' = ',1)[1],2**32-1,'instruction count');need(self.declared>0,'instruction count positive');self.seen=0;return
  self.record(line)
 def end(self):
  need(not self.ended,'duplicate end');self.ended=True
  need(self.size==self.expected,'wire truncated');need(self.sha.hexdigest()==self.m['sha256'],'wire SHA mismatch')
  if self.decoder:need(self.decoder.eof and not self.decoder.unused_data,'compressed EOF/CRC/trailing data')
  need(not self.pending,'final newline required by native PipeReader');self.flush()
  if self.kind=='cmdlist':need(any(s.startswith('kernel')for s in self.commands),'empty commandlist')
  else:
   need(self.body and self.record_count>0,'header/body absent')
   if self.kind=='traceg':need(not self.intb,'whole TB EOF closure')
   self.state.finish()
  completion=self.state.summary()if self.state is not None else {'not_applicable':'COMMANDLIST_NO_INSTRUCTION_COMPLETION'}
  self.state=None;self.decoder=None
  self.s.objects+=1
  return {'schema':'SM70_NATIVE_PARSER_COMPLETION_BITMAP_RESULT_V3','wire_sha256':self.sha.hexdigest(),'wire_bytes':self.size,'decoded_bytes':self.decoded,'kind':self.kind,'profile':self.s.profile,'consumer_pins_manifest_sha256':self.s.binding_sha256,'declared_consumer_binary_sha256':self.s.consumer_binary_sha256,'adapter_source_sha256':self.s.adapter_sha256,'consumer_binary_freshly_rehashed_by_this_callback':False,'format_status':'STRICT_ENVELOPE_REAL_NATIVE_PARSER_PHYSICAL_LANE_COMPLETION_PASS_V3'if self.kind!='cmdlist'else'COMMANDLIST_ENVELOPE_ONLY','records':self.record_count,'headers':self.headers,'opcode_root_counts':dict(self.ops),'ordered_commands':self.commands,'ISA_semantic_status':'HOLD_FULL_DECODER_NOT_EXECUTED','semantic_boundaries':sorted(self.holds),'consumer_binary_executed':False,'simulation_or_GPU_or_science_qualification':False,'stream_completion_profile':PROFILE_ID,'physical_lane_completion':completion,'decompression_resource_policy':{'codec':self.encoding,'Root_selected_liblzma_memlimit_bytes':self.max_xz_decoder_bytes,'default_liblzma_memlimit_bytes':64*2**20,'hard_liblzma_memlimit_bytes':256*2**20,'dictionary_bytes_are_not_total_liblzma_memusage':True,'automatic_fallback':False,'resource_HOLD_is_not_ISA_or_hardware_unsupported':True},'completion_source_sha256':hashlib.sha256(pathlib.Path(__file__).with_name('compact_completion_v3.py').read_bytes()).hexdigest()}
def framed_main():
 """Frame: uint32BE payload length, byte B/D/E/Q + payload. D<=64MiB.
 B JSON exact meta, D binary bytes, E empty finalizes, Q empty stops.
 One object at a time; one persistent native record subprocess per profile.
 """
 sessions={};obj=None
 def read(n):
  b=sys.stdin.buffer.read(n);need(len(b)==n,'framed EOF');return b
 try:
  while True:
   h=sys.stdin.buffer.read(4)
   if not h:break
   need(len(h)==4,'frame header EOF');n=struct.unpack('!I',h)[0];need(1<=n<=64*2**20+1,'frame cap');b=read(n);tag,payload=b[:1],b[1:]
   if tag==b'B':
    need(obj is None and len(payload)<=65536,'begin state/metadata cap');meta=json.loads(payload);profile=meta['profile']
    if profile not in sessions:sessions[profile]=Session(profile)
    obj=sessions[profile].begin(meta)
   elif tag==b'D':need(obj is not None,'data without begin');obj.feed(payload)
   elif tag==b'E':need(obj is not None and not payload,'end state');print(json.dumps(obj.end()),flush=True);obj=None
   elif tag==b'Q':need(obj is None and not payload,'quit state');break
   else:raise ValueError('unknown frame tag')
  need(obj is None,'open object at stream EOF')
 finally:
  for s in sessions.values():s.close()
if __name__=='__main__':framed_main()
