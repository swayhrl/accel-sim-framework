"""Complete final reader/input bindings only after actual independent E native.

Preparation draft: never run with producer-only/candidate evidence. No test,
compiler, controller, registry/CLIENT write, qualification registration or Git.
Required E assertion-review fields are documented in FINAL_BINDING_INTERFACE.md.
"""
from pathlib import Path
import argparse, copy, hashlib, json, subprocess

P=Path(__file__).resolve().parent
WORKS=('convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M')
SOURCE_KEYS=('core_source_commit','framework_source_commit','binary_sha256')
MARKERS=(
 'E_CAPACITY_HOST_PREFILL_FULL_ADDRESS_SCALED_INDEX_SECTORS_EPOCH_VERSION_ZERO PASS',
 'E_CAPACITY_HOST_PREFILL_DIRTY_REFUSAL_PRESERVES_IDENTITY_VERSION_OFFSET PASS',
 'E_CAPACITY_HOST_PREFILL_PENDING_RESPONSE_REFUSAL_REAL_RETURN_DRAIN_RETRY PASS')
ASSERTIONS=('new_default_and_explicit_OFF_equivalence',
 'new_ON_full_address_sector_version_zero','new_ON_dirty_pending_response_refusal',
 'new_ON_ownership_resource_drain','no_input_reader_opcode_change')

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
    require(isinstance(r,dict) and sha(r['path'])==r['sha256'],'evidence changed')
    return Path(r['path']).resolve(strict=True)
def write(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    require(not p.exists(),'never replace an old input binding')
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])

