#!/usr/bin/env python3
"""Read-only NSYS SQLite schema and bounded event samples."""
import sqlite3
from pathlib import Path

db = Path("/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/raw/NSYS_R19F1_FP8_CONSUMER_V1.sqlite")
conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
for (name,) in conn.execute("select name from sqlite_master where type='table' order by name"):
    print("TABLE", name)
    print("COLUMNS", [row[1] for row in conn.execute(f'pragma table_info("{name}")')])
    if name in ("NVTX_EVENTS", "CUPTI_ACTIVITY_KIND_KERNEL", "CUPTI_ACTIVITY_KIND_RUNTIME", "StringIds"):
        print("COUNT", conn.execute(f'select count(*) from "{name}"').fetchone()[0])
        for row in conn.execute(f'select * from "{name}" limit 3'):
            print("SAMPLE", row)
