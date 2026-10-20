"""Bounded inode-reader and metadata-stability proof; never opens payloads."""
from pathlib import Path
import os, json, stat, time, signal, csv, collections

P = Path(__file__).resolve().parent / 'r2'
signal.alarm(40)
started = time.time()
selected = json.loads((P/'COLD_FILE_CANDIDATES_V1.json').read_text())
keys = {(e['device'], e['inode']): e['path'] for e in selected}
assert len(keys) == len(selected)
changed, snapshots = [], []
for e in selected:
    s = os.lstat(e['path'])
    now = dict(device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
               size=s.st_size, allocated_bytes=s.st_blocks*512,
               mode=s.st_mode, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)
    diff = {k: [e[k], v] for k, v in now.items() if e[k] != v}
    if diff: changed.append(dict(path=e['path'], differences=diff))
    snapshots.append(dict(path=e['path'], uid=s.st_uid, gid=s.st_gid, **now))
readers, errors, vanished = [], [], []
observed, descriptors, maps_count = 0, 0, 0
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit(): continue
    observed += 1
    try:
        # Kernel file identity also finds hardlink/bind-mount aliases.
        for entry in [proc/'cwd', proc/'exe', *(proc/'fd').iterdir()]:
            try:
                s = entry.stat(); descriptors += 1
                if (s.st_dev, s.st_ino) in keys:
                    readers.append(dict(pid=int(proc.name), kind='inode:'+str(entry.relative_to(proc)),
                                        candidate=keys[(s.st_dev, s.st_ino)]))
            except FileNotFoundError: pass
            except PermissionError as ex: errors.append(dict(pid=int(proc.name), path=str(ex.filename)))
        for line in (proc/'maps').read_text().splitlines():
            parts = line.split(maxsplit=5)
            major, minor = [int(v, 16) for v in parts[3].split(':')]
            key = (os.makedev(major, minor), int(parts[4])); maps_count += 1
            if key in keys: readers.append(dict(pid=int(proc.name), kind='mmap_inode', candidate=keys[key]))
    except (FileNotFoundError, ProcessLookupError): vanished.append(int(proc.name))
    except PermissionError as ex: errors.append(dict(pid=int(proc.name), path=str(ex.filename)))
locks = []
for line in Path('/proc/locks').read_text().splitlines():
    for token in line.split():
        pieces = token.split(':')
        if len(pieces) != 3: continue
        try: key = (os.makedev(int(pieces[0], 16), int(pieces[1], 16)), int(pieces[2]))
        except ValueError: continue
        if key in keys: locks.append(dict(candidate=keys[key], kernel_lock=line))
registry = json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())
campaign = registry['mechanism_study_20261019_v1']
active = lambda d: {k:v for k,v in d.items() if v.get('status') in ['RESERVED','RUNNING','STARTING']}
active_runs, active_leases = active(registry['runs']), active(registry['resource_leases'])
assert campaign['actual_starts'] == 14 and campaign['controller']['state'] == 'STOPPED'
assert not active_runs and not active_leases
v = os.statvfs('/workspace')
summary = dict(schema='E2_COLD_SOURCE_INODE_AND_FREEZE_RECHECK_V1', at_unix=time.time(),
               elapsed_seconds=time.time()-started, host=os.uname().nodename,
               boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
               selected_files=len(selected), selected_inode_changes=changed,
               selected_all_single_link=all(e['nlink']==1 for e in snapshots),
               processes_observed=observed, descriptors_stat=descriptors,
               maps_entries_checked=maps_count, vanished_processes=vanished,
               permission_gaps=errors, inode_reader_matches=readers, kernel_lock_matches=locks,
               path_reader_snapshot='READER_SNAPSHOT.json', controller=campaign['controller'],
               active_runs=active_runs, active_leases=active_leases,
               workspace_available_bytes=v.f_bavail*v.f_frsize, workspace_inode_available=v.f_favail,
               full_payload_hashes=0, payload_bytes_read=0, source_release_authorized=False,
               limit='Snapshot proof only. S must recheck under source quiescence at seal/copy/release; this does not hold an immutable filesystem lock.',
               result='PASS_CANDIDATE_INODE_STABILITY_AND_NO_OBSERVED_READER' if not(changed or errors or readers or locks or vanished) else 'REVIEW_REQUIRED')
(P/'SOURCE_INODE_RECHECK.json').write_text(json.dumps(summary,indent=2)+'\n')
(P/'SOURCE_SELECTED_UID_GID_AND_METADATA.json').write_text(json.dumps(snapshots,indent=2)+'\n')
# All inventoried legacy raw/failure/current result and build files ranked by
# actual st_blocks; no result root qualifies for release in this proposal.
entries = json.loads((P/'FILE_METADATA.json').read_text())
ranked = sorted((e for e in entries if stat.S_ISREG(e['mode'])),key=lambda e:e['allocated_bytes'],reverse=True)
chosen = {e['path'] for e in selected}
warm_build = {e['path']:e['classification'] for e in json.loads((P/'HOT_WARM_BUILD_FILES_V1.json').read_text())}
with (P/'ALL_INVENTORIED_FILES_ALLOCATED_RANK.csv').open('w',newline='') as f:
    fields = ['rank','path','device','inode','nlink','size','allocated_bytes','classification','release_authorized']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for rank,e in enumerate(ranked,1):
        heat = 'COLD_CANDIDATE' if e['path'] in chosen else warm_build.get(e['path'],'HOT_ACCOUNTING_ROOT_OR_WARM_SCIENTIFIC_HISTORY')
        w.writerow(dict(rank=rank,**{k:e[k] for k in fields if k in e},classification=heat,release_authorized=False))
assert summary['result'].startswith('PASS'), summary
print(json.dumps(summary))
