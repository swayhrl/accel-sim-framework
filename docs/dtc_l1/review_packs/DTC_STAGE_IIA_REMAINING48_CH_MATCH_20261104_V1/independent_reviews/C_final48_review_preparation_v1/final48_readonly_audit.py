"""Read-only fixed48 final lifecycle checker. Never starts or controls models."""
from pathlib import Path, PurePosixPath
import argparse, copy, datetime, gzip, hashlib, importlib.util, io, json
import os, re, subprocess, sys, tarfile, time, traceback
sys.dont_write_bytecode = True
A = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
R = Path('/root/data/dtc_stage_iia_remaining48_20261104_v1')
PREP = A / 'agents/C_final48_review_preparation_v1'
REQ = 'DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
PLAN_SHA = '9f257eeea3ebe81610a88cef8ad37512b54bdb50728f965e8d73ccf5dd89a4b3'
CANDIDATE_SHA = '6f7aa38a351e58e0711cba1a2aabe5df916cc05fe3968e9fc70d595df6490703'
HELPER_SHA = 'a9f881775a6780237470104b286e82abad2e9d51f7b4f696767439bfce5595df'
PASS = 'PASS_STAGEII48_CH_STRICT_ARCHIVE_NATIVE_RESTORE'
NEGATIVE = 'FAIL_STAGEII48_CH_ARCHIVED_NO_RETRY'
REGISTRY = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
PROVIDER = A / 'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json'

def rd(path):
    return json.loads(Path(path).read_bytes())

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def relative(name):
    p = PurePosixPath(name)
    assert not p.is_absolute() and '..' not in p.parts
    return p

def live(pidmap):
    try:
        fields = Path('/proc', str(pidmap['pid']), 'stat').read_text().rsplit(')', 1)[1].split()
        return int(fields[19]) == pidmap['start_ticks'] and fields[0] not in ['Z', 'X']
    except (FileNotFoundError, ProcessLookupError):
        return False

def eligibility(points, request, states, live_ids):
    expected = {point['cohort'] for point in points}
    reasons = []
    if len(points) != 48 or len(expected) != 48:
        reasons.append('NOT_EXACT48_MATRIX')
    if request.get('budget') != 48 or request.get('remaining') != 0:
        reasons.append('BUDGET_NOT_FULLY_SPENT48')
    consumed = request.get('consumed', {})
    if set(consumed) != expected or set(request.get('admitted_specs', {})) != expected:
        reasons.append('CONSUMED_OR_GRANT_SET_NOT_EXACT48')
    if len({row.get('uuid') for row in consumed.values()}) != len(consumed):
        reasons.append('DUPLICATE_UUID')
    if any(row.get('charged') != 1 or not row.get('execution_receipt') for row in consumed.values()):
        reasons.append('MISSING_ONE_START_CHARGE_OR_DONE')
    if set(states) != expected or any(value not in [PASS, NEGATIVE] for value in states.values()):
        reasons.append('MISSING_OR_NONTERMINAL_RESULT')
    if live_ids:
        reasons.append('ACTUAL_MODEL_GENERATION_STILL_LIVE')
    return dict(ready_for_expensive_final_audit=not reasons, reasons=reasons,
                expected=48, consumed=len(consumed), live=list(live_ids),
                accepted=sum(value == PASS for value in states.values()),
                archived_negative=sum(value == NEGATIVE for value in states.values()),
                scientific_acceptance_granted_by_gate=False)

def typed_tree(source, restore, manifest, proof):
    entries = manifest['entries']
    names = [entry['path'] for entry in entries]
    assert len(names) == len(set(names)) == len(proof['rows'])
    assert set(names) == {row['path'] for row in proof['rows']}
    proof_by_name = {row['path']: row for row in proof['rows']}
    counts = dict(file=0, directory=0, symlink=0)
    files = []
    for entry in entries:
        name = str(relative(entry['path']))
        src, dst = Path(source) / name, Path(restore) / name
        record = proof_by_name[entry['path']]
        kind = entry['type']
        assert kind in counts and record['type'] == kind
        counts[kind] += 1
        if kind == 'file':
            assert src.is_file() and dst.is_file() and not src.is_symlink() and not dst.is_symlink()
            assert sha(src) == sha(dst) == entry['sha256'] == record['sha256']
            assert src.stat().st_size == dst.stat().st_size == entry['size']
            files.append(dict(path=name, sha256=entry['sha256'], bytes=entry['size']))
        elif kind == 'directory':
            assert src.is_dir() and dst.is_dir() and not src.is_symlink() and not dst.is_symlink()
        else:
            assert src.is_symlink() and dst.is_symlink()
            assert os.readlink(src) == os.readlink(dst) == entry['target'] == record['target']
    for root in [Path(source), Path(restore)]:
        actual = {'.'} | {str(p.relative_to(root)) for p in root.rglob('*')}
        assert actual == set(names), ('UNLISTED_OR_MISSING_TYPED_ENTRY', str(root), actual ^ set(names))
    return dict(entry_count=len(entries), type_counts=counts, files=files)

