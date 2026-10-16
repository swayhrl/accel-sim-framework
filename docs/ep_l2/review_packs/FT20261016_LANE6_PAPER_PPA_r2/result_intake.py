#!/usr/bin/python3
"""Normalize complete WB pairs without dropping failures or requiring absent SASS bytes.

The normalized packet must be hash-bound by a Lane-5 publication bundle.
This does not run/qualify the simulator or modify the shared registry.
"""
import hashlib
import json
import math

WORKLOADS = ["convolutionSeparable", "FWT_7_21", "cfd_097k", "vectorAdd_4M", "sad"]
BOOL_FEATURES = {"finite_wbuf", "unified_wb", "tvd", "ro", "adaptive_policy"}
NUM_FEATURES = {"wbuf_entries", "payload_capacity_per_slice", "bank_count", "ops_per_bank_cycle"}
IDEALS = {"wb", "meta", "read_hit"}
REQUIRED_GATES = {"normal_exit", "parser_success", "sector_version_reference",
                  "requester_exact_once", "payload_identity", "terminal_clean", "wb_milestone_closure"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def digest_ok(value, n):
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value)


def ro_bits(features):
    keys = ("ro_tag_detach", "ro_line_mshr_bypass")
    if not features["ro"] and not any(k in features for k in keys):
        return {"ro_tag_detach": False, "ro_line_mshr_bypass": False,
                "mapping": "R0_EXPLICIT_RO_OFF_COMPATIBILITY_VIEW_IDENTITY_UNCHANGED"}
    require(all(type(features.get(k)) is bool for k in keys), "RO requires separate explicit detach/bypass bits")
    return {k: features[k] for k in keys}


def validate_run(m, qualification):
    require(m["status"] == "COMPLETE_VALID", "Run is not complete")
    identity = m["identity"]
    require(m["run_key"] == canonical_sha(identity), "Canonical run-key mismatch")
    for k in ("core_source_commit", "framework_source_commit"):
        require(digest_ok(identity.get(k), 40), "Missing source SHA")
    for k in ("binary_sha256", "runtime_config_sha256", "trace_content_sha256"):
        require(digest_ok(identity.get(k), 64), "Missing runtime identity digest")
    require(digest_ok(m.get("raw_log_sha256"), 64), "Missing raw hash")
    require(isinstance(identity.get("epoch_range"), dict) and bool(identity["epoch_range"]), "Missing epoch")
    f, ideal = identity["feature_vector"], identity["ideal_vector"]
    require(BOOL_FEATURES <= f.keys() and NUM_FEATURES <= f.keys(), "Incomplete feature vector")
    require(all(type(f[k]) is bool for k in BOOL_FEATURES), "Feature boolean types")
    require(all(type(f[k]) is int for k in NUM_FEATURES), "Resource parameter types")
    require(IDEALS <= ideal.keys() and all(type(v) is bool for v in ideal.values()), "Incomplete ideal vector")
    ro_bits(f)  # Compatibility mapping is a view: never change the canonical key.
    require(qualification.get("status") == "INDEPENDENTLY_QUALIFIED", "Producer-ready is not independent qualification")
    for k in ("core_source_commit", "framework_source_commit", "binary_sha256"):
        require(qualification.get(k) == identity[k], "Qualification belongs to another release")
    require(REQUIRED_GATES <= m.get("validation", {}).keys(), "Incomplete scoped verification")
    require(all(m["validation"][k] is True for k in REQUIRED_GATES), "Verification failure")
    require(m["numeric_payload_validation"] in ("UNAVAILABLE_SASS_DATALESS", "DIRECTED_KNOWN_BYTES_ONLY"),
            "Do not claim unobserved full-byte application correctness")
    summary = m["summary"]
    require(all(type(summary[k]) is int and summary[k] > 0 for k in ("cycles", "instructions")), "Invalid native totals")


