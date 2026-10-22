"""Pure old212 native-selected declarations, never a fullGPU fixed-stream PASS.
The fixed old decoder cannot describe registered2/selected0; use its unchanged
source equations on actual selected declarations, without rewriting any record.
Real native process/binary/terminal/command evidence remains external.
"""
import hashlib
from pathlib import Path
from decoder import FIXED_R4_SHA256,Feed
from math_audit import require,uint

def validate_selected_old212(feed,fixed_module,schema):
 require(isinstance(feed,Feed) and feed.native_global and not feed.full,'explicit native-selected policy required')
 require(feed.error is None and feed.last is not None and feed.pending is None,'r5 snapshot not complete')
 path=Path(fixed_module.__file__);require(hashlib.sha256(path.read_bytes()).hexdigest()==FIXED_R4_SHA256,'native equations exact fixed647 source')
 fields=schema['counter_fields'];require(isinstance(fields,list) and len(fields)==212 and len(set(fields))==212,'exact old212 compatibility schema')
 p=feed.last;g=p['global'];cycle=g['cycle'];old={}
 for key,new in feed.scopes(p).items():
  lookup=(key[0],key[1],key[2],cycle);require(lookup in feed.old,'native old scope absent');r=feed.old[lookup];c=r['counters'];require(set(c)==set(fields),'native old field set')
  for k,v in c.items():uint(v,'native old '+k)
  for k in ('T','M','ro_runtime','epoch_closed','closure_ok','overflow_invalid','output_invalid'):require(type(r[k]) is bool,'native old flags bool')
  require(not r['overflow_invalid'] and not r['output_invalid'],'native old invalid')
  if r['record']!='GLOBAL':require(r['closure_ok'] and r['epoch_closed'],'native selected old closure')
  fixed_module.partitions(c);fixed_module.r3_partitions(c,r['M'])
  require(r['live_detached']==c['detach_success']-c['detached_retired']==0,'native old live residual')
  if r['record']=='SLICE' and r['ro_runtime']:
   summary=feed.old_summaries.get((r['slice'],cycle));require(isinstance(summary,dict),'native old actual SUMMARY absent')
   for oldkey,newkey in [('detached','detach_success'),('transactions','ro_admits'),('merges','ro_merges'),('responses','ro_responses')]:
    value=summary.get(oldkey);require(isinstance(value,str) and value.isdigit(),'native SUMMARY integer '+oldkey);require(int(value)==c[newkey],'native legacy independent '+oldkey)
  old[key]=r
 for sid in feed.expected:
  parent=old[('SLICE',sid,-1)]
  for k in fields:require(sum(old[('PHASE',sid,pid)]['counters'][k] for pid in range(len(g['kernel_catalog'])+2))==parent['counters'][k],'native old phase rollup '+k)
 for k in fields:require(sum(old[('SLICE',sid,-1)]['counters'][k] for sid in feed.expected)==old[('GLOBAL',feed.registered,-1)]['counters'][k],'native old unprinted residual nonzero '+k)
 return {'status':'VALID_R4_SELECTED_NATIVE_DECLARATIONS_ONLY','fixed_equation_source_sha256':FIXED_R4_SHA256,'schema_counter_fields':fields,'final_cycle':cycle,'global_counters':old[('GLOBAL',feed.registered,-1)]['counters'],'slice_counters':{str(sid):old[('SLICE',sid,-1)]['counters'] for sid in feed.expected},'selected_slices':feed.expected,'registered_cache_count':feed.registered,'unprinted_cache_count':feed.registered-len(feed.expected),'unprinted_slice_records_synthesized':False,'global_epoch_closed':old[('GLOBAL',feed.registered,-1)]['epoch_closed'],'full_application_qualified':False,'scientific_acceptance_granted':False,'scope':'REAL_SELECTED_SLICE_PHASE_AND_SAMEFIELD_GLOBAL_RESIDUAL_ONLY_NOT_GLOBAL_NATIVE_TERMINAL'}
