"""Inactive future-BPF policy primitives. No installer, registry writes or launches.

This is NOT a qualified native/strict V3 implementation. It defines scope and
terminal semantics for a later explicitly qualified producer/consumer generation.
Existing exact4 engineering trials always retain their immutable V2 route.
"""
import copy
import hashlib
import json
from pathlib import Path

ID = 'DTC_STRACE_FUTURE_PRIMARY_IR_POLICY_V3_CANDIDATE'
ROOT = Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
EXCLUSION = A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json'
EXCLUSION_SHA = '4d7e1d1990771d8dc8bc1a9afe6ea85b9dae0f8752e951332742664a28dd0aa7'
IR_PLAN = A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json'
IR_PLAN_SHA = '72ce5472b5d3fc76d4f8d27c3aa3f4f7ad3d224a5ada3eaba88b3f1a2e6feff5'
V2_CONSUMER_SHA = '5c4ded4df0dee860015208b0af46d967e91a0bb2a2fc98e6830ed7b54db6ae9f'
CORE = '9eedb3131937748f0492fa83aad37d3691118d70'
FRAMEWORK = '02775fd795cde5aae1480d81cee6eb481d0a08f4'
BINARY = '02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
ROLE_IR = 'INCIDENT_RECOVERY_PERFORMANCE_TRIAL'
PASS = 'PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'
SCIENCE_KEYS = ('binary_sha256','cell','configs','core_commit','correctness_validation_only',
 'downstream_profile','execution_mnt_namespace','expected','expected_options','framework_commit',
 'input_binding_path','input_binding_sha256','input_digest','native_simulator_argv',
 'original_environment','performance_scope','profile','project','request','runtime_files','schema',
 'source_kind','source_worktrees','suite','workload','program')

class PolicyHold(RuntimeError):
    pass

def require(value, reason):
    if not value:
        raise PolicyHold(reason)

def read(path):
    return json.loads(Path(path).read_bytes())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def compact_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def science_sha(spec):
    return compact_sha({key: spec[key] for key in SCIENCE_KEYS})

def objsha(value):
    return hashlib.sha256((json.dumps(value, sort_keys=True, indent=2)+'\n').encode()).hexdigest()

def pinned_contracts():
    require(sha(EXCLUSION) == EXCLUSION_SHA, 'ENGINEER_CONTRACT_DRIFT')
    require(sha(IR_PLAN) == IR_PLAN_SHA, 'IR_PLAN_DRIFT_REQUIRES_NEW_POLICY_GENERATION')
    return read(EXCLUSION), read(IR_PLAN)

