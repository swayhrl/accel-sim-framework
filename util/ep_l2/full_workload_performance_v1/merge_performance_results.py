"""Read-only, standard-library performance merge. No actor, admission or acceptance authority.

Input: EP_FULL_PERF_OFFLINE_MERGE_MANIFEST_V1 with registry_path/epoch_path,
case_specs [{path,sha256}], and required_common_inputs [input_identity_sha256].
CLI writes only a NEW user-selected output directory. Registry/epoch and all
referenced scientific files are read-only. No large Trace or raw body is read.
"""
import argparse, csv, hashlib, json, math
from pathlib import Path

GOAL = "EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1"
SOURCE_FIELDS = ("core_source_commit", "framework_source_commit", "vendor_pybind11_commit", "binary_sha256", "archive_sha256")
MODE_KEYS = {"-gpgpu_ep_l2_ft_mode", "-gpgpu_ep_l2_ro_tag_detach", "-gpgpu_ep_l2_ro_line_mshr_bypass", "-gpgpu_ep_l2_tvd_clean", "-gpgpu_ep_l2_tvd_dirty"}
CERT_KEYS = {"-gpgpu_ep_l2_ro_ranges", "-gpgpu_ep_l2_ro_ranges_sha256", "-gpgpu_ep_l2_ro_manifest", "-gpgpu_ep_l2_ro_manifest_sha256", "-gpgpu_ep_l2_ro_scope"}
ACCEPTED_STATES = {"ACCEPTED_PENDING_ARCHIVE", "CLOSED_ACCEPTED"}
ENV_OFF = {"EPL2_DETACH_DIAG": "0", "EPL2_TAGPRESSURE_DIAG": "0", "EPL2_TAG_LIFETIME": "0", "EP_L2_EVENT_TIMELINE": "0"}

def need(ok, msg):
    if not ok: raise ValueError(msg)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def digest_bytes(data): return hashlib.sha256(data).hexdigest()

def load_bytes(data):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda x: need(False, "nonfinite JSON"))

def read(path): return load_bytes(Path(path).read_bytes())

def exact(ref):
    data = Path(ref["path"]).read_bytes()
    need(digest_bytes(data) == ref["sha256"], "reference SHA drift: " + ref["path"])
    return load_bytes(data)

def stable_authority(registry_path, epoch_path):
    # E/R/E and one extra R check: foreign writers cause a bounded read-only HOLD.
    for unused in range(3):
        e1 = Path(epoch_path).read_bytes(); r1 = Path(registry_path).read_bytes()
        e2 = Path(epoch_path).read_bytes(); r2 = Path(registry_path).read_bytes()
        e = load_bytes(e1)
        if e1 == e2 and r1 == r2 and e["native_registry_sha256"] == digest_bytes(r1):
            need(e["epoch"] == 2, "unexpected science epoch")
            return load_bytes(r1), {"registry_sha256": digest_bytes(r1), "epoch_sha256": digest_bytes(e1), "epoch": 2}
    raise ValueError("AUTHORITY_READ_ONLY_HOLD_UNSTABLE")

def positive_int(value, label):
    need(type(value) is int and value > 0, "invalid " + label)
    return value

def source5(value):
    need(all(k in value and isinstance(value[k], str) and value[k] for k in SOURCE_FIELDS), "incomplete source5")
    return {k: value[k] for k in SOURCE_FIELDS}

def formal_mode(options, mode):
    need(mode in ("S", "F", "WV_ZERO_RO"), "unsupported mode")
    expected = {"-gpgpu_ep_l2_ft_mode": "1" if mode == "S" else "2",
                "-gpgpu_ep_l2_ro_tag_detach": "1" if mode == "F" else "0",
                "-gpgpu_ep_l2_ro_line_mshr_bypass": "1" if mode == "F" else "0",
                "-gpgpu_ep_l2_tvd_clean": "0" if mode == "S" else "1",
                "-gpgpu_ep_l2_tvd_dirty": "0" if mode == "S" else "1"}
    need(all(options.get(k) == v for k, v in expected.items()), "formal mode/actual option contract mismatch")

