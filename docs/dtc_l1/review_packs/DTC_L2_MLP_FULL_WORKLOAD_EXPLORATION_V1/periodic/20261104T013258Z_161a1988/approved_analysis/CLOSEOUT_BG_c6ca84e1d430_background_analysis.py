"""Standalone read-only analysis worker; no Git, model launch or model signals."""
import argparse,contextlib,datetime,fcntl,hashlib,importlib.util,json,os,pathlib,sys,time,uuid,csv,io,html,gzip,urllib.request
import readable_report
import ready_emitter
import analysis_extensions as ext
sys.dont_write_bytecode=True
P=pathlib.Path
SCHEMA='DTC_BACKGROUND_ANALYSIS_CONFIG_V1'
def rawjson(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def read(p):return json.loads(P(p).read_bytes())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def coherent(p):
 with P(p).open('rb') as h:
  a=os.fstat(h.fileno());b=h.read();z=os.fstat(h.fileno())
 assert (a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_ino,z.st_size,z.st_mtime_ns) and len(b)==z.st_size,'SOURCE_WRITE_RACE'
 return b,json.loads(b)
def atomic(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex)
 b=v if isinstance(v,bytes) else rawjson(v)
 with tmp.open('xb') as h:h.write(b);h.flush();os.fsync(h.fileno())
 os.replace(tmp,p);fd=os.open(p.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
@contextlib.contextmanager
def lock(p):
 with P(p).open('a+b') as h:
  fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:yield
  finally:fcntl.flock(h,fcntl.LOCK_UN)
def load(path,expected):
 assert sha(path)==expected,'PINNED_SOURCE_DRIFT '+str(path)
 m=importlib.util.module_from_spec(s:=importlib.util.spec_from_file_location('qualified_derived35',path));s.loader.exec_module(m);return m
def audit(event,args):
 if event=='subprocess.Popen' or event.startswith('os.exec') or event in ('os.system','os.kill','os.killpg'):
  raise RuntimeError('ANALYSIS_NO_SUBPROCESS_OR_SIGNAL')
def terminal_delta(initial,current):
 for c,h in initial.items():assert current.get(c)==h,'PREVIOUS_RESULT_MUTATED '+c
 return sorted(set(current)-set(initial))
def original_summary(mod,value,consumer):
 rows=[dict(key=r['key'],selected=r['original'] if r['original']['valid'] else None) for r in value['rows']]
 return mod.summarize(consumer.scope['points'],rows,consumer.contract['profiles'],value['summary']['formal_GM_generated'])
def render_table(v,original,closed=None,certificates=None):
 closed=closed or {};certificates=certificates or {}
 buf=io.StringIO();w=csv.writer(buf);w.writerow(['input_digest','program','suite','cell','profile','original_cohort','original_state','original_valid','original_cycles','named_selected_cohort','named_source_role','named_cycles','selection_reason','missing_reason','closed_not_accepted_status','closed_DONE_sha256','original_typed_negative_certificate_sha256'])
 for r in v['rows']:
  s=r['selected'];k=r['key'];o=r['original'];w.writerow([k['input_digest'],k['program'],k['suite'],k['cell'],k['profile'],r['original_cohort'],o['raw_state'],o['valid'],o['cycles'] if o['valid'] else '',s['cohort'] if s else '',s['scientific_role'] if s else '',s['cycles'] if s else '',r['reason'],'; '.join(o['reasons']),closed.get(r['original_cohort'],{}).get('status',''),closed.get(r['original_cohort'],{}).get('DONE_sha256',''),certificates.get(r['original_cohort'],{}).get('sha256','')])
 return buf.getvalue().encode()
def compact_summary(summary):
 fields=['analysis_namespace','formal_GM_generated','no_ledger_union','no_runtime_parent_or_adoption','no_role_mutation','no_missing_imputation','expected_inputs','expected_original_slots','selected_measurement_references','missing_slots']
 out={k:summary[k] for k in fields};out['aggregates']={}
 for profile,suites in summary['aggregates'].items():
  out['aggregates'][profile]={}
  for suite,metrics in suites.items():
   out['aggregates'][profile][suite]={}
   for metric,populations in metrics.items():
    out['aggregates'][profile][suite][metric]={name:{k:v for k,v in row.items() if k not in ('population','values')} for name,row in populations.items()}
 out['full_per_input_populations_values_and_source_pins']='REPORT.json.gz; lossless full evidence retained'
 return out
def report_html(v,original):
 def table(summary):
  rows=[]
  for p,suites in summary['aggregates'].items():
   for suite,metrics in suites.items():
    for metric,pops in metrics.items():
     for name,x in pops.items():rows.append('<tr>'+''.join('<td>'+html.escape(str(z))+'</td>' for z in [p,suite,metric,name,x['n'],x['expected_n'],x['GM'] if x['GM'] is not None else 'NOT_RELEASED'])+'</tr>')
  return '<table><tr><th>Profile</th><th>Suite</th><th>Metric</th><th>Population</th><th>n</th><th>Expected</th><th>GM</th></tr>'+''.join(rows)+'</table>'
 return ('<!doctype html><meta charset="utf-8"><title>Read-only long-tail analysis</title><style>body{font:14px sans-serif;margin:2em}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px}</style><h1>Frozen35 analysis</h1><p>UTC '+html.escape(v['UTC'])+'; original 350 slots and separately named measurement references. Missing remains missing; no performance selection, role mutation, runtime adoption or new trial. Metric populations are explicitly labelled; full35 requires n=35. Missing hardware counters are unavailable, never zero.</p><h2>Original 350</h2>'+table(original)+'<h2>Independent named Derived35</h2>'+table(v['summary'])+'<p><a href="results.csv">Every slot/source role</a> ? <a href="REPORT.json">All per-input paired ratios, coverage and source pins</a></p>').encode()
class Worker:
 def __init__(self,cfg,config_path):
  assert cfg['schema']==SCHEMA;self.c=cfg;self.config_path=P(config_path);self.config_sha=sha(config_path)
  a=P(cfg['archive_root']).resolve();self.out=P(cfg['output_root']).resolve();assert self.out.is_relative_to(a),'ALL_WRITES_MUST_BE_164'
  assert cfg['poll_seconds']>=30;self.out.mkdir(parents=True,exist_ok=True);self.statepath=self.out/'STATE.json'
  self.state=read(self.statepath) if self.statepath.exists() else {'known_results':{},'last_signature':None,'status':'NEW'}
  self.mod=load(cfg['consumer_path'],cfg['consumer_sha256'])
  for p,h in cfg['source_pins'].items():assert sha(p)==h,'CONFIG_SOURCE_PIN_DRIFT '+p
  self.scope=read(cfg['registered_scope_path']);assert sha(cfg['registered_scope_path'])==cfg['registered_scope_sha256'];self.registered=set(self.scope['admitted_cohorts']);assert len(self.registered)==360
 def save(self,**kw):self.state.update(kw,UTC=utc());atomic(self.statepath,self.state)
 def registry(self):
  _,v=coherent(self.c['registry_path']);q=v['registered_future_requests'][self.c['request']]
  assert set(q['admitted_specs'])==self.registered,'REGISTERED_SCOPE_CHANGED_REVIEW_REQUIRED'
  assert type(q['remaining']) is int and q['remaining']>=0,'MISSING_OR_INVALID_REMAINING_COUNTER'
  return q
 def snapshot_results(self):
  identities={};values={}
  for c in sorted(set(self.scope['all_watch_cohorts'])):
   p=P(self.c['root'])/'analysis'/(c+'.RESULT.json')
   if p.exists():b,v=coherent(p);identities[c]=digest(b);values[c]=v
  terminal_delta(self.state['known_results'],identities)
  return identities,values
 def snapshot_closed(self,identities):
  closed={}
  for c in sorted(self.registered-set(identities)):
   p=P(self.c['root'])/'control/qualification_ledger'/(c+'.DONE.json')
   if p.exists():
    raw,v=coherent(p);closed[c]={'status':'CLOSED_DONE_PRESENT_NOT_ACCEPTED','DONE_sha256':digest(raw),'uuid':v.get('uuid'),'stop_reason':v.get('stop_reason'),'launcher_wait_returncode':v.get('launcher_wait_returncode'),'native_simulator_observed':v.get('native_simulator_observed'),'performance_accepted':False}
  return closed
 def final_receipt(self,pointer):
  # Existing publisher verifies every Git member before push. Candidate adapter
  # additionally puts every provider member in its HTTPS checks.
  state=read(self.c['publisher_state_path']);proof=state.get('last_success')
  if not proof or proof.get('status')!='PUSH_LSREMOTE_AND_HTTPS_VERIFIED':return None
  found={x.get('sha256') for x in proof.get('files',{}).values()}
  manifest=read(pointer['manifest_path']);required={x['sha256'] for x in manifest['publication_files']}
  # Existing publisher HTTPS verifies the snapshot member manifest, which binds
  # approved file bytes; read the local, hash-verified manifest named in proof.
  snapshot=state.get('last_snapshot')
  if not snapshot:return None
  mp=P(snapshot)/'MEMBER_MANIFEST.json'
  if not mp.exists() or sha(mp) not in found:return None
  members=read(mp)['files'];published={x['sha256'] for k,x in members.items() if k.startswith('approved_analysis/AUTO_DERIVED35_V1_')}
  if not required<=published:return None
  entry=next((x for k,x in proof['files'].items() if k.endswith('/MEMBER_MANIFEST.json')),None)
  if not entry:return None
  checks={}
  for x in manifest['publication_files']:
   url=entry['url'].rsplit('/',1)[0]+'/approved_analysis/'+x['name']
   with urllib.request.urlopen(url,timeout=20) as h:b=h.read(1048577)
   assert len(b)<=1048576 and digest(b)==x['sha256'],'FINAL_ANALYSIS_HTTPS_READBACK_MISMATCH'
   checks[x['name']]={'url':url,'sha256':digest(b)}
  return dict(proof,analysis_exact_HTTPS_checks=checks)
 def tick(self):
  assert sha(self.config_path)==self.config_sha,'CONFIG_CHANGED_RESTART_REQUIRED'
  for p,h in self.c['source_pins'].items():assert sha(p)==h,'CONFIG_SOURCE_PIN_DRIFT '+p
  q=self.registry();identities,rawvalues=self.snapshot_results()
  closed=self.snapshot_closed(identities)
  neg_policy=ext.policy(self.c);negative_states={}
  if neg_policy is not None:assert set(neg_policy['scope'])<=self.registered,'NEGATIVE_POLICY_SCOPE_EXPANSION'
  for cohort,raw in sorted(rawvalues.items()):
   if cohort in self.registered and cohort not in self.scope['baseline_terminal_results'] and raw.get('state')=='FAIL_L2MLP_ARCHIVED_NO_RETRY':
    try:negative_states[cohort]=ext.negative_terminal(cohort,raw,self.c['root'],q,neg_policy)
    except (ValueError,KeyError,TypeError,OSError) as error:negative_states[cohort]={'terminal':False,'accepted':False,'cycles':None,'hold':str(error)}
  historical=ext.historical(self.c,self.state.get('historical_previous'))
  receipt=self.c.get('publication_receipt_path');formal=bool(receipt and P(receipt).exists())
  signature=digest(rawjson({'RESULTs':identities,'closed_not_accepted':closed,'negative_terminal_states':negative_states,'historical_signature':historical['signature'],'formal_receipt':sha(receipt) if formal else None,'remaining':q['remaining']}))
  if signature==self.state.get('last_signature') and (self.out/'LATEST.json').exists():
   pointer=read(self.out/'LATEST.json');self.emit(pointer);proof=self.final_receipt(pointer)
   if self.state.get('tail_complete') and pointer['formal_metrics'] and proof:self.save(status='COMPLETE_REGISTERED_TAIL_FINAL_REPORT_REMOTE_VERIFIED',final_publication=proof);return True
   return False
  consumer=self.mod.ReadonlyConsumer();value=consumer.run(publication_receipt=receipt if formal else None,qualification=self.c['qualification_path'] if formal else None)
  original=original_summary(self.mod,value,consumer)
  # Validate all small source pins a second time. A race is retried, never filled.
  for item in value['source_pins']:assert sha(item['path'])==item['sha256'],'SOURCE_CHANGED_DURING_ANALYSIS '+item['path']
  after,_=self.snapshot_results();assert identities==after,'RESULT_CHANGED_DURING_ANALYSIS'
  for negative in negative_states.values():
   for path,h in negative.get('source_pins',{}).items():assert sha(path)==h,'NEGATIVE_SOURCE_CHANGED_DURING_ANALYSIS'
  assert closed==self.snapshot_closed(after),'DONE_CHANGED_DURING_ANALYSIS'
  q2=self.registry();assert q['remaining']==q2['remaining'],'ADMISSION_MOVED_DURING_ANALYSIS'
  valid={x['cohort'] for r in value['rows'] for x in [r['original'],r['alternate']] if x and x.get('valid')}
  baseline=self.scope['baseline_terminal_results'];blocked=[]
  certificates=self.scope.get('baseline_terminal_certificates',{})
  for c,x in certificates.items():assert sha(x['path'])==x['sha256'],'FROZEN_TERMINAL_CERTIFICATE_CHANGED'
  for c in sorted(self.registered):
   if c in certificates:continue
   if c in baseline and identities.get(c)==baseline[c]:continue
   if c in valid or negative_states.get(c,{}).get('terminal') is True:continue
   blocked.append(c)
  dtc_complete=q['remaining']==0 and not blocked
  historical_complete=historical['completion']['all_fixed_objects_terminal'] if historical['configured'] else None
  complete=dtc_complete and (historical_complete if historical['configured'] else True)
  token=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+uuid.uuid4().hex[:8];d=self.out/'runs'/token;d.mkdir(parents=True)
  changed=terminal_delta(self.state['known_results'],identities)
  event={'schema':'DTC_ANALYSIS_IMMUTABLE_EVENT_V1','UTC':utc(),'new_RESULT_cohorts':changed,'RESULT_sha256':identities,'closed_not_accepted':closed,'negative_terminal_states':negative_states,'historical_signature':historical['signature'],'previous_signature':self.state.get('last_signature'),'signature':signature,'registry_remaining':q['remaining'],'fixed_registered_scope_sha256':self.c['registered_scope_sha256'],'candidate_CH35_not_registered_not_complete_claimed':True}
  report={'schema':'DTC_BACKGROUND_ANALYSIS_REPORT_V1','event':event,'derived35':value,'original350_summary':original,'coverage':{'original_valid':original['selected_measurement_references'],'original_slots':350,'derived35_selected':value['summary']['selected_measurement_references'],'registered_raw_budget':360,'runtime_display_population':len(self.scope['all_watch_cohorts']),'unresolved_registered':blocked,'registered_tail_complete':dtc_complete,'historical_fixed3_configured':historical['configured'],'historical_fixed3_complete':historical_complete,'all_authorized_populations_complete':complete,'closed_not_accepted':closed,'negative_terminal_states':negative_states,'original_terminal_certificates':certificates},'historical_fixed3':historical,'hardware_counters':{'availability':'NOT_COLLECTED_BY_THIS_ANALYSIS','missing_value':None,'missing_means_zero':False},'performance_selection':False,'scientific_role_changes':False,'new_models':0}
  atomic(d/'RESULTS.md',readable_report.render(report));atomic(d/'REPORT.json',report);atomic(d/'EVENT.json',event);atomic(d/'results.csv',render_table(value,original,closed,certificates));atomic(d/'dashboard.html',report_html(value,original));atomic(d/'SOURCE_PINS.json',{'daemon_sha256':sha(__file__),'config_sha256':self.config_sha,'consumer_source_pins':value['source_pins'],'source_transaction':'PER_FILE_PINNED_RECHECK_NO_GLOBAL_ATOMIC_TRANSACTION'})
  manifest={'schema':'DTC_ANALYSIS_RUN_MEMBER_MANIFEST_V1','run':token,'formal_metrics':formal,'registered_tail_complete':dtc_complete,'all_authorized_populations_complete':complete,'historical_fixed3_complete':historical_complete,'files':{p.name:{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(d.iterdir()) if p.is_file()}}
  atomic(d/'REPORT.json.gz',gzip.compress((d/'REPORT.json').read_bytes(),mtime=0));atomic(d/'results.csv.gz',gzip.compress((d/'results.csv').read_bytes(),mtime=0))
  summary={'UTC':value['UTC'],'coverage':report['coverage'],'formal_metrics':formal,'original350_summary':compact_summary(original),'named35_summary':compact_summary(value['summary']),'historical_fixed3':historical,'CH35_status':'NOT_REGISTERED_HOLD_NO_GRANT','namespace_roles_unchanged':True}
  # Per-input complete metrics remain losslessly in REPORT.json.gz.
  atomic(d/'SUMMARY.json.gz',gzip.compress(rawjson(summary),mtime=0))
  manifest['publication_files']=[{'name':ready_emitter.PREFIX+n,'path':str(d/n),'sha256':sha(d/n)} for n in ['REPORT.json.gz','results.csv.gz','SUMMARY.json.gz','RESULTS.md']]
  assert sum(P(x['path']).stat().st_size for x in manifest['publication_files'])<=1048576,'PUBLICATION_NAMESPACE_PAYLOAD_TOO_LARGE'
  atomic(d/'MANIFEST.json',manifest)
  pointer={'schema':'DTC_ANALYSIS_PROVIDER_LATEST_V1','run':token,'manifest_path':str(d/'MANIFEST.json'),'manifest_sha256':sha(d/'MANIFEST.json'),'registered_tail_complete':dtc_complete,'all_authorized_populations_complete':complete,'historical_fixed3_configured':historical['configured'],'historical_fixed3_complete':historical_complete,'formal_metrics':formal,'UTC':utc()}
  atomic(self.out/'LATEST.json',pointer)
  self.emit(pointer)
  # Immutable EVENT.json is authoritative event stream; index is disposable.
  self.save(status='WAIT_FINAL_PUBLICATION' if complete else 'WATCHING_REGISTERED_TAIL',known_results=identities,last_signature=signature,last_run=token,tail_complete=complete,historical_previous=historical if historical['configured'] else None,latest=pointer)
  return False
 def emit(self,pointer):
  auth=self.c.get('ready_authorization_path')
  if not auth or not P(auth).exists():return {'status':'AWAIT_ROOT_AUTHORIZATION_NO_READY_WRITE'}
  auth_sha=sha(auth)
  if self.state.get('authorized_AUTH_sha256'):assert self.state['authorized_AUTH_sha256']==auth_sha,'ROOT_AUTHORIZATION_CHANGED_REVIEW_REQUIRED'
  else:self.save(authorized_AUTH_sha256=auth_sha)
  m=read(pointer['manifest_path']);assert sha(pointer['manifest_path'])==pointer['manifest_sha256']
  return ready_emitter.emit(self.c['analysis_ready_path'],auth,self.out/'EMITTER_STATE.json',m['publication_files'],pointer,__file__,self.config_path,self.c.get('publication_receipt_path'))
 def recover(self):
  p=self.out/'LATEST.json'
  if not p.exists():return
  pointer=read(p);mp=P(pointer['manifest_path']);assert sha(mp)==pointer['manifest_sha256'];m=read(mp)
  for x in m['files'].values():assert sha(x['path'])==x['sha256'],'RECOVERY_MEMBER_DRIFT'
  e=read(mp.parent/'EVENT.json')
  if self.state.get('last_signature')!=e['signature']:
   self.save(status='RECOVERED_PUBLISHED_RUN',known_results=e['RESULT_sha256'],last_signature=e['signature'],tail_complete=pointer.get('all_authorized_populations_complete',pointer['registered_tail_complete']),historical_previous=read(mp.parent/'REPORT.json').get('historical_fixed3') if pointer.get('historical_fixed3_configured') else None,latest=pointer,last_run=pointer['run'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--once',action='store_true');args=ap.parse_args();cfg=read(args.config)
 # No shell, Git, subprocess or signals are part of this process.
 sys.addaudithook(audit);w=Worker(cfg,args.config)
 with lock(w.out/'analysis.process.lock'):
  stat=P('/proc/self/stat').read_text().rsplit(')',1)[1].split();atomic(w.out/'PID.json',{'pid':os.getpid(),'start_ticks':int(stat[19]),'source_sha256':sha(__file__),'config_sha256':sha(args.config),'not_a_model_controller':True,'not_a_git_publisher':True,'UTC':utc()});w.recover()
  while True:
   try:
    if w.tick():return
   except Exception as e:w.save(status='ANALYSIS_HOLD_RETRY',error=repr(e));print(json.dumps({'UTC':utc(),'status':'ANALYSIS_HOLD_RETRY','error':repr(e)}),flush=True)
   if args.once:return
   time.sleep(cfg['poll_seconds'])
if __name__=='__main__':main()