def classify_registered(cohort, spec, canonical_sha, q, matrix, frozen_scope,
                        memory_config, exclusion, ir_plan, frozen_bindings,
                        stage='ADMISSION'):
    """Pure classification; this NEVER grants permission to run.

    Call only outside any authority-write lock. A production reader must obtain
    current q and canonical files through the ratified source-bound native API.
    Future registered primary combinations are drawn from MATRIX, never a list
    copied from today's 15 pending cells or from all q globally.
    """
    require(stage in ('ADMISSION', 'TERMINAL'), 'UNKNOWN_STAGE')
    require(spec['cohort'] == cohort and spec['request'] == q['request'], 'IDENTITY')
    require(q['admitted_specs'].get(cohort) == canonical_sha, 'NOT_CURRENT_ADMITTED_SPEC')
    require(spec['host_cpu'] is None, 'CANONICAL_CPU_MUST_BE_NONE')
    require(cohort in memory_config['allowed_cohorts'], 'OFFICIAL_MEMORY_APPEND_REQUIRED')
    if stage == 'ADMISSION':
        require(cohort not in q['consumed'] and cohort not in q.get('sealed', []), 'SPENT_OR_SEALED')
    else:
        require(cohort in q['consumed'], 'TERMINAL_IDENTITY_NOT_CONSUMED')
    require(spec['core_commit'] == CORE and spec['framework_commit'] == FRAMEWORK
            and spec['binary_sha256'] == BINARY, 'FROZEN_BUILD_CHANGED')
    require(len(spec['expected_options']) == 270, 'INCOMPLETE_OPTIONS')
    frozen = frozen_bindings[spec['input_digest']]
    require(spec['input_binding_sha256'] == frozen['input_binding_sha256']
            and spec['expected'] == frozen['expected'], 'FROZEN_TRACE_BINDING_OR_COUNTS_CHANGED')
    require(spec['correctness_validation_only'] is False, 'CORRECTNESS_ONLY_NOT_PERFORMANCE')
    require(set(spec['expected']) >= {'CTA', 'instructions', 'kernels'}, 'MISSING_FROZEN_COUNTS')
    require(all(type(spec['expected'][k]) is int and spec['expected'][k] > 0
                for k in ('CTA', 'instructions', 'kernels')), 'INVALID_FROZEN_COUNTS')
    if cohort in exclusion['scope_cohorts']:
        return {'route':'EXACT_DELEGATE_V2_ENGINEERING', 'cohort':cohort,
                'mode':exclusion['scope_cohorts'][cohort]['mode'],
                'reference_cycles_equality_required':True, 'production_permission':False}
    points = [p for p in matrix['points'] if p['cohort'] == cohort]
    frozen_inputs = {p['input_digest'] for p in frozen_scope['points']}
    require(spec['input_digest'] in frozen_inputs, 'NOT_FROZEN_35_INPUT')
    role = spec.get('scientific_role')
    if points:
        require(len(points) == 1 and role in (None, 'PRIMARY_PERFORMANCE'), 'AMBIGUOUS_PRIMARY_ROLE')
        require(not any(r['new_cohort'] == cohort for r in ir_plan['rows']), 'IR_IN_PRIMARY_MATRIX')
        point = points[0]
        for key in ('input_digest','program','suite','cell','profile'):
            require(point[key] == spec[key], 'MATRIX_SCIENCE_MISMATCH_'+key)
        result_role, excluded = 'PRIMARY_PERFORMANCE', False
    else:
        require(role == ROLE_IR, 'UNKNOWN_NONPRIMARY_EXACT_OLD_DELEGATE')
        rows = [r for r in ir_plan['rows'] if r['new_cohort'] == cohort]
        require(len(rows) == 1, 'IR_NOT_IN_FROZEN_ONE_TO_ONE_PLAN')
        row = rows[0]
        require(science_sha(spec) == row['science_projection_sha256'], 'IR_SCIENCE_PROJECTION_CHANGED')
        lineage = spec['incident_recovery_trial_lineage']
        for key in ('original_cohort','original_uuid','original_negative_RESULT_sha256',
                    'original_DONE_sha256','science_projection_sha256'):
            require(lineage[key] == row[key], 'IR_LINEAGE_'+key)
        require(lineage['incident_id'] == ir_plan['incident_id'], 'IR_INCIDENT')
        require(lineage['primary_statistics_excluded'] is True and
                lineage['validated_union_authorized'] is False and
                lineage['reuse_old_UUID'] is False and lineage['refunds'] == 0,
                'IR_MUST_REMAIN_SEPARATE')
        records = [r for r in q.get('authorized_incident_recovery_trials', [])
                   if r['cohort'] == cohort]
        require(len(records) == 1, 'OFFICIAL_IR_REGISTRATION_REQUIRED')
        auth = records[0]
        require(auth['role'] == ROLE_IR and auth['incident_id'] == ir_plan['incident_id']
                and auth['recovery_plan_sha256'] == IR_PLAN_SHA, 'IR_AUTHORITY_LINEAGE')
        for key in ('original_cohort','original_uuid','science_projection_sha256',
                    'original_negative_RESULT_sha256','original_DONE_sha256'):
            require(auth[key] == row[key], 'IR_AUTHORITY_'+key)
        require(auth['primary_statistics_excluded'] is True and
                auth['validated_union_authorized'] is False, 'IR_AUTHORITY_UNION_FORBIDDEN')
        result_role, excluded = ROLE_IR, True
    return dict(route='V3_FUTURE_BPF_CANDIDATE', cohort=cohort, mode='BPF_REQUIRED',
        scientific_role=result_role, input_digest=spec['input_digest'],
        current_canonical_sha256=canonical_sha, science_projection_sha256=science_sha(spec),
        expected_options=copy.deepcopy(spec['expected_options']), expected=copy.deepcopy(spec['expected']),
        primary_statistics_excluded=excluded, validated_union_authorized=False,
        reference_cycles_equality_required=False, production_permission=False)