def collect_case(spec_ref, request):
    s = exact(spec_ref); case = s["cohort"]
    out = {"cohort": case, "input_identity_sha256": s["input_identity_sha256"], "profile": s["profile"],
           "mode": s["mode"], "state": "PENDING", "accepted": False, "spec_ref": spec_ref,
           "source_identity": source5(s["source_identity"]), "unknown_capture_completeness": True,
           "numeric_output_correctness": "UNKNOWN"}
    try:
        need(s["goal"] == GOAL and s["application_budget"] == 1 and s["source_keep"] is True, "spec scope")
        need(request["admitted_specs"].get(case) == spec_ref["sha256"], "not exact admitted spec")
        row = request.get("consumed", {}).get(case)
        if row is None: out["state"] = "NOT_STARTED"; return out
        out["state"] = row["state"]
        out["scientific_status"] = row.get("scientific_status", "UNSPECIFIED")
        # A point on disk never overrides an unaccepted/failure/invalidated row.
        need(row["state"] in ACCEPTED_STATES, "not currently Main-accepted")
        need(not any(x in row.get("scientific_status", "") for x in ("INVALIDATED", "NOT_ACCEPTED", "UNACCEPTED")), "negative final disposition")
        if row.get("final_disposition_ref"):
            disposition = exact(row["final_disposition_ref"])
            need(disposition.get("accepted") is True or disposition.get("scientific_status") in ACCEPTED_STATES, "final disposition not explicitly accepted")
        point = exact(row["accepted_point_ref"])
        need(point["status"] == "EP_FULL_PERF_APPLICATION_ACCEPTED" and point["goal"] == GOAL, "point status/scope")
        need(point["cohort"] == case and point["uuid"] == row["uuid"], "point/consumed identity")
        need(point["spec_ref"] == spec_ref, "point/spec ref mismatch")
        need(point["done_ref"] == row["done_ref"], "point/row DONE mismatch")
        done = exact(point["done_ref"]); validated = exact(point["validation_ref"])
        need(done["cohort"] == case and done["uuid"] == point["uuid"] and done["spec_ref"] == spec_ref, "DONE identity")
        need(done["launcher_wait_returncode"] == 0 and done["stop_reason"] is None and done["native_simulator_observed"] is True, "not natural observed completion")
        need(source5(done["source_identity"]) == source5(s["source_identity"]) == source5(point["source_identity"]), "source5 mismatch")
        need(point["input_identity_sha256"] == s["input_identity_sha256"] and point["mode"] == s["mode"] and point["profile"] == s["profile"], "point/spec population mismatch")
        need(point["hardware_drained"] is True, "not hardware drained")
        for key in ("cycles", "instructions", "CTA", "kernel_count"): positive_int(point[key], key)
        options = s["expected_effective_options"]
        need(len(options) == 282 and options["-trace"] == s["trace_entry"], "complete282/input contract")
        formal_mode(options, s["mode"])
        env = s["observer_env"]
        need(all(isinstance(v, str) for v in env.values()), "observer environment must be exact strings")
        need(all(env.get(k) == v for k, v in ENV_OFF.items()), "this low-cost merge excludes observer-on profiles")
        # Main's terminal validation is referenced, not re-granted here. Additional raw
        # semantics can be exposed by Main without requiring this tool to read a large raw.
        need(isinstance(validated, dict) and validated, "empty validation receipt")
        eligibility = exact(s["eligibility_ref"])
        need(eligibility["input_identity_sha256"] == s["input_identity_sha256"], "eligibility input")
        if s["mode"] == "F":
            cert = exact(s["ro_qualification_ref"])
            need(cert["status"] == "EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED", "F certificate status")
            need(cert["input_identity_sha256"] == s["input_identity_sha256"] and source5(cert["source_identity"]) == source5(s["source_identity"]), "F certificate identity")
            for name, option in (("manifest_ref", "manifest"), ("ranges_ref", "ranges")):
                r = cert[name]; data = Path(r["path"]).read_bytes()
                need(digest_bytes(data) == r["sha256"], "F certificate byte drift")
                need(options["-gpgpu_ep_l2_ro_"+option] == r["path"] and options["-gpgpu_ep_l2_ro_"+option+"_sha256"] == r["sha256"], "F actual certificate mapping")
        else: need(s["ro_qualification_ref"] is None, "non-F inherited RO permission")
        background = {k: v for k, v in options.items() if k not in MODE_KEYS | CERT_KEYS | {"-trace"}}
        population_key = {"input": s["input_identity_sha256"], "source5": source5(s["source_identity"]),
                          "profile": s["profile"], "background282": background, "observer_env": env}
        out.update(accepted=True, state=row["state"], cycles=point["cycles"], instructions=point["instructions"],
                   CTA=point["CTA"], kernel_count=point["kernel_count"], hardware_drained=True,
                   IPC=point["instructions"] / point["cycles"], point_ref=row["accepted_point_ref"],
                   done_ref=point["done_ref"], validation_ref=point["validation_ref"],
                   pair_key=digest_bytes(canonical(population_key)), hardware_background_digest=digest_bytes(canonical(background)), pair_population=population_key)
    except (KeyError, ValueError, OSError, TypeError) as exc:
        out["merge_exclusion"] = str(exc)
    return out

