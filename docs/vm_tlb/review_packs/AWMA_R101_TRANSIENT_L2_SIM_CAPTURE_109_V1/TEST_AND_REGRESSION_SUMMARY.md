
# Tests and regression summary

1. Accepted input payload and HiMuon source hashes matched their receipts; driver audit reproduced accepted normalization and final output bitwise.
2. Route-B formatter selftest PASS; source diff shows unchanged formatter/packet grammar and an opt-in bounded multi-kernel lifecycle only.
3. Payload-free census identified the frozen 18-kernel ROI; all 15 NS arithmetic function/grid/block strata match accepted R101R1.
4. One-kernel `INSTR_END=8` micro-canary: COMPLETE, zero drop/overflow, native traceg grammar PASS.
5. Three-kernel first-iteration canary: 3/3 COMPLETE and grammar PASS, zero drop/overflow. Its real trace size admitted full five-step capture under the preregistered cap.
6. FORMAL full-five-step: 18/18 terminal/trace/list/xz/grammar/frozen-parser/hash checks PASS, exact accepted output SHA and stable region/lifetime binding. No simulator was run.

Failed or excluded diagnostics are retained under node164 `raw/`: eager normalization bitwise mismatch (compiled accepted-style gate later passed), unfrozen Triton autotune geometry mismatch, and `NO_EAGER_LOAD=0` pre-Python memory growth. No excluded data was promoted as FORMAL evidence.
