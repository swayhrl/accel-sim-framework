"""Read-only, bounded audit of this SSH namespace; emits sanitized JSON only.

No source writes, hashes of history, permission changes, mount traversal, or cleanup.
An empty visible-process reference set never proves another container is inactive.
"""
import datetime
import glob
import json
import os
from pathlib import Path
import stat
import subprocess

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

commands = []

def run(args, timeout=15, publish=True):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        item = dict(argv=args, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except subprocess.TimeoutExpired as e:
        def dec(v):
            return v.decode(errors="replace") if isinstance(v, bytes) else (v or "")
        item = dict(argv=args, exit_code=None, timed_out=True,
                    stdout=dec(e.stdout), stderr=dec(e.stderr))
    if publish:
        commands.append(item)
    return item

def describe(path):
    d = dict(path=path, realpath=os.path.realpath(path), observed_at=now())
    try:
        s = os.lstat(path)
        d.update(exists=True, device=s.st_dev, inode=s.st_ino,
                 uid=s.st_uid, gid=s.st_gid, mode=oct(stat.S_IMODE(s.st_mode)),
                 is_symlink=stat.S_ISLNK(s.st_mode), nlink=s.st_nlink,
                 stat_size_bytes=s.st_size, allocated_self_bytes=s.st_blocks * 512,
                 mtime_ns=s.st_mtime_ns, atime_ns=s.st_atime_ns)
        v = os.statvfs(path)
        d.update(free_available_bytes=v.f_bavail * v.f_frsize,
                 total_bytes=v.f_blocks * v.f_frsize)
        d['df'] = run(['df', '-B1', '-P', path])
        d['findmnt'] = run(['findmnt', '-T', path, '-o', 'TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT'])
    except OSError as e:
        d.update(exists=False, error=str(e))
    return d

started = now()
paths = ['/workspace', '/tmp', '/root/workspace',
         '/root/workspace/accel-sim-framework',
         '/root/share/container-workspaces/hrl-174-new',
         '/root/share/container-workspaces/hrl-174-new/workspace',
         '/root/share/mnt164']
source_map = [describe(p) for p in paths]
identity = dict(id=run(['id'])['stdout'].strip(), hostname=run(['hostname'])['stdout'].strip(),
                pwd=os.getcwd(), mount_namespace=os.readlink('/proc/self/ns/mnt'),
                pid1_mount_namespace=os.readlink('/proc/1/ns/mnt'))
owner = Path('/root/share/container-workspaces/hrl-174-new/OWNER.md').read_text()
tools = {t: run(['which', t])['stdout'].strip()
         for t in ['ssh', 'rsync', 'lsof', 'fuser', 'ionice', 'docker', 'nsenter']}

# Do not publish SSH configuration, key contents, or hashed host records.
known = run(['ssh-keygen', '-F', '10.208.130.164'], publish=False)
fingerprint = None
if known['exit_code'] == 0:
    p = subprocess.run(['ssh-keygen', '-lf', '-'], input=known['stdout'],
                       capture_output=True, text=True, timeout=10)
    fingerprint = p.stdout.split()[1] if p.returncode == 0 else None
remote_cmd = 'hostname; id; df -B1 -P /home/shared; findmnt -T /home/shared; stat /home/shared/huangrulin'
handshake = run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                 '-o', 'ConnectTimeout=10', 'admin-wcx@10.208.130.164', remote_cmd], timeout=20)
remote = dict(status='COPY_GATE_BLOCKED', attempted_target='admin-wcx@10.208.130.164',
              target_source='Existing sshfs mount source and historical STORAGE_MOUNT_AUDIT.txt',
              trusted_known_host_fingerprint=fingerprint, handshake=handshake,
              authenticated_identity=None, remote_hostname=None, remote_data_device=None,
              approved_archive_root=None, remote_receipt=None,
              mount164_use='Metadata inspected only; never entered or used as staging/destination')

# One low-priority traversal, no symlink following, never traverse other mounts.
du = run(['timeout', '45', 'nice', '-n', '19', 'ionice', '-c', '3',
          'du', '-x', '-B1', '--max-depth=1', '/tmp'], timeout=50)
sizes = []
for line in du['stdout'].splitlines():
    parts = line.split('\t', 1)
    if len(parts) == 2 and parts[0].isdigit() and parts[1] != '/tmp':
        sizes.append((int(parts[0]), parts[1]))
sizes.sort(reverse=True)
candidate_paths = [p for _, p in sizes[:20]]
requested = ['/workspace/.git', '/workspace/build/postcheck',
             '/workspace/build/review_pack_staging', '/workspace/build/sim']
repo = '/root/workspace/accel-sim-framework'
candidate_paths += requested + [repo + '/build/' + x
                               for x in ['postcheck', 'review_pack_staging', 'sim']]
packs = glob.glob(repo + '/.git/tmp_pack_*') + glob.glob(repo + '/.git/objects/pack/tmp_pack_*')
candidate_paths += packs
allocation = dict((p, size) for size, p in sizes)

