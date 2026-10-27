"""Pure adaptive proposal generator. Never registers, launches, retries or edits results.

recommend(summary, scope, history=None) -> JSON-serializable decisions/proposals.
summary is Agent D's DTC_L2_MLP_AUTO_SUMMARY_V1. history['profiles'] maps names
to {parameters, kind, ...}; all registered/proposed names must be retained there.
The coordinator must register each accepted proposal as a NEW finite matrix.
"""
import hashlib
import itertools
import json
import math

BASE = {'entries':192, 'merge':4, 'miss_queue':32, 'frfcfs':64}
FACTORS = tuple(BASE)
PREFIX = {'entries':'E', 'merge':'M', 'miss_queue':'Q', 'frfcfs':'F'}
INITIAL = {'P0':BASE, **{PREFIX[k]+str(BASE[k]*v):dict(BASE, **{k:BASE[k]*v})
            for k in FACTORS for v in (2,4)}}
TERMINAL_NEGATIVE = {'FAIL_L2MLP_ARCHIVED_NO_RETRY', 'L2_MLP_NATIVE_NEGATIVE_UNACCEPTED'}
MIN_GAIN = 1.01
CONTRACT = {
 'schema':'DTC_L2_MLP_ADAPTIVE_CONTRACT_V1',
 'fixed_before_results':True,
 'minimum_whole_common_population_GM':MIN_GAIN,
 'boundary_incremental_GM':MIN_GAIN,
 'boundary_requires_upper_level_gain':True,
 'comparison_population':'identical accepted identities for every candidate compared',
 'full_suite_required_for_formal_candidate':True,
 'whole_uniform_profile_only':True,
 'provisional_search_with_terminal_negatives':True,
 'missing_imputation':False,
 'family_extension_multiplier':2,
 'combination_pairs':[['entries','merge'],['entries','miss_queue'],
                      ['entries','frfcfs'],['merge','miss_queue'],['merge','frfcfs']],
 'combination_rule':'one best family level per pair; if all significant directions exist also one union, never Cartesian product',
 'future_combination_escalation':'same supported direction levels can be doubled only after its whole-suite single-factor boundary evidence qualifies',
 'candidate_classes':['baseline','moderate','high_resource'],
 'moderate_rule':'excluding high-resource vector, minimum normalized logical slot sum among whole-suite profiles with DH/P0 GM >=1.01; absent benefit report lowest-cost remaining tested profile as unimproved',
 'high_resource_rule':'maximum normalized logical slot sum among full-suite tested profiles, tie broken by higher whole-suite DH/P0 GM; improvement_proven may be false',
 'distinct_classes_required':True,
 'insufficient_distinct_classes':'fewer than two fully accepted non-P0 parameter vectors cannot be adopted as the requested three-class comparison',
 'CH_matching':'all frozen identities for both selected uniform classes; reuse already registered exact CH cells only',
 'statistics':'suite rows and negatives retained; GM never selects best profile per input',
 'no_total_start_cap':True,
 'stopping':'saturation (<1.01 marginal), regression, source bounds, observed resource rejection or missing scientific evidence',
 'engineering_failures':'preserve UUID; coordinator diagnoses; never retry actual consumed identity',
 'only_parameter_keys':list(FACTORS),
 'fixed_clocks':'1410:1410:1410:850 MHz',
 'fixed_L2_bytes':10485760,
 'area_matching':False,
 'FRFCFS_credit_coupling':'shared per controller = frfcfs + 191; private credits=2'
}

def _gm(values):
    return math.exp(sum(math.log(x) for x in values)/len(values)) if values else None

def _params(p):
    if not isinstance(p,dict) or set(p)-set(BASE):raise ValueError('Unsupported parameter family')
    out=dict(BASE,**p)
    for k,v in out.items():
        if type(v) is not int or not BASE[k]<=v<=2147483647:raise ValueError('Invalid '+k)
    if out['entries']>1073741823:raise ValueError('MSHR constructor overflow bound')
    return out

