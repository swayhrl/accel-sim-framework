"""Focused native CPU fixture; real modules, private state, no model/control IO."""
import sys
sys.dont_write_bytecode=True
import copy,hashlib,importlib.util,json,pathlib,types
P=pathlib.Path;HERE=P(__file__).resolve().parent
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
paths={'old':R/'control/operational_amendments/large_job_aging_v1/large_job_aging.py',
 'af':R/'control/operational_amendments/aging_primary_target_selector_v1/primary_target_selector.py',
 'guard':R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py',
 'barrier':A/'agents/B/pending_natural_acceptance_barrier_v1/pending_acceptance_barrier.py'}
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old,af,guard,b=[mod('independent_'+k,v)for k,v in paths.items()]
G=1024**3;U=16800136602;C=32215220625;REAL_R=1084719667;COST=17517364839
rows=[dict(cohort='CPU_LAV_CH_P0',program='lavamd',suite='Rodinia',input_digest='cpu-lava',cell='CH',profile='P0',cost_bytes=80*G,first_eligible_monotonic=-5000),
 dict(cohort='CPU_CUTCP_DH_M8',program='cutcp',suite='Parboil',input_digest='cpu-cutcp',cell='DH',profile='M8',cost_bytes=COST,first_eligible_monotonic=-4000)]
specs={r['cohort']:dict(r,request=af.REQ,schema='DTC_L2_MLP_SPEC_V1',source_kind='FROZEN35_WHOLE_DECLARED_TRACE_CONTRACT',performance_scope='NEW_L2_MLP_ONLY_NEVER_ORIGINAL',correctness_validation_only=False,new_base_reuse=False,estimated_peak_model_RAM_bytes=r['cost_bytes'])for r in rows}
context=dict(registry=dict(admitted_specs={r['cohort']:'CPU_SHA'for r in rows},consumed={}),active_memory=dict(allowed_cohorts=list(specs)),specs=specs,
 matrix_points={r['cohort']:dict(r)for r in rows},spec_sha256={r['cohort']:'CPU_SHA'for r in rows},preserved_nonprimary=set(),initial_references=set(),INTENT_exists=set())
def frame():
 return dict(now=0,budget_bytes=200*G,effective_total_growth_bytes=200*G-(C-U),memory_utilization_fraction=.88,
 own_live=[dict(cohort='natural',uuid='nu',pid=1,start_ticks=1,RSS_bytes=1,anon_PSS_bytes=0,PSS_sample_monotonic=0,effective_future_bytes=U),
 dict(cohort='still-live',uuid='su',pid=2,start_ticks=2,RSS_bytes=100*G,anon_PSS_bytes=100*G,PSS_sample_monotonic=0,effective_future_bytes=60*G)],
 consumed={},claim_cohorts=[],closures=[],pending=copy.deepcopy(rows),active_input_digests=['other'],started_programs=['lavamd','cutcp'],pressure_reasons=[],
 total_padding_discount_bytes=0,padding_discount_by_cohort={},accounted_growth_by_cohort={'natural':U,'still-live':60*G})
def natural(f,accepted=False):
 v=copy.deepcopy(f);v['now']=5;v['own_live']=v['own_live'][1:];v['effective_total_growth_bytes']-=U
 v['closures']=[dict(cohort='natural',uuid='nu',natural_done=True,accepted_strict_archive_restore=accepted,strict_result_path=None)]
 return v
def setup(with_barrier=True,reader=None):
 aging=old.AgingChooser(lambda *args:None,lambda *args:None);main=types.SimpleNamespace()
 af.install_on_existing(aging,lambda f:context,lambda:None,guard.FrameUnavailable,main)
 if with_barrier:b.install_on_existing(aging,lambda:None,guard.FrameUnavailable,main,result_reader=reader)
 f=frame();aging.state.advance(f);aging.state.protected=REAL_R
 return aging,main,f
checks=[]
def ck(n,c):
 assert c,n
 checks.append(n)
