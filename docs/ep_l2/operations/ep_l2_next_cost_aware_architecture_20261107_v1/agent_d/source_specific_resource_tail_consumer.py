"""Read-only Source-specific cost/tail shell candidate, never application acceptance."""
import json,hashlib,re,argparse
from pathlib import Path
BODY='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817'
SUFFIX='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432'
# SUFFIX is checked against the declared immutable contract; no raw/math execution here.
def need(v,m):
 if not v:raise ValueError(m)
def uint(v,m):need(type(v)is int and v>=0,m)
def unique64(rows):
 need(type(rows)is list and len(rows)==64 and all(type(r.get('slice'))is int for r in rows)and {r.get('slice')for r in rows}==set(range(64)),'exact64 unique slice population')
 return {r['slice']:r for r in rows}
def check_legacy_and_new_cost(rows,c):
 by=unique64(rows)
 for sid,r in by.items():
  need(set(r)==set(c['expected_cost_field_names']),'missing/unexpected cost record fields')
  for k,v in c['invariant_cost_fields'].items():need(type(r.get(k))is type(v) and r.get(k)==v,'fixed historical cost changed '+k)
  need(r['metadata_PPA']=='UNKNOWN'and r['metadata_clock_closure']=='UNKNOWN','unproved physical PPA/clock claim')
  # Read-view count is not a physical update-lane count.
  need(r['logical_control_read_views']==3,'original logical read views changed')
  policy=c['legacy_update_contract']
  if policy=='PRESERVED_PLUS_ADDITIVE':
   need(r['legacy_indexed_control_update_lanes']==3,'old3 update lanes were not preserved')
   for k,v in c['new_additive_cost_fields'].items():need(type(r.get(k))is type(v) and r.get(k)==v,'new additive cost mismatch '+k)
  elif policy=='REPLACED_BY_SHARED_TOKEN_EXECUTION':
   need(r.get('update_execution')=='SHARED_TOKEN_GATED','replacement execution mode')
   need('legacy_indexed_control_update_lanes'not in r,'replacement cannot print fictitious old3 execution qualification')
   for k,v in c['replacement_cost_fields'].items():need(type(r.get(k))is type(v) and r.get(k)==v,'replacement cost mismatch '+k)
  else:raise ValueError('unreviewed legacy/update relation')
  for k in c.get('paid_nonnegative_counter_fields',[]):uint(r.get(k),'invalid paid counter '+k)
 return True
def check_inventory(rows,c,native_cycles):
 for sid,r in unique64(rows).items():
  for k in['observed_app_cycles','physical_slots','bank_count','bank_ops_per_physical_cycle','wad_capacity','line_mshr_capacity','descriptor_capacity','descriptor_free','mandatory_live','wb_live','bank_pending','row_tokens_live','metadata_updates_pending','packet_credits_outstanding','extension_dirty_live']:uint(r.get(k),'invalid inventory '+k)
  need(r['observed_app_cycles']==native_cycles,'final scoped/app cycles mismatch')
  need(r['physical_slots']==1168 and r['bank_count']==4 and r['bank_ops_per_physical_cycle']==1,'fixed payload/bank/P1 changed')
  need(r['wad_capacity']==128 and r['line_mshr_capacity']==128 and r['descriptor_capacity']==512,'mandatory/shared capacity changed')
  need(r['descriptor_free']==512 and r['mandatory_live']==r['wb_live']==r['bank_pending']==r['row_tokens_live']==r['metadata_updates_pending']==r['packet_credits_outstanding']==0,'terminal responsibility not drained')
  roles=[r[k]for k in['role_free','role_resident','role_bypass','role_wb','role_tvd']]
  for v in roles:uint(v,'negative role')
  need(sum(roles)==1168 and r['role_wb']==0,'shared data conservation/free extra array')
  uint(r['base_tvd_live'],'base TVD');uint(r['extension_tvd_live'],'extension TVD')
  need(r['base_tvd_live']<=128 and r['extension_tvd_live']<=c['extension_rows'],'segment row capacity exceeded')
  need(r['base_tvd_live']+r['extension_tvd_live']==r['role_tvd'],'per-segment/TVD data owner mismatch')
  if c.get('extension_clean_only'):need(r['extension_dirty_live']==0,'CLEAN-only extension has dirty state')
 return True
