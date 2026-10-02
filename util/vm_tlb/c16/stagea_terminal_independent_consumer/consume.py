#!/usr/bin/env python3
"""Independent CPU-only Stage A terminal consumer of two 164 durable raw packs."""

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import subprocess
from pathlib import Path


ORIGINAL_COMMIT = "a12bbfa4609ece57fadde107f9fd2e3bc0380cdf"
CONTINUATION_COMMIT = "f1026f499180a3b18cd1b7f9c91e63787f2398a4"
ACCEPTED_MODE_COMMIT = "9122fac5c50dbf19706636fc03978a356ffd800f"
CONT_PREEXEC = "31af510d85e89344acf6e4c519ae5f0419d50d40"
AUTHORITY = {
    "stagea_contract": "fad9da8116c8ad794f99a93f153b0866162158a4",
    "stagea_producer": "82788c2d587e86f94791d65aaa2bde28929f9303",
    "stagea_consumer": "9d82ff41132e7b1a1fdd18a287c13627fe62e5b7",
    "mode_deconflation_pass": ACCEPTED_MODE_COMMIT,
    "observer_failure": "c48331a9ea5a3f381741aad4bae91dfb0eefc2c2",
    "attribution_design": "ecd9978a719836268d1eb6625b534c8e66db1774",
    "attribution_level0": "ab3df70e3a18eea6292af71334f9a2727066c5b3",
    "dq2_original_preexec": "cfa3ba1f5cb5c236b0000ba0f5656e75e2e05b79",
    "dq2_original_result": ORIGINAL_COMMIT,
    "dq2_continuation_preexec": CONT_PREEXEC,
    "dq2_continuation_result": CONTINUATION_COMMIT,
}
INDEX = {
    "ORIGINAL": (ORIGINAL_COMMIT, "docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1/RAW_INDEX.json", "docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1/PUBLISH_RECEIPT.json", 26),
    "CONTINUATION": (CONTINUATION_COMMIT, "docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_MP03B_CONTINUATION_109_V1/RAW_INDEX.json", "docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_MP03B_CONTINUATION_109_V1/PUBLISH_RECEIPT.json", 15),
}


