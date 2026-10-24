"""Parent joins exact ADA9 source bytes, decoded records, actual cache counters/maps."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,lzma,time
B=Path('/root/data/ep_l2_main_ada_tex37_ada9_compat_20261024_v1');O=B/'run/5553b55c08224280afefe139c9c9333c';R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
assert sha(B/'control/FROZEN_SPEC.json')=='7ec0074f3286b3d13fc846c2bc9a6d4c799fb0423fca7eb96565d543646a4596'
assert sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json')=='83a948a665c2a183b28068b464cf911b918a990e5045115ff91d7aef2a3b2357'
s=json.loads((B/'control/FROZEN_SPEC.json').read_text());c=s['cases']['tex37_ada9_v1'];x=json.loads((O/'EXIT.json').read_text())
assert x['exit_code']==0 and x['stop_reason']is None and x['native_observed']and x['application_attempt_consumed']==1
assert sha(O/'raw.log')==x['raw_sha256']=='f80dcae774251b1a90f471fc6fe5d2461c72acd9c7d24b2a95b50d0bc873b33a'
for p,want in s['pinned_files'].items():assert sha(p)==want
raw=(O/'raw.log').read_text();decoded=[dict(v.split('=',1)for v in line.split()[1:])for line in raw.splitlines()if line.startswith('ADA8_DECODE ')]
source=[v for v in decoded if v['aux']=='0'];aux=[v for v in decoded if v['aux']=='1']
assert len(source)==26 and len(aux)==10 and sum(int(v['mask'],16).bit_count()for v in source)==481 and sum(int(v['mask'],16).bit_count()for v in aux)==185
assert sum(int(v['mask'],16).bit_count()for v in decoded if v['space']=='8')==222
assert sum(v['space']=='8'and v['width']=='8'for v in decoded)==6
assert sum(v['space']=='8'and v['width']=='4'for v in decoded)==6
tex=[v for v in source if v['op']=='TLD.SCR.B.LZ'];assert len(tex)==2 and sum(int(v['mask'],16).bit_count()for v in tex)==37 and all(v['space']=='9'and v['width']=='4'for v in tex)
assert sum(int(v['mask'],16).bit_count()for v in source if v['op']=='LDG.E')==74
assert sum(int(v['mask'],16).bit_count()for v in source if v['op']=='STG.E')==37
def count(pattern):
 a=re.findall(pattern,raw,re.M);assert a,pattern;return int(a[-1])
assert count(r'^gpu_tot_sim_insn\s*=\s*(\d+)')==666 and count(r'^gpu_tot_issued_cta\s*=\s*(\d+)')==1 and count(r'^ctas_completed\s+(\d+)')==1
assert count(r'^\s*L1C_total_cache_accesses\s*=\s*(\d+)')==12 and count(r'^\s*L1C_total_cache_misses\s*=\s*(\d+)')==6
assert count(r'^\s*L1T_total_cache_accesses\s*=\s*(\d+)')==6 and count(r'^\s*L1T_total_cache_misses\s*=\s*(\d+)')==4
assert count(r'^\s*L1T_total_cache_pending_hits\s*=\s*(\d+)')==2 and count(r'^\s*L1T_total_cache_reservation_fails\s*=\s*(\d+)')==0
assert count(r'^\s*Total_core_cache_stats_breakdown\[TEXTURE_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)')==6
assert count(r'^\s*Total_core_cache_stats_breakdown\[TEXTURE_ACC_R\]\[HIT_RESERVED\]\s*=\s*(\d+)')==2
assert count(r'^gpgpu_n_tex_insn\s*=\s*(\d+)')==37 and count(r'^gpgpu_n_mem_write_global\s*=\s*(\d+)')==5
assert count(r'^traffic_breakdown_coretomem\[TEXTURE_ACC_R\]\s*=\s*\d+\s*\{8:(\d+),\}')==4
assert count(r'^\s*L2_cache_stats_breakdown\[TEXTURE_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)')==16
assert count(r'^\s*L2_cache_stats_breakdown\[TEXTURE_ACC_R\]\[MISS\]\s*=\s*(\d+)')==4
assert count(r'^\s*L2_cache_stats_breakdown\[TEXTURE_ACC_R\]\[SECTOR_MISS\]\s*=\s*(\d+)')==12
T=Path(c['trace_entry']).parent;group=next(T.glob('*.traceg.xz'));original=next(Path('/root/data/ada9_parent_cold_review_20261024_v1').glob('ada_linear_texture_producer_v9_20261024_v1/native_attempts/*/*/*/traces/kernel*.trace.xz'))
assert sha(original)=='87a86a91b128a05e8453bab928ec27b42c191aa3e6e2ac0937f94069074b55ed'
raw_warps=defaultdict(list)
with lzma.open(original,'rt')as f:
 for line in f:
  if re.match(r'^\d+ \d+ \d+ \d+ ',line):
   t=line.split(maxsplit=4);assert tuple(map(int,t[:3]))==(0,0,0);raw_warps[int(t[3])].append(t[4])
warps=defaultdict(list);cta_count=0;wid=None
with lzma.open(group,'rt')as f:
 for line in f:
  if line.startswith('thread block ='):assert line.strip()=='thread block = 0,0,0';cta_count+=1
  elif line.startswith('warp ='):wid=int(line.split('=')[1]);assert wid not in warps
  elif re.match(r'^[0-9a-fA-F]{16}\s',line):warps[wid].append(line)
assert cta_count==1 and dict(warps)==dict(raw_warps)and set(warps)=={0,1}
triples=[]
for wid,lines in warps.items():
 assert len(lines)==13
 for line in lines:
  t=line.split();pc=int(t[0],16);mask=int(t[1],16);op=t[3+int(t[2])];assert pc>2**32;triples.append((pc,mask,op))
assert Counter(triples)==Counter((int(v['pc'],16),int(v['mask'],16),v['op'])for v in source)
assert Counter(m for _,m,op in triples if op=='EXIT')==Counter([0xffffffff,0x1f])
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
assert n==u['sample_count']==44 and len(seen)==8 and seen==set(u['mapped_dependency_union'])
cp=u['checkpoints'];assert [v['label']for v in cp]==['FIRST_ISSUE','TERMINAL']
for v in cp:assert v['state']in('T','t')and(v['pid'],v['start_ticks'])==(u['primary_identity']['pid'],u['primary_identity']['start_ticks'])and s['binary']in v['paths']
reg=json.loads(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_text());row=reg['registered_future_requests'][s['request']];assert row['budget']==row['consumed']==1
campaign=sum(reg['registered_future_requests'].get(k,{}).get('consumed',0)for k in s['campaign']['request_ids']);assert campaign==8
out={'status':'PARENT_INDEPENDENT_TEX37_ADA9_NATIVE_COMPATIBILITY_JOIN_PASS','request':s['request'],'run':str(O),'raw_sha256':x['raw_sha256'],'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'pins_checked_current_full_SHA':174,'source_records':26,'aux_records':10,'decoded_source_lane_instructions':481,'decoded_aux_lane_instructions':185,'actual_total_issued_lane_instructions':666,'issue_evidence_scope':'Full source/decoded PC-mask-opcode multiset plus actual aggregate issue count and completed CTA; no per-PC issue log claimed','constant_lane_accesses':222,'constant_width8_records':6,'constant_width4_records':6,'L1C_access_miss':[12,6],'texture_lane_instructions':37,'L1T_access_miss_pending':[6,4,2],'TEX_external_misses':4,'L2_TEX_total_miss_sector_miss':[16,4,12],'actual_core_global_write_requests':5,'ctas_issued_completed':1,'physical_warps':2,'physical_EXIT_masks':['ffffffff','1f'],'physical_EXIT_lanes':37,'all_original_raw_and_grouped_warp_record_bytes_equal':True,'source_decoded_full64_PC_mask_opcode_multisets_equal':True,'maps_samples':44,'mapped_paths_current_full_SHA':8,'checkpoints':cp,'scope':'Only exact actual module83f26,LINEAR U32 512B,one object/context/launch37,wholeAPI handle<=UINT32,inbounds signed indices and originalTLD.SCR.B.LZ','hardware_timing_or_EP_scientific_or_bulk_qualification':False,'maps_scope':x['maps_child_discovery_scope'],'campaign_consumed':8,'campaign_ceiling':8,'automatic_retry':False,'archive_and_reservation_retirement_pending':True,'GPU_or_simulator_execution_by_this_verifier':False,'verifier_sha256':sha(Path(__file__)),'unix':time.time()}
p=O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');(R/'control/ADA_TEX37_ADA9_PARENT_TERMINAL_JOIN.json').write_bytes(p.read_bytes())
print(json.dumps({k:v for k,v in out.items()if k!='checkpoints'}))
