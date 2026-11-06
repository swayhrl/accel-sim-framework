"""Postprocess-only source-proven sparse stock-L2 traffic reporting; no model/source writes."""
from pathlib import Path
import hashlib,os,re,sys,threading
P=Path
MARKER='_DTC_ORACLE_SOURCE_PROVEN_SPARSE_L2_REPORTING_V1'
LEGACY=P('/root/data/ep_l2_dtc_l1_native_v2/DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py')
LEGACY_SHA='9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4'
PINS={'oracle_strict.py':'4036ac6ae6f1ba7e18918fefde2e6c9c0bc53de38dff08581fca8f7ff4a6c162','oracle_population.py':'26f085f956bc935542c3baa34e82cd3d0b379a653fcd2db9a12783d99c0f61e3','oracle_results.py':'e9ed50a7534904c5a6a434282b1d760ff494da21c665eb9b1df3eeda7a1cb3ee'}
READ_KEYS=tuple('GLOBAL_ACC_R:'+k for k in ('HIT','HIT_RESERVED','MISS','SECTOR_MISS','TOTAL_ACCESS'))
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
CORE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/source/integration-core')
CORE_PINS={'src/abstract_hardware_model.h':'e4cab8e64aad9a331fc49e987fd4e9a7be4f067b814dd866aa5b461b300ce87c','src/gpgpu-sim/gpu-cache.cc':'f600601f96c07b6618f198e7b37dd394f07bb286a5d7b7f76c72634d7f2b1dd1','src/gpgpu-sim/gpu-cache.h':'66337ac7440bc96db827718c5f56b66b7904cabc57b8d1053da40cd274c1aba1','src/gpgpu-sim/gpu-sim.cc':'9ca7d25243fd93bd9cf44abecc23d0c9545fdc57bb7c43d38154b5f0f7dba3e9'}
KINDS=('GLOBAL_ACC_R','CHIPLET_ACC_R','LOCAL_ACC_R','CONST_ACC_R','TEXTURE_ACC_R','GLOBAL_ACC_W','CHIPLET_ACC_W','LOCAL_ACC_W','L1_WRBK_ACC','L2_WRBK_ACC','INST_ACC_R','L1_WR_ALLOC_R','L2_WR_ALLOC_R')
STATES=('HIT','HIT_RESERVED','MISS','RESERVATION_FAIL','SECTOR_MISS','MSHR_HIT','WRITE_ALLOCATED')
COUNTED=('HIT','HIT_RESERVED','MISS','SECTOR_MISS')
def nullable_traffic(original,block):
 buckets={}
 for kind,outcome,value in re.findall(r'^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',block,re.M):
  key=kind+':'+outcome
  assert key not in buckets,'duplicate_L2_bucket'
  buckets[key]=int(value)
 missing=[k for k in READ_KEYS if k not in buckets]
 if not missing:return original(block)
 # Fail closed except the exact, independently proven zero-total sparse case.
 # No arbitrary missing counter becomes zero, no fabricated line is appended.
 assert missing==['GLOBAL_ACC_R:TOTAL_ACCESS'],'MISSING_REQUIRED_L2_READ_STATUS_COUNTER_HOLD'
 assert all(sha(CORE/f)==v for f,v in CORE_PINS.items()),'FROZEN_SPARSE_PRINTER_SOURCE_REQUIRED'
 assert set(k.split(':')[0]for k in buckets)==set(KINDS),'FULL_MEM_ACCESS_TYPE_POPULATION_REQUIRED'
 assert all(k+':'+v in buckets for k in KINDS for v in STATES),'ALL_PRINTED_STATUS_BUCKETS_REQUIRED'
 assert all(set(x.split(':')[1]for x in buckets if x.startswith(k+':'))<=set(STATES+('TOTAL_ACCESS',))for k in KINDS),'UNEXPECTED_CACHE_STATUS'
 totals={k:sum(buckets[k+':'+v]for v in COUNTED)for k in KINDS}
 # The source's TOTAL_ACCESS accumulator is unsigned32. Reject overflow, even
 # though get_sub_stats()/bank Access use independent 64-bit accumulators.
 assert all(0<=v<2**32 for v in totals.values()),'SPARSE_TOTAL_UINT32_OVERFLOW_HOLD'
 for k,total in totals.items():
  if total:
   assert buckets.get(k+':TOTAL_ACCESS')==total,'NONZERO_KIND_TOTAL_MUST_BE_PRINTED_AND_MATCH'
  else:
   assert k+':TOTAL_ACCESS'not in buckets,'SOURCE_ZERO_TOTAL_OMISSION_REQUIRED'
 assert all(buckets['GLOBAL_ACC_R:'+v]==0 for v in COUNTED),'MISSING_NONZERO_READ_TOTAL_HOLD'
 printed=re.findall(r'^L2_total_cache_accesses\s*=\s*(\d+)\s*$',block,re.M)
 assert len(printed)==1,'ONE_INDEPENDENT_GLOBAL_L2_ACCESS_COUNTER_REQUIRED'
 banks=re.findall(r'^L2_cache_bank\[(\d+)\]: Access = (\d+),',block,re.M)
 assert len(banks)==40 and {int(i)for i,_ in banks}==set(range(40)),'FULL_40_L2_BANK_ACCESS_COUNTERS_REQUIRED'
 global_access=int(printed[0]);bank_access=sum(int(v)for _,v in banks)
 assert global_access==bank_access==sum(totals.values()),'INDEPENDENT_BANK_GLOBAL_AND_KIND_ACCESS_CONSERVATION'
 # Independently preserve miss/pending/reservation accounting, too.
 aggregate_proof={}
 for label,statuses in [('cache_misses',('MISS','SECTOR_MISS')),('cache_pending_hits',('HIT_RESERVED',)),('cache_reservation_fails',('RESERVATION_FAIL',))]:
  values=re.findall(r'^L2_total_'+label+r'\s*=\s*(\d+)\s*$',block,re.M)
  assert len(values)==1,'ONE_INDEPENDENT_L2_'+label+'_COUNTER_REQUIRED'
  derived=sum(buckets[k+':'+v]for k in KINDS for v in statuses)
  assert int(values[0])==derived,'INDEPENDENT_L2_'+label+'_CONSERVATION'
  aggregate_proof[label]=derived
 other_access=sum(v for k,v in totals.items()if k!='GLOBAL_ACC_R')
 independently_derived_read_total=global_access-other_access
 assert totals['GLOBAL_ACC_R']==independently_derived_read_total==0,'L2_ACCEPTED_READ_BUCKET_PARTITION_SOURCE_PROVEN'
 # Required DRAM population/field/duplicate checks remain unchanged.
 dram=re.findall(r'^DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)',block,re.M)
 assert len(dram)==20 and {int(i)for i,_ in dram}==set(range(20)),'DRAM_population_20_controllers'
 controllers={}
 for index,line in dram:
  entries=re.findall(r'(n_cmd|n_nop|n_act|n_pre|n_req|n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)',line)
  row={key:int(value)for key,value in entries}
  assert len(row)==len(entries),'duplicate_DRAM_field'
  controllers[str(int(index))]=row
 rd=sum(row['n_rd']+row['n_rd_L2_A']for row in controllers.values())
 wr=sum(row['n_write']+row['n_wr_bk']for row in controllers.values())
 return dict(L2_buckets=buckets,L2_accepted_read_32B_sectors=None,L2_read_payload_bytes=None,
  L2_read_statistics_status='RAW_TOTAL_UNPRINTED_SOURCE_PROVEN_SPARSE_ZERO',
  L2_read_statistics_missing_keys=missing,L2_reported_GLOBAL_ACC_R_TOTAL_ACCESS=None,
  L2_accepted_read_bucket_partition='PASS_SOURCE_SPARSE_ZERO_AND_INDEPENDENT_ACCESS_CONSERVATION',
  L2_derived_accepted_read_32B_sectors=independently_derived_read_total,L2_derived_read_payload_bytes=32*independently_derived_read_total,
  sparse_partition_proof=dict(read_status_sum=totals['GLOBAL_ACC_R'],global_accesses=global_access,
   all_40_bank_accesses=bank_access,other_kind_accesses=other_access,all_kind_accesses=totals,
   uint32_overflow_excluded=True,aggregate_proof=aggregate_proof,source_files=CORE_PINS,
   source_locations={'printer':'gpu-cache.cc:980-1000','independent_accessor':'gpu-cache.cc:1073-1079','bank_and_global':'gpu-sim.cc:1976-2001'}),
  DRAM_controllers=controllers,DRAM_atom_bytes=32,DRAM_issued_read_atoms=rd,DRAM_issued_write_atoms=wr,
  DRAM_read_payload_bytes=32*rd,DRAM_write_payload_bytes=32*wr,
  DRAM_n_ref_event='UNAVAILABLE_INHERITED_UNINITIALIZED_FIELD_RAW_PRESERVED',
  reporting_compatibility=dict(schema='DTC_ORACLE_SOURCE_PROVEN_SPARSE_L2_REPORTING_V1',source_sha256=sha(__file__),
   missing_values_are_null=True,original_lifecycle_and_oracle_checks_unchanged=True,
   original_traffic_partition_proven_by_source_and_independent_counters=True))
