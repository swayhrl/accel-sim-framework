"""Focused independent CPU checks; private fixture, no production install."""
import copy,hashlib,importlib.util,json,pathlib,types
P=pathlib.Path(__file__).resolve().parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('actual_aging',P/'installed_aging.source.py')
b=module('B_candidate',P/'B_candidate.source.py')
guardpath=P.parent/'frame_read_guard_v1/frame_read_guard.py'
g=module('actual_FrameGuard',guardpath)
# Source-location remap is CPU-only; exact original bytes/SHA remain checked.
b.SOURCE=P/'installed_aging.source.py'
checks=[]
def ck(name,condition):
 assert condition,name
 checks.append(name)
def row(c,cell='DH',profile='M8',age=-4000):
 return dict(cohort=c,input_digest='lava',program='lavamd',cell=cell,profile=profile,cost_bytes=80*a.G,first_eligible_monotonic=age)
def context(rows):
 specs={r['cohort']:dict(r,request=b.REQ,schema='DTC_L2_MLP_SPEC_V1',source_kind='FROZEN35_WHOLE_DECLARED_TRACE_CONTRACT',performance_scope='NEW_L2_MLP_ONLY_NEVER_ORIGINAL',correctness_validation_only=False,new_base_reuse=False,estimated_peak_model_RAM_bytes=r['cost_bytes'])for r in rows}
 return dict(registry=dict(admitted_specs={r['cohort']:'fixture-sha' for r in rows},consumed={}),specs=specs,
  matrix_points={r['cohort']:dict(r)for r in rows},active_memory=dict(allowed_cohorts=[r['cohort']for r in rows]),
  spec_sha256={r['cohort']:'fixture-sha'for r in rows},preserved_nonprimary=set(),initial_references=set(),INTENT_exists=set())
def frame(rows):
 return dict(now=0,budget_bytes=200*a.G,effective_total_growth_bytes=180*a.G,memory_utilization_fraction=.88,
 own_live=[dict(cohort='done',uuid='du',pid=1,start_ticks=1,RSS_bytes=20*a.G,anon_PSS_bytes=20*a.G,PSS_sample_monotonic=0,effective_future_bytes=10*a.G),
           dict(cohort='still-live',uuid='su',pid=2,start_ticks=2,RSS_bytes=100*a.G,anon_PSS_bytes=100*a.G,PSS_sample_monotonic=0,effective_future_bytes=60*a.G)],
 consumed={},claim_cohorts=[],closures=[],pending=rows,active_input_digests=[],started_programs=['lavamd'],pressure_reasons=[],
 total_padding_discount_bytes=0,padding_discount_by_cohort={},accounted_growth_by_cohort={'done':10*a.G})
rows=[row('LAV-CHP0','CH','P0'),row('LAV-DHM8')];ctx=context(rows)
compiled,_=b.build_advance(a.AgingState().advance,lambda f:ctx)
st=a.AgingState();f=frame(rows);before=copy.deepcopy(f)
ck('CH P0 after completed DH P0 can become sole target',compiled(st,f)['target']['cohort']=='LAV-CHP0' and f==before)
ck('variant-only pool can become target',compiled(a.AgingState(),frame(rows[1:]))['target']['cohort']=='LAV-DHM8')
bad=copy.deepcopy(ctx);bad['matrix_points'].pop('LAV-DHM8');ck('missing primary matrix identity rejected',not b.primary_eligible(rows[1],bad))
bad=copy.deepcopy(ctx);bad['preserved_nonprimary'].add('LAV-DHM8');ck('supplemental role rejected',not b.primary_eligible(rows[1],bad))
bad=copy.deepcopy(ctx);bad['spec_sha256']['LAV-DHM8']='tampered';ck('authority SHA mismatch rejected',not b.primary_eligible(rows[1],bad))
ck('spent claim active-input all excluded',all(not b.choose_candidates(f,a.DEFAULT,0,consumed,claims,active,ctx)for consumed,claims,active in [({r['cohort']:{}for r in rows},set(),set()),({},set(r['cohort']for r in rows),set()),({},set(),{'lava'})]))
old=[row('old-variant',age=-5000),row('young-P0','CH','P0',age=-4000)]
ctxold=context(old);c,_=b.build_advance(a.AgingState().advance,lambda f:ctxold)
ck('older variant not displaced by younger P0',c(a.AgingState(),frame(old))['target']['cohort']=='old-variant')
done=copy.deepcopy(f);done['now']=5;done['own_live']=done['own_live'][1:];done['effective_total_growth_bytes']-=10*a.G;done['budget_bytes']+=int(.88*20*a.G)
done['closures']=[dict(cohort='done',uuid='du',natural_done=True,accepted_strict_archive_restore=True)]
expected=int(.75*(10*a.G+int(.88*20*a.G)))
ck('natural strict release retains exact 75 percent bound',compiled(st,done)['protected_bytes']==expected)
failed=a.AgingState();compiled(failed,f);fail=copy.deepcopy(done);fail['closures'][0]['natural_done']=False
ck('unknown failed completion gives no credit',compiled(failed,fail)['protected_bytes']==0)
# Actual FrameGuard, second frame read race after advancing the same state.
calls=[0]
def provider(*args):
 calls[0]+=1
 if calls[0]>1:raise json.JSONDecodeError('CPU fixture partial JSON','{',1)
 return copy.deepcopy(f)
aging=a.AgingChooser(lambda *args:None,provider);main=types.SimpleNamespace()
state=aging.state;state.seen_completions.add(('old-accepted','old-uuid'))
b.install_on_existing(aging,lambda f:ctx,lambda:None,g.FrameUnavailable,main)
saved=state.advance
ck('plain callable survives deepcopy with exact identity',copy.deepcopy(state.__dict__)['advance'] is saved)
def simulated_old_choose(*args):
 state.advance(aging.frame_provider());aging.calls+=1
 aging.frame_provider()  # second frame fails all bounded retries
gate=g.FrameReadGuard(aging,sleeper=lambda n:None);gate.original_choose=simulated_old_choose
old_dict=copy.deepcopy(state.__dict__);v=gate.choose()
ck('real FrameGuard second-read failure rolls back same state and seen set',v is None and aging.state is state and state.__dict__==old_dict and state.advance is saved and ('old-accepted','old-uuid')in state.seen_completions)
b.restore_in_owner(lambda:None,main)
ck('restore removes only private selector and retains old credit history','advance'not in state.__dict__ and state.seen_completions=={('old-accepted','old-uuid')})
o=dict(schema='AGING_SELECTOR_INDEPENDENT_CPU_REVIEW_V1',status='PASS',checks=checks,
 source_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest()for x in [P/'installed_aging.source.py',P/'B_candidate.source.py',guardpath]},
 limits=['Synthetic private authority/resource fixture; not production runtime qualification.','Only source path remapped to exact installed-source copy; production paths untouched.','No models/grants/signals or production installation.'])
(P/'INDEPENDENT_CPU_REVIEW.json').write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8');print(json.dumps(o))
