"""CPU-only fixtures; no subprocesses, SSH, registration or model imports."""
import copy,json,pathlib
import l2_adaptive as a

checks=[]
def check(name,test):
    assert test,name
    checks.append(name)

def fixture(gains=None):
    gains=gains or {}
    scope={'frozen_input_count':3,'points':[]}
    table={d:{} for d in ['sha_A','sha_B','sha_C']}
    programs={d:dict(input_digest=d,program=d,suite='FIXTURE') for d in table}
    for p in a.INITIAL:
        for c in (['CH','DH'] if p=='P0' else ['DH']):
            for d in table:
                scope['points'].append(dict(cohort=d+p+c,input_digest=d,program=d,suite='FIXTURE',profile=p,cell=c))
                table[d].setdefault(p,{})[c]=dict(accepted=True,cycles=round(1000000/gains.get(p,1)),state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE')
    return {'profiles':list(a.INITIAL),'table':table,'programs':programs},scope

def run():
    summary,scope=fixture();r=a.recommend(summary,scope)
    check('flat => all four family saturation stops',sum(x['action']=='STOP_FAMILY_SATURATION_OR_REGRESSION' for x in r['decisions'])==4)
    check('flat => no DH false improvement proposals',not any(x['cells']==['DH'] for x in r['proposals']))
    check('flat => report unimproved resource classes',len(r['formal_candidates'])==2 and not any(x['improvement_proven'] for x in r['formal_candidates']))
    check('flat => two candidate parameter vectors are distinct',len({a._key(x['parameters']) for x in r['formal_candidates']})==2)
    check('high resource class uses maximum full-suite logical resource score',next(x for x in r['formal_candidates'] if x['candidate_class']=='high_resource')['logical_resources']['normalized_slot_score']==max(x['logical_resources']['normalized_slot_score'] for x in r['whole_suite_DH_ranking']))
    check('flat => candidate CH match all inputs',all(len(x['workloads'])==3 and x['new_cell_count']==3 for x in r['proposals']))
    s=copy.deepcopy(summary);s['table']['sha_A']['E384']['DH']=dict(accepted=False,state='PENDING')
    r=a.recommend(s,scope);check('pending blocks ranking and proposals',r['state']=='WAIT_INITIAL_TERMINAL' and not r['proposals'])
    s['table']['sha_A']['E384']['DH']['state']='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
    check('postprocess engineering is not terminal negative',a.recommend(s,scope)['state']=='WAIT_INITIAL_TERMINAL')
    s,sc=fixture({'E384':1.02,'E768':1.05});r=a.recommend(s,sc)
    check('rising E boundary extends past initial limit',any(p['profile']=='E1536' for p in r['proposals']))
    check('all-profile proposals cover full suite',all(len(p['workloads'])==3 and p['expected_input_count']==3 for p in r['proposals']))
    history={'proposal_ids':[p['proposal_id'] for p in r['proposals']]}
    check('proposal history suppresses exact duplicates',not a.recommend(s,sc,history)['proposals'])
    bounded=a.recommend(s,sc,{'resource_constraints':{'max_parameters':{'entries':768},'reason':'Observed constructor allocation risk fixture'}})
    check('explicit measured resource bounds defer unsafe extensions',not any(p['profile']=='E1536' for p in bounded['proposals']) and any(x['action']=='RESOURCE_HOLD' for x in bounded['decisions']))
    s,sc=fixture({'E384':1.03,'E768':1.031});r=a.recommend(s,sc)
    check('marginal saturation stops extension',not any(p['profile']=='E1536' for p in r['proposals']))
    s,sc=fixture({'E384':1.03,'E768':.95});r=a.recommend(s,sc)
    check('boundary regression retained and not extended',not any(p['profile']=='E1536' for p in r['proposals']) and any(x['top_GM']<1 for x in r['decisions'] if x['action']=='STOP_FAMILY_SATURATION_OR_REGRESSION'))
    s,sc=fixture({'E384':.99,'E768':1.05});r=a.recommend(s,sc)
    check('newly useful boundary still extends despite lower-level loss',any(p['profile']=='E1536' for p in r['proposals']))
    s,sc=fixture({'E384':1.02,'E768':1.05,'M8':1.03,'M16':1.06});r=a.recommend(s,sc)
    check('E x merge evidence generates one best-level pair',sum(p['phase']=='PAIR_COMBINATION' for p in r['proposals'])==1 and any(p['profile']=='E768_M16' for p in r['proposals']))
    s['table']['sha_A']['M16']['DH']=dict(accepted=False,state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=None)
    r=a.recommend(s,sc)
    check('terminal negative remains explicitly recorded',r['terminal_unaccepted']['M16']==['sha_A'])
    check('negative-containing GM is provisional with exact shared population',any(p['evidence'].get('status')=='PROVISIONAL_COMMON_POPULATION' and p['evidence']['n']==2 for p in r['proposals'] if p['phase']=='PAIR_COMBINATION'))
    check('full-suite candidate never selected from missing profile',all(x['profile']!='M16' for x in r['formal_candidates']))
    s,sc=fixture();sc['points']=[p for p in sc['points'] if not(p['profile']=='Q128' and p['input_digest']=='sha_A')]
    r=a.recommend(s,sc)
    check('partial registration fills only unregistered cells, not consumed identity',len(r['proposals'])==1 and r['proposals'][0]['new_cell_count']==1)
    check('resource count models FRFCFS coupled credits',a.resource_cost(dict(a.BASE,frfcfs=128))['shared_credit_limit_per_controller']==319)
    check('resources never change L2 capacity',all(a.resource_cost(p)['l2_data_bytes']==10485760 for p in a.INITIAL.values()))
    try:a.profile_name({'clock':1700})
    except ValueError:check('non-family scientific changes rejected',True)
    else:check('non-family scientific changes rejected',False)
    try:a.profile_name({'entries':2147483647})
    except ValueError:check('source integer/constructor safety bound enforced',True)
    else:check('source integer/constructor safety bound enforced',False)
    s,sc=fixture();s['table']['wrong_sha']=s['table'].pop('sha_A')
    try:a.recommend(s,sc)
    except ValueError:check('summary cannot silently change frozen identity',True)
    else:check('summary cannot silently change frozen identity',False)
    s,sc=fixture({'E768':1.05});r=a.recommend(s,sc)
    check('one effective profile cannot occupy both uniform resource classes',len(r['formal_candidates'])==2 and len({a._key(x['parameters']) for x in r['formal_candidates']})==2)
    check('unimproved moderate class remains explicitly false',any(x['candidate_class']=='moderate' and not x['improvement_proven'] for x in r['formal_candidates']))
    s,sc=fixture()
    for d in s['table']:
        for profile in a.INITIAL:
            if profile not in ('P0','E768'):
                s['table'][d][profile]['DH']=dict(accepted=False,state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=None)
    r=a.recommend(s,sc)
    check('only one full-suite vector reports insufficient distinct classes',r['insufficient_distinct_candidates'] and r['distinct_full_suite_nonP0_vectors']==1 and not r['adoption_ready'])
    for d in s['table']:
        s['table'][d]['E768']['CH']=dict(accepted=True,cycles=1000000,state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE')
        sc['points'].append(dict(cohort=d+'E768CH',input_digest=d,program=d,suite='FIXTURE',profile='E768',cell='CH'))
    r=a.recommend(s,sc)
    check('quiescent unaccepted matrix requires engineering review',r['state']=='QUIESCENT_REQUIRES_ENGINEERING_REVIEW' and r['requires_engineering_review'])
    check('quiescence plus missing second vector never means scientific stage complete',not r['scientific_stage_complete'] and not r['adoption_ready'])
    s,sc=fixture();s['table']['sha_A']['M8']['DH']=dict(accepted=False,state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS')
    r=a.recommend(s,sc)
    check('initial engineering issue stays pending',r['state']=='WAIT_INITIAL_TERMINAL')
    check('initial engineering issue has explicit review flag',r['requires_engineering_review'] and not r['scientific_stage_complete'])
    s,sc=fixture();first=a.recommend(s,sc)
    for proposal in first['proposals']:
        p=proposal['profile']
        for d in s['table']:
            s['table'][d][p]['CH']=dict(accepted=True,cycles=1000000,state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE')
            sc['points'].append(dict(cohort=d+p+'CH',input_digest=d,program=d,suite='FIXTURE',profile=p,cell='CH'))
    r=a.recommend(s,sc)
    check('two distinct fully matched classes permit adoption only after quiescence',r['state']=='SEARCH_QUIESCENT' and r['adoption_ready'] and r['scientific_stage_complete'] and not r['requires_engineering_review'])
    return dict(schema='DTC_L2_MLP_ADAPTIVE_CPU_QUALIFICATION_V1',status='PASS',checks=len(checks),names=checks,model_launches=0,registration_mutations=0)

if __name__=='__main__':
    result=run();pathlib.Path(__file__).with_name('QUALIFICATION.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));print(json.dumps(result,indent=2))
