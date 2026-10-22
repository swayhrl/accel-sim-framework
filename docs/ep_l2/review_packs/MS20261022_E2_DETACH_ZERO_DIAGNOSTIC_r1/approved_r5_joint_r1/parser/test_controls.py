import copy,hashlib,importlib.util,io,json,unittest
from collections import defaultdict
from pathlib import Path
import decoder
from decoder import Feed,AuditError,CONTRACT,SCHEMA_SHA256,PREFIX,OLD,TappingReader
from math_audit import audit_math,DIMS,U64
PACK=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1')
R4_SCHEMA=json.loads((PACK/'runtime_r4/SOURCE_BOUND_SCHEMA_r4.json').read_text())
BIND={'core_source_commit':'1'*40,'binary_sha256':'2'*64,'archive_sha256':'3'*64}

def scope(raw=2,ways=None,req=0,runtime=True,T=True,route=1,admit=True,early=0,sid=0,pid=0):
 if ways is None:ways=[(1,False,False,False,False)]*16
 r=sum(w[0]==0 for w in ways);inv=sum(w[0]==1 for w in ways)
 eligible=sum(w[1] and w[2] and not w[3] and w[4] for w in ways) if runtime else 0
 reasons=0;pred=defaultdict(int);cl=defaultdict(int)
 for kind,live,att,reuse,missing in ways:
  cl[kind]+=1
  if not runtime:continue
  if not live:reasons|=16;continue
  p=int(att)|int(reuse)*2|int(missing)*4;pred[p]+=1
  if not att:reasons|=2
  if reuse:reasons|=4
  if not missing:reasons|=8
  if att and not reuse and missing:reasons|=1
 h={n:[] for n in DIMS};h['heads_raw_reserved']=[[raw,r,1]];h['heads_raw_reserved_invalid']=[[raw,r,inv,1]];h['ways_raw_reserved_class']=[[raw,r,k,n] for k,n in cl.items()]
 if runtime:h['heads_raw_reserved_eligible']=[[raw,r,eligible,1]];h['heads_raw_reserved_reasonmask']=[[raw,r,reasons,1]];h['ways_raw_reserved_predmask']=[[raw,r,p,n] for p,n in pred.items()]
 h['head_route_joint']=[[sid,pid,raw,r,req if runtime else 2,2 if eligible else 1 if runtime else 0,route,int(admit),early,1]]
 return {'covered':1,'absent':0,'skipped':[0]*4,'ro_observed':int(runtime),'ro_na':int(not runtime),'T':T,'M':True,'ro_runtime':runtime,'invalid':False,'members':[[sid,pid]],'histograms':h}
def empty_scope(sid=0,pid=0):
 d=scope(sid=sid,pid=pid);d.update(covered=0,ro_observed=0);d['histograms']={n:[] for n in DIMS};return d

def oldcounts(d):
 c={k:0 for k in R4_SCHEMA['counter_fields']};c.update(observed_heads=d['covered']+sum(d['skipped']),probe_skipped=sum(d['skipped']),head_absent_cycles=d['absent'])
 for k,v in zip(('skip_tvd','skip_ideal','skip_disabled','skip_other'),d['skipped']):c[k]=v
 names=('raw_hit','raw_hit_reserved','raw_miss','raw_reservation_fail','raw_sector_miss','raw_mshr_hit','raw_write_allocated','raw_unknown')
 for raw,r,n in d['histograms']['heads_raw_reserved']:c[names[raw]]+=n
 for row in d['histograms']['head_route_joint']:c[('requester_ro_candidate','requester_nonro','requester_ro_runtime_off')[row[4]]]+=row[-1]
 return c

