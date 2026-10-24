"""Independent parent check of the new 1CTA/65-thread native case."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,lzma,time
B=Path('/root/data/ep_l2_main_ada_legacy65_r2_compat_20261024_v1');O=B/'run/86b6f52282c943d69b377f4332a4246a';R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
assert sha(B/'control/FROZEN_SPEC.json')=='e314bde7c84a236cff3e3cf9e47ad70294763d6b03c5249e19c3ae3adb8839b8'
assert sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json')=='99fb84a2f4d70c78df828be5eb22f643695d202112dc2da18a50d96907b5c249'
s=json.loads((B/'control/FROZEN_SPEC.json').read_text());c=next(iter(s['cases'].values()));x=json.loads((O/'EXIT.json').read_text())
assert x['exit_code']==0 and x['stop_reason']is None and x['native_observed']and x['application_attempt_consumed']==1
assert sha(O/'raw.log')==x['raw_sha256']=='8475ad0e227ffc907bd59d036ebca8735152e0767e36b715c1330906809708d7'
for p,want in s['pinned_files'].items():assert sha(p)==want
raw=(O/'raw.log').read_text();decoded=[dict(v.split('=',1)for v in line.split()[1:])for line in raw.splitlines()if line.startswith('ADA8_DECODE ')]
src=[v for v in decoded if v['aux']=='0'];aux=[v for v in decoded if v['aux']=='1']
assert len(src)==39 and len(aux)==12 and sum(int(v['mask'],16).bit_count()for v in src)==780 and sum(int(v['mask'],16).bit_count()for v in aux)==260
assert sum(int(v['mask'],16).bit_count()for v in decoded if v['space']=='8')==325
def count(pattern):
 a=re.findall(pattern,raw,re.M);assert a,pattern;return int(a[-1])
assert count(r'^gpu_tot_sim_insn\s*=\s*(\d+)')==1040 and count(r'^gpu_tot_issued_cta\s*=\s*(\d+)')==1 and count(r'^ctas_completed\s+(\d+)')==1
assert count(r'^\s*L1C_total_cache_accesses\s*=\s*(\d+)')==15 and count(r'^\s*L1C_total_cache_misses\s*=\s*(\d+)')==9
assert count(r'^\s*Total_core_cache_stats_breakdown\[CONST_ACC_R\]\[HIT\]\s*=\s*(\d+)')==6
assert count(r'^gpgpu_n_mem_const\s*=\s*(\d+)')==3 and count(r'^\s*L2_cache_stats_breakdown\[CONST_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)')==6
assert count(r'^gpgpu_n_mem_write_global\s*=\s*(\d+)')==9
tr=Path(c['trace_entry']).parent;group=next(tr.glob('*.traceg.xz'));warps=[];current=None;cta=0;store_addresses={};store_base=None
with lzma.open(group,'rt')as f:
 for line in f:
  if line.startswith('thread block ='):cta+=1;assert line.strip()=='thread block = 0,0,0'
  elif line.startswith('warp ='):current=[];warps.append(current);assert int(line.split('=')[1])==len(warps)-1
  elif re.match(r'^[0-9a-fA-F]{16}\s',line):
   t=line.split();n=int(t[2]);opi=3+n;op=t[opi];mask=int(t[1],16);current.append((int(t[0],16),mask,op));assert not op.startswith(('CALL.','RET.','WARPSYNC'))
   if op.startswith('STG'):
    nsrc=int(t[opi+1]);i=opi+2+nsrc;assert int(t[i])==4;encoding=int(t[i+1]);assert encoding in(1,2)
    base=int(t[i+2],0)
    if encoding==1:stride=int(t[i+3]);assert stride==4
    else:assert mask==1 and t.index('ADA8')-i==4;stride=4  # exact one-address base/delta case
    if store_base is None:store_base=base
    for lane in range(32):
     if mask>>lane&1:
      index=(len(warps)-1)*32+lane;assert index<65 and index not in store_addresses;addr=base+lane*stride;assert addr==store_base+4*index;store_addresses[index]=addr
assert cta==1 and len(warps)==3 and len(store_addresses)==65 and sum(len(w)for w in warps)==39
assert Counter((pc,m,op)for w in warps for pc,m,op in w)==Counter((int(v['pc'],16),int(v['mask'],16),v['op'])for v in src)
assert [m for w in warps for _,m,op in w if op=='EXIT' and m]==[0xffffffff,0xffffffff,1]
assert sum(m==0 for w in warps for _,m,_ in w)==3 and min(pc for w in warps for pc,_,_ in w)>2**32
M=O/'MAP_OBSERVATIONS';u=json.loads((M/'UNION.json').read_text());samples=[json.loads(v)for v in(M/'SAMPLES.jsonl').read_text().splitlines()];saved={};seen=set();n=0
for v in samples:
 if v.get('status')=='EXIT_RACE':continue
 n+=1;key=(v['pid'],v['start_ticks'])
 if v.get('saved_maps'):
  p=M/v['saved_maps'];assert sha(p)==v['maps_sha256'];saved[key]=v['maps_sha256']
  for line in p.read_text().splitlines():
   fields=line.split(None,5)
   if len(fields)<6 or not fields[5].startswith('/'):continue
   name=fields[5].replace('\\040',' ');assert name in s['pinned_files']and sha(name)==s['pinned_files'][name];seen.add(name)
 else:assert saved[key]==v['maps_sha256']
assert n==u['sample_count']==38 and len(seen)==8 and seen==set(u['mapped_dependency_union'])
cp=u['checkpoints'];assert [v['label']for v in cp]==['FIRST_ISSUE','TERMINAL']
for v in cp:assert v['state']in('T','t')and(v['pid'],v['start_ticks'])==(u['primary_identity']['pid'],u['primary_identity']['start_ticks'])and s['binary']in v['paths']
reg=json.loads(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_text());row=reg['registered_future_requests'][s['request']];assert row['budget']==row['consumed']==1
out={'status':'PARENT_INDEPENDENT_LEGACY_SINGLE_CTA65_TERMINAL_JOIN_PASS','request':s['request'],'run':str(O),'raw_sha256':x['raw_sha256'],'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'pinned_files_current_full_SHA':105,'source_records':39,'source_active_lanes':780,'aux_uops':12,'aux_active_lanes':260,'actual_issued_active_lane_uops':1040,'constant_lane_accesses':325,'actual_constant_requests':3,'L1C_access_miss_hit':[15,9,6],'L2_constant_accesses':6,'global_store_lanes':65,'independently_joined_store_addresses':store_addresses,'actual_core_global_writes':9,'ctas_issued_completed':1,'physical_warps':3,'physical_EXIT_masks':['ffffffff','ffffffff','1'],'physical_EXIT_lanes':65,'source_decoded_PC_mask_opcode_multisets_equal':True,'full64_PC_retained':True,'maps_samples':38,'all_saved_maps_and_current_eight_dependencies_SHA':True,'checkpoints':cp,'campaign_consumed':7,'campaign_ceiling':8,'source_legacy_scope':'Only measured single cuLaunch typed config block65/shared0/explicit param APIs; general ABI/lifecycle/Graph/texture not promoted','mapping_scope':x['maps_child_discovery_scope'],'performance_or_EP_science_qualification':False,'archive_and_reservation_retirement_pending':True,'automatic_retry':False,'GPU_or_simulator_execution_by_this_verifier':False,'observed_unix':time.time()}
p=O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');(R/'control/ADA_LEGACY65_R2_PARENT_TERMINAL_JOIN.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['independently_joined_store_addresses','checkpoints']}))
