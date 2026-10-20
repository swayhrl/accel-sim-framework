#!/usr/bin/env bash
# Plan by default. Run on original174 only after separately approved restoration,
# six authority SHA passes, and admission by the existing C16 resource/IO gate.
# No network setup, download, deletion, overwrite, supervisor or quota changes.
set -euo pipefail
exec python3 - "$0" "$@" <<'PY'
import argparse, csv, hashlib, json, os, pathlib, shlex, socket, stat, subprocess, sys, tarfile, time

ap = argparse.ArgumentParser(description='Restore only the six original174 outbound weight paths')
ap.add_argument('--execute', action='store_true', help='Future approved restore writes; default is plan only')
ap.add_argument('--mount', default='/root/share/mnt164', help='Existing authorized SSHFS mount of real164 /home/shared')
ap.add_argument('--package', choices=['P3', 'P2', 'all'], default='all', help='Independent complete package recovery; P3 precedes P2')
ap.add_argument('--shared-pipe', help='Foreground true164-on174new to original174 FIFO in the verified common Share bridge')
ap.add_argument('--print-producer', action='store_true', help='Print the exact174-new foreground producer command; no payload IO')
args = ap.parse_args(sys.argv[2:])
here = pathlib.Path(sys.argv[1]).resolve().parent
rows = list(csv.DictReader((here / 'RESTORE_MAPPING.tsv').open(), delimiter='\t'))
assert len(rows) == 6 and len({r['original174_path'] for r in rows}) == 6
rows = [r for package in ['P3', 'P2'] for r in rows
        if r['package'] == package and args.package in ['all', package]]
for r in rows:
    print(json.dumps({k: r[k] for k in ['pair_id', 'native164_path', 'original174_path', 'size_bytes', 'sha256_expected']}, ensure_ascii=False))
if args.print_producer:
    require_pipe = '/root/share/c16_storage_audit_restore_20261020_v1/restore-' + args.package + '.fifo'
    pipe = args.shared_pipe or require_pipe
    names = [str(pathlib.Path(r['native164_path']).relative_to('/home/shared')) for r in rows]
    code = "import os,json,subprocess; assert os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'; m=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164','-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]; assert m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs'; subprocess.run(" + repr(['tar', '--format=ustar', '-cf', pipe, '-C', '/root/share/mnt164', '--'] + names) + ",check=True)"
    print('RUN_ON_174NEW: ' + shlex.join(['timeout', '7200', 'ionice', '-c3', 'nice', '-n19', 'python3', '-c', code]))
    sys.exit(0)
if not args.execute:
    print('PLAN_ONLY: no payload read or write. See conditional_retirement/STATUS.md for current gates and conditional user authority.')
    sys.exit(0)

def require(ok, message):
    if not ok:
        raise SystemExit(message)

require(os.geteuid() == 0, 'Restore numeric 0:0 metadata as root in original174 only')
os.nice(19)  # Invoke the approved execution with ionice -c3 as well.
require(socket.gethostname() == 'huangrulin-174' and os.readlink('/proc/self/ns/mnt') == 'mnt:[4026534768]', 'Wrong original174 host/namespace; obtain a fresh identity review after any container replacement')
pipe_path = pathlib.Path(args.shared_pipe) if args.shared_pipe else None
if pipe_path:
    bridge = pathlib.Path('/root/share/c16_storage_audit_restore_20261020_v1')
    require(pipe_path == bridge / ('restore-' + args.package + '.fifo') and bridge.resolve(strict=True) == bridge, 'Wrong shared recovery pipe path')
    probe = json.loads((bridge / 'SOURCE_ROUTE_PROBE.json').read_text())
    ack = json.loads((bridge / 'TARGET_ROUTE_ACK.json').read_text())
    ack_text = json.dumps(ack)
    require(probe['nonce'] in ack_text and 'mnt:[4026535153]' in ack_text and 'admin-wcx@10.208.130.164:/home/shared' in ack_text, 'Shared recovery route handshake not closed')
    require(hashlib.sha256((bridge / 'SOURCE_ROUTE_PROBE.json').read_bytes()).hexdigest() == json.loads((here / 'conditional_retirement/RESTORE_ROUTE_SOURCE_PROBE.json').read_text())['sha256'], 'Source route probe changed')
else:
    mount = pathlib.Path(args.mount).resolve(strict=True)
    mount_info = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(mount), '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
    require(mount_info['fstype'] == 'fuse.sshfs' and mount_info['source'] == 'admin-wcx@10.208.130.164:/home/shared' and pathlib.Path(mount_info['target']).resolve() == mount, 'Not the proven real164 SSHFS mount; the old174 same-name local Share is invalid')
reserve = 48 * 1024**3  # Existing C16 reserve; no exception is granted by this script.
override_path = here / 'conditional_retirement/USER_IO_OVERRIDE.json'
override = json.loads(override_path.read_text()) if override_path.exists() else {}
allow_competing_io = override.get('IO10_stop_condition_removed') is True and override.get('active_E2_is_not_a_source_read_veto') is True

