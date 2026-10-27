"""Actual-source isolated registration/recovery CPU integration qualification."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/registry_recovery_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(v,sort_keys=True,indent=2)+'\n').encode())
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    A.mkdir(parents=True,exist_ok=True)
    w=load('journal_candidate',A/'l2_registry_journal.py')
    matrix=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json')
    plan=read(R/'control/EXECUTION_PLAN.json')
    own=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1']
    gen=load('journal_gen_actual',R/'tools/l2_config_generator.py')
    paths=['l2_registry.py','l2_native.py','l2_adaptive.py','l2_config_generator.py','l2_results.py']
    source_before={n:sha(R/'tools'/n)for n in paths}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run=A/('fixtures_'+stamp);run.mkdir()
    checks=[];cases=[]
    def ck(name,test):assert test,name;checks.append(name)
    ids=sorted({p['input_digest']for p in matrix['points']})
    proposal=dict(proposal_id='JOURNAL_CPU_F1536',profile='E1536',parameters={'entries':1536},
                  new_cells=[dict(input_digest=d,cell='DH')for d in ids])
    def fixture(name,hook=None):
        root=run/name;root.mkdir()
        reg=load('registry_actual_'+name,R/'tools/l2_registry.py')
        e=load('native_actual_'+name,R/'tools/l2_native.py')
        fake={'registered_future_requests':{e.REQ:copy.deepcopy(own),'FOREIGN':{'consumed':['UNTOUCHED']}}}
        calls=[]
        def registered():
            for pin in plan['source_pins']:assert sha(pin['path'])==pin['sha256']
            q=fake['registered_future_requests'][e.REQ]
            assert q['budget']==len(q['admitted_specs']) and q['remaining']==q['budget']-len(q['consumed'])
            return fake,{'CPU_ONLY':True},q,plan
        e.registered=registered
        def update(fn):
            # Match production callback atomicity: fn commits only if it returns.
            nxt=copy.deepcopy(fake);fn(nxt)
            assert nxt['registered_future_requests']['FOREIGN']==fake['registered_future_requests']['FOREIGN']
            fake.clear();fake.update(nxt);calls.append(True)
        e.update_authority=update
        reg.R=root
        reg.load=lambda name,f:e if f=='l2_native.py' else gen if f=='l2_config_generator.py' else (_ for _ in()).throw(AssertionError('Unexpected load'))
        put(root/'control/MATRIX_CURRENT.json',matrix);put(root/'control/SEARCH_HISTORY.json',history)
        (root/'control/EXECUTION_PLAN.json').write_bytes((R/'control/EXECUTION_PLAN.json').read_bytes())
        (root/'control/SCOPE.json').write_bytes((R/'control/SCOPE.json').read_bytes())
        for p in matrix['points']:
            if p['profile']=='P0':put(root/'control/specs'/(p['cohort']+'.json'),read(R/'control/specs'/(p['cohort']+'.json')))
        manifest=dict(wrapper_sha256=sha(A/'l2_registry_journal.py'),registry_sha256=sha(R/'tools/l2_registry.py'),execution_plan_sha256=sha(R/'control/EXECUTION_PLAN.json'))
        guard=w.RegistryJournal(reg,e,manifest,hook)
        return root,reg,e,fake,calls,guard
    def assert_closed(name,root,e,fake,calls,guard):
        q=fake['registered_future_requests'][e.REQ];m=read(root/'control/MATRIX_CURRENT.json');h=read(root/'control/SEARCH_HISTORY.json')
        rows=[p for p in m['points']if p['profile']=='E1536'and p['cell']=='DH']
        ck(name+' all35 matrix points exactly once',len(rows)==35 and len({p['cohort']for p in rows})==35)
        ck(name+' grant callback exactly once',len(calls)==1)
        ck(name+' budget increases exactly35',q['budget']==own['budget']+35 and len(q['admitted_specs'])==len(own['admitted_specs'])+35)
        ck(name+' all initial points unchanged',all(p in m['points']for p in matrix['points']))
        ck(name+' history ID exactly once',h['proposal_ids'].count(proposal['proposal_id'])==1)
        ck(name+' COMMITTED journal exists',(root/'control/extension_journal_v1'/proposal['proposal_id']/'COMMITTED.json').exists())
        before=copy.deepcopy(fake)
        ck(name+' repeated call adds nothing',guard.extend(proposal)==[] and fake==before and len(calls)==1)
        cases.append(dict(name=name,status='PASS',fixture_root=str(root),model_launches=0))
    for checkpoint in ('NONE','AFTER_PREPARED','AFTER_AUTHORITY','AFTER_MATRIX','AFTER_HISTORY'):
        fired=[]
        def hook(where):
            if where==checkpoint and not fired:fired.append(where);raise OSError('SYNTHETIC_'+where)
        root,reg,e,fake,calls,guard=fixture(checkpoint,hook)
        value=guard.extend(proposal)
        if checkpoint=='AFTER_PREPARED':
            ck('PREPARED failure has zero grants before retry',not calls and not value)
            ck('PREPARED failure retained as retryable engineering hold',guard.last_issue['state']=='UNGRANTED_ENGINEERING_HOLD_SAFE_TO_RETRY')
            value=guard.extend(proposal)
        ck(checkpoint+' expected fault injected',checkpoint=='NONE'or len(fired)==1)
        assert_closed(checkpoint,root,e,fake,calls,guard)

    # A registered UUID may be consumed before recovery; recovery must not regrant.
    holder={};uuid='SYNTHETIC_SPENT_UUID_MUST_REMAIN';fired=[]
    def spent_hook(where):
        if where=='AFTER_AUTHORITY'and not fired:
            fired.append(where);root,e,fake=holder['root'],holder['engine'],holder['authority'];q=fake['registered_future_requests'][e.REQ]
            c='E2-DTCL2MLP-'+ids[0][:16]+'-DH-E1536-V1'
            q['consumed'][c]={'uuid':uuid,'execution_receipt':{'uuid':uuid,'natural_done':True,'status':'SYNTHETIC_CPU_ONLY'}};q['remaining']-=1
            raise OSError('SYNTHETIC_SPENT_AFTER_GRANT')
    root,reg,e,fake,calls,guard=fixture('SPENT_RECONCILE',spent_hook);holder.update(root=root,engine=e,authority=fake)
    guard.extend(proposal);assert_closed('SPENT_RECONCILE',root,e,fake,calls,guard)
    c='E2-DTCL2MLP-'+ids[0][:16]+'-DH-E1536-V1';q=fake['registered_future_requests'][e.REQ]
    ck('spent UUID/receipt exactly preserved',q['consumed'][c]=={'uuid':uuid,'execution_receipt':{'uuid':uuid,'natural_done':True,'status':'SYNTHETIC_CPU_ONLY'}})
    ck('spent remaining count not refunded',q['remaining']==own['remaining']+34)

    holder={};fired=[]
    def amend_hook(where):
        if where=='AFTER_AUTHORITY'and not fired:
            fired.append(where);root,e,fake=holder['root'],holder['engine'],holder['authority'];q=fake['registered_future_requests'][e.REQ]
            c='E2-DTCL2MLP-'+ids[0][:16]+'-DH-E1536-V1';sp=root/'control/specs'/(c+'.json');s=read(sp)
            s['estimated_peak_model_RAM_bytes']+=1048576;s['limits']['max_process_tree_rss_bytes']+=1048576;s['limits']['max_process_tree_vms_bytes']+=2097152
            put(sp,s);put(root/'control'/(c+'_SPEC.json'),s);q['admitted_specs'][c]=sha(sp)
            raise OSError('SYNTHETIC_RESOURCE_AMEND_AFTER_GRANT')
    root,reg,e,fake,calls,guard=fixture('RESOURCE_AMEND',amend_hook);holder.update(root=root,engine=e,authority=fake)
    guard.extend(proposal);assert_closed('RESOURCE_AMEND',root,e,fake,calls,guard)
    receipt=read(root/'control/extension_journal_v1'/proposal['proposal_id']/'COMMITTED.json')
    ck('legitimate RSS/AS amend explicitly recorded',len(receipt['resource_only_spec_amendments'])==1)

    holder={};fired=[]
    def science_hook(where):
        if where=='AFTER_AUTHORITY'and not fired:
            fired.append(where);root,e,fake=holder['root'],holder['engine'],holder['authority'];q=fake['registered_future_requests'][e.REQ]
            c='E2-DTCL2MLP-'+ids[0][:16]+'-DH-E1536-V1';sp=root/'control/specs'/(c+'.json');s=read(sp)
            s['expected_options']['-gpgpu_clock_domains']=['1410.0:1410.0:1410.0:1700.0']
            put(sp,s);put(root/'control'/(c+'_SPEC.json'),s);q['admitted_specs'][c]=sha(sp)
            raise OSError('SYNTHETIC_SCIENCE_CHANGE')
    root,reg,e,fake,calls,guard=fixture('SCIENCE_MISMATCH',science_hook);holder.update(root=root,engine=e,authority=fake)
    value=guard.extend(proposal);q=fake['registered_future_requests'][e.REQ]
    ck('scientific mismatch requires hold',not value and guard.last_issue['state']=='EXTENSION_RECONCILIATION_HOLD_REQUIRES_REVIEW')
    ck('scientific mismatch does not invent matrix/history completion',len(read(root/'control/MATRIX_CURRENT.json')['points'])==len(matrix['points']) and proposal['proposal_id']not in read(root/'control/SEARCH_HISTORY.json')['proposal_ids'])
    ck('scientific mismatch preserves actual granted budget',q['budget']==own['budget']+35 and len(calls)==1)

    holder={};fired=[]
    def partial_hook(where):
        if where=='AFTER_AUTHORITY'and not fired:
            fired.append(where);e,fake=holder['engine'],holder['authority'];q=fake['registered_future_requests'][e.REQ]
            c='E2-DTCL2MLP-'+ids[0][:16]+'-DH-E1536-V1'
            del q['admitted_specs'][c];q['admitted_inputs'][ids[0]]['specs'].remove(c);q['budget']-=1;q['remaining']-=1
            raise OSError('SYNTHETIC_PARTIAL_GRANT')
    root,reg,e,fake,calls,guard=fixture('PARTIAL_GRANT',partial_hook);holder.update(engine=e,authority=fake)
    guard.extend(proposal)
    ck('partial inconsistent batch holds without regrant',guard.last_issue['state']=='EXTENSION_RECONCILIATION_HOLD_REQUIRES_REVIEW' and len(calls)==1)
    ck('partial batch never marks matrix complete',len(read(root/'control/MATRIX_CURRENT.json')['points'])==len(matrix['points']))

    holder={};fired=[]
    def config_hook(where):
        if where=='AFTER_AUTHORITY'and not fired:
            fired.append(where);root=holder['root'];cfg=root/'DTC/env/DH_E1536/config-0.config';cfg.write_bytes(cfg.read_bytes()+b'\n# synthetic corrupted config\n')
            raise OSError('SYNTHETIC_CONFIG_SHA_MISMATCH')
    root,reg,e,fake,calls,guard=fixture('CONFIG_MISMATCH',config_hook);holder.update(root=root)
    guard.extend(proposal)
    ck('config SHA mismatch holds instead of accepting drift',guard.last_issue['state']=='EXTENSION_RECONCILIATION_HOLD_REQUIRES_REVIEW' and len(calls)==1)

    holder={};fired=[]
    def stale_hook(where):
        if where=='AFTER_PREPARED'and not fired:
            fired.append(where);reg=holder['registry']
            other=dict(proposal_id='SYNTHETIC_OTHER_EXTENSION',profile='F512',parameters={'frfcfs':512},new_cells=[dict(input_digest=d,cell='DH')for d in ids])
            reg.extend(other)
            raise OSError('SYNTHETIC_STALE_PREPARED_BASE')
    root,reg,e,fake,calls,guard=fixture('STALE_PREPARED_MATRIX',stale_hook);holder.update(registry=reg)
    guard.extend(proposal);guard.extend(proposal);q=fake['registered_future_requests'][e.REQ];current=read(root/'control/MATRIX_CURRENT.json')
    ck('stale prepared base merges later valid rows without replacing them',len(current['points'])==len(matrix['points'])+70 and current['revision']==matrix['revision']+2)
    ck('stale prepared base budget counts both grants exactly once',q['budget']==own['budget']+70 and len(calls)==2)
    ck('stale prepared base closes its own journal',(root/'control/extension_journal_v1'/proposal['proposal_id']/'COMMITTED.json').exists())

    root,reg,e,fake,calls,guard=fixture('INITIAL_MATRIX_CHANGED');wrong=read(root/'control/MATRIX_CURRENT.json');wrong['points'][0]['program']='SYNTHETIC_WRONG_IDENTITY';put(root/'control/MATRIX_CURRENT.json',wrong)
    try:guard.extend(proposal)
    except AssertionError:ck('changed historical matrix identity blocks before grant',not calls)
    else:ck('changed historical matrix identity blocks before grant',False)

    root,reg,e,fake,calls,guard=fixture('PIN_MISMATCH');guard.manifest['registry_sha256']='0'*64
    try:guard.extend(proposal)
    except AssertionError:ck('source-pin mismatch blocks before authority',not calls)
    else:ck('source-pin mismatch blocks before authority',False)
    root,reg,e,fake,calls,guard=fixture('STARTUP_RECOVERY')
    _,_,q,p=guard.check();folder,prepared=guard.prepare(proposal,q,p)
    # Simulate process loss after original authority commit, bypass in-process catch.
    original_put=reg.put
    def crash_put(path,value):
        if P(path)==root/'control/MATRIX_CURRENT.json':raise OSError('SYNTHETIC_PROCESS_LOSS')
        original_put(path,value)
    reg.put=crash_put
    try:reg.extend(proposal)
    except OSError:pass
    finally:reg.put=original_put
    restarted=w.RegistryJournal(reg,e,guard.manifest)
    status=restarted.blocking_status()
    ck('restarted instance sees orphan PREPARED even without next proposal',not status['safe_for_scientific_completion'] and len(status['pending'])==1)
    gated=restarted.guard_decision(dict(scientific_stage_complete=True,adoption_ready=True,proposals=[{'KEEP':'UNCHANGED'}]))
    ck('pending journal blocks final scientific completion without removing proposals',not gated['scientific_stage_complete']and not gated['adoption_ready']and gated['proposals']==[{'KEEP':'UNCHANGED'}])
    recovery=restarted.recover_pending()
    ck('startup recovery creates zero authority updates',recovery['authority_updates']==0 and len(calls)==1)
    ck('startup recovery reconciles all pending proposals before new choices',recovery['status']['safe_for_scientific_completion'])
    assert_closed('STARTUP_RECOVERY',root,e,fake,calls,restarted)

    root,reg,e,fake,calls,guard=fixture('STARTUP_UNGRANTED')
    _,_,q,p=guard.check();guard.prepare(proposal,q,p)
    result=guard.recover_pending()
    ck('startup ungranted proposal is not auto-granted',not calls and result['results'][0]['state']=='UNGRANTED_SAFE_TO_RETRY')
    ck('startup ungranted journal holds completion but permits healthy execution',not result['status']['safe_for_scientific_completion']and result['status']['healthy_models_must_continue'])
    guard.extend(proposal);ck('ordinary authorized retry resolves ungranted journal',guard.blocking_status()['safe_for_scientific_completion'])
    ck('all original frozen source hashes remain unchanged',all(sha(R/'tools'/n)==value for n,value in source_before.items()))
    result=dict(schema='DTC_L2_MLP_REGISTRY_JOURNAL_CPU_QUALIFICATION_V1',status='PASS',checks=len(checks),names=checks,
                cases=cases,fixture_root=str(run),actual_source_hashes=source_before,
                wrapper_sha256=sha(A/'l2_registry_journal.py'),model_launches=0,
                production_authority_updates=0,production_source_mutations=0,production_applied=False)
    put(run/'QUALIFICATION.json',result);put(A/'QUALIFICATION.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
