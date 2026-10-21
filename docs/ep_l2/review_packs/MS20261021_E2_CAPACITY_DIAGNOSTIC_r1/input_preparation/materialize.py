"""DRAFT: materialize exact specs only after a real producer and E qualification.

No registry/CLIENT writes, lease, controller action, simulator or native call.
All three input documents and explicit --materialize-formal-release are required.
See MATERIALIZATION_INTERFACE.md. Never fill this interface with placeholders.
"""
from pathlib import Path
import argparse, copy, hashlib, json, re, subprocess, sys, time

P=Path(__file__).resolve().parent
ROOT=P.parents[4]
AUTHORITY='49343880865edb22a17523790fc32dd55975966c'
MASTER='-gpgpu_ep_l2_diag_l2_large_capacity'
BUCKET='five_input_capacity_diagnostic_user_approved_20261021'
MAIN61='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
WORKLOADS=('convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M')
SOURCE_FIELDS=('core_source_commit','framework_source_commit','binary_sha256','vendor_pybind11_commit')

def require(ok,message):
    if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text())
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(4*2**20),b''):h.update(block)
    return h.hexdigest()
def ref(p):return dict(path=str(Path(p).resolve(strict=True)),sha256=digest(p))
def checked_ref(value):
    require(isinstance(value,dict) and set(('path','sha256'))<=set(value),'real content reference required')
    require(re.fullmatch('[0-9a-f]{64}',value['sha256']) is not None,'invalid reference SHA256')
    p=Path(value['path']).resolve(strict=True)
    require(p.is_file() and digest(p)==value['sha256'],'missing or changed content: '+str(p))
    return p
