"""Derive compact, truthful receipts locally from the read-only audit JSON."""
import csv
import hashlib
import json
from pathlib import Path
import shlex

root = Path(__file__).resolve().parent
data = json.loads((root / 'AUDIT_EVIDENCE.json').read_text(encoding='utf-8'))
anchor = '543a88d63f899ccfa4f6c569245496d6deb8fdf2'
branch = 'hrl/ops-174new-164-archive-exec-v1'

def write(name, content):
    (root / name).write_text(content, encoding='utf-8', newline='\n')

def jwrite(name, content):
    write(name, json.dumps(content, ensure_ascii=False, indent=2) + '\n')

jwrite('SOURCE_FS_MAP.json', dict(identity=data['identity'], paths=data['source_map'],
    workspace_owner_record=data['workspace_owner_record'],
    lane5_workspace_accessible=False, same_underlying_filesystem_or_quota_proven=False,
    lane5_independent_measurement=None,
    conclusion='SSH /root/workspace overlay and shared ext4 are different mounts; neither is proven to be Lane5 /workspace.'))
jwrite('REMOTE_164_AUDIT.json', data['remote'])
jwrite('GIT_TEMP_PACK_AUDIT.json', data['git_audit'])
columns = ['EXACT_PATH', 'SIZE', 'SIZE_KIND', 'DEVICE', 'OWNER', 'INODE', 'MODE',
           'MTIME_NS', 'ATIME_NS', 'NLINK', 'SYMLINK', 'ACTIVE_USE', 'VISIBLE_REFERENCES',
           'UNIQUE', 'REPRODUCIBLE', 'DEST_AVAILABLE', 'DELETE_ELIGIBILITY',
           'LANE5_FS_RELATION', 'SOURCE_ACTION', 'ERROR']
