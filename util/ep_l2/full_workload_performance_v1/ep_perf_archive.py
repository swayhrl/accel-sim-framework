"""Closed-result SOURCE_KEEP copy, SHA verification and fresh native restores."""
import argparse, hashlib, json, os, pathlib, stat, subprocess, sys, tarfile, tempfile, uuid
from ep_perf_common import *

ARCHIVE_ROOT = P('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_full_workload_performance_20261027_v1')


def inventory(root):
    root = P(root)
    rows = []
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            need(not (P(parent)/name).is_symlink(), 'linked output directory')
        for name in sorted(files):
            p = P(parent)/name
            st = p.lstat()
            need(stat.S_ISREG(st.st_mode), 'nonregular result member')
            digest = sha(p)
            after = p.stat()
            need((st.st_size, st.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'result still changing')
            rows.append(dict(member=str(p.relative_to(root)), bytes=st.st_size, sha256=digest,
                             mode=stat.S_IMODE(st.st_mode), uid=st.st_uid, gid=st.st_gid,
                             mtime_ns=st.st_mtime_ns, atime_ns=st.st_atime_ns))
    need(rows and len(rows) <= 20000, 'unbounded output inventory')
    return sorted(rows, key=lambda row:row['member'])


def safe_member(name):
    p = pathlib.PurePosixPath(name)
    need(not p.is_absolute() and name == str(p) and '..' not in p.parts and name not in ['','.'], 'unsafe archive member')


def restore(archive, manifest, target, max_bytes):
    manifest = read(manifest)
    need(sha(archive) == manifest['archive_sha256'], 'archive content mismatch')
    need(not P(target).exists(), 'restore needs fresh target')
    expected = {row['member']:row for row in manifest['members']}
    need(len(expected) == len(manifest['members']) and sum(row['bytes'] for row in expected.values()) <= max_bytes,
         'restore byte bound/population')
    P(target).mkdir(parents=True)
    seen = set()
    with tarfile.open(archive, 'r|') as stream:
        for member in stream:
            safe_member(member.name)
            need(member.isfile() and member.name in expected and member.name not in seen, 'unexpected/duplicate archive member')
            row = expected[member.name]
            need(member.size == row['bytes'], 'member size differs')
            path = P(target)/member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            h = hashlib.sha256()
            count = 0
            with stream.extractfile(member) as source, path.open('xb') as output:
                for b in iter(lambda: source.read(M), b''):
                    count += len(b)
                    need(count <= row['bytes'], 'member byte overflow')
                    output.write(b)
                    h.update(b)
                output.flush()
                os.fsync(output.fileno())
            need(count == row['bytes'] and h.hexdigest() == row['sha256'], 'restored member SHA mismatch')
            os.chown(path, row['uid'], row['gid'])
            os.chmod(path, row['mode'])
            os.utime(path, ns=(row['atime_ns'],row['mtime_ns']))
            need(sha(path) == row['sha256'], 'closed reopened restore SHA mismatch')
            st = path.stat()
            need((st.st_size, stat.S_IMODE(st.st_mode), st.st_uid, st.st_gid, st.st_mtime_ns) ==
                 (row['bytes'],row['mode'],row['uid'],row['gid'],row['mtime_ns']), 'native restored metadata mismatch')
            seen.add(member.name)
    need(seen == set(expected), 'restore population incomplete')
    return dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS', target=str(target),
                archive_sha256=manifest['archive_sha256'], file_count=len(seen),
                logical_bytes=sum(row['bytes'] for row in expected.values()), source_keep=True)


def archive_case(case):
    # The aggregate guarantee reserves one restore window for the entire Goal.
    with locked(ROOT/'control/ARCHIVE_SHARED_WINDOW.lock'):
        return _archive_case(case)


