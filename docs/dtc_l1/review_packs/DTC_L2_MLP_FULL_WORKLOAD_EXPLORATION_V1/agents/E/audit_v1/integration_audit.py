"""Additional cross-module CPU audit against actual frozen sources and matrix.

No simulator execution or production authority update. All extend writes land in
an isolated Agent E fixture filesystem; only native.update_authority is mocked.
Synthetic performance fixtures are labeled, never published as actual results.
"""
import copy,datetime,hashlib,importlib.util,json,pathlib,types
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/audit_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(x,indent=2,sort_keys=True)+'\n').encode())
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    A.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run=A/('fixture_'+stamp);run.mkdir()
    assert str(run.resolve()).startswith(str(A.resolve())+'/')
    sources={f:sha(R/'tools'/f) for f in ('l2_adaptive.py','l2_config_generator.py','l2_registry.py','l2_native.py','l2_results.py')}
    adaptive=load('Eaudit_adaptive',R/'tools/l2_adaptive.py')
    gen=load('Eaudit_generator',R/'tools/l2_config_generator.py')
    consumer=load('Eaudit_consumer',R/'tools/l2_results.py')
    matrix=read(R/'control/MATRIX_CURRENT.json');scope=read(R/'control/SCOPE.json');history=read(R/'control/SEARCH_HISTORY.json')
    own=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1']
    checks=[];findings=[];tables=[]
    def ck(name,test,detail=None):
        assert test,(name,detail)
        checks.append(dict(name=name,detail=detail))
    ck('actual initial schema retains 35 frozen identities and 350 point cells',len({p['input_digest']for p in matrix['points']})==35 and len(scope['points'])==350)
    ck('all immutable scope rows remain byte-equivalent in current matrix',all(next(v for v in matrix['points']if v['cohort']==p['cohort'])==p for p in scope['points']))

    def synth(gains=None):
        gains=gains or {}
        records={}
        for p in matrix['points']:
            cycles=round(1000000/gains.get(p['profile'],1))
            records[p['cohort']]=dict(state=consumer.PASS,cycles=cycles,uuid='SYNTHETIC_CPU_ONLY',proof=dict(performance_accepted=True,cycles=cycles),archive={'SYNTHETIC_CPU_ONLY':True})
        return records
    records=synth({'E384':1.02,'E768':1.05,'M8':1.02,'M16':1.04})
    summary=consumer.summarize(matrix,records)
    decision=adaptive.recommend(summary,matrix,history)
    ck('actual D schema accepted by actual E on all35',summary['expected_input_count']==35 and decision['expected_input_count']==35)
    ck('initial terminal all35 emits expanded entry/merge profiles',{'E1536','M32'}<={p['profile']for p in decision['proposals']})
    ck('same population and full35 in every extension/combination proposal',all(p['expected_input_count']==35 and len(p['workloads'])==35 and len(p['new_cells'])==35 for p in decision['proposals']))
    ck('candidate classes use two uniform distinct parameter vectors',len({tuple(sorted(x['parameters'].items()))for x in decision['formal_candidates']})==2)
    ck('candidate classes have no per-input parameter overrides',all('parameters'in x and not any(k in x for k in ('per_input','best_of','input_overrides'))for x in decision['formal_candidates']))
    ck('selected CH matching requests cover every frozen identity',all({w['input_digest']for w in p['workloads']}==set(summary['programs']) for p in decision['proposals'] if p['cells']==['CH']))
    failed=copy.deepcopy(records);first=next(p for p in matrix['points']if p['profile']=='E768')
    failed[first['cohort']]=dict(state='FAIL_L2MLP_ARCHIVED_NO_RETRY',cycles=1,proof=dict(performance_accepted=False),archive={'SYNTHETIC_CPU_ONLY':True})
    badsummary=consumer.summarize(matrix,failed);bad=adaptive.recommend(badsummary,matrix,history)
    ck('terminal failure cycles cannot contaminate accepted performance',badsummary['table'][first['input_digest']]['E768']['DH']['cycles'] is None)
    ck('terminal failure explicitly reduces D population to34',badsummary['aggregates']['E768']['ALL']['DH_speedup']['n']==34 and badsummary['aggregates']['E768']['ALL']['DH_speedup']['missing_n']==1)
    ck('failed full-suite profile cannot become formal candidate',all(x['profile']!='E768'for x in bad['formal_candidates']))
    ck('failed terminal coverage cannot mean scientific complete',bad['requires_engineering_review'] and not bad['scientific_stage_complete'])
    missing=copy.deepcopy(records);missing.pop(first['cohort'])
    blocked=adaptive.recommend(consumer.summarize(matrix,missing),matrix,history)
    ck('D missing real cohort blocks E initial stage transition',blocked['state']=='WAIT_INITIAL_TERMINAL' and not blocked['proposals'])

    # Source-based Hash equality is a shared algorithm family, not equal inactive flags.
    core=P('/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim')
    cache=(core/'gpu-cache.cc').read_text();header=(core/'dtc-l1-tag-index.h').read_text()
    ck('traditional B index calls exactly DTC logical_tag_set hash function',
       'case BANK_PRESERVING_XOR_SET_FUNCTION:'in cache and 'set_index = dtc_l1::logical_tag_set(addr, m_nset, true);'in cache)
    ck('common hash preserves low2 bank bits and XORs configured row bits',
       '((line >> 2) ^ (line >> s)) & ((sets / 4) - 1)'in header and '4 * row + static_cast<unsigned>(line & 3)'in header)

    def fixture(name):
        root=run/name;root.mkdir()
        registry=load('Eaudit_registry_'+name,R/'tools/l2_registry.py')
        native=load('Eaudit_native_'+name,R/'tools/l2_native.py')
        fake={'registered_future_requests':{native.REQ:copy.deepcopy(own),'UNRELATED':{'spent':['do-not-touch']}}}
        calls=[]
        def mock_update(fn):
            before=copy.deepcopy(fake);fn(fake);calls.append(True)
            assert before['registered_future_requests']['UNRELATED']==fake['registered_future_requests']['UNRELATED']
            assert before['registered_future_requests'][native.REQ]['consumed']==fake['registered_future_requests'][native.REQ]['consumed']
        native.update_authority=mock_update
        registry.R=root
        registry.load=lambda name,f: native if f=='l2_native.py' else gen if f=='l2_config_generator.py' else (_ for _ in()).throw(AssertionError('Unexpected load '+f))
        put(root/'control/MATRIX_CURRENT.json',matrix);put(root/'control/SEARCH_HISTORY.json',history)
        # Actual canonical P0 science specs, config references stay read-only production.
        for point in matrix['points']:
            if point['profile']=='P0':
                put(root/'control/specs'/(point['cohort']+'.json'),read(R/'control/specs'/(point['cohort']+'.json')))
        return registry,native,fake,calls

    reg,native,fake,calls=fixture('normal_extend')
    inputs=sorted(summary['programs'])
    params=[{'entries':1536},{'merge':32},{'miss_queue':256},{'frfcfs':512},
            {'entries':1536,'merge':32,'miss_queue':256,'frfcfs':512}]
    before_count=len(matrix['points']);expected_added=0;parameter_checks=0
    for overrides in params:
        parameters=gen.normalize(overrides);profile=adaptive.profile_name(parameters)
        for cell in ('DH','CH'):
            proposal=dict(proposal_id='SYNTHETIC_'+profile+'_'+cell,profile=profile,parameters=parameters,
                          new_cells=[dict(input_digest=d,cell=cell)for d in inputs])
            rows=reg.extend(proposal);expected_added+=35
            ck('registry adds full35 unique future '+profile+' '+cell,len(rows)==35 and len({r['cohort']for r in rows})==35)
            detail=[]
            for row in rows:
                basepoint=next(p for p in matrix['points']if p['profile']=='P0'and p['input_digest']==row['input_digest']and p['cell']==cell)
                base=read(R/'control/specs'/(basepoint['cohort']+'.json'))
                spec=read(reg.R/'control/specs'/(row['cohort']+'.json'))
                options=gen.effective_options([P(v['path']).read_text()for v in spec['configs']])
                oldopts=gen.effective_options([P(v['path']).read_text()for v in base['configs']])
                changed={k for k in options if options[k]!=oldopts[k]}
                targets={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'}
                assert changed<=targets and len(options)==len(oldopts) and len(spec['expected_options'])==270
                assert set(spec['expected_options'])==set(base['expected_options']) and set(options)<=set(spec['expected_options'])
                assert all(spec['expected_options'][k]==[options[k]] for k in changed)
                assert all(spec['expected_options'][k]==base['expected_options'][k]for k in set(options)-targets)
                assert options['-gpgpu_clock_domains']=='1410.0:1410.0:1410.0:850.0'
                assert options['-gpgpu_dram_partition_queues']=='64:64:64:64'
                assert all(options[k]==oldopts[k] for k in options if 'dtc' in k or k=='-gpgpu_cache:dl1')
                assert spec['core_commit']==base['core_commit'] and spec['framework_commit']==base['framework_commit'] and spec['binary_sha256']==base['binary_sha256']
                assert spec['trace_entry']==base['trace_entry'] if 'trace_entry'in spec else True
                assert spec['native_simulator_argv'][0:3]==base['native_simulator_argv'][0:3]
                expected_index='B' if cell=='CH' else None
                if cell=='CH':assert options['-gpgpu_cache:dl1'].split(',')[1].split(':')[4]=='B'
                else:assert options['-gpgpu_dtc_l1_tag_hash_bankrow']=='1'
                parameter_checks+=1
                detail.append(dict(input_digest=row['input_digest'],expected_options=len(spec['expected_options']),explicit_text_options=len(options),changed=sorted(changed),config_sha256=[v['sha256']for v in spec['configs']]))
            tables.append(dict(profile=profile,cell=cell,parameters=parameters,cells=detail))
            count=len(read(reg.R/'control/MATRIX_CURRENT.json')['points']);budget=fake['registered_future_requests'][native.REQ]['budget']
            ck('registry exact duplicate does not add identities '+profile+' '+cell,
               reg.extend(proposal)==[] and len(read(reg.R/'control/MATRIX_CURRENT.json')['points'])==count and fake['registered_future_requests'][native.REQ]['budget']==budget)
    ck('all350 future specs preserve complete270-option contract',parameter_checks==350)
    ck('finite budget increased only by350 fresh fixture identities',fake['registered_future_requests'][native.REQ]['budget']==own['budget']+350)
    extmatrix=read(reg.R/'control/MATRIX_CURRENT.json');exthistory=read(reg.R/'control/SEARCH_HISTORY.json')
    ck('future matrix preserves all initial350 rows',len(extmatrix['points'])==before_count+350 and all(p in extmatrix['points']for p in matrix['points']))
    # Use actual result consumer with the real registry-created matrix/schema.
    extrecords=copy.deepcopy(records)
    for p in extmatrix['points']:
        if p['cohort']not in extrecords:
            extrecords[p['cohort']]=dict(state=consumer.PASS,cycles=1000000,uuid='SYNTHETIC_CPU_ONLY',proof=dict(performance_accepted=True,cycles=1000000),archive={'SYNTHETIC_CPU_ONLY':True})
    extdecision=adaptive.recommend(consumer.summarize(extmatrix,extrecords),extmatrix,exthistory)
    ck('real future registry output accepted by D then E without unknown-profile error','schema'in extdecision)
    ck('future profiles already registered cannot be proposed as fresh cells',all(p['profile']not in{adaptive.profile_name(gen.normalize(x))for x in params} for p in extdecision['proposals']))

    # Crash consistency injection: authority commit succeeds, next matrix write fails.
    crash,crashnative,crashreg,crashcalls=fixture('authority_commit_gap')
    proposal=dict(proposal_id='SYNTHETIC_COMMIT_GAP',profile='E1536',parameters={'entries':1536},new_cells=[dict(input_digest=d,cell='DH')for d in inputs])
    original_put=crash.put
    def fail_matrix_write(path,value):
        if str(path).endswith('/control/MATRIX_CURRENT.json'):raise OSError('SYNTHETIC_CRASH_AFTER_AUTHORITY_COMMIT')
        return original_put(path,value)
    crash.put=fail_matrix_write
    try:crash.extend(proposal)
    except OSError:pass
    else:raise AssertionError('Failure injection did not fire')
    current=read(crash.R/'control/MATRIX_CURRENT.json')
    grant=crashreg['registered_future_requests'][crashnative.REQ]
    unmatched=[c for c in grant['admitted_specs']if c.endswith('-DH-E1536-V1')and not any(p['cohort']==c for p in current['points'])]
    crash.put=original_put
    retry_error=None
    try:crash.extend(proposal)
    except AssertionError as exc:retry_error=type(exc).__name__
    findings.append(dict(id='REGISTRY_EXTEND_COMMIT_GAP',severity='ENGINEERING_RECOVERY_RISK',
        reproduced=len(unmatched)==35 and retry_error=='AssertionError',
        orphan_authorized_identities=len(unmatched),retry_error=retry_error,
        production_affected=False,
        exact_trigger='authority callback commit succeeds; MATRIX_CURRENT write fails before SEARCH_HISTORY commit',
        consequence='35 admitted identities absent from matrix; exact extend retry hits c-not-in-admitted assertion; no identities consumed in fixture',
        suggested_fix='Coordinator additive reconciliation journal: verify proposal/normalized params/spec SHA/config/source against admitted grants; append exactly matching missing points and history without increasing budget or resetting consumed IDs. Permit idempotent registration only when existing SHA and input linkage match; stop on mismatch.',
        evidence_root=str(crash.R)))
    ck('crash gap is reproduced without production mutation',findings[-1]['reproduced'])
    ck('frozen source hashes unchanged after all cross-module fixtures',all(sha(R/'tools'/f)==v for f,v in sources.items()))
    result=dict(schema='DTC_L2_MLP_E_CROSS_MODULE_AUDIT_V1',status='PASS_WITH_ENGINEERING_FINDING',
        actual_source_hashes=sources,actual_matrix_sha256=sha(R/'control/MATRIX_CURRENT.json'),
        actual_frozen_scope_sha256=sha(R/'control/SCOPE.json'),fixture_root=str(run),
        checks=len(checks),check_details=checks,future_spec_full_contract_cases=parameter_checks,
        findings=findings,model_launches=0,production_authority_updates=0,production_source_mutations=0,
        synthetic_results_never_performance_evidence=True)
    put(run/'AUDIT_RESULT.json',result);put(A/'AUDIT_RESULT.json',result);put(A/'FUTURE_PROFILE_CONFIG_CHECKS.json',tables)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