def summarize(packet):
    """Return pair-level facts and every unavailable row; full-cohort mean is conditional."""
    require(packet["evidence_kind"] == "FUNCTIONAL_IMPLEMENTATION", "Ideal/shadow/oracle cannot enter WB implementation table")
    qualification = packet["qualification"]
    runs = packet["runs"]
    modes = ("B16_BANKED", "U_WB16")
    indexed, unavailable = {}, []
    for m in runs:
        w, mode = m["workload"], m["mode"]
        require(w in WORKLOADS and mode in modes, "Undeclared workload/mode")
        require((w, mode) not in indexed, "Duplicate workload/mode, including failures")
        indexed[w, mode] = m
        if m["status"] != "COMPLETE_VALID":
            unavailable.append({"workload": w, "mode": mode, "status": m["status"], "reason": m.get("reason")})
    pairs = []
    for w in WORKLOADS:
        b, c = indexed.get((w, modes[0])), indexed.get((w, modes[1]))
        for mode, m in zip(modes, (b, c)):
            if m is None:
                unavailable.append({"workload": w, "mode": mode, "status": "NOT_RECEIVED"})
        if b is None or c is None or any(m["status"] != "COMPLETE_VALID" for m in (b, c)):
            continue
        for m in (b, c):
            validate_run(m, qualification)
            f = m["identity"]["feature_vector"]
            require(f["finite_wbuf"] and f["wbuf_entries"] == 16 and f["payload_capacity_per_slice"] == 1168
                    and f["bank_count"] == 4 and f["ops_per_bank_cycle"] == 1, "Not the B16 budget/port contract")
            require(not f["ro"] and not f["tvd"] and not f["adaptive_policy"], "Unexpected functional extension")
            require(not any(m["identity"]["ideal_vector"].values()), "Enabled ideal mode in implementation")
        bi, ci = b["identity"], c["identity"]
        require(not bi["feature_vector"]["unified_wb"] and ci["feature_vector"]["unified_wb"], "Wrong feature transition")
        for k in ("core_source_commit", "framework_source_commit", "binary_sha256", "trace_content_sha256", "epoch_range"):
            require(bi[k] == ci[k], "Cross-source/binary/trace/epoch comparison")
        require(b["effective_base_config_sha256"] == c["effective_base_config_sha256"]
                and digest_ok(b["effective_base_config_sha256"], 64), "Unmatched non-mode controls")
        require(b["summary"]["instructions"] == c["summary"]["instructions"], "Instructions differ")
        pairs.append({"workload": w, "baseline_cycles": b["summary"]["cycles"], "candidate_cycles": c["summary"]["cycles"],
                      "speedup": b["summary"]["cycles"] / c["summary"]["cycles"],
                      "baseline_run_key": b["run_key"], "candidate_run_key": c["run_key"]})
    # No mean over only the early/faster completed subset.
    return {"evidence_kind": packet["evidence_kind"], "pairs": pairs, "unavailable": unavailable,
            "cohort_size": len(WORKLOADS), "whole_group_geomean": math.prod(r["speedup"] for r in pairs) ** .2 if len(pairs) == 5 else None,
            "complete": len(pairs) == 5}


def read_published_packet(repo, publication, receipt_path, receipt_sha256, bundle_path, bundle_sha256, packet_file):
    """Bind the normalized adapter to a real Lane-5 receipt and published bundle."""
    import subprocess
    from pathlib import Path
    def read(path, expected):
        data = subprocess.check_output(["git", "-C", str(repo), "show", publication + ":" + path])
        require(hashlib.sha256(data).hexdigest() == expected, "Upstream publication hash mismatch")
        return json.loads(data)
    require(digest_ok(publication, 40), "Exact upstream publication required")
    receipt = read(receipt_path, receipt_sha256)
    require(receipt["lane_id"] == 5, "Independent implementation results must come from Lane 5")
    artifacts = {a if isinstance(a, str) else a.get("path") for a in receipt["artifacts"]}
    require(any(bundle_path == p or bundle_path.startswith(p.rstrip("/") + "/") for p in artifacts), "Receipt does not name bundle")
    bundle = read(bundle_path, bundle_sha256)
    data = Path(packet_file).read_bytes()
    require(hashlib.sha256(data).hexdigest() == bundle["normalized_pair_packet_sha256"], "Unbound normalized pair payload")
    return json.loads(data)
