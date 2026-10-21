"""Build five exact new-runtime Q documents after real E native/assertion seal.

No test, compiler, application, registry/CLIENT write, qualification registration
or Git operation. No proposal becomes PASS by this script. All nineteen native
gates must already be independently E-reviewed with actual direct-ELF cases.
"""
from pathlib import Path
import argparse, ast, copy, hashlib, json, subprocess, sys, time
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
PREP=P.parent
PACK=PREP.parent
ROOT=PACK.parents[3]
AUTH='49343880865edb22a17523790fc32dd55975966c'
MASTER='-gpgpu_ep_l2_diag_l2_large_capacity'
WORKS=('convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M')

def require(ok,message):
    if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*2**20),b''):h.update(b)
    return h.hexdigest()
def ref(p):return dict(path=str(Path(p).resolve(strict=True)),sha256=sha(p))
def checked(r):
    require(isinstance(r,dict) and sha(r['path'])==r['sha256'],'real evidence content reference changed')
    return Path(r['path']).resolve(strict=True)
def write(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    require(not p.exists(),'never overwrite an old qualification')
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])

def build(construction_path,output):
    request=read(construction_path)
    require(request.get('schema')=='E2_CAPACITY_QUALIFICATION_CONSTRUCTION_INTAKE_V1','wrong qualification construction intake')
    source_doc=read(checked(request['source_identity_document']));source=source_doc['source_identity']
    suite_path=checked(request['native_replay_result']);suite=read(suite_path)
    require(suite['status']=='NATIVE_EXPECTATIONS_MATCH_PENDING_SCIENTIFIC_QUALIFICATION' and
            suite['lease_released'] is True and suite['original_scientific_history_unchanged'] is True,'actual E native suite not safely closed')
    require(suite['source_identity']==source and suite['actual_starts']==36 and suite['full_applications_started']==0,'wrong actual native source/count')
    owner_path=checked(request['gate_assertion_review']);owner=read(owner_path)
    require(owner.get('schema') in ('E2_FINAL_INPUT_ASSERTION_REVIEW_V1','E2_CAPACITY_NATIVE_GATE_ASSERTION_REVIEW_V1') and
            owner.get('status')=='PASS' and owner.get('reviewed_by') in ('E','E2') and owner['source_identity']==source,'actual root E gate assertion review missing')
    require(checked(owner['native_replay_result'])==suite_path,'gate review names another E suite')
    sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
    import coordinator as c,capacity_policy as cp,capacity_validation as cv
    from headroom_config import options
    required=set(c.NATIVE_GATES)|set(cp.GATES)
    require(required<=set(owner['gates']),'missing original11 or affected8 reviewed native gates')
    cases={r['case_id']:r for r in suite['cases']}
    for name in sorted(required):
        g=owner['gates'][name]
        require(g['status']=='PASS' and g['production_driven'] is True and g.get('rationale'),'native gate not independently reviewed: '+name)
        require(g.get('case_ids') and g.get('evidence_refs'),'actual native case/evidence references required: '+name)
        new_case=False
        for case_id in g['case_ids']:
            r=cases[case_id];n=r['native_exit']
            require(r['kind']=='DIRECT_NATIVE_TEST_ELF' and r['status']=='EXPECTATIONS_MATCH' and
                    n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and n['released_to_native'] is True,'gate lacks true successful direct native case')
            require(read(checked(r['native_exit_receipt']))==n and n['native_process']==r['native_process'],'native direct-parent evidence differs')
            checked(r['raw']);require(all(r['required_checks'].values()),'required native check missing')
            artifact=r['binding']['executed_artifact']
            if artifact.get('source_identity')==source:new_case=True
            else:require(name in ('old_all_off_equivalence','capacity_master_off_equivalence') and artifact.get('reference_only') is True,'old reference cannot qualify new mechanism')
        require(new_case,'every gate must include actual new-production E native evidence')
        for evidence in g['evidence_refs']:checked(evidence)
    seal_path=checked(request['parser_seal']);seal=read(seal_path)
    require(seal.get('schema')=='E2_CAPACITY_PARSER_SEAL_V1' and seal.get('status')=='E_INDEPENDENTLY_REVIEWED_SEALED' and
            seal.get('reviewed_by') in ('E','E2') and seal['source_identity']==source,'actual new parser owner seal missing')
    require(checked(seal['native_replay_result'])==suite_path,'parser seal does not bind actual E replay')
    for key in ('normalized_profiles_reviewed','counter_coverage_reviewed','source_constructor_OFF_FIFO_reviewed'):
        require(seal.get(key) is True,'unreviewed parser/scope obligation: '+key)
    parser_path=checked(seal['terminal_parser']);parser=ref(parser_path)
    module=ast.parse(parser_path.read_text());constants={n.targets[0].id:ast.literal_eval(n.value) for n in module.body
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and
        n.targets[0].id in ('SOURCE_MAPPING_CORE','SOURCE_MAPPING_FRAMEWORK')}
    require(constants.get('SOURCE_MAPPING_CORE')==source['core_source_commit'] and constants.get('SOURCE_MAPPING_FRAMEWORK')==source['framework_source_commit'],'parser native source map differs')
    for key in ('actual_E_native_decoder_evidence','engineering_controls'):
        require(seal.get(key),'real parser decoder/control evidence required')
        for evidence in seal[key]:checked(evidence)
    normalized_path=checked(seal['normalized_scope_profiles']);normalized=read(normalized_path)
    require(normalized['source_identity']==source and set(normalized['profiles'])=={cp.OFF,cp.ON},'normalized profile source differs')
    coverage=copy.deepcopy(seal['counter_coverage_review'])
    require(set(coverage)<=set(normalized['profiles'][cp.ON]['capacities']),'coverage names differ from actual scoped resource vector')
    # UNKNOWN coverage remains UNKNOWN; never auto-promote a source proposal.
    for r in coverage.values():
        if r.get('evidence') and isinstance(r['evidence'],dict) and 'path' in r['evidence']:checked(r['evidence'])
    fifo=copy.deepcopy(seal['off_fifo_capacity_review'])
    require(fifo.get('status')=='INDEPENDENTLY_REVIEWED' and fifo.get('source_constructor_commit')==source['core_source_commit'] and
            fifo.get('capacity_identity_basis')=='EXACT_NATIVE_CONFIG_AND_QUALIFIED_SOURCE_CONSTRUCTOR','OFF FIFO constructor review incomplete')
    checked(fifo['source_constructor_review_evidence'])
    remote_path=checked(request['producer_remote_readback']);remote=read(remote_path);commit=remote['remote_commit']
    require(remote.get('formal_release_status')=='PRODUCER_PASS_DELIVERED_FOR_E_INDEPENDENT_QUALIFICATION' and remote.get('verified_paths'),'formal producer not remotely read back')
    published={Path(r['git_path']).name:r for r in remote['verified_paths']}
    def published_file(name):
        row=published[name];path=checked(row)
        repo=Path(git(path.parent,'rev-parse','--show-toplevel').decode().strip())
        require(git(repo,'show',commit+':'+row['git_path'])==path.read_bytes(),'producer bytes differ from exact publication')
        return path
    release_path=published_file('RELEASE.json');release=read(release_path)
    manifest_path=published_file('FROZEN_CAPACITY_VECTOR_FINAL.json');manifest=read(manifest_path)
    provenance_path=published_file('BUILD_PROVENANCE.json');provenance=read(provenance_path)
    producer_tests=published_file('NATIVE_EVIDENCE_INDEX.json')
    rid=release['identity'];actual_source={k:rid[k] for k in ('core_source_commit','framework_source_commit','vendor_pybind11_commit')};actual_source['binary_sha256']=rid['main']['sha256']
    require(actual_source==source and sha(rid['main']['path'])==source['binary_sha256'],'exact producer runtime differs')
    checked(rid['archive']);require(provenance['identity']==rid and provenance['assertions_enabled'] is True,'archive/build provenance differs')
    require(normalized['capacity_manifest']['sha256']==sha(manifest_path),'normalized scope binds a different capacity manifest')
    build_receipt=read(checked(provenance['build_receipt']))
    build_commands=[r for r in build_receipt['commands'] if '--build' in r['command'] and r['exit_code']==0]
    require(build_commands,'actual successful production cmake build log not recorded')
    build_log=dict(path=build_commands[-1]['log'],sha256=build_commands[-1]['log_sha256']);checked(build_log)
    bindings_path=checked(request['input_bindings_index']);bindings=read(bindings_path)
    require(bindings['schema']=='E2_FINAL_INPUT_BINDING_INDEX_V1' and bindings['source_identity']==source and
            set(bindings['workloads'])==set(WORKS),'five completed new input bindings missing')
    require(checked(bindings['actual_E_native_replay'])==suite_path,'input bindings use another native suite')
    output=Path(output).resolve();require(output.is_relative_to(P) and output!=P and not output.exists(),'new owned qualification child required')
    gates={name:dict(status='PASS',production_driven=True,evidence_path=str(owner_path),evidence_sha256=sha(owner_path),
            reviewed_case_ids=copy.deepcopy(owner['gates'][name]['case_ids']),scope_note=owner['gates'][name]['rationale']) for name in sorted(required)}
    pending=[]
    for work in WORKS:
        new_input_path=checked(bindings['workloads'][work]);new_input=read(new_input_path)
        require(new_input['status']=='PASS' and new_input['source_identity']==source and new_input['workload']==work and
                new_input['new_runtime_reader_semantics_independently_reviewed'] is True and new_input['new_host_prefill_and_read_reference_tests_passed'] is True,'input-native semantics not independently closed')
        specs={name:read(PREP/work/('S_OFF_SPEC_TEMPLATE.json' if name==cp.OFF else 'S_ON_SPEC_TEMPLATE.json')) for name in (cp.OFF,cp.ON)}
        selected,trace,insns=cp.INPUTS[work]
        require(all(s['selection_id']==selected and s['identity']['trace_content_sha256']==trace for s in specs.values()),'input template differs from exact approved selection')
        supported={}
        for name,spec in specs.items():
            p=normalized['profiles'][name];caps=p['capacities'];cfg=p['configuration'];master=int(name==cp.ON)
            effective=options([r['path'] for r in spec['configs']]);require(effective[MASTER]==str(master),'wrong exact E master request')
            features=dict(finite_wbuf=True,unified_wb=False,tvd=False,ro_tag_detach=False,ro_line_mshr_bypass=False,
                adaptive_policy=False,wbuf_entries=caps['wb_payload_slots'],payload_capacity_per_slice=caps['payload_slots_total'],
                bank_count=cfg['bank_count'],ops_per_bank_cycle=cfg['bank_ops_per_physical_cycle'],static_s64=False,wb_local_cap=0)
            supported[name]=dict(research_switches=dict(W=0,V=0,T=0,M=0),effective_options=effective,
                comparison_variable_options=[MASTER],feature_vector=features,
                ideal_vector=dict(copy_free=False,l2_data_free=bool(master),mem_all_data=False,meta=False,read_hit=False,wb=False),
                labels=dict(diagnostic=bool(master),oracle=False,subset=False,readonly_scope='NONE',victim_scope='TRADITIONAL_S_NATIVE'),
                hardware_P1_throughput_eligible=1-master,master_requested=master,
                scope='Exact new-runtime traditional S; master derived effective dimensions and service scope bound separately from requested raw options')
        term=specs[cp.OFF]['identity']['termination_contract'];require(term==specs[cp.ON]['identity']['termination_contract'],'different OFF/ON termination')
        scope=dict(schema='E2_CAPACITY_VALIDATION_SCOPE_V1',authority_commit=AUTH,source_identity=source,
            capacity_manifest_sha256=sha(manifest_path),expected_full_instructions=insns,input_selection_id=selected,
            termination_contract=term,profiles=copy.deepcopy(normalized['profiles']))
        cv.validate_scope(scope,source,supported)
        require(fifo['requested_native_queue_config']==supported[cp.OFF]['effective_options']['-gpgpu_dram_partition_queues'],'OFF constructor review does not match exact input config')
        contract=dict(authority_commit=AUTH,master_option=MASTER,capacity_manifest=ref(manifest_path),
            capacity_manifest_sha256=sha(manifest_path),common_capacity_vector=manifest,
            native_cache_geometry=copy.deepcopy(normalized['native_cache_geometry']),
            normalized_capacity_profiles={name:{k:copy.deepcopy(scope['profiles'][name][k]) for k in ('capacities','configuration')} for name in (cp.OFF,cp.ON)},
            validation_scope=scope,counter_coverage_review=coverage,off_fifo_capacity_review=fifo,
            producer_release_commit=commit,archive_sha256=rid['archive']['sha256'],parser_seal=ref(seal_path))
        q=dict(schema='E2_CAPACITY_EXACT_INPUT_NEW_RUNTIME_QUALIFICATION_V1',campaign_id=c.CAMPAIGN,qualified_by='E',
            status='INDEPENDENTLY_QUALIFIED',qualified_unix=time.time(),source_identity=source,binary_path=rid['main']['path'],
            archive=rid['archive'],producer_release=dict(publication_commit=commit,source_identity=source,**ref(release_path)),
            build_log=build_log,producer_test_manifest=ref(producer_tests),supported_profiles=supported,
            gates=copy.deepcopy(gates),affected_additional_gates=sorted(cp.GATES),terminal_parser=parser,
            input_selection_id=selected,input_semantics_review=ref(new_input_path),independent_native_replay=ref(suite_path),
            native_gate_assertion_review=ref(owner_path),parser_seal=ref(seal_path),capacity_diagnostic=contract,
            default_off_equivalence=dict(status='PASS',review=ref(owner_path),gates=['old_all_off_equivalence','capacity_master_off_equivalence']),
            scope_note='Exact new runtime and '+work+' full input OFF/ON only. Original11 plus affected8 gates are actual E production-native/source assertion evidence; no main61 runtime qualification or old application anchor inherited. Full application native exit, instruction/kernel64slice completion, input hashes and resources remain independently required. New diagnostic is separate from original MAIN; covered large-finite/UNKNOWN and unfavorable outcomes remain valid observations.')
        cp.qualification(q,sha)
        for name in c.NATIVE_GATES|set(q['affected_additional_gates']):checked(dict(path=q['gates'][name]['evidence_path'],sha256=q['gates'][name]['evidence_sha256']))
        pending.append((work,output/work/'QUALIFICATION.json',q,new_input_path))
    # All semantic/source/evidence checks above complete before any Q write.
    rows={}
    for work,path,q,new_input_path in pending:
        write(path,q);rows[work]=dict(qualification=ref(path),qualification_id=sha(path),new_input_review=ref(new_input_path))
    index=dict(schema='E2_CAPACITY_MATERIALIZATION_INPUTS_V1',status='E_INDEPENDENT_QUALIFICATION_COMPLETE',authority_commit=AUTH,
        producer=dict(commit=commit,release=ref(release_path),remote_readback=ref(remote_path)),binary=rid['main'],archive=rid['archive'],
        source_identity=source,capacity_manifest=ref(manifest_path),workloads=rows,registered=False,application_starts_added=0)
    write(output/'E2_CAPACITY_MATERIALIZATION_INPUTS.json',index)
    write(output/'QUALIFICATION_BUILD_RECEIPT.json',dict(status='FIVE_EXACT_QUALIFICATIONS_BUILT_NOT_REGISTERED',source_identity=source,
        construction_input=ref(construction_path),actual_native_suite=ref(suite_path),nineteen_gate_names=sorted(required),
        parser_seal=ref(seal_path),workloads=rows,materialization_index=ref(output/'E2_CAPACITY_MATERIALIZATION_INPUTS.json'),
        registry_writes=0,CLIENT_writes=0,application_starts_added=0))
    return dict(status='FIVE_EXACT_QUALIFICATIONS_BUILT_NOT_REGISTERED',index=ref(output/'E2_CAPACITY_MATERIALIZATION_INPUTS.json'))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--construction-input',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=P/'final_qualifications')
    ap.add_argument('--build-after-real-e-native-and-owner-seals',action='store_true',required=True)
    a=ap.parse_args();print(json.dumps(build(a.construction_input,a.output)),flush=True)

if __name__=='__main__':main()
