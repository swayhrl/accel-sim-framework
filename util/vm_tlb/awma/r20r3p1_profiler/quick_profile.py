#!/usr/bin/env python3
"""CPU-only exploratory print of the single repaired NSYS SQLite kernel sequence."""

import collections
import sqlite3
import sys


db = sqlite3.connect(sys.argv[1])
ranges = db.execute("SELECT text,start,end FROM NVTX_EVENTS ORDER BY start").fetchall()
for label, a, b in ranges:
    if "_T" not in label:
        continue
    rows = db.execute(
        "SELECT k.start,k.end,s.value,k.graphNodeId FROM CUPTI_ACTIVITY_KIND_KERNEL k "
        "LEFT JOIN StringIds s ON s.id=k.demangledName WHERE k.start>=? AND k.end<=? ORDER BY k.start", (a, b)).fetchall()
    print(label, "rows", len(rows), "time_us", sum((z[1]-z[0]) / 1000 for z in rows))
    unique = collections.Counter((str(z[2]).split("(")[0].split("::")[-1]) for z in rows)
    print("COUNTS", unique)
    for i, (start, end, name, node) in enumerate(rows):
        print(i, round((end-start)/1000, 3), str(name).split("(")[0].split("::")[-1], node)
