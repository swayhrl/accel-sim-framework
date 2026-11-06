"""UMT1 Main closed-result counters. No model, authority or source mutation."""
from pathlib import Path
import json,gzip,hashlib
PFX={
 'EPL2ROP5|ADMISSION|':{'sum':['activations','native_before_activation'],'max':[]},
 'EPL2ROV1|SUMMARY|':{'sum':['accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','detached','lower_sectors','concurrent_duplicate_sectors','responses','ro_bank_fill_ops','ro_bank_response_ops'],'max':['live']},
 'EPL2ROC1|RESOURCE|':{'sum':['normal_line_allocations','avoided_line_allocations','lower_read_bytes','concurrent_duplicate_read_bytes','query_count','query_wait_cycles','query_port_wait_attempts'],'max':['peak_transactions','peak_shared_descriptors','peak_shared_lines']},
 'EPL2B0V1|scope=application|interval=application_cumulative|':{'sum':['c7d_line_mshr_full_block','c7d_tag_set_all_reserved_block','c7d_descriptor_pool_full_block','c7d_per_address_cap_block','c7d_wad_full_events','c7d_wad_hazard_events','bank_wait_cycles','c7d_dram_scheduler_full_block'],'max':['line_mshr_max','descriptor_max','wad_max','c7d_reserved_set_max']},
 'EPL2TVDV2|SUMMARY|':{'sum':['read_responses','dirty_forward_responses','directory_queries','lookup_wait_cycles','bank_wait_cycles','wb_wait_cycles','icnt_wait_cycles'],'max':[]},
}
WAIT='EPL2ROC1|WAIT|'
REASONS=('TAG_SET_ALL_PENDING','LINE_MSHR_FULL','SHARED_DESCRIPTOR_FULL','PER_ADDRESS_FULL')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def parse(lines):
 groups={p:{}for p in PFX};wait={r:{}for r in REASONS};counts={p:0 for p in PFX};counts[WAIT]=0
 for line in lines:
  prefix=next((p for p in PFX if line.startswith(p)),None)
  if prefix is None and not line.startswith(WAIT):continue
  d={}
  for field in line.rstrip('\n').split('|')[1:]:
   if '=' in field:
    k,v=field.split('=',1);assert k not in d,'duplicate counter key';d[k]=v
  assert d.get('slice','').isdigit()
  sid=int(d['slice']);assert 0<=sid<64
  if prefix is None:
   reason=d['reason'];assert reason in wait;wait[reason][sid]=d;counts[WAIT]+=1
  else:groups[prefix][sid]=d;counts[prefix]+=1
 out={}
 for p,by in groups.items():
  if not by:
   out[p]={'status':'NOT_EMITTED_UNKNOWN','totals':None,'max_over_slices':None};continue
  assert set(by)==set(range(64)) and counts[p]%64==0,'missing final slice or incomplete emitted round '+p
  fields=PFX[p];tot={};mx={}
  for k in fields['sum']:
   assert all(by[i].get(k,'').isdigit() for i in by),'missing integer '+k
   tot[k]=sum(int(by[i][k])for i in by)
  for k in fields['max']:
   assert all(by[i].get(k,'').isdigit()for i in by)
   mx[k]=max(int(by[i][k])for i in by)
  out[p]={'status':'FINAL_CUMULATIVE64_SLICE_RECORDS','totals':tot,'max_over_slices':mx,'last_per_slice':{str(k):v for k,v in sorted(by.items())},'emitted_records':counts[p]}
 wout={}
 assert counts[WAIT]%(64*len(REASONS))==0,'incomplete WAIT emitted round'
 for reason,by in wait.items():
  if not by:wout[reason]={'status':'NOT_EMITTED_UNKNOWN'};continue
  assert set(by)==set(range(64)),'missing WAIT slices'
  wout[reason]={'status':'FINAL_CUMULATIVE64_NONEXCLUSIVE_HEAD_WAITS','unique_head_requests_sum':sum(int(v['unique_head_requests'])for v in by.values()),'first_to_accept_cycles_sum':sum(int(v['first_to_accept_cycles'])for v in by.values()),'pending_head_sum':sum(int(v['pending_head'])for v in by.values()),'last_per_slice':{str(k):v for k,v in sorted(by.items())}}
 act=out['EPL2ROP5|ADMISSION|']
 if act['status'].startswith('FINAL'):
  by=act['last_per_slice'];policies={int(v['policy_pressure_epoch'])for v in by.values()};assert len(policies)==1
  policy=next(iter(policies))
  ids=[int(i)for i,v in by.items()if int(v['active'])==1]
  assert all(int(v['activations'])in [0,1]for v in by.values())
  assert act['totals']['activations']==len(ids)
  classification='POLICY_DISABLED'if not policy else('ACTIVATED_ON_EXACT_CANDIDATE_PRESSURE_GATE'if ids else'NO_ACTIVATION')
  activation={'status':classification,'policy':policy,'activations':act['totals']['activations'],'active_slice_ids':sorted(ids),'active_slice_count':len(ids),'applicable_RO_runtime_slices':64,'native_before_activation':act['totals']['native_before_activation'],'joint_event_population':'Exact first activation implies the reviewed joint predicates at that event; total joint-event incidence and denominator not exported.'}
 else:activation={'status':'UNKNOWN_NOT_EMITTED'}
 b0=out['EPL2B0V1|scope=application|interval=application_cumulative|']
 pressure={'status':'UNKNOWN'}
 if b0['status'].startswith('FINAL'):
  ids=[int(i)for i,v in b0['last_per_slice'].items()if int(v['line_mshr_max'])>=128]
  pressure={'status':'MEASURED_SEPARATE_FROM_RO_TRIGGER','line_capacity':128,'slices_peak_reached_capacity':sorted(ids),'max_normal_line_over_slices':b0['max_over_slices']['line_mshr_max'],'normal_line_full_block_events_sum':b0['totals']['c7d_line_mshr_full_block'],'tag_all_reserved_block_events_sum':b0['totals']['c7d_tag_set_all_reserved_block'],'no_marginal_peak_proves_joint_RO_candidate_event':True}
 return {'groups':out,'RO_head_waits':wout,'activation':activation,'normal_line_pressure':pressure,'semantics':['Only final cumulative per-slice snapshots selected, never summed across kernel snapshots','Waiting sums are overlapping observations, never critical-path cycles','Lower read bytes are issued/admitted traffic, not completed DRAM bandwidth','No ratios across head/ingress/admission/independent UID populations']}
