import copy
import io
import json
from pathlib import Path
import unittest
from decoder import Decoder,Invalid,PREFIX,OLD
SCHEMA=json.loads((Path(__file__).parent/'SOURCE_BOUND_SCHEMA_cf.json').read_text())

def counts():return {k:0 for k in SCHEMA['counter_fields']}

def record(kind,sid,phase=-1):
 return {'record':kind,'slice':sid,'cycle':100,'phase':phase,
  'kernel_scope':'SLICE_CUMULATIVE' if phase==-1 else 'UNASSIGNED' if phase==0 else 'OVERLAP_UNKNOWN' if phase==1 else 'SINGLE_ACTIVE_INTERVAL',
  'kernel_uid':None if phase<2 else 10+phase,'candidate_owner_kernel':None,'trigger_later_linkage':'NOT_MEASURED',
  'overflow_invalid':False,'output_invalid':False,'closure_ok':True,'epoch_closed':True,
  'T':True,'M':True,'ro_runtime':True,'live_detached':0,'counters':counts()}

def rows(n=2):
 out=[]
 for sid in range(n):
  out.extend([record('SLICE',sid),record('PHASE',sid,0),record('PHASE',sid,1),record('PHASE',sid,2)])
  if sid==n-1:out.append(record('GLOBAL',n))
  out.append({'old':sid,'detached':0})
 return out

def encode(data):
 out=b''
 for r in data:
  if isinstance(r,bytes):out+=r
  elif 'old' in r:out+=OLD+f"slice={r['old']}|detached={r['detached']}\n".encode()
  else:out+=PREFIX+json.dumps(r,separators=(',',':')).encode()+b'\n'
 return out

def run(data,n=2,**kw):return Decoder(SCHEMA,expected_slice_count=n,data_kind='SYNTHETIC',**kw).decode(io.BytesIO(encode(data)))
def pick(data,kind,sid=0,phase=None):return next(r for r in data if isinstance(r,dict) and r.get('record')==kind and r['slice']==sid and (phase is None or r['phase']==phase))
def change(data,key,value,sid=0,phase=2):
 pick(data,'PHASE',sid,phase)['counters'][key]=value
 pick(data,'SLICE',sid)['counters'][key]=value
 pick(data,'GLOBAL',2)['counters'][key]=value

def pressure(data,sid=0,n=1):
 for k in ['observed_heads','raw_reservation_fail','pressure_T_enabled','pressure_no_live_ro',
  'pressure_prod_probe_reached','pressure_relief_not_consulted','pressure_frontend_denied','primary_unknown','eligible_hist_0']:
  change(data,k,n,sid)
 change(data,'ways_examined',16*n,sid);change(data,'way_no_live_ro',16*n,sid)

def sample(sid=0,uid=1):
 return {'record':'SAMPLE','slice':sid,'cycle':uid,'request_uid':uid,'set':0,'eligible':0,
  'first_eligible_way':2**32-1,'victim_payload':2**64-1,'victim_generation':0,'required':0,'issued':0,'ready':0,
  'reuse_seen':False,'attached':False,'requester_ro_candidate':False,'immediate_commit_result':-1,'candidate_owner_kernel':None}

