"""Short Collect SOURCE_KEEP copy and typed native restore.

This module never allocates a science UUID or starts a model. A caller must
provide a closed, registered identity. Old Oracle cohorts are refused.
"""
import fcntl
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import tarfile
from pathlib import Path

ROOT = Path('/root/data/dtc_short_collect_native_discovery10_v1_20261109')
NAS = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_short_collect_native_discovery10_v1/results')
OLD = Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_outbox.py')
FUSE_SOURCE = 'admin-wcx@10.208.130.164:/home/shared'
MIB = 1024 ** 2


def need(ok, code):
    if not ok:
        raise RuntimeError(code)


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(MIB), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def primitive():
    spec = importlib.util.spec_from_file_location('short_collect_pinned_outbox', OLD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    need(digest(OLD) == 'b2bac008c8de73d3f6e7344129f094cd073d19d1572005374dc067fb2077e229',
         'OUTBOX_PRIMITIVE_PIN')
    return m


def libraries():
    return primitive().libraries()


def strict_module():
    path = Path(__file__).with_name('mechanism_strict.py')
    spec = importlib.util.spec_from_file_location('short_collect_evidence_strict', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_manifest(intent, done, *, root=ROOT, nas=NAS):
    """Full closed source selector; no missing or altered member is synthesized."""
    root, nas = Path(root), Path(nas)
    need(intent['request'] == done['request'] and intent['cohort'] == done['cohort'] and
         intent['uuid'] == done['uuid'], 'CLOSED_IDENTITY_JOIN')
    need(not intent['cohort'].startswith('E2-DTCORACLE-'), 'OLD_ORACLE_COHORT_FORBIDDEN')
    src = Path(intent['output'])
    need(src == root / 'DTC/run/results' / intent['uuid'], 'EXACT_NEW_SOURCE_ROOT')
    need(read(src / 'NATIVE_EXIT.json') == done and done['new_attempt_consumed'] == 1 and
         done['automatic_retry'] is False, 'CLOSED_ONE_USE_RECEIPT')
    pid_file = src / 'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    if pid_file.exists():
        need(done['native_simulator_observed'] is True, 'PID_WITHOUT_NATIVE')
        pid = read(pid_file)
        proc = Path('/proc') / str(pid['pid'])
        if proc.exists():
            ticks = int((proc / 'stat').read_text().rsplit(')', 1)[1].split()[19])
            need(ticks != pid['start_ticks'], 'ACTUAL_NATIVE_STILL_LIVE')
    else:
        need(done['native_simulator_observed'] is False and
             (done['stop_reason'] is not None or done['launcher_wait_returncode'] != 0),
             'NATURAL_POSITIVE_REQUIRES_PID')
    f, _ = libraries()
    entries = []
    for path in [src, *sorted(src.rglob('*'))]:
        s = path.lstat()
        row = f.ident(s)
        row['path'] = path.relative_to(src).as_posix()
        row['type'] = ('directory' if stat.S_ISDIR(s.st_mode) else
                       'file' if stat.S_ISREG(s.st_mode) else
                       'symlink' if stat.S_ISLNK(s.st_mode) else 'unsupported')
        need(row['type'] != 'unsupported', 'UNSUPPORTED_SOURCE_MEMBER')
        if row['type'] == 'file':
            row['sha256'] = f.file_sha(path)
        if row['type'] == 'symlink':
            row['target'] = os.readlink(path)
            need(row['path'] == 'perf_counter.csv.gz' and '/' not in row['target'] and
                 row['target'].startswith('perf_counter_') and row['target'].endswith('.csv.gz') and
                 (src / row['target']).is_file() and not (src / row['target']).is_symlink(),
                 'SYMLINK_TYPE_SCOPE')
        entries.append(row)
    selector = hashlib.sha256(canon(entries)).hexdigest()
    txid = hashlib.sha256(canon(dict(request=intent['request'], cohort=intent['cohort'],
                                    uuid=intent['uuid'], selector_sha256=selector,
                                    source_root=str(src), destination=str(nas)))).hexdigest()
    strict_path = src / 'MECHANISM_STRICT.json'
    strict = read(strict_path) if strict_path.exists() else {}
    qualified = (strict.get('status') == 'NATURAL_STRICT_ACCEPTED' and
                 strict.get('request') == intent['request'] and
                 strict.get('cohort') == intent['cohort'] and
                 strict.get('uuid') == intent['uuid'] and
                 strict.get('raw_sha256') == done['raw_sha256'])
    natural = (done['stop_reason'] is None and done['launcher_wait_returncode'] == 0 and
               done['native_simulator_observed'] is True)
    if natural:
        need(qualified, 'NATURAL_POSITIVE_REQUIRES_STRICT')
        if root == ROOT:
            mechanism = strict_module()
            spec = read(root / 'control/specs' / (intent['cohort'] + '.json'))
            domain = read(spec['input_binding_path'])['qualification']
            need(strict == mechanism.closed(spec, intent, done, src, domain),
                 'STRICT_PROOF_RECOMPUTE_MISMATCH')
    return dict(schema='DTC_SHORT_COLLECT_TYPED_NATIVE_EVIDENCE_V1', request=intent['request'],
                cohort=intent['cohort'], uuid=intent['uuid'], project='DTC', txid=txid,
                source_root=str(src), selector_sha256=selector, entries=entries,
                reused_objects={}, source_disposition='SOURCE_KEEP',
                scientific_status='NATURAL_STRICT_ACCEPTED' if qualified else 'STOP_UNACCEPTED',
                native_execution_receipt_sha256=digest(src / 'NATIVE_EXIT.json'),
                source_filesystem_identity=dict(host=os.uname().nodename,
                    mount_namespace=os.readlink('/proc/self/ns/mnt'), device=src.stat().st_dev),
                persistent164_root=str(nas / intent['cohort'] / txid).replace('/root/share/mnt164', '/home/shared', 1))


def gate(reservation=0):
    need(ROOT.stat().st_dev == 2128 and os.uname().nodename == 'huangrulin-sshfs-174',
         'NATIVE_174_IDENTITY')
    mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', '/root/share/mnt164'], text=True))['filesystems'][0]
    need(mount['fstype'] == 'fuse.sshfs' and mount['source'] == FUSE_SOURCE, 'TRUE164_MOUNT')
    return primitive().gate(reservation)


def verify(bundle, manifest, restore):
    """Read back committed true164 bytes and typed native ext4 restoration."""
    f, v = libraries()
    bundle, restore = Path(bundle), Path(restore)
    need(bundle == NAS / manifest['cohort'] / manifest['txid'], 'ARCHIVE_NAMESPACE')
    need(manifest['schema'] == 'DTC_SHORT_COLLECT_TYPED_NATIVE_EVIDENCE_V1' and
         manifest['source_disposition'] == 'SOURCE_KEEP', 'ARCHIVE_TYPE')
    need(read(bundle / 'SOURCE_MANIFEST.json') == manifest, 'ARCHIVE_MANIFEST_JOIN')
    index = f.verify_archive(bundle, manifest)
    proof = f.check_native(restore, manifest)
    need(len(proof) == len(manifest['entries']), 'RESTORE_INVENTORY')
    return dict(archive_sha256=index['archive_sha256'], verified_entries=len(proof),
                source_disposition='SOURCE_KEEP', scientific_acceptance_granted_by_archive=False)


def archive(intent, done):
    """Only a closed request enters the new true164 namespace; no source deletion."""
    m = source_manifest(intent, done)
    source = Path(m['source_root'])
    raw_bytes = sum(r['size'] for r in m['entries'] if r['type'] == 'file')
    before = gate(raw_bytes + 16 * MIB)
    old = primitive()
    f, v = old.libraries()
    old.gate = gate
    target_lock = Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb')
    fcntl.flock(target_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    bundle = NAS / m['cohort'] / m['txid']
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / 'chunks').mkdir(exist_ok=True)
    v.exclusive_json(bundle / 'SOURCE_MANIFEST.json', m)
    for name, data in [('full_result_bundle.py', (old.BASELINE / 'full_result_bundle.py').read_bytes()),
                       ('v9_transaction.py', (old.BASELINE / 'v9_transaction.py').read_bytes()),
                       ('native_result.py', Path(__file__).read_bytes()),
                       ('RESULT_ENGINE_PIN.json', (old.ROOT / 'control/RESULT_ENGINE_PIN.json').read_bytes())]:
        path = bundle / name
        if path.exists():
            need(path.read_bytes() == data, 'ARCHIVE_TOOL_COLLISION')
        else:
            with path.open('xb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
    if not (bundle / 'COMMIT.json').exists():
        writer = old.RangeWriter(bundle, m, v, f)
        with tarfile.open(fileobj=writer, mode='w|', format=tarfile.PAX_FORMAT) as tar:
            for row in m['entries']:
                path = f.safe(m['source_root'], row['path'])
                info = tarfile.TarInfo(row['path'])
                info.uid, info.gid, info.mode = row['uid'], row['gid'], row['mode']
                info.mtime = row['mtime_ns'] // 10**9
                info.pax_headers = {'mtime': f"{row['mtime_ns']//10**9}.{row['mtime_ns']%10**9:09d}"}
                if row['type'] == 'directory':
                    info.type = tarfile.DIRTYPE
                    tar.addfile(info)
                elif row['type'] == 'symlink':
                    info.type = tarfile.SYMTYPE
                    info.linkname = row['target']
                    tar.addfile(info)
                else:
                    info.size = row['size']
                    with path.open('rb') as stream:
                        tar.addfile(info, stream)
        index = writer.finish()
        need(source_manifest(intent, done) == m, 'SOURCE_DRIFT_DURING_COPY')
        v.exclusive_json(bundle / 'ARCHIVE_INDEX.json', index)
        v.exclusive_json(bundle / 'COMMIT.json', dict(txid=m['txid'],
            manifest_sha256=hashlib.sha256(canon(m)).hexdigest(),
            archive_index_sha256=hashlib.sha256(canon(index)).hexdigest(),
            policy='EXCLUSIVE_CREATE_COMMIT_MARKER_LAST'))
    f.verify_archive(bundle, m)
    restore = ROOT / 'recovery' / m['txid']
    restore.parent.mkdir(exist_ok=True)
    if restore.exists():
        f.check_native(restore, m)
    else:
        f.restore(bundle, m, restore, v, gate=lambda: gate())
    proof = verify(bundle, m, restore)
    need(source_manifest(intent, done) == m, 'SOURCE_KEEP_DRIFT')
    return dict(schema='DTC_SHORT_COLLECT_ARCHIVE_RECEIPT_V1', request=m['request'],
                cohort=m['cohort'], uuid=m['uuid'], txid=m['txid'],
                true164_path=str(bundle), native_restore=str(restore),
                archive=proof, resources_before=before, source_disposition='SOURCE_KEEP',
                scientific_acceptance_granted_by_archive=False)
