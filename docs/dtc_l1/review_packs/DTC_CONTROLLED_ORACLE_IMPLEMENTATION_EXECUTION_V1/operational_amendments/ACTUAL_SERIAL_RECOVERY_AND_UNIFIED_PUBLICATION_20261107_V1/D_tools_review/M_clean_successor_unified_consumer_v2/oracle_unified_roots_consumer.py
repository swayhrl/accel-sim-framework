"""Read-only two-root adapter for the frozen Oracle consumer and analyzer.

No operational engine, owner guard or runtime module is imported or executed.
Only a private copy of S4182's fixed stage enumeration is changed.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import types

S_SHA = '4182a0464fe650a9beae17114065d75d5b9da42e7874486857838a70f0a15e54'
M_SHA = 'b5c3f4557e26f801ce1c27cb194bb74e62e963f76b3dc8753208ecbe856f2aff'
AUTH = '18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
REQUEST = 'DTC_ORACLE_REMAINING24_20261106_V1'
OLD_PIDS = (1498278, 438646)
PASS = 'PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE'
STAGE_OLD = " for stage in ('initial8','remaining24'):\n  root=P(base_root)/stage;p=root/'control/MATRIX.fixed.json'"
STAGE_NEW = " for stage,explicit_root in _EXPLICIT_STAGE_ROOTS:\n  root=P(explicit_root);p=root/'control/MATRIX.fixed.json'"

def need(x, message):
    if not x: raise ValueError(message)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())
def hashed(data): return hashlib.sha256(data).hexdigest()

def pin(ref, root=None):
    path=Path(ref['path'])
    if root is not None:
        need(path.resolve().is_relative_to(Path(root).resolve()), 'OPERATIONAL_REF_OUTSIDE_NEW_PRIVATE_ROOT')
    need(isinstance(ref.get('sha256'),str) and sha(path)==ref['sha256'], 'PIN_DRIFT:'+str(path))
    return path

def metadata_new_binding(root, plan, receipt, lease, engine_pins, expected_build, build):
    """Pure metadata consistency only: never a live-owner/registration grant."""
    root=str(Path(root).resolve())
    need(plan['preparation_phase']=='SCIENCE_FINAL_FROZEN' and plan['actual_execution_authorized'] is True,
         'NEW_ROOT_NOT_FINAL_SCIENCE_AUTHORIZED')
    need(plan['authority_commit']==AUTH and plan['request']==REQUEST and plan['stage']=='remaining24', 'NEW_SCOPE_MISMATCH')
    need(plan['expected_new_starts']==96 and plan['exact_input_count']==24 and plan['CH_budget']==0, 'ONLY_FROZEN_NEW96')
    need(str(Path(plan['execution_root']).resolve())==root, 'PLAN_EXECUTION_ROOT_MISMATCH')
    need(all(build.get(k)==v for k,v in expected_build.items()), 'NEW_ROOT_FIXED_SCIENCE_BUILD_CHANGED')
    pid,start=plan.get('parent_pid'),plan.get('parent_start_ticks')
    need(type(pid)is int and pid>0 and pid not in OLD_PIDS and type(start)is int and start>0, 'TRUTHFUL_NEW_PARENT_IDENTITY_REQUIRED')
    need(receipt.get('status')=='PASS_NEW_PRIVATE_CPU_LAYOUT_SOURCE_RESOURCE_QUALIFICATION', 'FINAL_BIND_RECEIPT_NOT_PASS')
    need(str(Path(receipt['root']).resolve())==root and receipt['parent_pid']==pid and receipt['parent_start_ticks']==start,
         'FINAL_BIND_ROOT_OR_PARENT_MISMATCH')
    need(receipt.get('source_scientific_projection_equal') is True, 'SCIENTIFIC_PROJECTION_NOT_PROVEN_EQUAL')
    need(lease['schema']=='DTC_ORACLE_CLEAN_MAIN_PRIVATE_LEASE_V1' and lease['request']==REQUEST and lease['budget']==96
         and lease['old32_new_starts']==0 and lease['pid']==pid and lease['start_ticks']==start, 'NEW_LEASE_METADATA_MISMATCH')
    need(lease.get('authority_commit')==AUTH and lease['guard_sha256']==plan['clean_owner_guard']['sha256'], 'NEW_LEASE_GUARD_BINDING')
    need(lease['controller']['path']==plan['parent_controller_path']
         and lease['controller']['sha256']==plan['parent_controller_sha256'], 'NEW_CONTROLLER_BINDING')
    need({x['role']for x in lease['locks']}=={'governance','owner','qualification','shared'} and len(lease['locks'])==4,
         'NEW_PRIVATE_LEASE_FOUR_ROLE_METADATA_REQUIRED')
    generation=plan.get('clean_operational_generation') or {}
    need(generation.get('kind')=='SERIAL_LEGAL_DTC_MAIN_SUCCESSOR' and generation.get('old32_new_starts')==0
         and (generation.get('no_same_PID_exec_continuation') is True or generation.get('same_PID_exec_or_legacy_frame_required') is False)
         and generation.get('same_PID_exec_or_legacy_frame_required') is not True
         and generation.get('no_same_PID_exec_continuation') is not False, 'OLD_SAME_PID_CONTEXT_NOT_ALLOWED')
    need(plan['RESULT_ENGINE_PIN']==plan['result_engine_pin'], 'AMBIGUOUS_RESULT_ENGINE_PIN')
    # This portable scientific result-engine pin is distinct from private ops.
    need(bool(engine_pins) and isinstance(engine_pins,dict), 'MISSING_SCIENTIFIC_RESULT_ENGINE_PIN')
    return {'status':'READONLY_NEW_PRIVATE_BINDING_SUPPORTED','execution_root':root,'parent_pid':pid,
        'parent_start_ticks':start,'request':REQUEST,'same_PID_or_old_frame_required':False,
        'live_owner_or_lock_reverification_performed':False,'scientific_registration_permission_granted':False}

def inspect_new_root(root, config):
    root=Path(root).resolve(); plan_path=root/'control/EXECUTION_PLAN.json'
    plan=read(plan_path)
    proof={'status':'NOT_READY','root':str(root),'plan_path':str(plan_path),'plan_sha256':sha(plan_path),
        'preparation_phase':plan.get('preparation_phase'),'actual_execution_authorized':plan.get('actual_execution_authorized'),
        'scientific_acceptance_granted_by_CPU_manifest':False}
    if plan.get('preparation_phase')!='SCIENCE_FINAL_FROZEN' or plan.get('actual_execution_authorized') is not True:
        proof['reason']='CPU_DRAFT_OR_UNAUTHORIZED_NEW_ROOT'; return proof
    try:
        build_path=root/'control/BUILD_PROFILE.json';build=read(build_path)
        need(sha(build_path)==plan['build_profile_sha256'],'BUILD_PROFILE_PIN_DRIFT')
        receipt_path=root/'control'/config['final_bind_receipt_name'];receipt=read(receipt_path)
        need(str(Path(receipt['plan']['path']).resolve())==str(plan_path), 'FINAL_RECEIPT_PLAN_PATH')
        need(receipt['plan']['sha256']==sha(plan_path),'FINAL_RECEIPT_PLAN_SHA')
        pin(receipt['candidate'],root)
        matrix_path=root/'control/MATRIX.fixed.json'
        need(sha(matrix_path)==config['matrix_fixed_sha256'],'NEW_MATRIX_CONTENT_CHANGED')
        points=read(matrix_path)['points']; expected=config['expected_plan_rows']
        need(len(points)==96 and len({p['plan_id']for p in points})==96 and
             {p['plan_id']for p in points}==set(expected),'NEW_ROOT_MUST_BIND_EXACT96_SLOTS')
        need(all(all(p[k]==expected[p['plan_id']][k]for k in ('program','suite','input_digest','mode'))for p in points),
             'NEW_MATRIX_FROZEN_INPUT_OR_MODE_CHANGED')
        need(len(plan['authorized_cohorts'])==96 and set(plan['authorized_cohorts'])=={p['cohort']for p in points},
             'NEW_COHORT_SCOPE_CHANGED')
        pins=plan['source_pins'];need(isinstance(pins,list)and pins,'MISSING_NEW_SOURCE_PINS')
        verified={}
        external_allowed={(str(Path(ref['path']).resolve()),ref['sha256'])for ref in config.get('allowed_external_source_pins',[])}
        external_verified=[]
        for ref in pins:
            path=Path(ref['path']).resolve()
            if path.is_relative_to(root):
                pin(ref,root)
            else:
                need((str(path),ref.get('sha256'))in external_allowed,'UNDECLARED_EXTERNAL_SOURCE_PIN:'+str(path))
                pin(ref);external_verified.append(copy.deepcopy(ref))
            need(str(path)not in verified,'DUPLICATE_NEW_SOURCE_PIN');verified[str(path)]=ref['sha256']
        guard=pin(plan['clean_owner_guard'],root);lease_path=pin(plan['clean_owner_lease'],root)
        controller=Path(plan['parent_controller_path']).resolve()
        need(controller.is_relative_to(root),'PRIVATE_CONTROLLER_OUTSIDE_NEW_ROOT')
        engine=root/'tools'/config['private_operational_engine_name']
        for path,value in [(guard.resolve(),plan['clean_owner_guard']['sha256']),
                           (controller,plan['parent_controller_sha256']),(engine.resolve(),sha(engine))]:
            need(verified.get(str(path))==value,'PRIVATE_OPERATIONAL_SOURCE_NOT_IN_PLAN_PINS:'+str(path))
        result_engine_path=pin(plan['RESULT_ENGINE_PIN'],root)
        lease=read(lease_path)
        pure=metadata_new_binding(root,plan,receipt,lease,read(result_engine_path),config['expected_build_identity'],build)
        proof.update(pure,ready=True,final_bind_receipt_path=str(receipt_path),final_bind_receipt_sha256=sha(receipt_path),
            lease_path=str(lease_path),lease_sha256=sha(lease_path),guard_path=str(guard),guard_sha256=sha(guard),
            private_operational_engine_path=str(engine),private_operational_engine_sha256=sha(engine),
            source_pin_count=len(verified),source_pins=copy.deepcopy(pins),external_source_pins=external_verified,scientific_result_engine_pin=copy.deepcopy(plan['RESULT_ENGINE_PIN']))
    except (ValueError,KeyError,OSError,TypeError)as error:
        proof.update(ready=False,reason='NEW_OPERATIONAL_BINDING_HOLD:'+str(error))
    return proof

def load_source_module(ref, expected_sha, name):
    path=pin(ref);need(sha(path)==expected_sha,'CANONICAL_SOURCE_SHA_CHANGED')
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module

def snapshot_once(bindings_path, out_dir, *, analyze=True):
    """One caller-driven refresh. Writes only caller-selected derived directory."""
    cfg=read(bindings_path); matrix_path=pin(cfg['fixed_matrix']); settings=read(pin(cfg['science_settings']))
    need(cfg['authority_commit']==AUTH,'WRONG_BINDING_AUTHORITY')
    legacy=cfg['initial8_data_only']; old_root=Path(legacy['root']).resolve()
    new=cfg['remaining24_private'];new_root=Path(new['root']).resolve()
    need(old_root!=new_root,'TWO_DISTINCT_STAGE_ROOTS_REQUIRED')
    old_snapshot_path=pin(legacy['snapshot']);pin(legacy['manifest']);pin(legacy['independent_data_review'])
    old_snapshot=read(old_snapshot_path);old_rows={r['plan_id']:r for r in old_snapshot['rows']if r.get('classification')=='accepted'}
    need(len(old_rows)==32 and all(r['initial_fixed8'] for r in old_rows.values()),'LEGACY_FROZEN_INITIAL32_ONLY')
    for row in old_rows.values():
        need(all(row.get(k)==v for k,v in settings['expected_build_identity'].items()),'LEGACY_FIXED_BUILD_CHANGED')
    source=pin(cfg['S_source']);need(sha(source)==S_SHA,'CANONICAL_S4182_SHA_CHANGED')
    text=source.read_text();need(text.count(STAGE_OLD)==1,'S_STAGE_ENUMERATION_ANCHOR_CHANGED')
    adapted=text.replace(STAGE_OLD,STAGE_NEW)
    mod=types.ModuleType('private_readonly_S4182_explicit_stage_roots');mod.__file__=str(source)
    exec(compile(adapted,str(source)+'#explicit-roots','exec'),mod.__dict__)
    mod._EXPLICIT_STAGE_ROOTS=(('initial8',str(old_root)),('remaining24',str(new_root)))
    new_config={**new,'expected_build_identity':settings['expected_build_identity'],
        'expected_plan_rows':{p['plan_id']:p for p in read(matrix_path)['rows']if not p['initial_fixed8']}}
    new_proof=inspect_new_root(new_root,new_config)
    original_accept=mod.accept_closed
    def accept_bound(root,point,result,result_path,derived):
        actual=Path(root).resolve()
        if actual==old_root:
            row=old_rows.get(point['plan_id']);need(row is not None,'NONLEGACY_SLOT_IN_OLD_DATA_ROOT')
            need(sha(result_path)==row['result_sha256'] and result['uuid']==row['uuid'] and result['cycles']==row['cycles'],
                 'IMMUTABLE_LEGACY_RESULT_CHANGED')
            need(all(result[k]==point[k] for k in ('program','input_digest','plan_id')),'LEGACY_PLAN_IDENTITY_CHANGED')
            need(result['oracle_mode']==point['mode']==row['mode'] and result['state']==PASS,'LEGACY_MODE_OR_STATUS_CHANGED')
            cache_source=Path(row['kernel_evidence_path']);need(sha(cache_source)==row['kernel_evidence_sha256'],'LEGACY_KERNEL_CACHE_PIN_DRIFT')
            facts=mod.read_gz(cache_source)
            cache=derived/('KERNEL_FACTS.'+row['result_sha256']+'.json.gz')
            if not cache.exists():cache.write_bytes(cache_source.read_bytes())
            need(sha(cache)==row['kernel_evidence_sha256'],'LEGACY_DERIVED_CACHE_DIFFERENT')
            detail={k:copy.deepcopy(row[k])for k in ('spec_path','spec_sha256','execution_plan_path','execution_plan_sha256',
                'core_commit','framework_commit','binary_sha256','libcudart_sha256','configuration_file_pins',
                'non_oracle_options_sha256','native_strict_path','native_strict_sha256','archive_receipt','actual_mechanism_exposure',
                'terminal_metrics_as_printed','traffic_as_printed','latency_counters_as_printed')}
            detail.update(kernel_evidence_path=str(cache),kernel_evidence_sha256=sha(cache),kernel_records=facts['records'],
                operational_stage_role='FROZEN_INITIAL8_DATA_ONLY_NO_OLD_OWNER_CONTEXT',
                legacy_independent_data_review=copy.deepcopy(legacy['independent_data_review']))
            return detail
        need(actual==new_root,'UNDECLARED_STAGE_ROOT')
        need(new_proof.get('ready')is True,new_proof.get('reason','NEW_BINDING_NOT_READY'))
        need(sha(new_root/'control/EXECUTION_PLAN.json')==new_proof['plan_sha256'],'NEW_PLAN_CHANGED_DURING_SNAPSHOT')
        build=settings['expected_build_identity'];need(all(result['proof'].get(k)==v for k,v in build.items()if k!='libcudart_sha256'),
            'NEW_RESULT_FIXED_SOURCE_OR_BINARY_CHANGED')
        detail=original_accept(root,point,result,result_path,derived)
        need(all(detail[k]==v for k,v in build.items()),'NEW_ACCEPTED_SCIENCE_BUILD_CHANGED')
        need([p['sha256']for p in detail['configuration_file_pins']]==settings['expected_configs_by_mode'][point['mode']],
             'NEW_SCIENCE_CONFIG_VECTOR_CHANGED')
        detail.update(operational_stage_role='NEW_PRIVATE_SERIAL_SUCCESSOR',new_operational_binding=copy.deepcopy(new_proof))
        return detail
    mod.accept_closed=accept_bound
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    report=mod.snapshot('UNUSED_EXPLICIT_ROOT_MAP',matrix_path,out)
    report['explicit_stage_bindings']={'initial8':{'root':str(old_root),'role':'FROZEN_DATA_ONLY','snapshot_sha256':legacy['snapshot']['sha256'],
        'independent_data_review':legacy['independent_data_review']},'remaining24':new_proof}
    report['readonly_adapter_provenance']={'S_source_sha256':S_SHA,'private_transformation':'ONLY_EXPLICIT_STAGE_ENUMERATION_PLUS_ACCEPT_WRAPPER',
        'private_transformed_source_sha256':hashed(adapted.encode()),'bindings_path':str(bindings_path),'bindings_sha256':sha(bindings_path),
        'operational_engines_or_guards_imported':False,'owner_or_tracer_actions':0,'registration_or_model_starts':0,
        'archive_or_restore_writes':0,'legacy_raw_reads':0,'CPU_receipt_is_scientific_acceptance':False}
    mod.put(out/'ORACLE_LIVE_RESULTS.json',report)
    if analyze:
        analyzer=load_source_module(cfg['M_analyzer'],M_SHA,'frozen_M_b5c_readonly')
        facts={r['plan_id']:mod.read_gz(r['kernel_evidence_path'])for r in report['rows']if r.get('classification')=='accepted'}
        c1=read(pin(cfg['C1_context']))if cfg.get('C1_context')else None
        derived=analyzer.analyze(report,read(matrix_path),facts,matrix_sha256=sha(matrix_path),snapshot_sha256=sha(out/'ORACLE_LIVE_RESULTS.json'),
            expected_build_identity=settings['expected_build_identity'],expected_configs_by_mode=settings['expected_configs_by_mode'],c1_context=c1)
        mod.put(out/'UNIFIED_CORE32_OPPORTUNITY_ANALYSIS.json.gz',derived,True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bindings',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();r=snapshot_once(a.bindings,a.out)
    print(json.dumps({'closed':r['closed_result_count'],'statuses':r['status_counts'],'new_root_binding':r['explicit_stage_bindings']['remaining24']['status'],
        'scientific_starts':0,'owner_or_tracer_actions':0,'source_generation':'EXPLICIT_TWO_ROOT_DATA_ONLY'}))
