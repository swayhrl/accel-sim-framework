# CODEX GOAL — C16 Qwen3 Runtime + Real Executor Closure V14 (node109)

## Mission

Continue from the existing Qwen3 producer campaign, but do not merely clear the current `transformers` blocker and stop again.

In ONE GOAL MODE task:

1. audit all remaining independent producer prerequisites in one comprehensive readiness sweep;
2. establish a hash-closed official Qwen3-compatible runtime;
3. turn the actual V11 campaign driver into a real stage executor;
4. run integration tests against the actual driver, not toy helper functions;
5. if all externally independent prerequisites are satisfied or automatically remediated within this contract, continue immediately into the authorized Qwen3 S2 scientific campaign;
6. keep running through the existing Qwen3 stages until scientific completion, an authorization-supported scoped completion, or a genuine external fail-closed blocker.

Do not stop just because environment setup, framework coding, or a readiness report has completed.

## Base producer state

Existing execution branch:

`hrl/c16-qwen3-8b-unattended-campaign-109-v12`

Expected starting HEAD:

`900588bbb2aaa0106e4ca430002b5eaeb9408ea0`

Preserve all previous blocked attempts as immutable campaign history.

Read first:

`docs/vm_tlb/chatgpt_handoff/c16/qwen3_runtime_executor_v14/CURRENT_AUDIT.md`

Also continue honoring the scientific authority from the prior V12/V13 handoffs and review packs.

Expected final review pack remains:

`docs/vm_tlb/review_packs/C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12/`

Add V14 runtime/executor/readiness evidence to the same campaign pack; do not create a scientifically new Qwen3 campaign merely because engineering infrastructure changes.

---

## P0 — Preserve and classify prior evidence

Do not delete or rewrite:

- original `BLOCKED_INPUT_AUTHORITY` evidence;
- V13 transport/resume receipt;
- `BLOCKED_ENVIRONMENT_RUNTIME_API` evidence;
- prior review-pack hashes.

Create a new immutable resume attempt for V14.

The old V13 executor self-test may remain as historical evidence, but label its scope accurately: `TOY_INVARIANT_TEST_NOT_REAL_DRIVER_INTEGRATION`.

Do not claim that it validated the real executor.

---

## P1 — Comprehensive producer readiness sweep

This sweep is deliberately NOT fail-fast. Check every independent row that can be checked safely before scientific GPU work.

Produce:

`PRODUCER_READINESS_MATRIX.tsv`

with columns at least:

- gate_id
- category
- requirement
- observed_state
- evidence
- auto_remediation_allowed
- remediation_result
- final_status = PASS | BLOCKED | NOT_APPLICABLE
- blocks_gpu_start

At minimum check:

### Authority/assets
- exact Qwen3-8B model id/revision;
- all five expected safetensor shards, index, config, tokenizer files required by runtime;
- V13 S2 payload exact SHA and canonical token SHA;
- V13 S3 payload exact SHA for later conditional use;
- V12 execution authorization and validation SHA bindings.

### Runtime
- Python version;
- current torch/CUDA identity;
- transformers/tokenizers/huggingface-hub/safetensors versions;
- whether `transformers.models.qwen3` exists;
- exact official Qwen3 classes/helpers required for layer execution;
- `pip check` status.

### GPU/toolchain
- GPU UUID/name/compute capability;
- torch CUDA visibility;
- driver/runtime CUDA identity;
- bounded CUDA tensor smoke;
- nsys binary/version;
- ncu binary/version and permission smoke;
- cuobjdump/nvdisasm;
- compiler/toolchain needed for NVBit tool;
- NVBit tool build and a bounded engineering-only instrumentation smoke.

### Storage/transport
- free space at all local staging paths;
- expected budgets for streamed state, formal trace shards, profiler reports and partials;
- atomic `.partial` -> final behavior;
- approved durable transfer/write path needed after capture.

### Pipeline/formal mechanics
- global formal-admission lock path and lock behavior;
- admission command/tool availability;
- read-only reachability/status check for the Pipeline endpoint/path;
- ACK polling mechanism availability;
- do NOT create a new scientific admission during readiness sweep.

### Qwen3 streamed-execution mechanics
- safetensors layer index covers all 36 layers;
- exact per-layer tensor-name/shape inventory can be resolved;
- embedding/final norm/lm_head tensors are locatable;
- official Qwen3 decoder-layer API can express exact hidden/position/attention/KV propagation;
- selected attention backend can execute on the current torch/CUDA stack;
- S2 context/decode dimensions are feasible under streamed mode;
- perform an engineering estimate/probe for S3 later, but S3 is still conditional.

Continue checking the matrix even after a row fails. Do not emit the final BLOCKED decision until the sweep is complete.

Automatically remediate allowed engineering rows and recheck them.

If any external blocker remains, report ALL unresolved independent rows together.

