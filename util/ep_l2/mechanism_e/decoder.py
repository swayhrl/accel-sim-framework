#!/usr/bin/env python3
"""Fixed-source observer framing/terminal declaration checker. No app acceptance."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import re

PREFIX=b'EPL2DETACH_DIAG_V1|'
OLD=b'EPL2ROV1|SUMMARY|'
U64=(1<<64)-1
BASE_SOURCE_COMMIT='cf7347151f86a17866b91af6d3f2da726ea8d062'
BASE_FIELDS_SHA256='d04d92058d2b952824a18a2ef347769ecc6d97c92727bba5938f3a4f918d4d96'
COMMON={'record','slice','cycle','phase','kernel_scope','kernel_uid','candidate_owner_kernel',
 'trigger_later_linkage','overflow_invalid','output_invalid','closure_ok','epoch_closed',
 'T','M','ro_runtime','live_detached','counters'}
SAMPLE={'record','slice','cycle','request_uid','set','eligible','first_eligible_way',
 'victim_payload','victim_generation','required','issued','ready','reuse_seen','attached',
 'requester_ro_candidate','immediate_commit_result','candidate_owner_kernel'}
RAW=['raw_hit','raw_hit_reserved','raw_miss','raw_reservation_fail','raw_sector_miss','raw_mshr_hit','raw_write_allocated','raw_unknown']
WAY=['way_no_live_ro','way_not_attached','way_reuse_seen','way_no_missing','way_eligible']
PRIMARY=['primary_owner','primary_directory','primary_query','primary_wad','primary_descriptor','primary_address','primary_line','primary_missq','primary_data','primary_response','primary_unknown','primary_none']
REQUIRED=set(RAW+WAY+PRIMARY+['observed_heads','probe_skipped','pressure_T_disabled','pressure_T_enabled',
 'pressure_no_live_ro','pressure_live_ro_no_eligible','pressure_eligible','ways_examined',
 'pressure_prod_probe_reached','pressure_prod_probe_not_reached','pressure_rewrite_miss',
 'pressure_rewrite_hit_reserved','pressure_kept_fail','pressure_relief_not_consulted','pressure_intermediate_other',
 'relieve_calls','relieve_T_disabled','relieve_no_eligible','relieve_eligible_selected',
 'detach_calls','detach_success','detach_false','detach_exception','ft_access_attempts',
 'commit_accepted','commit_denied','commit_exception','detached_retired','ro_admits','ro_merges',
 'ro_fill_packets','closure_errors','selected_identity_mismatch','samples_seen','samples_stored','samples_dropped']+
 [f'eligible_hist_{i}' for i in range(17)]+[f'predicate_hist_{i}' for i in range(8)]+[f'transition_joint_{i}' for i in range(8)])

class Invalid(ValueError):pass
class Incomplete(ValueError):pass

def require(ok,message):
 if not ok:raise Invalid(message)

def uint(value,context):
 require(type(value) is int and 0<=value<=U64,'invalid uint64/bool '+context)
 return value

def unique(pairs):
 d={}
 for k,v in pairs:
  require(k not in d,'duplicate JSON key '+k);d[k]=v
 return d


def partitions(c):
 """Actual fixed-source ledger equations, using Python nonwrapping integers."""
 checks={
 'SOURCE_FE':(c['observed_heads'],c['probe_skipped']+sum(c[k] for k in RAW)),
 'SOURCE_T_SCOPE':(c['raw_reservation_fail'],c['pressure_T_disabled']+c['pressure_T_enabled']),
 'SOURCE_ELIGIBILITY':(c['pressure_T_enabled'],c['pressure_no_live_ro']+c['pressure_live_ro_no_eligible']+c['pressure_eligible']),
 'SOURCE_WAY_SCAN':(c['ways_examined'],sum(c[k] for k in WAY)),
 'SOURCE_PROBE_REACH':(c['raw_reservation_fail'],c['pressure_prod_probe_reached']+c['pressure_prod_probe_not_reached']),
 'SOURCE_INTERMEDIATE':(c['pressure_prod_probe_reached'],sum(c[k] for k in ['pressure_rewrite_miss','pressure_rewrite_hit_reserved','pressure_kept_fail','pressure_relief_not_consulted','pressure_intermediate_other'])),
 'SOURCE_RELIEVE':(c['relieve_calls'],c['relieve_T_disabled']+c['relieve_no_eligible']+c['relieve_eligible_selected']),
 'SOURCE_DETACH':(c['detach_calls'],c['detach_success']+c['detach_false']+c['detach_exception']),
 'SOURCE_COMMIT':(c['ft_access_attempts'],c['commit_accepted']+c['commit_denied']+c['commit_exception']),
 'SOURCE_ELIGIBLE_HIST':(sum(c[f'eligible_hist_{i}'] for i in range(17)),c['pressure_T_enabled']),
 'SOURCE_PREDICATE_HIST':(sum(c[f'predicate_hist_{i}'] for i in range(8)),c['ways_examined']-c['way_no_live_ro']),
 'SOURCE_TRANSITION_HIST':(sum(c[f'transition_joint_{i}'] for i in range(8)),c['ro_admits']+c['ro_merges']+c['ro_fill_packets']),
 'SOURCE_PRIMARY':(sum(c[k] for k in PRIMARY),c['observed_heads']-c['probe_skipped']),
 }
 for name,(a,b) in checks.items():require(a==b,name+' does not close')
 require(c['detach_success']>=c['detached_retired'],'SOURCE_DETACHED_LIVE negative')
 for k in ['closure_errors','selected_identity_mismatch','commit_exception','detach_exception']:
  require(c[k]==0,'SOURCE_INVALID '+k)
 # Source's15th family is per-field disjoint PHASE sum; checked in snapshot().
 return len(checks)+1



R3_SOURCE_COMMIT='7cee27fde762406ecffef711a8f6c4c38761692c'
R3_FIELDS_SHA256='189c6810fd045ece48c04125f788aa60ba948081c94c8da0fea4cf660d023dff'
R3_SOURCE_DIFF_SHA256='423641553e557f8e3522f2698c4f5128e7f8caad4af83fb05e0d588400a0f4cc'
R4_SOURCE_COMMIT='9243f769620653f2a9d4df5599e9581e9dae6067'
R4_SOURCE_DIFF_SHA256='5161fd0d46e7ab911fde18e5c86ac1aa337c59ee648819ab6612039a376095d6'
R4_LINEAGE_PROOF_SHA256='c268aada4b3880146bae47c1eff28e97a1ace77e9e178a3cc7bb86e41a0ec8f4'
R3_NEW_FIELDS=['ro_capacity_population', 'ro_capacity_consulted', 'ro_capacity_not_consulted', 'ro_line_na_M_or_existing', 'ro_descriptor_checked', 'ro_descriptor_pass', 'ro_descriptor_fail', 'ro_descriptor_unobserved', 'ro_address_checked', 'ro_address_pass', 'ro_address_fail', 'ro_address_unobserved', 'ro_line_probe_checked', 'ro_line_probe_pass', 'ro_line_probe_fail', 'ro_line_probe_unobserved', 'ro_line_slots_checked', 'ro_line_slots_pass', 'ro_line_slots_fail', 'ro_line_slots_unobserved', 'eligible_frontend_admitted', 'eligible_frontend_denied', 'eligible_prod_probe_reached', 'eligible_prod_probe_not_reached', 'eligible_rewrite_miss', 'eligible_rewrite_hit_reserved', 'eligible_kept_fail', 'eligible_relief_not_consulted', 'eligible_intermediate_other', 'eligible_capacity_consulted', 'eligible_capacity_not_consulted', 'eligible_descriptor_fail', 'eligible_address_fail', 'eligible_line_probe_fail', 'eligible_line_slots_fail', 'eligible_early_owner', 'eligible_early_directory', 'eligible_early_query', 'eligible_early_wad', 'eligible_early_tvd']

def r3_partitions(c, static_M):
 """Exact r3 same-observation tri-state/joint equations; no domain mixing."""
 eq={
 'SOURCE_R3_CAPACITY_POPULATION':(c['ro_capacity_population'],c['ro_capacity_consulted']+c['ro_capacity_not_consulted']),
 'SCHEMA_R3_CANDIDATE_POPULATION':(c['ro_capacity_population'],c['requester_ro_candidate']),
 'SOURCE_R3_ELIGIBLE_ADMISSION':(c['pressure_eligible'],c['eligible_frontend_admitted']+c['eligible_frontend_denied']),
 'SOURCE_R3_ELIGIBLE_REACH':(c['pressure_eligible'],c['eligible_prod_probe_reached']+c['eligible_prod_probe_not_reached']),
 'SOURCE_R3_ELIGIBLE_INTERMEDIATE':(c['eligible_prod_probe_reached'],sum(c[k] for k in ('eligible_rewrite_miss','eligible_rewrite_hit_reserved','eligible_kept_fail','eligible_relief_not_consulted','eligible_intermediate_other'))),
 'SOURCE_R3_ELIGIBLE_CAPACITY':(c['pressure_eligible'],c['eligible_capacity_consulted']+c['eligible_capacity_not_consulted']),
 }
 for name in ('descriptor','address','line_probe','line_slots'):
  eq['SOURCE_R3_'+name+'_CHECKED']=(c['ro_'+name+'_checked'],c['ro_'+name+'_pass']+c['ro_'+name+'_fail'])
  eq['SOURCE_R3_'+name+'_COVERAGE']=(c['ro_capacity_population'],c['ro_'+name+'_checked']+c['ro_'+name+'_unobserved'])
 for name,(a,b) in eq.items():require(a==b,name+' does not close')
 # Explicit source-derived first-invocation short-circuit constraints.
 derived={
 'DESCRIPTOR_EVAL':(c['ro_descriptor_checked'],c['ro_capacity_consulted']),
 'ADDRESS_AFTER_DESCRIPTOR_PASS':(c['ro_address_checked'],c['ro_descriptor_pass']),
 'LINE_AFTER_ADDRESS_OR_NA':(c['ro_address_pass'],c['ro_line_na_M_or_existing']+c['ro_line_probe_checked']),
 'SLOTS_AFTER_LINE_PROBE_PASS':(c['ro_line_slots_checked'],c['ro_line_probe_pass']),
 'EXCLUSIVE_CAPACITY_OUTCOMES':(c['ro_capacity_consulted'],sum(c[k] for k in ('ro_descriptor_fail','ro_address_fail','ro_line_probe_fail','ro_line_slots_fail','ro_line_na_M_or_existing','ro_line_slots_pass'))),
 }
 for name,(a,b) in derived.items():require(a==b,'DERIVED_R3_'+name+' does not close')
 if static_M:
  require(c['ro_line_probe_checked']==c['ro_line_slots_checked']==0,'DERIVED_R3 M1 cannot consult traditional line predicates')
  require(c['ro_line_na_M_or_existing']==c['ro_address_pass'],'DERIVED_R3 M1 line NA only after shared predicates pass')
 pairs=[('eligible_frontend_admitted','pressure_frontend_admitted'),('eligible_frontend_denied','pressure_frontend_denied'),
  ('eligible_prod_probe_reached','pressure_prod_probe_reached'),('eligible_prod_probe_not_reached','pressure_prod_probe_not_reached'),
  ('eligible_rewrite_miss','pressure_rewrite_miss'),('eligible_rewrite_hit_reserved','pressure_rewrite_hit_reserved'),
  ('eligible_kept_fail','pressure_kept_fail'),('eligible_relief_not_consulted','pressure_relief_not_consulted'),
  ('eligible_intermediate_other','pressure_intermediate_other'),('eligible_capacity_consulted','ro_capacity_consulted')]
 for a,b in pairs:require(c[a]<=c[b],'DERIVED_R3 joint exceeds matching observed marginal '+a)
 for name in ('descriptor','address','line_probe','line_slots'):
  require(c['eligible_'+name+'_fail']<=c['ro_'+name+'_fail'],'DERIVED_R3 eligible failure exceeds actual predicate failure '+name)
 require(sum(c['eligible_'+n+'_fail'] for n in ('descriptor','address','line_probe','line_slots'))<=c['eligible_capacity_consulted'],'DERIVED_R3 mutually exclusive eligible first failures exceed consulted')
 require(sum(c['eligible_early_'+n] for n in ('owner','directory','query','wad','tvd'))<=c['eligible_capacity_not_consulted'],'DERIVED_R3 early-return joint requires capacity not consulted')
 return {'source_r3_families':13,'schema_r3_families':1,'derived_rules':'Explicitly source-derived short-circuit/conditional-subset constraints, not invented native counters.'}

class Decoder:
 def __init__(self,schema,*,expected_slice_count=64,require_closed=True,
  expected_T=True,expected_M=True,expected_runtime=True,max_line_bytes=262144,
  max_observer_bytes=67108864,max_input_bytes=402653184,data_kind='REAL_UNACCEPTED'):
  fields=schema.get('counter_fields')
  require(isinstance(fields,list) and fields and all(isinstance(k,str) and k for k in fields),'schema counter_fields absent')
  require(len(fields)==len(set(fields)),'schema duplicate counter fields')
  fields_sha=hashlib.sha256(json.dumps(fields,separators=(',',':')).encode()).hexdigest()
  if fields_sha!=BASE_FIELDS_SHA256:
   revision=schema.get('reviewed_field_set_revision',{})
   require(revision.get('base_source_commit')==BASE_SOURCE_COMMIT and revision.get('E_reviewed') is True and
    isinstance(revision.get('new_source_commit'),str) and re.fullmatch('[0-9a-f]{40}',revision['new_source_commit']) and
    isinstance(revision.get('source_diff_sha256'),str) and re.fullmatch('[0-9a-f]{64}',revision['source_diff_sha256']) and
    revision.get('new_counter_fields_sha256')==fields_sha,
    'changed field schema requires explicit E reviewed source-diff/revision binding; no old-schema zero fill')
  require(REQUIRED<=set(fields),'schema lacks fixed-source equation inputs; explicit new revision adapter needed')
  require(type(expected_slice_count) is int and 1<=expected_slice_count<=64,'invalid expected slice count')
  require(type(require_closed) is bool and all(type(x) is bool for x in (expected_T,expected_M,expected_runtime)),'configuration bool flags must be explicit')
  self.is_r3=fields_sha==R3_FIELDS_SHA256
  if self.is_r3:
   revision=schema.get('reviewed_field_set_revision',{})
   source=schema.get('source_commit')
   if source==R3_SOURCE_COMMIT:
    require(revision.get('new_source_commit')==R3_SOURCE_COMMIT and revision.get('source_diff_sha256')==R3_SOURCE_DIFF_SHA256,
     'r3 actual212 fields require exact7cee source and reviewed cf-to-r3 diff binding')
   elif source==R4_SOURCE_COMMIT:
    lineage=schema.get('source_lineage_binding',{})
    require(revision.get('new_source_commit')==R4_SOURCE_COMMIT and revision.get('source_diff_sha256')==R4_SOURCE_DIFF_SHA256 and
     lineage=={'schema':'E2_TEST_ONLY_SUCCESSOR_INTERFACE_BINDING_V1','source_commit':R4_SOURCE_COMMIT,
      'predecessor_core_commit':R3_SOURCE_COMMIT,'proof_sha256':R4_LINEAGE_PROOF_SHA256,
      'production_source_bytes_identical':True,'native_Q_inherited':False},
     'r4 actual212 fields require exact9243 and independently proved test-only lineage, no inherited qualification')
   else:
    raise Invalid('actual212 fields source has no explicit independently reviewed lineage')
  self.fields=fields;self.fieldset=set(fields);self.schema=schema
  self.n=expected_slice_count;self.closed=require_closed;self.expected=(expected_T,expected_M,expected_runtime)
  self.max_line=max_line_bytes;self.max_output=max_observer_bytes;self.max_input=max_input_bytes
  self.kind=data_kind;self.total_bytes=0;self.observer_bytes=0;self.line_number=0;self.records=0
  self.cur=self.empty();self.last=None;self.rounds=0;self.samples={};self.identical_duplicates=0
  self.all_observer_sha=hashlib.sha256()
 @staticmethod
 def empty():return {'slices':{},'phases':{},'global':None,'old':{}}
 def counters(self,r):
  c=r.get('counters');require(isinstance(c,dict),'missing counters object')
  require(set(c)==self.fieldset,'counter field set differs from exact bound schema')
  for k,v in c.items():uint(v,'counter '+k)
 def common(self,r):
  require(set(r)==COMMON,'common metadata missing/extra fields')
  for k in ['slice','cycle','live_detached']:uint(r[k],k)
  require(type(r['phase']) is int,'phase bool/nonint')
  for k in ['overflow_invalid','output_invalid','closure_ok','epoch_closed','T','M','ro_runtime']:
   require(type(r[k]) is bool,'nonbool metadata '+k)
  require(not r['overflow_invalid'] and not r['output_invalid'],'overflow/output invalid')
  require(r['candidate_owner_kernel'] is None,'unbound candidate owner kernel must be null')
  require(r['trigger_later_linkage']=='NOT_MEASURED','unproven later trigger linkage')
  require((r['T'],r['M'],r['ro_runtime'])==self.expected,'unexpected finiteF T/M/runtime flags')
  if r['record']=='PHASE':
   p=r['phase'];require(0<=p<18,'phase outside bounded source range')
   require(r['kernel_scope']==('UNASSIGNED' if p==0 else 'OVERLAP_UNKNOWN' if p==1 else 'SINGLE_ACTIVE_INTERVAL'),'phase scope mapping differs from source')
   if p<2:require(r['kernel_uid'] is None,'residual phase kernel must be null')
   else:uint(r['kernel_uid'],'phase kernel UID')
  else:
   require(r['phase']==-1 and r['kernel_scope']=='SLICE_CUMULATIVE' and r['kernel_uid'] is None,'nonphase scope mismatch')
  self.counters(r)
 def monotonic(self,prior,current,context):
  for field in self.fields:
   require(current['counters'][field]>=prior['counters'][field],'cumulative counter regressed '+context+' '+field)
 def store(self,d,key,r):
  if key in d:
   require(d[key]==r,'conflicting duplicate record '+str(key));self.identical_duplicates+=1
  else:d[key]=r
 def old(self,line):
  pairs=line[len(OLD):].decode('ascii').strip().split('|');d={}
  for item in pairs:
   require('=' in item,'bad old RO SUMMARY token');k,v=item.split('=',1);require(k not in d,'duplicate old SUMMARY key');d[k]=v
  for k in ['slice','detached']:
   require(k in d and re.fullmatch(r'[0-9]+',d[k]) is not None,'missing old SUMMARY '+k);d[k]=uint(int(d[k]),'old '+k)
  require(d['slice']<self.n,'unexpected old RO slice')
  if self.last is not None:
   previous=self.last['old'].get(d['slice'])
   require(previous is not None and d['detached']>=previous['detached'],'old RO detached counter regressed across snapshots')
  if d['slice'] in self.cur['old']:
   require(self.cur['old'][d['slice']]==d,'conflicting old SUMMARY duplicate');self.identical_duplicates+=1
  else:self.cur['old'][d['slice']]=d
 def sample(self,r):
  require(set(r)==SAMPLE,'sample missing/extra metadata')
  for k in SAMPLE-{'record','reuse_seen','attached','requester_ro_candidate','immediate_commit_result','candidate_owner_kernel'}:uint(r[k],'sample '+k)
  require(r['slice']<self.n,'sample unknown slice')
  for k in ['reuse_seen','attached','requester_ro_candidate']:require(type(r[k]) is bool,'sample nonbool '+k)
  require(type(r['immediate_commit_result']) is int and -1<=r['immediate_commit_result']<=6,'invalid sample immediate result; -1 is legitimate UNKNOWN')
  require(r['candidate_owner_kernel'] is None,'sample owner attribution unmeasured')
  for k in ('required','issued','ready'):require(r[k]<=15,'sample sector mask exceeds four sectors '+k)
  if r['eligible']:
   require(r['victim_payload']<1168 and 0<r['victim_generation']<=2**32-1,'sample eligible victim payload/generation outside source finite landing')
   require(r['attached'] and not r['reuse_seen'] and (r['required']&~r['ready'])!=0,'sample eligible victim violates attached/no-reuse/missing predicate')
  else:
   require(r['victim_payload']==U64 and r['victim_generation']==0 and r['required']==r['issued']==r['ready']==0 and not r['attached'] and not r['reuse_seen'],'sample no-eligible victim must preserve source sentinel/default state')
  require(r['eligible']<=16 and r['set']<64,'sample eligible/set exceeds fixed geometry')
  require(r['first_eligible_way']==2**32-1 if r['eligible']==0 else r['set']*16<=r['first_eligible_way']<(r['set']+1)*16,'sample first way sentinel/range')
  key=(r['slice'],r['cycle'],r['request_uid'])
  if key in self.samples:
   require(self.samples[key]==r,'conflicting sample duplicate');self.identical_duplicates+=1
  else:
   require(len(self.samples)<64,'sample cap64 exceeded');self.samples[key]=r
 def ingest(self,line):
  if line.startswith((OLD,PREFIX)) and not line.endswith(b'\n'):raise Incomplete('truncated structured line without source newline')
  if line.startswith(OLD):self.old(line);return
  if not line.startswith(PREFIX):return
  self.observer_bytes+=len(line);require(self.observer_bytes<=self.max_output,'observer output cap exceeded')
  self.all_observer_sha.update(line);self.records+=1
  try:r=json.loads(line[len(PREFIX):],object_pairs_hook=unique)
  except (UnicodeError,json.JSONDecodeError,RecursionError) as e:raise Invalid('malformed observer JSON') from e
  require(isinstance(r,dict),'observer JSON not object');kind=r.get('record')
  if kind=='OUTPUT_INVALID':raise Invalid('producer OUTPUT_INVALID marker')
  if kind=='SAMPLE':self.sample(r);return
  require(kind in ('SLICE','PHASE','GLOBAL'),'unknown observer record type')
  self.common(r)
  if kind=='SLICE':
   if self.cur['global'] is not None:
    # Exact repeated same terminal record is a duplicate; a later cycle starts a new snapshot.
    old=self.cur['slices'].get(r['slice'])
    if old is not None and old['cycle']==r['cycle']:
     require(old==r,'conflicting same-cycle SLICE after GLOBAL');self.identical_duplicates+=1;return
    require(r['cycle']>self.cur['global']['cycle'],'snapshot physical clock did not advance')
    # Earlier complete snapshots may be in-progress epochs. Check their
    # framing/arithmetic without requiring final epoch closure before discard.
    self.snapshot(self.cur,terminal=False)
    self.last=self.cur;self.rounds+=1;self.cur=self.empty()
   require(r['slice']<self.n,'SLICE physical ID outside exact expected membership')
   if self.last is not None:self.monotonic(self.last['slices'][r['slice']],r,'SLICE '+str(r['slice']))
   self.store(self.cur['slices'],r['slice'],r)
  elif kind=='PHASE':
   require(r['slice']<self.n,'PHASE physical slice outside expected membership')
   if self.last is not None:
    previous=self.last['phases'].get((r['slice'],r['phase']))
    if previous is not None:
     require(r['kernel_uid']==previous['kernel_uid'],'existing phase kernel UID changed across snapshots')
     self.monotonic(previous,r,'PHASE '+str((r['slice'],r['phase'])))
   self.store(self.cur['phases'],(r['slice'],r['phase']),r)
  else:
   require(r['slice']==self.n,'GLOBAL.slice must be owner count, not a physical slice')
   if self.last is not None:self.monotonic(self.last['global'],r,'GLOBAL')
   if self.cur['global'] is not None:
    require(self.cur['global']==r,'conflicting duplicate GLOBAL');self.identical_duplicates+=1
   else:self.cur['global']=r
 def snapshot(self,s,*,terminal=True):
  if s['global'] is None:raise Incomplete('latest observer snapshot lacks GLOBAL; no fallback to older complete snapshot')
  if set(s['slices'])!=set(range(self.n)):raise Incomplete('latest snapshot lacks exact unique SLICE membership')
  if self.expected[2] and set(s['old'])!=set(range(self.n)):raise Incomplete('last old RO SUMMARY lacks exact slice membership')
  g=s['global']
  if self.last is not None:
   require(set(self.last['phases'])<=set(s['phases']),'existing phase bucket disappeared across snapshots')
  require(all(r['cycle']<=g['cycle'] for r in self.samples.values()),'sample physical cycle after final snapshot')
  cycles={r['cycle'] for r in s['slices'].values()};require(cycles=={g['cycle']},'mixed snapshot cycles')
  expected_phase_map=None;phase_checks=0
  for sid,r in s['slices'].items():
   require(r['closure_ok'],'source closure_ok false')
   partitions(r['counters'])
   if self.is_r3:r3_partitions(r['counters'],r['M'])
   if r['T']:require(r['counters']['pressure_T_disabled']==0 and r['counters']['relieve_T_disabled']==0,'counter T-disabled contradicts static T=true')
   else:require(r['counters']['pressure_T_enabled']==0 and r['counters']['detach_success']==0,'T-disabled counters contradict static config')
   if r['epoch_closed']:require(r['live_detached']==0,'epoch_closed cannot claim live detached population')
   require(r['live_detached']==r['counters']['detach_success']-r['counters']['detached_retired'],'slice live_detached metadata false')
   if self.closed and terminal:require(r['epoch_closed'] and r['live_detached']==0,'terminal epoch not closed or live detached nonzero')
   ps={p:v for (sl,p),v in s['phases'].items() if sl==sid}
   require(ps and set(ps)==set(range(max(ps)+1)) and max(ps)>=1,'phase buckets missing/noncontiguous; residual0/1 mandatory')
   pmap={p:v['kernel_uid'] for p,v in ps.items()};uids=[v for p,v in pmap.items() if p>=2];require(len(uids)==len(set(uids)),'duplicate kernel UID assigned to distinct phase buckets')
   if expected_phase_map is None:expected_phase_map=pmap
   else:require(pmap==expected_phase_map,'slice phase/kernel catalogs inconsistent')
   for p,v in ps.items():
    if self.is_r3:r3_partitions(v['counters'],v['M'])
    require(v['cycle']==r['cycle'],'phase snapshot clock differs from parent')
    for k in ['live_detached','epoch_closed','closure_ok','T','M','ro_runtime']:
     require(v[k]==r[k],'phase metadata must equal cumulative parent '+k)
   for f in self.fields:require(sum(v['counters'][f] for v in ps.values())==r['counters'][f],'SOURCE_PHASE_ROLLUP '+f)
   phase_checks+=1
   if self.expected[2]:require(r['counters']['detach_success']==s['old'][sid]['detached'],'new detached does not match old authoritative RO SUMMARY')
  for f in self.fields:require(sum(r['counters'][f] for r in s['slices'].values())==g['counters'][f],'GLOBAL_64SLICE_ROLLUP '+f)
  partitions(g['counters'])
  if self.is_r3:r3_partitions(g['counters'],g['M'])
  require(g['closure_ok'],'GLOBAL closure_ok false')
  require(g['live_detached']==g['counters']['detach_success']-g['counters']['detached_retired'],'global live_detached false')
  require(g['epoch_closed']==all(r['epoch_closed'] for r in s['slices'].values()),'global epoch_closed false')
  if self.closed and terminal:require(g['epoch_closed'] and g['live_detached']==0,'global terminal unclosed')
  for sid,r in s['slices'].items():
   c=r['counters'];require(c['samples_seen']==c['samples_stored']+c['samples_dropped'],'DERIVED sample accounting')
   require(c['samples_seen']==c['raw_reservation_fail'],'DERIVED samples_seen equals actual pressure-hook calls')
   actual=sum(x['slice']==sid for x in self.samples.values());require(actual==c['samples_stored'],'stored sample count differs from actual bounded rows')
  require(g['counters']['samples_stored']==len(self.samples)<=64,'global sample count/cap mismatch')
  return {'global_counters':copy.deepcopy(g['counters']),'slice_counters':{str(k):copy.deepcopy(r['counters']) for k,r in sorted(s['slices'].items())},
   'phase_catalog':expected_phase_map,'phase_semantics':'Disjoint physical active-kernel state buckets, not requester/owner causal kernel intervals. Overlap is an explicit residual bucket.',
   'metadata_scope':'PHASE live_detached/closure/T/M/runtime are cumulative parent metadata, not phase-local populations; never summed.',
   'final_cycle':g['cycle'],'samples':list(self.samples.values()),'source_equation_families_checked':15+(13 if self.is_r3 else 0),
   'r3_candidate_population_schema_equation':self.is_r3,
   'r3_derived_checks':'Short-circuit checked/NA ordering and joint subset constraints, explicitly DERIVED' if self.is_r3 else None,
   'derived_checks':['GLOBAL=sum exact expected SLICE IDs','bounded sample stored/dropped accounting and samples_seen=pressure-hook calls','new detach_success equals old RO detached per exact slice','metadata live_detached equals successful minus retired transitions'],
   'legacy_ROC1_drain_still_required':True,'scientific_application_acceptance_granted':False}
 def decode(self,stream):
  try:
   while True:
    line=stream.readline(self.max_line+1)
    if not line:break
    self.line_number+=1;self.total_bytes+=len(line)
    require(len(line)<=self.max_line,'line cap exceeded');require(self.total_bytes<=self.max_input,'raw input cap exceeded')
    self.ingest(line)
   result=self.snapshot(self.cur)
   result.update(status='SYNTHETIC_OBSERVER_CONTROL_ONLY' if self.kind=='SYNTHETIC' else 'VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY',
    data_kind=self.kind,full_application_qualified=False,expected_slice_count=self.n,require_closed=self.closed,
    observer_records=self.records,observer_bytes=self.observer_bytes,input_bytes=self.total_bytes,
    observer_stream_sha256=self.all_observer_sha.hexdigest(),snapshot_count=self.rounds+1,
    identical_duplicates=self.identical_duplicates,schema_counter_fields=list(self.fields))
   return result
  except (Invalid,Incomplete) as e:
   return {'status':'INCOMPLETE' if isinstance(e,Incomplete) else 'INVALID','reason':str(e),'line_number':self.line_number,
    'data_kind':self.kind,'scientific_application_acceptance_granted':False,'full_application_qualified':False}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw');p.add_argument('--schema',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 schema_path=Path(a.schema);require(schema_path.stat().st_size<=1048576,'schema size bound')
 schema=json.loads(schema_path.read_text(),object_pairs_hook=unique)
 # One raw-file open, streaming once; no native/controller/registry side effects.
 with Path(a.raw).open('rb') as f:result=Decoder(schema).decode(f)
 result['schema_file_sha256']=hashlib.sha256(schema_path.read_bytes()).hexdigest()
 Path(a.out).write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
