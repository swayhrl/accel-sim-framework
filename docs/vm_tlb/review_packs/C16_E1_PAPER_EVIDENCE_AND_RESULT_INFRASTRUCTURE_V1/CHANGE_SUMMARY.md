# Change and verification summary

This isolated framework branch adds only `util/vm_tlb/c16/paper_result_ingest/` and this paper review pack. No Core source, simulator replacement policy, trace, GPU workload or experiment artifact is changed.

- `ingest.py` reads committed accepted native summaries and a future independently accepted simulator publication; absent results become `PENDING`.
- `CLAIMS.json` and `ledger.py` produce the claim ledger with exact wording, strength, caveat, source SHA256 and artifact commit.
- `plot.py` produces four data-driven native SVGs now and a simulator budget SVG only after accepted result publication.
- `test_ingest.py` exercises source mutation refusal, invalid schema/values, pending behavior and no false plot point.
- The paper draft, figure plan, claim boundaries, B16 decision template and related-work index define the current writing boundary.
- `SOURCE_CLOSURE.json` and `SHA256SUMS` bind the generated delivery to the committed inputs and files.

Validation commands and outcomes are recorded in `VALIDATION_SUMMARY.json`; upstream raw pointers are in `RAW_LOG_INDEX.tsv`. Open work is in `OPEN_ISSUES.json`.
