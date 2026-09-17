# C16 Qwen3-30B-A3B S2 formal capture V3 — tracer recovery + formal campaign

## Execution mode

Execute this task in **GOAL MODE** on node109.

This is a continuation from the accepted fail-closed V2 result. Do not redo scientific target discovery, natural routing discovery, or full S2 semantic-state generation unless an accepted authority is genuinely invalidated.

Use node109's existing Linux Git workflow/authentication. Do not install/configure `gh`. Do not use a Windows repository mirror.

## Upstream authority

Accepted V2 branch / HEAD:

`hrl/c16-qwen3-30b-s2-formal-capture-109-v2`

`cfacb6456d607fca2b6dab4ccb80b6781ec95e97`

Accepted V2 decision:

`C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V2_BLOCKED_RAW_TRACER_ALIGNMENT`

Accepted V2 review pack:

`docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V2/`

The corrected Decode Expert scientific identity is already frozen and must not be changed merely to make tracing easier:

- natural top-8: `[21,89,108,62,111,23,125,8]`
- selected natural expert: `21`
- semantic operator: `model.layers.24.mlp.experts.21.down_proj`
- kernel family/function: `internal::gemvx<int7>`
- exact full-layer selector: function-local occurrence 9, NVBit inventory global ordinal 198
- full-layer grid: `512x1x1`
- block: `32x4x1`
- code-object SHA256: `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`
- fresh static GLOBAL MREF count: `243`
- static map SHA256: `c4ccd2975bb407f84e099f2e5b1651ed263d1b09876036e0a99b905478cea5a5`

The V2 blocker is engineering-only:

- direct targeted callback reached the correct function;
- static index 810 was shown to reach the natural selected-expert activation range;
- the old compact one-MREF raw-buffer tracer failed to terminal-close on a known-positive `static810/CTA100` path;
- zero-record selectors must not be interpreted as scientific zero execution when independent evidence proves the kernel executes.

No formal raw was created, transferred, admitted, or ACKed in V2.

---

# Core strategy

Do **not** spend another long round patching the old compact full-layer raw tracer first.

The preferred recovery route is to reuse the already successful C16 formal producer pattern demonstrated by DeepSeek V23R1 and Qwen3 V20:

`exact semantic state -> isolated exact operator replay -> fresh process per static MREF -> known-good warp-regsource tracer -> same-process ADDRESS_CONTEXT -> terminal close -> formal shard set`

Known-good precedent from DeepSeek V23R1:

- tracer binary: `/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so`
- fresh process for each static MREF;
- clear inherited `C16_*` and `CUDA_INJECTION64_PATH` before setting the exact capture environment;
- use exact function selector;
- use `C16_WARP_FUNCTION_OCCURRENCE=0` when the isolated replay invokes the target function exactly once;
- derive load-source address register from the actual SASS/static map;
- require `C16_WARP_TERMINAL` and process return code 0;
- no formal shard is accepted merely because a file exists.

The purpose of V3 is to replace the unreliable full-layer occurrence-dependent compact trace path with a simpler, semantically exact, terminal-closing isolated operator path whenever possible.

---

# Stage 0 — platform / lock / authority revalidation

Before GPU work:

- verify expected RTX4080 / UUID / driver;
- inspect `/data/c16/locks/c16_gpu_campaign.lock`;
- acquire lock normally;
- never kill or bypass another scientific workload.

Revalidate, without regenerating:

- accepted S2 Decode3 Layer24 state authority;
- V2 natural-routing receipt;
- expert-21 down-projection input/output/weight identities;
- V2 fresh static map and code-object SHA;
- V2 review-pack SHA256SUMS.

Do not rerun the full 48-layer S2 semantic stream if accepted states remain intact.

---

# Stage 1 — build an isolated exact semantic replay for expert-21 down_proj

Create the smallest fresh-process replay that executes exactly:

`model.layers.24.mlp.experts.21.down_proj`

using:

- the exact naturally routed expert-21 down-projection input activation frozen from the accepted S2 Decode3 Layer24 replay;
- the exact original BF16 expert-21 `down_proj` weights/bias if applicable;
- the exact runtime implementation/backend already frozen for Q30;
- no synthetic activation;
- no forced routing used to create the source activation;
- no altered precision/backend.

