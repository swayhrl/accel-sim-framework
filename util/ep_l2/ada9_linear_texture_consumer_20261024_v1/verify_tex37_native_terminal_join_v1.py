from pathlib import Path
import json,re,lzma,hashlib,collections,sys
B=Path('/root/data/ep_l2_main_ada_tex37_ada9_compat_20261024_v1')
O=Path(sys.argv[1]);need=lambda x,m: x or (_ for _ in ()).throw(AssertionError(m))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
S=json.loads((B/'control/FROZEN_SPEC.json').read_text());E=json.loads((O/'EXIT.json').read_text());C=S['cases']['tex37_ada9_v1']
need(E['exit_code']==0 and E['stop_reason']is None,'terminal failed')
need(sha(O/'raw.log')==E['raw_sha256'],'raw SHA')
for p,h in S['pinned_files'].items():need(sha(p)==h,'pin '+p)
text=(O/'raw.log').read_text();rows=[]
for m in re.finditer(r'ADA8_DECODE pc=([0-9a-f]+) mask=([0-9a-f]+) aux=(\d+) op=(\S+).*space=(\d+) width=(\d+) const_bank=(-?\d+) const_offset=(-?\d+)',text):
 pc,mask,aux,op,space,width,bank,offset=m.groups()
 rows.append(dict(pc=int(pc,16),mask=int(mask,16),aux=int(aux),op=op,space=int(space),width=int(width),bank=int(bank),offset=int(offset)))
source=[x for x in rows if not x['aux']];aux=[x for x in rows if x['aux']]
need(len(source)==26 and len(aux)==10,'record count')
need(sum(x['mask'].bit_count()for x in source)==481 and sum(x['mask'].bit_count()for x in aux)==185,'lane count')
origin=next(Path(C['trace_entry']).parent.glob('kernel*.trace.xz'));expected=[]
with lzma.open(origin,'rt')as f:
 for line in f:
  t=line.split()
  if len(t)<8 or not all(x.isdigit()for x in t[:4]):continue
  expected.append((int(t[4],16),int(t[5],16),t[7+int(t[6])]))
need(collections.Counter(expected)==collections.Counter((x['pc'],x['mask'],x['op'])for x in source),'original PC/mask/op multiset')
const=[x for x in rows if x['space']==8];tex=[x for x in source if x['op']=='TLD.SCR.B.LZ']
need(sum(x['mask'].bit_count()for x in const)==222,'const222')
need(collections.Counter(x['width']for x in const)=={4:6,8:6},'constant width-preserving warp loads')
need(len(tex)==2 and all(x['space']==9 and x['width']==4 for x in tex),'TLD tex-space/width')
need(sum(x['mask'].bit_count()for x in tex)==37,'TLD37')
def lanes(prefix):return sum(x['mask'].bit_count()for x in source if x['op'].startswith(prefix))
need((lanes('LDG'),lanes('STG'),lanes('EXIT'))==(74,37,37),'global/EXIT lanes')
need(sorted(x['mask']for x in source if x['op']=='EXIT')==[31,0xffffffff],'physical EXIT masks')
def metric(pattern):
 m=re.findall(pattern,text,re.M);need(bool(m),'missing metric '+pattern);return int(m[-1])
