#!/usr/bin/env python3
"""Emit typed source-bound definitions, without reading additional runs."""
import csv,json,re
import mechanism_consumer_cpu_174_v1 as m

def main():
 evidence=json.loads((m.PACK/'COUNTER_EVIDENCE.json').read_text())['runs']
 with (m.PACK/'EXISTING_RUN_MECHANISM.tsv').open() as f:fields=csv.DictReader(f,delimiter='\t').fieldnames
 defs=[]
 for field in fields:
  unit='events';stage='terminal summed64SM / lifetime counters; final print only';domain='see raw names; fixed original full ordered workload';retry='no';comparison='same typed counter and source path only';numer=field;denom='1';source='src/gpgpu-sim/shader.cc:5702-6065';explain='Raw counter; not a GPU stall-cycle contribution.'
  if field in ('workload','arm','attempt_uuid','active_PIB','lower_cap'):
   unit='identity string' if field in ('workload','arm','attempt_uuid') else 'entries';source='accepted spec/config and exact UUID index';stage='before launch immutable identity / effective config';comparison='declared identity/design difference';explain='Not a sampled performance counter.'
  elif field in ('cycles','active_thread_instructions','ordered_kernels'):
   unit={'cycles':'GPU core cycles','active_thread_instructions':'active lane instructions','ordered_kernels':'kernels'}[field];source='src/gpgpu-sim/gpu-sim.cc:1812-1837';stage='final gpu_tot_*; ordered kernel headers checked separately';comparison='same original input and complete ROI only';explain='Per-kernel gpu_sim_insn summed; final gpu_tot_sim_insn crosschecked. Never sum cumulative snapshots.'
  elif field in ('ready_hit_events','pending_merge_events','cacheable_new_line_requests','tag_evictions'):
   unit='accepted128B logical-reference events' if field!='tag_evictions' else 'logical mapping replacement events';domain='cacheable DTC load references, not stores or all warp instructions';source='src/gpgpu-sim/dtc-l1-common.h:235-301,567-629;src/gpgpu-sim/shader.cc:3000-3140,3310-3455';comparison='IO/OO same units and acceptance stage; conventional lookup events UNCOMPARABLE';explain='ready means physical ready at accepted lookup; pending means attach to not-yet-ready mapped allocation; new requires new whole-line lower request. Directly counted accepted references sum to registered dependencies; not Tag grant attempts.'
  elif field=='duplicate_inflight_after_eviction':
   source='src/gpgpu-sim/dtc-l1-common.h:271-285';domain='IO cacheable lines';comparison='IO-only; OO UNAVAILABLE';explain='Count new access only when evicted original line remains pending; excludes all later cold reaccesses. Not a complete duplicate/reuse-distance trace.'
  elif field in ('tag_grant_events','tag_quota_reject_events','no_free_physical_events','allocation_width_reject_events'):
   source='src/gpgpu-sim/dtc-l1-common.h:198-230,235-301,530-565,567-629';retry='yes, successful Tag service can precede unsuccessful allocation; rejected repeated attempts not deduplicated';comparison='IO available; OO not printed; BASE Tag grants/arbitration differ from DTC allocation-reference statistics';domain='frontend attempt paths';explain='Counter attempts/failed grants. Not unique misses, disjoint bottleneck fractions or measured stall cycles.'
  elif field in ('PIB_full_events','MSHR_entry_reject_events','MSHR_merge_reject_events'):
   source='src/gpgpu-sim/dtc-l1-common.h:1782-1797;src/gpgpu-sim/gpu-cache.cc:1457-1521;src/gpgpu-sim/shader.cc:5990-6047';retry='yes';comparison='conventional path only; finite PIB-full UNAVAILABLE and finite conventional side MSHR UNCOMPARABLE with DTC main load path';domain='BASE PIB admission / ordinary cache MSHR fails; MSHR aggregate includes memory access types';explain='Repeated capacity/merge rejection events; legacy cycle aliases not cycle-deduplicated. Entry-full and merge-slot-full are different.'
  elif field in ('lower_credit_acquired','lower_credit_released','cap_full_events','candidate_queue_reject_events'):
   source='src/gpgpu-sim/gpu-sim.cc:1331-1370;src/gpgpu-sim/shader.cc:3020-3140,3310-3455';retry='yes for rejection counters; no for successful credit acquire/release';comparison='credit ownership stage differs BASE/finite; compare successful injected global reads instead; cap-full zero is scoped only';domain='DTC lower-read ownership and bounded candidate queue';explain='Credit acquired at creation, released on whole-line completion. Does not measure DRAM access or elapsed stall time; creation queue retry count is not a cycle count.'
  elif field in ('global_read_injected','global_write_injected'):
   source='src/gpgpu-sim/shader.cc:7579-7643';unit='successfully ICNT-injected mem_fetch packets';domain='GLOBAL_ACC_R, or GLOBAL_ACC_W plus L1_WRBK for write counter';comparison='read count aligned across all9 only after no local/atomic/bypass and four32B sectors per128B read checks';stage='icnt_inject_request_packet -> update_icnt_stats, once on successful injection';explain='No rejected retry counted; write counter includes writeback path if present. Still not a DRAM request.'
  elif field.startswith('L2_read_'):
   source='src/gpgpu-sim/gpu-cache.cc:695-716,954-996;src/gpgpu-sim/gpu-sim.cc:1935-1975';unit='32B L2 sector access outcomes';domain='GLOBAL_ACC_R only, stream0 of fixed workloads';retry='yes for RESERVATION_FAIL, excluded from TOTAL_ACCESS; MSHR_HIT is supplementary, not added twice';comparison='same L2 access/outcome stage across designs; HIT excludes HIT_RESERVED';stage='per-stream cache_stats cumulative, final print; all selected kernels use same stream';explain='TOTAL_ACCESS = HIT+HIT_RESERVED+MISS+SECTOR_MISS. Raw reservation failures are retry events, not accepted requests or stall cycles.'
   if field=='L2_read_requested_payload_bytes':unit='requested L2 read payload bytes';numer='L2_read_sectors*32';explain='Successful read demand reaching L2, independently4*GLOBAL_ACC_R injection. NOT DRAM bytes and not wire/header traffic.'
  elif field.startswith('L2_all_'):
   source='src/gpgpu-sim/gpu-sim.cc:1935-1975;src/gpgpu-sim/gpu-cache.cc:954-996';domain='all L2 read/write/access classes';unit='L2 access outcomes';retry='included only in reservation-retry field';comparison='all-class context only; not interchangeable with read-only traffic';explain='Writes can dominate this total; use typed GLOBAL_ACC_R buckets for read comparison.'
  elif field.startswith('DRAM_'):
   source='src/gpgpu-sim/dram.cc:560-623,691-705;src/gpgpu-sim/mem_latency_stat.cc:283-294';domain='all controller DRAM transfers, all address types; read n_rd excludes only explicit L2 allocation category';stage='last n_cmd tuple for each of20 controllers; cumulative monotone across kernel prints, never sum repeated aliases';comparison='same frozen DRAM command stage/atom configuration; not exclusively cacheable reads';unit='issued DRAM transfer commands';explain='n_rd_L2_A separate read-allocation commands; n_wr_bk separate L2 writebacks. Both categories included for payload byte totals. CSV DRAM-sector totals independently match at terminal.'
   if field=='DRAM_atom_bytes':unit='bytes per DRAM command';source='src/gpgpu-sim/gpu-sim.h:dram_atom_size formula / effective buswidth,burst,n_mem_per_ctrlr';explain='Fixed16byte bus * burst2 *1chip =32B.'
   elif field.endswith('_payload_bytes'):
    unit='DRAM transferred payload bytes';numer='(n_rd+n_rd_L2_A)*32' if 'read' in field else '(n_write+n_wr_bk)*32';explain='Derived from actual issued transfer-command counts, not lower credits; excludes row/column control/PHY overhead and memcpy preload that does not issue DRAM commands.'
  elif field.startswith('service_') or field.startswith('mean_'):
   source='src/gpgpu-sim/shader.cc:2105-2127,2961-2991,4946-4985,5727-5740;src/gpgpu-sim/dtc-l1-common.h:63-98';domain='cacheable load warp instructions for retired/residence/collection; all PIB operations for PIB integral; all allocated physical lines for physical integral';comparison='finite IO/OO only; C+/C16/C80/WAIT UNAVAILABLE at this definition';explain='Fully-ready means ALL references admitted and frontend data-ready, observed independently of IO head. Includes mandatory selection edge; excludes earlier admission/refill/replay. Sum decomposition exact; overlapping instruction intervals cannot be summed into GPU cycles.'
   if 'map_loss' in field:
    source='src/gpgpu-sim/dtc-l1-common.h:271-280,458-468,596-608,942-951';domain='freed physical allocations after logical mapping loss';comparison='same interval units; IO/OO reclaim policies and event populations differ';explain='Only completed mapping-loss-to-free intervals; mapped terminal residents excluded. Includes zero-cycle immediate OO reclaim. Not queryable data occupancy or a miss/reuse rate.'
   if field=='service_samples':unit='SM-core-cycle samples';numer='64*gpu_tot_sim_cycle';explain='All64 SMs, idle/gated/tail included, not active-only.'
   elif field in ('service_pib_integral','service_physical_integral'):unit='entry*core-cycle' if 'pib' in field else 'allocated-line*core-cycle'
   elif field=='service_collected_sectors':unit='collected requested32B sectors';explain='Union of referenced sectors for each cacheable warp instruction; includes repeated instructions, excludes unused sectors fetched by a128B fill.'
   elif field in ('service_retired','service_map_loss_to_free_count'):unit='cacheable retired warp instructions' if field=='service_retired' else 'completed mapping-loss-to-free events'
   else:unit='summed instruction core-cycle intervals' if 'map_loss' not in field else 'summed allocation core-cycle intervals'
   if field.startswith('mean_'):
    pair={'mean_PIB_all64_SM_cycles':('service_pib_integral','service_samples'),'mean_physical_all64_SM_cycles':('service_physical_integral','service_samples'),'mean_ready_to_complete':('service_fully_ready_to_complete_sum','service_retired'),'mean_ready_to_collect':('service_ready_to_collect_sum','service_retired'),'mean_collect':('service_collection_cycles','service_retired'),'mean_post_collect_WB':('service_wb_wait','service_retired'),'mean_map_loss_to_free':('service_map_loss_to_free_sum','service_map_loss_to_free_count')}[field]
    numer,denom=pair;unit='entries per SM over ALL GPU cycles' if 'PIB_all' in field else 'allocated physical lines per SM over ALL GPU cycles' if 'physical_all' in field else 'core cycles per completed allocation event' if 'map_loss' in field else 'core cycles per cacheable retired warp instruction'
  elif field.startswith('L1D_path_'):
   source='src/gpgpu-sim/shader.cc:5619-5645';domain='ordinary L1D cache path: conventional loads+stores; finite main loads bypass it';retry='reservation-retries yes; other buckets exclude rejected attempts';comparison='UNCOMPARABLE as main-load hit rate across conventional/finite; finite ordinary-side context only';explain='An ordinary L1D miss-rate does not measure the DTC logical Tag hit-rate.'
  elif field.startswith(('ordinary_','dynamic_')):
   source='src/gpgpu-sim/shader.cc:4380-4400,5702-5726';unit='warp instruction observations';domain='dynamic includes all issued memory operations of class; ordinary admits/retires excludes cacheable DTC load path';comparison='source-domain parity where available; conventional ordinary sidecar count is not the same mechanism';explain='Warp instructions, not thread instructions, line references or bytes; dynamic counts retain zero-effective-mask operations when issued.'
  hashes={str(core/name):m.sha(core/name) for name in re.findall(r'src/[A-Za-z0-9_./-]+\.(?:cc|h)',source) for core in [m.CORE,m.TRAD]}
  defs.append(dict(field=field,typed_unit=unit,numerator=numer,denominator=denom,logging_stage=stage,address_and_instruction_scope=domain,includes_retry=retry,per_kernel_or_whole='whole workload cumulative final snapshot; per-kernel cycle/insn explicit exception',comparability=comparison,source_location=source,source_SHA256=json.dumps(hashes,sort_keys=True),source_SHA_binding='SOURCE_SHA256.tsv exact finite6fba0136 and traditional6582b9d source SHA; accepted config identities in INPUT_RUN_IDENTITIES.json',explanation=explain))
 with (m.PACK/'METRIC_DEFINITIONS.tsv').open('x') as f:
  w=csv.DictWriter(f,fieldnames=list(defs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(defs)
 # Preserve actual conventional hit/pending counters at their own units rather
 # than pretending they are absent or share the finite128B-reference unit.
 contexts=[]
 suffixes=['HIT','HIT_RESERVED','MISS','SECTOR_MISS','MSHR_HIT','RESERVATION_FAIL','TOTAL_ACCESS']
 for e in evidence:
  identity=e['identity'];r=dict(attempt_uuid=identity['uuid'],label=identity.get('label',identity.get('kind')),comparability='UNCOMPARABLE_WITH_FINITE_UNIQUE128B_REFERENCE_HITS')
  for s in suffixes:r['conventional_GLOBAL_ACC_R_'+s]=e['raw_scalars'].get('Total_core_cache_stats_breakdown[GLOBAL_ACC_R]['+s+']','UNAVAILABLE')
  contexts.append(r)
 with (m.PACK/'CONVENTIONAL_LOOKUP_CONTEXT.tsv').open('x') as f:
  w=csv.DictWriter(f,fieldnames=list(contexts[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(contexts)
 print('Definitions for',len(defs),'primary columns; separate conventional lookup context for9 runs')
if __name__=='__main__':main()