The routing decision remains an upstream semantic receipt proving that expert 21 was naturally selected. The isolated operator replay itself may directly consume the already-frozen naturally routed activation.

## Required equivalence gate

Prove the isolated operator output is bitwise equal to the corresponding in-context expert-21 `down_proj` output, or use a stricter already-established exact numeric criterion if bitwise comparison is impossible for a documented deterministic reason.

Persist:

- input shape/dtype/stride/SHA256/storage range;
- weight shape/dtype/SHA256/storage range;
- output shape/dtype/stride/SHA256/storage range;
- natural-routing receipt SHA;
- in-context vs isolated output equality;
- exact function/grid/block signature.

If isolated replay does not reproduce the exact semantic operator, fail closed. Do not substitute another expert/projection.

---

# Stage 2 — known-good tracer A/B recovery gate

The goal is to distinguish tracer/lifecycle problems from semantic/operator problems quickly.

## 2A. Known-good control

Before blaming node109/NVBit globally, run one very small known-good control using the already accepted tracer scaffold, preferably an existing DeepSeek V23R1 or Qwen3 V20 isolated replay canary that previously terminal-closed on this machine.

Require:

- process return code 0;
- `C16_WARP_TERMINAL` observed;
- no overflow/drop;
- bounded completion.

If the known-good control now fails, classify a tool/environment regression and repair the shared tracer scaffold before Q30-specific work.

## 2B. Q30 isolated canary

Use the same known-good tracer scaffold on the isolated expert-21 `down_proj` replay.

Important environment discipline:

- start from `os.environ.copy()`;
- remove all inherited keys beginning with `C16_`;
- remove inherited `CUDA_INJECTION64_PATH`;
- set only the target-specific environment;
- do not inherit `C16_CTA_BEGIN`, `C16_CTA_END`, old occurrence selectors, or old output paths.

Use a fresh output directory.

The isolated replay should normally make the target function occurrence `0` for the tracer. Verify rather than assume this.

Run at least two bounded canaries if the static SASS supports them cleanly:

1. one source/load MREF that can be attributed to expert weight or exact routed activation;
2. one output/store MREF, or another independent source MREF if the kernel does not expose a clean store in the same function.

Do not hard-code static810 as the only required positive canary. Static810 is historical positive-path evidence from the full-layer tracer investigation. Select canaries from the fresh static map and actual isolated replay evidence.

For every load, derive the source address register pair from actual SASS. Do not assume generic MREF operand semantics.

Required canary PASS:

- process exits within a bounded time;
- `C16_WARP_TERMINAL` present;
- trace parses successfully;
- overflow/drop = 0;
- at least one active address joins an expected same-process semantic range;
- CTA extent is consistent with the isolated kernel launch;
- no inherited CTA slicing.

If this passes, freeze the isolated replay as the formal Decode Expert capture harness.

---

# Stage 3 — bounded fallback only if isolated known-good tracer still fails

Do not return immediately to a broad 243-index blind scan.

Use the following decision tree.

## Case A: known-good control fails too

Classification:

`SHARED_NVBIT_TRACER_OR_ENVIRONMENT_REGRESSION`

Repair the shared known-good tracer scaffold/build/runtime first. Re-run the same two control canaries. Do not alter Q30 semantics.

## Case B: known-good control passes, Q30 isolated replay hangs/nonterminal

Classification:

`Q30_ISOLATED_TRACER_LIFECYCLE_FAILURE`

Compare only the bounded lifecycle differences between the successful DeepSeek/Qwen3 scaffold and Q30 isolated replay:

- CUDA context creation/destruction;
- receiver/channel teardown;
- process exit path;
- function occurrence handling;
- output flush/terminal marker;
- callback record volume/capacity;
- target kernel launch count.

Prefer transplanting the known-good official/accepted lifecycle scaffold over repeatedly patching the old compact tracer.

## Case C: terminal-close passes but addresses do not join expected semantic ranges

Classification:

`Q30_ADDRESS_EXTRACTION_OR_OPERAND_SEMANTICS_FAILURE`

Audit actual SASS address registers and load/store address semantics. Use typed register-source extraction as in V20/V23R1. Do not call this a zero-execution result.

## Case D: object join passes but CTA/full-scope is partial

