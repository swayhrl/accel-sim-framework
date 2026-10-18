"""Small fail-closed V9 transaction primitives. No production source deletion API.

Target calls require exact immutable manifest/real mount; fixture-only release is
deliberately restricted to a marked temporary synthetic tree, with no retry API.
"""
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile
import time

CAP = 256 * 1024**2
RATE = 30 * 1024**2
REAL_MOUNT = ('/root/share/mnt164', 'admin-wcx@10.208.130.164:/home/shared', 'fuse.sshfs')
STATES = ['DISCOVERED', 'SOURCE_FROZEN', 'COPY_READY', 'ARCHIVE_STAGED',
          'ARCHIVE_VERIFIED', 'RESTORE_VERIFIED', 'RELEASE_ELIGIBLE', 'SOURCE_RELEASED']


class Hold(RuntimeError):
    pass


def require(ok, reason):
    if not ok:
        raise Hold(reason)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def relpath(name, root_ok=False):
    require(isinstance(name, str) and '\x00' not in name and '\\' not in name, 'invalid path')
    if root_ok and name == '.':
        return Path('.')
    p = PurePosixPath(name)
    require(name != '' and not p.is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')),
            'noncanonical relative path')
    require(p.as_posix() == name, 'path normalization changed')
    return Path(name)


def no_symlinks(path):
    p = Path(path).absolute()
    for q in [p, *p.parents]:
        if os.path.lexists(q):
            require(not q.is_symlink(), 'symlink traversal')
    return p


def identity(s):
    return dict(dev=s.st_dev, inode=s.st_ino, nlink=s.st_nlink, size=s.st_size,
                allocated=s.st_blocks * 512, uid=s.st_uid, gid=s.st_gid,
                mode=stat.S_IMODE(s.st_mode), mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)


def hash_file(path, expected=None, throttle=None):
    p = no_symlinks(path)
    before = p.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'file type/hardlink')
    if expected is not None:
        require(identity(before) == expected, 'source identity drift')
    h = hashlib.sha256()
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        require(identity(os.fstat(stream.fileno())) == identity(before), 'open identity drift')
        while True:
            data = stream.read(1024**2)
            if not data:
                break
            h.update(data)
            if throttle:
                throttle(len(data))
        require(identity(os.fstat(stream.fileno())) == identity(before), 'file changed during hash')
    require(identity(p.lstat()) == identity(before), 'path changed during hash')
    return h.hexdigest()


class Throttle:
    def __init__(self, rate=RATE):
        require(0 < rate <= RATE, 'rate exceeds contract')
        self.rate, self.start, self.total = rate, time.monotonic(), 0

    def __call__(self, size):
        self.total += size
        time.sleep(max(0, self.total / self.rate - (time.monotonic() - self.start)))


def floors(workspace, share, memory, staging=0):
    require(workspace >= 48 * 1024**3, 'workspace floor')
    require(share - staging >= 40 * 1024**3, 'Share floor including proposed stage')
    require(memory >= 64 * 1024**3, 'RAM floor')
    require(0 <= staging <= CAP, 'bridge >256MiB')