def frame(kind,sid,pid,d,seq=1,cycle=100,closed=True,catalog=None):
 catalog=[] if catalog is None else catalog
 return {'record':kind,'schema_id':CONTRACT['schema_id'],'schema_sha256':SCHEMA_SHA256,'source_base_core':CONTRACT['base_core'],'scope':CONTRACT['scope'],'slice':sid,'cycle':cycle,'snapshot_seq':seq,'phase':pid,'kernel_scope':kind+'_CUMULATIVE' if pid==-1 else 'UNASSIGNED' if pid==0 else 'OVERLAP_UNKNOWN' if pid==1 else 'SINGLE_ACTIVE_INTERVAL','kernel_uid':catalog[pid-2] if pid>=2 else None,'kernel_catalog':catalog,'assoc':16,'T':d['T'],'M':d['M'],'ro_runtime':d['ro_runtime'],'epoch_closed':closed,'overflow_invalid':False,'output_invalid':False,'closure_ok':True,'counters':{'observed_heads':d['covered']+sum(d['skipped']),'covered':d['covered'],'probe_skipped':sum(d['skipped']),**dict(zip(('skip_tvd','skip_ideal','skip_disabled','skip_other'),d['skipped'])),'head_absent_cycles':d['absent'],'ro_observed':d['ro_observed'],'ro_na':d['ro_na']},'histograms':{k:v for k,v in d['histograms'].items() if k!='head_route_joint'},'route_joint':d['histograms']['head_route_joint']}
def aggregate(frames,kind,sid):
 c,hs=decoder.add_frames(frames);out=copy.deepcopy(frames[0]);out.update(record=kind,slice=sid,phase=-1,kernel_uid=None,kernel_scope=kind+'_CUMULATIVE',counters=c,histograms={n:[list(k)+[v] for k,v in hs[n].items()] for n in DIMS if n!='head_route_joint'},route_joint=[list(k)+[v] for k,v in hs['head_route_joint'].items()]);return out

def snapshot(d=None,n=1,seq=1,cycle=100,closed=True,catalog=None,registered=None):
 catalog=[] if catalog is None else catalog;frames=[]
 for sid in range(n):
  phases=[]
  for pid in range(len(catalog)+2):
   dd=copy.deepcopy(d) if d is not None and pid==0 else empty_scope(sid,pid)
   dd['members']=[[sid,pid]]
   for row in dd['histograms']['head_route_joint']:row[0]=sid;row[1]=pid
   phases.append(frame('PHASE',sid,pid,dd,seq,cycle,closed,catalog))
  frames.extend([aggregate(phases,'SLICE',sid)]+phases)
 glob=aggregate([f for f in frames if f['record']=='SLICE'],'GLOBAL',registered or n)
 if registered and registered>n:glob['epoch_closed']=False
 frames.append(glob);return frames

def old_frame(f):
 can={'covered':f['counters']['covered'],'absent':f['counters']['head_absent_cycles'],'skipped':[f['counters'][k] for k in ('skip_tvd','skip_ideal','skip_disabled','skip_other')],'histograms':{**f['histograms'],'head_route_joint':f['route_joint']}}
 return {'record':f['record'],'slice':f['slice'],'cycle':f['cycle'],'phase':f['phase'],'kernel_scope':'SLICE_CUMULATIVE' if f['phase']==-1 else f['kernel_scope'],'kernel_uid':f['kernel_uid'],'candidate_owner_kernel':None,'trigger_later_linkage':'NOT_MEASURED','overflow_invalid':False,'output_invalid':False,'closure_ok':True,'epoch_closed':f['epoch_closed'],'T':f['T'],'M':f['M'],'ro_runtime':f['ro_runtime'],'live_detached':0,'counters':oldcounts(can)}
def old_result(frames,synthetic=True):
 g=frames[-1];return {'status':'SYNTHETIC_OBSERVER_CONTROL_ONLY' if synthetic else 'VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY','schema_counter_fields':R4_SCHEMA['counter_fields'],'final_cycle':g['cycle'],'global_counters':old_frame(g)['counters'],'slice_counters':{str(f['slice']):old_frame(f)['counters'] for f in frames if f['record']=='SLICE'}}
