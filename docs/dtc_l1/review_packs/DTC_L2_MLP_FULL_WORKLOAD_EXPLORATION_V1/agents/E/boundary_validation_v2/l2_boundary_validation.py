"""Supplementary search policy V2 candidate; no production application on import.

augment(existing_decision, summary, scope, history) preserves the original policy
output and its registry-journal final guard. It only proposes extra authorized
uniform matrices. Main must archive/announce V2 before considering activation.
"""
import copy,hashlib,json,math

BASE={'entries':192,'merge':4,'miss_queue':32,'frfcfs':64}
FACTORS=tuple(BASE)
PREFIX={'entries':'E','merge':'M','miss_queue':'Q','frfcfs':'F'}
INITIAL={'P0':dict(BASE),**{PREFIX[k]+str(BASE[k]*m):dict(BASE,**{k:BASE[k]*m})for k in FACTORS for m in (2,4)}}
EPS=1e-12
MATERIAL=1.01
NEGATIVE={'FAIL_L2MLP_ARCHIVED_NO_RETRY','L2_MLP_NATIVE_NEGATIVE_UNACCEPTED'}
POLICY={
 'schema':'DTC_L2_MLP_SUPPLEMENTARY_BOUNDARY_POLICY_V2',
 'candidate_revision':2,
 'unactivated_preimage_source_sha256':'7f2e3ddf571788719e65fdd319f910b2c001ef96a9f11b2dc733aa56e3ba3ea5',
 'status':'CANDIDATE_REQUIRES_MAIN_REVIEW_VERSIONED_ANNOUNCEMENT_NOT_PRODUCTION_APPLIED',
 'base_adaptive_source_sha256':'f21bc1233dfcaca2e003b9d5277fa31d27eb4b5f9d2cf21e6a694de9d2d0a1c3',
 'base_contract_retained':True,
 'initial_stage':'all350 initial point cells terminal; pending/engineering event never terminal',
 'supplementary_evidence':'full35 accepted DH, exact same frozen population; no subset extrapolation',
 'epsilon':EPS,
 'material_gain_label':MATERIAL,
 'boundary_rule':'highest registered accepted single-factor level / P0 >1+epsilon AND highest / immediately lower level >1+epsilon => factor times2',
 'boundary_missing_rule':'pending or unaccepted highest registered level holds family; never skip over it',
 'stopping':'nonpositive marginal/overall gain, source bound, explicit evidenced resource hold, or incomplete scientific evidence; no total-start cap',
 'suite_context':'immutable suite membership; n>=3, GM>=1.01, strictly more than half positive by epsilon',
 'global_context':'full35 GM>1+epsilon; 1% is materiality only, not eligibility gate',
 'combination_pairs':[['entries','merge'],['entries','miss_queue'],['entries','frfcfs'],['merge','miss_queue'],['merge','frfcfs']],
 'combination_rule':'one strongest useful completed family level per fixed context; supported pairs plus one union if >=3 directions; full35 uniform DH, no Cartesian grid',
 'CH_rule':'retain V1 full35 candidate matching; additionally match full35 globally positive best-observed uniform profile and each fixed-suite useful champion regardless of initial/noninitial identity; retain useful noninitial matching; never reduce the CH population',
 'uniform_best_rule':'rank only full35 accepted uniform DH profiles including P0; maximum whole35 GM, ties lower normalized logical slot score then deterministic profile name; expose all incomplete profiles',
 'potential_interpretation':'best observed uniform performance is distinct from highest-resource exploration; neither establishes a physical or unexplored performance upper bound',
 'identity_rule':'same canonical profile/parameter/design/frozen input population => same64hex proposal ID as base; never regrant evaluated/failed/pending identities',
 'final_guard':'never turn an existing false adoption/completion true; preserve and reapply registry journal guard outside augmentation',
 'fixed':['35 frozen inputs','7 unresolved excluded','DRAM850MHz','same Core/FW/binaries','L2 capacity/address map','DTC L1 architecture','Hash family','original P0 identity'],
 'no_historical_reinterpretation':True,
 'no_per_program_bestof':True,
 'no_total_start_cap':True,
}

