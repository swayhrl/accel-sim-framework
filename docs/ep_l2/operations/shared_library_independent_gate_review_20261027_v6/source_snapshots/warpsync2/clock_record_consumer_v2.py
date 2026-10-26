#!/usr/bin/env python3
"""Strict CPU consumer candidate for existing ADA8 plain-WARPSYNC records.
No GPU, simulator, latency model, qualification grant or application execution.
"""
import argparse,collections,csv,hashlib,json,lzma,pathlib,re
PROFILE='ADA8_CLOCK7390_HTOD2048_PLAIN_WARPSYNC_SOURCEQA_V2_CANDIDATE'
PRODUCER_SHA='77edc9b58a1575ea0de5f7fd250546cc595e69b6c820c5dc2dc447fe8385e4a5'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def opcode(s):
 t=s.split();need(bool(t),'empty static SASS');return t[1]if t[0].startswith('@')else t[0]
def namespace(r):return 0<=r<255 or 256<=r<319 or 320<=r<327 or 328<=r<335
def parse_record(line):
 t=line.split();i=0
 def take(base=10):
  nonlocal i
  need(i<len(t),'truncated record');v=int(t[i],base);i+=1;return v
 pc=take(16);mask=take(16);nd=take();need(0<=nd<=8,'destination count')
 def regs(n):
  nonlocal i
  out=[]
  for _ in range(n):
   need(i<len(t)and re.fullmatch(r'R[0-9]+',t[i]),'register syntax');r=int(t[i][1:]);i+=1;need(namespace(r),'register namespace');out.append(r)
  return out
 dst=regs(nd);need(i<len(t),'missing opcode');op=t[i];i+=1;ns=take();need(0<=ns<=24,'source count');src=regs(ns)
 width=take();need(width in [0,1,2,4,8,16],'unsupported explicit memory width');lanes=[j for j in range(32)if mask>>j&1];addresses={}
 if width:
  mode=take();need(mode in [0,1,2],'address mode')
  if mode==0:addresses={j:take(16)for j in lanes}
  elif mode==1:
   base=take(16);stride=take();addresses={j:base+k*stride for k,j in enumerate(lanes)}
  else:
   base=take(16)
   for k,j in enumerate(lanes):
    if k:base+=take()
    addresses[j]=base
 imm=take();need(i<len(t)and t[i]=='ADA8','exact ADA8 only');i+=1
 active=take(16);pred=take(16);bank=take();offset=take();qualified=take();cw=take();cmode=take()
 need(all(0<=v<=0xffffffff for v in [mask,active,pred]),'mask width');need(pred&~active==0 and mask==(active&pred),'active/predicate mask join')
 need(active>0,'no hardware instrumentation record can have zero active lanes')
 need(qualified==1 and -1<=bank<=31 and 0<=offset<=0xffffffff,'static qualification/bank/offset')
 need((bank==-1 and cw==0)or(bank>=0 and cw in [1,2,4,8,16]),'constant width')
 need(cmode==int(bank>=0),'constant mode')
 constants={j:take()for j in lanes}if bank>=0 else {}
 kind=take();need(kind in [0,3],'embedded CALL/RET or unknown control requires separate profile')
 targets={j:take()for j in lanes}if kind else {}
 need(i==len(t),'trailing record fields');need(0<=pc<2**64 and pc%16==0,'full64 PC range/alignment')
 need(all(0<=v<2**64 for v in addresses.values()),'memory address range')
 need(all(0<=v<=0xffffffff for v in constants.values()),'constant offset range')
 need((op=='WARPSYNC')==(kind==3),'plain WARPSYNC/control-kind bijection')
 need(not op.startswith('WARPSYNC.')and not op.startswith('BAR.WARP'),'unsupported WARPSYNC variant or arrive/wait')
 if kind==3:need(bank==-1 and width==0 and not dst,'control/constant/address payload alias')
 return dict(pc=pc,mask=mask,active=active,pred=pred,dst=dst,src=src,opcode=op,width=width,addresses=addresses,imm=imm,bank=bank,offset=offset,cw=cw,constants=constants,kind=kind,targets=targets)
