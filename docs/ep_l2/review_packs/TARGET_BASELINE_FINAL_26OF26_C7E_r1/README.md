# EP-L2 Target Baseline final 26/26 — C7e

Status: **TARGET_BASELINE_26RUN_PASS**.  This is the authoritative 13 × 2,
850 MHz B0-Legacy/B0-Banked campaign using Core
`ece1a3a77c5628763e0a4605bfd1c639ee6a1495`, Framework
`f08d2ce857972fad73c4e1ab7162ba94c6336507`, and formal config SHA-256
`85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d`.

All 26 direct campaign paths are `COMPLETE_VALID`, with normal simulator exit
and matching source/config provenance.  `analysis/` contains the exact C7e
analyzer outputs.  `C7E_DUPLICATE_WRITE_DIAGNOSTIC/` in the source result root
is deliberately excluded: it contains the earlier concurrent-write 3mm
attempt, while the formal 3mm rows in this pack are the clean replacement pair.

Review order: `campaign_manifest.json`, `RUN_STATUS_26OF26.csv`, then the five
tables in `analysis/`.  `RAW_LOG_INDEX.tsv` provides locations and sizes only;
large raw logs are not included.
