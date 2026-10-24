"""Host-only exact NN input/output, lifecycle, full memory-address join."""
from pathlib import Path
import json,hashlib,struct,math,ctypes,importlib.util,lzma,collections,re,sys
R=Path('/data/c16/ada_call_snapshot_nn_20261024_v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise AssertionError(m)
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def words(path):return [x.split('\t')for x in path.read_text().splitlines()]
def verify(mode):
 A=R/'attempts/pair_A3_v1'/mode;T=A/'traces';E=json.loads((A/'EXECUTION.json').read_text());S=json.loads((R/'control/CAPTURE_PAIR_SPEC_A3_V1.json').read_text())
 need(E['exit_code']==0 and E['stop_reason']is None,'failed process');need(E['tool_sha256']==sha(A/'TOOL_USED.so')==S['pins'][S['tool']],'SO')
 for p,h in S['pins'].items():need(sha(Path(p))==h,'pin drift '+p)
 source=b''
 need(E['mode']==mode and E['spec_sha256']==sha(R/'control/CAPTURE_PAIR_SPEC_A3_V1.json'),'execution spec/mode binding')
 for row in S['inputs']:
  p=A/row['relative'];need(sha(p)==row['sha256'],'input file SHA')
 for filename in (A/'data/filelist_4').read_text().split():
  for line in (A/filename).read_text().splitlines():
   need(len(line)==48,'input line grammar')
   coords=[f32(float(line[28:33])),f32(float(line[33:38]))];need(all(math.isfinite(x)for x in coords),'input finite')
   source+=struct.pack('<2f',*coords)
 need(len(source)==342112 and hashlib.sha256(source).hexdigest()==S['source_equivalent_input_sha256'],'source expected pack')
 inp=words(T/'ada-input.tsv');need(len(inp)==3 and [x[0]for x in inp]==['ENTRY','API_EXIT','COMPLETE'],'exact input journal')
 en,ex,co=inp;need(len(en)==10 and en[1:3]==['1','cuMemcpyHtoD_v2']and en[4]=='0'and int(en[7])==342112,'input API/shape')
 need(ex==['API_EXIT','1','0'],'input success');need(co==['COMPLETE','1','SYNC_API_SUCCESS_SOURCE_BYTES_FROZEN','342112',en[8],'HOST_BYTES_EQUAL_CLOSED_CAPSULE_NOT_DEVICE_READBACK'],'input completion')
 capsule=T/'inputs/copy_000001.bin';need({x.name for x in (T/'inputs').iterdir()}=={'copy_000001.bin'},'exact capsule set')
 need(Path(en[9]).name==capsule.name and capsule.read_bytes()==source and sha(capsule)==en[8],'actual bytes equal expected input')
 args=words(T/'ada-nn-kernel-args.tsv');need(len(args)==1,'one argument entry');ar=args[0]
 need(len(ar)==11 and ar[0]=='KERNEL_ARGS'and ar[1]==en[3]and ar[3]==en[5]and ar[5:10]==['41f00000','42b40000','42764','168,1,1','256,1,1'],'actual argument values')
 output=words(T/'ada-nn-output.tsv');need(len(output)==1,'one output return');out=output[0]
 need(len(out)==11 and out[:3]==['OUTPUT_SUCCESS','1','cuMemcpyDtoH_v2']and out[3]==ar[1]and out[4]==ar[4]and int(out[6])==171056 and out[10]=='SYNC_SUCCESS_RETURN_HOST_BYTES_NOT_ADDED_DEVICE_READBACK','output API/actual pointer')
 blob=T/'nn-output-1.bin';need(blob.stat().st_size==171056 and sha(blob)==out[7],'full output SHA')
 life=words(T/'ada-lifecycle.tsv');need([x[0]for x in life]==['CTX_BEGIN','LAUNCH_ENTRY','LAUNCH_EXIT','CTX_END','PROCESS_END'],'one complete lifecycle')
 cb,le,lx,ce,pe=life;need(cb[1]=='1'and cb[2]==ce[2]==ar[1]and ce[1]=='1','context')
 need(le[1]=='1'and le[2]=='cuLaunchKernel'and le[3]==ar[1]and le[4]=='0'and le[5]==ar[2]and le[6]=='_Z6euclidP7latLongPfiff','entry identity')
 need(lx[1:8]==le[1:8]and le[9]=='-1'and lx[9]=='0'and pe[1:4]==['1','1','1'],'launch exit function handle/status')
 need(out[8]==le[7]==cb[3]==ce[3]and all(x[1]==out[8]for x in words(T/'ada-api.tsv')),'single observed actor across input/kernel/output API')
 need(int(cb[4])<int(le[8])<int(lx[8])<int(out[9])<int(ce[4])<int(pe[4]),'output/lifecycle monotonic order')
 api=words(T/'ada-api.tsv');need(all(len(x)==5 and x[3]==ar[1]for x in api),'API context')
 ns=[int(x[0])for x in api];need(ns==sorted(ns),'API monotonic order')
 mem=[(x[2],x[4])for x in api if x[2].startswith('cuMemcpy')]
 need(mem==[('cuMemcpyHtoD_v2','0'),('cuMemcpyHtoD_v2','1'),('cuMemcpyDtoH_v2','0'),('cuMemcpyDtoH_v2','1')],'exact copy API order')
 need(not any(any(k in x[2]for k in ['Memset','Managed','Graph','Capture','Tex','Surface','External'])for x in api),'unsupported init/API')
 lib=ctypes.CDLL('libm.so.6');fma=lib.fmaf;fma.argtypes=[ctypes.c_float]*3;fma.restype=ctypes.c_float;sqrt=lib.sqrtf;sqrt.argtypes=[ctypes.c_float];sqrt.restype=ctypes.c_float
 coords=struct.unpack('<85528f',source);actual=struct.unpack('<42764f',blob.read_bytes());reference=[];maxerr=0.
 for i,got in enumerate(actual):
  need(math.isfinite(got),'output finite')
  dx=f32(30.-coords[2*i]);dy=f32(90.-coords[2*i+1])
  val=sqrt(fma(dx,dx,f32(dy*dy)));need(math.isfinite(val),'reference finite');reference.append(val)
  maxerr=max(maxerr,abs(got-math.hypot(coords[2*i]-30.,coords[2*i+1]-90.)))
 ref=struct.pack('<42764f',*reference);need(ref==blob.read_bytes(),'full42764 bitwise FP32/FMA/sqrt reference')
 proof=dict(CPU_libm_sha256=sha(Path('/usr/lib/x86_64-linux-gnu/libm.so.6').resolve()),CPU_libm_path=str(Path('/usr/lib/x86_64-linux-gnu/libm.so.6').resolve()),mode=mode,input_capsule_sha256=en[8],input_bytes=342112,input_identity='ACTUAL_SUCCESSFUL_SYNC_HTOD_SOURCE_BYTES_MATCH_EXACT_SOURCE_PACK_NOT_DEVICE_READBACK',output_capsule_sha256=out[7],output_bytes=171056,all_distances=42764,all_input_output_reference_values_finite=True,all_output_bytes_equal_CPU_FADD_FMUL_FMA_SQRT_RN=True,reference_sha256=hashlib.sha256(ref).hexdigest(),reference_origin='Actual static FADD/FADD/FMUL/FFMA norm; host libm fmaf and sqrtf round-to-nearest. No tolerance fit; all42764 f32 bytes exactly equal. The separate source-expression top5 oracle remains independent.',max_absolute_error_vs_double_hypot=maxerr,kernel_args_actual_observed=dict(context=ar[1],function_handle=ar[2],input_device=ar[3],output_device=ar[4],latitude_f32bits=ar[5],longitude_f32bits=ar[6],records=42764),source_top5_oracle=json.loads((R/('CPU_TOP5_'+mode+'_A3')/'CPU_REFERENCE_RECEIPT.json').read_text())['status'],snapshot_only=mode=='observer',no_additional_CUDA_readback_or_sync_by_output_hook=True,not_pure_uninstrumented_native=True)
 need(proof['source_top5_oracle']=='INDEPENDENT_CPU_FULL_RESULT_PASS','top5')
 if mode=='trace':
  vp=Path('/data/c16/ada_trace_extensions_v8_20261024_v1/validate_v8_warpsync_v3.py');need(sha(vp)=='ef0a272e161d88ca04ca631e4544863edee507687ce0e5cf491c550372e27a03','frozen full-body validator');sp=importlib.util.spec_from_file_location('v8',vp);v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
  need(sha(v.H)=='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b','frozen prefix parser')
  cubins=list(T.glob('loaded*.cubin'));need(len(cubins)==1 and sha(cubins[0])==S['expected_loaded_cubin_sha256'],'actual loaded code')
  rawfiles=list(T.glob('kernel*.trace.xz'));need(len(rawfiles)==1,'one raw')
  lists=list(T.glob('kernelslist_ctx_*'));stats=list(T.glob('stats_ctx_*'))
  need(len(lists)==len(stats)==1 and lists[0].name=='kernelslist_ctx_0x'+ar[1]and stats[0].name=='stats_ctx_0x'+ar[1],'exact command/stat context set')
  commands=lists[0].read_text().splitlines();need(len(commands)==2 and commands[1]==rawfiles[0].name,'exact raw command set')
  copycmd=commands[0].split(',');need(copycmd[0]=='MemcpyHtoD'and int(copycmd[1],16)==int(ar[3],16)and copycmd[2]=='342112','actual copy command')
  statrows=stats[0].read_text().splitlines();need(len(statrows)==2,'one stats kernel row')
  sr=[x.strip()for x in statrows[1].split(',')];need(sr==[rawfiles[0].name,'_Z6euclidP7latLongPfiff','168','1','1','168','256','1','1','256','41503','41503'],'exact stats source records/geometry')
  seen=set();loads=collections.Counter();opcounts=collections.Counter();calls=0;returns=0
  with lzma.open(rawfiles[0],'rt')as f:
   for line in f:
    if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
    t=line.split(maxsplit=4);cta=list(map(int,t[:3]));warp=int(t[3]);q=v.parse(t[4]);need(cta[1:]==[0,0],'grid')
    effective=q['mask'].bit_count();opcounts[q['opcode']]+=effective
    if q['control_kind']==1:calls+=effective
    if q['control_kind']==2:returns+=effective
    for lane,address in q['addrs'].items():
     tid=cta[0]*256+warp*32+lane
     if q['opcode'].startswith('STG'):
      need(q['width']==4 and tid<42764 and tid not in seen and address==int(ar[4],16)+4*tid,'actual STG to original DtoH source+4tid');seen.add(tid)
     elif q['opcode'].startswith('LDG'):
      delta=address-(int(ar[3],16)+8*tid);need(q['width']==4 and tid<42764 and delta in [0,4],'actual LDG input source')
      loads[(tid,delta)]+=1
  need(seen==set(range(42764))and len(loads)==2*42764 and all(n==1 for n in loads.values()),'complete store/input access bijections')
  need(opcounts['EXIT']==168*256,'full physical EXIT')
  full=json.loads((A/'FULL_RECORD_V8_WARPSYNC_VALIDATION.json').read_text());need(full['counts']['source_sass_records']==41503 and full['warps']==1344,'frozen fullrecord validator')
  need(full['source_files']=={rawfiles[0].name:sha(rawfiles[0])}and full['source_binary_sha256']==E['binary_sha256'],'full-record receipt exact source/binary binding')
  proof.update(raw_sha256=sha(rawfiles[0]),loaded_cubin_sha256=sha(cubins[0]),source_sass_records=41503,source_active_lane_instances=1284872,all_effective_STG_addresses_match_actual_DtoH_device_source=True,STG_lane_bijection=42764,LDG_lane_bijection=85528,physical_EXIT_lanes=43008,CTAs=168,physical_warps=1344,dynamic_CALL_active_lanes=calls,dynamic_RET_active_lanes=returns,static_contains_CALL_RET=True,dynamic_call_coverage='No dynamic CALL/RET taken in this exact finite input; static-only CALL support is not upgraded by a vacuous control check',full_record_validator_sha256=sha(vp),full_record_receipt_sha256=sha(A/'FULL_RECORD_V8_WARPSYNC_VALIDATION.json'))
 return proof
if __name__=='__main__':
 modes=[verify(x)for x in ['observer','trace']]
 need(modes[0]['input_capsule_sha256']==modes[1]['input_capsule_sha256']and modes[0]['output_capsule_sha256']==modes[1]['output_capsule_sha256'],'same actual inputs and outputs')
 out=dict(schema='NN_A3_PAIR_ALL_BYTES_FULL_MEMORY_JOIN_V3',status='EXACT_PRODUCER_INPUT_OUTPUT_AND_FULL_RECORD_JOIN_PASS_NOT_BULK_RELEASED',modes=modes,actual_input_pair_comparison='MATCH',actual_output_pair_comparison='BITWISE_MATCH',no_SIM_attempt=True,simulation_campaign_consumed=8,formal_bulk_admission=False,hardware_performance_qualification=False,source_KEEP=True)
 with (R/'NN_PAIR_FULL_BYTE_MEMORY_JOIN_A3_V3.json').open('x')as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps(out))
