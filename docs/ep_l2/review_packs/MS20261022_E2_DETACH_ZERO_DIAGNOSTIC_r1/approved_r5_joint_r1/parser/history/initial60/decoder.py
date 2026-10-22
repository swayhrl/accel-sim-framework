"""Additive bounded r5 tap; never alters bytes delivered to the fixed r4 decoder.
Structural/mathematical validity only. Release, process exit, full instructions,
resources and scientific acceptance remain external original E authorities.
"""
import copy,hashlib,json
from collections import defaultdict
from pathlib import Path
from math_audit import AuditError,audit_math,require,sparse,total,uint,DIMS,U64
PREFIX=b'EPL2TAGPRESSUREV1|';OLD=b'EPL2DETACH_DIAG_V1|'
CONTRACT_BYTES=Path(__file__).with_name('WIRE_CONTRACT.json').read_bytes()
CONTRACT=json.loads(CONTRACT_BYTES);SCHEMA_SHA256=hashlib.sha256(CONTRACT_BYTES).hexdigest()
FIXED_R4_SHA256='647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4'
MAX_R5=64*2**20;MAX_INPUT=384*2**20
COUNTERS=set(CONTRACT['counters']);HIST=set(CONTRACT['histograms']);FIELDS=set(CONTRACT['frame_fields'])
def unique(pairs):
 out={}
 for k,v in pairs:require(k not in out,'duplicate JSON key '+str(k));out[k]=v
 return out
def parse(data):return json.loads(data,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(AuditError('nonfinite JSON '+x)))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sparse_dict(frame,name):return sparse(frame['route_joint'] if name=='head_route_joint' else frame['histograms'][name],DIMS[name],name)
def content(frame):return {'counters':frame['counters'],'histograms':{n:sorted(sparse_dict(frame,n).items()) for n in DIMS}}
def flags(frame):return tuple(frame[k] for k in ('T','M','ro_runtime'))
def add_frames(frames):
 c={k:0 for k in COUNTERS};hs={n:defaultdict(int) for n in DIMS}
 for f in frames:
  for k,v in f['counters'].items():c[k]+=v;require(c[k]<=U64,'rollup scalar overflow')
  for n in DIMS:
   for k,v in sparse_dict(f,n).items():hs[n][k]+=v;require(hs[n][k]<=U64,'rollup histogram overflow')
 return c,{n:dict(v) for n,v in hs.items()}