class Warp:
 def __init__(self,physical,cta,warp,io):
  need(0<physical<=0xffffffff and physical&(physical+1)==0,'physical contiguous lane mask')
  self.physical=physical;self.exited=0;self.pending={};self.counts=collections.Counter();self.cta=cta;self.warp=warp;self.io=io;self.next=None;self.base=None;self.d={j:256 for j in range(32)if physical>>j&1}
 def source_check(self,r,s):
  rpc=s['pc']
  if self.next is None:
   self.base=r['pc']-rpc;self.next={j:self.base for j in self.d}
  need(r['pc']-rpc==self.base,'loaded code base changed inside warp')
  for j in self.d:
   if r['active']>>j&1:need(self.next[j]==r['pc'],'clock exact per-lane source PC frontier')
  self.counts['PC_EXEC_'+str(rpc)]+=r['mask'].bit_count()
  memory={176:8,208:4,224:4,304:4,320:4,448:4,464:4,496:4,576:4,640:4,752:8}
  if r['mask']and rpc in memory:
   need(r['width']==memory[rpc]and set(r['addresses'])=={j for j in self.d if r['mask']>>j&1},'missing exact source memory lane')
   for lane,addr in r['addresses'].items():
    tid=self.warp*32+lane;bid=self.cta[0]
    if rpc in [208,224]:expected=self.io['input_base']+4*(tid+(256 if rpc==224 else 0))
    elif rpc in [176,752]:
     index=bid+(64 if rpc==752 else 0);base=addr-8*index
     need(base>=0,'negative timer base');self.io.setdefault('timer_base',base);expected=self.io['timer_base']+8*index
    elif rpc==640:
     base=addr-4*bid;need(base>=0,'negative output base');self.io.setdefault('output_base',base);expected=self.io['output_base']+4*bid
    else:
     shared=self.io['shared_bases'];key=self.cta
     if rpc==304:
      base=addr-4*tid;need(base>=0,'negative shared base');shared.setdefault(key,base)
     need(key in shared,'shared read/write before source initialization')
     index=tid
     if rpc==320:index+=256
     elif rpc==464:index+=self.d[lane]
     elif rpc==576:index=0
     expected=shared[key]+4*index
    need(addr==expected,'clock exact source/observed input memory address join')
  elif r['mask']:need(r['width']==0,'memory operand on nonmemory source instruction')
  if rpc==496:need(r['mask']==0,'ascending float input minimum source rule has no conditional shared store')
  for j in self.d:
   if not(r['active']>>j&1):continue
   if r['opcode']=='EXIT'and r['mask']>>j&1:self.next[j]=None
   elif r['opcode']=='BRA'and r['mask']>>j&1:self.next[j]=self.base+int(re.search(r'0x([0-9a-fA-F]+)',s['sass'])[1],16)
   else:self.next[j]=r['pc']+16
   if rpc==528 and r['mask']>>j&1:self.d[j]//=2
 def consume(self,r,s):
  need(not((r['active']|r['pred']|r['mask'])&~self.physical),'nonexistent physical lane')
  need(not r['active']&self.exited,'active record after lane EXIT')
  need(r['opcode']==opcode(s['sass'])and r['src']==s['src']and r['dst']==s['dst'],'exact static opcode/dependencies')
  need(not any(r['opcode'].startswith(x)for x in ['CALL','RET','BRX','JMX','TEX','TLD','SULD','SUST','SUATOM','LDGSTS','CPASYNC','UTMA','WGMMA']),'uncomposed specialist domain')
  need((r['opcode']=='WARPSYNC')==(s['kind']==3),'static/dynamic control kind')
  self.source_check(r,s)
  if r['bank']>=0:
   need(s['bank']==r['bank']and s['offset']==r['offset']and s['cw']==r['cw'],'bank0/direct constant identity')
   need(all(v==r['offset']for v in r['constants'].values()),'indexed bank requires separate dynamic-offset proof')
  else:need(s['bank']==-1,'missing constant operand')
  # Active lanes visit the PC even if the SASS predicate is false.
  for lane in range(32):
   if r['active']>>lane&1 and lane in self.pending:
    need(r['pc']==self.pending.pop(lane),'WARPSYNC per-lane next PC must be original PC+16')
  if r['kind']==3:
   values=set(r['targets'].values())
   if r['mask']:
    need(len(values)==1,'nonuniform named participant values')
    participant=next(iter(values))
    need(participant==s['ctrl_static'],'dynamic named mask must equal static control_static immediate')
    need(0<participant<=0xffffffff and participant==r['mask'],'strict profile requires named mask == executing mask')
    need(not participant&self.exited,'participant already exited')
    for lane in r['targets']:self.pending[lane]=r['pc']+16
    self.counts['warp_drain_requests']+=1
    self.counts['WARPSYNC_named_lane_instances']+=r['mask'].bit_count()
   else:need(not r['targets'],'zero mask has no named tails')
   self.counts['WARPSYNC_records']+=1
  if r['opcode']=='EXIT':
   need(not any(r['mask']>>lane&1 for lane in self.pending),'EXIT with unresolved WARPSYNC successor')
   self.exited|=r['mask']
  self.counts['source_sass_records']+=1;self.counts['executing_lane_instances']+=r['mask'].bit_count();self.counts['zero_mask_records']+=r['mask']==0
 def finish(self):
  need(not self.pending,'EOF with unclosed WARPSYNC successor');need(self.exited==self.physical,'EOF without every physical lane EXIT')
  return dict(self.counts)
