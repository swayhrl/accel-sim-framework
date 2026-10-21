"""Read-only completion audit; never launches, accepts or changes the registry.

Uses exact registered receipts and the existing independent terminal validator.
Does not reread large traces/raw logs or reconstruct missing native exit status.
"""
from pathlib import Path
import hashlib, importlib.util, json, sys, time

PACK = Path(__file__).resolve().parents[1]
ROOT = PACK.parents[3]
sys.path.insert(0, str(ROOT / 'util/ep_l2/mechanism_e'))
import coordinator as c
import runner


def read(path):
    return json.loads(Path(path).read_bytes())


def checked(ref):
    raw = Path(ref['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref['sha256'], ref['path']
    return json.loads(raw)


def audit():
    module_spec = importlib.util.spec_from_file_location('capacity_report_audit', PACK / 'report.py')
    report = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(report)
    coord = c.Coordinator()
    state = coord.snapshot()
    old = report.check_history(state)
    plan = read(PACK / 'PLAN.json')
    assert plan['authority_commit'] == '49343880865edb22a17523790fc32dd55975966c'
    assert plan['main61_qualification_inherited'] is False and plan['old_anchor_reused'] is False
    assert len(plan['conditions']) == 10 and len(plan['pairs']) == 5
    assert state['actual_starts'] == 46 and len(state['attempts']) == 46
    assert len(old['attempts']) == 36
    new = state['attempts'][36:]
    assert len(new) == 10 and all(a['actual_start'] is True for a in new)
    assert {a['run_key'] for a in new} == {r['run_key'] for r in plan['conditions']}
    assert len({a['run_key'] for a in new}) == 10, 'No automatic retries or duplicated conditions'
    assert plan['source_identity'] == state['capacity_diagnostic_runtime']
    assert plan['source_identity']['binary_sha256'] == '93a9f28ddb9c0c9ceb93409764a5664666589477778fe5d41d90a179704706eb'
    checked(plan['formal_producer']['release'])
    checked(plan['formal_producer']['remote_readback'])
    assert plan['formal_producer']['commit'] == '0ae16a6c48bdffbdf38ced4da6c76dda4981a813'
    endpoints = []
    qualifications = {}
    for row in plan['conditions']:
        attempt, = [a for a in new if a['run_key'] == row['run_key']]
        pointer = state['accepted_results'].get(attempt['attempt_id'])
        qid = pointer['qualification_id'] if pointer else attempt['qualification_id']
        qrow = state['qualifications'][qid]
        q = checked(qrow)
        assert q == qrow['qualification'] and q['status'] == 'INDEPENDENTLY_QUALIFIED'
        assert q['source_identity'] == plan['source_identity']
        assert row['profile'] in q['supported_profiles']
        assert all(g['status'] == 'PASS' for g in q['gates'].values())
        coord.require_no_hold(state, qid)
        if qid not in qualifications:
            checked(q['independent_native_replay'])
            for gate in q['gates'].values():
                assert c.digest(gate['evidence_path']) == gate['evidence_sha256']
            qualifications[qid] = dict(path=qrow['path'], sha256=qrow['sha256'], gate_count=len(q['gates']), source_identity=q['source_identity'], native_evidence=q['independent_native_replay'])
        record = dict(condition_id=row['condition_id'], attempt_id=attempt['attempt_id'], profile=row['profile'], qualification_id=qid, original_attempt_state=attempt['state'])
        if not pointer:
            record.update(status='PENDING_ACCEPTED_RECEIPT', actual_process=attempt.get('process'), no_exit_status_inferred=True)
            endpoints.append(record)
            continue
        receipt = checked(pointer)
        assert receipt['status'] == 'COMPLETE_VALID' and receipt['independent_acceptance'] == 'PASS'
        assert receipt['complete_input_verified'] is True
        assert receipt['source_identity'] == plan['source_identity']
        assert receipt['run_key'] == row['run_key'] and receipt['qualification_id'] == qid
        assert receipt['summary']['instructions'] == row['expected_full_instructions']
        assert receipt['summary']['slices'] == 64 and receipt['summary']['hardware_drained'] is True
        native_path = Path(pointer['path']).parent / 'NATIVE_EXIT.json'
        native = read(native_path)
        assert c.digest(native_path) == receipt['native_exit_receipt_sha256']
        assert native == receipt['native_exit_evidence']
        assert native['exit_code'] == native['wait_status'] == 0 and native['stop_reason'] is None
        assert native['native_process'] == receipt['process'] == attempt['process']
        spec = read(Path(pointer['path']).parent / 'input_spec.json')
        assert runner.validate_terminal_summary(receipt['summary'], spec, qrow, receipt['input_audit']) == receipt['validation']
        record.update(status='VERIFIED_ACCEPTED_ENDPOINT', receipt=pointer, native_exit_sha256=receipt['native_exit_receipt_sha256'], native_process=native['native_process'], cycles=receipt['summary']['cycles'], instructions=receipt['summary']['instructions'], slices=64, hardware_drained=True, capacity_classification=receipt['summary'].get('capacity_classification'), parser_only_recovered=pointer.get('parser_only_recovered', False))
        endpoints.append(record)
    pairs = []
    for wanted in plan['pairs']:
        pair = state['accepted_pairs'].get(wanted['pair_id'])
        row = dict(pair_id=wanted['pair_id'], status='PENDING_CURRENT_ACCEPTED')
        if pair:
            assert pair['status'] == 'CURRENT_ACCEPTED' and pair['nonresearch_config_equal'] is True
            assert {v['run_key'] for v in pair['endpoints'].values()} == {wanted['left_run_key'], wanted['right_run_key']}
            assert all(v['identity']['binary_sha256'] == plan['source_identity']['binary_sha256'] for v in pair['endpoints'].values())
            artifact = read(PACK / (pair['pair_id'] + '_ACCEPTED_PAIR.json'))
            assert artifact['accepted_pair'] == pair
            delivery = read(PACK / (pair['pair_id'] + '_D_DELIVERY_RECEIPT.json'))
            assert delivery['status'] == 'DELIVERED_AFTER_REMOTE_READBACK_NOT_CONSUMPTION_CLAIM'
            assert len(delivery['channels']) == 3
            row.update(status='VERIFIED_CURRENT_ACCEPTED_AND_D_DELIVERED', cycles_off=pair['cycles_left'], cycles_on=pair['cycles_right'], delivery=delivery)
        pairs.append(row)
    usage = c.output_usage()
    assert usage['new_bytes'] <= state['additional_results_max_bytes'] == 10 * 1024**3
    assert usage['total_bytes'] <= state['old_plus_new_results_max_bytes'] == 24 * 1024**3
    complete = all(x['status'] == 'VERIFIED_ACCEPTED_ENDPOINT' for x in endpoints) and all(x['status'] == 'VERIFIED_CURRENT_ACCEPTED_AND_D_DELIVERED' for x in pairs) and state['controller']['state'] == 'STOPPED'
    return dict(schema='E2_CAPACITY_REQUIREMENT_COMPLETION_AUDIT_V1', at_unix=time.time(), status='COMPLETE_PROVEN' if complete else 'INCOMPLETE_WAIT_FOR_ACTUAL_TERMINAL_EVIDENCE', actual_starts=46, new_actual_starts=10, original_36_history_unchanged=True, original_T0=state['t0_unix'], original_matrix_reservations_holds_accepted_results_preserved=True, producer_commit=plan['formal_producer']['commit'], frozen_source_identity=plan['source_identity'], qualifications=qualifications, endpoints=endpoints, pairs=pairs, controller=state['controller'], output_usage=usage, result_limits=dict(new_bytes=state['additional_results_max_bytes'], old_plus_new_bytes=state['old_plus_new_results_max_bytes']), no_additional_application_or_native_starts=True, no_raw_or_trace_body_read=True, no_registry_or_lease_mutation=True, peer_ACK_not_inferred=True)


if __name__ == '__main__':
    result = audit()
    destination = Path(__file__).with_name('AUDIT.json')
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], accepted_endpoints=sum(r['status'] == 'VERIFIED_ACCEPTED_ENDPOINT' for r in result['endpoints']), accepted_pairs=sum(r['status'] == 'VERIFIED_CURRENT_ACCEPTED_AND_D_DELIVERED' for r in result['pairs']), controller=result['controller']['state'])))
