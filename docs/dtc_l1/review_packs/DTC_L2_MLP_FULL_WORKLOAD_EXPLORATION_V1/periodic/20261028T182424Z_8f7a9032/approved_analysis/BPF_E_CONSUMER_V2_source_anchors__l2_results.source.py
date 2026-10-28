"""Closed-result consumer and matched-population summaries; never starts a model."""
import pathlib,json,hashlib,importlib.util,os,time,math,statistics,datetime
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
PASS='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'
REUSE='REFERENCE_ACCEPTED_NO_NEW_START'

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,f):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x')as h:json.dump(x,h,indent=2,sort_keys=True);h.write('\n');h.flush();os.fsync(h.fileno())
 else:
  tmp=p.with_name(p.name+'.'+str(os.getpid())+'.L2writing')
  tmp.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');tmp.replace(p)

def archive_closed(c):
 o=load('l2_results_archive','l2_outbox.py');began=time.monotonic()
 while True:
  if(R/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists():return o.verify(c)
  try:o.archive(c)
  except BlockingIOError:
   assert time.monotonic()-began<21600;time.sleep(10)
  except RuntimeError as x:
   if 'HOLD'not in str(x)or time.monotonic()-began>=21600:raise
   time.sleep(10)

def finish_evidence(c):
 """Postprocess one DONE, preserving raw failures and never resubmitting it."""
 rp=R/'analysis'/(c+'.RESULT.json')
 if rp.exists():return read(rp)
 e=load('l2_finish_engine','l2_native.py');q=e.registered()[2]
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);d=read(ip.with_name(c+'.DONE.json'));out=P(i['output'])
 assert d==q['consumed'][c]['execution_receipt']==read(out/'NATIVE_EXIT.json') and i['uuid']==d['uuid']
 assert q['consumed'][c]['intent_sha256']==sha(ip) and sha(out/'raw.log.gz')==d['raw_sha256']
 failed=bool(d['stop_reason']or d['launcher_wait_returncode'])
 if failed:
  proof=dict(status='L2_MLP_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=d['stop_reason'],returncode=d['launcher_wait_returncode'],accepted_cycles=None,raw_sha256=d['raw_sha256'],performance_accepted=False)
 else:
  proof=load('l2_whole_input_strict','l2_strict.py').terminal(c);p=out/'L2_STRICT.json'
  if p.exists():assert read(p)==proof
  else:put(p,proof,True)
  qual=dict(status='L2_MLP_NATIVE_TRACE_PERFORMANCE_QUALIFIED',cohort=c,uuid=d['uuid'],strict_sha256=sha(p),performance_scope='NEW_L2_MLP_ONLY_NEVER_ORIGINAL',SOURCE_KEEP=True)
  p=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json')
  if p.exists():assert read(p)==qual
  else:put(p,qual,True)
 a=archive_closed(c)
 v=dict(state='FAIL_L2MLP_ARCHIVED_NO_RETRY'if failed else PASS,cohort=c,uuid=d['uuid'],cycles=None if failed else proof['cycles'],proof=proof,archive=a,new_contract_only=True,original_or_repair_results_replaced=False)
 if rp.exists():assert read(rp)==v
 else:put(rp,v,True)
 return v

def safe_finish(c):
 try:return finish_evidence(c)
 except BaseException as x:
  v=dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,error=repr(x),model_retries=0,accepted_cycles=None)
  # A distinct engineering event is retained. It is not a performance result and
  # does not prevent a later engineering-only completion of the same raw UUID.
  p=R/'analysis'/(c+'.POSTPROCESS_ENGINEERING.'+str(time.time_ns())+'.json');put(p,v,True);return v

def accepted(v):
 if v.get('state')not in[PASS,REUSE]:return False
 p=v.get('proof',{})
 if p.get('performance_accepted')is not True or type(v.get('cycles'))is not int or v['cycles']<=0:return False
 if v.get('state')==REUSE:
  r=v.get('reuse_verification',{})
  # Main coordinator emits this only after independently checking source strict,
  # natural DONE, archive/native restore, complete option and build equality.
  return all(r.get(k)is True for k in['strict_verified','natural_done_verified','archive_native_restore_verified','complete_effective_options_equal','core_framework_binary_equal','input_scope_equal'])
 return p.get('cycles')==v['cycles'] and bool(v.get('archive'))

def dist(rows,expected):
 """rows: identity,value; explicit population and missing counts for every GM."""
 vals=[x['value']for x in rows]
 return dict(n=len(vals),expected_n=expected,missing_n=expected-len(vals),GM=math.exp(sum(math.log(v)for v in vals)/len(vals))if vals else None,median=statistics.median(vals)if vals else None,positive=sum(v>1 for v in vals),neutral=sum(v==1 for v in vals),negative=sum(v<1 for v in vals),minimum=min(vals)if vals else None,maximum=max(vals)if vals else None,population=[x['input_digest']for x in rows],values=rows)

