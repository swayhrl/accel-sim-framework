"""Hostile evidence and concurrent ownership tests. Harness coverage, not Core qualification."""
from copy import deepcopy
import json
import multiprocessing
from pathlib import Path
import socket
import tempfile
import unittest

from registry import Registry, run_key, process_identity
from validate import InvalidEvidence, validate_events, validate_summary, reference_requests
from run import asset_manifest, content_hash, inspect, digest, GATES, validate_trace_closure


def identity():
    return {'core_source_commit': '1' * 40, 'framework_source_commit': '2' * 40,
            'binary_sha256': '3' * 64, 'runtime_config_sha256': '4' * 64,
            'trace_content_sha256': '5' * 64, 'workload': 'sad',
            'epoch_range': {'scope': 'full_application', 'selection': 'all'},
            'feature_vector': {'finite_wbuf': True, 'unified_wb': False, 'tvd': False,
                'ro': False, 'adaptive_policy': False, 'wbuf_entries': 16,
                'payload_capacity_per_slice': 1168, 'bank_count': 4, 'ops_per_bank_cycle': 1},
            'ideal_vector': {'wb': False, 'meta': False, 'read_hit': False},
            'termination_contract': {'kind': 'full_application_hardware_drained', 'residents_may_remain': True}}


def claim_worker(root, queue):
    try:
        result = Registry(root).claim(identity(), 'lane5', '/unused/test-only',
            resources={'available_memory_bytes': 2**50, 'disk_free_bytes': 2**50})
        queue.put(('OK', result[0], result[1]['lease_id']))
    except Exception as error:
        queue.put(('ERROR', str(error)))