def profile_name(parameters):
    p=_params(parameters)
    return '_'.join(PREFIX[k]+str(p[k]) for k in FACTORS if p[k]!=BASE[k]) or 'P0'

def _key(p):return tuple(p[k] for k in FACTORS)

def resource_cost(p):
    p=_params(p)
    return dict(l2_data_bytes=10485760,mshr_entries=40*p['entries'],
        mshr_request_refs=40*p['entries']*p['merge'],miss_queue_slots=40*p['miss_queue'],
        FRFCFS_slots=20*p['frfcfs'],shared_credit_limit_per_controller=p['frfcfs']+191,
        area_bytes='UNKNOWN; logical slots are not a hardware area model',
        normalized_slot_score=(p['entries']/192+p['entries']*p['merge']/(192*4)
                               +p['miss_queue']/32+p['frfcfs']/64))

def recommend(summary,scope,history=None):
    history=history or {}
    rows=summary.get('table',{})
    programs=summary.get('programs',{})
    scope_ids={p['input_digest'] for p in scope['points']}
    expected=scope.get('frozen_input_count',35)
    if len(scope_ids)!=expected:raise ValueError('Scope frozen input count mismatch')
    if set(rows)!=scope_ids or set(programs)!=scope_ids:raise ValueError('Summary/scope input identity mismatch')
    ids=sorted(scope_ids)
    workload=[dict(input_digest=d,program=programs[d]['program'],suite=programs[d]['suite']) for d in ids]
    registry={k:dict(v) for k,v in INITIAL.items()}
    for name,value in history.get('profiles',{}).items():
        p=_params(value.get('parameters',value))
        if name in registry and p!=registry[name]:raise ValueError('Profile identity collision '+name)
        registry[name]=p
    observed=set(summary.get('profiles',[]))
    if observed-set(registry):raise ValueError('Unknown profile metadata '+str(sorted(observed-set(registry))))
    registered={(p['profile'],p['cell'],p['input_digest']) for p in scope['points']}
    proposed=set(history.get('proposal_ids',[]))
    for value in history.get('proposals',[]):
        if 'proposal_id' in value:proposed.add(value['proposal_id'])
    plans=[];decisions=[]

    def cell(d,p,c):return rows[d].get(p,{}).get(c,{})
    def good(d,p,c):
        x=cell(d,p,c)
        return x.get('accepted') is True and type(x.get('cycles')) is int and x['cycles']>0
    def terminal(d,p,c):
        x=cell(d,p,c)
        return good(d,p,c) or x.get('state') in TERMINAL_NEGATIVE
    def population(profiles,c='DH'):
        return [d for d in ids if all(good(d,p,c) for p in profiles)]
    def ratio(a,b,pop,c='DH'):
        return _gm([cell(d,a,c)['cycles']/cell(d,b,c)['cycles'] for d in pop])
    def ready(p,c='DH'):return all(terminal(d,p,c) for d in ids)
    def full(p,c='DH'):return all(good(d,p,c) for d in ids)
    def evidence(names):
        pop=population(names)
        return dict(population=pop,n=len(pop),expected_n=expected,missing_n=expected-len(pop),
                    status='FULL_SUITE' if len(pop)==expected else 'PROVISIONAL_COMMON_POPULATION',
                    negatives={p:[d for d in ids if terminal(d,p,'DH') and not good(d,p,'DH')] for p in names})
    def propose(p,c,phase,why,ev):
        p=_params(p);name=profile_name(p)
        # Exact parameter identity is stronger than a display name.
        aliases=[n for n,v in registry.items() if v==p]
        if aliases:name=sorted(aliases,key=lambda x:(x!='P0',x))[0]
        missing=[d for d in ids if not any((n,c,d) in registered for n in aliases+[name])]
        if not missing:return False
        digest=hashlib.sha256(json.dumps(dict(parameters=p,cell=c,inputs=ids),sort_keys=True).encode()).hexdigest()
        if digest in proposed:return False
        constraints=history.get('resource_constraints',{})
        if digest in constraints.get('blocked_proposal_ids',[]):
            decisions.append(dict(action='RESOURCE_HOLD',profile=name,cell=c,reason=constraints.get('reason','Explicit observed resource constraint')))
            return False
        for k,bound in constraints.get('max_parameters',{}).items():
            if k not in BASE or type(bound) is not int:raise ValueError('Invalid resource bound')
            if p[k]>bound:
                decisions.append(dict(action='RESOURCE_HOLD',profile=name,cell=c,reason=constraints.get('reason','Measured resource/source bound'),bound={k:bound}))
                return False
        plans.append(dict(proposal_id=digest,profile=name,parameters=p,cells=[c],phase=phase,
            workloads=workload,expected_input_count=expected,new_cells=[dict(input_digest=d,cell=c) for d in missing],
            new_cell_count=len(missing),reuse_policy='only exact already registered profile/cell/input; never restart consumed identity',
            reason=why,evidence=ev,logical_resources=resource_cost(p),requires_coordinator_registration=True))
        proposed.add(digest)
        return True

    # Initial matrix is complete by declaration, not by picking successes.
    absent=[]
    for p in INITIAL:
        for c in (['CH','DH'] if p=='P0' else ['DH']):
            if not all((p,c,d) in registered for d in ids):absent.append((p,c))
    if absent:
        for p,c in absent:propose(registry[p],c,'INITIAL','Complete authorized whole-frozen-suite initial matrix',{})
        return dict(schema='DTC_L2_MLP_ADAPTIVE_DECISIONS_V1',state='INITIAL_MATRIX_INCOMPLETE',
                    proposals=plans,decisions=decisions,formal_candidates=[],blocked_reason='Initial registration incomplete',
                    adoption_ready=False,scientific_stage_complete=False,requires_engineering_review=False,contract=CONTRACT)
    waiting=[p for p in INITIAL if not ready(p)]
    if not ready('P0','CH'):waiting.append('P0_CH')
    if waiting:
        engineering=[dict(profile=p,cell=c,input_digest=d,state=cell(d,p,c).get('state'))
            for p,c,d in sorted(registered) if 'ENGINEERING' in str(cell(d,p,c).get('state',''))]
        return dict(schema='DTC_L2_MLP_ADAPTIVE_DECISIONS_V1',state='WAIT_INITIAL_TERMINAL',
                    pending_profiles=waiting,proposals=[],decisions=[],formal_candidates=[],
                    blocked_reason='Pending/engineering-only cells cannot rank or count as terminal failures',
                    adoption_ready=False,scientific_stage_complete=False,requires_engineering_review=bool(engineering),
                    engineering_cells=engineering,contract=CONTRACT)

    family_best={};family_levels={}
    for factor in FACTORS:
        levels=sorted([(p[factor],n) for n,p in registry.items() if p[factor]>BASE[factor]
                       and all(p[k]==BASE[k] for k in FACTORS if k!=factor)],key=lambda x:(x[0],x[1]))
        # A registered extension that is still live blocks another expansion of that family.
        if any(n in observed and not ready(n) for _,n in levels):
            decisions.append(dict(action='WAIT_FAMILY',factor=factor,reason='Registered higher level pending'))
        complete=[(v,n) for v,n in levels if n in observed and ready(n)]
        if not complete:continue
        names=['P0']+[n for _,n in complete];ev=evidence(names);pop=ev['population']
        if not pop:
            decisions.append(dict(action='EVIDENCE_HOLD',factor=factor,reason='No common accepted population',evidence=ev));continue
        gains={n:ratio('P0',n,pop) for _,n in complete}
        beneficial=[(v,n) for v,n in complete if gains[n]>=MIN_GAIN]
        if beneficial:
            winner=max(beneficial,key=lambda x:(gains[x[1]],-x[0]))
            family_best[factor]=winner[1]
            family_levels[factor]=[(v,n,gains[n]) for v,n in beneficial]
        topv,top=complete[-1]
        lower=complete[-2][1] if len(complete)>1 else 'P0'
        marginal=ratio(lower,top,pop)
        lower_gain=ratio('P0',lower,pop)
        if len(complete)<2 or gains[top]<MIN_GAIN or marginal<MIN_GAIN:
            decisions.append(dict(action='STOP_FAMILY_SATURATION_OR_REGRESSION',factor=factor,
                top_profile=top,top_GM=gains[top],marginal_GM=marginal,lower_GM=lower_gain,evidence=ev))
        elif not any(n in observed and not ready(n) for _,n in levels):
            value=topv*2
            try:p=_params({factor:value})
            except ValueError as exc:
                decisions.append(dict(action='STOP_SOURCE_BOUND',factor=factor,reason=str(exc)));continue
            propose(p,'DH','BOUNDARY_EXTENSION','Upper boundary has >=1% total and >=1% marginal whole-common-population gain; still improving',dict(ev,marginal_GM=marginal,lower_GM=lower_gain))

    # Completed single-factor directions generate only evidence-supported pairs.
    for a,b in CONTRACT['combination_pairs']:
        if a in family_best and b in family_best:
            left,right=family_best[a],family_best[b]
            p=dict(BASE);p[a]=registry[left][a];p[b]=registry[right][b]
            ev=evidence(['P0',left,right]);pop=ev['population']
            gains=[ratio('P0',n,pop) for n in (left,right)]
            if not pop or any(g is None or g<MIN_GAIN for g in gains):
                decisions.append(dict(action='COMBINATION_EVIDENCE_HOLD',parents=[left,right],
                                      reason='Directions do not both retain >=1% gain on identical paired population',evidence=ev))
                continue
            propose(p,'DH','PAIR_COMBINATION','Both single-factor directions have >=1% whole-common-population DH gain',
                    dict(ev,parents=[left,right],parent_GMs=gains))
    if len(family_best)>=3:
        parents=list(family_best.values());p=dict(BASE)
        for factor,name in family_best.items():p[factor]=registry[name][factor]
        ev=evidence(['P0']+parents);pop=ev['population'];gains=[ratio('P0',n,pop) for n in parents]
        if pop and all(g is not None and g>=MIN_GAIN for g in gains):
            propose(p,'DH','MULTI_COMBINATION','One union of significant single-factor directions; no Cartesian expansion',dict(ev,parents=parents,parent_GMs=gains))
        else:
            decisions.append(dict(action='COMBINATION_EVIDENCE_HOLD',parents=parents,
                                  reason='All directions must retain >=1% gain on one common population',evidence=ev))

    # Never rank candidates on different populations. Formal candidates require all35.
    candidate_names=[p for p in observed if p!='P0' and ready(p) and full(p) and full('P0')]
    ranking=[]
    for p in candidate_names:
        gain=ratio('P0',p,ids)
        ranking.append(dict(profile=p,parameters=registry[p],DH_speedup_GM=gain,
                            logical_resources=resource_cost(registry[p])))
    ranking.sort(key=lambda x:(-x['DH_speedup_GM'],x['logical_resources']['normalized_slot_score'],x['profile']))
    effective=[x for x in ranking if x['DH_speedup_GM']>=MIN_GAIN]
    selected=[]
    distinct_vectors={_key(x['parameters']) for x in ranking}
    insufficient_distinct=len(distinct_vectors)<2
    if ranking:
        high=max(ranking,key=lambda x:(x['logical_resources']['normalized_slot_score'],x['DH_speedup_GM'],x['profile']))
        remaining=[x for x in ranking if _key(x['parameters'])!=_key(high['parameters'])]
        remaining_effective=[x for x in remaining if x['DH_speedup_GM']>=MIN_GAIN]
        classes=[('high_resource',high)]
        if remaining:
            moderate=min(remaining_effective or remaining,key=lambda x:(x['logical_resources']['normalized_slot_score'],-x['DH_speedup_GM'],x['profile']))
            classes.insert(0,('moderate',moderate))
        else:
            decisions.append(dict(action='INSUFFICIENT_DISTINCT_FULL_SUITE_CONFIGURATIONS',
                reason='Only one accepted non-P0 parameter vector; cannot fill moderate/high-resource classes distinctly'))
        for label,x in classes:
            value=dict(x,candidate_class=label,matched_CH_complete=full(x['profile'],'CH'),
                       improvement_proven=x['DH_speedup_GM']>=MIN_GAIN)
            selected.append(value)
            propose(x['parameters'],'CH','CH_MATCH','Full-suite DH candidate requires identical full-suite CH profile before formal adoption',dict(n=expected,expected_n=expected,DH_speedup_GM=x['DH_speedup_GM'],candidate_class=label))
    if not effective:
        decisions.append(dict(action='NO_PROVEN_IMPROVED_UNIFORM_PROFILE',reason='No full-suite accepted uniform profile reaches preregistered 1% GM threshold; retain baseline and all regressions'))
    unresolved={p:[d for d in ids if not good(d,p,'DH')] for p in observed if p=='P0' or ready(p)}
    unresolved={p:ds for p,ds in unresolved.items() if ds}
    pending=[p for p in observed if not ready(p)]
    pending_cells=[dict(profile=p,cell=c) for p in observed for c in ('CH','DH')
        if any((p,c,d) in registered for d in ids) and not ready(p,c)]
    unaccepted_cells=[dict(profile=p,cell=c,input_digest=d,state=cell(d,p,c).get('state'))
        for p,c,d in sorted(registered) if terminal(d,p,c) and not good(d,p,c)]
    search_complete=not plans and not pending_cells
    engineering_cells=[dict(profile=p,cell=c,input_digest=d,state=cell(d,p,c).get('state'))
        for p,c,d in sorted(registered) if 'ENGINEERING' in str(cell(d,p,c).get('state',''))]
    requires_engineering_review=bool(unaccepted_cells or engineering_cells)
    adoption_ready=search_complete and not insufficient_distinct and len(selected)==2 and full('P0') and full('P0','CH') and all(x['matched_CH_complete'] for x in selected)
    return dict(schema='DTC_L2_MLP_ADAPTIVE_DECISIONS_V1',
        state='QUIESCENT_REQUIRES_ENGINEERING_REVIEW' if search_complete and requires_engineering_review else 'QUIESCENT_INSUFFICIENT_DISTINCT_CANDIDATES' if search_complete and insufficient_distinct else 'SEARCH_QUIESCENT' if search_complete else 'SEARCH_ACTIVE',
        expected_input_count=expected,proposals=plans,decisions=decisions,
        family_champions=family_best,whole_suite_DH_ranking=ranking,formal_candidates=selected,
        rank_status='FINAL_ALL_REGISTERED_TERMINAL' if search_complete else 'PROVISIONAL_SEARCH_ONGOING',
        adoption_ready=adoption_ready,
        insufficient_distinct_candidates=insufficient_distinct,distinct_full_suite_nonP0_vectors=len(distinct_vectors),
        requires_engineering_review=requires_engineering_review,engineering_cells=engineering_cells,
        scientific_stage_complete=adoption_ready and not requires_engineering_review,
        pending_profiles=pending,pending_cells=pending_cells,terminal_unaccepted=unresolved,
        all_terminal_unaccepted_cells=unaccepted_cells,
        blocked_reason='Some profiles lack full35 acceptance; their summaries remain provisional. Other fully matched profiles remain independently valid; preserve all failures' if unaccepted_cells else None,
        all_negative_inputs_retained=True,contract=CONTRACT)

if __name__=='__main__':
    import argparse,pathlib
    ap=argparse.ArgumentParser();ap.add_argument('summary');ap.add_argument('scope');ap.add_argument('--history');ap.add_argument('--output')
    args=ap.parse_args();read=lambda p:json.loads(pathlib.Path(p).read_text())
    result=recommend(read(args.summary),read(args.scope),read(args.history) if args.history else {})
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:pathlib.Path(args.output).write_text(text,encoding='utf-8')
    else:print(text,end='')