def wrap_legacy(module):
 assert P(module.__file__)==LEGACY and sha(LEGACY)==LEGACY_SHA
 if getattr(module,MARKER,False):return module
 original=module.traffic
 def traffic(block):return nullable_traffic(original,block)
 module.traffic=traffic;setattr(module,MARKER,True);return module

def wrap_population(module,root):
 root=P(root);assert P(module.__file__)==root/'tools/oracle_population.py' and sha(module.__file__)==PINS['oracle_population.py']
 if getattr(module,MARKER,False):return module
 original=module.load
 def loaded(name,path):
  value=original(name,path)
  return wrap_legacy(value)if P(path)==LEGACY else value
 module.load=loaded;setattr(module,MARKER,True);return module

def wrap_strict(module,root):
 root=P(root);assert P(module.__file__)==root/'tools/oracle_strict.py' and sha(module.__file__)==PINS['oracle_strict.py']
 if getattr(module,MARKER,False):return module
 original=module.load
 def loaded(name,path):
  value=original(name,path)
  return wrap_population(value,root)if P(path)==root/'tools/oracle_population.py' else value
 module.load=loaded;setattr(module,MARKER,True);return module

def wrap_consumer(module,root):
 root=P(root);assert P(module.__file__)==root/'tools/oracle_results.py' and sha(module.__file__)==PINS['oracle_results.py']
 if getattr(module,MARKER,False):return module
 original=module.load
 def loaded(name,filename):
  value=original(name,filename)
  return wrap_strict(value,root)if filename=='oracle_strict.py' else value
 module.load=loaded;setattr(module,MARKER,True);return module

