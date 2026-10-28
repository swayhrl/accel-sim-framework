"""Pure, uninstalled full35 interaction search V3. No writes or registration."""
import copy,hashlib,json,math
BASE=dict(entries=192,merge=4,miss_queue=32,frfcfs=64)
AXES=tuple(BASE);PREFIX=dict(entries='E',merge='M',miss_queue='Q',frfcfs='F')
EPS=1e-12
SCHEMA='DTC_L2_MLP_INTERACTION_POLICY_V3'
TYPED='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY'
NEGATIVE={'FAIL_L2MLP_ARCHIVED_NO_RETRY','L2_MLP_NATIVE_NEGATIVE_UNACCEPTED'}
INITIAL={'P0':dict(BASE),**{PREFIX[k]+str(BASE[k]*m):dict(BASE,**{k:BASE[k]*m})for k in AXES for m in (2,4)}}
SEEDS=[('entries_merge',dict(entries=768,merge=8)),('entries_send',dict(entries=768,miss_queue=128)),
 ('entries_schedule',dict(entries=768,frfcfs=256)),('merge_send',dict(merge=8,miss_queue=128)),
 ('merge_schedule',dict(merge=8,frfcfs=256)),('wide',dict(entries=768,merge=8,miss_queue=128,frfcfs=256))]
PHASES={'V3_STRUCTURAL_SEED','V3_WIDE_ABLATION','V3_CONTEXT_BRACKET','V3_CONTEXT_BOUNDARY',
 'V3_CONTEXT_SATURATION_CONFIRM','V3_UNIFORM_CH_MATCH'}
OLD_PHASES={'INITIAL','CH_MATCH','BOUNDARY_EXTENSION','PAIR_COMBINATION','MULTI_COMBINATION',
 'V2_BOUNDARY_VALIDATION','V2_FIXED_CONTEXT_PAIR_VALIDATION','V2_FIXED_CONTEXT_UNION_VALIDATION',
 'V2_BEST_GLOBAL_UNIFORM_CH_MATCH','V2_FIXED_SUITE_UNIFORM_CH_MATCH','V2_UNIFORM_CH_MATCH'}

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def normalize(v):
 if not isinstance(v,dict)or set(v)-set(BASE):raise ValueError('Forbidden scientific/parameter key')
 p=dict(BASE,**v)
 if any(type(n)is not int or not BASE[k]<=n<=2147483647 for k,n in p.items()):raise ValueError('Invalid source integer')
 if p['entries']>1073741823:raise ValueError('Source MSHR overflow bound')
 return p
def key(p):return tuple(p[k]for k in AXES)
def name(p):return '_'.join(PREFIX[k]+str(p[k])for k in AXES if p[k]!=BASE[k])or'P0'
def proposal_id(p,cell,ids):return digest(dict(parameters=p,cell=cell,inputs=ids))
def gm(v):return math.exp(math.fsum(math.log(x)for x in v)/len(v))if v else None
def logical(p):return dict(l2_data_bytes=10485760,mshr_address_entries_total=40*p['entries'],
 mshr_request_references_upper_bound=40*p['entries']*p['merge'],miss_queue_request_slots_total=40*p['miss_queue'],
 frfcfs_request_slots_total=20*p['frfcfs'],shared_credit_limit_per_controller=p['frfcfs']+191,private_credits_per_controller=2,
 physical_area_bytes=None,Host_RSS_bound_bytes=None,
 Host_RSS_qualification='Separate full forecast/host-cgroup gates; no initial-only padding discount or invented margin')

