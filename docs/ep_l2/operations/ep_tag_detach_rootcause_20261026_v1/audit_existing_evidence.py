#!/usr/bin/env python3
"""Read-only bounded reaggregation; optional pinned r5 decoder, never a simulator."""
import argparse, csv, hashlib, io, json
from pathlib import Path

R5 = "1093d2629e3d6a9130ba25b9dd119b6f3e16c092"
BIN = "e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33"
BASE = "docs/ep_l2/operations/ep_main_native_takeover_20261023_v1"
VECTOR = "docs/ep_l2/operations/ep_main_vector_r5_20261023_v1"
def digest(p, cap=32*1024*1024):
    if p.stat().st_size > cap: raise ValueError(f"input over cap: {p}")
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()
def read(p):
    digest(p, 16*1024*1024)
    return json.loads(p.read_text())
def require(v, msg):
    if not v: raise ValueError(msg)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--framework", type=Path, required=True)
    ap.add_argument("--vector-result", type=Path, required=True)
    ap.add_argument("--r5-tools", type=Path)
    a = ap.parse_args()
    r = a.vector_result
    point = read(r/"CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json")
    ident = point["source_identity"]
    require(ident["core_source_commit"] == R5 and ident["binary_sha256"] == BIN, "wrong runtime identity")
    require(point["pair"] is False and point["status"] == "EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED", "wrong acceptance domain")
    bindings = {"raw.log":"raw_sha256", "R5_TAGPRESSURE_TERMINAL.json":"r5_summary_sha256",
                "R4_212_TERMINAL.json":"old212_summary_sha256", "terminal_summary.json":"model_summary_sha256"}
    hashes = {}
    for file, key in bindings.items():
        hashes[file] = digest(r/file)
        require(hashes[file] == point[key], f"accepted hash mismatch: {file}")
    new = read(r/"R5_TAGPRESSURE_TERMINAL.json")
    old = read(r/"R4_212_TERMINAL.json")
    h = new["global_record"]["histograms"]
    gc = new["global_record"]["counters"]
    require(new["global_record"]["assoc"] == 16, "wrong assoc")
    for name in ["heads_raw_reserved", "heads_raw_reserved_eligible", "heads_raw_reserved_invalid",
                 "heads_raw_reserved_reasonmask"]:
        require(sum(row[-1] for row in h[name]) == gc["covered"], f"closure mismatch: {name}")
    require(sum(row[-1] for row in h["ways_raw_reserved_class"]) == 16*gc["covered"], "way class closure")
    require(gc["covered"]+gc["probe_skipped"] == gc["observed_heads"], "coverage closure")
    require(sum(gc[k] for k in ["skip_tvd","skip_ideal","skip_disabled","skip_other"]) == gc["probe_skipped"], "skip closure")
    heads = h["heads_raw_reserved"]
    eligible = h["heads_raw_reserved_eligible"]
    # WIRE_CONTRACT raw index2=MISS, index3=RESERVATION_FAIL; 4=SECTOR_MISS is existing Tag.
    selected = {2,3}
    values = {
        "new_tag_head_cycle_exposures":sum(n for raw,res,n in heads if raw in selected),
        "all16_reserved_new_tag_head_cycle_exposures":sum(n for raw,res,n in heads if raw in selected and res==16),
        "raw_FAIL_head_cycle_exposures":sum(n for raw,res,n in heads if raw==3),
        "maximum_reserved_ways_covered":max(res for raw,res,n in heads),
        "maximum_reserved_ways_new_tag_demand":max(res for raw,res,n in heads if raw in selected),
        "structural_eligible_head_cycle_exposures":sum(n for raw,res,e,n in eligible if e>0),
        "new_tag_and_structural_eligible_joint_head_cycle_exposures":sum(n for raw,res,e,n in eligible if raw in selected and e>0)
    }
    prodnames = ["ft_access_attempts","commit_raw_probe_reached","raw_tag_fail_commit","relieve_calls",
                 "relieve_T_disabled","relieve_no_eligible","relieve_eligible_selected","detach_calls",
                 "detach_success","detached_retired","trigger_accepted_after_detach","trigger_denied_after_detach"]
    prod = {k:old["global_counters"][k] for k in prodnames}
    proj = read(a.framework/VECTOR/"SCIENTIFIC_CAUSE_PROJECTION.json")
    require(all(proj[k]==v for k,v in values.items()), "projection aggregate mismatch")
    require(proj["actual_production_commit_domain"] == prod, "projection production mismatch")
    require(proj["r5_head_cycle_coverage"] == gc, "projection coverage mismatch")
    require(digest(r/"CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json") == proj["accepted_point_sha256"], "point binding")
    # Predicate bit2 is reuse_seen; reason-presence bit4 says at least one live target-set RO has reuse.
    reuse = h["ways_raw_reserved_predmask"]
    reason = h["heads_raw_reserved_reasonmask"]
    extra = {
        "reuse_way_exposures":sum(n for raw,res,mask,n in reuse if mask&2),
        "new_tag_and_reuse_way_exposures":sum(n for raw,res,mask,n in reuse if raw in selected and mask&2),
        "raw_FAIL_and_reuse_way_exposures":sum(n for raw,res,mask,n in reuse if raw==3 and mask&2),
        "heads_with_any_reuse":sum(n for raw,res,mask,n in reason if mask&4),
        "new_tag_heads_with_any_reuse":sum(n for raw,res,mask,n in reason if raw in selected and mask&4),
        "raw_FAIL_heads_with_any_reuse":sum(n for raw,res,mask,n in reason if raw==3 and mask&4),
    }
    rows = new["global_record"]["route_joint"]
    require(sum(row[-1] for row in rows)==gc["covered"], "route closure")
    joint = {}
    for sl,ph,raw,res,requester,elig,route,admitted,early,n in rows:
        if raw in selected and elig==2:
            key = f"requester={requester},route={route},admitted={admitted},early={early}"
            joint[key] = joint.get(key,0)+n
    require(sum(joint.values()) == values["new_tag_and_structural_eligible_joint_head_cycle_exposures"], "route eligible join")
    csvtext = io.StringIO()
    writer = csv.writer(csvtext)
    writer.writerow(["raw_status","reserved_ways","covered_head_cycle_exposures"])
    labels = ["HIT","HIT_RESERVED","MISS","RESERVATION_FAIL","SECTOR_MISS","MSHR_HIT","WRITE_ALLOCATED","UNKNOWN"]
    writer.writerows((labels[raw],res,n) for raw,res,n in heads)
    require(csvtext.getvalue().replace("\r\n","\n") == (a.framework/VECTOR/"COVERED_TARGET_SET_HISTOGRAM.csv").read_text(), "CSV mismatch")
    decoder_check = {"status":"NOT_REQUESTED"}
    if a.r5_tools:
        import sys, importlib.util
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(a.r5_tools))
        toolhashes = {n:digest(a.r5_tools/n) for n in ["decoder.py","math_audit.py","WIRE_CONTRACT.json"]}
        require(toolhashes == {
            "decoder.py":"65731a6df85e9821994e4efea84ea5473e482e6f1c2bb385c9b8abdf00aefcff",
            "math_audit.py":"f55b4f911a321aae2f22fd2b017e5bcef270847adf24968d7d1e0791401d5ae0",
            "WIRE_CONTRACT.json":"cb973b3bc462ce33895a0f8cc31b428f6bf14b63f8497e8895eb314ea0894db7"
        }, "frozen r5 tools identity mismatch")
        spec = importlib.util.spec_from_file_location("ep_rootcause_frozen_r5_decoder", a.r5_tools/"decoder.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        g = new["global_record"]
        feed = mod.Feed(expected_slices=list(range(64)), registered_slice_count=64,
                        expected_kernels=g["kernel_catalog"], expected_flags={k:g[k] for k in ["T","M","ro_runtime"]},
                        source_binding=new["source_binding_external"], old212_decoder_sha256=new["fixed_r4_decoder_sha256"])
        with (r/"raw.log").open("rb") as f:
            for line in f: feed.feed(line)
        redecoded = feed.finish(old)
        require(redecoded == new, "raw redecoded result differs from SHA-bound accepted terminal")
        math_check = mod.audit_normalized_result(new, old)
        decoder_check = {"status":"PASS", "raw_redecoded_terminal_exact_match":True, "normalized_math":math_check,
                         "tools_sha256":toolhashes,
                         "old212":"SHA-bound accepted result supplied; fixed old212 decoder NOT re-executed"}
    # Historical points: only reaggregate approved immutable projections, not their absent raw.
    historical = {}
    for name in ["r5CFD.json","r5DWT.json"]:
        d = read(a.framework/BASE/"evidence/github"/name)
        require(d["source_identity"]["core_source_commit"] == R5 and d["source_identity"]["binary_sha256"] == BIN, "historical runtime mismatch")
        c = d["mechanism_root_cause"]
        hist = c["raw_by_target_reserved"]
        require(sum(n for raw,res,n in hist)==c["observed_head_cycles"]["covered_probed_heads"], "historical coverage closure")
        require(sum(n for raw,res,n in hist if raw in selected)==c["new_tag_head_cycle_exposures"], "historical demand closure")
        require(sum(n for raw,res,n in hist if raw in selected and res==16)==c["all16_reserved_new_tag_head_cycle_exposures"], "historical all16 closure")
        historical[name] = {"scope":"PROJECTION_ONLY_NOT_RAW_REDECODED", "sha256":digest(a.framework/BASE/"evidence/github"/name),
                            "new_tag_head_cycle_exposures":c["new_tag_head_cycle_exposures"],
                            "raw_FAIL_head_cycle_exposures":sum(n for raw,res,n in hist if raw==3),
                            "maximum_reserved_ways_covered":max(res for raw,res,n in hist),
                            "production":c["actual_production_commit_domain"]}
    print(json.dumps({"schema":"EP_TAG_ROOTCAUSE_OFFLINE_REAGGREGATION_V1",
        "status":"PASS","source_identity":ident,"vector_raw_and_terminal_hashes":hashes,
        "vector_accepted_projection_and_csv_match":True,"vector_head_cycle_aggregates":values,
        "vector_production":prod,"vector_structural_eligible_way_exposures":sum(e*n for raw,res,e,n in eligible),"vector_same_set_reuse_joints":extra,
        "vector_new_tag_eligible_route_joint":joint,"vector_raw_r5_redecode":decoder_check,"historical":historical,
        "limits":["No simulator, GPU, source mutation or reacceptance. Optional existing r5 offline parser only.",
                  "Vector raw SHA verified; optional r5 decoder repeats existing validation, not a new independent parser or acceptance.",
                  "CFD/DWT are projection-only checks. Skipped dimensions remain NA.",
                  "Head/way-cycle exposures are not independent requests; no marginal multiplication."]},indent=2))
if __name__=="__main__": main()