def mount_identity(root, observed=None):
    no_symlinks(root)
    if observed is None:
        observed = json.loads(subprocess.check_output(
            ['findmnt', '-J', '-T', str(root), '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
    require(tuple(observed[k] for k in ['target', 'source', 'fstype']) == REAL_MOUNT, 'wrong genuine164 mount')
    return observed


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def rename_noreplace(source, target):
    """Linux RENAME_NOREPLACE; unsupported filesystems HOLD, never os.replace.

    Caller keeps both paths under one verified transaction filesystem.
    """
    no_symlinks(source); no_symlinks(target)
    require(Path(source).parent.stat().st_dev == Path(target).parent.stat().st_dev, 'cross-filesystem finalization')
    libc = ctypes.CDLL(None, use_errno=True)
    require(hasattr(libc, 'renameat2'), 'RENAME_NOREPLACE unavailable')
    fn = libc.renameat2
    fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    fn.restype = ctypes.c_int
    if fn(-100, os.fsencode(source), -100, os.fsencode(target), 1):
        err = ctypes.get_errno()
        raise Hold('no-replace finalize: ' + os.strerror(err))
    fsync_dir(Path(target).parent)


def exclusive_json(path, value):
    p = no_symlinks(path)
    raw = canonical(value)
    if p.exists():
        require(p.read_bytes() == raw, 'immutable record mismatch')
        return digest(raw)
    tmp = p.with_name(p.name + '.writing')
    if tmp.exists():
        require(tmp.read_bytes() == raw, 'interrupted/corrupt immutable record; inspect required')
    else:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    rename_noreplace(tmp, p)
    return digest(raw)


def transaction_id(manifest):
    require(manifest['source_root'].startswith('/') and str(PurePosixPath(manifest['source_root'])) == manifest['source_root'], 'source root not canonical')
    require('..' not in PurePosixPath(manifest['source_root']).parts, 'source root traversal')
    require(manifest['source_frozen_commit'] and len(manifest['source_frozen_commit']) == 40, 'source commit')
    value = {k: manifest[k] for k in ['source_filesystem_identity', 'source_root', 'selector_sha256',
                                    'source_frozen_commit', 'genuine164_destination_root']}
    return digest(canonical(value))


def validate_manifest(manifest):
    require(manifest['selector_sha256'] == digest(canonical(manifest['files'])), 'selector SHA mismatch')
    paths = []
    for row in manifest['files']:
        relpath(row['relative_path']); paths.append(row['relative_path'])
        require(row['type'] == 'regular' and row['nlink'] == 1, 'symlink/hardlink policy refuses')
        require(len(row['sha256']) == 64 and row['size'] >= 0, 'file SHA/size')
        require(all(k in row for k in ['dev', 'inode', 'uid', 'gid', 'mode', 'mtime_ns', 'ctime_ns', 'allocated']), 'missing native metadata')
    require(len(set(paths)) == len(paths), 'duplicate manifest path')
    dirs = [r['relative_path'] for r in manifest['directories']]
    for d in dirs:
        relpath(d, root_ok=True)
    require(len(set(dirs)) == len(dirs) and '.' in dirs, 'directory manifest')
    require(not (set(paths) & (set(dirs) - {'.'})), 'file/directory collision')
    for p in paths:
        for parent in PurePosixPath(p).parents:
            require(parent.as_posix() in dirs, 'missing parent metadata')
    return transaction_id(manifest)


class Transaction:
    def __init__(self, base, manifest, *, fixture=False):
        self.base = no_symlinks(base)
        if fixture:
            fixture_root(self.base)
        else:
            mount_identity(self.base)
        self.manifest = manifest
        self.txid = validate_manifest(manifest)
        require(str(self.base) == manifest['genuine164_destination_root'], 'wrong destination identity')
        self.rows = {r['relative_path']: r for r in manifest['files']}
        self.partial = self.base / (self.txid + '.partial')
        self.final = self.base / self.txid
        if self.final.exists():
            require((self.final / 'manifest.json').read_bytes() == canonical(manifest), 'final manifest drift')
            self.work = self.final
        else:
            if not self.partial.exists():
                self.partial.mkdir(mode=0o700)
            self.work = self.partial
        (self.work / 'chunks').mkdir(exist_ok=True)
        (self.work / 'receipts').mkdir(exist_ok=True)
        exclusive_json(self.work / 'manifest.json', manifest)
        self.throttle = Throttle()

    def transition(self, state, evidence):
        require(state in STATES and state not in ['RELEASE_ELIGIBLE', 'SOURCE_RELEASED'], 'target cannot authorize release')
        existing = sorted((self.work / 'receipts').glob('*.json'))
        records = [json.loads(p.read_bytes()) for p in existing]
        if records and records[-1]['state'] == state:
            require(records[-1]['evidence'] == evidence, 'duplicate state evidence changed')
            return digest(existing[-1].read_bytes())
        expected = STATES[len(records)]
        require(state == expected, 'invalid transition')
        prior = digest(existing[-1].read_bytes()) if existing else None
        return exclusive_json(self.work / 'receipts' / ('%02d.json' % len(records)),
                              dict(txid=self.txid, state=state, previous_receipt_sha256=prior, evidence=evidence))

    def accept_chunk(self, relative_path, offset, bridge_file, expected_chunk_sha, *, txid, crash=None):
        require(txid == self.txid, 'mismatched txid')
        require(self.work != self.final, 'verified final archive refuses writes')
        relpath(relative_path); row = self.rows[relative_path]
        p = no_symlinks(bridge_file); size = p.stat().st_size
        require(0 <= offset and 0 < size <= CAP and offset + size <= row['size'], 'invalid chunk range/cap')
        require(p.stat().st_blocks * 512 <= CAP, 'allocated staging >256MiB')
        require(hash_file(p, throttle=self.throttle) == expected_chunk_sha, 'bridge chunk SHA')
        key = digest(relative_path.encode()) + ('.%016d' % offset)
        chunk = self.work / 'chunks' / key
        record = self.work / 'chunks' / (key + '.json')
        evidence = dict(txid=txid, relative_path=relative_path, offset=offset, size=size, sha256=expected_chunk_sha)
        if chunk.exists():
            require(chunk.stat().st_size == size and hash_file(chunk, throttle=self.throttle) == expected_chunk_sha, 'existing chunk corrupt')
        else:
            tmp = chunk.with_name(chunk.name + '.partial')
            require(not tmp.exists(), 'incomplete chunk requires bounded orphan reconciliation')
            with p.open('rb') as src, tmp.open('xb') as dst:
                for block in iter(lambda: src.read(1024**2), b''):
                    dst.write(block); self.throttle(len(block))
                dst.flush(); os.fsync(dst.fileno())
            require(hash_file(tmp, throttle=self.throttle) == expected_chunk_sha, 'partial chunk SHA')
            if crash == 'before_chunk_record':
                raise Hold('injected before durable chunk record')
            rename_noreplace(tmp, chunk)
        exclusive_json(record, evidence)
        if crash == 'after_chunk_record':
            raise Hold('injected after durable chunk record')
        return evidence

    def reconcile_partial_chunk(self, relative_path, offset, expected_chunk_sha, size):
        """Adopt only a complete orphan whose exact digest/size match pinned READY."""
        relpath(relative_path)
        require(relative_path in self.rows and size <= CAP, 'orphan range invalid')
        key = digest(relative_path.encode()) + ('.%016d' % offset)
        p = self.work / 'chunks' / (key + '.partial')
        require(p.exists() and p.stat().st_size == size and hash_file(p, throttle=self.throttle) == expected_chunk_sha,
                'orphan not complete/verified; HOLD for exact reset')
        rename_noreplace(p, p.with_name(key))

    def finalize(self):
        tree = self.work / 'tree'
        tree.mkdir(exist_ok=True)
        for d in sorted(self.manifest['directories'], key=lambda r: len(Path(r['relative_path']).parts)):
            (tree / relpath(d['relative_path'], root_ok=True)).mkdir(exist_ok=True)
        for name, row in self.rows.items():
            final = tree / relpath(name)
            if final.exists():
                require(final.stat().st_size == row['size'] and hash_file(final, throttle=self.throttle) == row['sha256'], 'existing final file differs')
                continue
            tmp = final.with_name(final.name + '.partial')
            require(not tmp.exists(), 'interrupted assembly requires exact orphan reconciliation')
            records = [json.loads(p.read_bytes()) for p in (self.work / 'chunks').glob('*.json')]
            records = sorted((r for r in records if r['relative_path'] == name), key=lambda r: r['offset'])
            offset = 0
            with tmp.open('xb') as out:
                for r in records:
                    require(r['txid'] == self.txid and r['offset'] == offset, 'chunk overlap/gap/txid')
                    key = digest(name.encode()) + ('.%016d' % r['offset'])
                    chunk = self.work / 'chunks' / key
                    require(hash_file(chunk, throttle=self.throttle) == r['sha256'] and chunk.stat().st_size == r['size'], 'chunk/record corruption')
                    with chunk.open('rb') as inp:
                        for data in iter(lambda: inp.read(1024**2), b''):
                            out.write(data); self.throttle(len(data))
                    offset += r['size']
                require(offset == row['size'], 'missing content')
                out.flush(); os.fsync(out.fileno())
            require(hash_file(tmp, throttle=self.throttle) == row['sha256'], 'assembled SHA')
            rename_noreplace(tmp, final)
        require({p.relative_to(tree).as_posix() for p in tree.rglob('*') if p.is_file()} == set(self.rows), 'unexpected archive file')
        if self.work == self.final:
            return self.final
        for row in self.rows.values():
            p = tree / row['relative_path']
            require(hash_file(p, throttle=self.throttle) == row['sha256'], 'final full manifest SHA')
        require(not os.path.lexists(self.final), 'existing destination')
        rename_noreplace(self.partial, self.final)
        self.work = self.final
        return self.final


def native_restore(archive_tree, manifest, destination):
    dst = no_symlinks(destination)
    require(not os.path.lexists(dst), 'restore destination already exists')
    fs = subprocess.check_output(['findmnt', '-n', '-o', 'FSTYPE', '-T', str(dst.parent)], text=True).strip()
    require('fuse' not in fs and 'sshfs' not in fs, 'SSHFS projection is not native metadata')
    validate_manifest(manifest)
    dst.mkdir(mode=0o700)
    throttle = Throttle()
    for d in sorted(manifest['directories'], key=lambda r: len(Path(r['relative_path']).parts)):
        (dst / relpath(d['relative_path'], root_ok=True)).mkdir(exist_ok=True)
    verified = []
    for row in manifest['files']:
        src = no_symlinks(Path(archive_tree) / relpath(row['relative_path']))
        require(hash_file(src, throttle=throttle) == row['sha256'], 'archive drift before restore')
        p = dst / row['relative_path']
        with src.open('rb') as inp, p.open('xb') as out:
            for b in iter(lambda: inp.read(1024**2), b''):
                out.write(b); throttle(len(b))
            out.flush(); os.fsync(out.fileno())
        os.chown(p, row['uid'], row['gid']); os.chmod(p, row['mode']); os.utime(p, ns=(row['mtime_ns'], row['mtime_ns']))
        s = p.lstat()
        require((s.st_uid, s.st_gid, stat.S_IMODE(s.st_mode), s.st_mtime_ns) ==
                (row['uid'], row['gid'], row['mode'], row['mtime_ns']), 'native metadata mismatch')
        require(hash_file(p, throttle=throttle) == row['sha256'], 'restore SHA')
        verified.append(row['relative_path'])
    for d in sorted(manifest['directories'], key=lambda r: len(Path(r['relative_path']).parts), reverse=True):
        p = dst / relpath(d['relative_path'], root_ok=True)
        os.chown(p, d['uid'], d['gid']); os.chmod(p, d['mode']); os.utime(p, ns=(d['mtime_ns'], d['mtime_ns']))
        s = p.lstat()
        require((s.st_uid, s.st_gid, stat.S_IMODE(s.st_mode), s.st_mtime_ns) == (d['uid'], d['gid'], d['mode'], d['mtime_ns']), 'directory metadata')
    return dict(status='RESTORE_VERIFIED', files=verified, numeric_metadata_verified=True, ctime='PROVENANCE_ONLY_NOT_RESTORABLE')


def fixture_root(path):
    p = no_symlinks(path)
    candidates = [q for q in [p, *p.parents] if q.name.startswith('ops_v9_fixture_')]
    require(len(candidates) == 1, 'fixture-only operation')
    root = candidates[0]
    require(root.parent == Path(tempfile.gettempdir()).resolve() and
            (root / 'SYNTHETIC_ONLY').read_bytes() == b'OPS_V9_SYNTHETIC_ONLY\n', 'not an authorized synthetic fixture')
    return root


def journal_append(path, record):
    with Path(path).open('ab') as f:
        f.write(canonical(record)); f.flush(); os.fsync(f.fileno())


def fixture_release(path, expected, sha256, journal, gates, crash=None):
    """ONLY synthetic fixtures; never wired to a production source command."""
    p = no_symlinks(path); root = fixture_root(p); fixture_root(journal)
    require(Path(journal).is_relative_to(root), 'journal outside fixture')
    require(gates['exact_user_permission'] and gates['target_restore_verified'], 'permission/restore withheld')
    require(not any(gates.get(k) for k in ['reader_pid', 'registry', 'scheduled_reader']), 'active/future reader')
    for fd in Path('/proc/self/fd').iterdir():
        try:
            require(os.readlink(fd) != str(p), 'active reader FD')
        except FileNotFoundError:
            pass
    floors(gates['workspace'], gates['share'], gates['memory'], gates.get('staging', 0))
    require(not Path(journal).exists(), 'existing journal: reconcile, never retry unlink')
    require(hash_file(p, expected) == sha256, 'current SHA differs')
    parent = p.parent.stat()
    journal_append(journal, dict(event='INTENT', txid=gates['txid'], path=str(p), identity=expected,
                                 source_sha256=sha256, target_proof=gates['target_proof'], parent=[parent.st_dev, parent.st_ino]))
    if crash == 'after_intent':
        raise Hold('injected after INTENT')
    directory = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        require((os.fstat(directory).st_dev, os.fstat(directory).st_ino) == (parent.st_dev, parent.st_ino), 'parent drift')
        require(hash_file(p, expected) == sha256, 'identity changed before unlink')
        require(identity(os.stat(p.name, dir_fd=directory, follow_symlinks=False)) == expected, 'path drift before unlink')
        os.unlink(p.name, dir_fd=directory); os.fsync(directory)
        if crash == 'after_unlink':
            raise Hold('injected after unlink before DONE')
        journal_append(journal, dict(event='DONE', txid=gates['txid'], path=str(p)))
    finally:
        os.close(directory)
    if crash == 'after_done':
        raise Hold('injected after DONE')


def fixture_reconcile(path, journal):
    fixture_root(path); fixture_root(journal)
    records = [json.loads(line) for line in Path(journal).read_bytes().splitlines()]
    require(records and records[0]['event'] == 'INTENT', 'invalid release journal')
    require(all(r['path'] == str(path) and r['txid'] == records[0]['txid'] for r in records), 'journal identity mismatch')
    exists = os.path.lexists(path)
    done = records[-1]['event'] == 'DONE'
    return dict(status=('RELEASED_NO_RETRY' if done and not exists else
                        'HOLD_PATH_REAPPEARED' if done else
                        'HOLD_INTENT_PRESENT_NO_AUTO_UNLINK' if exists else 'UNCERTAIN_MANUAL_READBACK_REQUIRED'),
                path_exists=exists, unlink_performed_by_reconcile=False)


def space_accounting(batch_before, batch_after, endpoint_before, endpoint_after):
    return dict(immediate_batch_gain_bytes=batch_after - batch_before,
                long_window_endpoint_change_bytes=endpoint_after - endpoint_before)