class Evidence:
 def __init__(self,summary,scope,history,verified):
  self.summary=summary;self.scope=scope;self.history=history;self.verified=verified
  self.ids=sorted({p['input_digest']for p in scope['points']})
  assert len(self.ids)==35 and set(summary['table'])==set(summary['programs'])==set(self.ids),'Frozen35 domain changed'
  assert scope.get('frozen_input_count',35)==35
  assert not any(p.get('scientific_role')for p in scope['points']),'Supplemental scope must be stripped'
  self.registry=copy.deepcopy(INITIAL)
  for n,v in history.get('profiles',{}).items():
   p=normalize(v.get('parameters',v));assert n not in self.registry or self.registry[n]==p,'Profile collision'
   self.registry[n]=p
  self.registered={};self.meta={};cohorts=set()
  for point in scope['points']:
   assert point['cohort']not in cohorts,'Duplicate cohort';cohorts.add(point['cohort'])
   assert point['profile']in self.registry and point['cell']in ('CH','DH')
   d=point['input_digest'];m=(point['program'],point.get('suite','UNKNOWN'))
   assert self.meta.setdefault(d,m)==m
   assert (summary['programs'][d]['program'],summary['programs'][d]['suite'])==m
   slot=(point['profile'],point['cell'],d);assert slot not in self.registered,'Duplicate primary slot'
   self.registered[slot]=point
  assert not set(summary['profiles'])-set(self.registry),'Unregistered profile identity'
  vector_aliases={}
  for n,c,d in self.registered:vector_aliases.setdefault(key(self.registry[n]),set()).add(n)
  assert all(len(v)==1 for v in vector_aliases.values()),'Same registered parameter vector has multiple aliases'
  for d,pp in summary['table'].items():
   for n,cc in pp.items():
    for c,row in cc.items():
     assert (n,c,d)in self.registered and row['cohort']==self.registered[n,c,d]['cohort'],'Summary slot identity mismatch'
 def row(self,d,n,c='DH'):return self.summary['table'][d].get(n,{}).get(c,{})
 def good(self,d,n,c='DH'):
  r=self.row(d,n,c);return r.get('accepted')is True and type(r.get('cycles'))is int and r['cycles']>0
 def full(self,n,c='DH'):return all(self.good(d,n,c)for d in self.ids)
 def terminal(self,d,n,c='DH'):
  r=self.row(d,n,c)
  if self.good(d,n,c)or r.get('state')in NEGATIVE:return True
  if r.get('state')!=TYPED:return False
  p=self.verified.get(r.get('cohort'),{})
  return p.get('verified')is True and p.get('uuid')==r.get('uuid')and p.get('cycles')is None and p.get('performance_accepted')is False
 def aliases(self,p):return sorted(n for n,v in self.registry.items()if v==p)
 def resolve(self,p):
  aliases=self.aliases(p)
  # Preserve the exact already-registered alias; never retry via a new label.
  present=[n for n in aliases if any((n,'DH',d)in self.registered for d in self.ids)]
  assert len(present)<=1,'Duplicate scientific vector aliases require reconciliation'
  return present[0]if present else aliases[0]if aliases else name(p)
 def ratio(self,a,b):
  assert self.full(a)and self.full(b)
  return gm([self.row(d,a)['cycles']/self.row(d,b)['cycles']for d in self.ids])
 def parents(self,names):return sorted(set(['P0']+names))
 def missing(self,names):return {n:[d for d in self.ids if not self.good(d,n)]for n in names if not self.full(n)}

