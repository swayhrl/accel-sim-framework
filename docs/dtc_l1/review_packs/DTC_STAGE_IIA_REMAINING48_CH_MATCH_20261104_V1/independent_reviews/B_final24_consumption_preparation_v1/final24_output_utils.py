from pathlib import Path
import json,gzip,hashlib
RAW_PART_LIMIT=4*1024**2;PUBLISHED_MEMBER_LIMIT=8*1024**2;MAX_RECORD_BYTES=1024**2
class ChunkedJSONL:
 """At most4MiB raw bytes per gzip part; every closed published part is checked<8MiB."""
 def __init__(self,root,prefix,raw_limit=RAW_PART_LIMIT):
  self.root=Path(root);self.prefix=prefix;self.raw_limit=raw_limit;self.parts=[];self.f=None;self.z=None;self.raw_bytes=0;self.rows=0;self.total_rows=0
 def _open(self):
  self.root.mkdir(parents=True,exist_ok=True);self.path=self.root/(self.prefix+'.part'+str(len(self.parts)).zfill(4)+'.jsonl.gz');self.f=self.path.open('xb');self.z=gzip.GzipFile(fileobj=self.f,mode='wb',compresslevel=6,mtime=0);self.raw_bytes=0;self.rows=0
 def write(self,row):
  b=(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()
  if len(b)>MAX_RECORD_BYTES or len(b)>self.raw_limit:raise ValueError('SINGLE_DETAIL_ROW_TOO_LARGE; retain evidence and report HOLD, never truncate')
  if self.z is not None and self.raw_bytes+len(b)>self.raw_limit:self._close()
  if self.z is None:self._open()
  self.z.write(b);self.raw_bytes+=len(b);self.rows+=1;self.total_rows+=1
 def _close(self):
  if self.z is None:return
  self.z.close();self.f.close();n=self.path.stat().st_size
  if n>=PUBLISHED_MEMBER_LIMIT:raise ValueError('PUBLISHED_MEMBER_GE8MiB; no publication')
  self.parts.append({'path':str(self.path),'bytes':n,'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),'jsonl_rows':self.rows,'uncompressed_bytes':self.raw_bytes});self.z=None;self.f=None
 def close(self):self._close();return self.parts

def require_final_provider(provider):
 s=provider.get('summary',{})
 if not(provider.get('schema')=='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1'and provider.get('request')=='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'and provider.get('source_qualified')is True and provider.get('all_registered48_terminal_verified')is True and s.get('accepted_CH',0)+s.get('archived_negative_CH',0)==48 and s.get('verification_hold')==s.get('await_result')==s.get('registered_remaining')==0 and s.get('registered_consumed')==48):raise ValueError('AWAIT_ALL48_QUALIFIED_NATURAL_TERMINAL; no early scan or force bypass')

def selector_index(mapping,counts):
 out={}
 for digest,p in mapping['programs'].items():
  idx={}
  for phase in p['phases']:
   q=phase['kernel_ordinals'];ords=range(q['first'],q['last_inclusive']+1,q['step'])
   if len(ords)!=q['count']:raise ValueError('PHASE_SELECTOR_COUNT_MISMATCH')
   for ordinal in ords:
    if ordinal in idx:raise ValueError('OVERLAPPING_PHASE_SELECTORS')
    idx[ordinal]={'phase_id':phase['phase_id'],'source_stage':phase['source_stage'],'phase_evidence':'FIXED_SOURCE_CANDIDATE_AND_TRACE_SELECTOR_NOT_CAPTURE_ELF_CERTIFIED'}
  if set(idx)!=set(range(1,counts[digest]+1)):raise ValueError('PHASE_SELECTORS_NOT_EXACT_COVERAGE')
  out[digest]=idx
 return out

def phase_fold(bucket,kernel):
 bucket['kernel_count']+=1;bucket['cycles_sum']+=kernel['cycles']
 # Only parser-certified additive endpoint deltas enter grouped sums. Snapshots/means never enter.
 for key,value in kernel['print_interval_additive'].items():
  b=bucket['additive'].setdefault(key,{'observed':0,'observed_sum':0})
  if value is not None:b['observed']+=1;b['observed_sum']+=value

def complete_phase(bucket):
 return dict(kernel_count=bucket['kernel_count'],cycles_sum=bucket['cycles_sum'],additive={k:{'observed_kernel_intervals':v['observed'],'missing_kernel_intervals':bucket['kernel_count']-v['observed'],'value':v['observed_sum']if v['observed']==bucket['kernel_count']else None,'status':'COMPLETE_EXPLICIT_ENDPOINT_SUM'if v['observed']==bucket['kernel_count']else'MISSING_ENDPOINT_NOT_ZERO'}for k,v in bucket['additive'].items()},scope='Completed-kernel print intervals, not request-origin assignment. No mean/gauge/peak differencing or summation.')