---

## P2 — Establish the official Qwen3 runtime

The current `transformers==4.46.3` environment is not a valid Qwen3 environment.

Use a separate environment; do not mutate historical Qwen2/AWQ environments in place.

Preferred exact runtime:

- `transformers==4.51.0`
- `tokenizers==0.21.0`
- `huggingface-hub==0.30.2`
- retain accepted `torch==2.5.1+cu124` unless an executable test proves incompatibility
- keep other installed dependencies when they satisfy `transformers==4.51.0` metadata and `pip check`.

Search local caches/wheelhouses first.

If the exact runtime wheels are not locally available, this V14 task explicitly permits a narrowly scoped network bootstrap of PINNED PYTHON RUNTIME WHEELS ONLY.

This permission does NOT include downloading/changing model weights, tokenizer authority, input payloads, precision, scientific backend, or semantic targets.

Known expected hashes:

- transformers 4.51.0 wheel: `2e6baa476735ab8adccbaee6961525a0d1ce8c21d49293af30ef5ee4b082f64d`
- tokenizers 0.21.0 Linux x86-64 abi3 wheel: `e84ca973b3a96894d1707e189c14a774b701596d579ffc7e69debfc036a61a04`
- huggingface-hub 0.30.2 wheel: `68ff05969927058cfa41df4f2155d4bb48f5f54f719dd0390103eefa9b191e28`

Procedure:

1. download/copy wheels into a dedicated Qwen3 wheelhouse;
2. hash every wheel before installation;
3. verify known hashes above when those artifacts are used;
4. create a separate Qwen3 venv/environment;
5. install from the local wheelhouse;
6. run `pip check`;
7. record `pip freeze`, package file locations, wheel hashes and Python identity;
8. set scientific execution to local/offline mode after bootstrap;
9. use local model paths, `local_files_only` semantics, no remote-code execution, and safetensors-only checkpoint loading where applicable.

Do not install arbitrary latest versions.

Do not preemptively upgrade torch. `transformers==4.51.0` supports the existing torch family; only change torch if the exact official Qwen3 runtime demonstrably cannot execute, and in that case stop with consolidated evidence unless separately authorized.

Runtime PASS requires executable evidence:

- import Qwen3 config/model/decoder-layer classes;
- import required cache/rotary/mask helpers actually used by the implementation;
- load exact local config;
- instantiate a single official Qwen3 decoder layer;
- load exact layer-0 checkpoint state into that official module and validate all required tensor names/shapes/dtypes;
- run a bounded CUDA engineering smoke through that layer;
- record actual attention implementation/backend;
- prove the smoke used local exact assets and did not fetch model code/weights remotely.

Create:

- `QWEN3_RUNTIME_LOCK.json`
- `QWEN3_RUNTIME_WHEELS.tsv`
- `QWEN3_RUNTIME_SMOKE.json`

---

## P3 — Implement a REAL campaign executor

Current `util/vm_tlb/c16/campaign/driver.py` is not acceptable as the scientific executor because it can emit `FRAMEWORK_ONLY PASS` without stage work.

Upgrade the actual executor code used by the campaign.

Required architecture:

- explicit stage registry/dispatch;
- each scientific stage invokes a real stage implementation or returns BLOCKED/authorized SKIPPED;
- no fallback default that writes PASS;
- immutable attempt directories/receipts;
- contiguous hash-valid dependency chain;
- upstream semantic input digest invalidates downstream reuse;
- process lock per campaign;
- separate global formal-admission lock;
- signal-safe RUNNING/PARTIAL state;
- resumable shard state for formal capture;
- bounded fallback counters;
- no overwrite of earlier terminal attempts;
- actual command/argv, artifact hashes and validator results recorded in receipts.

`FRAMEWORK_ONLY`, `PLAN_ONLY`, `DRY_RUN`, mocks or synthetic fixtures can never produce a scientific PASS receipt.

If a stage handler is not implemented, the driver must emit `BLOCKED_STAGE_EXECUTOR_MISSING_<stage>`, never PASS.

The executor does not have to be over-generalized for every future model in this Goal. It must be real for the authorized Qwen3 campaign and keep a reusable interface.

---

## P4 — Real executor integration tests

Do not test toy helper functions defined only inside the test file.

Tests must invoke the actual driver/state/locking/shard/admission modules used by the campaign, preferably by subprocess in a temporary sandbox.

Required tests:

1. a stage with no real handler cannot PASS;
2. `FRAMEWORK_ONLY` result is rejected by the real receipt validator;
3. a normal small fixture passes stages through the real dispatcher;
4. changing an upstream semantic digest invalidates downstream resume;
5. a non-contiguous/stale receipt chain is rejected by the real resume code;
6. a second campaign process cannot take the same campaign lock;
7. formal admission lock rejects a second admission while ACK is unresolved;
8. interrupted `.partial` shard is never accepted as complete;
9. completed valid shard can be resumed without rerun;
10. prior blocked attempt history remains immutable after resume;
11. authorization/input/static-set hash mutation rejects downstream reuse.