class ChunkReader:
    """Sequential archive reader with independent per-chunk and whole SHA."""
    def __init__(self, root, index):
        self.root, self.index = Path(root), index
        self.rows = iter(sorted(index['chunks'], key=lambda row: row['offset']))
        self.current = None
        self.file = None
        self.chunk_sha = None
        self.chunk_bytes = 0
        self.total_sha = hashlib.sha256()
        self.total_bytes = 0
        self.verified_chunks = []

    def read(self, amount=-1):
        pieces = []
        remaining = amount
        while remaining != 0:
            if self.file is None:
                try:
                    self.current = next(self.rows)
                except StopIteration:
                    break
                row = self.current
                assert row['offset'] == self.total_bytes
                name = str(relative(row['name']))
                self.file = (self.root / 'chunks' / name).open('rb')
                self.chunk_sha, self.chunk_bytes = hashlib.sha256(), 0
            block = self.file.read(1024 * 1024 if remaining < 0 else remaining)
            if not block:
                self.file.close()
                self.file = None
                assert self.chunk_bytes == self.current['size']
                assert self.chunk_sha.hexdigest() == self.current['sha256']
                self.verified_chunks.append(self.current)
                continue
            self.chunk_sha.update(block)
            self.total_sha.update(block)
            self.chunk_bytes += len(block)
            self.total_bytes += len(block)
            pieces.append(block)
            if remaining > 0:
                remaining -= len(block)
        return b''.join(pieces)

def archive_stream(root, manifest, index):
    expected = {entry['path']: entry for entry in manifest['entries']}
    reader = ChunkReader(root, index)
    seen = set()
    with tarfile.open(fileobj=reader, mode='r|*') as archive:
        for member in archive:
            name = str(relative(member.name))
            assert name in expected and name not in seen
            seen.add(name)
            entry = expected[name]
            if entry['type'] == 'file':
                assert member.isfile() and member.size == entry['size']
                h = hashlib.sha256()
                with archive.extractfile(member) as data:
                    for block in iter(lambda: data.read(1024 * 1024), b''):
                        h.update(block)
                assert h.hexdigest() == entry['sha256']
            elif entry['type'] == 'directory':
                assert member.isdir()
            else:
                assert member.issym() and member.linkname == entry['target']
    while reader.read(1024 * 1024):
        pass
    assert seen == set(expected)
    assert reader.total_bytes == index['archive_bytes']
    assert reader.total_sha.hexdigest() == index['archive_sha256']
    assert len(reader.verified_chunks) == len(index['chunks'])
    return dict(archive_sha256=reader.total_sha.hexdigest(), archive_bytes=reader.total_bytes,
                tar_member_count=len(seen), chunks=reader.verified_chunks)

def output_allowed(path):
    path = Path(path)
    if '..' in path.parts:
        return False
    roots = [PREP, A / 'agents/C_final48_independent_audits_v1']
    return any(path.is_relative_to(root) and path.resolve().is_relative_to(root.resolve()) for root in roots)

