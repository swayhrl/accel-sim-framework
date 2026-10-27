#!/usr/bin/env python3
"""Integrate source-audit contributions; only writes atlas files."""
from pathlib import Path
import csv, hashlib, json, re, collections
ROOT = Path(__file__).resolve().parents[1]
WORKTREE = ROOT.parents[1]
FREEZE_PATH = WORKTREE / "docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json"
freeze = json.loads(FREEZE_PATH.read_text())
groups = ["polybench","rodinia","parboil","cuda_samples","conditional"]
summaries = {}
for group in groups:
    records = json.loads((ROOT / "contributions" / group / "summary.json").read_text())
    for row in records:
        assert row["program"] not in summaries, row["program"]
        summaries[row["program"]] = dict(row, reviewer=group)

def cell(v):
    if isinstance(v,(dict,list)): v=json.dumps(v,ensure_ascii=True,separators=(",",":"))
    if v is None: return ""
    if isinstance(v,bool): return str(v).lower()
    return re.sub(r"\s+"," ",str(v)).strip()

def tsv(name,rows):
    assert rows
    with (ROOT/name).open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n")
        writer.writeheader()
        writer.writerows({k:cell(v) for k,v in row.items()} for row in rows)

def section(text,n):
    match=re.search(r"^##\s+"+str(n)+r"\.\s+[^\n]*\n(.*?)(?=^##\s+\d+\.|\Z)",text,re.M|re.S)
    return re.sub(r"\s+"," ",match.group(1)).strip() if match else ""

ordinary=[p for p in freeze["programs_44_to_42"] if p["ordinary_main_slot"]]
assert len(ordinary)==42
assert set(summaries)=={p["program"] for p in ordinary}, (set(summaries), {p["program"] for p in ordinary})
index=[];matrix=[];gaps=[]
for program in freeze["programs_44_to_42"]:
    name=program["program"]; summary=summaries.get(name,{})
    report=summary.get("report","")
    if report:
        text=(ROOT/report).read_text()
        headings=[int(n) for n in re.findall(r"^##\s+(\d+)\.",text,re.M)]
        assert headings==list(range(1,11)),(report,headings)
        assert summary.get("source_verified") is True,(name,"source not verified")
        assert re.search(r":\d+|#L\d+",text),(name,"missing source lines")
        assert "128" in text and "32" in text,(name,"missing line/sector analysis")
    input_status=summary.get("input_bound","UNRESOLVED")
    trace_status=summary.get("trace_scope_bound","HEADER_COMPARED_FULL_APPLICATION_UNRESOLVED") if report else "EXCLUDED_DERIVED"
    if summary.get("binary_bound") in [False,"UNRESOLVED",None]:
        binary_status="UNRESOLVED"
    else:
        binary_status=summary["binary_bound"]
    if summary.get("identity_state")=="UNRESOLVED":
        assert program["state"]=="UNRESOLVED"
    row=dict(program_id=program["program_id"],program=name,suite=program["suite"],ordinary_main_slot=program["ordinary_main_slot"],identity_state=program["state"],report=report,selected_input_digest=program["selected_input_digest"],selected_bundle_id=program["selected_bundle_id"],selected_parameters=program["selected_parameters"],candidate_inputs=program["input_count"],source_authority=summary.get("source_authority","NOT_AUDITED_EXCLUDED_DERIVED"),SOURCE_VERIFIED="INSPECTED_FIXED_SOURCE_CANDIDATE" if report else "NOT_AUDITED_EXCLUDED_DERIVED",INPUT_BOUND=input_status,BINARY_BOUND=binary_status,TRACE_SCOPE_BOUND=trace_status,RUNTIME_MEASURED="NOT_ASSESSED_IN_SOURCE_AUDIT",UNRESOLVED=summary.get("evidence_gaps",program["reason"]),reviewer=summary.get("reviewer","excluded"))
    index.append(row)
    if report:
        matrix.append(dict(program_id=program["program_id"],program=name,identity_state=program["state"],source_kernels=summary.get("kernels",[]),trace_launch_count=summary.get("trace_launch_count",summary.get("launch_count_source_and_header",summary.get("capture_kernel_counts","SEE_REPORT"))),address_pattern=summary.get("address_pattern","SEE_REPORT_SECTION5"),source_features=section(text,8),DTC_L1_EP_L2_hypotheses=section(text,9),SOURCE_VERIFIED="INSPECTED_FIXED_SOURCE_CANDIDATE",INPUT_BOUND=input_status,BINARY_BOUND=binary_status,TRACE_SCOPE_BOUND=trace_status,RUNTIME_MEASURED="NOT_ASSESSED_IN_SOURCE_AUDIT",UNRESOLVED=summary.get("evidence_gaps","capture provenance"),evidence=report))
        gaps.append((name,report,cell(summary.get("evidence_gaps","Capture source/binary/input linkage unresolved"))))
