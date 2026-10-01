#!/usr/bin/env python3
"""CPU-only SQLite inventory for installed Nsight Systems export."""

import sqlite3
import sys


db = sqlite3.connect(sys.argv[1])
tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
for name in tables:
    if "CUDA" in name or "CUPTI" in name or "NVTX" in name or "String" in name:
        count = db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        print(f"{name}\t{count}")
        if "NVTX_EVENTS" == name:
            print("NVTX_COLUMNS", db.execute(f'PRAGMA table_info("{name}")').fetchall())
            print("NVTX_FIRST", db.execute(f'SELECT * FROM "{name}" LIMIT 5').fetchall())
        if "CUPTI_ACTIVITY_KIND_KERNEL" == name:
            print("KERNEL_COLUMNS", db.execute(f'PRAGMA table_info("{name}")').fetchall())
            print("KERNEL_FIRST", db.execute(f'SELECT * FROM "{name}" LIMIT 5').fetchall())