with (root / 'CANDIDATES.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    for item in data['candidates']:
        row = dict(item)
        if 'VISIBLE_REFERENCES' in row:
            row['VISIBLE_REFERENCES'] = json.dumps(row['VISIBLE_REFERENCES'], separators=(',', ':'))
        writer.writerow(row)
with (root / 'TRANSFER_MANIFEST.csv').open('w', encoding='utf-8', newline='') as f:
    csv.writer(f, lineterminator='\n').writerow(['exact_source', 'destination_relative_path',
        'size_bytes', 'sha256', 'copy_status', 'verify_status', 'source_action'])
jwrite('SHA256_VERIFICATION.json', dict(status='NOT_RUN_COPY_GATE_BLOCKED',
    source_data_hashed=False, transferred_files=0, transferred_bytes=0,
    remote_data_hashed=False, verified_remote_files=0, source_stability_check='NOT_RUN',
    note='SHA256SUMS covers only these local audit receipts, not historical source or archive data.'))
before = {x['path']: x for x in data['source_map']}
changes = []
for end in data['after']:
    start = before[end['path']]
    changes.append(dict(path=end['path'], source_device=start.get('device'),
        before_time=start['observed_at'], after_time=end['observed_at'],
        before_free_bytes=start.get('free_available_bytes'),
        after_free_bytes=end.get('free_available_bytes'),
        observed_net_change_bytes=(end['free_available_bytes'] - start['free_available_bytes'])
            if start.get('exists') and end.get('exists') else None,
        lane5_fs_relationship='UNPROVEN', ops_source_deletions=0,
        ops_attributable_released_bytes=0))
jwrite('SPACE_BEFORE_AFTER.json', dict(status='SPACE_NOT_RECOVERED',
    floor_bytes=51539607552, floor_gib=48, recommended_growth_bytes=8589934592,
    observations=changes, lane5_before=None, lane5_after=None,
    lane5_independent_remeasurement=None, remote_target_device=None, remote_target_free_bytes=None,
    lane5_workspace_bytes_released_by_ops=0,
    historical_lane5_snapshot=dict(free_bytes=50802106368, source='Frozen GOAL.md; not a current measurement'),
    attribution='No source data was removed. Other filesystem changes are not attributed to Ops.'))
write('STATUS.md', f'''# Storage-Ops status: COPY_GATE_BLOCKED

- Run: `20261016_storageops_01`; audit {data['started_at']} through {data['finished_at']} (UTC).
- Frozen Goal: `{anchor}`. Execution branch: `{branch}`.
- Executor: SSH `hrl-174-new`, root on `huangrulin-sshfs-174`, mount namespace `mnt:[4026535153]`.
- Execution checkout is independent at `D:/repo/storage-ops-174new-164-exec-v1`; no shared source Git refs, worktrees, lane registry, or scientific results were written.
- PRECHECK executed. COPY / VERIFY / CLEANUP: **NOT_RUN**. Transfer manifest has zero data rows.
- Source objects copied/deleted: **0 / 0**. Ops-released Lane5 workspace bytes: **0**.
- Lane5 actual `/workspace` is absent in this SSH namespace. Its device/quota relation to all visible candidates is unproven.
- Strict SSH to historical `admin-wcx@10.208.130.164` failed authentication (exit 255). Authenticated identity, remote data device and authorized archive root remain unknown.
- The observed `mnt164` mount is `fuse.sshfs`; this fact alone does not establish an authorized archive root. It was never traversed, copied into, or used as transit.
- This run has **not recovered build capacity**. The 48 GiB floor and all lane resource limits remain unchanged. Lane5 independent remeasurement is null.

Next: obtain the exact usable 164 SSH identity/port/archive root/fingerprint and a read-only route or independent mount/df/stat snapshot for Lane5 `/workspace`; then repeat the affected gates before any transfer. No tmp_pack deletion approval is requested yet: the actual source list, backup and verification are unavailable.

See `PRECHECK.md`, `CANDIDATES.csv`, `APPROVAL_REQUIRED.md`, and `SPACE_BEFORE_AFTER.json`. Publication is verified separately in `PUBLICATION.json`; absence of that file means publication has not yet been recorded.
''')
write('PRECHECK.md', '''# Read-only precheck

The frozen Goal was read in full from GitHub and again from the exact fetched commit. No experimental/scientific change is part of this task.

## Filesystem and namespace gate: BLOCKED

`/workspace` does not exist in the SSH container. `/tmp`, `/root/workspace` and the inspected framework use overlay device 1048578; `/root/share/container-workspaces/hrl-174-new/workspace` uses ext4 device 2431 (`/dev/md127`). Its OWNER.md assigns the namespace to `huangrulin-sshfs-174`, but does not identify Lane5's mount. Comparing available bytes alone cannot prove shared backing storage/quota. No mapping, permission change, namespace entry or bind mount was invented.

Actual per-path measurements and timestamps are in SOURCE_FS_MAP.json and SPACE_BEFORE_AFTER.json. None is labeled a current Lane5 measurement. The frozen 47.313 GiB value remains historical only.

## Remote gate: COPY_GATE_BLOCKED

Existing known_hosts contains ED25519 fingerprint `SHA256:dqYoOWVsWJITNfoRthWBnaGmiPvXIgWsfXb7BKGc3u4`. Existing mount metadata and a prior storage report identify `admin-wcx@10.208.130.164:/home/shared`. A BatchMode/StrictHostKeyChecking handshake to that existing identity returned `Permission denied (publickey,password)`. No alternative accounts, passwords, new host keys or permissions were guessed. There is no authenticated remote hostname, data device, archive owner or approved root. No remote command executed successfully.

Live findmnt describes `/root/share/mnt164` as fuse.sshfs, differing from the Goal's older path description. Only its mount/stat/df metadata was inspected; no directory contents or archives were read or written there, and this observation is not used to bypass the direct-SSH/root gate.

## Candidate and activity gate: no delete-eligible objects

One nice/ionice-prioritized, 45-second-limited `du -x` traversal of `/tmp` completed. CANDIDATES.csv records the top 20 directories and the inaccessible historical Git/build locations. Sizes for directories are allocated bytes from du, not complete logical file lengths. Stat mode, inode, device, owner, nlink, mtime and atime are recorded where accessible. Directory nlink does not describe hardlinks inside the directory. Tree ACLs, per-file hardlinks and uniqueness are unverified; no transfer gate is passed.

The largest visible temporary directory is only 222453760 allocated bytes. Historical M5/RTL/C2P candidates totaling approximately 32 GiB were not identified in this namespace. Neither `/workspace/.git` nor the historical build roots exists here. The inspected alternate framework Git directory has an ordinary pack/index and no tmp_pack candidates. Its ordinary pack is not a cleanup candidate.

Visible processes, cwd/exe/root links, file descriptors, mmap references and command-line references were inspected without publishing full command lines. An AWMA waiting shell is visible and untouched. No visible Git writer was found at the recorded snapshot. Other containers' Lane/AWMA/C16/DTC/C2P/RTL activity is not visible, so empty reference lists cannot prove inactivity. Every candidate remains UNKNOWN/UNPROVEN and KEEP. No project ownership or deterministically reproducible source was inferred from a directory name or age.

## Git temporary pack investigation

GIT_TEMP_PACK_AUDIT.json records the unavailable requested Git directory, alternate pack metadata and alternate root lock snapshot. Full fsck, reference/unique-object analysis, source SHA256 and remote backup are NOT_RUN because the exact actual source is unavailable and remote gates are blocked. No gc, repack, prune, pack deletion or source ref update was run. Exact source pack identification and full verified backup must precede any concrete deletion approval request.

## Resource and cleanup result

Zero data transfers, source deletions, or source bytes released. No broad history hashing, no experiment launch, no process termination, no lane contact/registry write, and no relaxation of 48 GiB/64 GiB/2-long-simulation/8-CPU/32-GiB constraints. Receipt files are stored on the independent Windows execution checkout. SHA256SUMS describes receipt integrity only; historical data verification is NOT_RUN.
''')
write('APPROVAL_REQUIRED.md', '''# Required information and deferred approval

Current gate: COPY_GATE_BLOCKED. No source deletion is proposed or approved by this receipt.

Provide one connection/mapping bundle: the precise reachable `user@host:archive_root`, SSH port and trusted SHA256 host fingerprint for the genuine 164 large data filesystem, plus a read-only route to Lane5's actual `/workspace` or its independent `df -B1 -P /workspace`, `findmnt -T /workspace`, and `stat -c '%d %i %n' /workspace` snapshot. The historical admin-wcx identity fails publickey authentication from 174-new. Do not send private keys or passwords into the receipt.

This missing identity/root/mapping information is required by frozen GOAL.md sections 1.2, 1.4 and 1.5. It cannot be inferred from the old mount record or from matching free-space numbers.

`/workspace/.git/tmp_pack_*`: REQUIRES_USER_APPROVAL before any eventual source deletion, as explicitly required by the user and Goal sections 2.B and 3.4. Exact paths, size/mtime/SHA256, Git health/unique-object assessment and verified full 164 backup are NOT_RUN/unavailable. No wildcard deletion approval is being requested. Supply a concrete exact-path list and remote verification first.

Historical traces, raw logs/config/CSV/receipts, review packs, Git refs, model weights, unique binaries and active/uncertain task files remain protected. No blanket authorization is inferred for those objects.
''')
lines = ['# Action log', '', 'All audit commands below executed in the 174-new SSH container. No secret/key material or complete SSH configuration is included.', '',
         '## Setup and preliminary probes', '',
         '- GitHub connector fetched the complete frozen GOAL.md successfully; local independent fetch/read confirmed SHA '+anchor+'.',
         '- Inspected SSH namespace identity, selected path metadata and workspace OWNER.md; no permission changes.',
         '- An initial nested shell-quoted SSH probe failed authentication; trailing read-only metadata commands ran in the local 174 namespace. Those trailing results were discarded as remote evidence. The argument-array subprocess probe below corrected this transport issue and also failed authentication (255).',
         '- Source-container git ls-remote timed out after 45 seconds; publishing was moved to the independent Windows checkout, where git ls-remote and shallow filtered fetch succeeded (0). No source-container branch/ref or worktree was created.',
         '- Local setup executed git init, remote add, gc.auto=0 fetch --filter=blob:none --depth=1 --no-tags, sparse-checkout, and switch to the requested independent execution branch; all returned 0.',
         '- Full Goal read from fetched commit and applicable instruction-file checks completed. No subagents were launched.',
         '', '## Reproducible read-only audit', '',
         '`Get-Content audit_readonly.py -Raw | ssh -o BatchMode=yes -o StrictHostKeyChecking=yes hrl-174-new "python3 -"` returned 0. Output is AUDIT_EVIDENCE.json.', '']
for i, c in enumerate(data['commands'], 1):
    lines += [f"{i}. Executed `{shlex.join(c['argv'])}`; exit={c['exit_code']}; timed_out={c.get('timed_out', False)}."]
lines += ['', '## Deferred actions', '',
          '- rsync dry-run, copy, source/remote SHA256, remote receipt, exact-source stability check: NOT_RUN (both precheck gates blocked).',
          '- tmp_pack fsck/unique-object inspection: NOT_RUN (actual source Git directory inaccessible).',
          '- Any source cleanup, permission change, process stop, lane result/registry/worktree write: NOT_RUN.',
          '- Local build_receipt.py generated the derived JSON/CSV/Markdown files; its receipt SHA256 values are not data archive verification.',
          '- git diff --check, explicit receipt-path staging, commit, push, fetch and remote readback are recorded after execution in PUBLICATION.json.', '']
write('ACTION_LOG.md', '\n'.join(lines))
# Never hash source history. These are only small local receipt artifacts.
write('SHA256SUMS', ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n'
      for p in sorted(root.iterdir()) if p.is_file() and p.name not in ['SHA256SUMS', 'PUBLICATION.json']))
print(json.dumps(dict(status='COPY_GATE_BLOCKED', candidates=len(data['candidates']),
    files=len(list(root.iterdir())), receipt_bytes=sum(p.stat().st_size for p in root.iterdir() if p.is_file()),
    source_released_bytes=0, receipt=str(root)), indent=2))