tsv("WORKLOAD_INDEX.tsv",index)
tsv("ARCH_FEATURE_MATRIX.tsv",matrix)
byname={p["program"]:p for p in freeze["programs_44_to_42"]}
bindings=[]
for row in freeze["mapping_72_to_42"]:
    p=byname[row["program"]]
    bindings.append(dict(program_id=row["program_id"],program=row["program"],input_digest=row["input_digest"],bundle_id=row["bundle_id"],trace_entry=row["trace_entry"],source_version=row["source_version"],parameters=row["parameters"],decision=row["decision"],maps_to_selected_input=row["maps_to_selected_input"],program_identity_state=p["state"],scope_evidence=p["scope_evidence"],selected_input=(row["input_digest"]==p["selected_input_digest"]),member_count=len(row["source_members_sha256"]),inherited_members=row["source_members_sha256"],capture_source_binary_input_linkage_newly_certified=False,reason=row["reason"],report=summaries.get(row["program"],{}).get("report","EXCLUDED_DERIVED")))
tsv("INPUT_TRACE_BINDINGS.tsv",bindings)

critical="""# Evidence gaps and independent discrepancy register

These observations describe fixed candidate source or inherited metadata. They do not retroactively modify accepted results, representative choices, scientific registries, manuscript values or model identities. Capture-time source/ELF linkage is unresolved, so a source defect is not proof that the historical captured executable contains that defect.

| Topic | Audited observation | Interpretation boundary |
|---|---|---|
| All ordinary inputs | Frozen record does not newly certify capture ELF and original input bytes; headers were read in bounded prefixes only. | SOURCE_VERIFIED, INPUT_BOUND and TRACE_SCOPE_BOUND remain independent. |
| ATAX,3MM,GESUMMV | Recovered original candidate has incomplete initialization before accumulation; source/repair variants must remain explicit. | Numerical correctness of capture binary is not decided by this source audit. See program reports and build-authority follow-up. |
| CFD | Standard source has14003 launches; all three candidates contain5 and no time_step. | DTC representative remains conditional; EP historical full_application label is preserved with discrepancy. |
| streamcluster | Five captured gain kernels do not match normal complete pFL loop at the named shapes. | Partial capture, modified binary, abnormal termination or source mismatch remain alternatives; no recapture/promotion. |
| pathfinder | Version/CLI and launch-count semantics remain unresolved. | Do not merge2.0-ft and3.1 simply by name. |
| heartwall | Selected one-frame path initializes templates; tracking convolution is in later-frame branch. | Full one-frame program does not exercise the complete algorithmic tracking capability. |
| convolutionSeparable | Fixed candidate host parser maps3072 to384x192 with warmup; selected capture is3072 square and one pair. | Device tile correspondence does not establish host/capture identity. |
| scan | Candidate host size and selected capture size differ despite compatible multistage sequence. | Source-scale and capture-scale must be separate. |
| particlefilter_float | CTA-local barriers do not order all-CTA weights before serial CDF, or publish block0 u0 to other CTAs. | Source risk is active for multi-CTA selected shape; no new native failure claim. |
| myocyte | Selected mode0 CAM writes a shared derivative buffer where communication output is expected; ECC/CAM outputs overlap. | Independent reviewer distinguishes mode0 cross-CTA risk from mode1 serial overwrite; capture binary binding remains open. |
| srad_v1 | Reduction tail omits scaled indexing in later reduction pass. | Selected source shape activates d_mul!=1 tail condition; no accepted numerical result is rewritten. |
| Parboil histo/SGEMM | Candidate initialization and beta0 expression caveats need compiled/numerical evidence. | Source spelling does not prove a SASS load survived optimization. |
| Cross-project reuse | Registered full member metadata matches7 EP inputs to DTC candidates, but only3 are selected representatives. | Three alternates and one conditional match stay distinct; Btree is a different derived trace. |
| Historical runtime | This atlas does not create performance/occupancy/latency evidence. | Existing measurements need their own exact model/config/input identities before explaining mechanisms. |

## Per-program remaining gaps

"""
critical+="\n".join("- ["+name+"]("+report+"): "+gap for name,report,gap in gaps)+"\n"
critical+="\n## Closure evidence needed\n\nRecover existing capture-time source revision or patch set, expanded nvcc recipe, original benchmark ELF hash, input-content or reproducible generator identity and capture ROI/launch arguments. Reconcile these against the frozen per-member trace metadata without editing it. Any later native test, recapture or performance run needs separate authorization; none is requested or started here.\n"
(ROOT/"EVIDENCE_GAPS.md").write_text(critical)

