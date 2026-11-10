"""DTC owner Stage II-A Remaining48 commitment closeout; no data deletion."""
import copy
import datetime
import fcntl
import hashlib
import json
import os
import pathlib
import sys
import time

P = pathlib.Path
ROOT = P('/root/data/ep_l2_dtc_l1_native_v2/control')
RP = ROOT / 'science_authority/NATIVE_SCIENCE_REGISTRY.json'
EP = ROOT / 'CURRENT_SCIENCE_EPOCH.json'
LOCK = ROOT / 'science_authority/REGISTRY_UPDATE.lock'
HISTORY = ROOT / 'science_authority/request_history'
RECEIPTS = ROOT / 'science_authority/dtc_stage48_owner_closeout_v2'
MIB = 1024 * 1024
TARGET = {
    'DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1': ('/root/data/dtc_stage_iia_remaining48_20261104_v1', 9395240960, 48),
}
RETAIN = 268435456


def sha(p):
    return hashlib.sha256(P(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(P(p).read_bytes())


def payload(v):
    return (json.dumps(v, sort_keys=True, indent=2) + '\n').encode()


def atomic(p, raw):
    temp = p.with_name('.' + p.name + '.DTC_CLOSEOUT.' + str(os.getpid()) + '.writing')
    with temp.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, p)
    fd = os.open(p.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def evidence(req, root, count):
    root = P(root)
    policy = root / 'control/RESOURCE_POLICY.json'
    p = read(policy)
    assert p['metadata_reserve_bytes'] == RETAIN
    control = root / 'control'
    analysis = root / 'analysis'
    specs = {x.name.removesuffix('_SPEC.json') for x in control.glob('*_SPEC.json')}
    assert len(specs) == count
    terminal = analysis / 'EXECUTION_TERMINAL.json'
    t = read(terminal)
    assert t['status'] == 'ALL' + str(count) + '_STRICT_OR_ARCHIVED_NEGATIVE_TERMINAL'
    assert set(t['states']) == specs
    assert all(s.startswith('PASS_') or (s.startswith('FAIL_') and s.endswith('ARCHIVED_NO_RETRY')) for s in t['states'].values())
    claims = control / 'POOL_DISPATCH_RESERVATIONS.json'
    assert read(claims)['claims'] == {}
    entries = []
    for cohort in sorted(specs):
        a = control / (cohort + '_ARCHIVE_RECEIPT.json')
        r = analysis / (cohort + '.RESULT.json')
        x = read(a)
        result = read(r)
        assert x['cohort'] == cohort and x['status'] == 'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
        assert x['source_disposition'] == 'SOURCE_KEEP' and x['source_release_bytes'] == 0
        assert result['state'] == t['states'][cohort]
        target = P(x['target_mount_path'])
        commit = target / 'COMMIT.json'
        restore = target / 'RESTORE_VERIFIED_NATIVE_TARGET.json'
        assert read(commit)['txid'] == x['txid'] and restore.exists()
        assert P(x['native_restore']).exists()
        entries.append({'cohort': cohort, 'result_sha256': sha(r), 'archive_receipt_sha256': sha(a), 'true164_commit_sha256': sha(commit), 'native_restore_receipt_sha256': sha(restore)})
    return {'request': req, 'root': str(root), 'terminal_path': str(terminal), 'terminal_sha256': sha(terminal), 'claim_path': str(claims), 'claim_sha256': sha(claims), 'policy_path': str(policy), 'policy_sha256': sha(policy), 'metadata_retained_bytes': RETAIN, 'cohorts': entries}


def main():
    RECEIPTS.mkdir(exist_ok=True)
    HISTORY.mkdir(exist_ok=True)
    # The 164 COMMIT and restore checks can block on FUSE. Finish them before
    # taking the shared registry EX lock; recheck local authority SHA inside.
    proofs = {req: evidence(req, root, count)
              for req, (root, old, count) in TARGET.items()}
    with LOCK.open('a+b') as lock:
        deadline = time.monotonic() + 2.0
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise RuntimeError('REGISTRY_EX_BUSY_HOLD_NO_MUTATION')
                time.sleep(.02)
        old_r = RP.read_bytes()
        old_e = EP.read_bytes()
        reg = json.loads(old_r)
        epoch = json.loads(old_e)
        before_r = hashlib.sha256(old_r).hexdigest()
        before_e = hashlib.sha256(old_e).hexdigest()
        assert epoch['epoch'] == reg['epoch'] == 2 and epoch['native_registry_sha256'] == before_r
        peers = {k: copy.deepcopy(v) for k, v in reg['registered_future_requests'].items() if k not in TARGET}
        old_nonrequests = {k: copy.deepcopy(v) for k, v in reg.items() if k != 'registered_future_requests'}
        details = []
        for req, (root, old, count) in TARGET.items():
            q = reg['registered_future_requests'][req]
            assert q['request'] == req and q['budget'] == count and q['remaining'] == 0
            assert len(q['consumed']) == count and q['reserved_write_bytes'] == old
            proof = proofs[req]
            assert sha(proof['terminal_path']) == proof['terminal_sha256']
            assert sha(proof['claim_path']) == proof['claim_sha256']
            assert read(proof['claim_path'])['claims'] == {}
            assert sha(proof['policy_path']) == proof['policy_sha256']
            assert set(q['consumed']) == {x['cohort'] for x in proof['cohorts']}
            details.append({'request': req, 'before_bytes': old, 'after_bytes': RETAIN, 'released_bytes': old - RETAIN, 'evidence': proof})
        intent = {'schema': 'DTC_STAGE48_OWNER_CLOSEOUT_INTENT_V2', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'operation': 'DTC_STAGE48_REMAINING_WRITE_COMMITMENT_OWNER_CLOSEOUT_V2', 'owner': 'DTC-L1 Main', 'before_registry_sha256': before_r, 'before_epoch_sha256': before_e, 'retained_metadata_per_request_bytes': RETAIN, 'source_release_bytes': 0, 'details': details}
        intent_path = RECEIPTS / 'DTC_STAGE48_CLOSEOUT_INTENT.json'
        if intent_path.exists():
            raise RuntimeError('INTENT_ALREADY_EXISTS_NO_MUTATION')
        with intent_path.open('xb') as f:
            f.write(payload(intent)); f.flush(); os.fsync(f.fileno())
        intent_sha = sha(intent_path)
        for p, raw in [(RP, old_r), (EP, old_e)]:
            backup = HISTORY / (p.stem + '.' + hashlib.sha256(raw).hexdigest() + '.json')
            if backup.exists():
                assert backup.read_bytes() == raw
            else:
                with backup.open('xb') as f:
                    f.write(raw); f.flush(); os.fsync(f.fileno())
        for x in details:
            q = reg['registered_future_requests'][x['request']]
            q['reserved_write_bytes'] = RETAIN
            q['owner_native_write_closeout'] = {'status': 'RESULT_AND_RESTORE_GROWTH_CLOSED_METADATA_RETAINED', 'intent_path': str(intent_path), 'intent_sha256': intent_sha, 'before_bytes': x['before_bytes'], 'retained_metadata_bytes': RETAIN, 'released_bytes': x['released_bytes'], 'source_disposition': 'SOURCE_KEEP'}
        assert peers == {k: v for k, v in reg['registered_future_requests'].items() if k not in TARGET}
        assert old_nonrequests == {k: v for k, v in reg.items() if k != 'registered_future_requests'}
        new_r = payload(reg)
        new_r_sha = hashlib.sha256(new_r).hexdigest()
        new_epoch = copy.deepcopy(epoch)
        new_epoch['native_registry_sha256'] = new_r_sha
        new_epoch['request_revision'] = {'operation': 'DTC_STAGE48_REMAINING_WRITE_COMMITMENT_OWNER_CLOSEOUT_V2', 'owner': 'DTC-L1 Main', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'prior_registry_sha256': before_r, 'prior_epoch_sha256': before_e, 'intent_sha256': intent_sha, 'request_ids': sorted(TARGET), 'previous_request_revision': epoch.get('request_revision')}
        new_e = payload(new_epoch)
        assert {k: v for k, v in new_epoch.items() if k not in ['native_registry_sha256', 'request_revision']} == {k: v for k, v in epoch.items() if k not in ['native_registry_sha256', 'request_revision']}
        try:
            atomic(RP, new_r)
            atomic(EP, new_e)
            assert sha(RP) == new_r_sha and read(EP)['native_registry_sha256'] == new_r_sha
        except Exception:
            atomic(RP, old_r)
            atomic(EP, old_e)
            raise
        done = {'schema': 'DTC_STAGE48_OWNER_CLOSEOUT_COMMITTED_V2', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'intent_path': str(intent_path), 'intent_sha256': intent_sha, 'before_registry_sha256': before_r, 'after_registry_sha256': sha(RP), 'before_epoch_sha256': before_e, 'after_epoch_sha256': sha(EP), 'released_commitment_bytes': sum(x['released_bytes'] for x in details), 'remaining_metadata_bytes': RETAIN, 'epoch': 2, 'new_scientific_budget_remaining_unchanged': reg['new_scientific_budget_remaining'], 'other_request_rows_unchanged': True, 'other_registry_fields_unchanged': True, 'epoch_unrelated_fields_unchanged': True, 'source_release_bytes': 0, 'model_starts': 0}
        done_path = RECEIPTS / 'DTC_STAGE48_CLOSEOUT_COMMITTED.json'
        with done_path.open('xb') as f:
            f.write(payload(done)); f.flush(); os.fsync(f.fileno())
        print(json.dumps(done, sort_keys=True))


if __name__ == '__main__':
    main()
