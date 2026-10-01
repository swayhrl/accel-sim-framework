"""Analytic illustration only: no C16 trace, GPU, or timing model is used.

Two policies have identical per-class occupancy at pass boundaries, but
one continually replaces its lines and the other retains a fixed subset.
The fixed-subset model assumes non-selected lines cannot evict protected
lines; it is not claimed to model CUDA persistence or Talus.
"""
from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any


def illustrate(classes: int = 2, lines_per_class: int = 8,
               quota_per_class: int = 2, passes: int = 3) -> dict[str, Any]:
    if not (classes > 0 and 0 < quota_per_class < lines_per_class and passes >= 2):
        raise ValueError("Require classes>0, 0<quota<lines_per_class, passes>=2")
    lru: list[OrderedDict[int, None]] = [OrderedDict() for _ in range(classes)]
    stable: list[set[int]] = [set() for _ in range(classes)]
    records: list[dict[str, Any]] = []
    for step in range(passes):
        hits_lru = hits_stable = 0
        for cls in range(classes):
            for line in range(lines_per_class):
                if line in lru[cls]:
                    hits_lru += 1
                    lru[cls].move_to_end(line)
                else:
                    if len(lru[cls]) == quota_per_class:
                        lru[cls].popitem(last=False)
                    lru[cls][line] = None
                if line in stable[cls]:
                    hits_stable += 1
                elif line < quota_per_class:
                    stable[cls].add(line)
                # Remaining lines bypass the protected subset in this toy model.
        records.append({
            "pass": step, "warmup": step == 0,
            "references": classes * lines_per_class,
            "class_quota_lru_hits": hits_lru,
            "fixed_subset_hits": hits_stable,
            "lru_occupancy_by_class": [len(x) for x in lru],
            "fixed_subset_occupancy_by_class": [len(x) for x in stable],
        })
    for row in records[1:]:
        assert row["class_quota_lru_hits"] == 0
        assert row["fixed_subset_hits"] == classes * quota_per_class
        assert row["lru_occupancy_by_class"] == row["fixed_subset_occupancy_by_class"]
    return {
        "status": "ANALYTIC_ILLUSTRATION_ONLY_NOT_C16_RESULT",
        "parameters": {"classes": classes, "lines_per_class": lines_per_class,
                       "quota_per_class": quota_per_class, "passes": passes},
        "records": records,
        "omitted": ["set placement", "sectoring", "L1 filtering", "request order",
                    "MSHR", "latency", "ordinary-traffic interference"],
    }


if __name__ == "__main__":
    print(json.dumps(illustrate(), ensure_ascii=False, indent=2))