# Independent re-evaluation of the EP hash comparison from recorded members.
ep=json.loads((ROOT/"contributions/ep_mapping/EP_FROZEN_INPUT_MAPPING.json").read_text())
def ephash(members):
    mapped=sorted([dict(name=x["relative_path"],sha256=x["sha256"],bytes=x["size"]) for x in members],key=lambda x:x["name"])
    return hashlib.sha256(json.dumps(mapped,sort_keys=True,separators=(",",":")).encode()).hexdigest()
ep_checks=[]
for item in ep["inputs"]:
    target=item["historical_identity"]["trace_content_sha256"]
    hits=[r["input_digest"] for r in freeze["mapping_72_to_42"] if ephash(r["source_members_sha256"])==target]
    assert sorted(hits)==sorted(item["matching_dtc_inputs"]),(item["ep_workload"],hits,item["matching_dtc_inputs"])
    ep_checks.append(dict(ep_workload=item["ep_workload"],matching_dtc_inputs=hits,status="MATCH" if hits else "DIFFERENT"))
counts=dict(collections.Counter(p["state"] for p in ordinary))
assert counts=={"IDENTITY_FROZEN":35,"UNRESOLVED":7},counts
assert len(index)==44 and len(matrix)==42 and len(bindings)==72
assert len({r["input_digest"] for r in bindings})==72
assert sum(r["selected_input"] for r in bindings)==35
validation=dict(status="PASS",scope="artifact coverage, exact inherited identity projection, fixed candidate source coverage, independent EP member-hash arithmetic; no workloads executed",ordinary_reports=len(matrix),frozen_reports=counts["IDENTITY_FROZEN"],conditional_reports=counts["UNRESOLVED"],excluded_derived_index_rows=len(index)-len(matrix),input_binding_rows=len(bindings),selected_inputs=35,source_hash_verification=json.loads((ROOT/"SOURCE_BLOB_VERIFICATION.json").read_text())["counts"],address_review=json.loads((ROOT/"ADDRESS_REVIEW_VALIDATION.json").read_text())["status"],ep_independent_checks=ep_checks)
(ROOT/"ATLAS_VALIDATION.json").write_text(json.dumps(validation,indent=2)+"\n")
review="""# Review status

Status: SOURCE_ATLAS_COMPLETE_WITH_EXPLICIT_CAPTURE_BINDING_GAPS.

All35 frozen ordinary workloads have independent ten-section reports: PolyBench9, Rodinia10, Parboil7, CUDA Samples9. Seven additional reports preserve conditional identities: backprop,cfd,kmeans,nn,nw,pathfinder,streamcluster. The index also lists derived b+tree/hotspot as excluded; they are not silently counted as ordinary reports.

The coordinator integrates the exact inherited35/7 selection and72 candidate input identities, independently verifies1,443 source blobs, reads ATAX/MVT/BICG/2DCONV/GEMM/particlefilter_naive/ParboilSGEMM sources, and checks address formulas. See CROSS_REVIEW.md and ADDRESS_REVIEW_VALIDATION.json. Suite agents self-check every owned report. PolyBench independently reviews particlefilter_naive; the conditional specialist independently reviews address derivations and three Rodinia source risks. EP and CUDA specialists independently compare shared input identities, and the coordinator recomputes the EP member hashes again from the frozen DTC metadata.

| Agent | Completed scope | Evidence |
|---|---|---|
| A | PolyBench9 and independent naive particle filter review | contributions/polybench/ |
| B | Rodinia10, all selected launch paths | contributions/rodinia/ |
| C | Parboil7, complete unique kernels and source variants | contributions/parboil/ |
| D | CUDA Samples9 and independent EP shared-input review | contributions/cuda_samples/ |
| E | Independent EP eight-input lineage/difference index and current-authority check | contributions/ep_mapping/ |
| F | Seven conditional source/scope audits plus independent address/source-risk review | contributions/conditional/ |
| Coordinator | Authority, exact selection, indexes, feature matrix, cross-review, project views, validation and publication | root atlas documents and tools/ |

Completion here means the source review and knowledge-base deliverables exist, not that missing benchmark capture provenance or numerical correctness has been certified. The matrix never upgrades candidate source verification into capture-source verification. No runtime measurements are newly made or invalidated.

Validation is reproducible with tools/integrate_atlas.py and tools/review_address_sets.py. ATLAS_VALIDATION.json verifies42 ordinary reports,35 selected inputs,seven conditional states,44 index slots and72 input identities, plus independent EP hash comparisons. Publication receipt is produced after the exact staged paths are committed, pushed to the independent branch and read back. Existing scientific files outside docs/workload_atlas are unchanged relative to the atlas base.
"""
(ROOT/"REVIEW_STATUS.md").write_text(review)
print(json.dumps(validation))
