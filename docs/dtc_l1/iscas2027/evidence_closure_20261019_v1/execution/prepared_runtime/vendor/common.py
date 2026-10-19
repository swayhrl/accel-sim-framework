"""Isolated output helpers for the reused guard. PREPARED_NOT_TESTED.

No historic project paths, process creation, admission or dispatch authority.
"""
import json
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x' if exclusive else 'w') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
