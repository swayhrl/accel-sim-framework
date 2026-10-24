from pathlib import Path
import json,re,lzma,hashlib,collections
B=Path('/root/data/ep_l2_main_ada_legacy65_r2_compat_20261024_v1');O=B/'run/86b6f52282c943d69b377f4332a4246a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
S=json.loads((B/'control/FROZEN_SPEC.json').read_text());E=json.loads((O/'EXIT.json').read_text());C=next(iter(S['cases'].values()))
assert E['exit_code']==0 and E['stop_reason']is None and sha(O/'raw.log')==E['raw_sha256']
for p,h in S['pinned_files'].items():assert sha(p)==h
text=(O/'raw.log').read_text();rows=[]
for m in re.finditer(r'ADA8_DECODE pc=([0-9a-f]+) mask=([0-9a-f]+) aux=(\d+) op=(\S+).*space=(\d+) width=(\d+) const_bank=(-?\d+) const_offset=(-?\d+)',text):
 pc,mask,aux,op,space,width,bank,offset=m.groups();rows.append({'pc':int(pc,16),'mask':int(mask,16),'aux':int(aux),'op':op,'space':int(space),'width':int(width),'bank':int(bank),'offset':int(offset)})
source=[x for x in rows if not x['aux']];aux=[x for x in rows if x['aux']]
assert len(source)==39 and len(aux)==12
assert sum(x['mask'].bit_count()for x in source)==780 and sum(x['mask'].bit_count()for x in aux)==260
origin=next(Path(C['trace_entry']).parent.glob('kernel*.trace.xz'));expected=[]
with lzma.open(origin,'rt')as f:
 for line in f:
  t=line.split()
  if len(t)<8 or not all(x.isdigit()for x in t[:4]):continue
  pc=int(t[4],16);mask=int(t[5],16);op=t[7+int(t[6])];expected.append((pc,mask,op))
assert collections.Counter(expected)==collections.Counter((x['pc'],x['mask'],x['op'])for x in source)
def metric(pattern):return int(re.findall(pattern,text,re.M)[-1])
stats={'gpu_tot_sim_insn':metric(r'^gpu_tot_sim_insn = (\d+)$'),'const_lane_instances':metric(r'^gpgpu_n_const_mem_insn = (\d+)$'),'actual_const_requests':metric(r'^gpgpu_n_mem_const = (\d+)$'),'L1C_accesses':metric(r'L1C_total_cache_accesses = (\d+)'),'L1C_misses':metric(r'L1C_total_cache_misses = (\d+)'),'L2_CONST_accesses':metric(r'L2_cache_stats_breakdown\[CONST_ACC_R\]\[TOTAL_ACCESS\] = (\d+)'),'global_write_requests':metric(r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[TOTAL_ACCESS\] = (\d+)'),'issued_ctas':metric(r'^gpu_tot_issued_cta = (\d+)$'),'completed_ctas':metric(r'ctas_completed (\d+)')}
assert stats['gpu_tot_sim_insn']==1040 and stats['const_lane_instances']==325
assert stats['actual_const_requests']>0 and stats['L1C_accesses']>=stats['L1C_misses']>0 and stats['L2_CONST_accesses']>0 and stats['global_write_requests']>0
assert stats['issued_ctas']==stats['completed_ctas']==1
stores=sum(x['mask'].bit_count()for x in source if x['op'].startswith('STG'));exits=sum(x['mask'].bit_count()for x in source if x['op']=='EXIT')
assert stores==exits==65
exitmasks=sorted(x['mask']for x in source if x['op']=='EXIT'and x['mask'])
assert exitmasks==[1,0xffffffff,0xffffffff]
U=json.loads((O/'MAP_OBSERVATIONS/UNION.json').read_text());assert len(U['mapped_dependency_union'])==8
for p,row in U['mapped_dependency_union'].items():assert sha(p)==row['sha256']==S['pinned_files'][p]
assert [x['label']for x in U['checkpoints']]==['FIRST_ISSUE','TERMINAL']
for cp in U['checkpoints']:
 assert cp['state']=='T'and cp['pid']==U['primary_identity']['pid']and cp['start_ticks']==U['primary_identity']['start_ticks']
 assert sha(O/'MAP_OBSERVATIONS'/cp['saved_maps'])==cp['maps_sha256']
proof={'status':'SCOPED_LEGACY65_R2_NATIVE_TERMINAL_JOIN_PASS','uuid':E['uuid'],'raw_sha256':E['raw_sha256'],'all_spec_pins_verified':len(S['pinned_files']),'source_sass_records':39,'source_active_lanes':780,'aux_uops':12,'aux_active_lanes':260,'all_original_pc_mask_opcode_multiset_matches':True,'source_trace_sha256':sha(origin),'stats':stats,'global_store_lanes':stores,'physical_EXIT_lanes':exits,'physical_nonzero_EXIT_masks':[hex(x)for x in exitmasks],'zero_mask_source_records':sum(x['mask']==0 for x in source),'maps_samples':U['sample_count'],'map_union_paths':len(U['mapped_dependency_union']),'live_stopped_checkpoints':U['checkpoints'],'maps_discovery_scope':S['maps_observation'],'numeric_reference':'Actual same-process GPU full65 CPU check, trace-driven consumer does not recompute values','hardware_timing_qualification':False,'EP_scientific_promotion':False,'campaign_consumed_after':7,'campaign_ceiling':8}
(O/'INDEPENDENT_TERMINAL_JOIN.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
