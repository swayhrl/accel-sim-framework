"""Bounded input-only preparation. No qualification, registry write or execution."""
from pathlib import Path
import copy, hashlib, json, math, os, subprocess, sys, time

P = Path(__file__).resolve().parent
ROOT = P.parents[4]
PACKS = P.parents[1]
AUTH = '49343880865edb22a17523790fc32dd55975966c'
AUTH_REL = 'docs/ep_l2/review_packs/MS20261021_D_CAPACITY_DIAGNOSTIC_AUTHORIZED_r2/'
REGISTRY = Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
sys.path.insert(0, str(ROOT/'util/ep_l2/mechanism_e'))
import runner

def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return dict(path=str(Path(p).resolve()), sha256=sha(p))
def write(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
def gitfile(name):
    return subprocess.check_output(['git','-C',str(ROOT),'show',AUTH+':'+AUTH_REL+name])
def file_stat(p):
    p=Path(p).resolve(strict=True); s=p.stat()
    assert p.is_file()
    return dict(path=str(p), device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                bytes=s.st_size, allocated_bytes=s.st_blocks*512,
                mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)
def sample(p):
    with Path(p).open('rb') as f:
        first=f.read(4096); f.seek(max(0,os.fstat(f.fileno()).st_size-4096)); last=f.read(4096)
    return dict(first_4096_sha256=hashlib.sha256(first).hexdigest(),
                last_4096_sha256=hashlib.sha256(last).hexdigest(),
                sample_is_not_full_content_validation=True)
def tree_size(p):
    # Only one known completed endpoint directory. No file bodies read.
    logical=allocated=0
    for root,dirs,files in os.walk(p):
        for name in files:
            path=Path(root)/name
            if path.is_symlink(): continue
            st=path.stat();logical+=st.st_size;allocated+=st.st_blocks*512
    return dict(logical_bytes=logical, allocated_bytes=allocated)

def main():
    auth=json.loads(gitfile('AUTHORIZED_FIVE_PAIRS.json'))
    approved=json.loads(gitfile('USER_APPROVAL.json'))
    source_files=json.loads(gitfile('FILES_SHA256.json'))
    for name,expected in source_files.items():
        assert hashlib.sha256(gitfile(name)).hexdigest()==expected
    registry=read(REGISTRY)['mechanism_study_20261019_v1']
    assert registry['actual_starts']>=36
    rows=[]; queue=[]
    for entry in auth['rows']:
        w=entry['workload']; out=P/w;out.mkdir(exist_ok=True)
        template=(PACKS/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/convolutionSeparable_S_SPEC.json'
                  if w=='convolutionSeparable' else PACKS/f'MS20261020_E2_MAIN_ROLLING_r1/{w}/S_SPEC.json')
        spec=read(template); old_id=entry['historical_main61_S_attempt']
        prior=registry['accepted_results'][old_id]
        assert sha(prior['path'])==prior['sha256']==entry['historical_S_receipt_sha256']
        receipt=read(prior['path']);audit=receipt['input_audit']
        assert receipt['independent_acceptance']=='PASS' and receipt['complete_input_verified']
        assert spec['selection_id']==entry['selection_id']
        assert spec['identity']['trace_content_sha256']==entry['complete_input_trace_sha256']
        assert runner.legacy.content_hash(audit['traces'])==entry['complete_input_trace_sha256']
        selection=registry['input_selections'][entry['selection_id']]
        assert sha(selection['path'])==selection['sha256']
        chosen=selection['selection']['full_input_identity']
        assert chosen['expected_full_instructions']==entry['expected_instructions']
        assert chosen['trace_content_sha256']==entry['complete_input_trace_sha256']
        runner.legacy.validate_trace_closure(spec)
        runner.legacy.validate_config_closure(spec)
        auxiliaries=runner.legacy.asset_manifest(spec['auxiliary_assets'])
        assert auxiliaries==audit['auxiliary_assets']
        configs=runner.legacy.asset_manifest(spec['configs'],ordered=True)
        assert configs==audit['configs']
        # Reuse historical full-content identity only as a declared identity.
        # Independent launch inspection must rehash complete current files.
        old_trace={x['name']:x for x in audit['traces']};trace_rows=[]
        for t in spec['trace_files']:
            record=file_stat(t['path']); expected=old_trace[t['name']]
            assert record['bytes']==expected['bytes']
            record.update(name=t['name'],historical_complete_sha256=expected['sha256'],
                          historical_identity_source=ref(prior['path']))
            if t['name']==spec['entry_trace_name']:
                assert sha(t['path'])==expected['sha256']
                record.update(current_full_sha256=expected['sha256'],current_verification='FULL_SMALL_ENTRY_FILE')
            else:
                record.update(sample(t['path']))
                record['current_verification']='STAT_SIZE_AND_BOUNDED_SAMPLES_ONLY_FINAL_FULL_HASH_PENDING'
            trace_rows.append(record)
        atomic=runner.legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],audit['traces'])
        source_overlay=Path(spec['configs'][-1]['path']).read_text()
        assert '-gpgpu_ep_l2_diag_l2_large_capacity' not in source_overlay
        modes=[]
        for mode,master in [('S_OFF',0),('S_ON',1)]:
            condition='V3_CAPACITY_'+w+'_'+mode
            profile='S_CAPACITY_OFF' if master==0 else 'S_L2_DATA_FREE_LARGE_CAPACITY'
            cfg=out/(mode+'.config')
            cfg.write_text('# INPUT PREPARATION ONLY: requires new A2 runtime and independent E qualification.\n'+source_overlay+'\n-gpgpu_ep_l2_diag_l2_large_capacity '+str(master)+'\n')
            cloned=copy.deepcopy(spec)
            cloned.update(schema='E2_CAPACITY_SPEC_TEMPLATE_NOT_LAUNCHABLE_V1',
                preparation_status='BLOCKED_NEW_A2_FORMAL_PRODUCER_AND_E_QUALIFICATION',
                binary=None,vendor_pybind11_commit=None,qualification_id=None,parser=None,
                profile=profile,profile_semantics=None,condition_id=condition,
                budget_bucket='USER_APPROVED_CAPACITY_DIAGNOSTIC_PENDING_E_POLICY_ADOPTION',
                comparison_group='V3_CAPACITY_DIAGNOSTIC_'+w,
                labels=dict(diagnostic=True,oracle=False,readonly_scope='NONE',
                            subset=profile,interpretation='SAME_NEW_BINARY_CAPACITY_DATA_SERVICE_DIAGNOSTIC'),
                comparison_invariants_sha256=None,maximum_result_bytes=None,
                expected_full_instructions=entry['expected_instructions'],
                expected_kernel_count=len(spec['trace_files'])-1,
                switch_requested=master,final_run_key=None,
                runtime_new_binary_anchor_required=True,
                input_content_identity_only_reused=True,
                main61_runtime_qualification_inherited=False)
            cloned['configs'][-1]={'name':'profile.config','path':str(cfg.resolve())}
            for name in ['core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','feature_vector','ideal_vector']:
                cloned['identity'][name]=None
            # Old native semantic proofs remain explicitly historical material,
            # rather than assertions that the changed runtime is qualified.
            cloned['historical_input_scope_admission']=cloned.pop('input_scope_admission')
            cloned['input_scope_admission']=None
            for key in ['atomic_input_scope','native_legacy_semantic_proof']:
                if key in cloned:cloned['historical_'+key]=cloned.pop(key)
            cloned['new_native_input_semantics_review']='PENDING_A2_READER_SOURCE_DELTA_AND_E_BINDING'
            sp=out/(mode+'_SPEC_TEMPLATE.json');write(sp,cloned)
            effective=runner.options([x['path'] for x in cloned['configs']])
            assert effective['-gpgpu_ep_l2_diag_l2_large_capacity']==str(master)
            modes.append(dict(condition_id=condition,profile=profile,master=master,
                              config=ref(cfg),template=ref(sp),effective_options=effective,
                              final_run_key=None))
            queue.append(dict(condition_id=condition,workload=w,master=master,
                              spec_template=ref(sp),launchable=False))
        off,on=(x['effective_options'] for x in modes)
        delta={key:[off.get(key),on.get(key)] for key in set(off)|set(on) if off.get(key)!=on.get(key)}
        assert delta=={'-gpgpu_ep_l2_diag_l2_large_capacity':['0','1']}
        cost=tree_size(Path(prior['path']).parent)
        empirical=dict(attempt_id=old_id,receipt=ref(prior['path']),
                wall_seconds=receipt['wall_seconds'],peak_process_tree_rss_bytes=receipt['peak_process_tree_rss_bytes'],
                result_directory_bytes=cost,
                source='Historical main61 S only, cost reference; never new-binary qualification or anchor')
        predicted=[math.ceil(receipt['wall_seconds']*.75),math.ceil(receipt['wall_seconds']*2.5)]
        row=dict(workload=w,status='INPUT_METADATA_CLOSED_NEW_RUNTIME_QUALIFICATION_PENDING',
                 selection_id=entry['selection_id'],selection=ref(selection['path']),
                 complete_input_trace_sha256=entry['complete_input_trace_sha256'],
                 expected_instructions=entry['expected_instructions'],expected_kernels=len(spec['trace_files'])-1,
                 epoch_scope=entry['epoch_scope'],expected_slices=64,
                 traces=trace_rows,auxiliary_assets=auxiliaries,old_input_only_atomic_scope=atomic,
                 input_scope_portability='Complete trace byte/opcode evidence can be retained only after new native reader equivalence independently reviewed; old runtime qualification is not retained.',
                 configurations=modes,single_option_delta=delta,
                 same_new_binary_required=True,old_S_is_cost_reference_only=True,
                 historical_cost=empirical,
                 estimated_wall_seconds_per_endpoint=predicted,
                 estimate_limitation='Before A2 host-RAM/geometry review; large-capacity ON can exceed empirical range. No speedup assumption.',
                 planning_timeout_seconds=10800,
                 planning_result_reservation_bytes_per_endpoint=384*2**20,
                 reservation_is_proposed_not_adopted=True,
                 outstanding=['A2 exact single-option name and common effective capacity vector',
                     'Formal new source/framework/vendor/archive/build/main identities',
                     'Affected production-driven native OFF/ON and input-reader applicability',
                     'Independent exact new profile qualification, parser and counter coverage',
                     'Final runtime_config/comparison/run_key hashes and original policy registration',
                     'Fresh full current trace hashes through original runner.inspect',
                     'Per-launch original resource/lease/result-budget admission'])
        write(out/'INPUT_PREPARATION.json',row);rows.append(row)
    report=dict(schema='E2_CAPACITY_FIVE_INPUT_PREPARATION_V1',prepared_unix=time.time(),
        status='FIVE_COMPLETE_INPUTS_PREPARED_NO_RUNTIME_QUALIFICATION_OR_START',
        approved_commit=AUTH,approved_pack=AUTH_REL,authority_files_sha256=source_files,
        registry_observed_actual_starts=registry['actual_starts'],registry_writes=0,
        native_runs=0,full_application_starts=0,main61_qualification_inherited=False,
        complete_trace_body_full_hash_reads=0,
        trace_body_sample_reads='First/last4096 bytes of each declared trace body only',
        ten_starts_planned=10,ten_unique_condition_ids=[r['condition_id'] for r in queue],
        final_run_keys='Not minted before new source/binary/config identity exists',
        proposed_result_reservations_bytes=10*384*2**20,
        collector_metadata_planning_reserve_bytes=64*2**20,
        proposed_total_additional_reservation_bytes=10*384*2**20+64*2**20,
        historical_sequential_S_seconds=sum(r['historical_cost']['wall_seconds'] for r in rows),
        pair_execution_priority=['convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M'],
        scheduling_note='Pair adjacent. At most existing global concurrency, and DWT single-worker if needed; publish every independently accepted pair immediately. No retries or replacement.',
        inputs=rows)
    write(P/'FIVE_INPUTS_PREPARATION.json',report)
    write(P/'CONDITION_TEMPLATE_INDEX.json',dict(status='NOT_A_CONTROLLER_QUEUE',conditions=queue))
    print(json.dumps(dict(status=report['status'],workloads=len(rows),templates=len(queue),actual_starts=registry['actual_starts'],new_starts=0,remaining_producer_fields='BLOCKED_A2_FORMAL_RELEASE_AND_E_INDEPENDENT_QUALIFICATION')))

if __name__=='__main__':main()
