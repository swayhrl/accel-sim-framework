# AWMA node109 resume after 174 LDGDEPBAR validator hotfix

Execute only after 174-new reports:

`174NEW_SIM_CONSUMER_LDGDEPBAR_VALIDATOR_HOTFIX_PASS`

and provides the exact hotfix commit SHA.

Producer checkpoint to resume:

- branch: `hrl/awma-sim-compat-terminal-recovery-109-v2`
- checkpoint commit: `e46193b94dd969a988126fc9fa5545da08b26d18`
- exact Q05 R3 canary already completed naturally
- records: 13,490,624
- terminal: COMPLETE
- drop=0 / overflow=0
- address mode 2 count = 0
- GPU lock is currently free

## Step 1 — CPU-only real-trace admission cross-check

Before any new GPU run:

1. fetch the exact 174 validator-hotfix commit;
2. build `traceg_grammar_smoke` from that exact committed source against the same repository authoritative `trace_parser.cc` used by the consumer hotfix;
3. hash-close validator source and binary;
4. run it against the existing Q05 R3 `.traceg.xz` artifact from checkpoint `e46193b94dd969a988126fc9fa5545da08b26d18`;
5. preserve stdout/stderr/returncode and parser receipt.

PASS requires the entire real Q05 trace to return `TRACEG_GRAMMAR_PASS`. Do not special-case or skip `LDGDEPBAR` records outside the committed validator rule.

If this cross-check reveals another exact false-positive semantic classification, stop for review with the exact opcode/source-backed semantics; do not mutate producer data to satisfy a lexical heuristic.

## Step 2 — producer formalization

If the existing Q05 R3 real trace passes the committed hotfix validator, continue immediately in solve-and-continue mode.

The producer source/binary already used for R3 remains authoritative unless a new producer-side defect is discovered. The consumer validator hotfix alone does not require changing producer trace bytes.

Run the formal exact Q05 capture under the frozen workload/target identity:

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

Formal PASS requires:

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