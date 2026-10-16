#!/usr/bin/python3
"""Consume Lane-5's actual published RESULTS.csv/PAIR_RECEIPT without a new producer schema."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
from result_intake import canonical_sha, require, digest_ok, REQUIRED_GATES, RELEASE_GATES
from acceptance_gate import load_current_acceptance, AcceptanceSnapshot

REPORT = "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/"


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def read_native_packet(repo, adapter, acceptance=None):
    # No fallback to the old R0 certificate, producer or result paths.
    for key in ("qualification_path", "producer_publication", "producer_contract_path", "current_acceptance"):
        require(key in adapter, "Explicit repaired-release adapter field required: " + key)
    if acceptance is None:
        acceptance = load_current_acceptance(repo, adapter["current_acceptance"])
    require(isinstance(acceptance, AcceptanceSnapshot), "Current acceptance context required")
    acceptance.assert_fresh()
    bindings = []
    def published(commit, path):
        require(digest_ok(commit, 40), "Exact source/publication SHA required")
        data = subprocess.check_output(["git", "-C", str(repo), "show", commit + ":" + path])
        bindings.append({"publication_commit": commit, "path": path, "sha256": hashlib.sha256(data).hexdigest()})
        return data
    qp = adapter["qualification_publication"]
    qbytes = published(qp, adapter["qualification_path"])
    q = json.loads(qbytes)
    require(q["status"] == "INDEPENDENTLY_QUALIFIED" and q["qualified_by"] == "lane5", "No independent release certificate")
    require(q["evidence_kind"] == "PRODUCTION_DRIVEN", "Not production qualification")
    # Gate completeness is checked after current acceptance, so revoked old
    # pairs are classified by supersession before legacy fixture details.
    gate_cache = {}
    for gate in q["gates"].values():
        path = gate["evidence_path"]
        require("docs/ep_l2/" in path, "Unmapped qualification evidence path")
        path = path[path.index("docs/ep_l2/"):]
        if path not in gate_cache: gate_cache[path] = published(qp, path)
        require(hashlib.sha256(gate_cache[path]).hexdigest() == gate["evidence_sha256"], "Qualification evidence digest")
    producer = json.loads(published(adapter["producer_publication"], adapter["producer_contract_path"]))
    for key in ("core_source_commit", "framework_source_commit", "binary_sha256"):
        require(q[key] == producer[key], "Certificate/producer release mismatch")
    runs = []
    for item in adapter["native_pairs"]:
        commit, base = item["publication_commit"], item["pair_repository_path"].rstrip("/")
        report = json.loads(published(commit, REPORT + "RECEIPT.json"))
        require(report["lane_id"] == 5, "Wrong result producer")
        names = [a if isinstance(a, str) else a["path"] for a in report["artifacts"]]
        require(any(base == p.rstrip("/") or base.startswith(p.rstrip("/") + "/") for p in names), "Pair not listed in Lane-5 publication")
        pair = json.loads(published(commit, base + "/PAIR_RECEIPT.json"))
        rows = list(csv.DictReader(io.StringIO(published(commit, base + "/RESULTS.csv").decode())))
        require(len(rows) == len(pair["results"]) == len(pair["specs"]) == 2, "Pair cardinality")
        for row, result, spec in zip(rows, pair["results"], pair["specs"]):
            require(row["workload"] == pair["workload"], "Pair workload mismatch")
            ident = spec["identity"]
            require(row["run_key"] == result["run_key"] == canonical_sha(ident), "Run identity mismatch")
            for key in ("core_source_commit", "framework_source_commit", "binary_sha256", "runtime_config_sha256", "trace_content_sha256"):
                require(row[key] == ident[key], "CSV identity mismatch: " + key)
            for key in ("feature_vector", "ideal_vector", "epoch_range"):
                require(json.loads(row[key]) == ident[key], "CSV structured identity mismatch")
            require(result["status"] == row["status"], "CSV status mismatch")
            if result["status"] != "COMPLETE_VALID":
                runs.append({"workload": row["workload"], "mode": row["mode"], "status": row["status"],
                             "reason": result.get("detail"), "original_row": row, "original_result": result})
                continue
            require(result["identity"] == ident, "Spec/result identity mismatch")
            acceptance.check_run({"run_key": row["run_key"], "identity": ident, "workload": row["workload"],
                                  "mode": row["mode"], "status": row["status"], "raw_log_sha256": row["raw_log_sha256"],
                                  "summary": result["summary"]})
            require(RELEASE_GATES <= q.get("gates", {}).keys(), "Missing repaired production gates")
            mode = producer["modes"][row["mode"]]
            require(ident["runtime_config_sha256"] == mode["runtime_config_sha256"], "Not the release exact ordered config")
            require(ident["feature_vector"] == mode["feature_vector"] and ident["ideal_vector"] == mode["ideal_vector"], "release mode vector mismatch")
            require(ident["feature_vector"] in q["qualified_feature_vectors"], "Unqualified feature vector")
            audit = result["audit"]
            require(audit["qualified_release_sha256"] == hashlib.sha256(qbytes).hexdigest(), "Different qualification bytes")
            require(audit["configs"] == mode["ordered_config_manifest"], "Ordered config audit mismatch")
            require(canonical_sha({"ordered_configs": audit["configs"], "auxiliary_assets": audit["auxiliary_assets"],
                                   "environment": spec.get("environment", {})}) == ident["runtime_config_sha256"], "Config/aux/environment hash recipe")
            require(canonical_sha(audit["traces"]) == ident["trace_content_sha256"], "Trace content-index hash recipe")
            root = result.get("result_directory") or result.get("allocation", {}).get("result_directory")
            if root is None:
                root = str(Path(adapter["result_root"]) / row["run_key"])
            root = Path(root)
            require(file_hash(root / "accel-sim.out") == ident["binary_sha256"], "Frozen executable hash mismatch")
            require(file_hash(root / "raw.log") == row["raw_log_sha256"] == result["raw_log_sha256"], "Raw payload mismatch")
            for index, record in enumerate(audit["configs"]):
                require(file_hash(root / f"config-{index}.config") == record["sha256"], "Frozen runtime config changed")
            summary = result["summary"]
            require(result["validation"]["status"] == "PASS" and summary["hardware_drained"] is True, "Unvalidated summary")
            require(summary["slices"] == 64 and summary["requester_exact_once_audit"] is True and summary["data_correctness_qualification"] is True,
                    "Incomplete identity/scoped reference gate")
            for k in ("live_descriptors", "live_line_mshrs", "live_wad", "pending_lower_reads", "pending_returns", "pending_responses", "transient_payloads"):
                require(summary[k] == 0, "Terminal resource leak")
            require(summary["wb_created"] == summary["wb_lower_accepted"] == summary["wb_completed"], "WB milestone leak")
            require(summary["payload_free"] + sum(summary["payload_roles"].values()) == summary["payload_capacity"] == 1168 * 64, "Payload budget")
            for k in ("cycles", "instructions"):
                require(summary[k] == int(row[k]), "CSV/native total mismatch")
            require(all(g["status"] == "PASS" and g["production_driven"] is True for g in q["gates"].values()), "Qualification gates")
            require(q["data_correctness_scope"] == "SYMBOLIC_32B_SECTOR_VERSIONS_AND_REQUEST_IDENTITY_NOT_NUMERIC_SASS_PAYLOAD", "Do not broaden data scope")
            # The only excluded config record is the exact hash-checked mode
            # overlay, so the common fingerprint is derived, not guessed.
            common = canonical_sha({"configs_before_mode_overlay": audit["configs"][:-1],
                                    "auxiliary_assets": audit["auxiliary_assets"], "environment": spec.get("environment", {})})
            runs.append({"workload": row["workload"], "mode": row["mode"], "status": row["status"],
                         "run_key": row["run_key"], "identity": ident, "summary": summary,
                         "raw_log_sha256": result["raw_log_sha256"], "effective_base_config_sha256": common,
                         "validation": {k: True for k in REQUIRED_GATES},
                         "validation_mapping": "repaired release independent certificate + current scientific acceptance + native summary/identity/resource checks above; not application full-byte validation",
                         "numeric_payload_validation": "UNAVAILABLE_SASS_DATALESS", "original_row": row,
                         "original_result": result, "original_spec": spec})
    acceptance.assert_fresh()
    return {"scientific_acceptance": acceptance.provenance(), "evidence_kind": "FUNCTIONAL_IMPLEMENTATION", "qualification": q, "runs": runs,
            "source_bindings": bindings, "mapping_source": "native_pair_intake.py"}