def _archive_case(case):
    registry, unused = authority()
    row = registry['registered_future_requests'][GOAL]['consumed'][case]
    need(row['state'] in ['ACCEPTED_PENDING_ARCHIVE','UNACCEPTED_ENGINEERING_FAILURE','PARSE_HOLD'], 'terminal result required')
    done = exact(row['done_ref'])
    out = P(done['output'])
    need(out.is_relative_to(ROOT/'cases'/case/'run') and row['uuid'] == out.name, 'case output scope')
    need(read(out/'NATIVE_EXIT.json') == done, 'DONE/EXIT mismatch')
    if (out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').exists():
        pid = read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
        proc = P('/proc')/str(pid['pid'])/'stat'
        if proc.exists():
            pieces = proc.read_text().rsplit(')',1)[1].split()
            need(int(pieces[19]) != pid['start_ticks'] or pieces[0] in ['Z','X'], 'model still alive')
    mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
    need(mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs','archive destination is not genuine164')
    destination_device=P('/root/share/mnt164').stat().st_dev
    target = ARCHIVE_ROOT/('accepted' if row['state'] == 'ACCEPTED_PENDING_ARCHIVE' else 'technical_negative')/case/row['uuid']
    need(not target.exists(), 'immutable archive exists; operational resume must inspect receipts')
    members = inventory(out)
    total = sum(x['bytes'] for x in members)
    required=total+len(members)*1024+2*M
    fs=os.statvfs('/root/share/mnt164')
    need(fs.f_bavail*fs.f_frsize>=required,'genuine164 actual incremental space unavailable')
    target.mkdir(parents=True)
    partial = target/'result.tar.PARTIAL'
    archive = target/'result.tar'
    with partial.open('xb') as disk:
        with tarfile.open(fileobj=disk, mode='w|') as stream:
            for member in members:
                path = out/member['member']
                need(sha(path) == member['sha256'], 'source changed before copy')
                info = tarfile.TarInfo(member['member'])
                info.size = member['bytes']
                info.mode = member['mode']
                info.uid, info.gid = member['uid'], member['gid']
                info.mtime = member['mtime_ns']//1000000000
                with path.open('rb') as source:
                    stream.addfile(info, source)
        disk.flush()
        os.fsync(disk.fileno())
    partial.rename(archive)
    digest = sha(archive)
    need(sha(archive) == digest, 'closed reopened NAS archive SHA mismatch')
    need(archive.stat().st_dev==destination_device==P('/root/share/mnt164').stat().st_dev,'archive mount identity changed')
    manifest = dict(schema='EP_FULL_PERF_IMMUTABLE_RESULT_ARCHIVE_V1', goal=GOAL, cohort=case,
                    uuid=row['uuid'], source_identity=done['source_identity'], done_ref=row['done_ref'],
                    scientific_state=row['state'], archive_sha256=digest, archive_bytes=archive.stat().st_size,
                    members=members, source_keep=True, source_release_bytes=0)
    manifest_path = target/'MANIFEST.json'
    put(manifest_path, manifest, True)
    receipts = []
    # Two independent fresh native restores reuse one bounded temporary window.
    # The scientific Source and genuine164 archive are kept; only owned scratch is released.
    window_root = ROOT/'restore_windows'
    window_root.mkdir(exist_ok=True)
    for label in ['FIRST','INDEPENDENT']:
        with tempfile.TemporaryDirectory(prefix=case+'_'+label+'_',dir=window_root) as scratch:
            native_target = P(scratch)/'fresh_target'
            result = subprocess.run([sys.executable,'-B',__file__,'restore','--archive',str(archive),
                        '--manifest',str(manifest_path),'--target',str(native_target),'--max-bytes',str(total)],
                        text=True, capture_output=True, timeout=max(120,total//M*4))
            need(result.returncode == 0, 'native restore failure ' + result.stderr[-2000:])
            restored = json.loads(result.stdout)
            restored.update(restore_label=label, temporary_native_working_set_released_after_verification=True,
                            permanent_scientific_source_deleted=False)
            receipts.append(restored)
    receipt = dict(status='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS', goal=GOAL,
                   cohort=case, uuid=row['uuid'], manifest_ref=ref(manifest_path), archive_ref=ref(archive),
                   native_restores=receipts, source_keep=True, source_release_bytes=0)
    receipt_ref = put(ROOT/'cases'/case/'control/ARCHIVE_RECEIPT.json', receipt, True)
    put(target/'ARCHIVE_RECEIPT.json', receipt, True)
    put(target/'COMMIT.json',dict(schema='EP_FULL_PERF_ARCHIVE_COMMIT_V1',goal=GOAL,
        cohort=case,uuid=row['uuid'],manifest_ref=ref(manifest_path),archive_ref=ref(archive),
        receipt_ref=ref(target/'ARCHIVE_RECEIPT.json'),commit_last=True,source_keep=True),True)
    def close(reg):
        q = reg['registered_future_requests'][GOAL]['consumed'][case]
        need(q['uuid'] == row['uuid'] and q['done_ref'] == row['done_ref'], 'own row changed')
        q.update(state='CLOSED_ACCEPTED' if row['state'] == 'ACCEPTED_PENDING_ARCHIVE' else 'CLOSED_UNACCEPTED',
                 archive_receipt_ref=receipt_ref, remaining_write_bytes=0)
    transaction('CLOSE_ARCHIVED_CASE_KEEP_CHARGE_AND_SOURCE', close)
    with locked(ROOT/'control/ADMISSION.lock'):
        path=ROOT/'control/DISPATCH_CLAIMS.json'
        claims=read(path)
        claims['claims'].pop(case,None)
        put(path,claims)
        publish_own_write_carrier(claims['claims'])
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action',required=True)
    one = sub.add_parser('archive')
    one.add_argument('cohort')
    two = sub.add_parser('restore')
    for arg in ['archive','manifest','target']:
        two.add_argument('--'+arg,required=True)
    two.add_argument('--max-bytes',required=True,type=int)
    args = parser.parse_args()
    if args.action == 'archive':
        print(json.dumps(archive_case(args.cohort)))
    else:
        print(json.dumps(restore(args.archive,args.manifest,args.target,args.max_bytes)))
