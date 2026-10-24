"""Validate observed supported HtoD source-byte capsules; no device/readback or complete-input claim."""
import argparse,pathlib,json,hashlib,re
PRODUCER_SHA='c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352'
APIS={'cuMemcpyHtoD_v2':False,'cuMemcpyHtoD_v2_ptds':False,'cuMemcpyHtoDAsync_v2':True,'cuMemcpyHtoDAsync_v2_ptsz':True}
ASYNC_BOUNDARIES={'EXISTING_APPLICATION_CTX_SYNC','EXISTING_APPLICATION_STREAM_SYNC','EXISTING_PRODUCER_PREKERNEL_SYNC'}
SYNC_PROOF='HOST_BYTES_EQUAL_CLOSED_CAPSULE_NOT_DEVICE_READBACK'
ASYNC_PROOF='HOST_BYTES_FROZEN_AND_EXISTING_GPU_COMPLETION_BOUNDARY'
def need(v,msg):
 if not v:raise ValueError(msg)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def hex64(s,name,nonzero=False):
 need(bool(re.fullmatch('[0-9a-f]{1,16}',s)),name+' noncanonical 64-bit hexadecimal')
 value=int(s,16);need(not nonzero or value>0,name+' must be nonzero');return value
def lifecycle(R,trace_required=False):
 tr=R/'traces';begins=[];ended=False;ctx_end=False;context=None;entries={};exits={};pending=None;launch_streams=set();launch_tids=set();previous_ns=0
 allowed={'cuLaunchKernel','cuLaunchKernel_ptsz','cuLaunchKernelEx','cuLaunchKernelEx_ptsz','cuLaunchCooperativeKernel','cuLaunchCooperativeKernel_ptsz'}
 for line in(tr/'ada-lifecycle.tsv').read_text().splitlines():
  t=line.split('\t');kind=t[0]
  if kind in('CTX_BEGIN','CTX_END'):
   need(len(t)==5,'context lifecycle grammar');seq=int(t[1]);ctx=hex64(t[2],'lifecycle context',True);need(int(t[3])>0,'context host TID');ns=int(t[4])
   if kind=='CTX_BEGIN':
    need(not begins and seq==1 and not ended,'second context lifetime including reused address');begins.append(ctx);context=ctx
   else:need(begins and seq==1 and ctx==context and not ctx_end and pending is None,'context end identity/state');ctx_end=True
  elif kind in('LAUNCH_ENTRY','LAUNCH_EXIT'):
   need(len(t)==10 and begins and not ended and not ctx_end,'launch lifecycle grammar/state')
   ordinal=int(t[1]);need(t[2]in allowed,'unadmitted launch API');ctx=hex64(t[3],'launch context',True);stream=hex64(t[4],'launch stream');hex64(t[5],'function handle',True);need(ctx==context and t[6]and int(t[7])>0,'launch identity');ns=int(t[8]);launch_streams.add(stream);launch_tids.add(int(t[7]));need(len(launch_streams)==len(launch_tids)==1,'multiple launch stream/host thread')
   if kind=='LAUNCH_ENTRY':
    need(pending is None and ordinal==len(entries)+1 and t[9]=='-1','launch entry order');entries[ordinal]=dict(api=t[2],context=ctx,stream=stream,function=t[6],tid=int(t[7]),entry_ns=ns);pending=ordinal
   else:
    need(pending==ordinal and ordinal in entries and ordinal not in exits and t[9]=='0','launch return pair/status')
    e=entries[ordinal];need(t[2]==e['api']and stream==e['stream']and t[6]==e['function']and int(t[7])==e['tid'],'launch return identity');exits[ordinal]=ns;pending=None
  elif kind=='PROCESS_END':
   need(len(t)==5 and not ended and begins and pending is None,'process end grammar/state')
   need(t[1]=='1'and int(t[2])==len(entries)==len(exits)==int(t[3]),'process end lifecycle counts');ended=True;ns=int(t[4])
  else:raise ValueError('unknown lifecycle event')
  need(ns>0 and ns>=previous_ns,'lifecycle monotonic time order');previous_ns=ns
 need(begins and ended and pending is None and set(entries)==set(exits),'incomplete process/launch lifecycle')
 trace_join='NOT_REQUESTED_SOURCE_BYTE_ONLY'
 if trace_required:
  files=list(tr.glob('kernel*.trace.xz'));need(len(files)==len(entries),'observed launches versus raw kernel count')
  found={}
  import lzma
  for f in files:
   m=re.fullmatch(r'kernel-([1-9][0-9]*)-ctx_0x([0-9a-f]+)\.trace\.xz',f.name);need(bool(m),'raw kernel identity grammar');ordinal=int(m[1]);need(ordinal in entries and ordinal not in found and int(m[2],16)==context,'raw context/ordinal identity')
   h={}
   with lzma.open(f,'rt')as inp:
    for line in inp:
     if line.startswith('-kernel name = '):h['function']=line.split(' = ',1)[1].strip()
     if line.startswith('-cuda stream id = '):h['stream']=int(line.split('=',1)[1])
     if line.startswith('-binary version = '):h['arch']=int(line.split('=',1)[1])
     if line.startswith('-accelsim tracer version = '):h['schema']=int(line.split('=',1)[1])
     if re.match(r'^\d+ \d+ \d+ \d+ ',line):break
   e=entries[ordinal];need(h.get('function')==e['function']and h.get('stream')==e['stream']and h.get('arch')==89 and h.get('schema')==7,'raw header versus observed launch identity');found[ordinal]=f.name
  need(set(found)==set(entries),'missing observed launch trace');trace_join='OBSERVED_DIRECT_LAUNCHES_EXACTLY_MATCH_RAW_HEADER_IDENTITIES_FULL_BODY_VALIDATION_SEPARATE'
 return dict(context_lifetime_count=1,context_hex='%x'%context,recognized_launch_count=len(entries),launch_stream_ids=sorted(launch_streams),launch_host_tids=sorted(launch_tids),process_end_observed=True,trace_launch_header_join=trace_join,source_launch_oracle='Still required to exclude API mechanisms outside NVBit callback coverage',journal_sha256=sha(tr/'ada-lifecycle.tsv'))