def write(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    require(not p.exists(),'refuse to replace an existing materialized document: '+str(p))
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def verify_source(source):
    require(isinstance(source,dict),'real source identity required')
    for k in SOURCE_FIELDS:
        n=64 if k=='binary_sha256' else 40
        require(isinstance(source.get(k),str) and re.fullmatch('[0-9a-f]{'+str(n)+'}',source[k]) is not None,'invalid source identity: '+k)
    require(source['binary_sha256']!=MAIN61,'main61 cannot supply a new capacity anchor')
def verify_formal_producer(index,source):
    producer=index['producer'];commit=producer['commit']
    require(re.fullmatch('[0-9a-f]{40}',commit) is not None,'formal producer commit required')
    release=checked_ref(producer['release'])
    tree=Path(subprocess.check_output(['git','-C',str(release.parent),'rev-parse','--show-toplevel'],text=True).strip())
    rel=release.relative_to(tree).as_posix()
    published=subprocess.check_output(['git','-C',str(tree),'show',commit+':'+rel])
    require(published==release.read_bytes(),'formal release differs from exact producer commit')
    remote=read(checked_ref(producer['remote_readback']))
    require(remote.get('remote_commit')==commit and bool(remote.get('verified_paths')),'producer remote byte readback missing')
    binary=checked_ref(index['binary']);archive=checked_ref(index['archive'])
    require(index['binary']['sha256']==source['binary_sha256'],'main SHA differs from new source identity')
    require(binary!=archive,'main and archive must be distinct real artifacts')
    return producer,binary,archive

def materialize(source_path,capacity_path,index_path,output):
    # Import the published original runtime only. Candidate source trees cannot
    # substitute for central adoption and its source-bound CLIENT contract.
    sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
    import runner, capacity_policy, coordinator
    from headroom_config import options
    source_doc=read(source_path);source=source_doc.get('source_identity',source_doc)
    verify_source(source)
    manifest=read(capacity_path);manifest_ref=ref(capacity_path);index=read(index_path)
    require(index.get('schema')=='E2_CAPACITY_MATERIALIZATION_INPUTS_V1','wrong E materialization input schema')
    require(index.get('status')=='E_INDEPENDENT_QUALIFICATION_COMPLETE','not independently E-qualified')
    require(index.get('authority_commit')==AUTHORITY,'wrong approval')
    require(set(index['workloads'])==set(WORKLOADS),'exact five workload qualification bindings required')
    producer,binary,archive=verify_formal_producer(index,source)
    registry=read('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')['mechanism_study_20261019_v1']
    require(registry.get('capacity_diagnostic_amendment',{}).get('authority_commit')==AUTHORITY,'original central amendment not adopted')
    require(registry.get('capacity_diagnostic_matrix')==capacity_policy.matrix(),'central ten-condition matrix differs from published policy')
    require(registry['actual_starts']==36,'materialize exactly once before this new batch starts; do not replace live specs')
    output=Path(output).resolve()
    require(output.is_relative_to(P.resolve()) and output!=P.resolve(),'output must be a new child of input_preparation')
    require(not output.exists(),'refuse to overwrite any old materialization')
    auth=read(P/'FIVE_INPUTS_PREPARATION.json');known={r['workload']:r for r in auth['inputs']}
    ready=[];pairs=[];input_reviews=[]
    matrix={r['condition_id']:r for r in capacity_policy.matrix()['conditions']}
    for work in WORKLOADS:
        binding=index['workloads'][work]
        qp=checked_ref(binding['qualification']);q=read(qp);qid=digest(qp)
        require(q['source_identity']==source,'qualification is not for exact new source')
        contract=capacity_policy.qualification(q,digest)
        require(contract.get('capacity_manifest_sha256')==manifest_ref['sha256'],'qualification does not bind exact formal capacity manifest')
        if 'capacity_manifest' in contract:require(checked_ref(contract['capacity_manifest'])==Path(capacity_path).resolve(),'qualification manifest path differs')
        require(contract.get('producer_release_commit')==producer['commit'],'qualification does not bind exact formal producer commit')
        require(contract.get('archive_sha256')==index['archive']['sha256'],'qualification does not bind real production archive')
        for gate in q['gates'].values():
            require(gate['status']=='PASS' and gate['production_driven'] is True,'unpassed or nonproduction E qualification gate')
            require(digest(gate['evidence_path'])==gate['evidence_sha256'],'qualification gate evidence changed')
        parser=q['terminal_parser'];checked_ref(parser)
        rp=checked_ref(binding['new_input_review']);review=read(rp)
        require(review.get('status')=='PASS' and review.get('reviewed_by') in ('E','E2'),'independent new-runtime input review required')
        require(review.get('source_identity')==source and review.get('workload')==work,'new native reader/source scope mismatch')
        require(review.get('trace_content_sha256')==known[work]['complete_input_trace_sha256'],'review changed full input')
        require(review.get('new_runtime_reader_semantics_independently_reviewed') is True,'old reader binding cannot be inherited')
        admission=review['input_scope_admission']
        require(isinstance(admission,dict),'new source-bound input admission required')
        # Legacy complete-byte/opcode reports may be retained only through a
        # newly hashed report that names the exact new runtime and actual E tests.
        retained=admission.get('retained_input_scope')
        require(isinstance(retained,dict),'explicit new retained-input review report required')
        retained_report=read(checked_ref(retained))
        require(retained_report.get('status')=='UNCHANGED_COMPLETE_INPUT_PARSER_AND_CONTENT_SCOPE','wrong new input portability review')
        require(retained_report.get('new_source_identity')=={k:source[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')},'retained input binding names old runtime')
        require(retained_report.get('new_host_prefill_and_read_reference_tests_passed') is True,'new input/reference native tests not passed')
        require(bool(retained_report.get('source_trees')) and all(x['old']==x['new'] for x in retained_report['source_trees']),'native input parser/opcode delta requires a different reviewed adapter')
        pair_id='CAPACITY_DIAGNOSTIC_'+work+'_OFF_ON_NEW_RUNTIME';member=[]
        traces=None
        for suffix,profile,master in [('S_OFF','S',0),('S_ON','S_L2_DATA_FREE_LARGE_CAPACITY',1)]:
            condition_id='V3_CAPACITY_'+work+'_'+suffix
            require(condition_id in matrix,'published capacity_policy condition naming differs')
            spec=read(P/work/(suffix+'_SPEC_TEMPLATE.json'))
            sem=copy.deepcopy(q['supported_profiles'][profile])
            require(sem['comparison_variable_options']==[MASTER],'exact pair comparison must vary only master switch')
            require(sem['research_switches']==dict(W=0,V=0,T=0,M=0),'capacity matrix is traditional S only')
            spec.update(schema='E2_CAPACITY_EXACT_SPEC_V1',preparation_status='NEW_RUNTIME_E_QUALIFIED_AWAIT_ORIGINAL_DISPATCH',
                binary=str(binary),vendor_pybind11_commit=source['vendor_pybind11_commit'],
                qualification_id=qid,parser=parser,profile=profile,profile_semantics=sem,labels=sem['labels'],
                condition_id=condition_id,budget_bucket=BUCKET,comparison_group='CAPACITY_DIAGNOSTIC_'+work,
                maximum_result_bytes=384*2**20,timeout_seconds=10800,
                input_scope_admission=copy.deepcopy(admission),auxiliary_assets=copy.deepcopy(review['auxiliary_assets']),
                independent_new_input_review=ref(rp),producer_release=producer['release'],
                capacity_manifest=manifest_ref,production_archive=ref(archive),
                atomic_input_scope=copy.deepcopy(review['atomic_input_scope']))
            if review.get('native_legacy_semantic_proof'):spec['native_legacy_semantic_proof']=copy.deepcopy(review['native_legacy_semantic_proof'])
            for key in list(spec):
                if key.startswith('historical_') or key in ('final_run_key','new_native_input_semantics_review'):
                    del spec[key]
            spec['identity'].update({k:source[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')})
            spec['identity'].update(feature_vector=sem['feature_vector'],ideal_vector=sem['ideal_vector'])
            effective=options([v['path'] for v in spec['configs']])
            require(effective==sem['effective_options'] and effective[MASTER]==str(master),'exact final config differs from independently qualified whitelist')
            configs=runner.legacy.asset_manifest(spec['configs'],ordered=True)
            assets=runner.legacy.asset_manifest(spec['auxiliary_assets'])
            if traces is None:traces=runner.legacy.asset_manifest(spec['trace_files'])
            require(runner.legacy.content_hash(traces)==known[work]['complete_input_trace_sha256'],'current complete trace bytes changed')
            require(spec['identity']['trace_content_sha256']==known[work]['complete_input_trace_sha256'],'different requested input')
            selection=registry['input_selections'][spec['selection_id']]
            require(digest(selection['path'])==selection['sha256'],'D selection changed')
            chosen=selection['selection']['full_input_identity']
            require(chosen['trace_content_sha256']==spec['identity']['trace_content_sha256'] and chosen['expected_full_instructions']==spec['expected_full_instructions'],'different complete input/instructions')
            runner.legacy.validate_config_closure(spec);runner.legacy.validate_trace_closure(spec)
            atomic=runner.legacy.validate_atomic_input_scope(spec,admission,traces)
            runner.legacy.validate_native_legacy_semantic_proof(spec,admission,traces)
            spec['identity']['runtime_config_sha256']=runner.legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']))
            invariant=dict(source=source,trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],
                termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,
                nonresearch_options={k:v for k,v in effective.items() if k!=MASTER},comparison_variable_options=[MASTER])
            spec['comparison_invariants_sha256']=runner.legacy.content_hash(invariant)
            key=runner.run_key(spec['identity'])
            require(not any(a['run_key']==key for a in registry['attempts']),'existing charged/reserved endpoint; no duplicate or retry materialization')
            for k in ('selection_id','profile','comparison_group','budget_bucket'):require(spec[k]==matrix[condition_id][k],'spec differs from adopted condition: '+k)
            sp=output/work/(suffix+'_SPEC.json')
            row=dict(condition_id=condition_id,workload=work,profile=profile,pair_id=pair_id,
                qualification_id=qid,qualification=ref(qp),run_key=key,spec_path=sp,
                expected_full_instructions=spec['expected_full_instructions'],maximum_result_bytes=spec['maximum_result_bytes'])
            ready.append((sp,spec,row))
            member.append((spec,key))
            input_reviews.append(dict(condition_id=condition_id,configs=configs,auxiliary_assets=assets,traces=traces,
                independent_new_input_review=ref(rp),atomic_scope=atomic,comparison_invariants=invariant))
        off,on=[x[0] for x in member]
        require(off['comparison_invariants_sha256']==on['comparison_invariants_sha256'],'OFF/ON changed invariant beyond master')
        changed={k:[off['profile_semantics']['effective_options'].get(k),on['profile_semantics']['effective_options'].get(k)]
                 for k in set(off['profile_semantics']['effective_options'])|set(on['profile_semantics']['effective_options'])
                 if off['profile_semantics']['effective_options'].get(k)!=on['profile_semantics']['effective_options'].get(k)}
        require(changed=={MASTER:['0','1']},'pair differs beyond exactly one requested master option')
        pairs.append(dict(pair_id=pair_id,left_run_key=member[0][1],right_run_key=member[1][1],
            mechanism='CAPACITY_DIAGNOSTIC_NEW_RUNTIME_S_OFF_VS_S_ON; original MAIN denominator unchanged',
            workload=work,diagnostic=True,capacity_manifest=manifest_ref))
    require(len(ready)==10 and len({r[2]['run_key'] for r in ready})==10,'exact ten distinct new run keys required')
    # All validation precedes writes. This is still preparation only; registration,
    # source binding, resource leases and controller dispatch remain E owner work.
    for sp,spec,row in ready:write(sp,spec)
    conditions=[]
    for sp,spec,row in ready:
        row=dict(row);del row['spec_path'];row['spec']=ref(sp);conditions.append(row)
    queue=dict(campaign_id=registry['campaign_id'],authority_commit=coordinator.AUTHORITY,
        capacity_authority_commit=AUTHORITY,prepared_by='E',
        input_and_profile_freeze_unix=time.time(),specs=[r['spec'] for r in conditions],pairs=pairs)
    write(output/'QUEUE.json',queue)
    write(output/'INPUT_CONFIG_REVIEWS.json',dict(status='NEW_RUNTIME_INDEPENDENT_INPUT_CONFIG_CLOSED_NO_START',conditions=input_reviews))
    plan=dict(schema='E2_CAPACITY_DIAGNOSTIC_EXECUTION_PLAN_V1',status='PREPARED_NOT_DISPATCHED',at_unix=time.time(),
        authority_commit=AUTHORITY,source_identity=source,source_identity_document=ref(source_path),
        formal_producer=producer,binary=ref(binary),archive=ref(archive),capacity_manifest=manifest_ref,
        E_qualification_input_index=ref(index_path),conditions=conditions,pairs=pairs,queue=ref(output/'QUEUE.json'),
        maximum_new_starts=10,historical_charged_starts=36,maximum_campaign_starts=46,
        maximum_total_result_bytes=10*384*2**20,collector_and_metadata_planning_reserve_bytes=64*2**20,
        timeout_seconds=10800,max_concurrency=2,T0=registry['t0_unix'],
        start_deadline=registry['start_deadline_unix'],intake_deadline=registry['intake_deadline_unix'],
        original_controller_only=True,no_registry_or_CLIENT_mutations=True,no_lease_or_application_started=True,
        main61_qualification_inherited=False,old_anchor_reused=False,no_automatic_retry=True)
    write(output/'PLAN.json',plan)
    return dict(status='TEN_NEW_RUNTIME_SPECS_MATERIALIZED_NO_REGISTRATION_OR_START',plan=ref(output/'PLAN.json'),conditions=10)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-identity',required=True,type=Path)
    ap.add_argument('--capacity-manifest',required=True,type=Path)
    ap.add_argument('--qualifications',required=True,type=Path)
    ap.add_argument('--output',type=Path,default=P/'materialized')
    ap.add_argument('--materialize-formal-release',action='store_true',required=True,
        help='Owner asserts all inputs are formally delivered and independently E-qualified, never placeholders')
    args=ap.parse_args()
    print(json.dumps(materialize(args.source_identity,args.capacity_manifest,args.qualifications,args.output)),flush=True)

if __name__=='__main__':main()