def collect(cohort,spec,row,control):
 assert row['state']=='CLOSED_ACCEPTED'
 cache=Path(control)/'CLOSED_COUNTERS';cache.mkdir(exist_ok=True);target=cache/(cohort+'.json')
 done=read(row['done_ref']['path']);raw=done['raw_compressed_ref'];accepted=read(row['accepted_point_ref']['path'])
 if target.exists():
  d=read(target);assert d['raw_compressed_ref']==raw and d['spec_sha256']==accepted['spec_ref']['sha256'] and d['cohort']==cohort and d['uuid']==row['uuid'] and d['source_identity']==spec['source_identity'];return d
 assert sha(raw['path'])==raw['sha256']
 with gzip.open(raw['path'],'rt',encoding='utf-8',errors='strict')as f:out=parse(f)
 a=read(row['accepted_point_ref']['path'])
 out.update(schema='EP_MAIN_UMT1_ACCEPTED_COUNTER_SUMMARY_V1',cohort=cohort,uuid=row['uuid'],source_identity=spec['source_identity'],input_identity_sha256=spec['input_identity_sha256'],spec_sha256=a['spec_ref']['sha256'],accepted_point_ref=row['accepted_point_ref'],raw_compressed_ref=raw,scientific_actor=False)
 target.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 return out