class Feed:
 def __init__(self,*,expected_slices,registered_slice_count,expected_kernels,
              expected_flags,source_binding,old212_decoder_sha256,
              full_application=True,allow_synthetic=False):
  require(isinstance(expected_slices,list) and expected_slices,'explicit slice membership')
  require(all(type(x) is int and 0<=x<64 for x in expected_slices),'bad expected slices')
  require(expected_slices==sorted(set(expected_slices)),'duplicate/unsorted expected slices')
  uint(registered_slice_count,'registered count',64);require(registered_slice_count>=len(expected_slices),'registered count below selection')
  require(type(full_application) is bool and type(allow_synthetic) is bool,'policy booleans')
  if full_application:require(expected_slices==list(range(64)) and registered_slice_count==64 and not allow_synthetic,'full application64 exact nonsynthetic')
  require(isinstance(expected_kernels,list) and len(expected_kernels)<=16,'exact input kernel catalog')
  for k in expected_kernels:uint(k,'expected kernel UID')
  require(len(set(expected_kernels))==len(expected_kernels),'duplicate expected kernels')
  require(isinstance(expected_flags,dict) and set(expected_flags)=={'T','M','ro_runtime'} and all(type(v) is bool for v in expected_flags.values()),'exact flags')
  require(old212_decoder_sha256==FIXED_R4_SHA256,'fixed old212 decoder identity changed')
  require(isinstance(source_binding,dict),'external release source binding')
  for key,n in [('core_source_commit',40),('binary_sha256',64),('archive_sha256',64)]:
   v=source_binding.get(key);require(isinstance(v,str) and len(v)==n and all(c in '0123456789abcdef' for c in v),'bad external source '+key)
  if not allow_synthetic:require(source_binding['core_source_commit']!=CONTRACT['base_core'],'r4 source cannot stand in for newr5 source')
  self.expected=expected_slices;self.registered=registered_slice_count;self.kernels=expected_kernels;self.expected_flags=expected_flags;self.binding=copy.deepcopy(source_binding);self.full=full_application;self.synthetic=allow_synthetic
  self.input_bytes=0;self.observer_bytes=0;self.error=None;self.old={};self.pending=None;self.last=None;self.snapshots=0;self.records=0;self.same_cycle_duplicates=0;self.same_cycle_closures=0;self.stream_sha=hashlib.sha256()
 def feed(self,line):
  """Sticky fail-closed tap; returns original bytes even after r5 error."""
  try:
   require(isinstance(line,bytes),'byte stream required');self.input_bytes+=len(line);require(self.input_bytes<=MAX_INPUT,'endpoint input cap')
   if line.startswith(PREFIX):
    self.observer_bytes+=len(line);require(self.observer_bytes<=MAX_R5,'r5 output64MiB cap');self.stream_sha.update(line);self.records+=1
    if self.error is None:self.ingest(parse(line[len(PREFIX):]))
   elif line.startswith(OLD) and self.error is None:
    r=parse(line[len(OLD):])
    if r.get('record') in ('SLICE','PHASE','GLOBAL'):
     for n in ('slice','cycle'):uint(r[n],'old '+n)
     key=(r['record'],r['slice'],r['phase'],r['cycle']);self.old[key]=r
  except (AuditError,ValueError,KeyError,TypeError,UnicodeError) as e:
   if self.error is None:self.error=str(e)
  return line
 def canonical(self,f):
  typ=f['record'];pid=f['phase'];sids=self.expected if typ=='GLOBAL' else [f['slice']]
  ps=list(range(len(f['kernel_catalog'])+2)) if typ!='PHASE' else [pid]
  c=f['counters'];return {'covered':c['covered'],'absent':c['head_absent_cycles'],'skipped':[c[n] for n in ('skip_tvd','skip_ideal','skip_disabled','skip_other')],'ro_observed':c['ro_observed'],'ro_na':c['ro_na'],'T':f['T'],'M':f['M'],'ro_runtime':f['ro_runtime'],'invalid':False,'members':[[s,p] for s in sids for p in ps],'histograms':{**f['histograms'],'head_route_joint':f['route_joint']}}
 def cross_old(self,f):
  key=(f['record'],f['slice'],f['phase'],f['cycle']);require(key in self.old,'same-snapshot old212 scope absent')
  r=self.old[key];require(isinstance(r.get('counters'),dict) and len(r['counters'])==212,'old212 exact field count')
  for k in ('T','M','ro_runtime','epoch_closed'):require(f[k]==r[k],'old/new metadata '+k)
  if f['record']=='PHASE':require(f['kernel_uid']==r['kernel_uid'] and f['kernel_scope']==r['kernel_scope'],'old/new phase UID mapping')
  return audit_math(self.canonical(f),r['counters'])
 def validate_frame(self,f):
  require(isinstance(f,dict),'frame object')
  if f.get('record')=='OUTPUT_INVALID':raise AuditError('source OUTPUT_INVALID marker')
  extra={'SYNTHETIC_FIXTURE'} if self.synthetic and f.get('SYNTHETIC_FIXTURE') is True else set()
  require(set(f)==FIELDS|extra,'exact wire field set')
  require(f['record'] in ('SLICE','PHASE','GLOBAL'),'unknown r5 record')
  require(f['schema_id']==CONTRACT['schema_id'] and f['schema_sha256']==SCHEMA_SHA256,'schema binding mismatch')
  require(f['source_base_core']==CONTRACT['base_core'] and f['scope']==CONTRACT['scope'],'sourcebase/scope mismatch')
  uint(f['slice'],'slice',64);uint(f['cycle'],'cycle');uint(f['snapshot_seq'],'sequence');require(f['snapshot_seq']>0,'sequence starts1')
  require(type(f['assoc']) is int and f['assoc']==16,'assoc16 required')
  for k in ('T','M','ro_runtime','epoch_closed','overflow_invalid','output_invalid','closure_ok'):require(type(f[k]) is bool,'boolean '+k)
  require(f['closure_ok'] and not f['overflow_invalid'] and not f['output_invalid'],'source invalid/closure flag')
  require(all(f[k]==v for k,v in self.expected_flags.items()),'qualified profile flags differ')
  cat=f['kernel_catalog'];require(isinstance(cat,list) and len(cat)<=16,'kernel catalog')
  for uid in cat:uint(uid,'catalog UID')
  require(len(set(cat))==len(cat),'duplicate kernel UID');require(cat==self.kernels[:len(cat)],'input catalog order/identity differs')
  if f['record']=='PHASE':
   uint(f['phase'],'phase',17);require(f['phase']<len(cat)+2,'phase outside catalog')
   uid=None if f['phase']<2 else cat[f['phase']-2];scope='UNASSIGNED' if f['phase']==0 else 'OVERLAP_UNKNOWN' if f['phase']==1 else 'SINGLE_ACTIVE_INTERVAL'
   require(f['kernel_uid']==uid and f['kernel_scope']==scope,'phase UID or scope differs')
  else:require(type(f['phase']) is int and f['phase']==-1 and f['kernel_uid'] is None and f['kernel_scope']==f['record']+'_CUMULATIVE','aggregate scope differs')
  if f['record']=='GLOBAL':require(f['slice']==self.registered,'GLOBAL registered membership differs')
  else:require(f['slice'] in self.expected,'slice outside qualified membership')
  require(isinstance(f['counters'],dict) and set(f['counters'])==COUNTERS,'exact counter set')
  for k,v in f['counters'].items():uint(v,k)
  c=f['counters'];require(total([c['covered'],c['probe_skipped']],'observed heads')==c['observed_heads'],'observed head partition')
  require(sum(c[n] for n in ('skip_tvd','skip_ideal','skip_disabled','skip_other'))==c['probe_skipped'],'skip partition')
  require(isinstance(f['histograms'],dict) and set(f['histograms'])==HIST,'exact histogram set')
  return self.cross_old(f)
 def ingest(self,f):
  self.validate_frame(f);kind=f['record'];sid=f['slice'];pid=f['phase']
  if self.pending is None:
   require(kind=='SLICE' and sid==self.expected[0],'snapshot must start first selected SLICE')
   self.pending={'slices':{},'phases':{},'global':None,'last_sid':None,'phase_next':0,'anchor':f}
  p=self.pending;a=p['anchor']
  for k in ('cycle','snapshot_seq','kernel_catalog'):require(f[k]==a[k],'mixed snapshot '+k)
  if kind=='SLICE':
   if p['last_sid'] is not None:require(p['phase_next']==len(a['kernel_catalog'])+2,'previous slice missing phase tail')
   require(sid==self.expected[len(p['slices'])] if len(p['slices'])<len(self.expected) else False,'slice order/duplicate')
   p['slices'][sid]=f;p['last_sid']=sid;p['phase_next']=0
  elif kind=='PHASE':
   require(sid==p['last_sid'] and pid==p['phase_next'],'phase order/duplicate/physical label')
   parent=p['slices'][sid];require(f['epoch_closed']==parent['epoch_closed'],'phase parent lifecycle differs')
   p['phases'][(sid,pid)]=f;p['phase_next']+=1
  else:
   require(len(p['slices'])==len(self.expected) and p['phase_next']==len(a['kernel_catalog'])+2,'incomplete snapshot before GLOBAL')
   p['global']=f;self.close_snapshot(p);self.pending=None
 def close_snapshot(self,p):
  g=p['global'];cat=g['kernel_catalog']
  for sid,f in p['slices'].items():
   children=[p['phases'][(sid,k)] for k in range(len(cat)+2)]
   self.rollup(children,f)
  self.rollup(list(p['slices'].values()),g)
  if self.registered==len(self.expected):require(g['epoch_closed']==all(x['epoch_closed'] for x in p['slices'].values()),'global lifecycle differs')
  else:require(not self.full,'inactive native population cannot full qualify')
  if self.last is not None:
   old=self.last;og=old['global'];require(g['snapshot_seq']>og['snapshot_seq'],'sequence did not advance');require(g['cycle']>=og['cycle'],'cycle regressed')
   require(cat[:len(og['kernel_catalog'])]==og['kernel_catalog'],'existing kernel mapping changed')
   if cat!=og['kernel_catalog']:require(g['cycle']>og['cycle'],'samecycle unproved catalog append')
   samecycle=g['cycle']==og['cycle'];closed_flip=False
   for key,new in self.scopes(p).items():
    if key not in self.scopes(old):continue
    before=self.scopes(old)[key];require(not before['epoch_closed'] or new['epoch_closed'],'epoch reopened')
    require(flags(new)==flags(before),'flags drift')
    if samecycle:require(content(new)==content(before),'samecycle unproved counter increase/rollback')
    else:self.monotonic(before,new)
    closed_flip|=before['epoch_closed']!=new['epoch_closed']
   if samecycle:
    if closed_flip:self.same_cycle_closures+=1
    else:self.same_cycle_duplicates+=1
  self.snapshots+=1;self.last=p
 @staticmethod
 def scopes(p):return {**{('SLICE',sid,-1):f for sid,f in p['slices'].items()},**{('PHASE',sid,pid):f for (sid,pid),f in p['phases'].items()},('GLOBAL',p['global']['slice'],-1):p['global']}
 @staticmethod
 def rollup(children,parent):
  c,hs=add_frames(children);require(c==parent['counters'],'counter phase/slice/global rollup')
  for n in DIMS:require(hs[n]==sparse_dict(parent,n),'histogram phase/slice/global rollup '+n)
 @staticmethod
 def monotonic(old,new):
  for n,v in old['counters'].items():require(new['counters'][n]>=v,'counter regressed '+n)
  for n in DIMS:
   now=sparse_dict(new,n)
   for key,v in sparse_dict(old,n).items():require(now.get(key,0)>=v,'cumulative bin regressed '+n)
 def finish(self,old212_result):
  try:
   require(self.error is None,'sticky r5 error: '+str(self.error));require(self.pending is None,'partial latest r5 tail; no fallback');require(self.last is not None,'no complete r5 snapshot')
   require(isinstance(old212_result,dict),'fixed212 result absent');status='SYNTHETIC_OBSERVER_CONTROL_ONLY' if self.synthetic else 'VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY';require(old212_result.get('status')==status,'fixed212 validation did not pass')
   require(len(old212_result.get('schema_counter_fields',[]))==212,'fixed212 exact212 schema absent')
   p=self.last;g=p['global'];require(g['kernel_catalog']==self.kernels,'final full input kernel catalog incomplete')
   require(g['cycle']==old212_result.get('final_cycle'),'r4/r5 final cycle differs')
   for f in self.scopes(p).values():self.cross_old(f)
   require(g['counters']['observed_heads']==old212_result['global_counters']['observed_heads'],'old212 final result differs')
   for sid,f in p['slices'].items():
    require(f['epoch_closed'],'selected slice terminal epoch open')
    require(f['counters']['observed_heads']==old212_result['slice_counters'][str(sid)]['observed_heads'],'old212 final selected differs')
   if self.full:require(g['epoch_closed'],'fullapp global terminal epoch open')
   return {'status':'R5_SYNTHETIC_CONTROL_ONLY' if self.synthetic else 'VALID_R5_OBSERVER_DECLARATIONS_ONLY','full_application_qualified':False,'scientific_acceptance_granted':False,'schema_sha256':SCHEMA_SHA256,'fixed_r4_decoder_sha256':FIXED_R4_SHA256,'source_binding_external':self.binding,'full_application_mode':self.full,'selected_slices':self.expected,'registered_slice_count':self.registered,'final_cycle':g['cycle'],'snapshot_count':self.snapshots,'same_cycle_identical_snapshots':self.same_cycle_duplicates,'same_cycle_metadata_closures':self.same_cycle_closures,'input_bytes':self.input_bytes,'r5_bytes':self.observer_bytes,'r5_stream_sha256':self.stream_sha.hexdigest(),'global_record':g,'slice_records':{str(k):v for k,v in p['slices'].items()},'phase_records':{str(k)+':'+str(pidx):v for (k,pidx),v in p['phases'].items()},'limits':['physical phase is event-time label, not requester/victim causal owner','NA remains explicit; old212 must independently pass','native selected population does not certify fullGPU64','normal exit/instructions/drain/input/qualification/resources remain outside decoder']}
  except (AuditError,KeyError,ValueError,TypeError) as e:return {'status':'INVALID_R5','reason':str(e),'full_application_qualified':False,'scientific_acceptance_granted':False,'input_bytes':self.input_bytes,'r5_bytes':self.observer_bytes}

class TappingReader:
 """Pass unchanged readline bytes through an independently-bound fixed r4 parser."""
 def __init__(self,stream,feed):self.stream=stream;self.feed=feed
 def readline(self,limit):
  line=self.stream.readline(limit)
  if line:self.feed.feed(line)
  return line