def static_admission(manifest):
 need(isinstance(manifest.get('instructions'),list)and manifest['instructions'],'empty manifest')
 keys=set();sync=[]
 for r in manifest['instructions']:
  k=(r['function'],r['pc']);need(k not in keys,'duplicate function/relative PC');keys.add(k);op=opcode(r['sass'])
  need(not any(op.startswith(x)for x in ['CALL','RET','BRX','JMX','TEX','TLD','SULD','SUST','SUATOM','LDGSTS','CPASYNC','UTMA','WGMMA']),'static specialist composition missing')
  if op.startswith('WARPSYNC')or op.startswith('BAR.WARP'):
   need(op=='WARPSYNC','EXCLUSIVE or split arrive/wait not admitted')
   m=re.fullmatch(r'(?:@!?P[0-6]\s+)?WARPSYNC\s+(0x[0-9a-fA-F]+|R(?:[0-9]+)|UR(?:[0-9]+));?',r['sass'].strip())
   need(m is not None,'unknown WARPSYNC operand grammar')
   v=m[1].rstrip(';')
   if v.startswith('0x'):need(0<=int(v,16)<=0xffffffff,'mask immediate range')
   sync.append(k)
 need(bool(sync),'no plain WARPSYNC sites')
 return sync
def load_static_journal(path,manifest,expected_context,expected_function):
 static_admission(manifest)
 original={(r['function'],r['pc']):r for r in manifest['instructions']}
 need(len(original)==len(manifest['instructions'])==50,'exact original 50 unique instruction keys')
 absolute={};bases={};seen=set()
 lines=pathlib.Path(path).read_text().splitlines()
 need(len(lines)==50,'static journal complete 50-row cardinality including unexecuted PC784')
 for line in lines:
  t=line.split('\t');need(len(t)==15 and t[14]=='ADA_STATIC_CTX_FUNCTION_V2','static journal exact V2 ctx/function schema; legacy12 rejected')
  need(all(re.fullmatch(r'[0-9a-f]{1,16}',t[i])for i in [0,1,12,13]),'static canonical hexadecimal')
  apc=int(t[0],16);rpc=int(t[1],16);fn=t[2];key=(fn,rpc)
  need(0<apc<2**64 and apc%16==0 and rpc%16==0,'static full64 aligned absolute/relative PC')
  need(key not in seen,'duplicate original function/relative PC');seen.add(key)
  need(int(t[12],16)==expected_context>0 and int(t[13],16)==expected_function>0,'static context/CUfunction must join paired lifecycle launch')
  need(t[7]=='1','unqualified loaded instruction');r=original.get(key)
  need(r is not None and re.sub(r'[\s;]','',r['sass'])==re.sub(r'[\s;]','',t[3]),'loaded SASS/frozen owner mismatch')
  base=apc-rpc;need(0<base<2**64 and (fn not in bases or bases[fn]==base),'loaded owner base changed')
  bases[fn]=base;need(apc not in absolute,'overlapping loaded function/absolute PC')
  need(all(re.fullmatch(r'-?(?:0|[1-9][0-9]*)',t[i])for i in [4,5,6,8,9]),'static canonical decimal operand fields')
  cb=re.search(r'c\[\s*(0x[0-9a-fA-F]+|\d+)\s*\]\[\s*(0x[0-9a-fA-F]+|\d+)\s*\]',r['sass'])
  op=opcode(r['sass'])
  if cb:
   expected_width=8 if op.startswith('IMAD.WIDE')or'.64'in op else 4
   need(int(t[4])==int(cb[1],0)and int(t[5])==int(cb[2],0)and int(t[6])==expected_width,'static exact CBANK identity/width')
  else:need('c['not in r['sass']and t[4]=='-1'and t[5]=='0'and t[6]=='0','indexed/unknown constant input outside exact profile')
  kind=int(t[8]);control=int(t[9])
  need(kind==(3 if op=='WARPSYNC'else 0),'static control kind mismatch')
  if kind==3:
   operand=re.fullmatch(r'WARPSYNC\s+(0x[0-9a-fA-F]+);?',r['sass'].strip())
   need(operand is not None and control==int(operand[1],16)==0xffffffff,'static control_static must equal exact SASS full32 immediate')
  else:need(control==0,'ordinary instruction control_static must be zero')
  need(not t[10]and not t[11],'CALL summary outside minimum profile')
  absolute[apc]={**r,'kind':kind,'ctrl_static':control,'bank':int(t[4]),'offset':int(t[5]),'cw':int(t[6]),'context_handle':int(t[12],16),'function_handle':int(t[13],16)}
 need(seen==set(original),'loaded static original keyset exact completeness')
 need(len(absolute)==50 and len(bases)==1,'single owner unique absolute 50-key mapping')
 return absolute