def counters(proof):
 """Convenience projection only; absent evidence remains None, never zero."""
 traffic=proof.get('traffic',{});metrics=proof.get('metrics',{});b=traffic.get('L2_buckets',{})
 miss=[v for k,v in b.items()if k.partition(':')[0].endswith('_R') and k.partition(':')[2]in['MISS','SECTOR_MISS']]
 reject=[v for k,v in b.items()if k.partition(':')[0].endswith('_R') and k.partition(':')[2]=='RESERVATION_FAIL']
 mshr={k:v for k,v in metrics.items()if 'l2'in k.lower()and'mshr'in k.lower()}
 return dict(L2_accepted_read_32B_sectors=traffic.get('L2_accepted_read_32B_sectors'),L2_accepted_read_miss_32B_sectors=sum(miss)if miss else None,L2_read_reservation_fail_attempts=sum(reject)if reject else None,L2_read_payload_bytes=traffic.get('L2_read_payload_bytes'),DRAM_issued_read_atoms=traffic.get('DRAM_issued_read_atoms'),DRAM_read_payload_bytes=traffic.get('DRAM_read_payload_bytes'),DRAM_issued_write_atoms=traffic.get('DRAM_issued_write_atoms'),DRAM_write_payload_bytes=traffic.get('DRAM_write_payload_bytes'),L2_visible_MSHR_counters=mshr or None,gpu_stall_dramfull=metrics.get('gpu_stall_dramfull'),L2_total_cache_reservation_fails=metrics.get('L2_total_cache_reservation_fails'),counter_notes='MISS+SECTOR_MISS read buckets; reservations are rejected attempts, not unique requests. gpu_stall_dramfull retains native unit. No missing counter is zero-filled.')

def summarize(scope,records):
 """Exact identity, common accepted cohorts. No live/raw files, no best-of GM."""
 table={};programs={};profiles=[];pointids=set()
 for p in scope['points']:
  c=p['cohort'];assert c not in pointids;pointids.add(c)
  digest=p['input_digest'];profile=p['profile'];cell=p['cell'];assert cell in['CH','DH']
  if profile not in profiles:profiles.append(profile)
  name=p['program'];suite=p.get('suite','UNKNOWN');old=programs.setdefault(digest,dict(program=name,suite=suite,input_digest=digest))
  assert old==dict(program=name,suite=suite,input_digest=digest)
  v=records.get(c,{})
  slot=table.setdefault(digest,{}).setdefault(profile,{})
  assert cell not in slot
  slot[cell]=dict(cohort=c,state=v.get('state','PENDING'),accepted=accepted(v),cycles=v.get('cycles')if accepted(v)else None,uuid=v.get('uuid'),counters=counters(v.get('proof',{}))if accepted(v)else None,metrics=v.get('proof',{}).get('metrics',{})if accepted(v)else {},traffic=v.get('proof',{}).get('traffic',{})if accepted(v)else {},latency_counters=v.get('proof',{}).get('latency_counters',{})if accepted(v)else {})
 def cyc(d,p,c):return table[d].get(p,{}).get(c,{}).get('cycles')
 comparisons={};aggregates={};suites=sorted({v['suite']for v in programs.values()})
 for d in table:
  comparison={}
  for p in profiles:
   a,b,c,f=cyc(d,'P0','CH'),cyc(d,'P0','DH'),cyc(d,p,'CH'),cyc(d,p,'DH')
   sch=a/c if a and c else None;sdh=b/f if b and f else None
   comparison[p]=dict(CH_speedup=sch,DH_speedup=sdh,relative_DTC_improvement=sdh/sch if sdh and sch else None,CH_over_DH=c/f if c and f else None,matched_quad=bool(a and b and c and f))
  comparisons[d]=dict(**programs[d],profiles=comparison)
 for p in profiles:
  groups={}
  for group in['ALL']+suites:
   ids=[d for d,v in programs.items()if group=='ALL'or v['suite']==group]
   gm={}
   for k in['DH_speedup','CH_speedup','relative_DTC_improvement','CH_over_DH']:
    rows=[dict(input_digest=d,program=programs[d]['program'],value=comparisons[d]['profiles'][p][k])for d in ids if comparisons[d]['profiles'][p][k]is not None]
    gm[k]=dist(rows,len(ids))
   common=[d for d in ids if comparisons[d]['profiles'][p]['matched_quad']]
   gm['common_matched_quad']={k:dist([dict(input_digest=d,program=programs[d]['program'],value=comparisons[d]['profiles'][p][k])for d in common],len(ids))for k in['DH_speedup','CH_speedup','relative_DTC_improvement','CH_over_DH']}
   groups[group]=gm
  aggregates[p]=groups
 states=[records.get(p['cohort'],{}).get('state','PENDING')for p in scope['points']]
 return dict(schema='DTC_L2_MLP_AUTO_SUMMARY_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),expected_input_count=len(table),target_programs=42,unresolved_programs=scope.get('unresolved_programs',[]),profiles=profiles,programs=programs,table=table,comparisons=comparisons,aggregates=aggregates,no_missing_imputation=True,no_per_program_best_GM=True,population_policy='Per-metric paired accepted population explicit; all four metrics also provided on identical common_matched_quad',performance_scope='NEW_L2_MLP_ONLY_PLUS_PROVEN_MATCHED_P0',state_counts={s:states.count(s)for s in sorted(set(states))})

def summary():
 base=R/'control/SCOPE.json';scope=read(base);matrix=R/'control/MATRIX_CURRENT.json'
 if matrix.exists():
  current=read(matrix);assert current['base_scope_sha256']==sha(base)
  assert type(current['revision'])is int and current['revision']>=0
  assert isinstance(current['points'],list)
  # Every initial scientific identity survives future search revisions unchanged.
  current_points={p['cohort']:p for p in current['points']}
  assert len(current_points)==len(current['points'])
  for p in scope['points']:assert current_points.get(p['cohort'])==p
  scope=dict(scope,**current)
 records={}
 for p in scope['points']:
  rp=R/'analysis'/(p['cohort']+'.RESULT.json')
  if rp.exists():records[p['cohort']]=read(rp)
 out=summarize(scope,records);put(R/'analysis/AUTO_SUMMARY.json',out);return out

if __name__=='__main__':
 import sys
 if len(sys.argv)==2:print(json.dumps(safe_finish(sys.argv[1]),indent=2))
 else:print(json.dumps(summary(),indent=2))
