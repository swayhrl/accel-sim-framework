#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a16_latpc_variant_lib import build_variant_manifest, load_latest_selected_workload, validate_noop_manifest, write_variant_manifest

REPO_ROOT = Path(__file__).resolve().parents[2]
Path(REPO_ROOT / ".local_reports").mkdir(exist_ok=True)
Path(REPO_ROOT / ".local_logs").mkdir(exist_ok=True)

TS = time.strftime("%Y%m%d_%H%M%S")
START = time.time()
START_ISO = time.strftime("%Y-%m-%dT%H:%M:%S%z")
MANIFEST = REPO_ROOT / f".local_reports/A16B_latpc_variant_manifest_{TS}.json"
REPORT = REPO_ROOT / f".local_reports/A16B_latpc_variant_slot_{TS}.md"
LOG = REPO_ROOT / f".local_logs/A16B_latpc_variant_slot_{TS}.log"

status = "PASS"
blocker = "none"
manifest = {}
diffs: list[str] = []
with LOG.open("w") as f:
    f.write(f"A16B LATPC variant slot\nStart: {START_ISO}\n")
try:
    selected = load_latest_selected_workload()
    manifest = build_variant_manifest(selected)
    ok, diffs = validate_noop_manifest(manifest)
    if not ok:
        status = "FAIL_NOOP_NOT_EQUIVALENT"
        blocker = "baseline and latpc_noop inputs differ: " + ",".join(diffs)
    write_variant_manifest(MANIFEST, manifest)
except FileNotFoundError:
    status = "BLOCKED_NO_A16A"
    blocker = "missing A16A selected workload JSON"

end_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = int(time.time() - START)
REPORT.write_text(f"""# A16B LATPC No-op Variant Slot

- Status: {status}
- Start time: {START_ISO}
- End time: {end_iso}
- Wall clock seconds: {wall}
- Command: `python3 scripts/accelsim/a16_latpc_variant_slot.py`
- Log: `{LOG.relative_to(REPO_ROOT)}`
- Manifest JSON: `{MANIFEST.relative_to(REPO_ROOT)}`
- Blocker: {blocker}

## Equivalence Check

- Baseline and latpc_noop use identical simulator binary, kernelslist, configs, and simulator args.
- Differing input fields: `{','.join(diffs) if diffs else 'none'}`
- Variant metadata is not passed into simulator config.

## Limitations

A16B creates a no-op metadata slot only. It does not implement LATPC mechanisms.

## Git Status

```
{subprocess.getoutput('git status --short')}
```
""")

print(f"A16B report: {REPORT.relative_to(REPO_ROOT)}")
print(f"A16B manifest: {MANIFEST.relative_to(REPO_ROOT)}")
print(f"A16B status: {status}")
sys.exit(0 if status in {"PASS", "PASS_WITH_WARNINGS", "BLOCKED_NO_A16A"} else 1)
