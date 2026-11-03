"""Bounded sidecar observation in an EXISTING POST parse traversal; never reads payload files itself."""
import hashlib,json,os
from pathlib import Path
class FeatureTap:
 def __init__(self,max_features=4096):self.max_features=max_features;self.features={};self.records=0;self.active=0;self.inactive=0;self.active_unknown=0
 def observe(self,record,kernel,cta,warp,header):
  r=record;mask=r['mask'];self.records+=1
  if not mask:self.inactive+=1;return record
  self.active+=1;self.active_unknown+=bool(r.get('qualified',1)!=1 or r.get('kind',0)==255);op=r.get('opcode',r.get('op'));src=r.get('src',[]);dst=r.get('dst',[]);bank=r.get('bank',-1);width=r.get('width',0);cw=r.get('cw',0);kind=r.get('kind',0)
  features={'opcode:'+op,'format:'+str(header['tracer_version'])+':'+header.get('profile',''),'RF_count:'+str(len(src))+':'+str(len(dst)),'memory_width:'+str(width),'predicate_class:'+('mixed'if mask!=r['active']else'active'),'CFI_kind:'+str(kind)}
  if bank>=0:features.add('CBANK:'+str(bank)+':'+str(cw)+':'+('lane_indexed'if len(set(r.get('constant_offsets',{}).values()))>1 else'lane_uniform'))
  if kind in(1,2):features.add('CFI_pair:'+str(r.get('pair')));features.add('CFI_target_width:64')
  for k in features:
   if k not in self.features:
    assert len(self.features)<self.max_features,'FEATURE_INDEX_BOUND_EXCEEDED'
    self.features[k]=dict(kernel=kernel,cta=list(cta),warp=warp,PC=hex(r['pc']),observed_active=True)
  return record
 def finish(self,post_ref,index_ref,grouped_refs,kernel_headers,required_sidecars=None):
  closed_groups=[]
  for original in grouped_refs:
   ref=dict(original)
   p=Path(ref['path']);z=p.stat();ref['stat_signature']=dict(bytes=z.st_size,mtime_ns=z.st_mtime_ns,ctime_ns=z.st_ctime_ns)
   assert ref['POST_whole_SHA_closed']is True
   closed_groups.append(ref)
  return dict(schema='ACTUAL_POST_ACTIVE_FEATURE_WITNESS_INDEX_V1',source='same existing validated POST record traversal; no extra payload scan',records_observed=self.records,active_unknown_records=self.active_unknown,active_records=self.active,inactive_records=self.inactive,features=self.features,POST_ref=post_ref,index_ref=index_ref,grouped_refs=closed_groups,kernel_headers=kernel_headers,required_sidecars=required_sidecars or [],consumer_admission_granted=False,whole_input_functional_qualified=False,science_numeric_performance=False)
def write_new(path,index):
 with open(path,'x')as f:json.dump(index,f,sort_keys=True,indent=2);f.write('\n')