def io_gate():
    for line in pathlib.Path('/proc/pressure/io').read_text().splitlines():
        avg10 = float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
        require(avg10 < 10 or allow_competing_io, 'C16 IO HOLD: leave partial copy for owner review; no autonomous retry')
    registry = json.loads(pathlib.Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())
    active = {'RESERVED', 'RUNNING'}
    require(not any(v.get('status') in active for v in registry['resource_leases'].values()), 'Active physical resource lease: no C16 restore admission')
    require(allow_competing_io or not any(v.get('status') in active for v in registry['runs'].values()), 'E2/other active resource use: no C16 restore admission')
    require(allow_competing_io or registry['mechanism_study_20261019_v1']['controller']['state'] == 'STOPPED', 'E2 controller still active')

plans = []
for r in rows:
    dst = pathlib.Path(r['original174_path'])
    require(str(dst).startswith('/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_'), 'Destination outside exact outbound scope')
    require(dst.parent.resolve(strict=True) == dst.parent, 'Destination parent missing or redirected')
    require(not os.path.lexists(dst), 'Destination exists; refusing overwrite: ' + str(dst))
    src, before = None, None
    if not pipe_path:
        src = mount / pathlib.Path(r['native164_path']).relative_to('/home/shared')
        require(src.resolve(strict=True) == src, 'Authority path redirected')
        before = src.stat()
        require(stat.S_ISREG(before.st_mode) and before.st_size == int(r['size_bytes']), 'Authority size/type mismatch')
    plans.append((r, src, dst, before))
v = os.statvfs('/workspace/c16_exchange/autodl_wave1/outbound')
require(v.f_bavail * v.f_frsize >= sum(int(r['size_bytes']) for r in rows) + reserve, 'Insufficient original174 restore capacity and existing 48GiB reserve')
io_gate()
archive = None
if pipe_path:
    if not os.path.lexists(pipe_path):
        os.mkfifo(pipe_path, 0o600)
    pipe_stat = pipe_path.lstat()
    require(stat.S_ISFIFO(pipe_stat.st_mode) and pipe_stat.st_uid == 0 and not pipe_path.is_symlink(), 'Shared pipe type/owner mismatch')
    print('FIFO_READY: start the printed174-new producer. Run this foreground consumer under timeout7200.', flush=True)
    archive = tarfile.open(str(pipe_path), mode='r|')
for r, src, dst, before in plans:
    tmp = dst.with_name(dst.name + '.restore-' + str(os.getpid()) + '.partial')
    digest = hashlib.sha256()
    amount = 0
    start = time.monotonic()
    # O_EXCL: preserve any pre-existing partial; no authority or source writes.
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    if archive:
        member = archive.next()
        expected_member = str(pathlib.Path(r['native164_path']).relative_to('/home/shared'))
        require(member is not None and member.isfile() and member.name == expected_member and member.size == int(r['size_bytes']), 'Unexpected restore stream member; no arbitrary archive extraction')
        input_stream = archive.extractfile(member)
    else:
        input_stream = src.open('rb')
    with os.fdopen(fd, 'wb') as output, input_stream as input_file:
        while True:
            io_gate()
            block = input_file.read(1024 * 1024)
            if not block:
                break
            output.write(block)
            digest.update(block)
            amount += len(block)
            time.sleep(max(0, amount / (8 * 1024**2) - (time.monotonic() - start)))
        output.flush()
        os.fsync(output.fileno())
        if src:
            after = src.stat()
            require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'Authority changed during restore')
        require(amount == int(r['size_bytes']) and digest.hexdigest() == r['sha256_expected'], 'Stream SHA/size mismatch; do not promote partial')
        os.fchown(output.fileno(), int(r['uid']), int(r['gid']))
        os.fchmod(output.fileno(), int(r['mode_octal'], 8))
    os.utime(tmp, ns=(int(r['mtime_ns']), int(r['mtime_ns'])))
    # Independently verify restored bytes before publication, bounded by the same rate.
    verify, verified, verify_start = hashlib.sha256(), 0, time.monotonic()
    with tmp.open('rb') as check:
        while True:
            io_gate()
            block = check.read(1024 * 1024)
            if not block:
                break
            verify.update(block)
            verified += len(block)
            time.sleep(max(0, verified / (8 * 1024**2) - (time.monotonic() - verify_start)))
        os.fsync(check.fileno())
    require(verified == int(r['size_bytes']) and verify.hexdigest() == r['sha256_expected'], 'Restored file SHA/size mismatch')
    restored = tmp.stat()
    require((restored.st_uid, restored.st_gid, stat.S_IMODE(restored.st_mode), restored.st_mtime_ns) ==
            (int(r['uid']), int(r['gid']), int(r['mode_octal'], 8), int(r['mtime_ns'])), 'Restored metadata mismatch')
    # Atomic no-overwrite publication of our own verified independent copy.
    os.link(tmp, dst, follow_symlinks=False)
    os.unlink(tmp)  # Only our own temporary link; never deletes a source or authority.
    parent_fd = os.open(dst.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    print(json.dumps({'restored': str(dst), 'stream_sha256': digest.hexdigest(), 'bytes': amount}))
if archive:
    require(archive.next() is None, 'Unlisted member after the exact selected package')
    archive.close()
print('Restored selected complete outbound package(s). ctime/dev/inode are provenance only; existing directories and all controls were retained.')
PY
