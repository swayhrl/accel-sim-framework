#!/usr/bin/env python3
"""Same-owner recovery candidate. Passive prepare; no automatic activation/retry."""
import argparse,copy,hashlib,importlib.util,json,os,pathlib,subprocess,sys,time,uuid
P=pathlib.Path;V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1');D=V/'recovery_20261104_v1/agent_d_successor';OLD=V/'activation_20261104_v1/agent_d_execution/finite_main_authorized18.py'
if hashlib.sha256(OLD.read_bytes()).hexdigest()!='414826aa29620a4daf2cc73a230786bee072d58ac8c2217d7e0f9c834e9d7f33':raise RuntimeError('frozen predecessor drift')
sys.path.insert(0,str(OLD.parent));import finite_main_authorized18 as E
from finite_main_authorized18 import *
RECOVERY_CONTROL=V/'activation_20261104_v1/recovery_20261104_v1/control'
INITIAL={'EP_PERF_PFV2_SYSTEM850_FWT_S_FRFCFS256_V1','EP_PERF_CC_CAM_VECTOR4M_F_850_V1'}
HOST_FIELDS={'host_common_ref','host_engine_ref','host_qualification_ref','helpers_ref','archive_module_ref','compact_module_ref','output_module_ref','postprocess_module_ref','validation_module_ref','resource_module_ref','resource_policy_ref','mode_contract_ref','pinned_files','native_entry_ref','validation_contract_ref'}
VERSIONED_NATIVE_PATHS={g:ROOTS[g].parent/'bin/native_recovery_20261104_v1'for g in REQUESTS}
def validate_versioned_entries(m,prior,digest=None):
 if digest is None:digest=sha
 for g in REQUESTS:
  r=m['groups'][g]['native_entry_ref'];old=prior['groups'][g]['native_entry_ref']
  need(P(r['path'])==VERSIONED_NATIVE_PATHS[g],'only exact approved versioned recovery entry path '+g)
  need(r['sha256']==digest(r['path']),'versioned scoped Native SHA mismatch '+g)
  need(P(old['path'])==ROOTS[g].parent/'bin/native'and old['sha256']==digest(old['path']),'accepted canonical Native must retain prior bytes '+g)
 return True
def validate_recovery_manifest(m):
 need(m['schema']=='EP_MAIN_V2_SAME_OWNER_RECOVERY_EXECUTION_MANIFEST_V1'and P(m['control_root'])==RECOVERY_CONTROL,'exact recovery control/schema')
 prior=exact(m['prior_manifest_ref']);need(prior['schema']=='EP_MAIN_V2_AUTHORIZED18_EXECUTION_MANIFEST_V1','prior exact18 origin')
 index=exact(m['prior_spec_byte_index_ref']);need(same_ref(index['old_manifest_ref'],m['prior_manifest_ref']),'prior byte snapshot manifest')
 baseline={r['cohort']:r for r in index['points']};need(set(baseline)==SYSTEM|HIGH,'all18 preserved prior bytes')
 qual=exact(m['host_only_revision_qualification_ref']);need(qual['schema']=='EP_MAIN_V2_HOST_ONLY_SPEC_REVISION_QUALIFICATION_V1'and qual['status']=='MAIN_REVIEWED_SAME_SOURCE_INPUT_282_OBSERVERS_REMAINING16_HOST_ONLY'and qual['approved_by']=='EP-MAIN','Main Host-only revision qualification')
 allowed=set(qual['allowed_host_only_fields']);need(allowed<=HOST_FIELDS,'no hardware/science fields in Host allowlist')
 original={p['cohort']:p for p in prior['points']}
 for p in m['points']:
  c=p['cohort'];old=exact(baseline[c]['immutable_byte_snapshot_ref']);need(same_ref(baseline[c]['old_official_spec_ref'],original[c]['spec_ref'])and sha(baseline[c]['immutable_byte_snapshot_ref']['path'])==original[c]['spec_ref']['sha256'],'byte snapshot original SHA')
  s=exact(p['spec_ref']);need(set(s)==set(old),'no silent extra/removed spec fields')
  changed={k for k in s if s[k]!=old[k]};need(changed<=allowed,'GPU/science contract changed '+c+':'+str(sorted(changed-allowed)))
  if c in INITIAL:need(not changed and same_ref(p['spec_ref'],original[c]['spec_ref']),'consumed2 frozen spec immutable')
 # Reuse exact18/source/budget/282/native/runtime/publisher mathematical checks;
 # only the control/schema differs for this explicit same-owner handoff.
 validate_versioned_entries(m,prior)
 adjusted=copy.deepcopy(m);adjusted['schema']='EP_MAIN_V2_AUTHORIZED18_EXECUTION_MANIFEST_V1';adjusted['control_root']=str(E.DEFAULT_CONTROL)
 # Legacy helper checks the immutable canonical paths using their old refs;
 # versioned paths/bytes are separately and exactly validated above.
 for g in REQUESTS:adjusted['groups'][g]['native_entry_ref']=prior['groups'][g]['native_entry_ref']
 E.validate_manifest(adjusted)
 need(P(m['postrun_only_entry_ref']['path']).is_file()and sha(m['postrun_only_entry_ref']['path'])==m['postrun_only_entry_ref']['sha256'],'exact2 qualified postrun-only scoped wrapper')
 return True