def encode(frames):
 # Pure synthetic declaration order; native evidence is not asserted.
 out=b'';batch=[]
 for f in frames:
  batch.append(f)
  if f['record']=='GLOBAL':
   out+=b''.join(OLD+json.dumps(old_frame(x)).encode()+b'\n' for x in batch)+b''.join(PREFIX+json.dumps(x).encode()+b'\n' for x in batch);batch=[]
 if batch:out+=b''.join(OLD+json.dumps(old_frame(x)).encode()+b'\n' for x in batch)+b''.join(PREFIX+json.dumps(x).encode()+b'\n' for x in batch)
 return out
def run(frames,*,n=1,registered=None,full=False,extra=b'',synth=True):
 a=frames[-1];feed=Feed(expected_slices=list(range(n)),registered_slice_count=registered or n,expected_kernels=a['kernel_catalog'],expected_flags={k:a[k] for k in ('T','M','ro_runtime')},source_binding=BIND,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=full,allow_synthetic=synth)
 for line in (encode(frames)+extra).splitlines(keepends=True):feed.feed(line)
 return feed.finish(old_result(frames,synth))

class MathControls(unittest.TestCase):
 def valid(self,d):self.assertEqual(audit_math(d)['status'],'MATH_VALID_NOT_QUALIFICATION')
 def bad(self,d):
  with self.assertRaises((AuditError,KeyError,TypeError)):audit_math(d)
 def test_empty_scope_is_zero_pop_not_qualification(self):self.valid(empty_scope())
 def test_miss_empty_set(self):self.valid(scope(req=1))
 def test_r16_new_identityfail_eligible(self):self.valid(scope(3,[(0,True,True,False,True)]*16))
 def test_r16_hit_is_not_newtagfail(self):self.valid(scope(0,[(0,True,True,False,True)]*16))
 def test_r16_hitreserved(self):self.valid(scope(1,[(0,True,True,False,True)]*16))
 def test_r16_sectormiss(self):self.valid(scope(4,[(0,True,True,False,True)]*16))
 def test_r16_miss_invalid(self):self.bad(scope(2,[(0,True,True,False,True)]*16))
 def test_r15_fail_invalid(self):self.bad(scope(3,[(0,True,True,False,True)]*15+[(1,False,False,False,False)]))
 def test_reuse_missing_overlap(self):self.valid(scope(3,[(0,True,True,True,False)]*16))
 def test_mixed_actual_predicates(self):self.valid(scope(3,[(0,True,True,False,True)]*3+[(0,True,True,True,True)]*5+[(0,True,True,False,False)]*4+[(0,False,False,False,False)]*4))
 def test_runtimeoff_tag_observed_RO_NA(self):self.valid(scope(runtime=False))
 def test_T0_structural_eligible_legal(self):self.valid(scope(3,[(0,True,True,False,True)]*16,T=False))
 def test_runtimeoff_wrong_eligible(self):
  d=scope(runtime=False);d['histograms']['head_route_joint'][0][5]=1;self.bad(d)
 def test_bool_count(self):d=scope();d['covered']=True;self.bad(d)
 def test_bool_coordinate(self):d=scope();d['histograms']['heads_raw_reserved'][0][0]=False;self.bad(d)
 def test_negative(self):d=scope();d['histograms']['heads_raw_reserved'][0][-1]=-1;self.bad(d)
 def test_float(self):d=scope();d['covered']=1.0;self.bad(d)
 def test_duplicate_bin(self):d=scope();d['histograms']['heads_raw_reserved']*=2;self.bad(d)
 def test_explicit_zero_is_not_missing(self):d=scope();d['histograms']['heads_raw_reserved'][0][-1]=0;self.bad(d)
 def test_missing_hist_not_zero(self):d=scope();del d['histograms']['ways_raw_reserved_predmask'];self.bad(d)
 def test_crossslice_tuple(self):d=scope();d['histograms']['head_route_joint'][0][0]=1;self.bad(d)
 def test_wrong_joint_eligible(self):d=scope();d['histograms']['head_route_joint'][0][5]=2;self.bad(d)
 def test_wrong_presence_joint(self):d=scope();d['histograms']['heads_raw_reserved_reasonmask'][0][2]=0;self.bad(d)
 def test_way_overcount(self):d=scope();d['histograms']['ways_raw_reserved_class'][0][-1]=17;self.bad(d)
 def test_invalid_weight(self):d=scope();d['histograms']['heads_raw_reserved_invalid'][0][2]=15;self.bad(d)
 def test_predicate_marginal_invented(self):d=scope();d['histograms']['ways_raw_reserved_predmask']=[[2,0,5,1]];self.bad(d)
 def test_uint64_overflow(self):d=scope();d['covered']=2**64;self.bad(d)
 def test_rawFAIL_hidden_by_preview_miss(self):
  d=scope(3,[(0,True,True,False,True)]*16,route=2);c=oldcounts(d);audit_math(d,c);c['raw_reservation_fail']=0;c['raw_miss']=1
  with self.assertRaises(AuditError):audit_math(d,c)
 def test_requester_swap_not_marginal_product(self):
  d=scope();c=oldcounts(d);c['requester_ro_candidate']=0;c['requester_nonro']=1
  with self.assertRaises(AuditError):audit_math(d,c)