def augment(existing,summary,scope,history=None):
 history=history or{};out=copy.deepcopy(existing)
 out['interaction_policy']=dict(schema=SCHEMA,epsilon=EPS,six_seeds_are_not_total_cap=True,
  scope='primary frozen35 only; no supplemental union',implementation='SEEDS_ABLATIONS_CONTEXT_BRACKETS_DOUBLING_CH_CLOSURE')
 state=out['interaction_search']=dict(phase='INITIAL_GATE',notes=[],ladders=[],new_proposals=0,
  declared_seed_count=6,declared_context_ladder_count=14,DH_work_closed=False,CH_work_closed=False)
 notes=state['notes'];verified={v['cohort']:v for v in existing.get('verified_typed_engineering_negatives',[])}
 ev=Evidence(summary,scope,history,verified);ids=ev.ids
 def hold(reason,**details):notes.append(dict(action=reason,**details))
 def blockfinal():out.update(scientific_stage_complete=False,adoption_ready=False)
 waiting=[dict(profile=n,cell=c,input_digest=d)for n in INITIAL for c in (('CH','DH')if n=='P0'else('DH',))for d in ids
  if(n,c,d)not in ev.registered or not ev.terminal(d,n,c)]
 if waiting:hold('WAIT_INITIAL_350_TERMINAL',missing=waiting);blockfinal();return out
 if not ev.full('P0'):hold('FULL35_P0_HOLD',missing=ev.missing(['P0']));blockfinal();return out
 proposals=out.setdefault('proposals',[])
 known=set(history.get('proposal_ids',[]))|{p['proposal_id']for p in history.get('proposals',[])if'proposal_id'in p}
 known|={p['proposal_id']for p in proposals}
 outstanding=[]
 def add(p,phase,parents,reason,details=None,cell='DH'):
  try:p=normalize(p)
  except ValueError as err:hold('STOP_SOURCE_BOUND',phase=phase,error=str(err),parameters=p);return 'SOURCE_STOP'
  n=ev.resolve(p);parents=ev.parents(parents);missing=ev.missing(parents)
  if missing:hold('FULL35_PARENT_HOLD',profile=n,parents_missing=missing);return 'HOLD'
  present=[d for d in ids if(n,cell,d)in ev.registered]
  if present:
   if len(present)!=35:hold('PARTIAL_REGISTERED_HOLD',profile=n,cell=cell,n=len(present));return 'HOLD'
   if ev.full(n,cell):return 'COMPLETE'
   hold('REGISTERED_PENDING_OR_UNACCEPTED_HOLD',profile=n,cell=cell,missing=[d for d in ids if not ev.good(d,n,cell)])
   return 'HOLD'
  pid=proposal_id(p,cell,ids)
  if pid in known:
   hold('KNOWN_PROPOSAL_AWAIT_REGISTRY',profile=n,cell=cell,proposal_id=pid);return 'PENDING'
  rc=history.get('resource_constraints',{})
  if rc:
   assert isinstance(rc.get('reason'),str)and rc['reason'].strip(),'Resource constraint needs evidence reason'
   assert all(k in BASE and type(v)is int and v>=BASE[k]for k,v in rc.get('max_parameters',{}).items())
  if pid in rc.get('blocked_proposal_ids',[])or any(p[k]>v for k,v in rc.get('max_parameters',{}).items()):
   hold('RESOURCE_QUALIFICATION_HOLD',profile=n,cell=cell,constraint=copy.deepcopy(rc));return 'RESOURCE_HOLD'
  value=dict(proposal_id=pid,profile=n,parameters=p,cells=[cell],phase=phase,
   workloads=[dict(input_digest=d,program=ev.meta[d][0],suite=ev.meta[d][1])for d in ids],
   new_cells=[dict(input_digest=d,cell=cell)for d in ids],expected_input_count=35,new_cell_count=35,
   evidence=dict(parents=parents,full35_population=ids,full35_n=35,details=details or{}),
   reason=reason,logical_resources=logical(p),supplementary_policy=SCHEMA,requires_coordinator_registration=True,
   requires_separate_host_RSS_qualification=True,initial_padding_discount_applicable=False)
  proposals.append(value);known.add(pid);state['new_proposals']+=1;outstanding.append(n);return 'PROPOSED'
 state['phase']='STRUCTURAL_SEEDS';seed_complete=True
 seedvectors=[]
 for label,override in SEEDS:
  p=normalize(override);seedvectors.append(p)
  parents=[ev.resolve(dict(BASE,**{k:p[k]}))for k in AXES if p[k]!=BASE[k]]
  # All seed axes use initial parents (merge M8), never missing OFAT M16.
  result=add(p,'V3_STRUCTURAL_SEED',parents,'Predeclared uniform masking probe; no positive-parent filter',dict(structural_seed=label))
  if result!='COMPLETE':seed_complete=False
 # Every dependent probe requires its actual seed full35; independent contexts may progress.
 if not seed_complete:blockfinal()
 state['phase']='WIDE_ABLATIONS';wide=seedvectors[-1];wide_n=ev.resolve(wide);ablations_complete=True
 for axis in AXES:
  p=dict(wide,**{axis:BASE[axis]})
  parents=[wide_n]+[ev.resolve(dict(BASE,**{k:p[k]}))for k in AXES if p[k]!=BASE[k]]
  if add(p,'V3_WIDE_ABLATION',parents,'Predeclared one-axis removal, independent of observed seed gain',dict(removed_axis=axis))!='COMPLETE':ablations_complete=False
 if not ablations_complete:blockfinal()
 state['phase']='CONDITIONAL_LADDERS'
 contexts=[]
 for label,override in SEEDS[:-1]:
  seed=normalize(override)
  for axis in AXES:
   if seed[axis]!=BASE[axis]:contexts.append((label+'__'+axis,axis,dict(seed,**{axis:BASE[axis]}),seed))
 for axis in AXES:contexts.append(('wide__'+axis,axis,dict(wide,**{axis:BASE[axis]}),wide))
 assert len(contexts)==14
 allclosed=seed_complete and ablations_complete
 for label,axis,context,seed in contexts:
  entry=dict(context_id=label,axis=axis,fixed_context=context,status='BRACKETING');state['ladders'].append(entry)
  cn=ev.resolve(context);sn=ev.resolve(seed)
  missing=ev.missing([cn,sn])
  if missing:entry.update(status='PARENT_HOLD',missing=missing);allclosed=False;continue
  # Predeclared 1x/2x/4x bracket in this exact context, even if all OFAT gains are flat.
  bracket_ok=True
  for multiplier in (2,4):
   p=dict(context,**{axis:BASE[axis]*multiplier})
   parents=[cn,sn]
   if multiplier==4:parents.append(ev.resolve(dict(context,**{axis:BASE[axis]*2})))
   status=add(p,'V3_CONTEXT_BRACKET',parents,'Complete fixed contextual bracket before local stopping',dict(context_id=label,axis=axis,multiplier=multiplier))
   if status!='COMPLETE':bracket_ok=False;allclosed=False;entry.update(status='BRACKET_'+status);break
  if not bracket_ok:continue
  levels={BASE[axis]:cn}
  for n,p in ev.registry.items():
   if all(p[k]==context[k]for k in AXES if k!=axis)and p[axis]>=BASE[axis]:
    if any((n,'DH',d)in ev.registered for d in ids):
     assert p[axis]not in levels or levels[p[axis]]==n,'Duplicate contextual vector'
     levels[p[axis]]=n
  ordered=sorted(levels.items());entry['levels']=[dict(value=v,profile=n,accepted35=ev.full(n))for v,n in ordered]
  if any(not ev.full(n)for _,n in ordered):entry['status']='REGISTERED_LEVEL_EVIDENCE_HOLD';allclosed=False;continue
  assert len(ordered)>=3
  (pv,pn),(lv,ln),(tv,tn)=ordered[-3:]
  marginal=ev.ratio(ln,tn);previous=ev.ratio(pn,ln)
  entry.update(previous_marginal_GM=previous,top_marginal_GM=marginal,total_P0_GM=ev.ratio('P0',tn))
  if marginal<=1+EPS and previous<=1+EPS:
   entry.update(status='STOP_TWO_NONPOSITIVE_CONTEXTUAL_MARGINALS',scope='Local tested context only; no global optimum proof');continue
  p=dict(context,**{axis:tv*2})
  phase='V3_CONTEXT_BOUNDARY'if marginal>1+EPS else'V3_CONTEXT_SATURATION_CONFIRM'
  status=add(p,phase,[cn,pn,ln,tn,sn],'Positive conditional marginal continues; one nonpositive marginal requires confirmation',
   dict(context_id=label,axis=axis,previous_marginal_GM=previous,top_marginal_GM=marginal,total_P0_GM=entry['total_P0_GM']))
  entry['status']='NEXT_'+status
  if status=='SOURCE_STOP':entry['status']='STOP_SOURCE_BOUND'
  else:allclosed=False # resource/evidence holds require explicit review; never claim saturation
 # Existing OFAT/combination work remains part of the same scientific stage.
 other_dh=[p for p in proposals if p.get('cells')==['DH']]
 if not allclosed or other_dh:blockfinal();return out
 state['DH_work_closed']=True;state['phase']='CH_CLOSURE'
 completed=[n for n in summary['profiles']if ev.full(n)]
 best=min(completed,key=lambda n:(-ev.ratio('P0',n),key(ev.registry[n]),n))
 winners={best}if ev.ratio('P0',best)>1+EPS else set()
 # Predeclared, disjoint resource tiers, not an area estimate. Both require CH
 # even when all measured non-P0 configurations regress or are exactly flat.
 moderate_limits={k:2*v for k,v in BASE.items()}
 tier_candidates=dict(moderate=[n for n in completed if n!='P0'and all(ev.registry[n][k]<=moderate_limits[k]for k in AXES)],
  high_resource_potential=[n for n in completed if any(ev.registry[n][k]>moderate_limits[k]for k in AXES)])
 tiers={};tier_missing=False
 for tier,candidates in tier_candidates.items():
  if not candidates:
   tier_missing=True;hold('UNIFORM_RESOURCE_TIER_EVIDENCE_HOLD',tier=tier);tiers[tier]=dict(status='HOLD_NO_FULL35_UNIFORM_PROFILE');continue
  n=min(candidates,key=lambda n:(-ev.ratio('P0',n),key(ev.registry[n]),n));winners.add(n)
  tiers[tier]=dict(status='BEST_OBSERVED_FULL35_IN_FIXED_RESOURCE_TIER',profile=n,parameters=ev.registry[n],
   DH_P0_over_DH_GM=ev.ratio('P0',n),improvement_proven=ev.ratio('P0',n)>1+EPS,
   full35_population=ids,logical_resources=logical(ev.registry[n]),CH_full35=ev.full(n,'CH'))
 state['uniform_resource_tiers']=dict(baseline=dict(profile='P0',DH_P0_over_DH_GM=1.0,CH_full35=ev.full('P0','CH')),
  moderate_limits=moderate_limits,ranking='higher full35 DH GM, then lexicographic E/M/Q/F values, then profile; not physical area',**tiers)
 for suite in sorted({m[1]for m in ev.meta.values()}):
  pop=[d for d in ids if ev.meta[d][1]==suite]
  if len(pop)<3:continue
  useful=[n for n in completed if gm([ev.row(d,'P0')['cycles']/ev.row(d,n)['cycles']for d in pop])>=1.01
   and sum(ev.row(d,'P0')['cycles']/ev.row(d,n)['cycles']>1+EPS for d in pop)>len(pop)/2]
  if useful:winners.add(min(useful,key=lambda n:(-gm([ev.row(d,'P0')['cycles']/ev.row(d,n)['cycles']for d in pop]),key(ev.registry[n]),n)))
 state['best_observed_uniform_profile']=best;state['best_observed_uniform_GM']=ev.ratio('P0',best)
 state['CH_required_profiles']=sorted(winners);chclosed=not tier_missing
 for n in sorted(winners):
  if add(ev.registry[n],'V3_UNIFORM_CH_MATCH',[n],'Complete same35 CH for mandatory moderate/high tiers and uniform global/fixed-suite candidates',cell='CH')!='COMPLETE':chclosed=False
 if any(p.get('cells')==['CH']for p in proposals):chclosed=False
 outstanding_ch=sorted({n for n,c,d in ev.registered if c=='CH'and not ev.full(n,'CH')})
 if outstanding_ch:state['registered_CH_missing_profiles']=outstanding_ch;chclosed=False
 state['CH_work_closed']=chclosed;state['phase']='CLOSED_SUBJECT_TO_EXISTING_GUARDS'if chclosed else'CH_PENDING_OR_HOLD'
 if not chclosed:blockfinal()
 # Never promote a false flag, clear engineering provenance, or override journal.
 return out