def gm(values):return math.exp(sum(math.log(v)for v in values)/len(values))if values else None
def normalize(overrides):
    if not isinstance(overrides,dict)or set(overrides)-set(BASE):raise ValueError('Unsupported parameter family')
    p=dict(BASE,**overrides)
    for k,v in p.items():
        if type(v)is not int or not BASE[k]<=v<=2147483647:raise ValueError('Invalid source integer '+k)
    if p['entries']>1073741823:raise ValueError('MSHR constructor overflow guard')
    return p
def name(p):return '_'.join(PREFIX[k]+str(p[k])for k in FACTORS if p[k]!=BASE[k])or'P0'
def key(p):return tuple(p[k]for k in FACTORS)
def resources(p):
    return dict(l2_data_bytes=10485760,mshr_address_entries_total=40*p['entries'],
      mshr_request_references_upper_bound=40*p['entries']*p['merge'],miss_queue_request_slots_total=40*p['miss_queue'],
      frfcfs_request_slots_total=20*p['frfcfs'],shared_credit_limit_per_controller=p['frfcfs']+191,
      physical_area_or_bytes='UNKNOWN; logical capacity is not physical area or eager host RSS')
def resource_score(p):
    return p['entries']/192+p['entries']*p['merge']/(192*4)+p['miss_queue']/32+p['frfcfs']/64

