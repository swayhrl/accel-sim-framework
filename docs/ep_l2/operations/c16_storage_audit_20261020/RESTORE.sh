#!/usr/bin/env bash
# Plan by default. Run on original174 only after separately approved restoration,
# six authority SHA passes, and admission by the existing C16 resource/IO gate.
# No network setup, download, deletion, overwrite, supervisor or quota changes.
set -euo pipefail
exec python3 - "$0" "$@" <<'PY'
import argparse, csv, hashlib, json, os, pathlib, socket, stat, subprocess, sys, time

ap = argparse.ArgumentParser(description='Restore only the six original174 outbound weight paths')
ap.add_argument('--execute', action='store_true', help='Future approved restore writes; default is plan only')
ap.add_argument('--mount', default='/root/share/mnt164', help='Existing authorized SSHFS mount of real164 /home/shared')
args = ap.parse_args(sys.argv[2:])
here = pathlib.Path(sys.argv[1]).resolve().parent
rows = list(csv.DictReader((here / 'RESTORE_MAPPING.tsv').open(), delimiter='\t'))
assert len(rows) == 6 and len({r['original174_path'] for r in rows}) == 6
for r in rows:
    print(json.dumps({k: r[k] for k in ['pair_id', 'native164_path', 'original174_path', 'size_bytes', 'sha256_expected']}, ensure_ascii=False))
if not args.execute:
    print('PLAN_ONLY: no payload read or write. See RELEASE_REQUEST.md for unresolved gates.')
    sys.exit(0)

def require(ok, message):
    if not ok:
        raise SystemExit(message)

require(os.geteuid() == 0, 'Restore numeric 0:0 metadata as root in original174 only')
require(socket.gethostname() == 'huangrulin-174' and os.readlink('/proc/self/ns/mnt') == 'mnt:[4026534768]', 'Wrong original174 host/namespace; obtain a fresh identity review after any container replacement')
mount = pathlib.Path(args.mount).resolve(strict=True)
mount_info = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(mount), '-o', 'TARGET,SOURCE,FSTYPE'], text=True))['filesystems'][0]
require(mount_info['fstype'] == 'fuse.sshfs' and mount_info['source'] == 'admin-wcx@10.208.130.164:/home/shared' and pathlib.Path(mount_info['target']).resolve() == mount, 'Not the proven real164 SSHFS mount; the old174 same-name local Share is invalid')
reserve = 48 * 1024**3  # Existing C16 reserve; no exception is granted by this script.

def io_gate():
    for line in pathlib.Path('/proc/pressure/io').read_text().splitlines():
        avg10 = float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
        require(avg10 < 10, 'C16 IO HOLD: leave partial copy for owner review; no autonomous retry')

plans = []
for r in rows:
    dst = pathlib.Path(r['original174_path'])
    require(str(dst).startswith('/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_'), 'Destination outside exact outbound scope')
    require(dst.parent.resolve(strict=True) == dst.parent, 'Destination parent missing or redirected')
    require(not os.path.lexists(dst), 'Destination exists; refusing overwrite: ' + str(dst))
    src = mount / pathlib.Path(r['native164_path']).relative_to('/home/shared')
    require(src.resolve(strict=True) == src, 'Authority path redirected')
    before = src.stat()
    require(stat.S_ISREG(before.st_mode) and before.st_size == int(r['size_bytes']), 'Authority size/type mismatch')
    plans.append((r, src, dst, before))
v = os.statvfs('/workspace/c16_exchange/autodl_wave1/outbound')
require(v.f_bavail * v.f_frsize >= sum(int(r['size_bytes']) for r in rows) + reserve, 'Insufficient original174 restore capacity and existing 48GiB reserve')
io_gate()
for r, src, dst, before in plans:
    tmp = dst.with_name(dst.name + '.restore-' + str(os.getpid()) + '.partial')
    digest = hashlib.sha256()
    amount = 0
    start = time.monotonic()
    # O_EXCL: preserve any pre-existing partial; no authority or source writes.
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as output, src.open('rb') as input_file:
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
        after = src.stat()
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'Authority changed during restore')
        require(amount == int(r['size_bytes']) and digest.hexdigest() == r['sha256_expected'], 'Stream SHA/size mismatch; do not promote partial')
        os.fchown(output.fileno(), int(r['uid']), int(r['gid']))
        os.fchmod(output.fileno(), int(r['mode_octal'], 8))
    os.utime(tmp, ns=(int(r['mtime_ns']), int(r['mtime_ns'])))
    # Atomic no-overwrite publication of our own verified independent copy.
    os.link(tmp, dst, follow_symlinks=False)
    os.unlink(tmp)  # Only our own temporary link; never deletes a source or authority.
    print(json.dumps({'restored': str(dst), 'stream_sha256': digest.hexdigest(), 'bytes': amount}))
print('Restored six outbound files. ctime/dev/inode are provenance only; existing directories and all controls were retained.')
PY
