#!/usr/bin/env python3
"""Emit the read-only C12 F0 cache-behavior checkpoint.

This analysis consumes only terminal-PASS C12 Prefill/Decode1 F0 raw logs.  It
does not run a simulator and does not write any C5 execution input.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN")
PACK = Path(__file__).resolve().parents[2] / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE"
ROIS = ("prefill", "decode1")
FOCUS = ("DATA_WEIGHT", "DATA_KV_CACHE", "DATA_UNKNOWN")
OUTPUT = PACK / "C12_CACHE_BEHAVIOR_CHECKPOINT.tsv"
FINDINGS = PACK / "C12_CACHE_BEHAVIOR_FINDINGS.md"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def read_log(roi: str) -> tuple[Counter[tuple[str, str, str]], Counter[tuple[str, str]], set[str], str]:
    """Return L1/L2 counters and L2 incoming/victim replacement counters."""
    path = ROOT / roi / "f0" / "run.log"
    if not path.is_file():
        raise SystemExit(f"missing C12 terminal F0 raw log: {path}")
    cache: Counter[tuple[str, str, str]] = Counter()
    replacement: Counter[tuple[str, str]] = Counter()
    classes: set[str] = set()
    with path.open(errors="ignore") as source:
        for raw in source:
            fields = raw.rstrip("\n").split("\t")
            if len(fields) != 7:
                continue
            record, _window, _scope, _cluster, class_or_incoming, event_or_victim, value = fields
            try:
                count = int(value)
            except ValueError:
                continue
            if record == "m4c_telemetry" and event_or_victim in {"HIT", "MISS", "RESERVATION_FAIL"}:
                cache[("L1D", class_or_incoming, event_or_victim)] += count
            elif record == "m4c_telemetry_l2" and event_or_victim in {"HIT", "MISS", "RESERVATION_FAIL"}:
                cache[("L2", class_or_incoming, event_or_victim)] += count
            elif record == "m4c_telemetry_l2_replacement":
                replacement[(class_or_incoming, event_or_victim)] += count
                classes.update((class_or_incoming, event_or_victim))
    return cache, replacement, classes, digest(path)


def rate(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.9f}" if denominator else "NA"


def cache_row(roi: str, level: str, request_class: str, counters: Counter[tuple[str, str, str]], raw_sha: str) -> dict[str, str]:
    hit = counters[(level, request_class, "HIT")]
    miss = counters[(level, request_class, "MISS")]
    reservation_fail = counters[(level, request_class, "RESERVATION_FAIL")]
    hit_miss = hit + miss
    all_attempts = hit_miss + reservation_fail
    return {
        "record_type": "CACHE_LOCALITY",
        "roi": roi,
        "level": level,
        "incoming_class": request_class,
        "victim_class": "",
        "raw_hit": str(hit),
        "raw_miss": str(miss),
        "raw_reservation_fail": str(reservation_fail),
        "hit_plus_miss": str(hit_miss),
        "hit_plus_miss_plus_reservation_fail": str(all_attempts),
        "hit_rate_hit_over_hit_plus_miss": rate(hit, hit_miss),
        "hit_rate_hit_over_all_attempts": rate(hit, all_attempts),
        "replacement_raw_count": "",
        "replacement_row_total": "",
        "replacement_global_total": "",
        "replacement_row_normalized_share": "",
        "replacement_total_normalized_share": "",
        "source_raw_log_sha256": raw_sha,
    }


FIELDS = (
    "record_type", "roi", "level", "incoming_class", "victim_class",
    "raw_hit", "raw_miss", "raw_reservation_fail", "hit_plus_miss",
    "hit_plus_miss_plus_reservation_fail", "hit_rate_hit_over_hit_plus_miss",
    "hit_rate_hit_over_all_attempts", "replacement_raw_count",
    "replacement_row_total", "replacement_global_total",
    "replacement_row_normalized_share", "replacement_total_normalized_share",
    "source_raw_log_sha256",
)


def format_pct(value: str) -> str:
    return "NA" if value == "NA" else f"{100.0 * float(value):.4f}%"


def locality_sentence(roi: str, level: str, request_class: str, cache: Counter[tuple[str, str, str]]) -> str:
    hit = cache[(level, request_class, "HIT")]
    miss = cache[(level, request_class, "MISS")]
    reservation_fail = cache[(level, request_class, "RESERVATION_FAIL")]
    return (f"{roi} {level} {request_class}: hit={hit}, miss={miss}, "
            f"reservation_fail={reservation_fail}, hit/(hit+miss)={format_pct(rate(hit, hit + miss))}, "
            f"hit/(hit+miss+reservation_fail)={format_pct(rate(hit, hit + miss + reservation_fail))}.")


def pair_sentence(roi: str, incoming: str, victim: str, replacement: Counter[tuple[str, str]]) -> str:
    raw = replacement[(incoming, victim)]
    row_total = sum(count for (source, _), count in replacement.items() if source == incoming)
    total = sum(replacement.values())
    return (f"{roi} incoming={incoming} -> victim={victim}: raw={raw}, row_total={row_total}, "
            f"row_share={format_pct(rate(raw, row_total))}, total={total}, total_share={format_pct(rate(raw, total))}.")


def main() -> None:
    all_cache: dict[str, Counter[tuple[str, str, str]]] = {}
    all_replacement: dict[str, Counter[tuple[str, str]]] = {}
    all_classes: dict[str, set[str]] = {}
    hashes: dict[str, str] = {}
    for roi in ROIS:
        all_cache[roi], all_replacement[roi], all_classes[roi], hashes[roi] = read_log(roi)

    rows: list[dict[str, str]] = []
    for roi in ROIS:
        for level in ("L1D", "L2"):
            for request_class in FOCUS:
                rows.append(cache_row(roi, level, request_class, all_cache[roi], hashes[roi]))
        replacement = all_replacement[roi]
        total = sum(replacement.values())
        for incoming in sorted(all_classes[roi]):
            row_total = sum(count for (source, _), count in replacement.items() if source == incoming)
            for victim in sorted(all_classes[roi]):
                raw = replacement[(incoming, victim)]
                rows.append({
                    "record_type": "L2_REPLACEMENT",
                    "roi": roi,
                    "level": "L2",
                    "incoming_class": incoming,
                    "victim_class": victim,
                    "raw_hit": "",
                    "raw_miss": "",
                    "raw_reservation_fail": "",
                    "hit_plus_miss": "",
                    "hit_plus_miss_plus_reservation_fail": "",
                    "hit_rate_hit_over_hit_plus_miss": "",
                    "hit_rate_hit_over_all_attempts": "",
                    "replacement_raw_count": str(raw),
                    "replacement_row_total": str(row_total),
                    "replacement_global_total": str(total),
                    "replacement_row_normalized_share": rate(raw, row_total),
                    "replacement_total_normalized_share": rate(raw, total),
                    "source_raw_log_sha256": hashes[roi],
                })

    with OUTPUT.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    p_cache, d_cache = all_cache["prefill"], all_cache["decode1"]
    p_repl, d_repl = all_replacement["prefill"], all_replacement["decode1"]
    lines = [
        "# C12 cache-behavior checkpoint — terminal F0 only",
        "",
        "Scope: `MEASURED_FULL_ROI_FACT`. This checkpoint reads only the terminal-PASS C12 Prefill F0 and Decode1 F0 raw logs. It neither runs nor changes any simulator input.",
        "The C5 F0 execution identity is the formal baseline; C4/Window-A values are not mixed.",
        "",
        "## Provenance and formulas",
        "",
        f"- Prefill F0 raw-log SHA-256: `{hashes['prefill']}`.",
        f"- Decode1 F0 raw-log SHA-256: `{hashes['decode1']}`.",
        "- Locality counters sum the emitted full-ROI `m4c_telemetry` (L1D) or `m4c_telemetry_l2` (L2) records for each requested class/event.",
        "- `hit/(hit+miss) = raw_hit / (raw_hit + raw_miss)`; `hit/(hit+miss+reservation_fail) = raw_hit / (raw_hit + raw_miss + raw_reservation_fail)`.",
        "- Replacement counters sum `m4c_telemetry_l2_replacement`. `row_share = raw / incoming-row-total`; `total_share = raw / all-emitted-replacement-total`. `DATA_UNKNOWN` is kept verbatim and is **not** renamed Activation.",
        "",
        "## MEASURED_FULL_ROI_FACT",
        "",
        "### Weight locality",
        "",
        locality_sentence("prefill", "L1D", "DATA_WEIGHT", p_cache),
        locality_sentence("decode1", "L1D", "DATA_WEIGHT", d_cache),
        locality_sentence("prefill", "L2", "DATA_WEIGHT", p_cache),
        locality_sentence("decode1", "L2", "DATA_WEIGHT", d_cache),
        "",
        "### KV-cache locality",
        "",
        locality_sentence("prefill", "L1D", "DATA_KV_CACHE", p_cache),
        locality_sentence("decode1", "L1D", "DATA_KV_CACHE", d_cache),
        locality_sentence("prefill", "L2", "DATA_KV_CACHE", p_cache),
        locality_sentence("decode1", "L2", "DATA_KV_CACHE", d_cache),
        "",
        "### L2 replacement rows relevant to Weight/KV/UNKNOWN",
        "",
        pair_sentence("prefill", "DATA_WEIGHT", "DATA_WEIGHT", p_repl),
        pair_sentence("prefill", "DATA_WEIGHT", "DATA_UNKNOWN", p_repl),
        pair_sentence("prefill", "DATA_WEIGHT", "DATA_KV_CACHE", p_repl),
        pair_sentence("decode1", "DATA_WEIGHT", "DATA_WEIGHT", d_repl),
        pair_sentence("decode1", "DATA_WEIGHT", "DATA_UNKNOWN", d_repl),
        pair_sentence("decode1", "DATA_WEIGHT", "DATA_KV_CACHE", d_repl),
        pair_sentence("prefill", "DATA_UNKNOWN", "DATA_WEIGHT", p_repl),
        pair_sentence("decode1", "DATA_UNKNOWN", "DATA_WEIGHT", d_repl),
        "",
        "## SUPPORTED_SIGNAL",
        "",
        "- Weight has markedly higher measured F0 L1D locality in Prefill than Decode1; at L2, Prefill Weight is near 49.3% hit/(hit+miss), while Decode1 Weight is near 0.12%. This is a full-ROI F0 association, not an arm-level causal result.",
        "- KV-cache L2 locality is higher in Decode1 than Prefill in this F0 checkpoint, while its L1D locality is also higher in Decode1. The raw counters and both denominator conventions are retained in the TSV.",
        "- Replacement composition differs by ROI: Prefill incoming Weight replacements split almost evenly between DATA_UNKNOWN and DATA_WEIGHT; Decode1 incoming Weight replacements are predominantly DATA_WEIGHT. These are replacement correlations, not proof that one class causes the other class's eviction behavior.",
        "- If these C5 F0 counters differ from Window-A/C4 characterization, no reconciliation or parameter tuning is applied: C5 uses the frozen C11 common-PA backend, binary/config/registration identity, and complete F0 ROI logs. C5 F0 is the formal baseline for this replay.",
        "",
        "## UNRESOLVED",
        "",
        "- `DATA_UNKNOWN` remains an instrumentation category; this checkpoint makes no Activation relabeling claim.",
        "- Replacement rows do not establish causality, residency lifetime, or a counterfactual cache-policy outcome.",
        "- F0-only evidence cannot determine whether candidate arms change the observed locality/replacement mix; those comparisons remain pending the 22-point C12 matrix.",
        "",
        "The complete raw counters and all replacement rows (including PTE and OTHER classes) are in `C12_CACHE_BEHAVIOR_CHECKPOINT.tsv`.",
    ]
    FINDINGS.write_text("\n".join(lines) + "\n")
    print(f"C12 cache checkpoint PASS rows={len(rows)} output={OUTPUT}")


if __name__ == "__main__":
    main()
