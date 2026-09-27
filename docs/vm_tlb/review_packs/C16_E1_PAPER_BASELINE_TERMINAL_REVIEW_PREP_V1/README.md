# C16 E1 paper baseline and terminal-review prep V1

Status: `C16_PAPER_BASELINE_TERMINAL_REVIEW_PREP_V1_READY` after the validation and SHA checks below. This is an independent prep branch from frozen Lane 3 `a402828860ced26124ddbf3c9d87baa6f6774d55`. It does not update Lane 3 V1, change Lane 4, declare Paper/Evidence V2 accepted, run GPU work, or interpret partial Lane 4 numbers.

Review order:

1. `SOURCE_ANCHORS.json` and `C16_LANE4_TERMINAL_REVIEW_CONTRACT_V1.md` for immutable authority and the ten-step gate order.
2. `C16_LANE4_TERMINAL_GATE_SCHEMA_V1.json` and `util/vm_tlb/c16/e1_lane4_terminal_review.py` for the CPU-only committed-packet interface.
3. `C16_STRONG_BASELINE_MATRIX_V1.md`, `LITERATURE_TO_BASELINE_MAP.tsv`, `C16_PAPER_STORY_PREFREEZE_V1.md`, `CLAIM_STATUS_PREFREEZE.tsv`.
4. `OPEN_ISSUES.md`, `VALIDATION_SUMMARY.json`, `RAW_LOG_INDEX.tsv`, `CHANGE_SUMMARY.md`, `COMMIT_HISTORY.md`, `SHA256SUMS`.

The evaluator may inspect only a committed `TERMINAL_REVIEW_PACKET.json` inside a C16 E1 review pack. It checks primary source identity, terminal receipts, exact 1565-kernel scope, R0/M1 workload and correctness before considering the diagnostic. It emits normalized review metrics on stdout only. A/B/C/D stay `REQUIRES_PROJECT_REVIEW` because the frozen canary code declares sign-only interpretation without a preregistered materiality threshold. Synthetic tests cover the four decision routes without creating scientific thresholds. No Lane 4 terminal packet is shipped here or formally evaluated.

Validation:

```bash
python3 -m unittest discover -s util/vm_tlb/c16 -p test_e1_lane4_terminal_review.py -v
git diff --check
sha256sum -c docs/vm_tlb/review_packs/C16_E1_PAPER_BASELINE_TERMINAL_REVIEW_PREP_V1/SHA256SUMS
```

The frozen Lane 3 claim/result table and the literature branch remain read-only authorities. Source-file SHA256s and commits are in `SOURCE_ANCHORS.json`. Literature notes supply design context, not experiment authorization. Formal Paper/Evidence V2 waits for a terminal Lane 4 review and a separate project decision.