class Controls(unittest.TestCase):
 def valid(self,r):self.assertEqual(r['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY');self.assertFalse(r['scientific_application_acceptance_granted']);self.assertTrue(r['legacy_ROC1_drain_still_required'])
 def invalid(self,r):self.assertEqual(r['status'],'INVALID',r)
 def test_full64_zero_is_synthetic_only(self):self.valid(run(rows(64),64))
 def test_two_slice_fixture(self):self.valid(run(rows(),require_closed=False))
 def test_missing_slice(self):
  d=[r for r in rows() if r.get('record')!='SLICE' or r['slice']!=1];self.assertEqual(run(d)['status'],'INCOMPLETE')
 def test_extra_slice(self):
  d=rows();d.insert(0,record('SLICE',2));self.invalid(run(d))
 def test_global_slice_is_owner_count(self):
  d=rows();pick(d,'GLOBAL',2)['slice']=1;self.invalid(run(d))
 def test_missing_counter_not_zero(self):
  d=rows();del pick(d,'SLICE')['counters']['detach_success'];self.invalid(run(d))
 def test_extra_counter_not_silently_ignored(self):
  d=rows();pick(d,'SLICE')['counters']['new_guess']=0;self.invalid(run(d))
 def test_bool_counter(self):
  d=rows();pick(d,'SLICE')['counters']['detach_success']=False;self.invalid(run(d))
 def test_above_u64(self):
  d=rows();pick(d,'SLICE')['counters']['detach_success']=2**64;self.invalid(run(d))
 def test_overflow_flag(self):
  d=rows();pick(d,'SLICE')['overflow_invalid']=True;self.invalid(run(d))
 def test_output_invalid_marker(self):self.invalid(run([{'record':'OUTPUT_INVALID','output_invalid':True,'reason':'synthetic'}]))
 def test_output_invalid_metadata(self):
  d=rows();pick(d,'SLICE')['output_invalid']=True;self.invalid(run(d))
 def test_duplicate_json_key(self):
  d=rows();d.insert(0,PREFIX+b'{"record":"SLICE","record":"GLOBAL"}\n');self.invalid(run(d))
 def test_nested_duplicate_key(self):
  d=rows();d.insert(0,PREFIX+b'{"record":"SLICE","counters":{"x":0,"x":1}}\n');self.invalid(run(d))
 def test_identical_record_duplicate(self):
  d=rows();d.insert(1,copy.deepcopy(d[0]));r=run(d);self.valid(r);self.assertEqual(r['identical_duplicates'],1)
 def test_conflicting_record_duplicate(self):
  d=rows();dup=copy.deepcopy(d[0]);dup['cycle']=101;d.insert(1,dup);self.invalid(run(d))
 def test_truncated_tail_never_falls_back(self):
  d=rows();new=record('SLICE',0);new['cycle']=101;d.append(new);self.assertEqual(run(d)['status'],'INCOMPLETE')
 def test_latest_complete_snapshot(self):
  a=rows();b=rows()
  for r in b:
   if 'cycle' in r:r['cycle']=101
  self.valid(run(a+b));self.assertEqual(run(a+b)['snapshot_count'],2)
 def test_metadata_fake_closure_with_live(self):
  d=rows()
  for k in ['detach_calls','detach_success']:change(d,k,1)
  # Producer closure_ok can be true despite lifecycle live; must reject fabricated0 metadata.
  self.invalid(run(d))
 def test_epoch_false(self):
  d=rows();pick(d,'SLICE')['epoch_closed']=False;self.invalid(run(d))
 def test_phase_live_is_parent_not_summed(self):
  d=rows()
  for k in ['detach_calls','detach_success']:change(d,k,1)
  pick(d,'SLICE')['live_detached']=1
  for ph in range(3):pick(d,'PHASE',phase=ph)['live_detached']=1
  pick(d,'GLOBAL',2)['live_detached']=1
  for r in d:
   if 'old' in r and r['old']==0:r['detached']=1
   elif r.get('record')=='GLOBAL' or r.get('slice')==0:r['epoch_closed']=False
  r=run(d,require_closed=False);self.valid(r)
 def test_phase_scope_mismatch(self):
  d=rows();pick(d,'PHASE',phase=1)['kernel_scope']='SINGLE_ACTIVE_INTERVAL';self.invalid(run(d))
 def test_explicit_overlap_bucket_is_additive_residual(self):
  d=rows()
  for k in ['observed_heads','raw_miss','primary_none']:change(d,k,1,phase=1)
  self.valid(run(d))
 def test_same_kernel_in_two_phase_buckets(self):
  d=rows();r=record('PHASE',0,3);r['kernel_uid']=12;d.insert(4,r);self.invalid(run(d))
 def test_slice_phase_rollup(self):
  d=rows();pick(d,'PHASE',phase=2)['counters']['ro_admits']=1;self.invalid(run(d))
 def test_global_rollup(self):
  d=rows();pick(d,'GLOBAL',2)['counters']['ro_admits']=1;self.invalid(run(d))
 def test_false_source_eq_despite_closure_true(self):
  d=rows();change(d,'raw_reservation_fail',1);self.invalid(run(d))
 def test_old_new_detached_mismatch(self):
  d=rows();next(r for r in d if 'old' in r)['detached']=1;self.invalid(run(d))
 def test_missing_old_summary(self):
  d=[r for r in rows() if 'old' not in r];self.assertEqual(run(d)['status'],'INCOMPLETE')
 def test_native_not_consulted_not_noeligible(self):
  d=rows();pressure(d)
  for k in ['samples_seen','samples_stored']:change(d,k,1)
  d.append(sample());r=run(d);self.valid(r);self.assertEqual(r['global_counters']['pressure_relief_not_consulted'],1);self.assertEqual(r['global_counters']['pressure_kept_fail'],0)
 def test_drop_sample_does_not_drop_counters(self):
  d=rows();pressure(d,n=65)
  change(d,'samples_seen',65);change(d,'samples_stored',64);change(d,'samples_dropped',1)
  d.extend(sample(uid=i+1) for i in range(64));self.valid(run(d))
 def test_sample_cap65(self):
  d=rows();d.extend(sample(uid=i+1) for i in range(65));self.invalid(run(d))
 def test_immediate_minus1_is_unknown(self):
  d=rows();pressure(d)
  for k in ['samples_seen','samples_stored']:change(d,k,1)
  d.append(sample());r=run(d);self.valid(r);self.assertEqual(r['samples'][0]['immediate_commit_result'],-1)
 def test_false_sample_count(self):
  d=rows();change(d,'samples_stored',1);change(d,'samples_seen',1);self.invalid(run(d))
 def test_line_bound(self):self.invalid(run([b'x'*100+b'\n'],max_line_bytes=10))
 def test_observer_bytes_bound(self):self.invalid(run(rows(),max_observer_bytes=30))
 def test_wrong_flags(self):
  d=rows();pick(d,'SLICE')['M']=False;self.invalid(run(d))
 def test_negative_clock(self):
  d=rows();pick(d,'SLICE')['cycle']=-1;self.invalid(run(d))
 def test_changed_schema_needs_explicit_source_diff(self):
  d=copy.deepcopy(SCHEMA);d['counter_fields'].append('new_r2_field')
  with self.assertRaises(Invalid):Decoder(d)
 def test_extra_metadata_not_accepted(self):
  d=rows();pick(d,'SLICE')['fake_source_flag']=True;self.invalid(run(d))



class AdditionalControls(unittest.TestCase):
 def test_sample_clock_cannot_be_future(self):
  d=rows();pressure(d);change(d,'samples_seen',1);change(d,'samples_stored',1);r=sample();r['cycle']=101;d.append(r)
  self.assertEqual(run(d)['status'],'INVALID')
 def test_no_newline_is_not_complete_framing(self):
  data=encode(rows()).rstrip(b'\n');r=Decoder(SCHEMA,expected_slice_count=2,data_kind='SYNTHETIC').decode(io.BytesIO(data));self.assertEqual(r['status'],'INCOMPLETE')
 def test_legal_nonzero_victim_multiple_responses_trigger_denied(self):
  d=rows()
  for k in ['detach_calls','detach_success','detached_retired','ft_access_attempts','commit_denied','trigger_denied_after_detach','denied_capacity']:change(d,k,1)
  change(d,'detached_responses',7)
  next(r for r in d if 'old' in r)['detached']=1
  r=run(d);self.assertEqual(r['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY');self.assertEqual(r['global_counters']['detached_responses'],7)
 def test_T_false_counter_cannot_hide_under_true_metadata(self):
  d=rows();pressure(d)
  change(d,'pressure_T_disabled',1);change(d,'pressure_T_enabled',0);change(d,'pressure_no_live_ro',0)
  change(d,'ways_examined',0);change(d,'way_no_live_ro',0);change(d,'eligible_hist_0',0)
  change(d,'samples_seen',1);change(d,'samples_stored',1);d.append(sample())
  self.assertEqual(run(d)['status'],'INVALID')
 def test_explicit_new_field_revision_and_complete_fields(self):
  import hashlib
  schema=copy.deepcopy(SCHEMA);schema['counter_fields'].append('explicit_synthetic_r2_field')
  schema['reviewed_field_set_revision']={'base_source_commit':'cf7347151f86a17866b91af6d3f2da726ea8d062','E_reviewed':True,'new_source_commit':'b'*40,'source_diff_sha256':'c'*64,'new_counter_fields_sha256':hashlib.sha256(json.dumps(schema['counter_fields'],separators=(',',':')).encode()).hexdigest()}
  d=rows()
  for r in d:
   if 'counters' in r:r['counters']['explicit_synthetic_r2_field']=0
  result=Decoder(schema,expected_slice_count=2,data_kind='SYNTHETIC').decode(io.BytesIO(encode(d)));self.assertEqual(result['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY')
 def test_declared_revision_does_not_fill_missing_new_field(self):
  import hashlib
  schema=copy.deepcopy(SCHEMA);schema['counter_fields'].append('explicit_synthetic_r2_field')
  schema['reviewed_field_set_revision']={'base_source_commit':'cf7347151f86a17866b91af6d3f2da726ea8d062','E_reviewed':True,'new_source_commit':'b'*40,'source_diff_sha256':'c'*64,'new_counter_fields_sha256':hashlib.sha256(json.dumps(schema['counter_fields'],separators=(',',':')).encode()).hexdigest()}
  result=Decoder(schema,expected_slice_count=2,data_kind='SYNTHETIC').decode(io.BytesIO(encode(rows())));self.assertEqual(result['status'],'INVALID')



class DuplicateTailControls(unittest.TestCase):
 def test_same_clock_conflict_after_complete_global(self):
  d=rows();r=copy.deepcopy(pick(d,'SLICE'));r['counters']['raw_miss']=1;d.append(r);self.assertEqual(run(d)['status'],'INVALID')
 def test_clock_regression_after_complete_global(self):
  d=rows();r=copy.deepcopy(pick(d,'SLICE'));r['cycle']=99;d.append(r);self.assertEqual(run(d)['status'],'INVALID')

class IndependentReviewFixControls(unittest.TestCase):
 def advance(self,data,cycle=101):
  for r in data:
   if isinstance(r,dict) and 'cycle' in r:r['cycle']=cycle
  return data
 def test_counter_regression_witness_rejected(self):
  a=rows();change(a,'head_absent_cycles',5)
  r=run(a+self.advance(rows()));self.assertEqual(r['status'],'INVALID');self.assertIn('regressed',r['reason'])
 def test_old_and_new_detached_rewind_witness_rejected(self):
  a=rows()
  for k in ('detach_calls','detach_success','detached_retired'):change(a,k,1)
  next(r for r in a if 'old' in r)['detached']=1
  self.assertEqual(run(a+self.advance(rows()))['status'],'INVALID')
 def test_phase_counts_cannot_move_to_another_bucket(self):
  a=rows();change(a,'head_absent_cycles',5)
  b=rows();change(b,'head_absent_cycles',5,phase=0)
  r=run(a+self.advance(b));self.assertEqual(r['status'],'INVALID');self.assertIn('PHASE',r['reason'])
 def test_old_authoritative_detached_regression_direct(self):
  decoder=Decoder(SCHEMA,expected_slice_count=2,data_kind='SYNTHETIC')
  decoder.last={'old':{0:{'detached':1}}}
  with self.assertRaisesRegex(Invalid,'old RO detached counter regressed'):decoder.old(OLD+b'slice=0|detached=0\n')
 def test_existing_phase_uid_cannot_be_renumbered(self):
  b=rows()
  for r in b:
   if r.get('record')=='PHASE' and r['phase']==2:r['kernel_uid']=99
  result=run(rows()+self.advance(b));self.assertEqual(result['status'],'INVALID');self.assertIn('kernel UID changed',result['reason'])
 def test_phase_append_is_legal(self):
  b=rows()
  for sid in range(2):
   idx=next(i for i,r in enumerate(b) if r.get('record')=='PHASE' and r['slice']==sid and r['phase']==2)
   b.insert(idx+1,record('PHASE',sid,3))
  result=run(rows()+self.advance(b));self.assertEqual(result['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY');self.assertEqual(len(result['phase_catalog']),4)
 def test_existing_phase_cannot_disappear(self):
  a=rows()
  for sid in range(2):
   idx=next(i for i,r in enumerate(a) if r.get('record')=='PHASE' and r['slice']==sid and r['phase']==2)
   a.insert(idx+1,record('PHASE',sid,3))
  result=run(a+self.advance(rows()));self.assertEqual(result['status'],'INVALID');self.assertIn('disappeared',result['reason'])
 def test_earlier_open_epoch_can_be_followed_by_final_closed(self):
  a=rows()
  for r in a:
   if 'epoch_closed' in r:r['epoch_closed']=False
  result=run(a+self.advance(rows()));self.assertEqual(result['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY')
 def test_invalid_previous_complete_snapshot_not_hidden(self):
  a=rows();pick(a,'SLICE')['closure_ok']=False
  result=run(a+self.advance(rows()));self.assertEqual(result['status'],'INVALID');self.assertIn('closure_ok',result['reason'])
 def sample_data(self,s):
  d=rows();pressure(d)
  for k in ('samples_seen','samples_stored'):change(d,k,1)
  if s['eligible']:
   for k,v in {'pressure_no_live_ro':0,'pressure_eligible':1,'way_no_live_ro':15,'way_eligible':1,'eligible_hist_0':0,'eligible_hist_1':1,'predicate_hist_5':1}.items():change(d,k,v)
  d.append(s);return d
 def positive_sample(self):
  s=sample();s.update(eligible=1,first_eligible_way=15,victim_payload=1167,victim_generation=1,required=1,issued=0,ready=0,reuse_seen=False,attached=True)
  return s
 def test_valid_positive_eligible_sample(self):
  result=run(self.sample_data(self.positive_sample()));self.assertEqual(result['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY')
 def test_positive_sample_initial_ready_may_include_other_sectors(self):
  s=self.positive_sample();s['ready']=14
  self.assertEqual(run(self.sample_data(s))['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY')
 def test_eligible_payload_outside_P1_rejected(self):
  s=self.positive_sample();s['victim_payload']=1168;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_eligible_zero_generation_rejected(self):
  s=self.positive_sample();s['victim_generation']=0;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_eligible_generation_max_unsigned32_is_legal(self):
  s=self.positive_sample();s['victim_generation']=2**32-1;self.assertEqual(run(self.sample_data(s))['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY')
 def test_eligible_generation_above_unsigned32_rejected(self):
  s=self.positive_sample();s['victim_generation']=2**32;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_eligible_requires_attached(self):
  s=self.positive_sample();s['attached']=False;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_eligible_reuse_seen_rejected(self):
  s=self.positive_sample();s['reuse_seen']=True;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_eligible_all_required_ready_rejected(self):
  s=self.positive_sample();s['ready']=1;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_each_sample_sector_mask_four_bits(self):
  for key in ('required','issued','ready'):
   with self.subTest(key=key):
    s=self.positive_sample();s[key]=16;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_noeligible_sentinel_victim_defaults(self):
  self.assertEqual(run(self.sample_data(sample()))['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY')
  for key,value in (('victim_payload',0),('victim_generation',1),('required',1),('issued',1),('ready',1),('attached',True),('reuse_seen',True)):
   with self.subTest(key=key):
    s=sample();s[key]=value;self.assertEqual(run(self.sample_data(s))['status'],'INVALID')
 def test_partial_new_snapshot_still_not_fallback(self):
  r=record('SLICE',0);r['cycle']=101
  self.assertEqual(run(rows()+[r])['status'],'INCOMPLETE')
 def test_three_monotonic_rounds_and_new_phases(self):
  a=rows();change(a,'head_absent_cycles',1)
  b=rows();change(b,'head_absent_cycles',2)
  for sid in range(2):
   idx=next(i for i,r in enumerate(b) if r.get('record')=='PHASE' and r['slice']==sid and r['phase']==2)
   b.insert(idx+1,record('PHASE',sid,3))
  c=copy.deepcopy(b);change(c,'head_absent_cycles',3)
  result=run(a+self.advance(b,101)+self.advance(c,102));self.assertEqual(result['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY');self.assertEqual(result['snapshot_count'],3)


if __name__=='__main__':unittest.main()