def check_tail(t,inventory,c,expected_kernel_count):
 need(t['cycle_domain']=='GPU_CUMULATIVE','cleanup/app mixed clock domains')
 for k in['last_kernel_cycles','cleanup_requested_at','app_after_cleanup_cycles','native_final_cycles']:uint(t[k],'invalid tail cycle '+k)
 uint(t['kernel_count'],'kernel population type');need(expected_kernel_count>0 and t['native_final_cycles']>0,'nonempty complete application required')
 need(t['kernel_count']==expected_kernel_count and t['cleanup_is_kernel']is False,'tail invented/dropped a kernel')
 need(t['last_kernel_cycles']<=t['cleanup_requested_at']<=t['app_after_cleanup_cycles']==t['native_final_cycles'],'tail ordering or subtracted cleanup cycles')
 need(t['cleanup_cycles_included_in_app']is True,'app tail cost omitted')
 for sid,r in unique64(inventory).items():
  uint(r['cleanup_done_at'],'cleanup done cycle')
  need(t['cleanup_requested_at']<=r['cleanup_done_at']<=t['app_after_cleanup_cycles'],'per-slice cleanup timing')
 if c.get('timed_cleanup_required'):
  need(t['cleanup_producer_marker']==c['cleanup_producer_marker'],'unreviewed timed cleanup marker')
 return True
def validate(envelope,contract,spec):
 need(contract['status']=='SOURCE_SPECIFIC_ENGINEERING_CONTRACT_FROZEN'and contract.get('source_identity')is not None,'unqualified consumer template')
 source=spec['source_identity'];need(type(source)is dict,'Source5 shape')
 for k in['core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256','archive_sha256']:need(type(source.get(k))is str and re.fullmatch('[0-9a-f]{'+str(64 if k.endswith('sha256')else 40)+'}',source[k]),'Source5 field '+k)
 need(envelope['source_identity']==contract['source_identity']==source,'new Source/ELF/Framework mismatch')
 need(envelope['input_identity_sha256']==spec['input_identity_sha256']and envelope['ordered_commands_canonical_sha256']==spec['ordered_commands_canonical_sha256'],'input/commandlist mismatch')
 opts=spec['expected_effective_options'];need(len(opts)==contract['actual_option_count'],'actual option population differs')
 need(envelope['fullconfig_sha256']==hashlib.sha256(json.dumps(opts,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'fullconfig identity mismatch')
 need(contract['original_math_body_sha256']==BODY,'numeric math body must remain pinned')
 need(contract['original_math_final_suffix_sha256']==SUFFIX,'original suffix required')
 check_legacy_and_new_cost(envelope['metadata_cost_rows'],contract)
 check_tail(envelope['application_tail'],envelope['final_inventory_rows'],contract,len(spec['expected_kernel_launches']))
 check_inventory(envelope['final_inventory_rows'],contract,envelope['application_tail']['native_final_cycles'])
 return dict(status='SOURCE_SPECIFIC_RESOURCE_TAIL_SHELL_PASS_NOT_APPLICATION_ACCEPTANCE',original_math_and_population_validation_still_required=True,body_sha256=BODY,scientific_acceptance=False,new_model_authority=False)
def read_pinned(p,h):
 data=Path(p).read_bytes();need(len(data)<=32*(1<<20)and hashlib.sha256(data).hexdigest()==h,'input size/SHA')
 def pairs(xs):
  q={}
  for k,v in xs:need(k not in q,'duplicate key');q[k]=v
  return q
 return json.loads(data,object_pairs_hook=pairs,parse_constant=lambda x:need(False,'nonfinite JSON'))
def main():
 ap=argparse.ArgumentParser()
 for n in ['contract','envelope','spec']:ap.add_argument('--'+n,required=True);ap.add_argument('--'+n+'-sha',required=True)
 a=ap.parse_args();print(json.dumps(validate(read_pinned(a.envelope,a.envelope_sha),read_pinned(a.contract,a.contract_sha),read_pinned(a.spec,a.spec_sha)),sort_keys=True))
if __name__=='__main__':main()
