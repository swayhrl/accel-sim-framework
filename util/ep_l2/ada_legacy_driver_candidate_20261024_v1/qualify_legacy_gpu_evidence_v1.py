from pathlib import Path
import json,hashlib,lzma,re
R=Path('/root/data/ada_native_extensions_stage4_20261024_v1');E=R/'legacy_evidence';A=E/'attempts/legacy_typed_single_campaign_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for mode in ['grid','grid_async','launch','modern']:
 a=A/mode;ex=json.loads((a/'EXECUTION.json').read_text());na=json.loads((a/'NATIVE_EXECUTION.json').read_text());q=json.loads((a/'FULL_RECORD_V8_WARPSYNC_VALIDATION.json').read_text())
 assert ex['exit_code']==na['exit_code']==0 and b'Test PASSED'in(a/'native.stdout').read_bytes()and b'Test PASSED'in(a/'stdout.log').read_bytes()
 assert ex['tool_sha256']==sha(a/'TOOL_USED.so')=='cebd9a6cc7277e43156e44a5bf528369bb4962a06a3ec89a3c7849c234d1aaf4'
 cubins=list((a/'traces').glob('loaded*.cubin'));assert len(cubins)==1 and sha(cubins[0])=='41425beaa2ecbd5a0bdc3e3f992bcb8be328c17dce22c9a335d2a280ac399bf1'
 raw=next((a/'traces').glob('kernel*.trace.xz'));assert q['source_files'][raw.name]==sha(raw)
 grid=1 if mode=='launch'else 2;block=65 if mode=='launch'else 37
 stores={};headers={}
 with lzma.open(raw,'rt')as f:
  for line in f:
   if line.startswith('-grid dim ='):headers['grid']=tuple(map(int,re.findall(r'\d+',line)))
   if line.startswith('-block dim ='):headers['block']=tuple(map(int,re.findall(r'\d+',line)))
   if ' STG.'not in line:continue
   t=line.split();cx,cy,cz,warp=map(int,t[:4]);mask=int(t[5],16);n=int(t[6]);j=7+n;op=t[j];n=int(t[j+1]);j+=2+n;width=int(t[j]);comp=int(t[j+1]);j+=2
   assert op=='STG.E'and width==4 and cy==cz==0
   lanes=[i for i in range(32)if mask>>i&1]
   if comp==1:
    base=int(t[j],0);stride=int(t[j+1]);addrs=[base+stride*k for k in range(len(lanes))]
   elif comp==2:
    base=int(t[j],0);addrs=[base]
    for k in range(len(lanes)-1):addrs.append(addrs[-1]+int(t[j+1+k]))
   elif comp==0:addrs=[int(x,0)for x in t[j:j+len(lanes)]]
   else:raise AssertionError('unknown compression')
   for lane,address in zip(lanes,addrs):
    index=cx*block+warp*32+lane;assert 0<=index<65 and index not in stores;stores[index]=address
 assert set(stores)==set(range(65))
 bases={address-4*index for index,address in stores.items()};assert len(bases)==1
 assert headers=={'grid':(grid,1,1),'block':(block,1,1)}
 launch=[x.split('\t')for x in(a/'traces/ada-launch.tsv').read_text().splitlines()];assert len(launch)==2 and [x[1]for x in launch]==['0','1']and launch[0][0]==launch[1][0]and launch[0][2:]==launch[1][2:]
 if mode!='modern':
  configs=[x.split('\t')for x in(a/'traces/ada-legacy-config.tsv').read_text().splitlines()];assert len(configs)==1;c=configs[0]
  api={'grid':'cuLaunchGrid','grid_async':'cuLaunchGridAsync','launch':'cuLaunch'}[mode]
  assert c[0]==launch[0][0]==api and c[3]==launch[0][2]and list(map(int,c[4:]))==[grid,1,1,block,1,1,0]
  assert(mode=='grid_async')==(int(c[3],16)!=0)
  events=[x.split('\t')for x in(a/'traces/ada-api.tsv').read_text().splitlines()]
  for api_name in ['cuFuncSetBlockShape','cuFuncSetSharedSize','cuParamSetv','cuParamSeti','cuParamSetSize',api]:
   rows=[x for x in events if x[2]==api_name];assert [x[4]for x in rows]==['0','1']
   assert len({x[1]for x in rows})==1 and all(x[3]==c[1]for x in rows)
 results.append({'mode':mode,'native_and_capture_full65_reference':True,'full_record_counts':q['counts'],'grid':grid,'block':block,'warps':q['warps'],'launch_API':launch[0][0],'stream':launch[0][2],'all65_global_store_addresses':'BASE_PLUS_4_GLOBAL_INDEX','observed_store_base':hex(next(iter(bases))),'source_raw_sha256':sha(raw),'actual_loaded_cubin_sha256':sha(cubins[0]),'producer_sha256':ex['tool_sha256'],'host_binary_sha256':ex['binary_sha256']})
proof={'schema':'LEGACY_SINGLE_CONTEXT_TYPED_GPU_CANDIDATE_JOIN_V1','status':'SCOPED_GPU_PRODUCER_CANDIDATE_PASS_NOT_BULK_ADMITTED','results':results,'kernel_parameter_bank0':'Source explicitly sets pointer bytes0..7 and uint32 N65 at8..11 via checked legacy APIs; bank0 device contents not snapshotted. Actual global address bases measured independently.','excluded':['multiple context lifetimes/generation','multiple host launch threads','multiple streams within one process','Graph','texture/surface','general arbitrary legacy parameter ABI','hardware performance equivalence'],'simulator_attempts_consumed':0,'source_keep':True}
(R/'LEGACY_TYPED_GPU_CANDIDATE_JOIN.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