def canary4_release_eligibility(frame, main):
    """Only actual immutable V2 route + complete real replay may qualify release.

    Never accepts a CPU qualification receipt or a supplied PASS boolean. Missing
    real exact4 RESULT short-circuits to NOT_ELIGIBLE. No simulated positive
    production-release fixture exists in this package.
    """
    try:
        exclusion, _ = pinned_contracts()
        marker = main.DTC_STRACE_BPF_PRIVATE_CONSUMER_V2
        require(marker['frame'] is frame and marker['consumer'] is frame.f_locals['consumer'], 'WRONG_OWNER_CONSUMER')
        require(marker['consumer'].safe_finish is marker['wrapper'], 'PRIVATE_SAFE_ROUTE_CHANGED')
        require(marker['source_sha256'] == V2_CONSUMER_SHA, 'UNQUALIFIED_V2_CONSUMER')
        require(not marker['cfg']['qualification_only'] and Path(marker['cfg']['root']) == ROOT, 'CPU_FIXTURE_NOT_RELEASE')
        replay = marker['bridge']['readonly_replay']
        require(sha(replay.__code__.co_filename) == V2_CONSUMER_SHA, 'REPLAY_SOURCE_DRIFT')
        paths = {c: ROOT/'analysis'/(c+'.RESULT.json') for c in exclusion['scope_cohorts']}
        require(all(p.exists() for p in paths.values()), 'REAL_EXACT4_ACCEPTED_RESULTS_MISSING')
        receipts = []
        for cohort, rule in exclusion['scope_cohorts'].items():
            value = replay(cohort)  # original strict+CPU2+IO+new strict+full native archive replay
            require(value == read(paths[cohort]) and value['state'] == PASS, 'V2_REAL_REPLAY_NOT_ACCEPTED')
            proof = value['proof']; extra = proof['additional_strace_bpf_observation_strict']
            require(proof['performance_accepted'] is True and value['cycles'] == proof['cycles'] == rule['reference_cycles'], 'ENGINEER_REFERENCE_CYCLES')
            require(extra['mode'] == rule['mode'] and extra['engineering_reference']['same_physics_counts_and_cycles'] is True, 'ENGINEER_MODE_OR_COUNTS')
            require(value['archive']['additional_strace_bpf_archive_verification']['status'] == 'PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED', 'REAL_ARCHIVE_NOT_VERIFIED')
            receipts.append(dict(cohort=cohort, mode=rule['mode'], RESULT_sha256=sha(paths[cohort]),
                                 uuid=proof['uuid'], cycles=proof['cycles'],
                                 counts={k:proof[k] for k in ('CTA','instructions','kernel_count')}))
        return dict(status='REAL_CANARY4_RELEASE_PREREQUISITE_VERIFIED', receipts=receipts,
                    production_permission=False, requires_qualified_V3_native_and_consumer=True)
    except Exception as error:
        return dict(status='NOT_ELIGIBLE_NOT_INSTALLED', production_permission=False,
                    reason=repr(error), accepted_cycles=None)

def check_terminal_semantics(policy, spec, proof, done, native_exit, execution_receipt,
                             activation, archive_verification):
    """Semantic predicate over outputs from the future qualified V3 readers.

    This does not independently authenticate paths, snapshots or archive bytes;
    it cannot substitute for native producer/3bindings/raw activation/consumer.
    In particular it has no installer and never returns production_permission.
    """
    require(policy['route'] == 'V3_FUTURE_BPF_CANDIDATE', 'ENGINEERING_MUST_DELEGATE_V2')
    require(proof['cohort'] == policy['cohort'] == spec['cohort'], 'TERMINAL_COHORT')
    require(science_sha(spec) == policy['science_projection_sha256'], 'TERMINAL_SCIENCE_CHANGED')
    require(proof['performance_accepted'] is True and type(proof['cycles']) is int and proof['cycles'] > 0, 'ORIGINAL_PERFORMANCE_STRICT')
    require(proof['additional_cpu_spare_memory_admission_strict']['status'] == 'PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE', 'CPU2_STRICT')
    require('additional_shared_json_io_strict' in proof or 'additional_future_memory_io_strict' in proof, 'IO_STRICT')
    for key in ('input_digest','core_commit','framework_commit','binary_sha256','cell','profile'):
        require(proof[key] == spec[key], 'TERMINAL_IDENTITY_'+key)
    require(proof['effective_options'] == spec['expected_options'] == policy['expected_options']
            and len(proof['effective_options']) == 270, 'ALL_ACTUAL_270_OPTIONS')
    for actual, frozen in (('CTA','CTA'),('instructions','instructions'),('kernel_count','kernels')):
        require(proof[actual] == spec['expected'][frozen] == policy['expected'][frozen], 'FULL_CAPTURE_COUNTS_'+actual)
    require(done == native_exit == execution_receipt, 'NATURAL_CLOSURE_JOIN')
    require(done['cohort'] == spec['cohort'] and done['uuid'] == proof['uuid'] and
            done['stop_reason'] is None and done['launcher_wait_returncode'] == 0, 'NATURAL_SUCCESS_REQUIRED')
    require(activation['status'] == 'PASS_BPF_REQUIRED_ACTIVE' and activation['fallback_accepted'] is False
            and activation['baseline_Seccomp'] == activation['baseline_filters'] == 0
            and activation['model_Seccomp'] == 2 and activation['model_filters'] == 1, 'ACTIVATION_REQUIRED_NO_FALLBACK')
    require(archive_verification['status'] == 'PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED'
            and archive_verification['cohort'] == spec['cohort']
            and archive_verification['uuid'] == proof['uuid']
            and archive_verification['original_full_archive_verifier_required'] is True, 'FULL_ORIGINAL_AND_NEW_ARCHIVE')
    return dict(status='PASS_CPU_POLICY_SEMANTICS_NOT_RUNTIME_QUALIFICATION', cohort=spec['cohort'],
        cycles=proof['cycles'], reference_cycles_equality_checked=False,
        primary_statistics_excluded=policy['primary_statistics_excluded'],
        validated_union_authorized=False, production_permission=False)

def deployment_status():
    return dict(status='NOT_ELIGIBLE_NOT_INSTALLED', production_permission=False,
        reason='Candidate primitives only: real exact4 receipts and qualified V3 producer, binding, strict/consumer, scope and owner integration required.',
        models_started=0, grants_added=0, primary_statistics_union_authorized=False)
