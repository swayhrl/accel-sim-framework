"""Pure one-end scope controls; isolated candidate, no registry/process APIs.

Default denies synthetic manifests. Real integration must supply exact published
approval/release/Q/spec hashes and reviewed original Coordinator hooks.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

FIELD = 'detach_observer_diagnostic_batch'
CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
ACTIVE = {'RESERVED', 'RUNNING', 'START_INTENT_UNRECONCILED'}
SCI_SCOPE = 'DETACH_OBSERVER_DIAGNOSTIC_POINT_V1'
GIB = 2**30


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spec_sha(spec):
    return sha({k: v for k, v in spec.items() if k != 'input_audit'})


def old_seal(item):
    fields = ('campaign_id', 'authority_commit', 't0_unix', 'reservations',
              'full_system_matrix', 'final_source_identity', 'capacity_diagnostic_runtime',
              'capacity_diagnostic_matrix', 'capacity_diagnostic_amendment',
              'start_and_time_limit_removal', 'formal_simulator_concurrency',
              'workspace_disk_policy', 'additional_results_max_bytes',
              'old_plus_new_results_max_bytes', 'maximum_actual_starts',
              'start_deadline_unix', 'intake_deadline_unix', 'per_end_timeout_seconds')
    return dict(old50=sha(item['attempts'][:50]),
                old_workload=sha(item['workload_pipeline_batches']),
                immutable={k: sha(item.get(k)) for k in fields},
                records={g: {k: sha(v) for k, v in item.get(g, {}).items()}
                         for g in ('accepted_results', 'accepted_pairs', 'scientific_holds',
                                   'qualifications', 'input_selections')})


class Authority:
    """Hash-bound metadata only. Does not fetch, hash binaries or create processes."""
    def __init__(self, manifest_path, manifest_sha256, approval_path,
                 approval_sha256, *, fixture_mode=False):
        self.manifest_path = Path(manifest_path)
        self.manifest_sha256 = manifest_sha256
        self.approval_path = Path(approval_path)
        self.approval_sha256 = approval_sha256
        self.fixture_mode = fixture_mode

    def authority(self):
        require(file_sha(self.manifest_path) == self.manifest_sha256, 'manifest bytes changed')
        require(file_sha(self.approval_path) == self.approval_sha256, 'approval bytes changed')
        m = json.loads(self.manifest_path.read_text())
        a = json.loads(self.approval_path.read_text())
        require(m['schema'] == 'E2_EXACT_DETACH_OBSERVER_FINAL_MANIFEST_V1', 'manifest schema')
        require(a['schema'] == 'E2_EXACT_DETACH_OBSERVER_USER_APPROVAL_V1', 'approval schema')
        require(m['campaign_id'] == a['campaign_id'] == CAMPAIGN, 'campaign')
        require(m['maximum_new_actual_starts'] == a['maximum_new_actual_starts'] == 1,
                'one new start only')
        require(m['baseline_actual_starts'] == a['baseline_actual_starts'] == 50, 'old50 baseline')
        require(a['condition_id'] == m['condition_id'] and a['batch_id'] == m['batch_id'],
                'approval exact condition/batch')
        require(a['manifest_scientific_binding_sha256'] == sha(m['scientific_binding']),
                'approval scientific binding')
        if m.get('deployment_state') == 'SYNTHETIC_FIXTURE_NOT_DEPLOYABLE':
            require(self.fixture_mode and a.get('synthetic_fixture') is True,
                    'synthetic fixture cannot activate production')
        else:
            require(not self.fixture_mode and m.get('deployment_state') == 'E_SEALED_FORMAL_RELEASE',
                    'real E sealed manifest required')
            require(a.get('synthetic_fixture') is False, 'real approval required')
            require(bool(m.get('producer_publication_commit')) and
                    re.fullmatch('[0-9a-f]{40}', m['producer_publication_commit']),
                    'exact published producer required')
        binding = m['scientific_binding']
        source = binding['source_identity']
        for key in ('core_source_commit', 'framework_source_commit', 'vendor_pybind11_commit'):
            require(type(source.get(key)) is str and re.fullmatch('[0-9a-f]{40}', source[key]),
                    'exact source identity')
        for key in ('binary_sha256', 'archive_sha256'):
            require(type(source.get(key)) is str and re.fullmatch('[0-9a-f]{64}', source[key]),
                    'exact producer binary/archive')
        require(source['binary_sha256'] not in m['prohibited_old_binary_sha256'],
                'old binary excluded')
        require(binding['scientific_scope'] == SCI_SCOPE and m['pairs'] == [],
                'one diagnostic point never S/F pair')
        require(binding['trace_content_sha256'] ==
                '694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb',
                'exact SGEMM trace')
        require(binding['manifest_sha256'] ==
                '853369d8e256d57ff440b88cb31f9b7c5967f3e411eb84c32612021fa1ade6c3' and
                binding['ranges_sha256'] ==
                'be570e38e168b59252ac7f4ed041e2b606aed79ea0c9650e94c840f825767aa8',
                'exact C positive certificate')
        require(binding['profile'] == 'F' and binding['selection_id'] ==
                'D_EXP_SGEMM_MEDIUM_20261022_r1', 'exact F/input selection')
        return m

    def active(self, item):
        if FIELD not in item:
            require(len(item['attempts']) <= 50, 'unauthorized post50 tail')
            return False
        m = self.authority()
        row = item[FIELD]
        require(row['manifest_sha256'] == self.manifest_sha256 and
                row['approval_sha256'] == self.approval_sha256, 'adoption authority mismatch')
        require(item['campaign_id'] == CAMPAIGN and item['t0_unix'] == 1792414193,
                'original campaign/T0')
        require(len(item['attempts']) >= 50 and sha(item['attempts'][:50]) == m['old_seal']['old50'],
                'old50 prefix changed/refunded')
        require(sha(item['workload_pipeline_batches']) == m['old_seal']['old_workload'],
                'old workload batch changed')
        for key, digest in m['old_seal']['immutable'].items():
            require(sha(item.get(key)) == digest, 'old contract changed: ' + key)
        for group, records in m['old_seal']['records'].items():
            for key, digest in records.items():
                require(key in item.get(group, {}) and sha(item[group][key]) == digest,
                        'old scientific record changed: ' + group)
        require(set(item['accepted_pairs']) == set(m['old_seal']['records']['accepted_pairs']),
                'new S/F pair forbidden in one-end batch')
        require(set(item['input_selections']) == set(m['old_seal']['records']['input_selections']),
                'new input selection forbidden')
        allowed_q = set(m['old_seal']['records']['qualifications']) | {m['scientific_binding']['qualification']['sha256']}
        require(set(item['qualifications']) <= allowed_q, 'extra qualification outside one scope')
        tail = item['attempts'][50:]
        require(len(tail) <= 1, 'one reservation maximum/no retry')
        require(row['attempt_ids'] == [a['attempt_id'] for a in tail], 'tail accounting mismatch')
        require(len(set(row['attempt_ids'])) == len(tail), 'duplicate tail')
        binding = row.get('binding')
        if binding is not None:
            require(binding['spec_sha256'] == m['scientific_binding']['spec_sha256'],
                    'binding changed')
            require(binding['identity'] == m['scientific_binding']['identity'] and
                    binding['qualification_id'] == m['scientific_binding']['qualification']['sha256'],
                    'bound identity/Q changed')
        allowed_results = set(m['old_seal']['records']['accepted_results']) | {
            a['attempt_id'] for a in tail if a['state'] == 'COMPLETE_VALID'}
        require(set(item['accepted_results']) <= allowed_results, 'extra accepted endpoint')
        allowed_holds = set(m['old_seal']['records']['scientific_holds']) | {
            'qualification:'+m['scientific_binding']['qualification']['sha256']}
        require(set(item['scientific_holds']) <= allowed_holds, 'extra unrelated HOLD')
        witness = row.get('start_witness')
        require(witness is None or len(tail) == 1, 'start witness cannot lose charged attempt')
        for a in tail:
            require(binding is not None and a['diagnostic_spec_sha256'] == binding['spec_sha256'],
                    'unbound tail')
            require(a['condition_id'] == m['condition_id'] and a['budget_bucket'] == m['batch_id'],
                    'extra condition/bucket')
            require(a['identity'] == binding['identity'] and
                    a['run_key'] == sha(binding['identity']) and
                    a['qualification_id'] == binding['qualification_id'] and
                    a['scientific_scope'] == SCI_SCOPE, 'tail identity/scope changed')
            before_start = {'RESERVED', 'START_INTENT_UNRECONCILED', 'FAILED_SPAWN',
                            'CANCELLED_BEFORE_START'}
            after_start = {'RUNNING', 'COMPLETE_VALID', 'FAILED', 'RESOURCE_LIMIT', 'TIMEOUT', 'INCOMPLETE'}
            require(a['state'] in before_start | after_start, 'unknown tail state')
            retained_start = any(k in a for k in ('process', 'started_unix', 'started_identity', 'immutable_started_marker'))
            require(not retained_start or a['actual_start'] is True, 'retained process/start witness forbids refund')
            require(a['actual_start'] is (a['state'] in after_start), 'no actual-start refund')
            if a['actual_start']:
                expected_witness = dict(attempt_id=a['attempt_id'], run_key=a['run_key'],
                                        process=a.get('process'), started_unix=a.get('started_unix'))
                require(witness == expected_witness and a.get('started_identity') == a.get('process')
                        and a.get('immutable_started_marker') == sha(expected_witness),
                        'charged start witness/identity mismatch')
            else:
                require(witness is None, 'batch start witness forbids refund')
        require(item['actual_starts'] == sum(a.get('actual_start') is True for a in item['attempts']),
                'actual-start recount mismatch')
        return True

    def adopt(self, item, external_leases=()):
        m = self.authority()
        if FIELD in item:
            self.active(item)
            return False
        require(len(item['attempts']) == item['actual_starts'] == 50, 'exact completed50 required')
        require(item['controller']['state'] == 'STOPPED', 'original controller must STOP')
        require(not any(a['state'] in ACTIVE for a in item['attempts']) and
                not any(x['status'] in ACTIVE for x in external_leases), 'active/uncertain own work')
        require(old_seal(item) == m['old_seal'], 'adoption snapshot changed')
        item[FIELD] = dict(manifest_sha256=self.manifest_sha256,
                           approval_sha256=self.approval_sha256, binding=None, attempt_ids=[], start_witness=None)
        self.active(item)
        return True

    def bind(self, item, spec):
        require(self.active(item), 'no observer adoption')
        m = self.authority()
        require(not item[FIELD]['attempt_ids'], 'started binding immutable')
        self.check_spec(m, spec)
        qrow = item['qualifications'].get(spec['qualification_id'])
        require(qrow is not None and qrow['sha256'] == spec['qualification_id']
                and qrow['path'] == m['scientific_binding']['qualification']['path'],
                'new Q not registered')
        old = item[FIELD]['binding']
        binding = dict(spec_sha256=spec_sha(spec), identity=copy.deepcopy(spec['identity']),
                       qualification_id=spec['qualification_id'])
        require(old is None or old == binding, 'immutable spec binding')
        item[FIELD]['binding'] = binding
        return binding

    def check_spec(self, m, spec):
        b = m['scientific_binding']
        require(spec_sha(spec) == b['spec_sha256'], 'exact spec changed')
        require(spec['identity'] == b['identity'], 'exact identity changed')
        for k, v in dict(condition_id=m['condition_id'], budget_bucket=m['batch_id'],
                         profile='F', scientific_scope=SCI_SCOPE,
                         selection_id=b['selection_id']).items():
            require(spec.get(k) == v, 'wrong spec field: ' + k)
        require(not spec.get('retry_previous_attempt') and not spec.get('retry_reason'),
                'no implicit retry')
        require(spec['identity']['trace_content_sha256'] == b['trace_content_sha256'], 'input')
        require(all(spec['identity'][k] == b['source_identity'][k]
                    for k in ('core_source_commit', 'framework_source_commit', 'binary_sha256')),
                'source')
        require(spec['profile_semantics']['research_switches'] == dict.fromkeys(('W', 'V', 'T', 'M'), 1)
                and spec['identity']['feature_vector']['payload_capacity_per_slice'] == 1168
                and spec['identity']['feature_vector']['ops_per_bank_cycle'] == 1, 'profile semantics')
        qref = b['qualification']
        require(spec['qualification_id'] == qref['sha256'] and file_sha(qref['path']) == qref['sha256'],
                'new independent Q changed')
        q = json.loads(Path(qref['path']).read_text())
        require(q['status'] == 'INDEPENDENTLY_QUALIFIED' and
                q['source_identity'] == b['source_identity'] and
                q['scientific_scope'] == SCI_SCOPE and
                q['profile_semantics'] == spec['profile_semantics'], 'new Q scope/source/profile')
        require(file_sha(b['producer']['path']) == b['producer']['sha256'], 'producer changed')
        producer = json.loads(Path(b['producer']['path']).read_text())
        require(producer['source_identity'] == b['source_identity'], 'producer source mismatch')
        for ref in b['content_refs']:
            require(file_sha(ref['path']) == ref['sha256'], 'bound config/asset/schema changed')
        require(file_sha(spec['parser']['path']) == spec['parser']['sha256'] and
                spec['parser'] == b['parser'], 'parser changed')
        if self.fixture_mode:
            require(q.get('synthetic_fixture') is True and producer.get('synthetic_fixture') is True,
                    'fixture evidence explicitly synthetic')
        else:
            require(q.get('synthetic_fixture') is False and producer.get('synthetic_fixture') is False,
                    'synthetic Q/producer forbidden in production')

    def guard(self, item, spec):
        require(self.active(item), 'no adoption')
        m = self.authority()
        self.check_spec(m, spec)
        require(item[FIELD]['binding'] is not None and
                item[FIELD]['binding']['spec_sha256'] == spec_sha(spec), 'unbound condition')
        require('qualification:'+spec['qualification_id'] not in item.get('scientific_holds', {}),
                'new qualification HOLD')
        require(not item[FIELD]['attempt_ids'], 'one reservation consumed/no retry')
        return True

    def resource_guard(self, spec, resources):
        require(resources['workspace_free_bytes'] >= 7*GIB + spec['maximum_result_bytes'],
                'workspace5+2GiB guard')
        require(resources['share_free_bytes'] >= 40*GIB, 'Share guard')
        require(resources['available_memory_bytes'] >= 64*GIB + spec['memory_bytes'], 'RAM guard')
        require(resources['reserved_memory_bytes'] + spec['memory_bytes'] <= 32*GIB and
                resources['reserved_cpu_units'] + spec['cpu'] <= 8, 'CPU/RAM reservation guard')
        require(resources['new_bytes'] + spec['maximum_result_bytes'] <= 10*GIB and
                resources['total_bytes'] + spec['maximum_result_bytes'] <= 24*GIB,
                'cumulative generation guard')


