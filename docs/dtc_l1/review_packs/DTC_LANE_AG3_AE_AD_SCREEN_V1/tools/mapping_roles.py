"""AG2 CPU-qualified mapping validator. No process creation or dispatch API.

Linux x86-64, same mount namespace, exact file-backed maps; version 1.
Caller must stop its owned target across the complete maps read and validation.
This module is a candidate production parser, not a simulator executor.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import time

ROLES = {'ELF_EXECUTABLE', 'ELF_INTERPRETER', 'ELF_SHARED_OBJECT',
         'LOADER_DATA_CACHE', 'KNOWN_READ_ONLY_DATA'}
PSEUDO = {'[heap]', '[stack]', '[vvar]', '[vvar_vclock]', '[vdso]', '[vsyscall]'}
CACHE = '/etc/ld.so.cache'

class Reject(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise Reject(reason)

def sha(path):
    with open(path, 'rb') as f:
        digest = hashlib.sha256()
        for data in iter(lambda: f.read(65536), b''):
            digest.update(data)
        return digest.hexdigest()

def identity(s):
    return dict(device=s.st_dev, major=os.major(s.st_dev), minor=os.minor(s.st_dev),
                inode=s.st_ino, size=s.st_size, mode=s.st_mode, uid=s.st_uid,
                gid=s.st_gid, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns,
                nlink=s.st_nlink)

def digest_fd(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    h = hashlib.sha256()
    total = 0
    while True:
        data = os.read(fd, 65536)
        if not data:
            break
        total += len(data)
        require(total <= 32 * 1024 * 1024, 'FILE_TOO_LARGE_FOR_CPU_CONTRACT')
        h.update(data)
    return h.hexdigest()

def file_record(path):
    """Open canonical name without following a final symlink; hash under fstat checks."""
    require(os.path.isabs(path) and str(Path(path).resolve()) == path,
            'NON_CANONICAL_PATH:' + path)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            before = identity(os.fstat(fd))
            require(stat.S_ISREG(before['mode']), 'NOT_REGULAR_FILE:' + path)
            header = os.pread(fd, 64, 0)
            digest = digest_fd(fd)
            after = identity(os.fstat(fd))
            named = identity(os.stat(path, follow_symlinks=False))
            require(before == after == named, 'TOCTOU_IDENTITY_CHANGED:' + path)
            require(str(Path(path).resolve()) == path, 'TOCTOU_PATH_CHANGED:' + path)
        finally:
            os.close(fd)
    except OSError as exc:
        raise Reject('FILE_IDENTITY_UNCONFIRMABLE:' + path + ':' + str(exc.errno)) from exc
    elf = header[:4] == b'\x7fELF'
    elf_type = None
    if elf:
        require(len(header) == 64 and header[4:6] == b'\x02\x01', 'UNSUPPORTED_ELF')
        elf_type = struct.unpack_from('<H', header, 16)[0]
        require(struct.unpack_from('<H', header, 18)[0] == 62, 'UNSUPPORTED_ELF_MACHINE')
    return dict(path=path, identity=before, sha256=digest,
                kind='ELF' if elf else 'NON_ELF', elf_type=elf_type,
                header_hex=header[:20].hex())

def check_role(entry, actual):
    role = entry.get('role')
    require(role in ROLES, 'MISSING_OR_UNKNOWN_ROLE:' + entry['path'])
    if role.startswith('ELF_'):
        require(actual['kind'] == 'ELF' and actual['elf_type'] in (2, 3),
                'ROLE_REQUIRES_ELF:' + entry['path'])
        if role in ('ELF_INTERPRETER', 'ELF_SHARED_OBJECT'):
            require(actual['elf_type'] == 3, 'ROLE_REQUIRES_ET_DYN:' + entry['path'])
    else:
        require(actual['kind'] == 'NON_ELF', 'ELF_MASQUERADING_AS_DATA:' + entry['path'])
        if role == 'LOADER_DATA_CACHE':
            require(entry['path'] == CACHE, 'CACHE_ROLE_EXACT_PATH_REQUIRED')
            require(bytes.fromhex(actual['header_hex']).startswith(b'glibc-ld.so.cache'),
                    'UNSUPPORTED_CACHE_FORMAT')
        else:
            require(bool(entry.get('data_purpose')), 'READ_ONLY_DATA_PURPOSE_REQUIRED')

def verify_file(entry):
    require(entry.get('role') in ROLES, 'MISSING_OR_UNKNOWN_ROLE:' + entry['path'])
    current = file_record(entry['path'])
    check_role(entry, current)
    require(current['identity'] == entry['identity'], 'FROZEN_FILE_IDENTITY_MISMATCH:' + entry['path'])
    require(current['sha256'] == entry['sha256'], 'FROZEN_FILE_SHA_MISMATCH:' + entry['path'])
    return current

def freeze(specs, executable, interpreter):
    entries = []
    for path, role, source in specs:
        canonical = str(Path(path).resolve(strict=True))
        e = dict(file_record(canonical), role=role, source=source,
                 frozen_monotonic_ns=time.monotonic_ns(), frozen_unix_ns=time.time_ns(),
                 presence=('REQUIRED_EARLY_THEN_OPTIONAL_AFTER_VERIFIED_UNMAP'
                           if role == 'LOADER_DATA_CACHE' else 'REGISTERED_EXACT_FILE'),
                 disappearance='ONLY_AFTER_IDENTITY_CONFIRMED_IN_STOPPED_COMPLETE_SNAPSHOT')
        check_role(e, e)
        entries.append(e)
    require(len({e['path'] for e in entries}) == len(entries), 'DUPLICATE_PATH')
    manifest = dict(version='AG2_MAPPING_ROLE_V1', execution_authority=False,
                    target=str(Path(executable).resolve()), interpreter=str(Path(interpreter).resolve()),
                    cache_mode='PRESENT_REQUIRED_EARLY', no_cache_host_qualification='NOT_QUALIFIED_STOP',
                    frozen_monotonic_ns=time.monotonic_ns(), files=entries)
    validate_manifest(manifest)
    return manifest

def validate_manifest(m):
    require(m['version'] == 'AG2_MAPPING_ROLE_V1' and m['execution_authority'] is False,
            'MANIFEST_VERSION_OR_AUTHORITY')
    files = m['files']
    require(len({e['path'] for e in files}) == len(files), 'DUPLICATE_PATH')
    registry = {e['path']: e for e in files}
    require(m.get('cache_mode') == 'PRESENT_REQUIRED_EARLY', 'NO_CACHE_MODE_NOT_QUALIFIED')
    require(CACHE in registry, 'CACHE_REGISTRATION_MISSING')
    require(registry[CACHE]['role'] == 'LOADER_DATA_CACHE', 'CACHE_ROLE_REQUIRED')
    require(registry.get(m['target'], {}).get('role') == 'ELF_EXECUTABLE', 'EXECUTABLE_ROLE_REQUIRED')
    require(registry.get(m['interpreter'], {}).get('role') == 'ELF_INTERPRETER', 'INTERPRETER_ROLE_REQUIRED')
    require(sum(e.get('role') == 'ELF_EXECUTABLE' for e in files) == 1, 'EXACTLY_ONE_EXECUTABLE')
    require(sum(e.get('role') == 'ELF_INTERPRETER' for e in files) == 1, 'EXACTLY_ONE_INTERPRETER')
    for e in files:
        require(bool(e.get('source')) and bool(e.get('frozen_monotonic_ns'))
                and bool(e.get('presence')) and bool(e.get('disappearance')), 'ROLE_PROVENANCE_REQUIRED')
        verify_file(e)
    return registry

def parse_maps(text):
    """Every line parsed; only named Linux anonymous/pseudo maps lack file roles."""
    rows = []
    for line in text.splitlines():
        parts = line.split(None, 5)
        require(len(parts) >= 5, 'MALFORMED_MAPS_LINE')
        interval, perms, offset, dev, inode = parts[:5]
        name = parts[5] if len(parts) == 6 else ''
        require(re.fullmatch(r'[0-9a-f]+-[0-9a-f]+', interval) is not None, 'BAD_MAP_INTERVAL')
        require(re.fullmatch(r'[r-][w-][x-][ps]', perms) is not None, 'BAD_MAP_PERMISSIONS')
        require(re.fullmatch(r'[0-9a-f]+:[0-9a-f]+', dev) is not None, 'BAD_MAP_DEVICE')
        a, b = (int(x, 16) for x in interval.split('-'))
        major, minor = (int(x, 16) for x in dev.split(':'))
        row = dict(start=a, end=b, permissions=perms, offset=int(offset, 16),
                   major=major, minor=minor, inode=int(inode), path=name)
        require(a < b, 'EMPTY_MAP')
        if name.startswith('/'):
            require(not name.endswith(' (deleted)'), 'DELETED_MAPPING_IDENTITY_UNCONFIRMABLE')
            name = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1], 8)), name)
            row['path'] = name
            require(row['inode'] != 0, 'FILE_MAPPING_ZERO_INODE')
            row['file_backed'] = True
        else:
            require((not name or name in PSEUDO) and row['inode'] == 0,
                    'UNKNOWN_NONFILE_MAPPING:' + name)
            row['file_backed'] = False
        rows.append(row)
    require(bool(rows), 'EMPTY_MAPS_SNAPSHOT')
    return rows

def validate_snapshot(text, registry):
    rows = parse_maps(text)
    observed = {}
    for r in rows:
        if not r['file_backed']:
            continue
        path = r['path']
        require(path in registry, 'UNREGISTERED_FILE_MAPPING:' + path)
        e = registry[path]
        require(e.get('role') in ROLES, 'MISSING_OR_UNKNOWN_ROLE:' + path)
        s = e['identity']
        require((r['major'], r['minor'], r['inode']) == (s['major'], s['minor'], s['inode']),
                'MAP_DEVICE_INODE_MISMATCH:' + path)
        if not e['role'].startswith('ELF_'):
            require('w' not in r['permissions'] and 'x' not in r['permissions'], 'DATA_MAPPING_NOT_READ_ONLY:' + path)
        if path not in observed:
            observed[path] = verify_file(e)
    return dict(status='PASS_COMPLETE_STOPPED_SNAPSHOT', rows=len(rows), files=observed)

class Sequence:
    def __init__(self, manifest):
        self.registry = validate_manifest(manifest)
        self.target = manifest['target']
        self.interpreter = manifest['interpreter']
        self.ever = set()
        self.previous = set()
        self.cache_disappearances = 0
        self.snapshots = 0

    def observe(self, text, exe):
        require(exe == self.target, 'PROC_EXE_IDENTITY_MISMATCH')
        result = validate_snapshot(text, self.registry)
        paths = set(result['files'])
        require(self.target in paths and self.interpreter in paths, 'EXECUTABLE_OR_INTERPRETER_MAPPING_MISSING')
        if CACHE in self.previous and CACHE not in paths:
            # Prior stopped snapshot already confirmed the exact cache content+inode.
            verify_file(self.registry[CACHE])
            self.cache_disappearances += 1
        self.ever |= paths
        self.previous = paths
        self.snapshots += 1
        return result

    def close(self, natural_exit0):
        require(natural_exit0, 'CPU_PROBE_NOT_NATURAL_EXIT0')
        require(CACHE in self.ever, 'EARLY_CACHE_NOT_OBSERVED_QUALIFICATION_PARTIAL')
        require(self.cache_disappearances >= 1, 'CACHE_UNMAP_NOT_OBSERVED_QUALIFICATION_PARTIAL')
        require(set(self.registry) <= self.ever, 'REGISTERED_ELF_NOT_OBSERVED')
        for e in self.registry.values():
            verify_file(e)
        return dict(status='PASS_CPU_MAPPING_SEQUENCE', complete_snapshots=self.snapshots,
                    cache_observed=True, cache_disappearances=self.cache_disappearances,
                    files_observed=sorted(self.ever), all_registered_files_observed=True)
