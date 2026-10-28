import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,importlib.util,types,copy,tempfile
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('B_pending_barrier_candidate',D/'pending_acceptance_barrier.py');af=load('B_previous_actual_af096',A/'agents/B/aging_primary_targets_v1/primary_target_selector.py');old=load('B_unchanged_old_aging',af.SOURCE);fg=load('B_actual_FrameGuard',R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py')
assert sha(af.__file__)==m.AF_SHA
target='E2-DTCL2MLP-ddb6806316876a85-CH-P0-V1';ts=read(R/'control/specs'/(target+'.json'));tr=dict(cohort=target,input_digest=ts['input_digest'],program=ts['program'],cell='CH',profile='P0',cost_bytes=ts['estimated_peak_model_RAM_bytes'],first_eligible_monotonic=0)
small='E2-DTCL2MLP-af7320f9d9dc6629-DH-M8-V1';cost=17517364839;sr=dict(cohort=small,input_digest='CPU_HISTORICAL_CUTCP_INPUT',program='cutcp',cell='DH',profile='M8',cost_bytes=cost,first_eligible_monotonic=0)
probe=read(A/'agents/B/aging_release_erosion_readonly_v1/CHRONOLOGY_PROBE_V1.json');episodes=probe['episodes'];checked=[]
def ck(n,b):assert b,n;checked.append(n)
def book(s):return {k:v for k,v in s.__dict__.items()if k not in ['last_decision','advance']}
def frames_for(c,afterC,Rinitial):
 e=episodes[c];t=e['first_pending_token'];u=t['uuid'];raw=t['raw_release_bytes'];oldR=Rinitial
 persistent=dict(cohort='CPU_PERSISTENT_LIVE',uuid='CPU_PERSISTENT_ONLY',RSS_bytes=120*G,effective_future_bytes=20*G,anon_PSS_bytes=120*G,PSS_sample_monotonic=10000)
 witness=dict(cohort=c,uuid=u,RSS_bytes=t['last_anon_PSS_bytes'],effective_future_bytes=t['last_effective_future_bytes'],anon_PSS_bytes=t['last_anon_PSS_bytes'],PSS_sample_monotonic=10000)
 def f(now,C,alive=True,accepted=False,natural=True):
  live=[dict(persistent,PSS_sample_monotonic=now)]+([dict(witness,PSS_sample_monotonic=now)]if alive else[])
  return dict(now=now,budget_bytes=200*G,effective_total_growth_bytes=200*G-C,memory_utilization_fraction=.95,own_live=live,consumed={c:dict(uuid=u,terminal=not alive)},claim_cohorts=[],pending=[copy.deepcopy(tr),copy.deepcopy(sr)],active_input_digests=['CPU_PERSISTENT_INPUT'],started_programs=['lavamd','cutcp'],accounted_growth_by_cohort={},closures=[]if alive else[dict(cohort=c,uuid=u,natural_done=natural,accepted_strict_archive_restore=accepted,strict_result_path=None)],total_padding_discount_bytes=0,padding_discount_by_cohort={},pressure_reasons=[])
 return [f(10000,afterC-raw),f(10001,afterC,False),f(10002,afterC,False,True)],raw,u
def state_pair(initialR):
 s=old.AgingState();s.target=copy.deepcopy(tr);s.protected=initialR;control=copy.deepcopy(s);calls=[0]
 compiled,_=af.build_advance(s.advance,lambda f:(_ for _ in()).throw(AssertionError('Existing target should not reselect')))
 def previous(f):calls[0]+=1;return compiled(s,f)
 wrapped=m.make_wrapper(previous,s,fg.FrameUnavailable,result_reader=lambda *a:dict(status='CPU_ONLY_AWAITING',accepted=False))
 return s,control,calls,compiled,wrapped
cases=[('E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2',15024396689,0),('E2-DTCL2MLP-af7320f9d9dc6629-DH-F256-V1',32215220625,1084719667),('E2-DTCL2MLP-09f94fcc7494a03b-DH-P0-V1',29917743300,1349378150)]
for c,C,initialR in cases:
 fs,raw,u=frames_for(c,C,initialR);s,control,calls,compiled,w=state_pair(initialR)
 for ix,f in enumerate(fs):
  before=calls[0];d=w(copy.deepcopy(f));compiled(control,copy.deepcopy(f));assert calls[0]==before+1 and book(s)==book(control)
  if ix==1:assert d['pending_natural_acceptance_barrier']['active']and d['backfill_cohorts']==[]
  if ix==2:assert not d['pending_natural_acceptance_barrier']['active']and s.protected==min(tr['cost_bytes'],initialR+int(.75*raw))
 ck('synthetic actual-identity sequence '+c+' invokes oldaf once and preserves all old bookkeeping; pending blocks backfill then strict forms75% once',True)
 if 'F256'in c:
  ck('real wide-margin counterexample M8 would fit C-R but is explicitly absent from pending backfill',C-cost>=initialR and small in d['backfill_cohorts'])
  # d now strict-success; original backfill resumes and full cost still fits strictR.
  ck('after actual-rule synthetic strict conversion M8 fullcost fits and old75/25 lane resumes',C-cost>=s.protected and small in d['backfill_cohorts'])
# No natural closure: external headroom alone creates neither token nor barrier.
fs,raw,u=frames_for(cases[1][0],cases[1][1],cases[1][2]);s,ctrl,count,compiled,w=state_pair(0);w(fs[0]);free=copy.deepcopy(fs[0]);free['now']+=1;free['budget_bytes']+=30*G;d=w(free);ck('no closure/external free cannot create token, barrier or credit',not d['pending_natural_acceptance_barrier']['active']and not s.pending_releases and s.protected==0)
# Pending0 and unknown are still pending, no time-based fake closure.
s,ctrl,count,compiled,w=state_pair(cases[1][2]);w(fs[0]);w(fs[1]);key=next(iter(s.pending_releases));s.pending_releases[key]['realized_credit_bytes']=0
unknown=copy.deepcopy(fs[1]);unknown['now']=20000;unknown['own_live'][0]['PSS_sample_monotonic']=20000;d=w(unknown);ck('zero realized unknown pending remains explicit barrier without money/credit',d['pending_natural_acceptance_barrier']['active']and d['pending_natural_acceptance_barrier']['pending'][0]['realized_kind']=='ZERO_REALIZED_PENDING'and d['pending_natural_acceptance_barrier']['strict_credit_added_bytes']==0)
failure=copy.deepcopy(unknown);failure['closures'][0]['natural_done']=False;d=w(failure);ck('authoritative nonnatural closure lets oldcode remove token and barrier with zero new credit',not s.pending_releases and not d['pending_natural_acceptance_barrier']['active']and s.protected==cases[1][2])
# Explicit natural strict negative is visible and does not auto-release/accept.
tmp=P(tempfile.mkdtemp(prefix='CPU_NEGATIVE_',dir=D));negative=tmp/'analysis'/(cases[1][0]+'.RESULT.json');negative.parent.mkdir();negative.write_text(json.dumps(dict(cohort=cases[1][0],uuid=u,state='FAIL_L2MLP_ARCHIVED_NO_RETRY',proof={'performance_accepted':False})))
s,ctrl,count,compiled,_=state_pair(cases[1][2]);prev=lambda f:compiled(s,f);w=m.make_wrapper(prev,s,fg.FrameUnavailable,root=tmp);w(fs[0]);w(fs[1]);bad=copy.deepcopy(fs[1]);bad['closures'][0]['strict_result_path']=str(negative);d=w(bad);ck('natural DONE plus explicit negative RESULT remains visible Main-review HOLD, never credit or fake accepted',d['pending_natural_acceptance_barrier']['active']and d['pending_natural_acceptance_barrier']['pending'][0]['acceptance_observation']['status']=='NATURAL_DONE_WITH_EXPLICIT_NEGATIVE_RESULT_MAIN_REVIEW'and s.protected==cases[1][2])
# Fullcost target offer/backed behavior and pressure are unmodified.
s,ctrl,count,compiled,w=state_pair(cases[1][2]);w(fs[0]);w(fs[1]);offer=copy.deepcopy(fs[1]);offer['budget_bytes']+=100*G;d=w(offer);ck('fullcost target offer preserved despite backfill barrier',d['offer_target_first']==target and d['pending_natural_acceptance_barrier']['active'])
backed=copy.deepcopy(fs[1]);backed['claim_cohorts']=[target];backed['accounted_growth_by_cohort'][target]=tr['cost_bytes'];d=w(backed);ck('target fullclaim already accounted releases virtual fence without new money or double RAM deduction',not d['pending_natural_acceptance_barrier']['active']and d['protected_bytes']==0 and d['virtual_fence_released_due_full_claim'])
pressure=copy.deepcopy(fs[1]);pressure['pressure_reasons']=['memory_pressure'];d=w(pressure);ck('negative physical pressure list remains unchanged',d['pressure_reasons']==['memory_pressure'])
# Actual installed class/FrameGuard/af instance layer and second-fresh rollback.
private_calls=[];provider_calls=[0];f=copy.deepcopy(offer)
def provider(*a):
 provider_calls[0]+=1
 if provider_calls[0]in[2,3,4]:raise json.JSONDecodeError('CPU second-fresh failure','x',0)
 return copy.deepcopy(f)
def private(pending,*a):private_calls.append(pending);return dict(cohort=target)
aging=old.AgingChooser(private,provider);aging.state.target=copy.deepcopy(tr);aging.state.protected=cases[1][2];gate=fg.FrameReadGuard(aging,sleeper=lambda x:None);main=types.SimpleNamespace();af.install_on_existing(aging,lambda f:{},lambda:None,fg.FrameUnavailable,main);previous=aging.state.advance
before=copy.deepcopy(book(aging.state));refs=(aging.original,aging.frame_provider,aging.wrapper,aging.lock)
m.install_on_existing(aging,lambda:None,fg.FrameUnavailable,main,result_reader=lambda*a:dict(status='CPU_ONLY',accepted=False));wrapper=aging.state.advance
assert gate.wrapper([{'cohort':target}],{}, {},{},None,{},0)is None
ck('actual FrameGuard second-fresh JSON failure restores all bookkeeping and same plain closure/state',book(aging.state)==before and aging.state.advance is wrapper and aging.calls==0 and gate.last_issue['state_restored'])
gate.wrapper([{'cohort':target}],{}, {},{},None,{},1);ck('after rollback original private resource leaf still used and refs unchanged',private_calls and refs==(aging.original,aging.frame_provider,aging.wrapper,aging.lock))
m.restore_in_owner(lambda:None,main);ck('exact previousaf instance function restored with no credit replay or state replacement',aging.state.advance is previous and refs==(aging.original,aging.frame_provider,aging.wrapper,aging.lock));af.restore_in_owner(lambda:None,main)
out=dict(schema='B_PENDING_NATURAL_ACCEPTANCE_BARRIER_CPU_QUALIFICATION_V1',status='PASS',count=len(checked),checks=checked,source_sha256=sha(m.__file__),prior_selector_sha256=sha(af.__file__),old_aging_sha256=sha(af.SOURCE),only_advance_called_once_and_backfill_restricted=True,real_wide_margin_values_from_journal=True,all_memory_release_events_SYNTHETIC_NOT_ACTUAL_CREDIT=True,production_changes=0,models_started=0,new_grants=0,signals=0)
p=D/'CPU_QUALIFICATION.json';p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),status='PASS',count=len(checked),source_sha256=sha(m.__file__))))
