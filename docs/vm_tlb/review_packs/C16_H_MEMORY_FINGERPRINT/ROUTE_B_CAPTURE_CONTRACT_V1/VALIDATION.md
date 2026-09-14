# Validation

| Check | Result |
|---|---|
| Route A input figures | PASS: reproduced from `LLAMA_S0_FORMAL_V1/MEMORY_FINGERPRINTS.tsv` |
| Recovery-V2 authority | PASS: commit `2e955e007bcabcd3ec24a5f9d24768d27caaee27`, manifest SHA256 `0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc` |
| Exact S0 native census availability | PASS AS BLOCKER: one identity-matched targeted nsys row, no phase-duration kernel catalog; no S1/S2 substitution |
| Existing static maps | PASS: LargeIndex and SmallIndex each have 3 direct `GLOBAL && has_mref=1` rows (two loads, one store) |
| Targeted tool capability | PASS AS GAP: exact function and single-index map/filter are evidenced; all-MREF per-lane producer is absent |
| Memory-only decision | PASS: unchanged `NO_GO`; no evidence to reopen |
| Budget arithmetic | PASS: raw calibration rounded conservatively to 664B/address-bearing event and bounded below 4GiB for anchors; time remains unmeasured |
| GPU actions / replay | NOT_RUN BY DESIGN |

| `python3 -m unittest discover -s tests/vm_tlb/c16/lane_h -p 'test_*.py' -v` | PASS: 13 directed tests |
| `python3 -m py_compile util/vm_tlb/c16/lane_h/*.py tests/vm_tlb/c16/lane_h/test_*.py` | PASS |
| Route-B TSV width/safety-boundary audit | PASS: 3 authority, 2 anchor, and 3 budget rows; status/NO_GO/schema checks present |
| `git diff --check` | PASS |
