"""A65-only outputs; original A61 input tree is never a write destination."""
import os
from pathlib import Path
import hashlib
import json
import time

W = Path(__file__).resolve().parents[2]
OLD = Path('/data/c16/aiarch_a61_igb_small_gnn_native_109_v1')
ROOT = Path('/data/c16/aiarch_a65_igb_small_compiled_numeric_109_v1')
R = ROOT / 'resume_20261016'
CLEANUP = Path('/data/c16/storage_cleanup_20261016_lane_m_first_batch_v1')
os.sched_setaffinity(0, [0, 2, 4, 6])


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def save(name, value):
    p = R / name
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    os.replace(tmp, p)


def event(phase, **kw):
    data = {'phase': phase, 'epoch': time.time(), **kw}
    print(json.dumps(data), flush=True)
    with (R / 'events.jsonl').open('a') as f:
        f.write(json.dumps(data) + '\n')


def allocated():
    # Count new inode allocations once; package symlinks never include old payloads.
    seen = set()
    total = 0
    for root in [ROOT, W, CLEANUP]:
        for p in root.rglob('*'):
            st = p.lstat()
            key = (st.st_dev, st.st_ino)
            if key not in seen:
                seen.add(key)
                total += st.st_blocks * 512
    return total