Produce an executable test report with command lines and exit codes:

`REAL_EXECUTOR_INTEGRATION.tsv`

Acceptance requires every test PASS from actual code paths.

Any failure -> no Qwen3 scientific GPU work.

---

## P5 — Exact Qwen3 layer-streaming engine

After runtime and real-executor acceptance, implement/validate the scientific execution path using official Qwen3 runtime modules.

Default execution mode is the already authorized `EXACT_SEMANTIC_LAYER_STREAMING_REPLAY` unless full-resident feasibility is independently proven and selected.

For streamed mode:

- use exact BF16 checkpoint weights;
- use official Qwen3 decoder layer and helper semantics from the pinned runtime;
- load only the necessary layer/components to GPU at a time;
- propagate the exact hidden state through all required decoder layers;
- preserve exact position state, attention mask semantics and per-layer KV cache;
- preserve embedding, final norm and lm-head semantics when producing model-level next-token state;
- no synthetic hidden states;
- no standalone replacement GEMM as a substitute for model state reconstruction;
- no Qwen2 class reuse;
- no quantization/precision substitution.

Before expensive tracing, perform an exact S2 streamed functional smoke that produces deterministic/repeatable model-state evidence sufficient to proceed to target selection/state capture.

Record memory peak and runtime identity.

---

## P6 — Continue the authorized S2 campaign automatically

Once P1-P5 PASS, DO NOT STOP FOR A STATUS REPORT.

Continue the existing scientific workflow automatically:

1. S2 exact input authority recheck;
2. streamed/native authorized smoke;
3. bounded S2 kernel census with synchronized semantic evidence;
4. implementation-class table;
5. semantic candidate table;
6. select one losslessly bound decode MLP-linear anchor for Qwen2.5 lineage continuity when available;
7. optional attention/KV target only if materially distinct and losslessly bindable;
8. exact target state capture;
9. replay equivalence;
10. in-context vs replay signature equivalence using bounded methods;
11. fresh Qwen3 SASS/global-address-path audit;
12. direct GLOBAL and LDGSTS GLOBAL_SOURCE closure independently;
13. detect other address-bearing special paths;
14. prove complete static executed/zero partition;
15. formal capture with resumable deterministic shards;
16. drop=0 and overflow=0;
17. serial admission, ACK before any second admission;
18. application-context NCU with explicit metric units/report hashes;
19. compact supported memory fingerprint;
20. conditional S3 only after S2 closure under existing authorization.

Keep all prior scientific guardrails unchanged.

A required S2 gate failure is BLOCKED, never `PASS_WITH_SCOPED_EVIDENCE`.

---

## P7 — Stop policy for this Goal

Do not stop for automatically resolvable engineering issues covered by V14. Resolve and continue.

Do not stop after runtime installation, readiness sweep, executor implementation, integration tests, or S2 smoke if the next stage is authorized and PASS prerequisites hold.

A final BLOCKED result is allowed only when, after the complete readiness sweep and bounded remediation, continuation requires an EXTERNAL fact or a scientifically forbidden substitution, or a later scientific gate genuinely fails.

Examples of legitimate terminal blockers:

- pinned runtime artifacts cannot be acquired locally or by the narrowly authorized package bootstrap;
- exact Qwen3 official layer API is incompatible with the accepted torch/CUDA stack and fixing it requires an unauthorized torch/backend change;
- exact streamed state reconstruction fails;
- semantic binding/signature remains ambiguous after bounded methods;
- new address-bearing path lacks instrumentation;
- drop/overflow nonzero;
- Pipeline admission/ACK failure;
- storage failure threatens evidence integrity.

If blocked, report ALL known independent unresolved readiness rows plus the terminal scientific blocker, preserve partial evidence, hash-close review pack, commit/push and STOP.

---

## Required final artifacts

Add at least:

- `PRODUCER_READINESS_MATRIX.tsv`
- `QWEN3_RUNTIME_LOCK.json`
- `QWEN3_RUNTIME_WHEELS.tsv`
- `QWEN3_RUNTIME_SMOKE.json`
- `REAL_EXECUTOR_INTEGRATION.tsv`
- real executor source changes;
- S2 execution-mode/input/smoke receipts;
- census/implementation/candidate/target-selection artifacts;
- per-target state/replay/signature/static-audit/formal/ACK/NCU evidence if reached;
- compact memory fingerprint if reached;
- conditional S3 decision;
- updated `FINAL_DECISION.json`, `OPEN_ISSUES.md`, `SHA256SUMS`.

Commit/push the same execution branch and report final HEAD/decision/last completed real stage.