def wrap_ops(module):
 if getattr(module,MARKER,False):return module
 original=module.load
 def loaded(name,path):
  value=original(name,path)
  return wrap_consumer(value,P(path).resolve().parents[1])if P(path).name=='oracle_results.py' else value
 module.load=loaded;setattr(module,MARKER,True);return module

def install(parent_module_name='dtc_oracle_initial_scientific_main_addon_forward_v2'):
 assert threading.current_thread()is threading.main_thread() and os.getpid()==1498278
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 parent=sys.modules[parent_module_name]
 assert sha(parent.__file__)=='f4b3338510b4c89ca16977c2f1fc13fcde262f8d8b3b21681946b177f2016778'
 state=getattr(sys.modules['__main__'],'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1');current=[]
 with state['lock']:
  for ctx in state['contexts'].values():
   wrap_consumer(ctx['consumer'],ctx['root']);current.append(ctx['request'])
  if not getattr(parent,MARKER,False):
   original=parent.load
   def loaded(name,path):
    value=original(name,path)
    return wrap_ops(value)if P(path).name=='oracle_ops.py' else value
   parent.load=loaded;setattr(parent,MARKER,True)
 return dict(status='POSTPROCESS_ONLY_SOURCE_PROVEN_SPARSE_STOCK_L2_REPORTING_INSTALLED',source_sha256=sha(__file__),current_requests=current,
  future_remaining24_consumer_hooked=True,model_restarts=0,new_dispatchers=0,registry_or_approval_or_plan_or_source_file_writes=0,
  missing_counters='NULL_UNKNOWN_NEVER_ZERO',all_nonreporting_lifecycle_checks='UNCHANGED')
