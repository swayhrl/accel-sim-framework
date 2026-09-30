#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import time
import traceback
from pathlib import Path

import torch

from common import ATOL, RTOL, compare_outputs, fixed_meta, forward_backward, init_state_accounting, qualified, write_json


CASES = [
    {"name": "single_contributor", "B": 73, "V": 256, "D": 64, "ignore": "none", "repeats": 1},
    {"name": "multi_contributor_same_tile", "B": 384, "V": 256, "D": 64, "ignore": "none", "repeats": 1},
    {"name": "v_tail", "B": 192, "V": 259, "D": 64, "ignore": "none", "repeats": 1},
    {"name": "d_tail", "B": 192, "V": 256, "D": 70, "ignore": "none", "repeats": 1},
    {"name": "ignore_mixture", "B": 257, "V": 259, "D": 70, "ignore": "mixed", "repeats": 1},
    {"name": "all_ignore_zero_valid", "B": 257, "V": 259, "D": 70, "ignore": "all", "repeats": 1},
    {"name": "concurrent_arrival_repeats", "B": 1024, "V": 256, "D": 64, "ignore": "none", "repeats": 8},
]


def clone_output(value):
    return tuple(t.detach().clone() for t in value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    raw = args.root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    result = {
        "stage": "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1",
        "status": "RUNNING",
        "atol": ATOL,
        "rtol": RTOL,
        "fixed_meta": fixed_meta(),
        "cases": [],
    }
    rows = []
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable")
        props = torch.cuda.get_device_properties(0)
        if (props.major, props.minor) != (8, 9):
            raise RuntimeError(f"expected SM89, got {props.major}.{props.minor}")
        for case_index, case in enumerate(CASES):
            torch.manual_seed(7000 + case_index)
            torch.cuda.manual_seed_all(7000 + case_index)
            B, V, D = case["B"], case["V"], case["D"]
            hidden = (torch.randn(B, D, device="cuda:0", dtype=torch.bfloat16) / math.sqrt(D)).contiguous()
            weight = (torch.randn(V, D, device="cuda:0", dtype=torch.bfloat16) / math.sqrt(D)).contiguous()
            labels = torch.randint(0, V, (B,), device="cuda:0", dtype=torch.long)
            if case["ignore"] == "mixed":
                labels[::3] = -100
            elif case["ignore"] == "all":
                labels.fill_(-100)
            case_record = {
                **case,
                "valid_labels": int((labels != -100).sum().cpu()),
                "init_state": init_state_accounting(V, D),
                "runs": [],
            }
            for repeat in range(case["repeats"]):
                started = time.perf_counter()
                reference = clone_output(forward_backward("C0", hidden, weight, labels))
                candidate = clone_output(forward_backward("C1", hidden, weight, labels))
                torch.cuda.synchronize()
                metrics = compare_outputs(candidate, reference)
                ok = qualified(metrics)
                if case["ignore"] == "all":
                    for output in (reference[1], reference[2], candidate[1], candidate[2]):
                        ok = ok and bool((output == 0).all().cpu())
                run = {
                    "repeat": repeat,
                    "qualified": ok,
                    "wall_ms": (time.perf_counter() - started) * 1000,
                    "metrics": metrics,
                }
                case_record["runs"].append(run)
                for metric_name, metric in metrics.items():
                    rows.append({
                        "case": case["name"],
                        "repeat": repeat,
                        "B": B,
                        "V": V,
                        "D": D,
                        "valid_labels": case_record["valid_labels"],
                        "metric": metric_name,
                        "qualified": metric.get("allclose"),
                        "finite": metric.get("finite"),
                        "both_nan": metric.get("both_nan", False),
                        "max_abs": metric.get("max_abs", ""),
                        "mean_abs": metric.get("mean_abs", ""),
                        "max_rel": metric.get("max_rel", ""),
                        "cosine_similarity": metric.get("cosine_similarity", ""),
                        "rtol": RTOL,
                        "atol": ATOL,
                    })
                if not ok:
                    raise RuntimeError(f"directed qualification failed: {case['name']} repeat {repeat}")
                del reference, candidate
                gc.collect()
            result["cases"].append(case_record)
            del hidden, weight, labels
            gc.collect()
            torch.cuda.empty_cache()
        result["status"] = "PASS"
        result["case_count"] = len(CASES)
        result["pair_runs"] = sum(case["repeats"] for case in CASES)
        write_json(raw / "DIRECTED_TESTS.json", result)
        with (raw / "DIRECTED_TESTS.tsv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(json.dumps({"status": "PASS", "cases": len(CASES), "pair_runs": result["pair_runs"]}))
    except Exception as exc:
        result.update({"status": "FAIL", "error": repr(exc), "traceback": traceback.format_exc()})
        write_json(raw / "DIRECTED_TESTS_FAILURE.json", result)
        raise
    finally:
        if torch.cuda.is_initialized():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
