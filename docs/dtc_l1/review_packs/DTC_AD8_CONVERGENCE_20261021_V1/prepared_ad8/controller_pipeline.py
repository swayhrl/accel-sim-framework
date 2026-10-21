"""Canonical controller's source-bound pipeline helpers; no independent CLI.

No UUIDs, budgets, admission pairs or model starts are created here. Root owns
those actions. Full original identity validation precedes R2; the final fork
window rechecks frozen stat identities plus root's exact loaded image binding.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

import ag7_strict
from ag7_runner import RuntimeSampler, collect_actual
import runtime_policy_b
import telemetry_receiver
import validate_identity as identity_validator
from guarded_process import run_guarded
from ownership import identity
from cpu_admission_v2 import NoOwnedChildren
from legacy_authority_runtime import bind_frozen_procedures

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
REPO = HERE.parents[4]
OLD = REPO / 'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution'
ROOT = Path('/workspace/dtc-ag8-ad-convergence-174-v1')
STAT_KEYS = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')


def require(value, message):
    if not value:
        raise ValueError(message)


def load(name, path, digest=None):
    raw = Path(path).read_bytes()
    if digest is not None:
        require(hashlib.sha256(raw).hexdigest() == digest, 'FROZEN_MODULE_CHANGED:' + str(path))
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, path))
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def signature(path):
    stat = Path(path).stat()
    return {key: getattr(stat, key) for key in STAT_KEYS}


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def stable_manifest(value):
    """Only newly recorded freeze clocks vary during current-file revalidation."""
    if isinstance(value, dict):
        return {key: stable_manifest(item) for key, item in value.items()
                if key not in ('frozen_monotonic_ns', 'frozen_unix_ns')}
    if isinstance(value, list):
        return [stable_manifest(item) for item in value]
    return value


class Pipeline:
    def __init__(self, registration, authority, publication):
        self.registration = registration
        self.authority = authority
        self.publication = publication
        self.identity = identity
        self.empty = NoOwnedChildren()
        self.resources = load('ag7_original_resources', OLD / 'prepared_ag6/resources_v2.py',
            'f1844de51555384a48227affe48d70bea09c98dc787269e5b43c43ea735f94f9')
        self.legacy_strict = load('ag7_original_strict', OLD / 'prepared_ag6/ag6_strict.py',
            '9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4')
        prior = sys.modules.get('ag6_strict')
        sys.modules['ag6_strict'] = self.legacy_strict
        try:
            self.legacy_close = load('ag7_original_close', OLD / 'prepared_ag6/close_attempt_v2.py',
                '4bac37f743c2f5818032b2062baff49bb8d5445398a3d6565d3618aeddf7ebc8')
        finally:
            if prior is None:
                sys.modules.pop('ag6_strict', None)
            else:
                sys.modules['ag6_strict'] = prior
        proc_reader, _, _ = bind_frozen_procedures()
        self.deps = dict(run_guarded=run_guarded, resource_module=self.resources,
            proc_reader=proc_reader, receiver_module=telemetry_receiver,
            runtime_module=runtime_policy_b)
        self.sampler = RuntimeSampler(authority, identity, self.resources, ROOT,
            registration['pilot_acceptance'])
        # Warm the exact reviewer imports before binding loaded images, without
        # sampling resources or invoking a launch/admission operation.
        self.sampler.reviews[id(self.empty)] = authority.bind_review(self.empty, peer_provider=lambda: [])
        self.image_helper = load('ag7_w1_image_helper', PACK / 'w1_cpu_entry.py')
        self.loaded_images = None
        self.own_instance = None
        self.frozen_stats = {}
        self.actual_identity = None
        self.manifests = None
        self.last_authority = None
        self.point_context = {}
        self.provenance_bytes = dict(
            old_preregistration=(OLD / 'AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json').read_bytes(),
            science_manifest=(OLD / 'ag6_final_prep_intake/AG6_FOUR_ARM_SCIENCE_PROPOSAL.json').read_bytes(),
            kernel_audit=(OLD / 'prepared_ag6/identity_metadata/KERNEL_BODY_AUDIT.tsv').read_bytes(),
            metric_dictionary=(OLD / 'ag6_final_prep_intake/FROZEN_METRIC_DICTIONARY.tsv').read_bytes())
        self.original_prereg = self.legacy_strict.json_bytes(self.provenance_bytes['old_preregistration'])

    def loaded_image_check(self):
        require(self.loaded_images is not None and self.own_instance is not None, 'ROOT_IMAGES_NOT_BOUND')
        require(self.image_helper.identity() == self.own_instance, 'ROOT_PID_START_TICKS_BOOT_CHANGED')
        require(self.image_helper.images() == self.loaded_images, 'ROOT_LOADED_IMAGE_CLOSURE_CHANGED')
        return True

    def _bind_stats(self):
        executable = json.loads((OLD / 'AG6_EXECUTABLE_PREREGISTRATION_V2.json').read_text())
        binding = executable['identity_contract']
        sources = json.loads(Path(binding['artifacts']['sources']['path']).read_text())
        traces = json.loads(Path(binding['artifacts']['input_stats']['path']).read_text())
        paths = set(self.registration['role']['source_sha256'])
        paths |= {str(Path(binding['source_roots'][row['repository']]) / row['path']) for row in sources}
        paths |= {str(REPO / row['path']) for row in sources if row['repository'] == 'Framework'}
        paths |= {str(REPO / 'gpu-simulator/ag7_policyb_progress.h'), str(identity_validator.EVIDENCE / 'build/accelsim_version.h')}
        paths |= {str(row['path']) for row in traces}
        paths |= {str(row['path']) for row in binding['artifacts'].values()}
        paths.add(str(binding['preregistration']['path']))
        for data in self.manifests.values():
            paths |= {str(row['path']) for row in data['files']}
        for point in self.actual_identity['points'].values():
            paths |= {str(row['path']) for row in point['config_copies']}
            paths.add(point['trace_list'])
        self.frozen_stats = {path: signature(path) for path in paths}

    def initial_gate(self):
        receipt, manifests, _objects = identity_validator.validate_all_identity(prepare_configs=False)
        require(receipt['status'] == 'PASS_CURRENT_AG7_STATIC_IDENTITY_BRIDGE_NOT_BA_ACCEPTANCE',
            'COMPLETE_CURRENT_IDENTITY_NOT_PASS')
        for name in ag7_strict.ORDER:
            self.legacy_strict.frozen_inputs(name, self.provenance_bytes['old_preregistration'],
                self.provenance_bytes['science_manifest'], self.provenance_bytes['kernel_audit'],
                self.provenance_bytes['metric_dictionary'])
        self.actual_identity, self.manifests = receipt, manifests
        self._bind_stats()
        self.own_instance = self.image_helper.identity()
        self.loaded_images = self.image_helper.images()
        self.sampler.current_controller_check = self.loaded_image_check
        return dict(receipt, controller_loaded_images=self.loaded_images,
            controller_instance=self.own_instance,
            final_window_stat_identities=len(self.frozen_stats),
            root_loaded_image_admission=True, source_only_current_mapping_not_fullsim_acceptance=True)

    def current_frozen_check(self, point):
        self.loaded_image_check()
        require(self.frozen_stats and all(signature(path) == expected
            for path, expected in self.frozen_stats.items()), 'CURRENT_SOURCE_RUNTIME_CONFIG_TRACE_STAT_CHANGED')
        require(self.actual_identity is not None and point['runtime_path'] in self.manifests,
            'CURRENT_VALIDATED_TARGET_NOT_REGISTERED')
        return True

    def prepare_point(self, spec, manifest_bytes, manifest_sha, publication_head):
        self.current_frozen_check(spec)
        actual = self.actual_identity['points'][spec['point']]
        expected_roi = canonical_sha({key: spec[key] for key in
            ('full_processing_window', 'expected_kernels', 'expected_instructions', 'expected_CTA', 'expected_commands')})
        env = dict(actual['validated_environment'], DTC_AG7_POLICY_B_PROGRESS='1',
            DTC_AG7_GENERATION='AD8_' + spec['attempt_uuid'],
            DTC_AG7_INPUT_SHA=spec['trace_list_sha256'], DTC_AG7_ROI_SHA=expected_roi)
        require(spec['runtime_environment'] == env, 'EXACT_REGISTERED_INPUT_ROI_GENERATION_FORMULAS_FAILED')
        ag7_strict.frozen_inputs(self.legacy_strict, spec['point'],
            registration=manifest_bytes, registration_sha256=manifest_sha,
            expected_framework_version=actual['expected_embedded_framework_version'],
            expected_base_decision_sha256=self.registration['comparator']['sha256'],
            **self.provenance_bytes)
        require(actual['runtime_path'] == spec['runtime_path'] and
            actual['runtime_sha256'] == spec['runtime_sha256'] and
            actual['options'] == spec['expected_full_effective_options'], 'ACTUAL_POINT_SCIENCE_RUNTIME_CHANGED')
        identity_receipt = dict(actual, current_identity_receipt=self.actual_identity,
            mapping_manifests=self.manifests, attempt_uuid=spec['attempt_uuid'])
        point = dict(spec, validated_argv=actual['validated_argv'], config_copies=actual['config_copies'],
            identity_receipt=identity_receipt, publication_head=publication_head,
            output_filesystem_device=os.stat(ROOT).st_dev)
        self.point_context[spec['point']] = dict(registration_bytes=manifest_bytes,
            registration_sha256=manifest_sha, identity_receipt=identity_receipt,
            publication_head=publication_head)
        return point, self.manifests

    def validate_root_image(self, point, pid, instance):
        before = identity(pid)
        require(before['start_ticks'] == instance['start_ticks'] and
            before['tracer_pid'] == os.getpid() and before['state'] != 'Z', 'ACTUAL_POSTFORK_INSTANCE_MISMATCH')
        require(os.readlink('/proc/' + str(pid) + '/exe') == point['runtime_path'], 'ACTUAL_ROOT_EXECUTABLE_CHANGED')
        require(signature(point['runtime_path']) == self.frozen_stats[point['runtime_path']],
            'ACTUAL_ROOT_ELF_FILE_IDENTITY_CHANGED')
        after = identity(pid)
        require(after['start_ticks'] == before['start_ticks'] and after['tracer_pid'] == os.getpid(),
            'ACTUAL_ROOT_CHANGED_DURING_BINDING')
        return True

    def finalize(self, **kwargs):
        point = kwargs['point']
        context = self.point_context[point['point']]
        def final_static():
            self.publication()
            self.loaded_image_check()
            receipt, manifests, _objects = identity_validator.validate_all_identity(prepare_configs=False)
            require(receipt['status'] == 'PASS_CURRENT_AG7_STATIC_IDENTITY_BRIDGE_NOT_BA_ACCEPTANCE' and
                stable_manifest(manifests) == stable_manifest(self.manifests) and receipt['points'][point['point']] ==
                self.actual_identity['points'][point['point']], 'FINAL_CURRENT_IDENTITY_SCOPE_CHANGED')
            return self.current_frozen_check(point)
        return collect_actual(**kwargs, sampler=self.sampler, legacy_close=self.legacy_close,
            legacy_strict=self.legacy_strict, strict_adapter=ag7_strict,
            provenance_bytes=self.provenance_bytes,
            expected_base_decision_sha256=self.registration['comparator']['sha256'],
            final_static_check=final_static, **context)
