#!/usr/bin/env python3
"""Deterministic CPU-only validation of committed canary receipts."""
import csv
import hashlib
import json
from pathlib import Path

from canary import PACK, SOURCES, compare, identity, sha, write_json

def read_tsv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def main():
    final = json.loads((PACK / "FINAL_DECISION.json").read_text())
    raw = Path(final["raw_local"])
    checks = {}
    results = {}
    comparisons = []
    for point in ("MP02", "MP03"):
        a = json.loads((raw / f"{point}_A.json").read_text())
        b = json.loads((raw / f"{point}_B.json").read_text())
        results[point] = (a,b)
        checks[f"{point}_batch"] = a["batch_size"] == b["batch_size"] == (1 if point == "MP02" else 4)
        checks[f"{point}_source_rows"] = [r["source_id"] for r in a["formal_rows"]] == [r["source_id"] for r in b["formal_rows"]] == SOURCES[:1 if point == "MP02" else 4]
        checks[f"{point}_a_identity"] = identity(a)
        checks[f"{point}_b_identity"] = identity(b)
        c = compare(point,a,b)
        comparisons.append(c)
        checks[f"{point}_correctness"] = c[0]
        for mode,result in (("A",a),("B",b)):
            names = result["kernel_names"]
            expected = hashlib.sha256("\n".join(names).encode()).hexdigest()
            recorded = json.loads((PACK / "KERNEL_INVENTORY_SHA256.json").read_text())[f"{point}_{mode}"]
            checks[f"{point}_{mode}_kernel_sha"] = expected == recorded
            checks[f"{point}_{mode}_bf16_projection"] = any("bf16" in n.lower() and ("gemm" in n.lower() or "gemvx" in n.lower()) for n in names)
            checks[f"{point}_{mode}_compiled_submodule"] = any(x["name"] == "model" and x["class"] == "Qwen2Model" and not x["do_not_compile"] and x["aot_compiled_fn"] for x in result["runtime_identity"]["compiled_modules"])
    expected_rows = sum(len(c[2]) for c in comparisons)
    for name in ("TOKEN_COMPARISON.tsv","LOGPROB_DELTA_BY_STEP.tsv","FREE_RUNNING_CORRECTNESS_BY_ROW_STEP.tsv"):
        rows = read_tsv(PACK / name)
        checks[f"{name}_row_count"] = len(rows) == expected_rows == 160
        checks[f"{name}_all_pass"] = all(row.get("pass", "True") == "True" and row.get("token_pass", "True") == "True" and row.get("logprob_pass", "True") == "True" and row.get("mapping_pass", "True") == "True" and row.get("shape_order_pass", "True") == "True" for row in rows)
    index = read_tsv(PACK / "RAW_INDEX.tsv")
    raw_roots = [raw,raw.parent / "20261002T044649Z",raw.parent / "20261002T045024Z"]
    checks["raw_index_complete"] = {row["local_path"] for row in index} == {str(p) for root in raw_roots for p in root.iterdir() if p.is_file()}
    checks["raw_hashes"] = all(Path(row["local_path"]).stat().st_size == int(row["size_bytes"]) and sha(Path(row["local_path"])) == row["sha256"] for row in index)
    checks["decision"] = final["decision"] == "MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY" and final["automatic_next_goal"] is False
    budget = json.loads((PACK / "GPU_ACTIVE_BUDGET.json").read_text())
    checks["gpu_budget"] = budget["within_cap"] and budget["gpu_active_seconds_conservative_wall"] <= 120
    result = {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"raw":str(raw)}
    write_json(PACK / "TESTS.json",result)
    print(json.dumps({"status":result["status"],"checks":len(checks)}))
    if result["status"] != "PASS":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