Classification:

`Q30_SCOPED_CAPTURE_ONLY`

Clear inherited CTA filters / occurrence selectors and repair the selector. Do not admit as full-scope formal evidence.

The repair stage is bounded. Once the isolated tracer gate passes, continue automatically into formal capture.

---

# Stage 4 — freeze corrected four-target portfolio

Keep exactly four semantic targets unless a true blocker invalidates one.

1. `S2_DEC3_NATURAL_EXPERT21_DOWN`
   - S2/T2048 Decode3
   - naturally selected expert 21
   - `model.layers.24.mlp.experts.21.down_proj`
   - formal harness should use the exact isolated semantic replay if Stage 2 closes

2. `S2_PF_EXPERT_GEMM`
   - accepted V1 S2 Prefill expert target

3. `S2_DEC3_ATTENTION_SPLITKV`
   - accepted V1 S2 Decode attention/KV target

4. `S2_PF_ATTENTION_FLASH`
   - accepted V1 S2 Prefill attention target

Do not reintroduce the old S0 Decode Expert target merely because the new tracer was difficult.

Before launching a full sharded campaign for each of targets 2–4, run one bounded terminal-close canary with the final tracer/scaffold. This prevents wasting tens of minutes on a target whose capture harness is not operational.

If the old full-layer occurrence selector is required for targets 2–4, verify its exact terminal behavior with a canary before launching all shards.

---

# Stage 5 — complete formal capture campaign

Recommended order:

1. `S2_DEC3_NATURAL_EXPERT21_DOWN`
2. `S2_PF_EXPERT_GEMM`
3. `S2_DEC3_ATTENTION_SPLITKV`
4. `S2_PF_ATTENTION_FLASH`

Hard global rule:

`FORMAL_ADMISSION_CONCURRENCY=1`

For each target:

- create a fresh capture root;
- freeze exact source/state/semantic receipt;
- freeze exact function/code-object/static map;
- capture every frozen address-bearing static shard independently;
- same-process `ADDRESS_CONTEXT` per shard;
- require terminal closure;
- require drop=0 and overflow=0;
- classify executed vs `ZERO_EXECUTION_PROVEN` only when the tracer/selector is independently proven operational;
- audit CTA/full-scope appropriate to the target;
- hash-close local bundle;
- transfer to node164;
- verify destination hashes;
- submit exactly one formal admission;
- wait for positive ACK before the next target begins admission.

Do not create cross-shard chronology, cross-replay VA union, or reconstructed reuse distance.

For expert-21 Decode target, preserve natural-routing receipt and expert-specific weight/activation object attribution with the formal run.

---

# Stage 6 — review / final decision

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V3/`

Include at minimum:

- `UPSTREAM_AUTHORITY.tsv`
- `TRACER_RECOVERY_CONTROL.json`
- `DECODE_EXPERT21_ISOLATED_REPLAY.json`
- `DECODE_EXPERT21_TRACER_GATE.json`
- `CORRECTED_FORMAL_CAPTURE_PORTFOLIO.tsv`
- per-target static/path receipts
- per-target formal summaries
- per-target admission/ACK receipts
- `FORMAL_CAPTURE_TOTAL_SUMMARY.json`
- `NCU_TYPED_EVIDENCE.json` or a scoped reuse receipt if no new NCU is scientifically necessary
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Full PASS requires all four corrected targets to be formally captured and positively ACKed:

`C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V3_PASS`

If tracer recovery still fails before formal raw, emit a typed engineering blocker, preserve the already accepted scientific target identity, hash-close the partial review pack, commit/push, release lock, and STOP.

---

# Git / cleanup

Suggested implementation branch:

`hrl/c16-qwen3-30b-s2-formal-capture-109-v3`

After completion or a genuine fail-closed blocker:

- commit only Goal-owned artifacts;
- push actual HEAD;
- verify canonical repository identity;
- verify `LOCAL_HEAD == git ls-remote` SHA;
- require clean worktree;
- release `/data/c16/locks/c16_gpu_campaign.lock`;
- verify no profiler/Q30 CUDA process remains;
- verify GPU returns to expected baseline;
- report final branch/SHA/decision and STOP.

Do not ask the user to perform routine Git closure manually.
