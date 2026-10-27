"""New CPU cross-module policy qualification using the actual35-input D schema."""
import copy,datetime,hashlib,importlib.util,json,pathlib
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/boundary_validation_v2')

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p.write_bytes((json.dumps(v,indent=2,sort_keys=True)+'\n').encode())
def load(n,path):
    s=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    module=load('boundary_v2',A/'l2_boundary_validation.py')
    base=load('frozen_adaptive_v1',R/'tools/l2_adaptive.py')
    consumer=load('frozen_consumer_v1',R/'tools/l2_results.py')
    gen=load('frozen_generator_v1',R/'tools/l2_config_generator.py')
    scope=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json')
    assert len(scope['points'])==350,'Qualification contract expects initial full350 matrix'
    paths=['l2_adaptive.py','l2_results.py','l2_config_generator.py','l2_registry.py','l2_native.py']
    pins={n:sha(R/'tools'/n)for n in paths}
    checks=[];examples=[]
    def ck(name,condition):assert condition,name;checks.append(name)
    def fixture(gain=None):
        gain=gain or(lambda p:1.0);records={}
        for p in scope['points']:
            value=round(10**12/gain(p));records[p['cohort']]=dict(state=consumer.PASS,cycles=value,
                uuid='SYNTHETIC_CPU_ONLY',proof=dict(performance_accepted=True,cycles=value),archive={'SYNTHETIC_CPU_ONLY':True})
        return records
    def evaluate(records,matrix=None,hist=None,journal=None):
        matrix=matrix or scope;hist=hist or history
        summary=consumer.summarize(matrix,records);original=base.recommend(summary,matrix,hist)
        if journal:
            original.update(registry_journal_status=journal,scientific_stage_complete=False,adoption_ready=False,
                state='REGISTRY_JOURNAL_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS',requires_engineering_review=True)
        before=copy.deepcopy(original);out=module.augment(original,summary,matrix,hist)
        ck('pure augment keeps original decision input unchanged '+str(len(checks)),original==before)
        return original,out,summary
    weak={'E384':1.002,'E768':1.004}
    records=fixture(lambda p:weak.get(p['profile'],1));old,new,summary=evaluate(records)
    ck('V1 calls sub1percent E boundary saturation',any(x.get('factor')=='entries'and x['action']=='STOP_FAMILY_SATURATION_OR_REGRESSION'for x in old['decisions']))
    added=[p for p in new['proposals']if p.get('supplementary_policy')]
    ck('V2 continues sub1percent positive E boundary',any(p['profile']=='E1536'and p['phase']=='V2_BOUNDARY_VALIDATION'for p in added))
    ck('material label remains false while extension eligible',next(p for p in added if p['profile']=='E1536')['evidence']['material_total']is False)
    ck('all added matrices exact35 cells identities',all(p['new_cell_count']==35 and len(p['new_cells'])==35 and len(p['workloads'])==35 and len({x['input_digest']for x in p['new_cells']})==35 for p in added))
    ck('new proposal IDs satisfy journal safe basename grammar',all(len(p['proposal_id'])==64 and p['proposal_id'].isalnum()for p in added))
    ck('no active supplement declares scientific completion',not new['scientific_stage_complete']and not new['adoption_ready'])
    ck('original V1 proposals remain byte-equivalent',new['proposals'][:len(old['proposals'])]==old['proposals'])
    boundary=next(p for p in added if p['profile']=='E1536')
    examples.append(dict(case='sub1percent_boundary',base=old['decisions'],new_proposal=boundary))
    counter={'E384':1.009,'E768':1.008}
    counter_records=fixture(lambda p:counter.get(p['profile'],1))
    original,counter_result,_=evaluate(counter_records)
    ck('V1 actual counterexample omits sub1percent winning initial E384 formal class',all(x['profile']!='E384'for x in original['formal_candidates']))
    ck('revision2 reports actual full35 uniform winner E384',counter_result['best_global_uniform_profile']['profile']=='E384'and abs(counter_result['best_global_uniform_GM']-1.009)<1e-10)
    ck('sub1percent winning initial E384 receives exact35 CH request',any(p['profile']=='E384'and p['cells']==['CH']and len(p['new_cells'])==35 and p['phase']=='V2_BEST_GLOBAL_UNIFORM_CH_MATCH'for p in counter_result['proposals']))
    ck('V1 formal fields are preserved, not silently replaced by best winner',counter_result['formal_candidates']==original['formal_candidates'])
    ck('highest resource point is explicitly distinct from best observed performance',next(x['profile']for x in original['formal_candidates']if x['candidate_class']=='high_resource')=='E768'and counter_result['best_global_uniform_profile']['profile']=='E384'and 'upper bound'in counter_result['performance_potential_interpretation'])
    ck('winning profile cannot be adopted before full35 CH qualification',not counter_result['global_best_CH_qualified']and not counter_result['supplementary_uniform_CH_qualification_complete']and not counter_result['adoption_ready'])
    examples.append(dict(case='initial_sub1percent_winner',V1_formal_candidates=original['formal_candidates'],best_uniform=counter_result['best_global_uniform_profile'],CH_request=[p for p in counter_result['proposals']if p['profile']=='E384'and p['cells']==['CH']]))
    tied={'E384':1.009,'E768':1.008,'M8':1.009,'M16':1.008}
    _,result,_=evaluate(fixture(lambda p:tied.get(p['profile'],1)))
    ck('uniform winner GM tie breaks toward lower logical resource score',result['best_global_uniform_profile']['profile']=='M8')
    reduced=copy.deepcopy(counter_records);failure=next(p for p in scope['points']if p['profile']=='E384')
    reduced[failure['cohort']]=dict(state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=None)
    _,result,_=evaluate(reduced)
    ck('34accepted cannot win full35 uniform ranking',result['best_global_uniform_profile']['profile']=='E768'and any(x['profile']=='E384'and len(x['missing'])==1 for x in result['incomplete_uniform_profiles']))
    ck('incomplete better-looking profile receives no subset-based CH promotion',not any(p.get('supplementary_policy')and p['profile']=='E384'and p['cells']==['CH']for p in result['proposals']))
    partial_scope=copy.deepcopy(scope);partial_records=copy.deepcopy(counter_records)
    for p in scope['points']:
        if p['profile']=='P0'and p['cell']=='CH'and p['input_digest']!=sorted({q['input_digest']for q in scope['points']})[-1]:
            np=dict(p,profile='E384',cohort=p['cohort'].replace('-P0-','-E384-'));partial_scope['points'].append(np)
            partial_records[np['cohort']]=copy.deepcopy(counter_records[p['cohort']])
    _,result,_=evaluate(partial_records,matrix=partial_scope)
    ck('34of35 CH coverage explicitly remains unqualified',result['best_global_uniform_profile']['CH_accepted_n']==34 and result['best_global_uniform_profile']['CH_missing_n']==1 and not result['global_best_CH_qualified'])
    ck('partial CH winner requests reconciliation not a duplicate full35 batch',result.get('supplementary_waiting_registry')and not result['adoption_ready']and not any(p.get('supplementary_policy')and p['profile']=='E384'and p['cells']==['CH']for p in result['proposals']))
    full_bad_scope=copy.deepcopy(scope);full_bad_records=copy.deepcopy(counter_records)
    for profile in ('E384','E768','F128'):
        for p in scope['points']:
            if p['profile']=='P0'and p['cell']=='CH':
                np=dict(p,profile=profile,cohort=p['cohort'].replace('-P0-','-'+profile+'-'));full_bad_scope['points'].append(np)
                full_bad_records[np['cohort']]=copy.deepcopy(counter_records[p['cohort']])
    onebad=next(p for p in full_bad_scope['points']if p['profile']=='E384'and p['cell']=='CH')
    full_bad_records[onebad['cohort']]=dict(state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=None)
    previous,result,_=evaluate(full_bad_records,matrix=full_bad_scope)
    ck('best uniform unaccepted CH cannot inherit V1 other-class adoption readiness',previous['adoption_ready']and not result['adoption_ready']and not result['global_best_CH_qualified'])

    # Every new target uses the actual frozen generator and canonical P0 configs.
    for design in ('CH','DH'):
        point=next(p for p in scope['points']if p['profile']=='P0'and p['cell']==design)
        spec=read(R/'control/specs'/(point['cohort']+'.json'))
        texts=[P(c['path']).read_text()for c in spec['configs']]
        before=gen.effective_options(texts)
        for parameters in ({'entries':1536},{'merge':32},{'miss_queue':256},{'frfcfs':512},
                           {'entries':1536,'merge':32,'miss_queue':256,'frfcfs':512}):
            after,manifest=gen.generate(texts,parameters);options=gen.effective_options(after)
            ck('actual generator keeps fixed options '+design+module.name(gen.normalize(parameters)),
               {k for k in options if options[k]!=before[k]}<={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'}
               and options['-gpgpu_clock_domains']=='1410.0:1410.0:1410.0:850.0'and manifest['logical_resource_cost']['l2_data_bytes']==10485760)
    ck('pure parameter normalize matches source generator',all(module.normalize(p)==gen.normalize(p)for p in [{'entries':1536},{'merge':32},{'miss_queue':256},{'frfcfs':512}]))

    for gains,label in [({'E384':1.004,'E768':1.004},'exact saturation'),({'E384':1.004,'E768':1.002},'marginal regression'),({'E384':.997,'E768':.999},'overall regression')]:
        old,result,_=evaluate(fixture(lambda p:gains.get(p['profile'],1)))
        ck(label+' does not extend E boundary',not any(p['profile']=='E1536'and p.get('supplementary_policy')for p in result['proposals']))
    gains={'E384':1+2e-13,'E768':1+4e-13}
    _,result,_=evaluate(fixture(lambda p:gains.get(p['profile'],1)))
    ck('numeric epsilon excludes insignificant float rounding',not any(p['profile']=='E1536'and p.get('supplementary_policy')for p in result['proposals']))
    partial=copy.deepcopy(records)
    for p in scope['points']:
        if p['input_digest']not in sorted(summary['programs'])[:9]:partial.pop(p['cohort'],None)
    _,result,_=evaluate(partial)
    ck('nine completed fast inputs cannot trigger new policy direction',result['supplementary_new_proposals']==0 and any(x['action']=='WAIT_INITIAL_ALL35_TERMINAL'for x in result['supplementary_decisions']))
    failed=copy.deepcopy(records);first=next(p for p in scope['points']if p['profile']=='E768')
    failed[first['cohort']]=dict(state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=None,proof={'performance_accepted':False})
    _,result,failed_summary=evaluate(failed)
    ck('terminal unaccepted 34of35 cannot extend E boundary',not any(p['profile']=='E1536'and p.get('supplementary_policy')for p in result['proposals']))
    ck('unaccepted original remains explicit missing not zero',failed_summary['aggregates']['E768']['ALL']['DH_speedup']['missing_n']==1 and result['requires_engineering_review'])
    failed=copy.deepcopy(records);point=next(p for p in scope['points']if p['profile']=='P0'and p['cell']=='DH')
    failed[point['cohort']]=dict(state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=None)
    _,result,_=evaluate(failed)
    ck('missing baseline accepted population blocks every supplement',result['supplementary_new_proposals']==0 and any(x['action']=='FULL35_BASELINE_EVIDENCE_HOLD'for x in result['supplementary_decisions']))

    blocked=copy.deepcopy(history);blocked['resource_constraints']={'max_parameters':{'entries':768},'reason':'SYNTHETIC_MEASURED_MEMORY_RISK'}
    _,result,_=evaluate(records,hist=blocked)
    ck('evidenced resource bound blocks additional factor growth',not any(p['profile']=='E1536'for p in result['proposals']) and any(x['action']=='RESOURCE_HOLD'for x in result['supplementary_decisions']))
    known=copy.deepcopy(history);known['proposal_ids'].append(boundary['proposal_id'])
    _,result,_=evaluate(records,hist=known)
    ck('known historical proposal is not reissued',not any(p.get('supplementary_policy')and p['profile']=='E1536'for p in result['proposals']))
    ck('known proposal absent from matrix waits for registry, cannot complete',result.get('supplementary_waiting_registry')and not result['scientific_stage_complete'])

    # A real future profile identity in the actual matrix/schema is never repeated.
    expanded=copy.deepcopy(scope);hist=copy.deepcopy(history);hist['profiles']['E1536']={'parameters':gen.normalize({'entries':1536})}
    future_records=copy.deepcopy(records)
    for p in scope['points']:
        if p['profile']=='P0'and p['cell']=='DH':
            newpoint=dict(p,profile='E1536',cohort=p['cohort'].replace('-P0-','-E1536-'));expanded['points'].append(newpoint)
            cycles=round(10**12/1.004);future_records[newpoint['cohort']]=dict(state=consumer.PASS,cycles=cycles,proof=dict(performance_accepted=True,cycles=cycles),archive={'SYNTHETIC_CPU_ONLY':True})
    _,result,_=evaluate(future_records,matrix=expanded,hist=hist)
    ck('already evaluated E1536 never regranted or extended when saturated',not any(p.get('supplementary_policy')and p['profile']in('E1536','E3072')and p['cells']==['DH']for p in result['proposals']))
    ck('useful completed future uniform profile gets full35 CH matching without duplicating V1 request',any(p['profile']=='E1536'and p['cells']==['CH']and len(p['new_cells'])==35 for p in result['proposals']))
    pending_future=copy.deepcopy(future_records);future_point=next(p for p in expanded['points']if p['profile']=='E1536');pending_future.pop(future_point['cohort'])
    _,result,_=evaluate(pending_future,matrix=expanded,hist=hist)
    ck('pending higher registered level cannot be skipped for boundary expansion',not any(p.get('supplementary_policy')and p['profile']=='E3072'and p['cells']==['DH']for p in result['proposals'])and any(x['action']=='BOUNDARY_FULL35_EVIDENCE_HOLD'and x['top']=='E1536'for x in result['supplementary_decisions']))
    twice=copy.deepcopy(expanded);twice_records=copy.deepcopy(future_records);twice_hist=copy.deepcopy(hist)
    twice_hist['profiles']['E3072']={'parameters':gen.normalize({'entries':3072})}
    for p in scope['points']:
        if p['profile']=='P0'and p['cell']=='DH':
            np=dict(p,profile='E3072',cohort=p['cohort'].replace('-P0-','-E3072-'));twice['points'].append(np)
            cyc=round(10**12/1.004);twice_records[np['cohort']]=dict(state=consumer.PASS,cycles=cyc,proof=dict(performance_accepted=True,cycles=cyc),archive={'SYNTHETIC_CPU_ONLY':True})
    previous,result,_=evaluate(twice_records,matrix=twice,hist=twice_hist)
    ck('noninitial useful profile outside current resource classes gets supplemental CH',
       not any(p['profile']=='E1536'and p['cells']==['CH']for p in previous['proposals'])and any(p['profile']=='E1536'and p['cells']==['CH']and p.get('supplementary_policy')and len(p['new_cells'])==35 for p in result['proposals']))

    # Fixed-suite signal diluted globally. All35 still run every proposed config.
    suites={}
    for p in scope['points']:
        if p['profile']=='P0'and p['cell']=='DH':suites.setdefault(p['suite'],[]).append(p['input_digest'])
    suite=min((s for s in suites if len(suites[s])>=3),key=lambda s:len(suites[s]))
    target=set(suites[suite])
    def suite_gain(p):
        if p['profile']not in('E384','E768','M8','M16'):return 1
        return 1.02 if p['input_digest']in target else .99
    suite_records=fixture(suite_gain);_,result,suite_summary=evaluate(suite_records)
    global_value=suite_summary['aggregates']['E384']['ALL']['DH_speedup']['GM']
    suite_proposals=[p for p in result['proposals']if p.get('supplementary_policy')and p['phase'].startswith('V2_FIXED_CONTEXT')]
    ck('suite fixture has diluted all35 GM below material threshold',global_value<1.01)
    ck('fixed suite can support a whole35 uniform combination',any(p['profile']=='E384_M8'and p['evidence']['context']=='SUITE:'+suite for p in suite_proposals))
    ck('suite-triggered combinations retain all35 including regressions',all(len(p['new_cells'])==35 and len(p['workloads'])==35 for p in suite_proposals))
    ck('no per-input profile optimizer is emitted',all(p['evidence'].get('selection_unit')=='whole profile per fixed context, never per-input best-of'for p in suite_proposals))
    examples.append(dict(case='suite_dilution',suite=suite,suite_n=len(target),global_GM=global_value,proposals=suite_proposals))
    def single_suite_gain(p):
        if p['profile']not in('E384','E768'):return 1
        return (1.02 if p['profile']=='E384'else 1.019)if p['input_digest']in target else .99
    _,result,_=evaluate(fixture(single_suite_gain))
    ck('initial single-family fixed-suite champion receives all35 CH despite globally nonpositive result',any(p['profile']=='E384'and p['cells']==['CH']and p.get('phase')=='V2_FIXED_SUITE_UNIFORM_CH_MATCH'and len(p['new_cells'])==35 for p in result['proposals']))
    lone=sorted(target)[0]
    def no_majority_gain(p):
        if p['profile']not in('E384','E768','M8','M16'):return 1
        return 100 if p['input_digest']==lone else .9 if p['input_digest']in target else .99
    _,result,_=evaluate(fixture(no_majority_gain))
    ck('one huge suite winner without majority cannot trigger suite eligibility',not any(p.get('supplementary_policy')and p['evidence'].get('context')=='SUITE:'+suite for p in result['proposals']))
    overlap={'E384':1.02,'E768':1.04,'M8':1.03,'M16':1.05}
    original,result,_=evaluate(fixture(lambda p:overlap.get(p['profile'],1)))
    ck('V1 plus ALL and four suite contexts deduplicate identical combination',sum(p['profile']=='E768_M16'and p['cells']==['DH']for p in result['proposals'])==1)
    ck('same canonical combination ID matches V1 exactly',next(p['proposal_id']for p in original['proposals']if p['profile']=='E768_M16')==next(p['proposal_id']for p in result['proposals']if p['profile']=='E768_M16'))
    _,deduped,_=evaluate(suite_records,hist=dict(history,proposal_ids=[p['proposal_id']for p in suite_proposals]))
    ck('same fixed suite combination proposals are not duplicated after history registration',not any(p.get('supplementary_policy')and p['phase'].startswith('V2_FIXED_CONTEXT')for p in deduped['proposals']))
    journal=dict(safe_for_scientific_completion=False,requires_engineering_review=True,pending=[{'proposal_id':'PENDING_JOURNAL'}])
    _,result,_=evaluate(records,journal=journal)
    ck('outer registry journal hold survives augmentation',result['registry_journal_status']==journal and result['state']=='REGISTRY_JOURNAL_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS'and not result['adoption_ready']and not result['scientific_stage_complete'])
    for overflow in [{'entries':1073741824},{'frfcfs':2147483648},{'merge':2147483648},{'miss_queue':2147483648}]:
        rejected=[]
        for normalize in (module.normalize,gen.normalize):
            try:normalize(overflow)
            except ValueError:rejected.append(True)
        ck('supplement and actual source generator agree on safety bound '+str(overflow),len(rejected)==2)
    ck('original frozen sources remain unmodified',all(sha(R/'tools'/n)==v for n,v in pins.items()))
    result=dict(schema='DTC_L2_MLP_SUPPLEMENTARY_BOUNDARY_V2_CPU_QUALIFICATION',status='PASS',checks=len(checks),names=checks,
        source_pins=pins,module_sha256=sha(A/'l2_boundary_validation.py'),actual_matrix_sha256=sha(R/'control/MATRIX_CURRENT.json'),
        suite_membership={s:sorted(v)for s,v in suites.items()},model_launches=0,production_authority_updates=0,
        production_source_mutations=0,production_applied=False,synthetic_results_never_performance_evidence=True)
    put(A/'QUALIFICATION.json',result);put(A/'SYNTHETIC_POLICY_EXAMPLES.json',examples)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
