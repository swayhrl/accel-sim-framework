#!/usr/bin/env python3
"""Pure c67 detailed-DRAM final32 extraction. No authority and no writes."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,pathlib,re
P=pathlib.Path
CORE='c67b332db703f09571ba6628222c77d71440e141'
FIELDS=['n_cmd','n_nop','n_act','n_pre','n_req','n_rd','n_rd_L2_A','n_write','n_wr_bk']
def need(ok,msg):
 if not ok:raise ValueError(msg)
def extract(raw,expected_final_cycle,effective_options):
 """Read exact last native-clock full DRAM[0..31] rows; preserve absent optional scalars."""
 need(type(expected_final_cycle)is int and expected_final_cycle>0,'positive accepted final core cycle required')
 need(effective_options['-gpgpu_simple_dram_model']=='0'and effective_options['-gpgpu_dram_scheduler']=='1','detailed FRFCFS semantics required')
 clock=None;pending=None;records={};duplicates=0;native={};rawhash=hashlib.sha256()
 hpat=re.compile(r'DRAM\[(\d+)\]: (\d+) bks, busW=(\d+) BL=(\d+) CL=(\d+),')
 with P(raw).open('rb')as f:
  for b in f:
   rawhash.update(b);line=b.decode('utf8',errors='strict')
   m=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
   if m:clock=int(m[1]);pending=None
   m=re.fullmatch(r'(gpgpu_n_dram_[A-Za-z_]+)\s*=\s*(\d+)\s*',line)
   if m and clock==expected_final_cycle:native[m[1]]=int(m[2])
   m=hpat.match(line)
   if m:pending={'channel':int(m[1]),'banks':int(m[2]),'busW':int(m[3]),'BL':int(m[4]),'CL':int(m[5]),'native_clock':clock}
   elif line.startswith('n_cmd=')and pending is not None:
    fields=dict(re.findall(r'([A-Za-z_0-9]+)=([0-9]+)',line));need(all(k in fields for k in FIELDS),'full DRAM row missing split counters')
    row={**pending,**{k:int(fields[k])for k in FIELDS}};sid=row['channel']
    need(all(0<=row[k]<=2**64-1 for k in FIELDS),'counter uint64')
    if clock==expected_final_cycle:
     need(sid in range(32),'unregistered final channel')
     if sid in records:need(records[sid]==row,'contradictory same-final-clock full DRAM counters');duplicates+=1
     records[sid]=row
    pending=None
 need(clock==expected_final_cycle and set(records)==set(range(32)),'latest native clock and exact32 complete full DRAM channels required; no earlier fallback')
 totals={k:sum(r[k]for r in records.values())for k in FIELDS};native_joins={}
 for n,v in {'gpgpu_n_dram_reads':totals['n_rd'],'gpgpu_n_dram_writes':totals['n_write']+totals['n_wr_bk'],'gpgpu_n_dram_commands':totals['n_cmd']}.items():
  if n in native:need(native[n]==v,'native scalar/full DRAM join '+n);native_joins[n]='PASS'
  else:native_joins[n]='UNKNOWN: helper scalar absent from actual raw'
 BL=int(effective_options['-gpgpu_dram_burst_length']);busW=int(effective_options['-gpgpu_dram_buswidth']);chips=int(effective_options['-gpgpu_n_mem_per_ctrlr']);ratio=int(effective_options['-dram_data_command_freq_ratio'])
 need(BL>0 and busW>0 and chips>0 and ratio>0,'positive bus/burst parameters')
 need(all(r['BL']==BL and r['busW']==busW for r in records.values()),'printed actual burst parameters differ')
 atom=BL*busW*chips;reads=totals['n_rd']+totals['n_rd_L2_A'];writes=totals['n_write']+totals['n_wr_bk'];bytes_total=(reads+writes)*atom
 return {'status':'FULL_DRAM32_FINAL_COUNTER_EXTRACTION_ONLY','scientific_acceptance_granted':False,'source_semantics_core_commit':CORE,'actual_source_identity_verified_by_this_extractor':False,'raw_sha256':rawhash.hexdigest(),'native_final_core_cycle':expected_final_cycle,'channels':{str(k):v for k,v in records.items()},'same_final_clock_duplicate_full_rows':duplicates,'totals':totals,'native_scalar_join':native_joins,'read_column_commands_including_write_allocate_reads':reads,'write_column_commands_including_WB':writes,'burst_bytes_per_column':atom,'modeled_read_bus_burst_bytes':reads*atom,'modeled_write_bus_burst_bytes':writes*atom,'modeled_total_bus_burst_bytes':bytes_total,'modeled_burst_capacity_fraction':{'numerator_burst_bytes':bytes_total,'denominator_DRAM_channel_ticks_times_atom_bytes':totals['n_cmd']*atom,'value':bytes_total/(totals['n_cmd']*atom)if totals['n_cmd']else'UNKNOWN'},'data_command_freq_ratio':ratio,'BL_over_data_command_freq_ratio_integer':BL//ratio,'field_unit_notes':{'n_cmd':'DRAM calls/ticks, including idle/NOP and row/column opportunities; not read+write count','n_req':'dram_t::push accepted memory packets, not bursts','n_rd':'read column commands excluding L2 write-allocate read commands','n_rd_L2_A':'read column commands for L2 write-allocate reads','n_write':'write column commands excluding L2 writeback commands','n_wr_bk':'L2 writeback column commands','burst_bytes':'modeled bus transfer bytes per column; no ECC/address/command overhead or hardware measurement'},'excluded':['n_ref_event uninitialized/garbage; never used','abbreviated DRAM(id) print omits alloc-read/WB splits','cumulative repeated snapshots never added','EPL2DRAM successful_* and LIFE DRAM_SERVICE are lower-pop admission payload populations, not these column commands']}