plain,pm,f=setup(False);aging,main,_=setup();s=aging.state;event=natural(f)
base=plain.state.advance(copy.deepcopy(event));decision=s.advance(copy.deepcopy(event))
ck('actual wide-margin old counterexample admits M8 but barrier blocks backfill',rows[1]['cohort']in base['backfill_cohorts']and decision['backfill_cohorts']==[]and C-COST>=base['protected_bytes'])
keys=['protected','seen_completions','pending_releases','previous_C','previous_discount','previous_discount_rows','last_live','target']
ck('original bookkeeping exactly equals one unchanged af advance',all(getattr(s,k)==getattr(plain.state,k)for k in keys))
ck('no new RAM or strict credit added',decision['pending_natural_acceptance_barrier']['provisional_RAM_money_added_bytes']==0 and decision['pending_natural_acceptance_barrier']['strict_credit_added_bytes']==0)
event2=copy.deepcopy(event);event2['now']=6;event2['closures'][0]['accepted_strict_archive_restore']=True
d=s.advance(event2);expect=REAL_R+int(.75*U)
ck('strict pop restores backfill and exactly original75pct realR',s.protected==expect and not s.pending_releases and not d['pending_natural_acceptance_barrier']['active']and rows[1]['cohort']in d['backfill_cohorts'])
s.advance(copy.deepcopy(event2));ck('same strict completion cannot credit twice',s.protected==expect)
z,zm,zf=setup();zd=z.state.advance(copy.deepcopy(zf));ck('no natural closure no barrier',not zd['pending_natural_acceptance_barrier']['active'])
z.state.advance(natural(zf));z.state.pending_releases[('natural','nu')]['realized_credit_bytes']=0
u=natural(zf);u['now']=7200;u['own_live'][0]['PSS_sample_monotonic']=7200
zd=z.state.advance(u);ck('zero-realized unknown remains explicit pending without timeout',zd['pending_natural_acceptance_barrier']['active']and zd['pending_natural_acceptance_barrier']['pending'][0]['realized_kind']=='ZERO_REALIZED_PENDING')
negative=lambda closure,c,u:dict(status='NATURAL_DONE_WITH_EXPLICIT_NEGATIVE_RESULT_MAIN_REVIEW',accepted=False)
n,nm,nf=setup(reader=negative);nd=n.state.advance(natural(nf));ck('natural strict-negative observable HOLD not accepted',nd['pending_natural_acceptance_barrier']['active']and nd['pending_natural_acceptance_barrier']['pending'][0]['acceptance_observation']['accepted']is False)
fail=natural(nf);fail['closures'][0]['natural_done']=False
nd=n.state.advance(fail);ck('non-natural failure old pop removes pending barrier',not nd['pending_natural_acceptance_barrier']['active']and not n.state.pending_releases)
claim,cm,cf=setup();claim.state.advance(natural(cf));full=natural(cf);full['claim_cohorts']=[rows[0]['cohort']];full['accounted_growth_by_cohort'][rows[0]['cohort']]=rows[0]['cost_bytes']
cd=claim.state.advance(full);ck('fully accounted target claim keeps virtual0 no extra barrier',cd['virtual_fence_released_due_full_claim']and cd['protected_bytes']==0 and not cd['pending_natural_acceptance_barrier']['active'])
offer,om,of=setup();ofn=natural(of);ofn['budget_bytes']+=100*G
od=offer.state.advance(ofn);ck('full-cost target offer preserved despite backfill barrier',od['offer_target_first']==rows[0]['cohort']and od['pending_natural_acceptance_barrier']['active'])
pressure=copy.deepcopy(ofn);pressure['pressure_reasons']=['cpu_pressure_full'];pd=offer.state.advance(pressure)
ck('CPU pressure preserved unchanged',pd['pressure_reasons']==['cpu_pressure_full'])
# Real FrameGuard rollback after state advances and second provider read fails.
rollback,rm,rf=setup();rollback.state.advance(natural(rf));state=rollback.state;before=copy.deepcopy(state.__dict__);calls=[0]
def provider(*args):
 calls[0]+=1
 if calls[0]>1:raise json.JSONDecodeError('CPU partial JSON','{',1)
 return copy.deepcopy(natural(rf))
rollback.frame_provider=provider;gate=guard.FrameReadGuard(rollback,sleeper=lambda n:None)
def twice(*args):
 state.advance(rollback.frame_provider());rollback.calls+=1;rollback.frame_provider()
gate.original_choose=twice
ck('real FrameGuard rolls back same state callable tokens and previousC',gate.choose()is None and rollback.state is state and state.__dict__==before)
# Runtime refs were deliberately not changed during install; restore correct pair.
original_provider=main.__dict__[b.MARKER]['refs'][1]
b.restore_in_owner(lambda:None,main);ck('barrier restore returns exact saved af wrapper',aging.state.advance is getattr(main,af.MARKER)['wrapper'])
af.restore_in_owner(lambda:None,main);ck('reverse restore returns original class advance','advance'not in aging.state.__dict__)
o=dict(schema='E_PENDING_NATURAL_BARRIER_INDEPENDENT_CPU_V1',status='PASS',checks=checks,check_count=len(checks),
 sources={k:dict(path=str(v),sha256=hashlib.sha256(v.read_bytes()).hexdigest())for k,v in paths.items()},
 scope='Native CPU only, actual frozen modules with private registry/resource fixtures; not model or production install qualification',
 exact_wide_margin_values=dict(C=C,U=U,R=REAL_R,candidate_full_cost=COST),production_mutations=False,model_starts=0,new_grants=0,
 scientific_scope='No input/results/GM/acceptance changes; R2 never unioned. Operational closure fixtures are not scientific acceptance.')
(HERE/'INDEPENDENT_CPU_REVIEW.json').write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8');print(json.dumps(o))