def augment(existing_decision,summary,scope,history=None):
    history=history or {};out=copy.deepcopy(existing_decision)
    base_sha=hashlib.sha256(json.dumps(existing_decision,sort_keys=True).encode()).hexdigest()
    out['supplementary_policy']=dict(POLICY,base_decision_sha256=base_sha)
    out['supplementary_decisions']=notes=[]
    out['supplementary_new_proposals']=0
    out['best_global_uniform_profile']=None
    out['best_global_uniform_GM']=None
    out['fixed_suite_uniform_champions']=[]
    out['performance_potential_interpretation']=POLICY['potential_interpretation']
    table=summary['table'];programs=summary['programs'];ids=sorted({p['input_digest']for p in scope['points']})
    if scope.get('frozen_input_count',35)!=35 or len(ids)!=35 or set(ids)!=set(table)or set(ids)!=set(programs):
        raise ValueError('Supplement V2 requires the exact complete35 frozen input domain')
    frozen_meta={}
    for p in scope['points']:
        value=(p['program'],p.get('suite','UNKNOWN'))
        if frozen_meta.setdefault(p['input_digest'],value)!=value:raise ValueError('Scope program/suite inconsistency')
    if any((programs[d]['program'],programs[d]['suite'])!=frozen_meta[d]for d in ids):
        raise ValueError('Fixed program/suite identity changed')
    registry={n:dict(p)for n,p in INITIAL.items()}
    for n,value in history.get('profiles',{}).items():
        p=normalize(value.get('parameters',value))
        if n in registry and registry[n]!=p:raise ValueError('Profile identity collision '+n)
        registry[n]=p
    observed=set(summary['profiles'])
    if observed-set(registry):raise ValueError('Unknown profile metadata')
    registered={(p['profile'],p['cell'],p['input_digest'])for p in scope['points']}
    proposals=out.setdefault('proposals',[])
    known_ids=set(history.get('proposal_ids',[]))|{p['proposal_id']for p in proposals}
    known_ids|={p['proposal_id']for p in history.get('proposals',[])if'proposal_id'in p}
    contexts={'ALL':ids}
    suites=sorted({programs[d]['suite']for d in ids})
    for suite in suites:
        population=[d for d in ids if programs[d]['suite']==suite]
        if len(population)>=3:contexts['SUITE:'+suite]=population
    def cell(d,p,c='DH'):return table[d].get(p,{}).get(c,{})
    def good(d,p,c='DH'):
        value=cell(d,p,c)
        return value.get('accepted')is True and type(value.get('cycles'))is int and value['cycles']>0
    def terminal(d,p,c='DH'):return good(d,p,c)or cell(d,p,c).get('state')in NEGATIVE
    def full(p,c='DH'):return all(good(d,p,c)for d in ids)
    def ratios(p,population):return [cell(d,'P0')['cycles']/cell(d,p)['cycles']for d in population]
    def useful(p,context):
        vals=ratios(p,contexts[context]);value=gm(vals)
        if context=='ALL':return value>1+EPS
        return value>=MATERIAL and sum(v>1+EPS for v in vals)>len(vals)/2
    def ev(p,context):
        vals=ratios(p,contexts[context])
        return dict(context=context,context_population=contexts[context],context_n=len(vals),context_GM=gm(vals),
                    context_positive=sum(v>1+EPS for v in vals),full35_GM=gm(ratios(p,ids)),
                    full35_population=ids,full35_n=35,material_global=gm(ratios(p,ids))>=MATERIAL)
    def add(parameters,cellname,phase,reason,evidence):
        p=normalize(parameters);aliases=[n for n,v in registry.items()if v==p]
        profile=sorted(aliases,key=lambda n:(n!='P0',n))[0]if aliases else name(p)
        present=[d for d in ids if any((n,cellname,d)in registered for n in aliases+[profile])]
        if present:
            notes.append(dict(action='ALREADY_EVALUATED_OR_PENDING'if len(present)==35 else'PARTIAL_REGISTERED_MATRIX_REQUIRES_RECONCILIATION',profile=profile,cell=cellname,registered_n=len(present)))
            if len(present)!=35:out.update(supplementary_waiting_registry=True,requires_engineering_review=True)
            return
        pid=hashlib.sha256(json.dumps(dict(parameters=p,cell=cellname,inputs=ids),sort_keys=True).encode()).hexdigest()
        if pid in known_ids:
            # Retain the base proposal bytes and attach a separate cross-reference.
            notes.append(dict(action='EXACT_PROPOSAL_ALREADY_KNOWN',profile=profile,cell=cellname,proposal_id=pid,evidence=evidence))
            if not any(p['proposal_id']==pid for p in proposals):out['supplementary_waiting_registry']=True
            return
        constraint=history.get('resource_constraints',{})
        if pid in constraint.get('blocked_proposal_ids',[]):
            notes.append(dict(action='RESOURCE_HOLD',profile=profile,cell=cellname,reason=constraint.get('reason','Explicit evidenced constraint')));return
        for k,bound in constraint.get('max_parameters',{}).items():
            if k not in BASE or type(bound)is not int:raise ValueError('Invalid evidenced resource bound')
            if p[k]>bound:
                notes.append(dict(action='RESOURCE_HOLD',profile=profile,cell=cellname,bound={k:bound},reason=constraint.get('reason','Explicit evidenced bound')));return
        proposals.append(dict(proposal_id=pid,profile=profile,parameters=p,cells=[cellname],phase=phase,
            workloads=[dict(input_digest=d,program=programs[d]['program'],suite=programs[d]['suite'])for d in ids],
            expected_input_count=35,new_cells=[dict(input_digest=d,cell=cellname)for d in ids],new_cell_count=35,
            reason=reason,evidence=evidence,logical_resources=resources(p),requires_coordinator_registration=True,
            supplementary_policy=POLICY['schema']))
        known_ids.add(pid);out['supplementary_new_proposals']+=1

    # Initial stage must truly be terminal: not just fast-input accepted subsets.
    waiting=[]
    for profile in INITIAL:
        for design in (('CH','DH')if profile=='P0'else('DH',)):
            if not all((profile,design,d)in registered and terminal(d,profile,design)for d in ids):waiting.append(dict(profile=profile,cell=design))
    if waiting:
        notes.append(dict(action='WAIT_INITIAL_ALL35_TERMINAL',pending=waiting))
        out.update(scientific_stage_complete=False,adoption_ready=False)
        return out
    if not full('P0'):
        notes.append(dict(action='FULL35_BASELINE_EVIDENCE_HOLD',missing=[d for d in ids if not good(d,'P0')]))
        out.update(scientific_stage_complete=False,adoption_ready=False)
        return out
    family_levels={}
    for factor in FACTORS:
        levels=sorted([(p[factor],n)for n,p in registry.items()if n in observed and p[factor]>BASE[factor]
                       and all(p[k]==BASE[k]for k in FACTORS if k!=factor)],key=lambda v:(v[0],v[1]))
        complete=[(value,n)for value,n in levels if full(n)]
        family_levels[factor]=complete
        if len(levels)<2:
            notes.append(dict(action='WAIT_TWO_REGISTERED_FAMILY_LEVELS',factor=factor));continue
        top_value,top=levels[-1];lower=levels[-2][1]
        if not full(top)or not full(lower):
            notes.append(dict(action='BOUNDARY_FULL35_EVIDENCE_HOLD',factor=factor,top=top,lower=lower,
                              top_missing=[d for d in ids if not good(d,top)],lower_missing=[d for d in ids if not good(d,lower)]));continue
        total=gm(ratios(top,ids));marginal=gm([cell(d,lower)['cycles']/cell(d,top)['cycles']for d in ids])
        evidence=dict(factor=factor,top=top,lower=lower,full35_population=ids,full35_n=35,
                      total_GM=total,marginal_GM=marginal,material_total=total>=MATERIAL,material_marginal=marginal>=MATERIAL)
        if total>1+EPS and marginal>1+EPS:
            try:parameters=normalize({factor:top_value*2})
            except ValueError as exc:
                notes.append(dict(action='STOP_SOURCE_BOUND',factor=factor,reason=str(exc),evidence=evidence));continue
            add(parameters,'DH','V2_BOUNDARY_VALIDATION','Complete35 deterministic total and marginal gains remain positive; 1% is materiality only',evidence)
        else:notes.append(dict(action='STOP_NONPOSITIVE_OR_SATURATED',factor=factor,evidence=evidence))

    # Contexts choose one level per family, then whole-suite experiments test it.
    for context,population in contexts.items():
        champions={}
        for factor,levels in family_levels.items():
            candidates=[(value,n)for value,n in levels if useful(n,context)]
            if candidates:champions[factor]=max(candidates,key=lambda item:(gm(ratios(item[1],population)),-item[0]))[1]
        def combine(factors,phase):
            parents=[champions[k]for k in factors];parameters=dict(BASE)
            for k in factors:parameters[k]=registry[champions[k]][k]
            add(parameters,'DH',phase,'Evidence-supported fixed-context directions; verify one uniform profile on all35',
                dict(context=context,parents=parents,parent_evidence=[ev(p,context)for p in parents],
                     selection_unit='whole profile per fixed context, never per-input best-of'))
        for a,b in POLICY['combination_pairs']:
            if a in champions and b in champions:combine([a,b],'V2_FIXED_CONTEXT_PAIR_VALIDATION')
        if len(champions)>=3:combine([k for k in FACTORS if k in champions],'V2_FIXED_CONTEXT_UNION_VALIDATION')

    # Search-family champions are not the final uniform-config winner. Match the
    # best whole35 completed uniform profile even if it is initial and sub1%.
    completed=sorted(p for p in observed if full(p))
    out['incomplete_uniform_profiles']=[dict(profile=p,missing=[d for d in ids if not good(d,p)])
                                       for p in sorted(observed)if not full(p)]
    def uniform_record(profile,context):
        evidence=ev(profile,context)
        ch_registered=[d for d in ids if(profile,'CH',d)in registered]
        ch_accepted=[d for d in ids if good(d,profile,'CH')]
        return dict(profile=profile,parameters=registry[profile],context=context,
            context_GM=evidence['context_GM'],whole35_GM=evidence['full35_GM'],population=ids,n=35,expected_n=35,
            logical_resource_score=resource_score(registry[profile]),logical_resources=resources(registry[profile]),
            deterministic_positive_global=evidence['full35_GM']>1+EPS,material_global=evidence['full35_GM']>=MATERIAL,
            CH_registered_n=len(ch_registered),CH_accepted_n=len(ch_accepted),CH_missing_n=35-len(ch_accepted),
            CH_match_complete=len(ch_accepted)==35,
            rank_status='BEST_OBSERVED_COMPLETED_UNIFORM_NOT_UNEXPLORED_UPPER_BOUND',
            incomplete_profile_count=len(out['incomplete_uniform_profiles']))
    global_best=min(completed,key=lambda p:(-gm(ratios(p,ids)),resource_score(registry[p]),p))
    best=uniform_record(global_best,'ALL')
    out['best_global_uniform_profile']=best;out['best_global_uniform_GM']=best['whole35_GM']
    if best['deterministic_positive_global']:
        add(registry[global_best],'CH','V2_BEST_GLOBAL_UNIFORM_CH_MATCH',
            'Best observed complete35 globally positive uniform profile requires CH35, including initial profiles with <1% gain',
            dict(uniform_candidate=best,full35_population=ids,full35_n=35))
    for context,population in contexts.items():
        if context=='ALL':continue
        eligible=[p for p in completed if useful(p,context)]
        if not eligible:continue
        winner=min(eligible,key=lambda p:(-gm(ratios(p,population)),resource_score(registry[p]),p))
        champion=uniform_record(winner,context)
        out['fixed_suite_uniform_champions'].append(champion)
        add(registry[winner],'CH','V2_FIXED_SUITE_UNIFORM_CH_MATCH',
            'Best useful completed uniform profile in a fixed suite requires CH35, including all other suite regressions',
            dict(uniform_candidate=champion,fixed_suite_evidence=ev(winner,context),full35_population=ids,full35_n=35))
    out['global_best_CH_qualified']=best['CH_match_complete']
    out['supplementary_uniform_CH_qualification_complete']=all(
        candidate['CH_match_complete']for candidate in [best]+out['fixed_suite_uniform_champions'])

    # Additional noninitial profiles demonstrated useful globally or by a fixed
    # suite get exact all35 CH matching; no claim from smaller matched subsets.
    for profile in sorted(observed-set(INITIAL)):
        if not full(profile):continue
        evidence=[ev(profile,c)for c in contexts if useful(profile,c)]
        if evidence:add(registry[profile],'CH','V2_UNIFORM_CH_MATCH','Completed useful noninitial uniform profile requires full35 CH matching',dict(contexts=evidence,full35_population=ids,full35_n=35))
    out['supplementary_candidate_materiality']=[dict(profile=x['profile'],whole_suite_GM=x['DH_speedup_GM'],
        deterministic_positive_improvement=x['DH_speedup_GM']>1+EPS,material_improvement=x['DH_speedup_GM']>=MATERIAL,
        original_V1_improvement_proven=x.get('improvement_proven'))for x in out.get('formal_candidates',[])]
    if out['supplementary_new_proposals']:
        out['scientific_stage_complete']=False;out['adoption_ready']=False
        if not out.get('registry_journal_status',{}).get('requires_engineering_review',False):out['state']='SUPPLEMENTARY_V2_SEARCH_ACTIVE'
    if out.get('supplementary_waiting_registry'):
        out.update(scientific_stage_complete=False,adoption_ready=False,
                   state='SUPPLEMENTARY_V2_WAIT_KNOWN_PROPOSAL_REGISTRY_RECONCILIATION')
    if not out['supplementary_uniform_CH_qualification_complete']:
        out.update(scientific_stage_complete=False,adoption_ready=False)
    # Never remove an existing journal hold or promote an old false final flag.
    if not existing_decision.get('scientific_stage_complete',False):out['scientific_stage_complete']=False
    if not existing_decision.get('adoption_ready',False):out['adoption_ready']=False
    journal=out.get('registry_journal_status',{})
    if journal.get('requires_engineering_review')or journal.get('safe_for_scientific_completion')is False:
        out.update(scientific_stage_complete=False,adoption_ready=False,requires_engineering_review=True,
                   state='REGISTRY_JOURNAL_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS')
    return out