class StreamControls(unittest.TestCase):
 def ok(self,result):self.assertIn(result['status'],('R5_SYNTHETIC_CONTROL_ONLY','VALID_R5_OBSERVER_DECLARATIONS_ONLY'),result);self.assertFalse(result['scientific_acceptance_granted'])
 def bad(self,result):self.assertEqual(result['status'],'INVALID_R5',result)
 def test_valid_snapshot(self):self.ok(run(snapshot(scope())))
 def test_native_registered2_selected1(self):self.ok(run(snapshot(scope(),registered=2),registered=2))
 def test_all64_full_mode_still_not_qualification(self):self.ok(run(snapshot(n=64),n=64,full=True,synth=False))
 def test_fullmode_requires64(self):
  with self.assertRaises(AuditError):run(snapshot(),full=True,synth=False)
 def test_missing_old_scope(self):
  f=snapshot();feed=Feed(expected_slices=[0],registered_slice_count=1,expected_kernels=[],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=BIND,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=False,allow_synthetic=True)
  for x in f:feed.feed(PREFIX+json.dumps(x).encode()+b'\n')
  self.bad(feed.finish(old_result(f)))
 def test_missing_phase(self):d=snapshot();del d[2];self.bad(run(d))
 def test_phase_label_fake(self):d=snapshot();d[1]['phase']=1;self.bad(run(d))
 def test_crossslice_phase(self):d=snapshot();d[1]['slice']=1;self.bad(run(d))
 def test_empty_catalog_uid_invented(self):d=snapshot();d[1]['kernel_uid']=99;self.bad(run(d))
 def test_schema_wrong(self):d=snapshot();d[0]['schema_sha256']='f'*64;self.bad(run(d))
 def test_sourcebase_wrong(self):d=snapshot();d[0]['source_base_core']='1'*40;self.bad(run(d))
 def test_scope_wrong(self):d=snapshot();d[0]['scope']='KERNEL_CAUSAL';self.bad(run(d))
 def test_bad_flag(self):d=snapshot();d[0]['T']=1;self.bad(run(d))
 def test_overflowinvalid(self):d=snapshot();d[0]['overflow_invalid']=True;self.bad(run(d))
 def test_outputinvalid_after_valid(self):self.bad(run(snapshot(),extra=PREFIX+b'{"record":"OUTPUT_INVALID","output_invalid":true}\n'))
 def test_partial_tail_no_fallback(self):d=snapshot();tail=copy.deepcopy(d[0]);tail['snapshot_seq']=2;tail['cycle']=101;self.bad(run(d,extra=OLD+json.dumps(old_frame(tail)).encode()+b'\n'+PREFIX+json.dumps(tail).encode()+b'\n'))
 def test_duplicate_json_key(self):self.bad(run(snapshot(),extra=PREFIX+b'{"record":"SLICE","record":"OUTPUT_INVALID"}\n'))
 def test_unknown_field(self):d=snapshot();d[0]['pretendQ']=True;self.bad(run(d))
 def test_wrong_global_registered(self):d=snapshot();d[-1]['slice']=2;self.bad(run(d))
 def test_rollup_mutation(self):d=snapshot(scope());d[-1]['route_joint'][0][7]=0;self.bad(run(d))
 def test_unclosed_terminal(self):self.bad(run(snapshot(closed=False)))
 def test_exact_samecycle_repeat(self):self.ok(run(snapshot(scope())+snapshot(scope(),seq=2)))
 def test_samecycle_metadata_close(self):r=run(snapshot(scope(),closed=False)+snapshot(scope(),seq=2,closed=True));self.ok(r);self.assertEqual(r['same_cycle_metadata_closures'],1)
 def test_samecycle_growth_rejected(self):self.bad(run(snapshot()+snapshot(scope(),seq=2)))
 def test_latercycle_growth_allowed(self):self.ok(run(snapshot()+snapshot(scope(),seq=2,cycle=101)))
 def test_latercycle_counter_rollback(self):self.bad(run(snapshot(scope())+snapshot(seq=2,cycle=101)))
 def test_epoch_reopen(self):self.bad(run(snapshot(scope())+snapshot(scope(),seq=2,cycle=101,closed=False)))
 def test_late_old_samecycle_close_missing_new(self):
  d=snapshot(closed=False);later=copy.deepcopy(d);[x.update(epoch_closed=True) for x in later];extra=b''.join(OLD+json.dumps(old_frame(x)).encode()+b'\n' for x in later);self.bad(run(d,extra=extra))
 def test_r5cap(self):
  save=decoder.MAX_R5
  try:decoder.MAX_R5=20;self.bad(run(snapshot()))
  finally:decoder.MAX_R5=save
 def test_inputcap(self):
  save=decoder.MAX_INPUT
  try:decoder.MAX_INPUT=20;self.bad(run(snapshot()))
  finally:decoder.MAX_INPUT=save
 def test_fixed212_byte_transparency_real_synthetic_decoder(self):
  path=PACK/'parser_recovery/decoder_samecycle_close.py';self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),decoder.FIXED_R4_SHA256)
  sp=importlib.util.spec_from_file_location('fixed_r4_compat',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  f=snapshot(n=2,catalog=[12]);raw=b''
  for sid in range(2):
   group=[x for x in f if x['record']!='GLOBAL' and x['slice']==sid]
   if sid==1:group.append(f[-1])
   raw+=b''.join(OLD+json.dumps(old_frame(x)).encode()+b'\n' for x in group)
   raw+=b'EPL2ROV1|SUMMARY|slice='+str(sid).encode()+b'|detached=0\n'
  raw+=b''.join(PREFIX+json.dumps(x).encode()+b'\n' for x in f)
  feed=Feed(expected_slices=[0,1],registered_slice_count=2,expected_kernels=[12],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=BIND,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=False,allow_synthetic=True)
  baseline=m.Decoder(R4_SCHEMA,expected_slice_count=2,data_kind='SYNTHETIC').decode(io.BytesIO(raw))
  tapped=m.Decoder(R4_SCHEMA,expected_slice_count=2,data_kind='SYNTHETIC').decode(TappingReader(io.BytesIO(raw),feed))
  self.assertEqual(tapped,baseline);self.assertEqual(tapped['status'],'SYNTHETIC_OBSERVER_CONTROL_ONLY',tapped);self.ok(feed.finish(tapped))

if __name__=='__main__':unittest.main(verbosity=2)
