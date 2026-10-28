"""Focused actual-schema CPU qualification; synthetic cycles, isolated authority."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys,threading,types
P=pathlib.Path;H=P(__file__).resolve().parent;sys.path.insert(0,str(H))
import interaction_policy as policy
import owner_adapter as owner
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=R.parent # no production writes
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
cfg=read(R/'control/operational_amendments/typed_negative_transport_v3/INSTALL_CONFIG.json')
gp=R/'control/operational_amendments/typed_negative_full35_v2/terminal_gate.py';gate=load('real_gate',gp)
consumer=load('real_consumer',R/'tools/l2_results.py');gen=load('real_gen',R/'tools/l2_config_generator.py')
scope=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json');assert len(scope['points'])==350
checks=[];examples=[];counter=[0]
def ck(n,x):assert x,n;checks.append(n)
def fixture(gains=None):
 gains=gains or{};records={}
 for p in scope['points']:
  c=p['cohort'];cycles=round(10**12/gains.get(p['profile'],1));records[c]=dict(cohort=c,uuid='CPU_'+c,state=consumer.PASS,cycles=cycles,proof=dict(performance_accepted=True,cycles=cycles),archive={'CPU_ONLY':True})
 s=consumer.summarize(scope,records)
 return copy.deepcopy(s),copy.deepcopy(scope),copy.deepcopy(history)
def actual(s,m,h):return gate.recommend(s,m,h,cfg['source_paths'],cfg['source_pins'],{},lambda*a:(_ for _ in()).throw(AssertionError('No typed fixture here')))
def run(s,m,h,old=None):
 old=actual(s,m,h)if old is None else old
 v=policy.augment(old,s,m,h)
 return policy.validate_new_phases(v,s,m,h,{v['cohort']:v for v in old.get('verified_typed_engineering_negatives',[])})
def own(v):return [p for p in v['proposals']if p.get('supplementary_policy')==policy.SCHEMA]
def addprofile(s,m,h,params,gain=1,cell='DH',state=None):
 params=policy.normalize(params);n=policy.name(params);h['profiles'][n]=dict(parameters=params)
 if n not in s['profiles']:s['profiles'].append(n)
 for p in list(scope['points']):
  if p['profile']!='P0'or p['cell']!=cell:continue
  d=p['input_digest'];c=p['cohort'].replace('-P0-','-'+n+'-');point=dict(p,profile=n,cohort=c)
  if not any(x['cohort']==c for x in m['points']):m['points'].append(point)
  s['table'][d].setdefault(n,{})[cell]=dict(cohort=c,uuid='CPU_'+c,state=state or consumer.PASS,
   accepted=state is None,cycles=round(10**12/gain)if state is None else None)
 return n
def structural(s,m,h):
 for _,p in policy.SEEDS:addprofile(s,m,h,p)
def ablations(s,m,h):
 wide=policy.normalize(policy.SEEDS[-1][1])
 for a in policy.AXES:addprofile(s,m,h,dict(wide,**{a:policy.BASE[a]}))
def allbrackets(s,m,h):
 for _,over in policy.SEEDS:
  seed=policy.normalize(over)
  for a in policy.AXES:
   if seed[a]==policy.BASE[a]:continue
   context=dict(seed,**{a:policy.BASE[a]})
   for mul in (1,2,4):addprofile(s,m,h,dict(context,**{a:policy.BASE[a]*mul}))

s,m,h=fixture();original=actual(s,m,h);v=run(s,m,h,original)
ck('actual chain flat parents still gives exactly six structural DH35 seeds',len(own(v))==6 and all(p['new_cell_count']==35 and p['cells']==['DH']for p in own(v)))
ck('old proposals and engineering flags are retained without promotion',v['proposals'][:len(original['proposals'])]==original['proposals']and not v['adoption_ready']and not v['scientific_stage_complete'])
ck('six seeds never treated as total budget cap',v['interaction_policy']['six_seeds_are_not_total_cap'])
examples.append(dict(case='flat_OFAT',proposed=[p['profile']for p in own(v)]))
ids=sorted(s['table']);d=ids[0]
pending=copy.deepcopy(s);pending['table'][d]['P0']['CH'].update(accepted=False,cycles=None,state='PENDING')
ck('one initial pending CH cell blocks new scientific work',not own(run(pending,m,h)))
typed=copy.deepcopy(s);row=typed['table'][d]['M16']['DH'];row.update(accepted=False,cycles=None,state=policy.TYPED)
old=copy.deepcopy(original);old.update(requires_engineering_review=True,negative_review_disposition_required=True,
 verified_typed_engineering_negatives=[dict(cohort=row['cohort'],uuid=row['uuid'],verified=True,cycles=None,performance_accepted=False)])
tv=run(typed,m,h,old)
ck('verified M16 negative only closes terminal gate never supplies performance',len(own(tv))==6 and tv['requires_engineering_review']and tv['negative_review_disposition_required']and all('M16'not in p['evidence']['parents']for p in own(tv)))
bad=copy.deepcopy(old);bad['verified_typed_engineering_negatives']=[]
ck('unverified typed negative holds initial gate',not own(run(typed,m,h,bad)))
failed=copy.deepcopy(s);failed['table'][d]['E768']['DH'].update(accepted=False,cycles=None,state='FAIL_L2MLP_ARCHIVED_NO_RETRY')
fv=run(failed,m,h)
ck('34accepted parents cannot silently become full35 and independent seeds continue',len(own(fv))==2 and all('E768'not in p['evidence']['parents']for p in own(fv)))
hh=copy.deepcopy(h);hh['proposal_ids']+= [p['proposal_id']for p in own(v)]
ck('known proposal IDs deduplicate without retry or budget reset',not own(run(s,m,hh)))
aliasm=copy.deepcopy(m);aliash=copy.deepcopy(h);aliass=copy.deepcopy(s)
aliash['profiles']['M8_ALIAS']=dict(parameters=policy.normalize(dict(merge=8)))
aliaspoint=next(x for x in m['points']if x['profile']=='M8');aliasm['points'].append(dict(aliaspoint,profile='M8_ALIAS',cohort=aliaspoint['cohort']+'_ALIAS'))
aliass['profiles'].append('M8_ALIAS');aliass['table'][aliaspoint['input_digest']]['M8_ALIAS']={'DH':dict(aliass['table'][aliaspoint['input_digest']]['M8']['DH'],cohort=aliaspoint['cohort']+'_ALIAS')}
try:run(aliass,aliasm,aliash)
except AssertionError:rejected=True
else:rejected=False
ck('same registered vector cannot gain a second alias to bypass prior identity',rejected)
bounded=copy.deepcopy(h);bounded['resource_constraints']=dict(reason='CPU explicit measured infeasibility witness',max_parameters=dict(entries=384))
ck('logical resource rejection is an explicit HOLD not saturation',len(own(run(s,m,bounded)))==2 and not run(s,m,bounded)['adoption_ready'])

structural(s,m,h);v=run(s,m,h)
ck('wide ablations are required even when all six joint seeds flat',len([p for p in own(v)if p['phase']=='V3_WIDE_ABLATION'])==4)
ck('conditional brackets progress independently before all other contexts finish',any(p['phase']=='V3_CONTEXT_BRACKET'for p in own(v)))
ck('CH not added early by interaction layer',not any(p['phase']=='V3_UNIFORM_CH_MATCH'for p in own(v)))
ablations(s,m,h);allbrackets(s,m,h);flat=run(s,m,h)
ck('14 declared fixed conditional ladders close after two flat marginals',len(flat['interaction_search']['ladders'])==14 and all(x['status']=='STOP_TWO_NONPOSITIVE_CONTEXTUAL_MARGINALS'for x in flat['interaction_search']['ladders']))
tiers=flat['interaction_search']['uniform_resource_tiers']
ck('flat results still require distinct moderate and high whole35 CH matches',flat['interaction_search']['DH_work_closed']and tiers['moderate']['profile']!=tiers['high_resource_potential']['profile']and
 all(tiers[t]['profile']in flat['interaction_search']['CH_required_profiles']for t in('moderate','high_resource_potential'))and all(not tiers[t]['improvement_proven']for t in('moderate','high_resource_potential')))
target=dict(entries=768,frfcfs=256);n=addprofile(s,m,h,target,gain=1.01)
v=run(s,m,h)
ck('conditional E axis grows to1536 within F256 despite flat E OFAT',any(p['profile']=='E1536_F256'and p['phase']=='V3_CONTEXT_BOUNDARY'for p in own(v)))
ck('conditional F axis also proceeds without per-program best selection',any(p['profile']=='E768_F512'for p in own(v)))
addprofile(s,m,h,dict(entries=1536,frfcfs=256),gain=1.01)
v=run(s,m,h)
ck('one flat marginal after gain asks one saturation confirmation',any(p['profile']=='E3072_F256'and p['phase']=='V3_CONTEXT_SATURATION_CONFIRM'for p in own(v)))
addprofile(s,m,h,dict(entries=3072,frfcfs=256),gain=1.01)
v=run(s,m,h)
lad=next(x for x in v['interaction_search']['ladders']if x['context_id']=='entries_schedule__entries')
ck('two consecutive nonpositive contextual marginals stop this context only',lad['status']=='STOP_TWO_NONPOSITIVE_CONTEXTUAL_MARGINALS'and any(p['profile']=='E768_F512'for p in own(v)))
addprofile(s,m,h,dict(entries=768,frfcfs=512),gain=1.01);addprofile(s,m,h,dict(entries=768,frfcfs=1024),gain=1.01)
v=run(s,m,h)
ck('best uniform positive configuration receives whole35 CH only after DH closure',v['interaction_search']['DH_work_closed']and any(p['cells']==['CH']and p['new_cell_count']==35 for p in v['proposals']))
ck('unclosed CH prevents old adoption or final flag from becoming true',not v['adoption_ready']and not v['scientific_stage_complete'])
for p in list(own(v)):
 if p['cells']==['CH']:addprofile(s,m,h,p['parameters'],gain=1,cell='CH')
# Existing a7 can require additional CH profiles beyond V3 winners; those remain visible.
v=run(s,m,h)
ck('existing CH obligations never silently removed',all(p in v['proposals']for p in actual(s,m,h)['proposals']))
sx,mx,hx=fixture();structural(sx,mx,hx);ablations(sx,mx,hx);allbrackets(sx,mx,hx)
addprofile(sx,mx,hx,dict(entries=384,frfcfs=256),gain=.8);addprofile(sx,mx,hx,dict(entries=768,frfcfs=256),gain=.9)
ck('positive conditional marginal continues even while total P0 speedup negative',any(p['profile']=='E1536_F256'for p in own(run(sx,mx,hx))))
sx,mx,hx=fixture();structural(sx,mx,hx);ablations(sx,mx,hx);allbrackets(sx,mx,hx)
for pp in sx['table'].values():
 for n,cc in pp.items():
  if n!='P0':cc['DH']['cycles']=round(10**12/.95)
regression=run(sx,mx,hx);tiers=regression['interaction_search']['uniform_resource_tiers']
ck('all negative results retain mandatory two distinct tiers without claiming improvement',all(not tiers[t]['improvement_proven']for t in('moderate','high_resource_potential'))and tiers['moderate']['profile']!=tiers['high_resource_potential']['profile']and len(regression['interaction_search']['CH_required_profiles'])>=2)

# Explicit gate rejects forged or unknown new inference, no default fallthrough.
s0,m0,h0=fixture();base=run(s0,m0,h0);p=own(base)[0]
for label,change in [('unknown phase',lambda q:q.update(phase='V3_UNKNOWN')),('subset population',lambda q:q['evidence'].update(full35_n=34)),
 ('physical clock key',lambda q:q['parameters'].update(clock=850)),('missing parent',lambda q:q['evidence'].update(parents=['P0','M16']))]:
 q=copy.deepcopy(base);q['proposals']=[copy.deepcopy(p)];change(q['proposals'][0]);sx=copy.deepcopy(s0)
 if label=='missing parent':sx['table'][ids[0]]['M16']['DH'].update(accepted=False,cycles=None,state=policy.TYPED)
 try:policy.validate_new_phases(q,sx,m0,h0,{})
 except (AssertionError,ValueError):rejected=True
 else:rejected=False
 ck('explicit phase gate rejects '+label,rejected)
pending_gate=copy.deepcopy(s0);pending_gate['table'][ids[0]]['P0']['CH'].update(accepted=False,cycles=None,state='PENDING')
try:policy.validate_new_phases(base,pending_gate,m0,h0,{})
except AssertionError:rejected=True
else:rejected=False
ck('explicit gate rederives initial350 ordering not merely parent full35',rejected)
forged=copy.deepcopy(base);forged['proposals']=[copy.deepcopy(p)];forged['proposals'][0]['evidence']['details']['structural_seed']='POSTHOC_UNDECLARED'
try:policy.validate_new_phases(forged,s0,m0,h0,{})
except AssertionError:rejected=True
else:rejected=False
ck('valid phase with undeclared contextual provenance cannot bypass policy replay',rejected)

# Main-only composition/restore preserves outer primary adapter and same journal.
class Journal:
 def __init__(self):self.calls=0
 def guard_decision(self,v):self.calls+=1;return dict(v,CPU_journal_object=id(self))
 def extend(self,p):return ['CPU_ONLY_EXTENSION_REACHED']
j=Journal();previous=lambda raw,view,hist:actual(raw,m0,hist);project=lambda raw:(copy.deepcopy(raw),{})
contract=dict(input_ids=ids);wrapped=owner.make_owner_recommend(previous,j,lambda:m0,project,contract,lambda c:None)
value=wrapped(s0,m0,h0)
ck('same live journal is final call after new explicit typed gate',value['CPU_journal_object']==id(j)and value['interaction_phase_gate']['status'].startswith('PASS'))
for error in (OSError('transient read'),AssertionError('source drift')):
 def badproject(raw):raise error
 w=owner.make_owner_recommend(previous,j,lambda:m0,badproject,contract,lambda c:None);value=w(s0,m0,h0)
 ck('owner '+type(error).__name__+' does not escape or terminate healthy scheduler',not value['proposals']and value['requires_engineering_review']and w.last_issue is not None)
adaptive=types.SimpleNamespace(recommend=previous);installation=owner.Installation(adaptive,wrapped,j,lambda:None,threading.RLock(),recommend_only_cpu_fixture=True)
installation.install();ck('private install preserves previous primary chain',adaptive.recommend.previous_recommend is previous)
installation.restore();ck('restore returns exact previous callable',adaptive.recommend is previous)
resource_proof=dict(status='PASS_SEPARATE_COMBINATION_RESOURCE_QUALIFICATION',proposal_id=p['proposal_id'],parameters=p['parameters'],
 initial_profile_padding_discount_applied=False,invented_fixed_margin_used=False,existing_dynamic_admission_retained=True,
 new_qualifier_reduces_forecast_or_limits=False,ratified_original_refresh_may_adjust_resource_caps=True,
 source_pins=[dict(path=str(H/'interaction_policy.py'),sha256=sha(H/'interaction_policy.py'))],
 cell_forecasts=[dict(input_digest=d,cell='DH',full_reserved_peak_bytes=8*1024**3,candidate_full_forecast_retained=True,new_qualifier_reduces_forecast_or_limits=False)for d in ids])
ext=owner.make_extend_guard(j,lambda q:copy.deepcopy(resource_proof),contract,lambda c:None)
ck('separate resource qualification permits only same-journal extension',ext(p)==['CPU_ONLY_EXTENSION_REACHED'])
badproof=copy.deepcopy(resource_proof);badproof['initial_profile_padding_discount_applied']=True
badext=owner.make_extend_guard(j,lambda q:badproof,contract,lambda c:None)
ck('initial profile discount cannot be blindly applied to combinations',badext(p)==[]and badext.last_issue['new_grants']==0)
registry=types.SimpleNamespace(extend=j.extend);inst=owner.Installation(adaptive,wrapped,j,lambda:None,threading.RLock(),registry,ext)
inst.install();ck('atomic private install includes resource gate on same journal without new owner',registry.extend is ext and adaptive.recommend is wrapped)
inst.restore();ck('coupled restore returns exact original recommendation and journal extension',registry.extend==j.extend and adaptive.recommend is previous)
inst.install();outer=lambda q:registry_captured(q);registry_captured=registry.extend;registry.extend=outer
try:inst.restore()
except AssertionError:rejected=True
else:rejected=False
ck('E restore refuses to bypass an active outer A scope-sync wrapper',rejected)
registry.extend=registry_captured;inst.restore()
extra=copy.deepcopy(m0);extra['points'].append(dict(extra['points'][0],scientific_role=owner.ROLE,cohort='CPU-DH-M16-V2'));extra['supplemental_dispatch_view']={}
ck('outer composition strips supplemental solely for scientific inference',len(own(wrapped(s0,extra,h0)))==6)

# Real generator with inherited canonical270 options; no simulator execution.
point=next(p for p in m0['points']if p['profile']=='P0'and p['cell']=='DH');spec=read(R/'control/specs'/(point['cohort']+'.json'))
texts=[P(x['path']).read_text()for x in spec['configs']];before=gen.effective_options(texts)
vectors=[policy.normalize(p)for _,p in policy.SEEDS]+[dict(policy.BASE,entries=1536,merge=32,miss_queue=256,frfcfs=512)]
for vector in vectors:
 after,trans=gen.generate(texts,vector);opt=gen.effective_options(after);assert set(opt)==set(before)
 assert all(opt[k]==before[k]for k in before if k not in (gen.L2,gen.FR))
 canonical=copy.deepcopy(spec['expected_options'])
 for k in (gen.L2,gen.FR):canonical[k]=[opt[k]]
 assert len(canonical)==270 and all(canonical[k]==spec['expected_options'][k]for k in canonical if k not in (gen.L2,gen.FR))
ck('real generator qualifies seeds and expanded joint vectors preserving270 identity',True)
pins=[dict(path=str(path),sha256=sha(path))for path in [R/'tools/l2_adaptive.py',P(cfg['source_paths']['supplement']),gp,R/'tools/l2_config_generator.py',H/'interaction_policy.py',H/'owner_adapter.py']]
contract=owner.build_contract(R,pins);owner.check_contract(contract);put(H/'SCIENTIFIC_CONTRACT.json',contract)
ck('actual70 P0 bindings inputSHA clocks capacity CoreFWbinary and source pins verified',True)
receipt=dict(schema='INTERACTION_V3_CPU_QUALIFICATION',status='PASS',count=len(checks),checks=checks,examples=examples,
 source_pins=pins,candidate_sources={p.name:sha(p)for p in(H/'interaction_policy.py',H/'owner_adapter.py')},
 model_starts=0,production_changes=0,production_grants=0,scientific_cycles='ALL SYNTHETIC CPU FIXTURES')
put(H/'CPU_QUALIFICATION.json',receipt);print(json.dumps(receipt))