def git_bytes(repo, commit, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{commit}:{path}"])


def git_json(repo, commit, path):
    return json.loads(git_bytes(repo, commit, path))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv_bytes(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8")), delimiter="\t"))


def verify_pack(repo, group, root):
    commit, index_path, publish_path, expected_count = INDEX[group]
    index_bytes = git_bytes(repo, commit, index_path)
    index = json.loads(index_bytes)
    assert len(index) == expected_count
    assert len({Path(item["durable_path"]).name for item in index}) == expected_count
    listed = {Path(item["durable_path"]).name for item in index}
    assert {p.name for p in root.iterdir() if p.is_file()} == listed | {"RAW_SHA256SUMS"}
    manifest = {}
    for line in (root / "RAW_SHA256SUMS").read_text().splitlines():
        digest, filename = line.split("  ", 1)
        assert filename not in manifest
        manifest[filename] = digest
    assert set(manifest) == listed
    publish = git_json(repo, commit, publish_path)
    assert publish["status"] == "PASS_DURABLE_PUBLISH_AND_COPYBACK"
    assert publish["copyback_verify"]["status"] == "PASS"
    assert publish["copyback_verify"]["file_count"] == expected_count
    assert publish["copyback_verify"]["manifest_sha256"] == sha(root / "RAW_SHA256SUMS")
    copyback = {row["relative_path"]: row for row in publish["copyback_verify"]["files"]}
    assert set(copyback) == listed
    rows = []
    for item in sorted(index, key=lambda record: Path(record["durable_path"]).name):
        path = Path(item["durable_path"])
        assert path.parent == root and path.is_file()
        name = path.name
        actual_size, actual_sha = path.stat().st_size, sha(path)
        assert actual_size == item["size_bytes"]
        assert actual_sha == item["sha256"] == manifest[name]
        assert item["copyback_path"] and item["local_path"]
        cb = copyback[name]
        assert cb["actual_sha256"] == cb["sha256"] == actual_sha and cb["size_bytes"] == actual_size
        rows.append({"group": group, "file": name, "durable_path": str(path),
                     "expected_size_bytes": item["size_bytes"], "actual_size_bytes": actual_size,
                     "expected_sha256": item["sha256"], "actual_sha256": actual_sha,
                     "manifest_match": "PASS", "copyback_receipt_match": "PASS"})
    return rows, {"commit": commit, "index_path": index_path,
                  "index_sha256": hashlib.sha256(index_bytes).hexdigest(),
                  "payload_count": expected_count, "durable_root": str(root),
                  "durable_manifest_sha256": sha(root / "RAW_SHA256SUMS"),
                  "copyback_receipt": "PASS_IN_COMMITTED_PRODUCER_REVIEW_PACK"}


def sample_stats(samples):
    assert len(samples) == 5
    assert all(row["role"] == "FORMAL" and row["timing_role"] == "SCIENCE_FORMAL" for row in samples)
    values = [float(row["request_gpu_elapsed_ms"]) for row in samples]
    assert all(math.isfinite(value) and value > 0 for value in values)
    median = statistics.median(values)
    return {"n": 5, "median_ms": median,
            "mad_ms": statistics.median(abs(value - median) for value in values),
            "min_ms": min(values), "max_ms": max(values), "raw_ms": values}


def validate_row(row, source_id, batch_row):
    assert row["source_id"] == source_id and row["batch_row"] == batch_row
    assert row["prompt_token_count"] == 512
    assert len(row["tokens"]) == len(row["sampled_logprobs"]) == 32
    assert all(type(token) is int for token in row["tokens"])
    assert all(math.isfinite(float(value)) for value in row["sampled_logprobs"])


def compare_rows(reference, candidate, source_ids):
    assert len(reference) == len(candidate) == len(source_ids)
    comparisons = 0
    max_abs_delta = 0.0
    for index, (left, right, source_id) in enumerate(zip(reference, candidate, source_ids)):
        validate_row(left, source_id, index)
        validate_row(right, source_id, index)
        assert left["tokens"] == right["tokens"]
        for a, b in zip(left["sampled_logprobs"], right["sampled_logprobs"]):
            delta = abs(float(a) - float(b))
            max_abs_delta = max(max_abs_delta, delta)
            assert delta <= 0.05 + 0.01 * abs(float(a))
            comparisons += 1
    return comparisons, max_abs_delta


def cache_signature(root):
    return {"path": root["path"], "file_count": root.get("actual_file_count", root.get("file_count")),
            "content_sha256": root.get("actual_sha256", root.get("content_identity_sha256")),
            "files": {item["relative_path"]: (item["sha256"], item["size_bytes"]) for item in root["files"]}}


def compare_cache_snapshots(before, after):
    old, new = before["four_bound_roots"]["rows"], after["four_bound_roots"]["rows"]
    assert len(old) == len(new) == 4
    old_by = {(row["point"], row["mode"]): row for row in old}
    new_by = {(row["point"], row["mode"]): row for row in new}
    assert set(old_by) == set(new_by) == {("MP02", "A"), ("MP02", "B"), ("MP03", "A"), ("MP03", "B")}
    rows = []
    for key in sorted(old_by):
        left, right = cache_signature(old_by[key]), cache_signature(new_by[key])
        assert left == right
        rows.append({"root_id": f"{key[0]}_{key[1]}", "path": left["path"],
                     "file_count": left["file_count"], "before_sha256": left["content_sha256"],
                     "after_sha256": right["content_sha256"], "per_file_metadata_exact": "PASS", "unchanged": "PASS"})
    left, right = cache_signature(before["pre_warmup_aot_root"]), cache_signature(after["pre_warmup_aot_root"])
    assert left == right
    rows.append({"root_id": "MP03_B_AOT_PREWARMUP", "path": left["path"],
                 "file_count": left["file_count"], "before_sha256": left["content_sha256"],
                 "after_sha256": right["content_sha256"], "per_file_metadata_exact": "PASS", "unchanged": "PASS"})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    for name, commit in AUTHORITY.items():
        assert subprocess.check_output(["git", "-C", str(args.repo), "cat-file", "-t", commit], text=True).strip() == "commit", name
    raw_rows, raw_authority = [], {}
    for group, root in (("ORIGINAL", args.original), ("CONTINUATION", args.continuation)):
        rows, receipt = verify_pack(args.repo, group, root)
        raw_rows.extend(rows)
        raw_authority[group] = receipt
    assert len(raw_rows) == 41
    write_tsv(args.output / "RAW_SHA_RECALCULATION.tsv",
              ["group", "file", "durable_path", "expected_size_bytes", "actual_size_bytes", "expected_sha256", "actual_sha256", "manifest_match", "copyback_receipt_match"], raw_rows)

    original = {name: read_json(args.original / f"{name}.json") for name in ("MP02_A", "MP02_B", "MP03_A", "MP03_B")}
    continuation = read_json(args.continuation / "MP03_B.json")
    for name in ("MP02_A", "MP02_B", "MP03_A"):
        assert original[name]["point"] == name[:4] and original[name]["mode"] == name[-1]
        assert len(original[name]["warmups"]) == 2
    assert len(original["MP03_B"]["warmups"]) == len(original["MP03_B"]["formal_samples"]) == 0
    metrics = {name: sample_stats(original[name]["formal_samples"]) for name in ("MP02_A", "MP02_B", "MP03_A")}
    assert len(continuation["warmups"]) == 2 and len(continuation["formal_samples"]) == 0
    t_a, t_b = metrics["MP02_A"]["median_ms"], metrics["MP02_B"]["median_ms"]
    ratio, reduction = t_b / t_a, 1.0 - t_a / t_b
    recalc_rows = []
    for name in ("MP02_A", "MP02_B", "MP03_A", "MP03_B_ORIGINAL", "MP03_B_CONTINUATION"):
        data = metrics.get(name)
        point = "MP02" if name.startswith("MP02") else "MP03"
        mode = "A" if name.endswith("_A") else "B"
        status = "SCIENCE_VALID_B1_POINT" if point == "MP02" else ("DIAGNOSTIC_ONLY_NOT_SCIENCE_VALID_POINT_INCOMPLETE" if mode == "A" else "INCOMPLETE_EXECUTION_IDENTITY_STOP")
        recalc_rows.append({"arm": name, "point": point, "mode": mode, "science_status": status,
                            "formal_n": data["n"] if data else 0,
                            "median_ms": repr(data["median_ms"]) if data else "NA",
                            "mad_ms": repr(data["mad_ms"]) if data else "NA",
                            "min_ms": repr(data["min_ms"]) if data else "NA",
                            "max_ms": repr(data["max_ms"]) if data else "NA",
                            "ms_per_generated_token": repr(data["median_ms"] / 32) if data and point == "MP02" else "NA",
                            "raw_formal_ms_json": json.dumps(data["raw_ms"], separators=(",", ":")) if data else "[]"})
    write_tsv(args.output / "DQ2_INDEPENDENT_RECALCULATION.tsv",
              ["arm", "point", "mode", "science_status", "formal_n", "median_ms", "mad_ms", "min_ms", "max_ms", "ms_per_generated_token", "raw_formal_ms_json"], recalc_rows)

    a_ref = original["MP02_A"]["formal_samples"][0]["rows"]
    b_ref = original["MP02_B"]["formal_samples"][0]["rows"]
    step_checks, max_delta = 0, 0.0
    for name in ("MP02_A", "MP02_B"):
        for sample in original[name]["formal_samples"]:
            n, delta = compare_rows(a_ref, sample["rows"], ["TRAIN_A_DISCOVERY_00"])
            step_checks += n
            max_delta = max(max_delta, delta)
    for a, b in zip(original["MP02_A"]["formal_samples"], original["MP02_B"]["formal_samples"]):
        n, delta = compare_rows(a["rows"], b["rows"], ["TRAIN_A_DISCOVERY_00"])
        step_checks += n
        max_delta = max(max_delta, delta)
    assert step_checks == 480

    accepted_prefix = "docs/vm_tlb/review_packs/C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1/"
    accepted_tokens = read_tsv_bytes(git_bytes(args.repo, ACCEPTED_MODE_COMMIT, accepted_prefix + "TOKEN_COMPARISON.tsv"))
    accepted_logprobs = read_tsv_bytes(git_bytes(args.repo, ACCEPTED_MODE_COMMIT, accepted_prefix + "LOGPROB_DELTA_BY_STEP.tsv"))
    tok_map = {(row["point"], int(row["row"]), int(row["step"])): row for row in accepted_tokens}
    lp_map = {(row["point"], int(row["row"]), int(row["step"])): row for row in accepted_logprobs}
    assert len(tok_map) == len(lp_map) == 160
    for step in range(32):
        key = ("MP02", 0, step)
        assert int(tok_map[key]["a_token"]) == a_ref[0]["tokens"][step]
        assert int(tok_map[key]["b_token"]) == b_ref[0]["tokens"][step]
        assert float(lp_map[key]["a_logprob"]) == a_ref[0]["sampled_logprobs"][step]
        assert float(lp_map[key]["b_logprob"]) == b_ref[0]["sampled_logprobs"][step]

    mp03_ref = original["MP03_A"]["formal_samples"][0]["rows"]
    source_ids = [f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)]
    warmup_checks, warmup_max_delta = 0, 0.0
    for sample in continuation["warmups"]:
        assert sample["role"] == "WARMUP" and sample["timing_role"] == "INLINE_CORRECTNESS_CANARY_NOT_SCIENCE"
        n, delta = compare_rows(mp03_ref, sample["rows"], source_ids)
        warmup_checks += n
        warmup_max_delta = max(warmup_max_delta, delta)
        for row_index, row in enumerate(sample["rows"]):
            for step in range(32):
                key = ("MP03", row_index, step)
                assert int(tok_map[key]["b_token"]) == row["tokens"][step]
                assert abs(float(lp_map[key]["b_logprob"]) - float(row["sampled_logprobs"][step])) <= 0.05 + 0.01 * abs(float(lp_map[key]["b_logprob"]))
    assert warmup_checks == 256

    before = read_json(args.continuation / "CACHE_BEFORE.json")
    after = read_json(args.continuation / "CACHE_AFTER.json")
    cache_rows = compare_cache_snapshots(before, after)
    write_tsv(args.output / "CACHE_IDENTITY_RECALCULATION.tsv",
              ["root_id", "path", "file_count", "before_sha256", "after_sha256", "per_file_metadata_exact", "unchanged"], cache_rows)
    preexec = git_json(args.repo, CONT_PREEXEC, "docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_MP03B_CONTINUATION_109_V1/CONTINUATION_PREEXEC_CONTRACT.json")
    lifecycle = continuation["cache_lifecycle"]
    assert lifecycle["pre_warmup"]["status"] == "PASS"
    assert lifecycle["pre_warmup"]["actual_path"] == preexec["aot_pre_warmup"]["path"]
    assert lifecycle["pre_warmup"]["actual_content_sha256"] == preexec["aot_pre_warmup"]["content_sha256"]
    assert lifecycle["after_warmup"]["status"] == "AFTER_WARMUP_FINAL_IDENTITY_FAIL"
    assert lifecycle["after_warmup"]["actual_path"] == preexec["aot_pre_warmup"]["path"]
    assert lifecycle["after_warmup"]["actual_path"] != preexec["after_warmup_final"]["path"]
    assert lifecycle["after_warmup"]["expected_path"] == preexec["after_warmup_final"]["path"]
    assert lifecycle["after_warmup"]["accepted_final_content_sha256"] == preexec["after_warmup_final"]["content_sha256"]
    assert continuation["compiled_qwen2model_after_warmup"][0]["aot_compiled_fn"] is True
    assert continuation["compiled_qwen2model_after_warmup"][0]["do_not_compile"] is False
    assert continuation["runtime"]["enforce_eager"] is False
    assert continuation["runtime"]["compilation_mode"] == "VLLM_COMPILE"
    assert continuation["runtime"]["backend"] == "inductor"
    assert continuation["runtime"]["cudagraph_mode"] == "NONE"
    assert continuation["backend"]["attention_impl"] == ["FlashAttentionImpl"]
    assert continuation["backend"]["linear_method"] == ["UnquantizedLinearMethod"]
    assert lifecycle["graph_count_after_warmup"] == 0
    run = read_json(args.continuation / "RUN_IDENTITY.json")
    usage = read_json(args.continuation / "GPU_USAGE_RECEIPT.json")
    assert run["only_new_arm"] == "MP03_B" and len(usage["history"]) == 1
    assert usage["history"][0]["arm"] == "MP03_B"
    assert usage["lock"]["acquired"] is usage["lock"]["released"] is True
    assert usage["lock"]["baseline"]["uuid"] == usage["lock"]["after"]["uuid"] == preexec["gpu"]["uuid"]
    assert abs(usage["total_gpu_active_seconds_conservative_wall"] - 9.442614242900163) < 1e-9
    assert all(run["old_arm_sha256"][f"{name}.json"] == sha(args.original / f"{name}.json") for name in ("MP02_A", "MP02_B", "MP03_A"))
    write_json(args.output / "CORRECTNESS_INDEPENDENT_RECHECK.json", {
        "frozen_atol": 0.05, "frozen_rtol": 0.01,
        "mp02_b1_native_point": "SCIENCE_VALID",
        "mp02_a_b_formal_requests": 10, "mp02_raw_reference_and_pairwise_step_checks": step_checks,
        "mp02_max_sampled_logprob_abs_delta": max_delta,
        "accepted_9122_mp02_steps_crosschecked": 32,
        "mp03_continuation_warmup_requests": 2, "mp03_warmup_four_row_step_checks": warmup_checks,
        "mp03_max_warmup_logprob_abs_delta_vs_original_a": warmup_max_delta,
        "accepted_9122_mp03_b_steps_crosschecked": 256,
        "mp03_b4_native_point": "INCOMPLETE_EXECUTION_IDENTITY_STOP",
        "mp03_b_formal_samples": 0,
        "warmup_correctness_is_formal_timing_authority": False,
    })

    # Producer-derived summaries are read only after independent raw calculations.
    producer = read_json(args.original / "DQ2_METRICS.json")
    combined = read_json(args.continuation / "COMBINED_DQ2_METRICS.json")
    flat = {}
    for name, arm in (("MP02_A", "A"), ("MP02_B", "B")):
        result = metrics[name]
        source = producer["MP02_B1"][arm]
        for field in ("sample_count", "median_ms", "mad_ms", "min_ms", "max_ms", "ms_per_generated_token"):
            flat[f"{name}.{field}"] = (result["n"] if field == "sample_count" else result["median_ms"] / 32 if field == "ms_per_generated_token" else result[field], source[field])
    flat["MP02_B_over_A_ratio"] = (ratio, producer["MP02_B_over_A_ratio"])
    flat["MP02_A_vs_B_time_reduction"] = (reduction, producer["MP02_A_vs_B_time_reduction"])
    for field in ("sample_count", "median_ms", "mad_ms", "min_ms", "max_ms"):
        flat[f"MP03_A_diagnostic.{field}"] = (metrics["MP03_A"]["n"] if field == "sample_count" else metrics["MP03_A"][field], producer["MP03_B4"]["A_raw_diagnostic_only"][field])
    flat["CONTINUATION.new_MP03_B_formal_samples"] = (len(continuation["formal_samples"]), combined["new_MP03_B_formal_samples"])
    flat["CONTINUATION.old_MP02_A_median_ms"] = (t_a, combined["old_MP02_A_median_ms"])
    flat["CONTINUATION.old_MP02_B_median_ms"] = (t_b, combined["old_MP02_B_median_ms"])
    flat["CONTINUATION.old_MP03_A_raw_median_diagnostic_only_ms"] = (metrics["MP03_A"]["median_ms"], combined["old_MP03_A_raw_median_diagnostic_only_ms"])
    comparison = []
    for metric, (independent, published) in sorted(flat.items()):
        match = independent == published or (isinstance(independent, float) and isinstance(published, float) and math.isclose(independent, published, rel_tol=0, abs_tol=1e-12))
        assert match, (metric, independent, published)
        comparison.append({"metric": metric, "independent_value": repr(independent), "producer_value": repr(published), "exact_or_1e_minus_12_match": "PASS"})
    write_tsv(args.output / "DQ2_PRODUCER_CONSUMER_COMPARISON.tsv",
              ["metric", "independent_value", "producer_value", "exact_or_1e_minus_12_match"], comparison)
    authority_index = {"commits": {}, "raw": raw_authority,
                       "raw_index_storage_note": "RAW_INDEX.json is committed in each producer review pack; durable root contains the 26/15 payloads plus RAW_SHA256SUMS, not RAW_INDEX.json",
                       "primary_calculation_authority": "164 durable arm JSON bytes",
                       "producer_derived_summary_role": "POST_RECOMPUTE_CROSSCHECK_ONLY"}
    for name, commit in AUTHORITY.items():
        tree = subprocess.check_output(["git", "-C", str(args.repo), "show", "-s", "--format=%T", commit], text=True).strip()
        authority_index["commits"][name] = {"commit": commit, "tree": tree}
    assert authority_index["commits"]["attribution_level0"]["tree"] == "d68af347fe33addef143c634fab850e9a2580fd0"
    assert authority_index["commits"]["dq2_original_result"]["tree"] == "7830be7533c4169ab1a79478bc7d259f1f6f7752"
    assert authority_index["commits"]["dq2_continuation_result"]["tree"] == "0bfa120909ce54f015bc3aafb664f65976eb9ebc"
    write_json(args.output / "AUTHORITY_INDEX.json", authority_index)
    write_json(args.output / "RAW_RECOMPUTE_RECEIPT.json", {
        "raw_payload_files_verified": 41, "original_payload_files": 26, "continuation_payload_files": 15,
        "all_durable_size_sha_manifest_copyback_receipt_checks": "PASS",
        "cache_roots_unchanged_before_after": 5,
        "mp02_a_median_ms": t_a, "mp02_b_median_ms": t_b,
        "mp02_b_over_a_ratio": ratio, "mp02_a_vs_b_time_reduction": reduction,
        "mp03_a_median_diagnostic_only_ms": metrics["MP03_A"]["median_ms"],
        "mp03_b_original_formal_samples": 0, "mp03_b_continuation_formal_samples": 0,
        "mp03_b_continuation_warmup_correctness": "PASS_TWO_WARMUPS_FOUR_ROWS",
        "mp03_b_continuation_cache_identity": "AFTER_WARMUP_FINAL_IDENTITY_FAIL",
        "mp03_b_continuation_gpu_active_seconds": usage["total_gpu_active_seconds_conservative_wall"],
        "producer_numeric_field_comparisons": len(comparison), "producer_numeric_mismatches": 0,
    })
    print(f"PASS: {len(raw_rows)} durable payloads; MP02 medians {t_a:.9f}/{t_b:.9f} ms; ratio {ratio:.9f}; {len(comparison)} producer crosschecks; five cache roots unchanged")


if __name__ == "__main__":
    main()