stats={
 'gpu_tot_sim_insn':metric(r'^gpu_tot_sim_insn = (\d+)$'),
 'const_lane_instances':metric(r'^gpgpu_n_const_mem_insn = (\d+)$'),
 'actual_const_requests':metric(r'^gpgpu_n_mem_const = (\d+)$'),
 'actual_texture_interconnect_requests':metric(r'^gpgpu_n_mem_texture = (\d+)$'),
 'L1C_accesses':metric(r'L1C_total_cache_accesses = (\d+)'),
 'L1C_misses':metric(r'L1C_total_cache_misses = (\d+)'),
 'L1T_accesses':metric(r'L1T_total_cache_accesses = (\d+)'),
 'L1T_misses':metric(r'L1T_total_cache_misses = (\d+)'),
 'L1T_hits':metric(r'Total_core_cache_stats_breakdown\[TEXTURE_ACC_R\]\[HIT\] = (\d+)'),
 'L1T_cache_misses':metric(r'Total_core_cache_stats_breakdown\[TEXTURE_ACC_R\]\[MISS\] = (\d+)'),
 'L2_TEX_hit':metric(r'L2_cache_stats_breakdown\[TEXTURE_ACC_R\]\[HIT\] = (\d+)'),
 'L2_TEX_miss':metric(r'L2_cache_stats_breakdown\[TEXTURE_ACC_R\]\[MISS\] = (\d+)'),
 'global_write_requests':metric(r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[TOTAL_ACCESS\] = (\d+)'),
 'issued_ctas':metric(r'^gpu_tot_issued_cta = (\d+)$'),
 'completed_ctas':metric(r'ctas_completed (\d+)')}
need(stats['gpu_tot_sim_insn']==666 and stats['const_lane_instances']==222,'issued model counts')
need(stats['actual_const_requests']>0 and stats['L1C_accesses']>=stats['L1C_misses']>0,'const actual route')
need(stats['L1T_accesses']==6 and stats['L1T_misses']>0 and stats['actual_texture_interconnect_requests']>0,'actual six TEX cache requests')
need(stats['L1T_hits']+stats['L1T_cache_misses']>0 and stats['L2_TEX_hit']+stats['L2_TEX_miss']>0,'actual TEX cache side effects')
need(stats['global_write_requests']>0 and stats['issued_ctas']==stats['completed_ctas']==1,'write/CTA terminal')
U=json.loads((O/'MAP_OBSERVATIONS/UNION.json').read_text())
for p,row in U['mapped_dependency_union'].items():need(sha(p)==row['sha256']==S['pinned_files'][p],'mapped path '+p)
need([x['label']for x in U['checkpoints']]==['FIRST_ISSUE','TERMINAL'],'stopped checkpoint labels')
for cp in U['checkpoints']:
 need(cp['state']=='T'and cp['pid']==U['primary_identity']['pid']and cp['start_ticks']==U['primary_identity']['start_ticks'],'stopped checkpoint identity')
 need(sha(O/'MAP_OBSERVATIONS'/cp['saved_maps'])==cp['maps_sha256'],'checkpoint map SHA')
proof=dict(status='SCOPED_ADA9_LINEAR_U32_EXACT37_NATIVE_TERMINAL_JOIN_PASS',uuid=E['uuid'],raw_sha256=E['raw_sha256'],all_spec_pins_verified=len(S['pinned_files']),source_sass_records=26,source_active_lanes=481,aux_uops=10,aux_active_lanes=185,total_model_lane_uops=666,all_original_pc_mask_opcode_multiset_matches=True,source_trace_sha256=sha(origin),stats=stats,constant_warp_widths={4:6,8:6},constant_space='symbolic bank/context + byte offset, not GPU VA',TLD_lane_accesses=37,texture_address_origin='API_RESOURCE_LINEAR_SIGNED_INDEX_RESOLUTION_NOT_NVBIT_NATIVE_MREF',global_load_lanes=74,global_store_lanes=37,physical_EXIT_lanes=37,physical_nonzero_EXIT_masks=['0xffffffff','0x1f'],maps_samples=U['sample_count'],map_union_paths=len(U['mapped_dependency_union']),live_stopped_checkpoints=U['checkpoints'],maps_discovery_scope=S['maps_observation'],numeric_reference='same-process actual GPU full37 CPU check; trace consumer does not recompute values',hardware_timing_qualification=False,EP_scientific_promotion=False,campaign_consumed_after=8,campaign_ceiling=8)
p=O/'INDEPENDENT_TERMINAL_JOIN.json'
with p.open('x')as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof,indent=2))
