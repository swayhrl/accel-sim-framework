# C15 Lane B — native census checkpoint

Recommended entry: this file. Status: `C15_B_NATIVE_CAPTURE_CAPABILITY_LIMITED_READY_FOR_REVIEW`. The checkpoint contains an actual host capability probe, isolated synthetic contract tests, and frozen C12 trace-list provenance only. It contains **zero** new native GPU runs, zero native timings, zero new SASS, zero simulator replay, zero full-ROI simulation, and zero capture windows.

`KERNEL_CATALOG_TRACE_HEADER_ONLY.tsv` is a provenance directory: its `kernel_markers` are historical list counts, not per-launch headers. Its timestamps, launch identity, kernel semantics, shapes, and object attribution remain `NA`/`UNKNOWN`. Consumers must not treat it as `NATIVE_NEW` or sample targets from it.

Source anchors: planning/handoff `9a755b14b01c5a77a6fc98c2547616e1c490e806`; C12 provenance `a268aba0d01310294074ded5bb8017e2092394c0` (input file SHA256 dbc17e3489d20e64d338e61707955577338447514b566ac42dbe090acca87981). Validation: `python3 -m unittest tests/vm_tlb/c15/lane_b/test_c15_lane_b.py -v`; `python3 util/vm_tlb/c15/lane_b/c15_lane_b.py --self-test --fixture-file docs/vm_tlb/chatgpt_handoff/c15_lowcost/fixtures/contract_examples.json`; and the read-only `--validate --output-root docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_b`.

Open issues: an authorized visible GPU, compatible installed native backend, >=64 GiB disk reserve, >=32 GiB MemAvailable, verified local model revisions, a real profiler canary, and a read-only observer for lifetime V2. `RAW_LOG_INDEX.tsv` records the intentional absence of C15 raw logs.