def validate_new_phases(decision,summary,scope,history,verified):
 """Explicit final inference fence; unknown phases and subset evidence fail closed."""
 ev=Evidence(summary,scope,history,verified);out=copy.deepcopy(decision)
 for p in out.get('proposals',[]):
  if p.get('phase')in OLD_PHASES:
   assert p.get('supplementary_policy')!=SCHEMA,'V3 proposal cannot hide in an old phase'
   continue # trusted, separately gated prior chain; never a V3 inference bypass
  assert p.get('phase')in PHASES and p.get('supplementary_policy')==SCHEMA,'Unknown inference phase'
  q=normalize(p['parameters']);assert p['parameters']==q and p['profile']==ev.resolve(q)
  assert p['cells']in (['DH'],['CH'])and (p['phase']=='V3_UNIFORM_CH_MATCH')==(p['cells']==['CH'])
  c=p['cells'][0];assert p['proposal_id']==proposal_id(q,c,ev.ids)
  assert p['new_cell_count']==p['expected_input_count']==35
  assert p['new_cells']==[dict(input_digest=d,cell=c)for d in ev.ids]
  assert p['workloads']==[dict(input_digest=d,program=ev.meta[d][0],suite=ev.meta[d][1])for d in ev.ids]
  e=p['evidence'];assert e['full35_n']==35 and e['full35_population']==ev.ids
  assert e['parents']and 'P0'in e['parents']and not ev.missing(e['parents']),'V3 actual source parent not full35'
  assert p['requires_separate_host_RSS_qualification']is True and p['initial_padding_discount_applicable']is False
 # Re-derive the declared algorithm from the already gated OLD proposal list.
 # This also fences initial350 terminal, seed vectors, context and ordering;
 # a syntactically valid new phase cannot smuggle in an arbitrary experiment.
 prior=copy.deepcopy(decision)
 prior['proposals']=[p for p in prior.get('proposals',[])if p.get('supplementary_policy')!=SCHEMA]
 rederived=augment(prior,summary,scope,history)
 actual=[p for p in out.get('proposals',[])if p.get('supplementary_policy')==SCHEMA]
 expected=[p for p in rederived.get('proposals',[])if p.get('supplementary_policy')==SCHEMA]
 assert actual==expected,'V3 proposals do not match the declared algorithm/initial gate'
 out['interaction_phase_gate']=dict(status='PASS_EXPLICIT_V3_PHASES_FULL35_PARENTS',new_phases=sorted(PHASES))
 return out

