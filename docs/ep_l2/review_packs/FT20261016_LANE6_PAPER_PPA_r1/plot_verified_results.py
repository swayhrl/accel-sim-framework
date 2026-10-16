#!/usr/bin/python3
"""Fail-closed plot intake for first WB comparisons from published Lane-4/5 bundles."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

COORD = "6c136e2a56a008695f8c8b815723bf8f1a760db9"
KINDS = {"FUNCTIONAL_IMPLEMENTATION", "ORACLE_ASSISTED_IMPLEMENTATION", "IDEAL_DIAGNOSTIC"}
FEATURES = {"unified_wb", "tvd", "ro", "oracle_ro"}
IDEALS = {"I_WB", "I_META", "I_READ_HIT"}
GATES = {"normal_exit", "parser_success", "terminal_clean", "payload_consistent", "request_identity_check", "data_version_check"}
COHORTS = {"development": ["convolutionSeparable", "FWT_7_21", "cfd_097k", "vectorAdd_4M", "sad"],
           "validation": ["btree", "dwt2d"], "scan": ["scan"]}


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def full_hash(value, width):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{%d}" % width, value) is not None


def validate_manifest(m, kind):
    require(kind in KINDS and m.get("evidence_kind") == kind, "Evidence kind mismatch or shadow/historical input")
    require(m.get("status") == "COMPLETE_VALID", "Incomplete runtime manifest")
    for key in ("core_source_commit", "framework_source_commit"):
        require(full_hash(m.get(key), 40), "Missing full runtime source: " + key)
        require(m[key] != COORD, "Coordination commit is not runtime source")
    for key in ("binary_sha256", "config_sha256", "trace_sha256", "raw_log_sha256"):
        require(full_hash(m.get(key), 64), "Missing full runtime digest: " + key)
    for name, keys in (("feature_vector", FEATURES), ("ideal_vector", IDEALS)):
        vector = m.get(name)
        require(isinstance(vector, dict) and keys <= vector.keys(), "Incomplete explicit " + name)
        require(all(type(v) is bool for v in vector.values()), "Non-boolean mode vector")
    if kind != "IDEAL_DIAGNOSTIC":
        require(not any(m["ideal_vector"].values()), "Ideal bits cannot enter implementation plot")
    if kind == "FUNCTIONAL_IMPLEMENTATION":
        require(not m["feature_vector"]["oracle_ro"], "Oracle cannot enter ordinary implementation plot")
    require(isinstance(m.get("epoch_range"), dict) and bool(m["epoch_range"]), "Missing epoch identity")
    config = m.get("effective_config")
    require(isinstance(config, dict) and bool(config), "Missing effective base config")
    require(GATES <= m.get("validation", {}).keys() and all(m["validation"][k] is True for k in GATES), "Incomplete independent correctness/terminal gates")
    for k in ("run_id", "workload", "mode"):
        require(isinstance(m.get(k), str) and bool(m[k]), "Missing row identity " + k)
    for k in ("cycles", "instructions"):
        require(str(m.get(k, "")).isdigit() and int(m[k]) > 0, "Invalid " + k)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("adapter", type=Path)
    p.add_argument("--framework-repo", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    a = json.loads(args.adapter.read_text())
    require(a.get("schema") == "EP_L2_LANE6_VERIFIED_RESULT_ADAPTER_V1", "Unknown adapter schema")
    require(a.get("coordination_commit") == COORD, "Wrong execution contract")
    kind = a.get("evidence_kind")
    require(kind in KINDS, "Do not plot shadow/historical speedup as new results")
    require(a.get("source_lane") in (4, 5), "Expected Lane 4/5 result producer")
    require(kind == "IDEAL_DIAGNOSTIC" or a["source_lane"] == 5, "Functional results require Lane-5 validation")
    revision = a.get("publication_commit")
    require(full_hash(revision, 40), "Missing upstream publication commit")
    bound = {}
    for prefix in ("receipt", "bundle"):
        require(full_hash(a.get(prefix + "_sha256"), 64), "Missing " + prefix + " digest")
        data = subprocess.check_output(["git", "-C", str(args.framework_repo), "show", revision + ":" + a[prefix + "_repository_path"]])
        require(digest(data) == a[prefix + "_sha256"], "Published " + prefix + " hash mismatch")
        bound[prefix] = json.loads(data)
    receipt, bundle = bound["receipt"], bound["bundle"]
    require(receipt.get("lane_id") == a["source_lane"] and receipt.get("coordination_commit") == COORD, "Receipt producer mismatch")
    artifacts = {r if isinstance(r, str) else r.get("path") for r in receipt.get("artifacts", [])}
    require(a["bundle_repository_path"] in artifacts, "Receipt does not bind bundle")
    def local(path):
        q = Path(path)
        return q if q.is_absolute() else args.adapter.resolve().parent / q
    csv_data = local(a["results_csv"]).read_bytes()
    require(digest(csv_data) == bundle["results_csv_sha256"], "Results CSV hash mismatch")
    import io
    rows = list(csv.DictReader(io.StringIO(csv_data.decode())))
    require(rows, "No result rows")
    cohort = COHORTS[a["cohort"]]
    base, candidate = a["baseline_mode"], a["candidate_mode"]
    if kind != "IDEAL_DIAGNOSTIC":
        require((base, candidate) in {( "B16_BANKED", "U_WB16"), ("B8_BANKED", "U_WB8")}, "This tool only accepts reviewed first-WB comparisons")
        require(kind == "FUNCTIONAL_IMPLEMENTATION", "Oracle comparisons need a separate reviewed transition contract")
    by_key, run_ids = {}, set()
    for row in rows:
        require(row["status"] == "COMPLETE_VALID" and row["evidence_kind"] == kind, "Non-complete/mixed-kind CSV row")
        run_id = row["run_id"]
        require(run_id not in run_ids, "Duplicate run ID")
        run_ids.add(run_id)
        data = local(a["run_manifests"][run_id]).read_bytes()
        require(digest(data) == bundle["run_manifest_sha256s"][run_id], "Runtime manifest hash mismatch")
        m = json.loads(data)
        validate_manifest(m, kind)
        for key in ("run_id", "workload", "mode", "cycles", "instructions"):
            require(str(m[key]) == row[key], "CSV/runtime manifest row mismatch: " + key)
        key = (row["workload"], row["mode"])
        require(key not in by_key, "Duplicate workload/mode")
        by_key[key] = m
    require(set(by_key) == {(w, m) for w in cohort for m in (base, candidate)}, "Missing/extra cohort rows; no performance selection")
    plotted = []
    for w in cohort:
        b, c = by_key[w, base], by_key[w, candidate]
        for field in ("trace_sha256", "epoch_range"):
            require(b[field] == c[field], "Unmatched workload/epoch control")
        require(b["instructions"] == c["instructions"], "Instruction count mismatch")
        require(b["effective_config"] == c["effective_config"], "Base settings differ outside explicit feature/ideal vectors")
        if kind != "IDEAL_DIAGNOSTIC":
            for field in ("core_source_commit", "framework_source_commit", "binary_sha256"):
                require(b[field] == c[field], "First-WB comparison is not same-source/binary")
            require(not any(b["feature_vector"].values()), "Baseline contains a functional feature")
            require(c["feature_vector"]["unified_wb"] and sum(c["feature_vector"].values()) == 1, "Unexpected candidate features")
            config = b["effective_config"]
            n = 1168 if base == "B16_BANKED" else 1160
            require(config.get("payload_slots_per_slice") == n and config.get("banks") == 4 and config.get("line_ops_per_bank_cycle") == 1, "Budget/port mismatch")
        else:
            require(not any(b["ideal_vector"].values()) and any(c["ideal_vector"].values()), "Ideal comparison lacks explicit diagnostic transition")
            require(b["feature_vector"] == c["feature_vector"], "Diagnostic changes functional features")
        plotted.append({"workload": w, "speedup": int(b["cycles"]) / int(c["cycles"]),
                        "baseline_run_id": b["run_id"], "candidate_run_id": c["run_id"]})
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = args.output_dir
    require(not out.exists(), "Use a new immutable output directory")
    out.mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(plotted)), [r["speedup"] for r in plotted], color="#3b6f8f")
    ax.axhline(1, color="black", linewidth=.6)
    ax.set_xticks(range(len(plotted)), cohort, rotation=25, ha="right")
    ax.set_ylabel("Baseline cycles / candidate cycles")
    ax.set_title(kind + ": " + base + " vs " + candidate)
    fig.tight_layout()
    fig.savefig(out / (kind + ".svg"), metadata={"Date": None})
    fig.savefig(out / (kind + ".pdf"), metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    output = {"evidence_kind": kind, "source_lane": a["source_lane"], "publication_commit": revision,
              "adapter_sha256": digest(args.adapter.read_bytes()), "receipt_sha256": a["receipt_sha256"],
              "bundle_sha256": a["bundle_sha256"], "results_csv_sha256": digest(csv_data),
              "rows": plotted, "geomean_all_predeclared_workloads": math.prod(r["speedup"] for r in plotted) ** (1 / len(plotted)),
              "runtime_manifests": by_manifest_list(by_key)}
    (out / "FIGURE_INPUT_MANIFEST.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pairs": len(plotted), "kind": kind, "output_dir": str(out)}))


def by_manifest_list(by_key):
    return [by_key[key] for key in sorted(by_key)]


if __name__ == "__main__":
    main()