def load_strict():
    spec = importlib.util.spec_from_file_location('C_final48_exact_strict', R / 'tools/stage2_strict.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def point_audit(point, request, strict):
    cohort = point['cohort']
    row = request['consumed'][cohort]
    result_path = R / 'analysis' / (cohort + '.RESULT.json')
    result = rd(result_path)
    state = result['state']
    assert state in [PASS, NEGATIVE]
    assert result['uuid'] == row['uuid'] and row['charged'] == 1
    assert result['scientific_role'] == 'STAGEII_REMAINING48_AUTHORIZED_CH'
    assert result['input_digest'] == point['input_digest'] and result['profile'] == point['profile']
    spec_path = R / 'control/specs' / (cohort + '.json')
    spec = rd(spec_path)
    assert sha(spec_path) == point['spec_sha256'] == request['admitted_specs'][cohort]
    assert spec['approved_contract_commit'] == '5f67b4d6b94568a9f1acc80c3e56736bd81e4753'
    assert spec['core_commit'] == '9eedb3131937748f0492fa83aad37d3691118d70'
    assert spec['framework_commit'] == '02775fd795cde5aae1480d81cee6eb481d0a08f4'
    assert spec['binary_sha256'] == '02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
    assert sha(spec['input_binding_path']) == spec['input_binding_sha256']
    for record in spec['configs']:
        assert sha(record['path']) == record['sha256']
    for record in spec['runtime_files']:
        assert sha(record['actual_realpath']) == record['sha256']
    output = R / 'DTC/run/results' / row['uuid']
    intent_path = R / 'control/qualification_ledger' / (cohort + '.INTENT.json')
    done_path = intent_path.with_name(cohort + '.DONE.json')
    intent, done = rd(intent_path), rd(done_path)
    assert sha(intent_path) == row['intent_sha256']
    assert intent['uuid'] == done['uuid'] == result['uuid']
    assert done == row['execution_receipt'] == rd(output / 'NATIVE_EXIT.json')
    assert done['new_attempt_consumed'] == 1 and done['automatic_retry'] is False
    assert done['source_disposition'] == 'SOURCE_KEEP'
    pid_path = output / 'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    pid = rd(pid_path) if pid_path.exists() else None
    assert not pid or not live(pid), 'NEVER_READ_LIVE_RAW'
    raw_path = output / 'raw.log.gz'
    assert sha(raw_path) == done['raw_sha256']
    plain_sha, plain_bytes, last_cycle = hashlib.sha256(), 0, None
    with gzip.open(raw_path, 'rb') as raw:
        for line in raw:
            plain_sha.update(line)
            plain_bytes += len(line)
            match = re.match(rb'^gpu_tot_sim_cycle\s*=\s*([0-9]+)\s*$', line)
            if match:
                last_cycle = int(match.group(1))
    assert plain_sha.hexdigest() == done['raw_uncompressed_sha256']
    assert plain_bytes == done['raw_uncompressed_bytes']
    if state == PASS:
        assert pid and done['native_simulator_observed']
        assert done['stop_reason'] is None and done['launcher_wait_returncode'] == 0
        # Exact qualified strict implementation; only closed sources are read.
        computed = strict.terminal(cohort)
        assert computed == rd(output / 'L2_STRICT.json') == result['proof']
        assert result['cycles'] == last_cycle == computed['cycles']
        assert computed['performance_accepted'] is True
        assert computed['instructions'] == spec['expected']['instructions']
        assert computed['CTA'] == spec['expected']['CTA']
        assert computed['kernel_count'] == spec['expected']['kernels']
    else:
        assert done['stop_reason'] or done['launcher_wait_returncode']
        assert result['cycles'] is None and result['proof']['performance_accepted'] is False
        assert result['proof']['accepted_cycles'] is None
    receipt = result['archive']['receipt']
    archive_root = Path(receipt['target_mount_path'])
    manifest, index = rd(archive_root / 'SOURCE_MANIFEST.json'), rd(archive_root / 'ARCHIVE_INDEX.json')
    commit, proof = rd(archive_root / 'COMMIT.json'), rd(archive_root / 'RESTORE_VERIFIED_NATIVE_TARGET.json')
    assert receipt == rd(archive_root / 'RECEIPT.json')
    assert sha(archive_root / 'SOURCE_MANIFEST.json') == commit['manifest_sha256'] == receipt['manifest_sha256']
    assert sha(archive_root / 'ARCHIVE_INDEX.json') == commit['archive_index_sha256']
    assert index['archive_sha256'] == receipt['archive_sha256']
    assert receipt['source_disposition'] == 'SOURCE_KEEP' and receipt['source_release_bytes'] == 0
    assert receipt['scientific_acceptance_granted_by_archive'] is False
    mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(archive_root)], text=True))['filesystems'][0]
    assert mount['fstype'] == 'fuse.sshfs' and mount['source'] == 'admin-wcx@10.208.130.164:/home/shared'
    restore = Path(receipt['native_restore'])
    assert output.stat().st_dev == restore.stat().st_dev == R.stat().st_dev == 2128
    typed = typed_tree(output, restore, manifest, proof)
    assert typed['type_counts'] == dict(file=receipt['regular_files'], directory=receipt['directories'], symlink=receipt['symlinks'])
    stream = archive_stream(archive_root, manifest, index)
    return dict(cohort=cohort, uuid=result['uuid'], program=point['program'], input_digest=point['input_digest'],
                profile=point['profile'], state=state, accepted=state == PASS, cycles=result['cycles'],
                RESULT_path=str(result_path), RESULT_sha256=sha(result_path),
                strict_recomputed_exact=state == PASS, raw_gzip_sha256=sha(raw_path),
                raw_plain_sha256=plain_sha.hexdigest(), native_exit_sha256=sha(output / 'NATIVE_EXIT.json'),
                typed_recovery=typed, archive_stream=stream, missing_runtime_PID_on_negative=pid is None)