class Successor(E.Executor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_recovery_manifest(self.m);self.C=P(self.m['control_root']);self.states={};self.running={};self.pending_accept=[];self.started=time.monotonic();self.lastpublish=0;self.lastresource={};self.fatal=[];self.session=str(uuid.uuid4());self.points=self.m['points'];self.bypoint={p['cohort']:p for p in self.points};self.specs={p['cohort']:exact(p['spec_ref'])for p in self.points};self.phase_cache={};self.failures={};self.initial_consumed=sorted(INITIAL)
 def native(self,op,c,**kw):
  if c in INITIAL:
   need(op=='accept','consumed handoff point can never model fork again')
   r=self.m['postrun_only_entry_ref'];need(sha(r['path'])==r['sha256'],'postrun-only wrapper drift');need(sha(self.m['shared_native_ref']['path'])==self.m['shared_native_ref']['sha256'],'currentNative requires renewed exact qualification')
   style=self.m.get('postrun_only_cli','CASE_APPLY_ONLY')
   need(style in ['CASE_APPLY_ONLY','STANDARD_SCOPED_ACCEPT'],'qualified postrun-only CLI')
   argv=([sys.executable,'-B',r['path'],'--case',c,'--apply']if style=='CASE_APPLY_ONLY'else[r['path'],'experiment','accept',c,'--project','EP_L2'])
   return subprocess.Popen(argv,**kw)
  return super().native(op,c,**kw)
 def check_activation(self):
  a=read(self.C/'SAME_OWNER_HANDOFF_AUTHORIZATION.json');need(a['schema']=='EP_MAIN_V2_SAME_OWNER_SUCCESSOR_ACTIVATION_V1'and a['status']=='MAIN_REVIEWED_IDLE_OWNER_HANDOFF_AND_REMAINING16_AUTHORIZED'and a['approved_by']=='EP-MAIN','Main reviewed handoff required')
  need(same_ref(a['executor_ref'],ref(__file__))and same_ref(a['manifest_ref'],ref(self.manifest_path))and a['no_retry']is True and a['no_refund']is True,'exact successor code/manifest no retry/refund')
  need(same_ref(a['prior_manifest_ref'],self.m['prior_manifest_ref'])and same_ref(a['host_only_revision_qualification_ref'],self.m['host_only_revision_qualification_ref']),'exact predecessor/Host-only contract')
  prior=exact(a['prior_started_ref']);need(same_ref(prior['manifest_ref'],self.m['prior_manifest_ref']),'predecessor session exact manifest');need(not same_live(prior['process']),'old controller same generation still live; Main must hand off idle owner first')
  snap=exact(a['consumed_snapshot_ref'])
  if snap.get('schema')=='EP_MAIN_V2_SAME_OWNER_CONSUMED_HANDOFF_SNAPSHOT_V1':snaprequests=snap['requests']
  else:
   need(set(snap)==set(REQUESTS),'exact Main idle per-group consumed snapshot');snaprequests={qid:snap[g]for g,qid in REQUESTS.items()}
  reg,rows=self.rows();need(set(rows)==INITIAL,'only exact prior consumed2; no restart/new extra consumption during handoff')
  for g,qid in REQUESTS.items():
   q=reg['registered_future_requests'][qid];sq=snaprequests[qid];need(q['budget']==sq['budget']==BUDGETS[g]and q['remaining']==sq['remaining']==BUDGETS[g]-1,'original budget/remaining unchanged 11+5')
   need(set(q['consumed'])==set(sq['consumed']),'consumed population changed since idle handoff')
   for cc,rr in q['consumed'].items():
    before=sq['consumed'][cc]
    need(all(rr.get(k)==before.get(k)for k in ['uuid','intent_ref','done_ref','output','consumed']),'consumed identity/Done changed since idle snapshot')
    need(rr['state']==before['state']or rr['state']in TERMINAL,'only qualified postrun closure may advance old row')
   admitted={p['cohort']:p['spec_ref']['sha256']for p in self.points if p['group']==g};need(q['admitted_specs']==admitted,'exact Host-revised remaining specs registered; consumed specs retained')
   claims=read(P(self.m['groups'][g]['data_root'])/'control/DISPATCH_CLAIMS.json');priorclaims=exact(a['claims_snapshot_refs'][g]);need(set(claims['claims'])<=set(priorclaims['claims']),'new claim after idle snapshot')
   for cc,cl in claims['claims'].items():need(cl==priorclaims['claims'][cc],'retained claim mutated before owner handoff')
   for cc in set(priorclaims['claims'])-set(claims['claims']):need(q['consumed'][cc]['state']in TERMINAL and self.closed_view(cc,q['consumed'][cc])['archived'],'claim removed only by qualified native archive closure')
   need(set(claims['claims'])<=(INITIAL&set(admitted)),'unconsumed/live extra claim forbids owner handoff')
   for c,row in q['consumed'].items():
    s=self.specs[c];done=exact(row['done_ref']);intent=exact(row['intent_ref']);need(row['uuid']==done['uuid']==intent['uuid']and done['cohort']==intent['cohort']==c,'same consumed/Done/intent UUID population')
    need(same_ref(done['spec_ref'],self.bypoint[c]['spec_ref'])and same_ref(intent['spec_ref'],self.bypoint[c]['spec_ref']),'consumed original specSHA retained')
    need(done['source_identity']==intent['source_identity']==s['source_identity'],'consumed Source/ELF retained')
    cl=claims['claims'].get(c,{})
    if row['state']not in TERMINAL:need(cl.get('uuid')==row['uuid']and cl.get('spec_sha256')==self.bypoint[c]['spec_ref']['sha256']and cl.get('state')=='TERMINAL_PENDING_VALIDATION','retained terminal claim/UUID/spec')
    if cl.get('model_pid'):need(not same_live(dict(pid=cl['model_pid'],start_ticks=cl['model_start_ticks'])),'consumed model generation still live')
    if cl.get('launcher_pid'):
     try:need(pid_identity(cl['launcher_pid'])['state']in ['Z','X'],'consumed launcher still live')
     except OSError:pass
  need(sha(self.m['shared_native_ref']['path'])==self.m['shared_native_ref']['sha256'],'new exactNative qualification current')
 def close_handoff_done(self):
  # Attempt both old sealed Done rows before any of the remaining16 can start.
  for c in self.initial_consumed:
   _,rows=self.rows()
   if rows[c]['state']in TERMINAL:continue
   self.pending_accept.append(c)
   try:self.accept_one()
   except Exception as e:self.states[c]=dict(status='POSTRUN_ONLY_HANDOFF_CLOSURE_HOLD',terminal_hold=True,reason=repr(e));self.event('POSTRUN_ONLY_HANDOFF_CLOSURE_HOLD',cohort=c,reason=repr(e))
  _,rows=self.rows();put(self.C/'HANDOFF_DONE_CLOSURE_RESULT.json',dict(status='OLD_DONE_CLOSURE_ATTEMPTED_NO_MODEL_RETRY',points={c:rows[c]for c in self.initial_consumed},scientific_starts=0))
 def decisions(self,reg,rows):
  out,views,refs,errors=super().decisions(reg,rows)
  for c in self.initial_consumed:
   if rows.get(c,{}).get('state')not in TERMINAL:
    g=self.bypoint[c]['group'];errors[g]='prior sealed Done postrun-only closure unresolved'
    for p in self.points:
     if p['group']==g and p['cohort']not in rows:out[p['cohort']]=dict(status='HOLD',group=g,reason='LOCAL_PRIOR_DONE_CLOSURE_HOLD_NO_CONSUMED_RETRY')
  return out,views,refs,errors
 def summary(self,decisions=None):
  r=super().summary(decisions);r['same_owner_handoff']=True;r['prior_consumed_never_reforked']=sorted(INITIAL);r['maximum_remaining_new_starts']=16;r['original_scoped_budgets_unchanged']=dict(system=12,highclock=6);r['new_budget_or_refund']=False;put(self.C/'RESULTS_CURRENT.json',r);return r
 def publish(self,final=False):
  # Same Main repository/function/lock, no second Git writer.
  oldfile=E.__file__;E.__file__=__file__
  try:return super().publish(final)
  finally:E.__file__=oldfile
 def run(self):
  self.check_activation()
  with lock(self.C/'SINGLE_MAIN_AUTHORIZED18_EXECUTOR.lock',True),lock(OWNERSHIP,True):
   need(not(self.C/'EXECUTOR_STARTED.json').exists(),'no automatic resume/re-fork');put(self.C/'EXECUTOR_STARTED.json',dict(schema='EP_MAIN_V2_AUTHORIZED18_EXECUTOR_START_V1',utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),no_consumed_retry=True));self.event('SINGLE_MAIN_EXECUTOR_STARTED')
   self.summary()
   try:self.publish()
   except Exception as e:self.event('INITIAL_PUBLICATION_HOLD',reason=repr(e))
   self.close_handoff_done()
   nextgroup='highclock'
   while True:
    try:self.poll()
    except Exception as e:self.event('LOCAL_POLL_HOLD_NO_MODEL_KILL',reason=repr(e))
    try:self.accept_one()
    except Exception as e:
     _,heldrows=self.rows()
     for hc,hr in heldrows.items():
      if hr.get('state')not in TERMINAL and hc not in self.running and hc not in self.pending_accept:self.states[hc]=dict(status='LOCAL_ACCEPTANCE_REVIEW_HOLD',terminal_hold=True,reason=repr(e),utc=now())
     self.event('LOCAL_ACCEPTANCE_HOLD_NO_MODEL_RETRY',reason=repr(e))
    reg,rows=self.rows();decisions,views,refs,errors=self.decisions(reg,rows);self.failures=errors
    for g in REQUESTS:
     try:self.emit_stage_receipts(decisions,views,refs,rows,only_group=g)
     except Exception as e:
      self.failures[g]=repr(e)
      for p in self.points:
       if p['group']==g and p['cohort']not in rows:decisions[p['cohort']]=dict(status='HOLD',group=g,reason='LOCAL_STAGE_RECEIPT_HOLD',detail=repr(e))
    ready={g:[]for g in REQUESTS}
    for p in sorted(self.points,key=self.priorities):
     c=p['cohort'];d=decisions[c]
     if c in rows or c in self.running:continue
     if d['status']in ['HOLD','PRUNE']:self.states[c]=dict(status='PRUNED_NOT_CONSUMED'if d['status']=='PRUNE'else'LOCAL_FAMILY_HOLD_NOT_CONSUMED',terminal_hold=True,reason=d['reason'],utc=now());continue
     if d['status']=='RELEASE'and not self.states.get(c,{}).get('terminal_hold'):ready[p['group']].append(p)
    while len(self.running)<2 and any(ready.values()):
     g=nextgroup if ready[nextgroup]else next(g for g in REQUESTS if ready[g]);p=ready[g].pop(0);nextgroup='system'if g=='highclock'else'highclock'
     try:self.start(p)
     except Exception as e:self.states[p['cohort']]=dict(status='LOCAL_PRELAUNCH_QUALIFICATION_HOLD',terminal_hold=True,reason=repr(e),utc=now());self.event('LOCAL_PRELAUNCH_QUALIFICATION_HOLD',cohort=p['cohort'],reason=repr(e))
    self.summary(decisions)
    if time.monotonic()-self.lastpublish>=1800:
     try:self.publish()
     except Exception as e:self.event('PERIODIC_PUBLICATION_HOLD',reason=repr(e))
    _,rows=self.rows();settled=all(rows.get(p['cohort'],{}).get('state')in TERMINAL or self.states.get(p['cohort'],{}).get('terminal_hold')for p in self.points)
    if settled and not self.running and not self.pending_accept:break
    if time.monotonic()-self.started>self.m.get('admission_wait_and_execution_wall_seconds',7*86400)and not self.running:break
    time.sleep(10)
   self.summary(decisions)
   try:self.archive_summary()
   except Exception as e:self.event('SUMMARY_ARCHIVE_HOLD',reason=repr(e))
   try:self.publish(final=True)
   except Exception as e:self.event('FINAL_PUBLICATION_HOLD',reason=repr(e))
   _,rows=self.rows();remote=read(self.C/'REMOTE_PUBLICATION_RECEIPT.json')if(self.C/'REMOTE_PUBLICATION_RECEIPT.json').exists()else{};put(self.C/'EXECUTOR_FINISHED.json',dict(utc=now(),session=self.session,status='SAME_OWNER_REMAINING16_TERMINAL_OR_LOCAL_REVIEW_HOLD',consumed=len(rows),accepted=sum(r['state']=='CLOSED_ACCEPTED'for r in rows.values()),unaccepted=sum(r['state']=='CLOSED_UNACCEPTED'for r in rows.values()),unconsumed_cohorts=[p['cohort']for p in self.points if p['cohort']not in rows],all_consumed_terminal=all(r['state']in TERMINAL for r in rows.values()),final_remote_readback_pass=remote.get('final')is True and remote.get('HEAD')==remote.get('remote_HEAD'),no_retry=True,no_refund=True))

def main(argv=None):
 ap=argparse.ArgumentParser(description='Main same-owner remaining16 successor; passive default');ap.add_argument('--manifest',required=True);g=ap.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');a=ap.parse_args(argv)
 if a.run:Successor(a.manifest).run()
 else:validate_recovery_manifest(read(a.manifest));print(json.dumps(dict(status='PASS_PASSIVE_SAME_OWNER18_WITH16_UNCONSUMED',model_starts=0,registry_writes=0,dispatcher_started=False)))
if __name__=='__main__':main()
