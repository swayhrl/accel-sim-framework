from pathlib import Path
import json,re,lzma,hashlib,struct,collections
R=Path('/data/c16/ada_linear_texture_producer_v9_20261024_v1');ROOTOBS=Path('/data/c16/linear_texture_semantics_proto_20261024_v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(line):
 t=line.split();i=0
 def take():
  nonlocal i
  x=t[i];i+=1;return x
 cta=[int(take())for _ in range(3)];warp=int(take());pc=int(take(),16);mask=int(take(),16);n=mask.bit_count();dst=[int(take()[1:])for _ in range(int(take()))];op=take();src=[int(take()[1:])for _ in range(int(take()))];width=int(take());addresses=[];fmt=None
 if width:
  fmt=int(take())
  if fmt==0:addresses=[int(take(),16)for _ in range(n)]
  elif fmt==1:
   base=int(take(),16);stride=int(take());addresses=[base+j*stride for j in range(n)]
  elif fmt==2:
   base=int(take(),16);addresses=[base]
   for _ in range(n-1):addresses.append(addresses[-1]+int(take()))
  else:raise AssertionError('unknown compression')
 imm=int(take());assert take()=='ADA9';active=int(take(),16);pred=int(take(),16);bank=int(take());co=int(take());qualified=int(take());cw=int(take());cm=int(take());offsets=[int(take())for _ in range(n)]if bank>=0 else [];ctrl=int(take());targets=[int(take())for _ in range(n)]if ctrl else [];tex=int(take());resource=None;pairs=[]
 if tex:
  base,size,handle,gen,count=[int(take())for _ in range(5)];pairs=[int(take())for _ in range(count)];resource=dict(base=base,size=size,handle=handle,generation=gen,effective=count)
 assert i==len(t),'trailing or missing field';assert mask==active&pred
 return dict(cta=cta,warp=warp,pc=pc,mask=mask,dst=dst,op=op,src=src,width=width,addresses=addresses,compression=fmt,imm=imm,active=active,pred=pred,bank=bank,co=co,qualified=qualified,cw=cw,constant_mode=cm,offsets=offsets,ctrl=ctrl,targets=targets,tex=tex,resource=resource,pairs=pairs)
q=json.loads((R/'native_control/NATIVE_BATCH_CASE8_A2_capture_v1.json').read_text())[0];a=Path(q['output']);assert q['exit']==0;assert 'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59'in q['gpu'];assert q['task']['binary_sha256']=='9d5ccda8de79be73a9b5278ebf5c3c4176543e530f7301c45ca4344030d33937';assert q['native_only_preload_libraries'][0]['sha256']=='f4c6939d4266c88071cdf80b469bc49b6017e5b9b63d9cd9f5bed47e0df598eb';assert sha(Path(q['native_only_preload_libraries'][0]['path']))==q['native_only_preload_libraries'][0]['sha256']
traces=a/'traces';files=list(traces.glob('kernel*.trace.xz'));assert len(files)==1;raw=files[0];data=lzma.open(raw,'rb').read();text=data.decode();assert '-grid dim = (1,1,1)'in text and '-block dim = (37,1,1)'in text and '-binary version = 89'in text and '-accelsim tracer version = 9'in text;rows=[parse(l)for l in text.splitlines()if re.match(r'^\d+ \d+ \d+ \d+ ',l)];assert len(rows)==26
loaded=list(traces.glob('loaded*.cubin'));assert len(loaded)==1 and sha(loaded[0])=='83f26c01fbf4ccfd580e6f1aab5f036cf0b988378ecd739a548aefea4eafb255'
mapfile=Path('/data/c16/ada_linear_texture_full_v9_20261024_v1/actual_loaded_map_v1/semantic-map.tsv');assert sha(mapfile)=='717f0d849d49ea27e1aefc6ffe92b0c17e452748bf13beb5bd1628092ee969bc';mapping={}
for l in mapfile.read_text().splitlines():
 fn,pc,dst,src,sass=l.split('\t');mapping[int(pc,16)]=(fn,[]if dst=='-'else list(map(int,dst.split(','))),[]if src=='-'else list(map(int,src.split(','))),sass.split()[0])
static=[]
for l in (traces/'ada-static.tsv').read_text().splitlines():
 t=l.split('\t');static.append(dict(full=int(t[0],16),offset=int(t[1],16),function=t[2],sass=t[3],bank=int(t[4]),co=int(t[5]),cw=int(t[6]),qualified=int(t[7])))
bases={x['full']-x['offset']for x in static};assert len(bases)==1;basecode=bases.pop();byPC={x['full']:x for x in static};assert len(static)==24
journal=(traces/'ada9-resource-journal.tsv').read_text();assert 'PROCESS_END creates=1 destroys=1 launches=1 completed=1 copies=3 generation=1'in journal;copies=re.findall(r'HTOD_BEGIN id=(\d+) ctx=(\w+) dst=(\w+) bytes=(\d+) api=(\w+)',journal);assert len(copies)==3 and [int(x[3])for x in copies]==[512,148,8];assert len({x[1]for x in copies})==1
app=json.loads((a/'APP_RESOURCE.json').read_text());base=int(app['actual_backing_pointer'],16);assert all(int(app[k],16)==base for k in ['actual_backing_pointer','queried_backing_pointer','pointer_attributes_device_pointer']);assert app['resource_type']==2 and app['channel_bits']==[32,0,0,0]and app['channel_kind']==1 and app['size_bytes']==512;assert int(copies[0][2],16)==base
for i,name in enumerate(['HOST_INPUT_U32.bin','HOST_INDICES_I32.bin','HOST_HANDLE_U64.bin']):assert(a/name).read_bytes()==(traces/f'ada9-htod-{i:03}.bin').read_bytes()
descriptor=json.loads((traces/'ada9-driver-descriptors.json').read_text());assert descriptor['base']==base and descriptor['bytes']==512 and descriptor['format']==3 and descriptor['components']==1 and descriptor['resource_type']==2 and descriptor['resource_flags']==0 and descriptor['view_is_null']is True and descriptor['address_modes']==[1,0,0]and descriptor['filter']==0 and descriptor['flags']==0 and descriptor['reserved']==[0]*12;assert(traces/'ada9-driver-resource-desc.raw').stat().st_size==144 and(traces/'ada9-driver-texture-desc.raw').stat().st_size==104
inputs=struct.unpack('<128I',(a/'HOST_INPUT_U32.bin').read_bytes());indices=struct.unpack('<37i',(a/'HOST_INDICES_I32.bin').read_bytes());output=struct.unpack('<37I',(a/'HOST_OUTPUT_U32.bin').read_bytes());assert inputs==tuple(0x12340000+i*19 for i in range(128));assert indices==tuple((i*13+7)%128 for i in range(37));assert output==tuple(inputs[i]for i in indices)
baseline=ROOTOBS/'native_attempts/indirect_native_static_v5/linear_tex_u32_indirect_native_v2/attempt001'
for name in ['HOST_INPUT_U32.bin','HOST_INDICES_I32.bin','HOST_OUTPUT_U32.bin']:assert(a/name).read_bytes()==(baseline/name).read_bytes()
resolved=[];texlines={};summary=[]
for w in [0,1]:
 wr=[x for x in rows if x['warp']==w];assert[x['pc']-basecode for x in wr]==list(range(0,193,16));assert all(x['cta']==[0,0,0]and x['mask']==(0xffffffff if w==0 else 0x1f)and x['active']==x['mask']and x['pred']==x['mask']and x['qualified']==1 for x in wr)
 for x in wr:
  off=x['pc']-basecode;fn,dst,src,op=mapping[off];assert x['dst']==dst and x['src']==src and x['op']==op,'complete actual PLR typed deps';m=byPC[x['pc']];assert(x['bank'],x['co'],x['cw'])==(m['bank'],m['co'],m['cw'])
  if x['bank']>=0:assert x['constant_mode']==1 and x['offsets']==[x['co']]*x['mask'].bit_count() and x['width']==0
  assert x['ctrl']==0 and not x['targets']
  if off in [96,128,176]:assert{260,261}.issubset(x['src']),'implicit UR high halves retained'
  if off==48:assert x['dst']==[260,261]and x['cw']==8
  if off==112:assert x['dst']==[4,5]and x['cw']==8
  if off==160:assert x['dst']==[6,7]and x['cw']==8
  if x['op']=='TLD.SCR.B.LZ':
   assert x['tex']==1 and x['width']==4 and x['bank']==-1 and x['resource']==dict(base=base,size=512,handle=int(app['texture_object'],16),generation=1,effective=x['mask'].bit_count());lines=set()
   for lane,(pair,address)in enumerate(zip(x['pairs'],x['addresses'])):
    tid=w*32+lane;handle=pair>>32;lo=pair&0xffffffff;idx=lo if lo<0x80000000 else lo-2**32;assert handle==int(app['texture_object'],16)<=0xffffffff and 0<=idx<128 and idx==indices[tid]and address==base+idx*4 and address+4<=base+512;lines.add(address//128*128);resolved.append({'cta':[0,0,0],'warp':w,'pc':x['pc'],'offset':off,'lane':lane,'thread':tid,'mask':x['mask'],'pair':pair,'observed_handle32':handle,'signed_index32':idx,'API_backing_CUdeviceptr':base,'resolved_prefix_address':address,'width':4,'original_opcode':x['op'],'address_origin':'API_RESOURCE_LINEAR_SIGNED_INDEX_RESOLUTION_NOT_NVBIT_NATIVE_MREF','same_process_output_word':output[tid]})
   texlines[str(w)]=sorted(lines)
  else:assert x['tex']==0 and not x['pairs']
  if off==96:assert x['addresses']==[int(copies[2][2],16)]*x['mask'].bit_count()
  if off==128:assert x['addresses']==[int(copies[1][2],16)+(w*32+i)*4 for i in range(x['mask'].bit_count())]
 summary.append({'warp':w,'records':len(wr),'mask':hex(wr[0]['mask']),'full_original_pc_sequence_verified':True})
assert len(resolved)==37
out=R/'evidence/CPU_FULLTRACE_JOIN_A2_V1.json';result={'status':'PRODUCER_CASE8_CANDIDATE_FULL_RECORD_BINDING_PASS_PENDING_PARENT_AND_CONSUMER_REVIEW','GPU_reexecution':False,'SIM_run':False,'actual_attempt':str(a),'contract_sha256':'be2711906a2b4a3ece4997112b7cf5a0e6e57570adb995028c885abc81222019','source_binary_sha256':q['task']['binary_sha256'],'producer_SO_sha256':q['native_only_preload_libraries'][0]['sha256'],'loaded_cubin_sha256':sha(loaded[0]),'full_PLR_semantic_map_sha256':sha(mapfile),'raw_trace_compressed_sha256':sha(raw),'raw_trace_expanded_sha256':hashlib.sha256(data).hexdigest(),'raw_trace_expanded_bytes':len(data),'full_xz_CRC_reopened':True,'record_count':26,'physical_warps':summary,'complete_typed_implicit_UR_and_high_halves':True,'complete_actual_CBANK_offset_widths':True,'effective_TLD_lanes':37,'actual_resource_lifetime_and_HtoD_snapshots':True,'unloaded_baseline_reused_same_binary_input_output_bytes':True,'expected_128B_TEX_line_bases_by_warp':texlines,'expected_128B_TEX_request_count_if_one_per_line':sum(map(len,texlines.values())),'prediction_scope':'CPU engineering line grouping only, not hardware timing or SIM execution','resolved_lanes':resolved,'actual_effective_flags':{'TOOL_COMPRESS':1,'TRACE_FILE_COMPRESS':1,'C16_EXACT_ROOT_FUNCTION_ONLY':0,'C16_USE_NVBIT_STATIC_INDEX':0,'EXCLUDE_PRED_OFF':0,'ACTIVE_FROM_START':1,'note':'requested ENABLE_COMPRESS/EXACT_ROOT_FUNCTION_ONLY/XZ_COMPRESS_TRACE names were ignored; actual stdout and trace retained, no rerun/relabel'}};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='resolved_lanes'},indent=2))
