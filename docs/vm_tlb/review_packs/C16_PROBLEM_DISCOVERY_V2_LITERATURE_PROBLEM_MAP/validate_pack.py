#!/usr/bin/env python3
"""Read-only deterministic schema/decision checks for this literature pack."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "LITERATURE_EXPERIMENT_AUDIT.tsv", "AI_ARCH_PROBLEM_TAXONOMY.md",
    "PHENOMENON_TO_MECHANISM_MAP.tsv", "STRONG_SOFTWARE_BOUNDARIES.md",
    "C16_LITERATURE_GAP_MAP.tsv", "TOP_PROBLEM_DISCOVERY_CANDIDATES.md",
    "SOURCE_READING_LEVEL.tsv", "LITERATURE_EXPERIMENT_CONTEXT.tsv",
    "FINAL_DECISION.json",
]
for name in REQUIRED:
    assert (ROOT / name).is_file() and (ROOT / name).stat().st_size > 0, name

def table(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert rows and all(None not in row for row in rows), name
    return rows

sources = table("SOURCE_READING_LEVEL.tsv")
audits = table("LITERATURE_EXPERIMENT_AUDIT.tsv")
contexts = table("LITERATURE_EXPERIMENT_CONTEXT.tsv")
problems = table("PHENOMENON_TO_MECHANISM_MAP.tsv")
gaps = table("C16_LITERATURE_GAP_MAP.tsv")
source_ids = {r["source_id"] for r in sources}
assert len(source_ids) == len(sources)
assert all(r["source_id"] in source_ids for r in audits)
audit_keys = {(r["source_id"], r["group_id"]) for r in audits}
context_keys = {(r["source_id"], r["group_id"]) for r in contexts}
assert len(audit_keys) == len(audits) and audit_keys == context_keys
assert all(r["reading_level"] in {"FULLTEXT_VERIFIED", "SECTION_VERIFIED", "ABSTRACT_ONLY", "CODE_ONLY", "UNAVAILABLE"} for r in sources)
assert all(r["artifact_status"] == "NOT_RUN" for r in sources)
assert all(r["artifact_status"] == "NOT_RUN" for r in audits)
assert all(r["reading_level"] in {"FULLTEXT_VERIFIED", "SECTION_VERIFIED"} for r in audits)
assert all(r["missing_disclosure"] and r["negative_or_boundary_case"] for r in audits)
decision = json.loads((ROOT / "FINAL_DECISION.json").read_text(encoding="utf-8"))
assert decision["decision"] == "NO_NEW_LITERATURE_DRIVEN_PROBLEM_QUALIFIED"
assert decision["qualified_candidate_count"] == 0
assert decision["closed_direction_count_preserved"] == 8
assert decision["literature_audit_experiment_group_count"] == len(audits)
assert decision["literature_source_count"] == len(sources)
assert not any(decision[k] for k in ("author_artifacts_run", "gpu_used", "simulator_used", "new_trace_captured", "new_mechanism_implemented", "new_experiment_authorized"))
assert len(problems) >= 7 and len(gaps) >= 8
print(f"PASS sources={len(sources)} experiment_groups={len(audits)} problems={len(problems)} c16_gaps={len(gaps)} candidates=0")