class KeyTests(unittest.TestCase):
    def test_json_order_does_not_change_key(self):
        row = identity()
        self.assertEqual(run_key(row), run_key(dict(reversed(list(row.items())))))

    def test_every_identity_dimension_changes_key(self):
        base = identity()
        for name in base:
            row = deepcopy(base)
            if name.endswith('_commit'):
                row[name] = 'a' * 40
            elif name.endswith('_sha256'):
                row[name] = 'b' * 64
            elif name == 'workload':
                row[name] = 'scan'
            else:
                row[name]['additional_identity_dimension'] = True
            with self.subTest(name=name):
                self.assertNotEqual(run_key(base), run_key(row))

    def test_missing_identity_is_not_defaulted(self):
        for key in identity():
            row = identity()
            del row[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                run_key(row)

    def test_path_and_owner_are_not_identity_dimensions(self):
        row = identity()
        row['owner'] = 'lane4'
        with self.assertRaises(ValueError):
            run_key(row)

    def test_complete_asset_content_including_order(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / 'a').write_text('first')
            (p / 'b').write_text('second')
            assets = [{'name': x, 'path': str(p / x)} for x in ('a', 'b')]
            before = content_hash(asset_manifest(assets))
            self.assertEqual(before, content_hash(asset_manifest(list(reversed(assets)))))
            self.assertNotEqual(content_hash(asset_manifest(assets, ordered=True)),
                                content_hash(asset_manifest(list(reversed(assets)), ordered=True)))
            (p / 'b').write_text('different trace body')
            self.assertNotEqual(before, content_hash(asset_manifest(assets)))

    def test_duplicate_and_escaping_asset_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'input'
            p.write_text('x')
            for names in [('a', 'a'), ('../escape',), ('/absolute',)]:
                with self.subTest(names=names), self.assertRaises(ValueError):
                    asset_manifest([{'name': name, 'path': str(p)} for name in names])


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.host = socket.gethostname()
        policy = {'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                  'max_simulators': 2, 'max_cpu_units': 8, 'max_reserved_memory_bytes': 32 * 1024**3,
                  'default_run_memory_bytes': 8 * 1024**3, 'min_available_memory_bytes': 64 * 1024**3,
                  'min_disk_free_bytes': 48 * 1024**3, 'max_build_jobs': 4, 'scan_exclusive': True}
        (self.root / 'RUN_REGISTRY.json').write_text(json.dumps({'authority_host': self.host,
            'hosts': {self.host: policy}, 'runs': {}, 'resource_leases': {}}))
        self.registry = Registry(self.root)
        self.resources = {'available_memory_bytes': 2**50, 'disk_free_bytes': 2**50}

    def tearDown(self):
        self.tmp.cleanup()

    def claim(self, row=None):
        return self.registry.claim(row or identity(), 'lane5', '/unused/test-only', resources=self.resources)

    def test_multiprocess_exactly_one_claim(self):
        ctx = multiprocessing.get_context('fork')
        queue = ctx.Queue()
        workers = [ctx.Process(target=claim_worker, args=(str(self.root), queue)) for _ in range(8)]
        for worker in workers: worker.start()
        rows = [queue.get(timeout=10) for _ in workers]
        for worker in workers:
            worker.join(timeout=10)
            self.assertEqual(worker.exitcode, 0)
        self.assertTrue(all(row[0] == 'OK' for row in rows), rows)
        self.assertEqual(sum(row[1] for row in rows), 1)
        self.assertEqual(len({row[2] for row in rows}), 1)

    def test_lane4_reuses_lane5_baseline(self):
        self.claim()
        fresh, row = self.registry.claim(identity(), 'lane4', '/different/path', resources=self.resources)
        self.assertFalse(fresh)
        self.assertEqual(row['owner'], 'lane5')

    def test_shared_quota(self):
        self.claim()
        other = identity()
        other['workload'] = 'cfd_097k'
        self.claim(other)
        other['workload'] = 'FWT_7_21'
        with self.assertRaisesRegex(ValueError, 'quota full'):
            self.claim(other)

    def test_scan_cannot_overlap(self):
        self.claim()
        other = identity()
        other['workload'] = 'scan'
        with self.assertRaisesRegex(ValueError, 'exclusive'):
            self.claim(other)

    def test_scan_blocks_new_short_task(self):
        row = identity()
        row['workload'] = 'scan'
        self.claim(row)
        with self.assertRaisesRegex(ValueError, 'exclusive'):
            self.claim()

    def test_disk_and_memory_floors(self):
        for field in self.resources:
            resources = dict(self.resources)
            resources[field] = 0
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.registry.claim(identity(), 'lane5', '/unused', resources=resources)

    def test_invalid_owner_and_negative_reservations(self):
        for kwargs in ({'owner': 'unknown'}, {'owner': 'lane5', 'cpu': -1},
                       {'owner': 'lane5', 'memory': -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.registry.claim(identity(), result_directory='/unused', resources=self.resources, **kwargs)

    def test_terminal_ownership_and_no_implicit_retry(self):
        _, row = self.claim()
        with self.assertRaises(ValueError):
            self.registry.update(row['run_key'], 'wrong-owner-token', 'FAILED')
        self.registry.update(row['run_key'], row['lease_id'], 'FAILED', detail='test-only failed record')
        self.assertFalse(self.claim()[0])
        with self.assertRaises(ValueError):
            self.registry.update(row['run_key'], row['lease_id'], 'RUNNING', process={'pid': 1})

    def test_running_requires_real_identity(self):
        _, row = self.claim()
        with self.assertRaises(ValueError):
            self.registry.update(row['run_key'], row['lease_id'], 'RUNNING')
        import os
        self.registry.update(row['run_key'], row['lease_id'], 'RUNNING', process=process_identity(os.getpid()))
        self.assertEqual(self.registry.snapshot()['runs'][row['run_key']]['status'], 'RUNNING')

    def test_registry_missing_and_wrong_authority_fail_closed(self):
        with self.assertRaises(ValueError):
            Registry(self.root / 'not-an-authority').snapshot()
        data = self.registry.snapshot()
        data['authority_host'] = 'a-different-host'
        (self.root / 'RUN_REGISTRY.json').write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.claim()


def reference_fixture():
    return [{'op': 'initialize', 'epoch': 1, 'slice': 0, 'line': 4096, 'sector': 2, 'data': 'ab' * 32},
            {'op': 'read', 'epoch': 1, 'slice': 0, 'line': 4096, 'sector': 2, 'request_id': 'A'},
            {'op': 'write', 'epoch': 1, 'slice': 0, 'line': 4096, 'sector': 2, 'request_id': 'B', 'data': 'cd' * 32},
            {'op': 'read', 'epoch': 1, 'slice': 0, 'line': 4096, 'sector': 2, 'request_id': 'C'}]


def event_fixture():
    rows = []
    def add(event, **fields):
        rows.append({'event': event, 'epoch': 1, 'slice': 0, 'cycle': len(rows), **fields})
    for request in 'ABC':
        add('request_admitted', request_id=request)
        add('descriptor_alloc', id=ord(request), request_id=request)
    add('payload_alloc', id=4, generation=1, role='FILL_PENDING')
    add('tag_bind', tag=4, line=4096, tag_generation=1, payload_id=4, payload_generation=1, reason='miss')
    add('fill', attached=True, tag=4, line=4096, tag_generation=1, payload_id=4, payload_generation=1)
    add('bank_op', bank=0)
    add('response', request_id='A', kind='read', data='ab' * 32)
    add('descriptor_free', id=ord('A'))
    add('response', request_id='B', kind='write')
    add('descriptor_free', id=ord('B'))
    add('response', request_id='C', kind='read', data='cd' * 32)
    add('descriptor_free', id=ord('C'))
    add('wad_alloc', id=3, line=4096)
    add('wb_created', id=5, wad_id=3)
    add('tag_unbind', tag=4, tag_generation=1)
    add('payload_role', id=4, generation=1, role='WB_STAGED')
    add('wb_lower_accepted', id=5, data_handoff_accounted=True)
    add('payload_free', id=4, generation=1, pending_sectors=0, read_refs=0, wb_id=5)
    add('wb_completed', id=5)
    add('wad_free', id=3, wb_id=5)
    add('terminal', hardware_drained=True)
    return rows


class EvidenceTests(unittest.TestCase):
    def test_reference_data_and_versions(self):
        result = validate_events(reference_fixture(), event_fixture())
        self.assertEqual((result['unique_requesters'], result['responses'], result['wb_completed']), (3, 3, 1))

    def mutate(self, event_type, field, value):
        rows = event_fixture()
        next(r for r in rows if r['event'] == event_type)[field] = value
        return rows

    def test_corrupt_sector_bytes(self):
        with self.assertRaisesRegex(InvalidEvidence, 'data/version'):
            validate_events(reference_fixture(), self.mutate('response', 'data', '00' * 32))

    def test_stale_store_version(self):
        rows = event_fixture()
        next(r for r in rows if r['event'] == 'response' and r['request_id'] == 'C')['data'] = 'ab' * 32
        with self.assertRaisesRegex(InvalidEvidence, 'data/version'):
            validate_events(reference_fixture(), rows)

    def test_duplicate_response_not_hidden_by_equal_total(self):
        rows = event_fixture()
        next(r for r in rows if r['event'] == 'response' and r['request_id'] == 'C')['request_id'] = 'A'
        with self.assertRaises(InvalidEvidence):
            validate_events(reference_fixture(), rows)

    def test_stale_fill_and_detached_install(self):
        for kind, field, value in [('fill', 'tag_generation', 99),
                                   ('tag_bind', 'reason', 'detached_fill'),
                                   ('payload_free', 'generation', 99),
                                   ('payload_free', 'pending_sectors', 1),
                                   ('payload_free', 'read_refs', 1),
                                   ('wb_lower_accepted', 'data_handoff_accounted', False),
                                   ('terminal', 'hardware_drained', False)]:
            with self.subTest(field=field), self.assertRaises(InvalidEvidence):
                validate_events(reference_fixture(), self.mutate(kind, field, value))

    def test_missing_milestones_are_not_zero(self):
        for event_type in ('response', 'descriptor_free', 'payload_free', 'wb_lower_accepted',
                           'wb_completed', 'wad_free', 'tag_unbind', 'terminal'):
            rows = event_fixture()
            rows.remove(next(r for r in rows if r['event'] == event_type))
            with self.subTest(event_type=event_type), self.assertRaises(InvalidEvidence):
                validate_events(reference_fixture(), rows)

    def test_bank_oversubscription(self):
        rows = event_fixture()
        index = next(i for i, r in enumerate(rows) if r['event'] == 'bank_op')
        rows.insert(index, deepcopy(rows[index]))
        with self.assertRaisesRegex(InvalidEvidence, 'bank cycle'):
            validate_events(reference_fixture(), rows)

    def test_no_implicit_zero_or_empty_stimulus(self):
        with self.assertRaises(InvalidEvidence):
            reference_requests([])
        with self.assertRaises(InvalidEvidence):
            reference_requests(reference_fixture()[1:])

    def test_unrelated_epoch_cannot_complete_waiter(self):
        rows = self.mutate('response', 'epoch', 2)
        with self.assertRaises(InvalidEvidence):
            validate_events(reference_fixture(), rows)

    def test_event_after_terminal(self):
        rows = event_fixture()
        rows.append(dict(rows[-1], cycle=100))
        with self.assertRaises(InvalidEvidence):
            validate_events(reference_fixture(), rows)


def summary_fixture():
    return dict(cycles=100, instructions=200, unique_requesters=3, responses=3,
        live_descriptors=0, live_line_mshrs=0, live_wad=0, pending_lower_reads=0,
        pending_returns=0, pending_responses=0, wb_created=1, wb_lower_accepted=1,
        wb_completed=1, payload_capacity=1168 * 64, payload_free=1168 * 64 - 10,
        payload_roles={'RESIDENT_CLEAN': 10}, transient_payloads=0, hardware_drained=True,
        workload_termination=identity()['termination_contract'], slices=64,
        requester_exact_once_audit=True, data_correctness_qualification=True)


class TerminalTests(unittest.TestCase):
    def test_resident_data_may_legally_remain(self):
        self.assertEqual(validate_summary(summary_fixture(), identity())['status'], 'PASS')

    def test_missing_or_invalid_terminal_metrics(self):
        row = summary_fixture()
        for field in row:
            changed = deepcopy(row)
            del changed[field]
            with self.subTest(field=field), self.assertRaises((ValueError, KeyError)):
                validate_summary(changed, identity())

    def test_invalid_closure_and_scope(self):
        for field, value in [('live_descriptors', 1), ('live_line_mshrs', 1), ('live_wad', 1),
            ('pending_lower_reads', 1), ('pending_returns', 1), ('pending_responses', 1),
            ('wb_completed', 0), ('responses', 2), ('transient_payloads', 1),
            ('hardware_drained', False), ('payload_free', 0), ('slices', 63),
            ('payload_capacity', 1152 * 64), ('cycles', 0), ('instructions', -1),
            ('requester_exact_once_audit', False), ('data_correctness_qualification', False)]:
            row = summary_fixture()
            row[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_summary(row, identity())

    def test_scalar_counter_is_not_cycle_sum(self):
        result = validate_summary(summary_fixture(), identity())
        self.assertIn('never slice-summed', result['cycles_scope'])


class RunnerInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name, data in [('sim', 'fixture executable content; never launched'), ('config', '-mode 1\n'),
                           ('kernelslist.g', 'MemcpyHtoD,0x1000,32\nkernel-1.traceg\n'),
                           ('kernel-1.traceg', 'fixture trace body'), ('parser.py', '# fixture parser'),
                           ('evidence.json', '{"test_fixture_only":true}')]:
            (self.root / name).write_text(data)
        self.spec = {'identity': identity(), 'owner': 'lane5', 'binary': str(self.root / 'sim'),
                     'configs': [{'name': 'primary', 'path': str(self.root / 'config')}],
                     'auxiliary_assets': [],
                     'trace_files': [{'name': n, 'path': str(self.root / n)} for n in ('kernelslist.g', 'kernel-1.traceg')],
                     'entry_trace_name': 'kernelslist.g', 'qualified_release': str(self.root / 'release.json'),
                     'parser': {'path': str(self.root / 'parser.py'), 'sha256': digest(self.root / 'parser.py')},
                     'timeout_seconds': 30, 'environment': {}}
        row = self.spec['identity']
        row['binary_sha256'] = digest(self.root / 'sim')
        row['runtime_config_sha256'] = content_hash({'ordered_configs': asset_manifest(self.spec['configs'], ordered=True),
                                                   'auxiliary_assets': [], 'environment': {}})
        row['trace_content_sha256'] = content_hash(asset_manifest(self.spec['trace_files']))
        # Synthetic envelope exercises validation only and is never published as production evidence.
        self.release = {'status': 'INDEPENDENTLY_QUALIFIED', 'qualified_by': 'lane5',
                        'evidence_kind': 'PRODUCTION_DRIVEN',
                        **{k: row[k] for k in ('core_source_commit', 'framework_source_commit', 'binary_sha256')},
                        'qualified_feature_vectors': [row['feature_vector']],
                        'gates': {g: {'status': 'PASS', 'production_driven': True,
                            'evidence_path': str(self.root / 'evidence.json'),
                            'evidence_sha256': digest(self.root / 'evidence.json')} for g in GATES}}
        self.write_release()

    def tearDown(self):
        self.tmp.cleanup()

    def write_release(self):
        (self.root / 'release.json').write_text(json.dumps(self.release))

    def test_complete_input_manifest_can_be_inspected_without_launch(self):
        self.assertEqual(inspect(self.spec)['run_key'], run_key(self.spec['identity']))

    def test_every_runtime_asset_is_content_checked(self):
        for name in ('sim', 'config', 'kernel-1.traceg', 'kernelslist.g', 'parser.py', 'evidence.json'):
            path = self.root / name
            original = path.read_bytes()
            path.write_bytes(original + b'changed')
            with self.subTest(name=name), self.assertRaises(ValueError):
                inspect(self.spec)
            path.write_bytes(original)

    def test_pending_harness_and_unpassed_gates_rejected(self):
        for field, value in [('status', 'RUNTIME_VALIDATION_PENDING'), ('qualified_by', 'lane1'),
                             ('evidence_kind', 'HARNESS_ONLY')]:
            old = self.release[field]
            self.release[field] = value
            self.write_release()
            with self.subTest(field=field), self.assertRaises(ValueError):
                inspect(self.spec)
            self.release[field] = old
        self.release['gates']['sector_reference_data']['status'] = 'NOT_RUN'
        self.write_release()
        with self.assertRaises(ValueError):
            inspect(self.spec)

    def test_missing_reference_content_rejected(self):
        self.spec['trace_files'] = self.spec['trace_files'][:1]
        with self.assertRaises(ValueError):
            validate_trace_closure(self.spec)

    def test_unknown_trace_commands_rejected(self):
        (self.root / 'kernelslist.g').write_text('unknown-future-command input.bin\n')
        with self.assertRaises(ValueError):
            validate_trace_closure(self.spec)

    def test_incomplete_feature_vectors_and_unequal_budgets_rejected(self):
        for flag, value in [('payload_capacity_per_slice', 1152), ('bank_count', 8),
                            ('ops_per_bank_cycle', 2), ('finite_wbuf', False),
                            ('tvd', True), ('adaptive_policy', True)]:
            spec = deepcopy(self.spec)
            spec['identity']['feature_vector'][flag] = value
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                inspect(spec)

    def test_environment_changes_identity(self):
        self.spec['environment']['GPGPUSIM_ROOT'] = '/some/other/core'
        with self.assertRaises(ValueError):
            inspect(self.spec)

    def test_fragment_and_ideal_excluded_from_formal_results(self):
        spec = deepcopy(self.spec)
        spec['identity']['epoch_range']['scope'] = 'diagnostic_fragment'
        with self.assertRaises(ValueError):
            inspect(spec)
        spec = deepcopy(self.spec)
        spec['identity']['ideal_vector']['wb'] = True
        with self.assertRaises(ValueError):
            inspect(spec)


if __name__ == '__main__':
    unittest.main(verbosity=2)