# Inspect only visible processes and publish bounded project metadata, not full args.
processes = []
refs = {p: [] for p in candidate_paths}
read_errors = 0
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():
        continue
    try:
        pid = int(proc.name)
        comm = (proc / 'comm').read_text().strip()
        raw = (proc / 'cmdline').read_bytes().decode(errors='replace').replace('\0', ' ')
        links = []
        for name in ['cwd', 'exe', 'root']:
            try:
                links.append(os.readlink(proc / name))
            except OSError:
                pass
        try:
            for fd in (proc / 'fd').iterdir():
                try:
                    links.append(os.readlink(fd))
                except OSError:
                    pass
        except OSError:
            read_errors += 1
        try:
            maps = (proc / 'maps').read_text(errors='replace')
        except OSError:
            maps = ''
        for path in candidate_paths:
            kinds = []
            if any(x == path or x.startswith(path + '/') for x in links):
                kinds.append('cwd/exe/root/fd')
            if path in maps:
                kinds.append('mmap')
            if path in raw:
                kinds.append('cmdline')
            if kinds:
                refs[path].append(dict(pid=pid, comm=comm, reference_types=kinds))
        projects = [x for x in ['ep_l2', 'ep-l2', 'lane', 'awma', 'c16', 'dtc', 'c2p', 'rtl']
                    if x in raw.lower()]
        if projects or comm in ['git', 'rsync', 'make', 'ninja', 'gpgpu-sim', 'accel-sim.out']:
            processes.append(dict(pid=pid, comm=comm, project_tags=projects,
                                  cwd=links[0] if links else None))
    except OSError:
        read_errors += 1

candidates = []
for path in candidate_paths:
    try:
        s = os.lstat(path)
        item = dict(EXACT_PATH=path, SIZE=allocation.get(path, s.st_size if stat.S_ISREG(s.st_mode) else None),
                    SIZE_KIND='du_allocated_tree_bytes' if path in allocation else 'file_length_or_unknown',
                    DEVICE=s.st_dev, OWNER=f'{s.st_uid}:{s.st_gid}', INODE=s.st_ino,
                    MODE=oct(stat.S_IMODE(s.st_mode)), MTIME_NS=s.st_mtime_ns,
                    ATIME_NS=s.st_atime_ns, NLINK=s.st_nlink,
                    SYMLINK=os.readlink(path) if stat.S_ISLNK(s.st_mode) else None,
                    ACTIVE_USE='VISIBLE_REFERENCE' if refs[path] else 'UNKNOWN_CROSS_NAMESPACE',
                    VISIBLE_REFERENCES=refs[path], UNIQUE='UNKNOWN', REPRODUCIBLE='UNPROVEN',
                    DEST_AVAILABLE='NO_VERIFIED_SSH_ROOT',
                    DELETE_ELIGIBILITY='BLOCKED_NOT_PROVEN_SAFE',
                    LANE5_FS_RELATION='UNPROVEN', SOURCE_ACTION='KEEP')
    except OSError as e:
        item = dict(EXACT_PATH=path, SIZE=None, SIZE_KIND='UNKNOWN', DEVICE=None,
                    OWNER=None, ACTIVE_USE='UNKNOWN', UNIQUE='UNKNOWN', REPRODUCIBLE='UNPROVEN',
                    DEST_AVAILABLE='NO_VERIFIED_SSH_ROOT', DELETE_ELIGIBILITY='NOT_ACCESSIBLE',
                    LANE5_FS_RELATION='UNPROVEN', SOURCE_ACTION='KEEP', ERROR=str(e))
    candidates.append(item)

git_audit = dict(requested_git_dir='/workspace/.git', accessible=False,
                 alternate_git_dir=repo+'/.git', alternate_tmp_packs_found=packs,
                 exact_source_pack_list=None, fsck='NOT_RUN_SOURCE_UNAVAILABLE',
                 unique_object_analysis='NOT_RUN_SOURCE_UNAVAILABLE',
                 sha256='NOT_RUN_NO_CONFIRMED_SOURCE', remote_backup='NOT_RUN',
                 deletion='NOT_RUN_REQUIRES_EXACT_LIST_AND_USER_APPROVAL',
                 visible_git_processes=[p for p in processes if p['comm'] == 'git'])
git_audit['alternate_pack_metadata'] = run(['find', repo+'/.git/objects/pack',
    '-maxdepth', '1', '-type', 'f', '-printf', '%f\t%s\t%T@\n'])
git_audit['alternate_root_locks'] = run(['find', repo+'/.git', '-maxdepth', '1',
                                      '-name', '*.lock', '-printf', '%f\t%s\t%T@\n'])
after = [describe(p) for p in ['/workspace', '/tmp', '/root/workspace',
                             '/root/share/container-workspaces/hrl-174-new/workspace']]
print(json.dumps(dict(started_at=started, finished_at=now(), identity=identity,
                     source_map=source_map, workspace_owner_record=owner, tools=tools,
                     remote=remote, candidates=candidates, tmp_scan_complete=du['exit_code'] == 0,
                     process_visibility='Only this SSH container; other Lane namespaces not visible',
                     process_read_errors=read_errors, project_processes=processes,
                     git_audit=git_audit, after=after,
                     source_deletions=0, source_bytes_released_by_ops=0,
                     commands=commands), ensure_ascii=False, indent=2))