def provider_check(path, final=False):
    provider = rd(path)
    assert provider['source_qualified'] is True and provider['request'] == REQ
    assert provider['summary']['expected_CH'] == 48
    assert provider['summary']['core32_fixed_input_n'] == 32
    assert provider['summary']['expected_six_source_slots'] == 192
    assert provider['new_model_starts'] == provider['native_scientific_writes'] == 0
    assert provider['qualification_manifest']['sha256'] == 'ff7555aff68156598df69ef83a1d48750b29884383ba8362f91f04c6ab5a16ea'
    assert sha(provider['qualification_manifest']['path']) == provider['qualification_manifest']['sha256']
    assert sha(provider['manifest']['path']) == provider['manifest']['sha256']
    for record in provider['files']:
        assert sha(record['path']) == record['sha256']
    summary_file = next(record for record in provider['files'] if record['name'] == 'STAGEIIA_REMAINING48_SUMMARY.json.gz')
    assert json.loads(gzip.decompress(Path(summary_file['path']).read_bytes())) == provider['summary']
    if final:
        summary = provider['summary']
        assert provider['all_registered48_terminal_verified'] and summary['all_registered48_terminal_verified']
        assert summary['accepted_CH'] + summary['archived_negative_CH'] == 48
        assert summary['verification_hold'] == summary['await_result'] == summary['registered_remaining'] == 0
        assert summary['registered_consumed'] == 48
    return provider

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['gate', 'subset', 'final'], default='gate')
    parser.add_argument('--cohort', action='append', default=[])
    parser.add_argument('--provider', type=Path, default=PROVIDER)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    contract = rd(PREP / 'FINAL_AUDIT_CONTRACT.json')
    assert sha(__file__) == contract['validator_sha256']
    assert sha(R / 'control/EXECUTION_PLAN.json') == PLAN_SHA
    assert sha(R / 'control/REGISTRY_REQUEST_CANDIDATE.json') == CANDIDATE_SHA
    plan, matrix, registry = rd(R / 'control/EXECUTION_PLAN.json'), rd(R / 'control/MATRIX.json'), rd(REGISTRY)
    assert len(plan['source_pins']) == 122
    assert all(sha(pin['path']) == pin['sha256'] for pin in plan['source_pins'])
    request = registry['registered_future_requests'][REQ]
    candidate = rd(R / 'control/REGISTRY_REQUEST_CANDIDATE.json')
    assert all(request[key] == value for key, value in candidate.items() if key not in ['consumed', 'remaining', 'state'])
    assert sha(PREP / 'OLD_DTC_IDENTITIES_BEFORE_NEW48.fixed.json') == contract['old_DTC_baseline_sha256']
    states, active = {}, []
    for point in matrix['points']:
        cohort = point['cohort']
        path = R / 'analysis' / (cohort + '.RESULT.json')
        if path.exists():
            try:
                states[cohort] = rd(path)['state']
            except (FileNotFoundError, json.JSONDecodeError):
                pass  # An exclusive writer not yet flushed is still pending.
        row = request['consumed'].get(cohort)
        if row:
            pid_path = R / 'DTC/run/results' / row['uuid'] / 'NATIVE_SIMULATOR_PID_AND_MAPS.json'
            if pid_path.exists() and live(rd(pid_path)):
                active.append(cohort)
    gate = eligibility(matrix['points'], request, states, active)
    tag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = args.output_dir or PREP / 'runs' / (args.mode + '_' + tag)
    assert output_allowed(out) and not out.exists()
    out.mkdir(parents=True)
    put(out / 'ELIGIBILITY.json', gate)
    if args.mode == 'gate' or args.mode == 'final' and not gate['ready_for_expensive_final_audit']:
        put(out / 'STATUS.json', dict(status='READY_FOR_FINAL_AUDIT_NOT_YET_AUDITED' if gate['ready_for_expensive_final_audit'] else 'PENDING_ALL48_TERMINAL', mode=args.mode, live_raw_read=False, final_review_complete=False))
        print(json.dumps(dict(output=str(out), gate=gate, final_review_complete=False)))
        if args.mode == 'final':
            raise SystemExit(2)  # Pending never looks like successful final review.
        return
    if args.mode == 'subset':
        assert args.cohort and len(set(args.cohort)) == len(args.cohort)
        selected = [point for point in matrix['points'] if point['cohort'] in args.cohort]
        assert len(selected) == len(args.cohort)
        assert all(states.get(point['cohort']) == PASS and point['cohort'] not in active for point in selected)
    else:
        selected = matrix['points']
        provider = provider_check(args.provider, final=True)
        put(out / 'PROVIDER.fixed.json', provider)
    try:
        old = rd(PREP / 'OLD_DTC_IDENTITIES_BEFORE_NEW48.fixed.json')
        assert all(value == {key: registry['registered_future_requests'][name].get(key) for key in ['budget', 'remaining', 'consumed']} for name, value in old.items())
        qids = [row['uuid'] for row in request['consumed'].values()]
        assert len(qids) == len(set(qids))
        others = {row['uuid'] for name, req in registry['registered_future_requests'].items() if name != REQ and isinstance(req.get('consumed'), dict) for row in req['consumed'].values() if isinstance(row, dict) and 'uuid' in row}
        assert not set(qids) & others
        strict, rows = load_strict(), []
        for point in selected:
            rows.append(point_audit(point, request, strict))
            put(out / 'LIFECYCLE_PROGRESS.json', dict(mode=args.mode, completed=len(rows), expected=len(selected), rows=rows, final_review_complete=False))
        final = args.mode == 'final'
        math_report = None
        if final:
            helper = PREP / 'APPROVED_CYCLE_AUDIT_SOURCE.py'
            assert sha(helper) == HELPER_SHA
            math_dir = out / 'reviewed_integer_recomputation'
            subprocess.run([sys.executable, '-B', str(helper), '--provider', str(out / 'PROVIDER.fixed.json'), '--output-dir', str(math_dir)], check=True, capture_output=True, text=True)
            math_report = json.loads(gzip.decompress((math_dir / 'AUDIT.json.gz').read_bytes()))
            assert math_report['status'] == 'PASS'
            assert math_report['new48_raw_cycle_endpoints_rechecked'] == sum(row['accepted'] for row in rows)
            by_uuid = {row['uuid']: row for row in rows if row['accepted']}
            for source in math_report['raw_sources']:
                if source['role'] == 'STAGEII_REMAINING48_AUTHORIZED_CH':
                    point = by_uuid[source['uuid']]
                    assert source['source_RESULT_sha256'] == point['RESULT_sha256'] and source['cycles'] == point['cycles']
            assert math_report['accepted_slots_rechecked'] == 144 + len(by_uuid)
        put(out / 'REVIEW.json', dict(validator_sha256=sha(__file__), execution_plan_sha256=PLAN_SHA, registry_candidate_sha256=CANDIDATE_SHA, status='PASS_ALL48_INDEPENDENT_LIFECYCLE_AND_REVIEWED_INTEGER_STATISTICS' if final else 'PASS_ACCEPTED_SUBSET_QUALIFICATION_NOT_FINAL', mode=args.mode, rows=rows, accepted=sum(row['accepted'] for row in rows), archived_negative=sum(not row['accepted'] for row in rows), whole48_independent_automated_review_complete=final, all48_accepted_data_available=final and all(row['accepted'] for row in rows), no_live_raw_read=True, model_or_control_actions=0, reviewed_integer_recomputation=math_report and dict(accepted_slots=math_report['accepted_slots_rechecked'], common_both_F_n=math_report['common_both_F_n'], source_sha256=HELPER_SHA), limitations=['A final narrative/mechanism/cost and Git publication signoff remains DTC-MAIN responsibility.','The statistics helper is source-reviewed Root Fraction algorithm executed independently into this C output; no B formula implementation imported.','Accepted negatives stay nonperformance; full32 claims require32completeaccepted sixcell inputs.']))
        print(json.dumps(dict(output=str(out), mode=args.mode, completed=len(rows), final_review_complete=final)))
    except Exception:
        put(out / 'HOLD.json', dict(status='HOLD_PRESERVE_ALL_EVIDENCE_NO_MODEL_RETRY', mode=args.mode, traceback=traceback.format_exc(), final_review_complete=False, model_actions=0))
        raise

if __name__ == '__main__':
    main()