def validate_capture(root,manifest,plan):
 root=pathlib.Path(root);need(plan['schema']=='WARPSYNC_PLAIN_FUTURE_CAPTURE_CONTRACT_V2','plan schema')
 need(manifest['binary_sha256']=='9f3d1c80c2a5c1b7d6d7c3c41766e2d3ea1df7287777f48c2b137f4f01cf7e17','single exact clock binary only')
 need(hashlib.sha256(json.dumps(manifest['instructions'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()=='2c8516ff03ab72a75a1f62650285b78a0df28ebc43d67a65882e0cb4fb19cd98','exact clock static instruction identity')
 need(plan['expected_launch_count']==1,'single exact source launch')
 need(plan['producer_sha256']==PRODUCER_SHA,'wrong producer profile')
 need(type(plan['expected_launch_count'])is int and 0<plan['expected_launch_count']<=10000,'bounded launch count')
 need(type(plan['max_live_warp_states'])is int and 0<plan['max_live_warp_states']<=100000,'bounded state policy')
 need(type(plan['max_uncompressed_bytes_per_kernel'])is int and 0<plan['max_uncompressed_bytes_per_kernel']<=17179869184,'bounded expanded byte policy')
 execution=json.loads((root/'EXECUTION.json').read_text());need(execution['exit_code']==0 and execution['tool_sha256']==PRODUCER_SHA and execution['binary_sha256']==manifest['binary_sha256']==plan['binary_sha256'],'execution/binary/tool binding')
 commandlists=list((root/'traces').glob('kernelslist_ctx_*'));need(len(commandlists)==1,'one context commandlist required')
 names=[s.strip()for s in commandlists[0].read_text().splitlines()if s.strip()and not s.startswith('Memcpy')]
 need(names and len(names)==len(set(names))==plan['expected_launch_count'],'source launch count/duplicate')
 need(all(pathlib.PurePosixPath(n).name==n and re.fullmatch(r'kernel-\d+-ctx_0x[0-9a-fA-F]+\.trace\.xz',n)for n in names),'unsafe raw member')
 files={p.name:p for p in(root/'traces').glob('kernel*.trace.xz')};need(set(names)==set(files),'missing or extra raw trace')
 need(len({re.search(r'ctx_(0x[0-9a-fA-F]+)',n)[1]for n in names})==1,'multiple context identities')
 launch=[line.split('\t')for line in(root/'traces/ada-lifecycle.tsv').read_text().splitlines()if line.startswith('LAUNCH_')]
 need(len(launch)==2 and [t[0]for t in launch]==['LAUNCH_ENTRY','LAUNCH_EXIT']and all(len(t)==10 for t in launch),'single paired lifecycle static join')
 need(all(re.fullmatch(r'[0-9a-f]{1,16}',t[i])for t in launch for i in [3,5]),'lifecycle context/function hexadecimal')
 need(launch[0][3:8]==launch[1][3:8] and launch[0][1:3]==launch[1][1:3]and launch[0][9]=='-1'and launch[1][9]=='0','lifecycle pair identity for static join')
 ctx=int(launch[0][3],16);function_handle=int(launch[0][5],16)
 need(ctx>0 and function_handle>0 and launch[0][6]=='_Z14timedReductionPKfPfPl','exact context/function handle join target')
 need(commandlists[0].name=='kernelslist_ctx_0x%x'%ctx and all(re.search(r'ctx_0x([0-9a-f]+)',n)[1]=='%x'%ctx for n in names),'static/lifecycle/raw context binding')
 static=load_static_journal(root/'traces/ada-static.tsv',manifest,ctx,function_handle)
 need(type(plan['observed_input_destination'])is int and 0<plan['observed_input_destination']<2**64-2048,'fresh new-profile capsule input destination')
 clockio={'input_base':plan['observed_input_destination'],'shared_bases':{}}
 total=collections.Counter();kernels=[];streamset=set()
 for name in names:
  header={};warps={};counts=collections.Counter();expanded=0;started_records=False
  with lzma.open(files[name],'rt')as inp:
   for line in iter(lambda:inp.readline(65537),''):
    need(len(line.encode())<=65536,'bounded raw line length')
    expanded+=len(line.encode());need(expanded<=plan['max_uncompressed_bytes_per_kernel'],'bounded input exceeded')
    if not line.strip()or line.startswith('#'):continue
    if line.startswith('-'):
     need(not started_records,'header after records');need(' = 'in line,'header grammar');k,v=line[1:].strip().split(' = ',1);need(k not in header,'duplicate header');header[k]=v.strip();continue
    need(re.match(r'^\d+ \d+ \d+ \d+ ',line)is not None,'malformed nonheader/record')
    started_records=True;words=line.split(maxsplit=4);cta=tuple(map(int,words[:3]));warp=int(words[3]);r=parse_record(words[4])
    need(header.get('binary version')=='89'and header.get('accelsim tracer version')=='8','exact SM89/ADA8 header')
    grid=tuple(map(int,re.findall(r'\d+',header['grid dim'])));block=tuple(map(int,re.findall(r'\d+',header['block dim'])))
    need(grid==(64,1,1)and block==(256,1,1)and header['kernel name']=='_Z14timedReductionPKfPfPl'and header.get('shmem')=='2048','exact64x256 shared2048 source launch/function');need(len(grid)==len(block)==3 and all(x>0 for x in grid+block),'launch dimensions');threads=block[0]*block[1]*block[2];need(threads<=1024,'block limit')
    need(all(0<=cta[i]<grid[i]for i in range(3))and 0<=warp<(threads+31)//32,'CTA/warp bounds')
    state=warps.setdefault((cta,warp),Warp((1<<min(32,threads-warp*32))-1,cta,warp,clockio));need(len(warps)<=plan['max_live_warp_states'],'bounded state cap')
    need(r['pc']in static,'unknown loaded absolute PC');need(static[r['pc']]['function']==header['kernel name'],'minimum profile root function only')
    state.consume(r,static[r['pc']]);counts['records']+=1
  need(warps,'empty trace')
  grid=tuple(map(int,re.findall(r'\d+',header['grid dim'])));block=tuple(map(int,re.findall(r'\d+',header['block dim'])));threads=block[0]*block[1]*block[2]
  need(len(warps)==grid[0]*grid[1]*grid[2]*((threads+31)//32),'missing whole CTA/warp')
  for state in warps.values():total.update(state.finish())
  streamset.add(header.get('cuda stream id'));need(None not in streamset,'stream header required')
  kernels.append({'name':name,'records':counts['records'],'warps':len(warps),'raw_sha256':sha(files[name])})
 need(len(streamset)==1,'concurrent stream domain not admitted')
 statsfiles=list((root/'traces').glob('stats_ctx_*'));need(len(statsfiles)==1,'one stats file')
 with statsfiles[0].open()as f:stats=list(csv.reader(f))[1:]
 need(len(stats)==len(names)and len({r[0].strip()for r in stats})==len(names),'stats exact count')
 stats={r[0].strip():int(r[-1])for r in stats};need(set(stats)==set(names)and all(stats[r['name']]==r['records']for r in kernels),'stats record counts')
 expected={pc:16384 for pc in range(0,321,16)}
 expected.update({80:64,96:64,144:64,176:64,336:0,352:16384,368:147456,384:147456,400:147456,416:114752,432:32704,448:32704,464:32704,480:32704,496:0,512:147456,528:147456,544:147456,560:131072,576:64,592:64,608:16384,624:64,640:64,656:16384,672:16320,688:64,704:64,720:64,736:64,752:64,768:64,784:0})
 need(set(expected)=={r['pc']for r in manifest['instructions']},'source oracle PC set')
 need(all(total['PC_EXEC_'+str(pc)]==n for pc,n in expected.items()),'source-derived exact executed-lane counts')
 need(total['WARPSYNC_records']==512 and total['WARPSYNC_named_lane_instances']==16384 and total['warp_drain_requests']==512,'exact per-source whole-warp sync counts')
 need(len(clockio['shared_bases'])==64 and 'timer_base'in clockio and 'output_base'in clockio,'missing source memory intervals')
 ranges=sorted([(clockio['input_base'],2048),(clockio['output_base'],256),(clockio['timer_base'],1024)])
 need(all(ranges[i][0]+ranges[i][1]<=ranges[i+1][0]for i in range(2)),'simultaneously-live source allocations overlap')
 return {'schema':'WARPSYNC_PLAIN_CPU_STRUCTURAL_REVIEW_V2','status':'CPU_STRUCTURAL_PASS_PENDING_DYNAMIC_ROOT_ADMISSION','profile':PROFILE,'counts':dict(total),'kernels':kernels,'trace_qualified':False,'consumer_or_science_qualified':False,'hardware_latency_calibrated':False,'source_input_runtime_oracle_closed_by_this_check':False,'sourceQA_observed_control_and_memory_rules_checked':True,'static_complete_unique_50_keys':True,'static_context_handle':ctx,'static_CUfunction_handle':function_handle,'static_control_static_joined_dynamic_named_masks':True,'numerical_result_not_read_back':True,'timer_not_numerical_or_performance_qualification':True}
def main():
 p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('manifest');p.add_argument('plan');p.add_argument('--output',required=True);a=p.parse_args()
 result=validate_capture(a.attempt,json.loads(pathlib.Path(a.manifest).read_text()),json.loads(pathlib.Path(a.plan).read_text()))
 with pathlib.Path(a.output).open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
if __name__=='__main__':main()