def complete(native_path,assertion_path,out):
    source_doc=read(P/'FINAL_SOURCE_IDENTITY_PENDING_E_NATIVE.json');source=source_doc['source_identity']
    portability=read(P/'FINAL_NEW_INPUT_SOURCE_PORTABILITY_PENDING_E_NATIVE.json')
    require(portability['source_identity']==source,'wrong final source review')
    checked(source_doc['main']);checked(source_doc['archive'])
    evidence=read(native_path);owner=read(assertion_path)
    require(evidence['status']=='NATIVE_EXPECTATIONS_MATCH_PENDING_SCIENTIFIC_QUALIFICATION','actual E native suite has not closed')
    require(evidence['lease_released'] is True and evidence['original_scientific_history_unchanged'] is True,'native lease/history did not close')
    require(evidence['source_identity']==source and evidence['actual_starts']==36 and evidence['full_applications_started']==0,'wrong E native runtime or scientific boundary')
    require(owner.get('schema')=='E2_FINAL_INPUT_ASSERTION_REVIEW_V1' and owner.get('status')=='PASS' and owner.get('reviewed_by') in ('E','E2'),'real root E input assertion review required')
    require(owner['source_identity']==source and all(owner['assertions'].get(k) is True for k in ASSERTIONS),'new input/native assertions incomplete')
    require(checked(owner['native_replay_result'])==Path(native_path).resolve(),'assertion review names another native suite')
    intake=read(checked(evidence['intake']));formal=intake['formal_producer']
    require(formal['formal_release_reviewed_by_E'] is True and intake['source_identity']==source,'formal source release not bound')
    release=checked(formal['release']);remote=read(checked(formal['remote_readback']))
    require(remote.get('remote_commit')==formal['commit'] and remote.get('verified_paths'),'formal producer remote readback absent')
    repo=Path(git(release.parent,'rev-parse','--show-toplevel').decode().strip())
    require(git(repo,'show',formal['commit']+':'+release.relative_to(repo).as_posix())==release.read_bytes(),'release differs from exact remote-verified committed bytes')
    cases={r['case_id']:r for r in evidence['cases']}
    ids=[owner['host_case_id'],*owner['off_case_ids']]
    require(len(set(owner['off_case_ids']))>=2,'actual separate new default and explicit-OFF E native cases required')
    for name in ids:
        case=cases[name];native=case['native_exit']
        require(case['kind']=='DIRECT_NATIVE_TEST_ELF' and case['status']=='EXPECTATIONS_MATCH','not direct successful native ELF evidence')
        require(case['binding']['source_identity']==source,'native case not bound to final runtime')
        require(case['binding']['executed_artifact']['source_identity']==source,'old OFF comparison cannot masquerade as new native input evidence')
        require(native['exit_code']==native['wait_status']==0 and native['stop_reason'] is None and native['released_to_native'] is True,'true native normal exit0 required')
        require(read(checked(case['native_exit_receipt']))==native,'native direct-parent exit evidence differs')
        require(native['native_process']==case['native_process'],'PID/start ticks/boot identity changed')
        checked(case['raw'])
        require(all(case['required_checks'].values()),'native assertion terminal missing')
    host=cases[owner['host_case_id']];raw=Path(host['raw']['path']).read_text(errors='replace')
    require(all(marker in raw for marker in MARKERS),'actual E ON host-prefill/refusal/version-zero assertions missing')
    out=Path(out).resolve();require(out.is_relative_to(P) and out!=P and not out.exists(),'new owned output child required')
    reviews={}
    for work in WORKS:
        partial_path=P/(work+'_FINAL_INPUT_PENDING_E_NATIVE.json');partial=read(partial_path)
        require(partial['source_identity']==source,'input partial is not for actual final runtime')
        for row in partial['source_trees']:
            actual=git(row['repository'],'rev-parse',row['new_commit']+':'+row['path']).decode().strip()
            require(actual==row['new']==row['old'],'input parser/opcode content changed')
        directory=out/work;scope_path=directory/'RETAINED_INPUT_SCOPE.json'
        atomic=partial['historical_atomic_input_scope'];checked(atomic)
        legacy=partial['historical_native_legacy_semantic_proof']
        if legacy:checked(legacy)
        scope=dict(status='UNCHANGED_COMPLETE_INPUT_PARSER_AND_CONTENT_SCOPE',
            new_source_identity={k:source[k] for k in SOURCE_KEYS},
            original_source_identity=partial['original_source_identity'],
            original_producer_publication=partial['original_producer_publication'],
            source_trees=partial['source_trees'],retained_atomic_report_sha256=[atomic['sha256']],
            retained_native_byte_proof_sha256=legacy['sha256'] if legacy else None,
            new_host_prefill_and_read_reference_tests_passed=True,
            new_input_assertion_review=ref(assertion_path),independent_E_native_replay=ref(native_path),
            static_source_review=ref(P/'FINAL_NEW_INPUT_SOURCE_PORTABILITY_PENDING_E_NATIVE.json'),
            input_only=True,main61_runtime_qualification_inherited=False)
        write(scope_path,scope)
        semantics_path=directory/'NATIVE_INPUT_SEMANTICS.json'
        write(semantics_path,dict(schema='E2_NEW_RUNTIME_INPUT_SEMANTICS_ONLY_V1',status='PASS',
            source_identity=source,workload=work,trace_content_sha256=partial['trace_content_sha256'],
            retained_complete_content_and_opcode_evidence=atomic,retained_input_scope=ref(scope_path),
            actual_new_E_input_assertion_review=ref(assertion_path),
            numerical_trace_payload_reconstruction_claim=False,production_runtime_qualification=False))
        admission=copy.deepcopy(partial['historical_input_scope_admission'])
        admission['retained_input_scope']=ref(scope_path)
        if admission.get('input_adapter_revision'):
            admission['input_adapter_revision'].pop('runtime_gates_source_binary_config_unchanged',None)
            admission['input_adapter_revision']['new_runtime_qualification_is_separate']=True
        assets=copy.deepcopy(partial['historical_auxiliary_assets'])
        for a in assets:
            if a['name']=='current_input_scope_binding.json':a['path']=str(scope_path)
            elif a['name']=='native_input_semantics.json':a['path']=str(semantics_path)
        review_path=directory/'NEW_INPUT_REVIEW.json'
        review=dict(schema='E2_FINAL_NEW_RUNTIME_INPUT_REVIEW_V1',status='PASS',reviewed_by='E2',
            source_identity=source,workload=work,trace_content_sha256=partial['trace_content_sha256'],
            new_runtime_reader_semantics_independently_reviewed=True,
            new_host_prefill_and_read_reference_tests_passed=True,
            input_scope_admission=admission,auxiliary_assets=assets,atomic_input_scope=atomic,
            static_source_portability=ref(partial_path),actual_E_native_replay=ref(native_path),
            independent_E_input_assertion_review=ref(assertion_path),
            scope='Exact complete input semantics only; full new runtime/config/resource qualification is separate',
            runtime_qualification_inherited=False)
        if legacy:review['native_legacy_semantic_proof']=legacy
        write(review_path,review);reviews[work]=ref(review_path)
    write(out/'INPUT_BINDING_INDEX.json',dict(schema='E2_FINAL_INPUT_BINDING_INDEX_V1',source_identity=source,
        actual_E_native_replay=ref(native_path),independent_E_input_assertion_review=ref(assertion_path),workloads=reviews))
    return dict(status='FIVE_INPUT_ONLY_BINDINGS_COMPLETE_NOT_RUNTIME_QUALIFICATION',index=ref(out/'INPUT_BINDING_INDEX.json'))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native-replay',type=Path,required=True)
    ap.add_argument('--assertion-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=P/'final_bindings')
    ap.add_argument('--complete-after-real-e-native',action='store_true',required=True)
    args=ap.parse_args();print(json.dumps(complete(args.native_replay,args.assertion_review,args.output)),flush=True)

if __name__=='__main__':main()
