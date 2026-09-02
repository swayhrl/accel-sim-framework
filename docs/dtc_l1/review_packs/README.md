# DTC-L1 Review Packs

Codex creates one review directory per executable stage:

```text
docs/dtc_l1/review_packs/<stage_name>/
├── README.md
├── MANIFEST.json
├── SOURCE_ANCHORS.md
├── COMMIT_HISTORY.md
├── CHANGED_FILES.md
├── VALIDATION_SUMMARY.md
├── OPEN_ISSUES.md
├── RAW_LOG_INDEX.tsv
└── validation/...
```

Minimum expectations:

- `README.md` is the single review entry point;
- both Core and Framework base/final SHAs are recorded;
- changed files and semantic purpose are explicit;
- build/directed/integrated test outcomes are summarized;
- formal versus diagnostic evidence is labeled;
- raw logs/traces/build trees are not committed;
- large external logs are indexed by path/size/hash/status when available;
- `git diff --check` and working-tree status are included at closeout.

A stage review pack must contain enough evidence for an independent PASS/FAIL decision without relying on the Codex conversation.