def qualify(R,max_copy_bytes=32*2**20,max_total_bytes=64*2**20,trace_required=False):
 R=pathlib.Path(R);tr=R/'traces'
 need(0<max_copy_bytes<=2**32 and max_copy_bytes<=max_total_bytes<=2**36,'invalid explicit validation limits')
 e=json.loads((R/'EXECUTION.json').read_text())
 need(e['tool_sha256']==PRODUCER_SHA,'producer identity not admitted')
 need(bool(re.fullmatch('[0-9a-f]{64}',e['binary_sha256'])),'binary SHA format')
 life=lifecycle(R,trace_required or e.get('kind')=='instrumented')
 entries={};exits={};done={};order={};active_api=None;last_event=None;async_streams=set();total_declared=0
 for index,line in enumerate((tr/'ada-input.tsv').read_text().splitlines()):
  t=line.split('\t');need(len(t)>=2 and t[0]in('ENTRY','API_EXIT','COMPLETE'),'unknown journal event')
  need(bool(re.fullmatch('[1-9][0-9]*',t[1])),'copy ID grammar');i=int(t[1]);need(i<=1000000,'copy count bound')
  if t[0]=='ENTRY':
   need(len(t)==10 and i==len(entries)+1 and i not in entries and active_api is None,'entry sequence/overlapping API')
   need(t[2]in APIS,'unsupported input copy API')
   hex64(t[3],'context',True);stream=hex64(t[4],'stream');dst=hex64(t[5],'device destination');src=hex64(t[6],'host source')
   need(bool(re.fullmatch('0|[1-9][0-9]*',t[7])),'byte count grammar');n=int(t[7])
   need(0<=n<=max_copy_bytes and total_declared+n<=max_total_bytes,'declared byte bound')
   need(dst+n<=2**64 and src+n<=2**64 and(not n or(dst>0 and src>0)),'pointer/byte range')
   need(bool(re.fullmatch('[0-9a-f]{64}',t[8])),'capsule SHA grammar')
   basename=pathlib.PurePosixPath(t[9]).name;need(basename=='copy_%06d.bin'%i,'copy ID/basename binding')
   need(pathlib.PurePosixPath(t[9]).parts[-3:]==('traces','inputs',basename),'capsule original path suffix')
   if APIS[t[2]]:async_streams.add(stream);need(len(async_streams)<=1,'multiple async streams including default')
   else:need(stream==0,'sync copy stream must be zero')
   entries[i]=dict(api=t[2],context=t[3],stream=t[4],device_destination=t[5],host_source=t[6],bytes=n,sha256=t[8],original_path=t[9])
   total_declared+=n;order[(i,'entry')]=index;active_api=i
  elif t[0]=='API_EXIT':
   need(len(t)==3 and i in entries and i not in exits and active_api==i,'exit pairing/order')
   need(t[2]=='0','CUDA input copy API did not succeed');exits[i]=0;order[(i,'exit')]=index;active_api=None
  else:
   need(len(t)==6 and i in exits and i not in done and active_api is None,'completion pairing/order')
   c=entries[i];need(t[3]==str(c['bytes'])and t[4]==c['sha256'],'completion byte/hash mismatch')
   if APIS[c['api']]:
    need(t[2]in ASYNC_BOUNDARIES and t[5]==ASYNC_PROOF,'unknown async completion boundary/proof')
   else:
    need(t[2]=='SYNC_API_SUCCESS_SOURCE_BYTES_FROZEN'and t[5]==SYNC_PROOF,'unknown sync completion boundary/proof')
    need(last_event==('API_EXIT',i),'sync completion must immediately follow its API return')
   need(order[(i,'entry')]<order[(i,'exit')]<index,'completion before API return')
   done[i]=dict(boundary=t[2],proof=t[5])
  last_event=(t[0],i)
 need(entries and active_api is None and set(entries)==set(exits)==set(done),'unfinished input API/capsule')
 need(len({c['context']for c in entries.values()})==1,'multiple input contexts')
 need(all(c['context']==life['context_hex']for c in entries.values()),'input context versus lifetime journal')
 need(not any(c['boundary']=='EXISTING_PRODUCER_PREKERNEL_SYNC'for c in done.values()) or life['recognized_launch_count']>0,'pre-kernel completion requires observed launch')
 need(not async_streams or not life['launch_stream_ids'] or async_streams==set(life['launch_stream_ids']),'async input stream versus single launch stream')
 observed=set();total=0
 for i,c in entries.items():
  basename='copy_%06d.bin'%i;need(basename not in observed,'duplicate capsule path');p=tr/'inputs'/basename
  need(p.is_file()and not p.is_symlink()and p.stat().st_size==c['bytes']and sha(p)==c['sha256'],'raw capsule size/SHA mismatch')
  observed.add(basename);total+=c['bytes'];c['restorable_relative_path']='traces/inputs/'+basename;c.update(done[i])
 paths=list((tr/'inputs').iterdir());need(all(p.is_file()and not p.is_symlink()for p in paths),'nonregular capsule member')
 need(observed=={p.name for p in paths},'extra/missing raw capsule member')
 return dict(schema='ADA7_INPUT_OBSERVED_SOURCE_BYTES_AND_LIFECYCLE_V4R2',lifecycle=life,status='OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_CLOSED_SHA_QUALIFIED',copies=entries,total_bytes=total,validated_max_copy_bytes=max_copy_bytes,validated_max_total_bytes=max_total_bytes,async_stream_ids=sorted(async_streams),device_input_readback_proven=False,complete_CUDA_initialization_snapshot=False,async_host_lifetime_proof='Requires independent source rule: host source remains unchanged and allocated through recorded completion; API-return recheck alone does not prove this interval',async_extra_synchronization_inserted=False,producer_existing_synchronization_profile=True,numerical_reference_observed=e.get('numerical_reference_pass'),application_exit_code=e['exit_code'],numerical_qualification='Separate same-instrumented source-specific reference receipt required; capsule qualification is not numerical qualification',stdout_sha256=sha(R/'stdout.log'),tool_sha256=e['tool_sha256'],binary_sha256=e['binary_sha256'],log_sha256=sha(tr/'ada-input.tsv'),ordered_input_identity_sha256=hashlib.sha256(json.dumps([(entries[i]['bytes'],entries[i]['sha256'])for i in sorted(entries)],separators=(',',':')).encode()).hexdigest())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('--trace-required',action='store_true');p.add_argument('--max-copy-bytes',type=int,default=32*2**20);p.add_argument('--max-total-bytes',type=int,default=64*2**20);a=p.parse_args();r=qualify(a.attempt,a.max_copy_bytes,a.max_total_bytes,a.trace_required)
 with(pathlib.Path(a.attempt)/'INPUT_CAPSULE_QUALIFICATION_V4R2.json').open('x')as f:json.dump(r,f,indent=2);f.write('\n')
 print(json.dumps(r))
