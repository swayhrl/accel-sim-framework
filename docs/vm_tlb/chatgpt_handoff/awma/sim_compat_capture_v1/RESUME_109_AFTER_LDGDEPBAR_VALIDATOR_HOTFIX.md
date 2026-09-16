# AWMA node109 resume after 174 LDGDEPBAR validator hotfix

174-new has now formally reported:

`174NEW_SIM_CONSUMER_LDGDEPBAR_VALIDATOR_HOTFIX_PASS`

Accepted hotfix implementation:

- branch: `hrl/awma-sim-consumer-validator-ldgdepbar-174new-v1`
- commit: `fb5d0bebee421a0153661239e1f7c2bc088d5c9e`
- accepted consumer base retained: `25aa29862239a408099639ae9d5f1a0ea4fee1e1`
- hotfix validator source SHA256: `dfc42e9225aa5d7a0e87fc1be8c433580c1bb687deb677c687ec70470187394c`
- authoritative frozen `gpu-simulator/trace-parser/trace_parser.cc` SHA256 remains `9545c56336c8fa25cb7af842ce6955bf4e08b41835f9cfea2dcfa9a8a5802c28`

The hotfix is narrow: exact `LDGDEPBAR` is classified as addressless control; `LDG.E.32 width=0` and `LDGSTS width=0` still fail. Producer bytes, simulator source/binary, Q05 identity, and SIM_BASELINE_ID are unchanged.

Producer checkpoint to resume:

- branch: `hrl/awma-sim-compat-terminal-recovery-109-v2`
- checkpoint commit: `e46193b94dd969a988126fc9fa5545da08b26d18`
- exact Q05 R3 canary already completed naturally
- records: 13,490,624
- terminal: COMPLETE
- drop=0 / overflow=0
- address mode 2 count = 0
- canonical raw -> postprocess -> traceg completed
- GPU lock is currently free

## Step 1 — CPU-only real-trace admission cross-check

Before any new GPU run:

1. fetch exact hotfix commit `fb5d0bebee421a0153661239e1f7c2bc088d5c9e`;
2. build `traceg_grammar_smoke` from that exact committed source against the unchanged repository-authoritative `trace_parser.cc`;
3. verify source SHA256s above and hash-close the locally built validator binary;
4. run it against the existing Q05 R3 `.traceg.xz` artifact from checkpoint `e46193b94dd969a988126fc9fa5545da08b26d18`;
5. preserve command/stdout/stderr/returncode and parser receipt;
6. verify the whole real trace returns `TRACEG_GRAMMAR_PASS`, including the 16,128 `LDGDEPBAR` records;
7. run/retain the relevant negative regressions proving real memory records remain strict.

Do not special-case records outside the committed validator rule. If another exact semantic false positive appears, stop for source-backed review; do not mutate producer bytes to satisfy lexical heuristics.

## Step 2 — prefer promotion of the already-complete R3 trace

Do not automatically recapture Q05 merely because the run was originally called a canary.

First compare the actual R3 capture command/environment/selector/runtime/output policy against the frozen formal producer contract. R3 may be promoted to the formal producer artifact if and only if all of the following are true and are documented with evidence:

- exact frozen workload identity and token/input authority were used;
- exact semantic function + occurrence 0 binding was resolved for that run;
- there was no instruction-count, record-count, time, CTA, warp, kernel-body, or output truncation specific to canary/debug operation;
- tracer source/binary and Route-B address policy are the intended formal producer implementation;
- target ran to natural workload completion;
- terminal COMPLETE is device/channel-derived;
- drop_count=0 and overflow_count=0;
- address mode 2 count=0 under the accepted frozen-baseline compatibility policy;
- canonical raw -> existing post-traces-processing -> traceg path was used;
- the exact hotfix validator passes the complete R3 trace;
- kernelslist/trace members and all required context/launch/address identities are recoverable and hash-closeable;
- no artifact was modified after capture except deterministic canonical post-processing already admitted by contract.

If every item holds, **do not rerun the GPU capture**. Materialize R3 as the formal producer bundle by creating the formal terminal receipt, manifest, hash roots, source/build/binary/runtime receipts, accepted READY publication, final review pack/report, and provenance statement that the previously named canary was promoted because its actual execution satisfied the formal capture contract.

The original label `canary` alone is not a scientific reason to discard an otherwise contract-identical, naturally complete trace.

## Step 3 — recapture only if R3 is not formally promotable

If any canary-only execution difference is found, run exactly one formal capture under the frozen identity:

- model: `Qwen/Qwen2.5-0.5B-Instruct`
- revision: `7ae557604adf67be50417f59c2c2f167def9a775`
- scenario: `S2_TEXT`
- phase: PREFILL
- batch: 1
- prefill tokens: 2048
- decode tokens: 32
- backend: sdpa
- dtype: float16
- target: `Q05_PREFILL_ATTN_FLASH`
- target function occurrence: 0

Re-resolve semantic/function/occurrence binding at run time; a historical numeric kernel ID is not authority.

Whether promoted R3 or one necessary recapture is used, formal PASS requires:

- natural workload completion;
- target terminal COMPLETE derived from device/channel receiver closure;
- drop_count=0;
- overflow_count=0;
- no address-mode 2 records for this frozen-baseline producer policy;
- canonical raw -> existing post-traces-processing -> traceg path;
- exact committed hotfix grammar validator PASS on every listed trace;
- kernelslist/member completeness;
- source/build/binary/tracer/runtime hashes;
- terminal receipt hash;
- bundle/member hash roots;
- workload/target/runtime/launch/address context closure;
- accepted 109 -> durable storage / 174 READY publication;
- final review pack/report;
- commit/push/clean status.

Do not generate `SIM_INPUT_ID` on 109 and do not run Accel-Sim replay on 109.

## Success state

`SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS`

`TERMINAL_PROTOCOL_SM89_RECOVERED_V2`

After PASS, STOP node109. The next stage is 174 independent destination rehash, formal consumer admission, SIM_INPUT_ID, fixed 10k baseline replay, determinism, SIM_RUN_ID and SIM_EVIDENCE.