def summarize_pairs(records, required_inputs):
    groups = {}
    for r in records:
        if r["accepted"]: groups.setdefault(r["pair_key"], []).append(r)
    pairs = []; blocked = []
    for key, rows in sorted(groups.items()):
        modes = {}
        for r in rows: modes.setdefault(r["mode"], []).append(r)
        if any(len(v) > 1 for v in modes.values()):
            blocked.append({"pair_key": key, "reason": "MULTIPLE_ACCEPTED_REPLICATES_REQUIRE_EXPLICIT_SELECTION; no best-run selection", "cohorts": [r["cohort"] for r in rows]}); continue
        if "S" not in modes: continue
        for treatment in ("F", "WV_ZERO_RO"):
            if treatment not in modes: continue
            a, b = modes["S"][0], modes[treatment][0]
            need((a["instructions"], a["CTA"], a["kernel_count"]) == (b["instructions"], b["CTA"], b["kernel_count"]), "S/F complete dynamic population mismatch")
            ratio = a["cycles"] / b["cycles"]
            pairs.append({"input_identity_sha256": a["input_identity_sha256"], "profile": a["profile"], "treatment": treatment,
                          "S_cohort": a["cohort"], "F_cohort": b["cohort"], "S_cycles": a["cycles"], "F_cycles": b["cycles"],
                          "speedup_S_over_treatment": ratio, "treatment_cycle_reduction_fraction": 1-b["cycles"]/a["cycles"],
                          "source_identity": a["source_identity"], "observer_env": a["pair_population"]["observer_env"],
                          "pair_key": key, "hardware_background_digest": a["hardware_background_digest"], "slowdown": ratio < 1})
    summaries = []
    strata = {}
    for p in pairs:
        # Never combine different Source/observer populations into one global GM.
        strat = (p["profile"], p["treatment"], digest_bytes(canonical(p["source_identity"])), digest_bytes(canonical(p["observer_env"])), p["hardware_background_digest"])
        strata.setdefault(strat, []).append(p)
    for key, rows in sorted(strata.items()):
        ids = [r["input_identity_sha256"] for r in rows]
        need(len(ids) == len(set(ids)), "duplicate input in profile stratum")
        required = set(required_inputs); covered = set(ids)
        complete = bool(required) and covered == required
        summaries.append({"profile": key[0], "treatment": key[1], "source5_digest": key[2], "observer_env_digest": key[3], "hardware_background_digest": key[4],
                          "observed_pair_count": len(rows), "required_common_count": len(required),
                          "missing_inputs": sorted(required-covered), "unexpected_inputs": sorted(covered-required),
                          "common_set_complete": complete, "observed_set_GM_not_global_claim": math.exp(sum(math.log(r["speedup_S_over_treatment"]) for r in rows)/len(rows)),
                          "full_common_set_GM": math.exp(sum(math.log(r["speedup_S_over_treatment"]) for r in rows)/len(rows)) if complete else None,
                          "slowdown_count": sum(r["slowdown"] for r in rows), "worst_speedup": min(r["speedup_S_over_treatment"] for r in rows),
                          "per_input_best_is_not_global_candidate": True})
    return pairs, summaries, blocked

def merge(manifest):
    need(manifest["schema"] == "EP_FULL_PERF_OFFLINE_MERGE_MANIFEST_V1" and manifest["goal"] == GOAL, "merge manifest identity")
    registry, snap = stable_authority(manifest["registry_path"], manifest["epoch_path"])
    request = registry["registered_future_requests"].get(GOAL)
    need(request is not None, "Goal not registered; no scientific merge population")
    specs = manifest["case_specs"]
    need(len({r["path"] for r in specs}) == len(specs), "duplicate spec ref")
    required = manifest["required_common_inputs"]
    need(len(required) == len(set(required)) and all(isinstance(x, str) and x for x in required), "invalid required common input set")
    records = [collect_case(r, request) for r in specs]
    pairs, summaries, blocked = summarize_pairs(records, required)
    return {"schema": "EP_FULL_PERF_OFFLINE_MERGE_RESULT_V1", "goal": GOAL,
            "status": "OFFLINE_SUMMARY_ONLY_NOT_ACCEPTANCE_AUTHORITY", "authority_snapshot": snap,
            "records": records, "pairs": pairs, "profile_summaries": summaries, "blocked_pair_groups": blocked,
            "model_launches": 0, "registry_writes": 0, "source_mutations": 0,
            "capture_completeness": "UNKNOWN unless independently provided; complete trace commandlist != capture completeness",
            "numeric_output_correctness": "UNKNOWN", "hardware_area_mm2": "UNKNOWN"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True); parser.add_argument("--output", required=True)
    a = parser.parse_args(); result = merge(read(a.manifest))
    dest = Path(a.output); need(not dest.exists() and not dest.is_symlink(), "output must be fresh")
    need(not any(p.is_symlink() for p in [dest.parent, *dest.parents]), "symlink output parent")
    dest.mkdir(parents=True, exist_ok=False)
    (dest/"SUMMARY.json").write_bytes(canonical(result)+b"\n")
    columns = ["input_identity_sha256", "profile", "treatment", "S_cohort", "F_cohort", "S_cycles", "F_cycles", "speedup_S_over_treatment", "treatment_cycle_reduction_fraction", "slowdown"]
    with (dest/"PAIRED_RESULTS.csv").open("x", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore"); w.writeheader(); w.writerows(result["pairs"])
    print(json.dumps({"status": result["status"], "output": str(dest), "science_granted": False}))

if __name__ == "__main__": main()
