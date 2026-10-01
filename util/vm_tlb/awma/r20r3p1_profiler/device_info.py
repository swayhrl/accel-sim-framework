#!/usr/bin/env python3
"""One locked device-property receipt, not a performance sweep."""

import json
import os
import warp as wp

if os.environ.get("R20R3P1_GPU_LOCK_HELD") != "1":
    raise RuntimeError("GPU campaign lock receipt absent")
wp.init()
d = wp.get_device("cuda:0")
print(json.dumps({"name": d.name, "arch": d.arch, "sm_count": getattr(d, "sm_count", None),
                  "multiprocessor_count": getattr(d, "multiprocessor_count", None),
                  "max_threads_per_block": getattr(d, "max_threads_per_block", None)}, sort_keys=True))
