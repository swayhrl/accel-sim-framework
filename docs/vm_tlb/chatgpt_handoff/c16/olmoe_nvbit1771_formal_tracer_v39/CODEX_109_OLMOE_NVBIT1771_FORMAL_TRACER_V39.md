# C16 OLMoE NVBit 1.7.7.1 formal tracer + variant-A closure — node109 V39

## Execution mode

Execute in **GOAL MODE** on node109.

This is a direct continuation of V38. The scientific target, input, runtime, actual-JIT variant-A identity, complete static audit, and dynamic audit are accepted. The only blocker is that the old V20 formal warp-regsource tracer was built on NVBit 1.7.5 while the actual-JIT selector identity was established with NVBit 1.7.7.1.

The V39 objective is:

`NVBit 1.7.7.1 formal tracer -> lifecycle closure -> exact A canary -> complete formal capture -> serial admission/positive ACK`

Suggested implementation branch:

`hrl/c16-olmoe-nvbit1771-formal-tracer-109-v39`

## Accepted upstream

V38:
- branch `hrl/c16-olmoe-variant-a-formal-109-v38`
- HEAD `7a940a4e324c694edf13d2ad7c94f284eea027fd`
- decision `C16_OLMOE_VARIANT_A_FORMAL_109_V38_FAIL_CLOSED_WARP_REGSOURCE_ACTUAL_JIT_SELECTOR_LIFECYCLE_UNCLOSED`

Accepted V38 evidence:
- formal-protocol fresh probes: variant A = 4/4
- actual variant-A static instruction count = 1096
- complete address-bearing GLOBAL/LDGSTS selected count = 243
- all-static SHA256:
  `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
- normalized complete selector SHA256:
  `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`
- selected-set dynamic audit = 132096 address events
- exact same-process expert58 input / weight / output ranges closed
- old V20 `v20_warp_regsource.so` built on NVBit 1.7.5 produced no trace/terminal for this actual-JIT selector
- empty output is not zero-execution evidence

Scientific target:
- model `allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`
- S2_TEXT B1/T2048/D32 frozen input from V34
- Layer1 decode32
- natural top-8 `[58,59,47,51,25,15,12,48]`
- rank-0 expert58
- `experts[58].down_proj`
- BF16
- input `[1,1024]`
- weight `[2048,1024]`
- output `[1,2048]`
- actual implementation condition: cuBLAS JIT variant A under fixed formal protocol

Do not reopen model/input/semantic target selection.

## Hard version rule

**Do not use the NVBit 1.7.5 V20 tracer binary for V39 formal capture.**

Build and use a new formal tracer against the same NVBit **1.7.7.1** toolchain/API family used by V36/V38 actual-JIT enumeration.

The old V20 tracer may be used only as a semantic reference for:
- warp active-mask handling
- source-register address extraction
- event payload meaning
- drop/overflow accounting
- C16 consumer-compatible output semantics

Do not transplant its old global/context lifecycle wholesale.

## Asset/runtime retention

Node164 remains sole model authority.

Reuse the retained hash-closed node109 OLMoE replica:
`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Reuse exact V34 frozen S2 IDs.

Reuse V36/V38 NVBit 1.7.7.1 actual-function introspection sources/tooling.

At Goal end retain the valid OLMoE replica and the new 1.7.7.1 formal tracer/tool source.

---

# Stage 0 — freeze and receipt the NVBit 1.7.7.1 base

Locate the exact NVBit 1.7.7.1 installation/source already used successfully by V36/V38.

Record:
- NVBit version
- root path
- relevant headers/library hashes
- actual V36/V38 introspector binary/source hashes
- compiler/CUDA toolkit used to build the tool

Use the **official NVBit 1.7.7.1 mem_trace lifecycle/scaffold** already proven to load and enumerate the actual JIT function as the lifecycle base.

Preserve its:
- context-owned state model
- channel creation/init
- receiver thread startup
- device channel pointer setup
- instrumentation activation
- flush/termination
- receiver join
- context teardown ordering

Do not start by patching the V20/NVBit-1.7.5 lifecycle.

If the exact official scaffold copy used in earlier 109 work is available, reuse it and hash it. Otherwise derive from the installed official NVBit 1.7.7.1 examples and record source identity.

---

# Stage 1 — implement `warp_regsource_1771`

Create a new tracer, preferably under a durable C16 tool path such as:

`/data/c16/tools/nvbit1771_warp_regsource_v39/`

or another established node109 durable tools root.

Port only the required C16 event semantics onto the official 1.7.7.1 lifecycle.

## Runtime selection

The tracer must support:
- exact runtime function-name/family matching
- actual static-fingerprint guard
- same-name function occurrence selector for the isolated replay
- single selected static instruction per process/shard
- exact selected source-address register/operand

Before enabling instrumentation:
1. obtain actual loaded `CUfunction`
2. enumerate static instructions with NVBit 1.7.7.1
3. normalize the actual static stream
4. compute the fingerprint
5. require exact variant-A identity
6. rebuild/lookup the selector from the same static stream
7. only then instrument

Known historical B or unknown variant:
- do not apply A indices
- emit typed non-formal retry status
- terminate cleanly
- no formal trace shard

## Event semantics

For each instrumented execution emit enough data to preserve the existing C16 formal semantics:
- selected static instruction identity
- warp active mask
- lane addresses derived from the exact source register
- load/store or path type
- CTA/warp/lane metadata needed by current C16 decoders
- terminal record
- overflow/drop status

Preserve event schema/consumer semantics compatible with the existing C16 formal decoder where possible.

If the binary event layout must change only because of 1.7.7.1 implementation details:
- do not silently call it the old schema
- add an explicit schema version and corresponding bounded decoder
- prove old semantic fields are preserved
- do not change scientific counting definitions

Prefer keeping the existing C16WARP1 event meaning and storing tool/version/fingerprint metadata in sidecar manifests rather than changing analysis semantics.

---

# Stage 2 — lifecycle controls before the scientific canary

Before touching the OLMoE formal target, prove the new 1.7.7.1 tracer lifecycle with bounded controls.

## C0 — no-selected control

Run an isolated CUDA/PyTorch workload with a selector that matches no static instruction.

Require:
- process rc=0
- no segfault/hang
- receiver starts and terminates
- terminal closure is explicit
- event count = 0
- drop=0
- overflow=0

This is lifecycle evidence only. It is not scientific zero-execution evidence.

## C1 — known-selected micro/control

Use a tiny bounded CUDA/PyTorch target with one unquestionably executed selected memory instruction, or a V36/V38-known actual function if simpler.

Require:
- nonzero trace events
- correct terminal
- source-register addresses are plausible and stable
- drop=0
- overflow=0

If C0/C1 fail, fix the new 1.7.7.1 implementation and continue.

Routine build/lifecycle/channel/receiver issues are engineering problems, not scientific stop conditions.

Do not fall back to the 1.7.5 binary merely because porting requires repair.

---

# Stage 3 — regenerate the COMPLETE A selector inside the V39 toolchain

Important: the V38 review pack committed only the summary:

- selected count = 243
- selector SHA = `9d2d4149...`

It did **not** commit 243 per-instruction rows.

Therefore V39 must regenerate and persist the complete selector from the actual loaded variant-A function using the same NVBit 1.7.7.1 static identity as the new tracer.

Require:
- all static instruction count = 1096
- all-static normalized SHA:
  `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
- selected address-bearing count = 243
- normalized selector SHA:
  `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

If any of these identities differ:
- first diagnose serialization/normalization differences
- compare actual instruction rows
- fail closed only if the actual variant-A static function has materially changed

Persist all 243 rows, including:
- static index
- PC/offset
- opcode
- path class
- load/store
- memory-space classification
- exact address source register / operand index
- width/vector information where available

No two-row/example-only selector is acceptable.

---

# Stage 4 — exact formal-protocol A identity

Run at least 4 fresh processes under the **new V39 1.7.7.1 formal tracer lifecycle** before the scientific canary.

For each record:
- actual function name
- normalized static fingerprint
- selected-set hash
- grid/block
- nregs/shmem
- replay output hash
- observed variant

A must be naturally obtainable.

If historical B/unknown appears:
- preserve evidence
- do not instrument with A selector
- retry naturally

Do not alter cuBLAS algorithm/backend/workspace/determinism/stream policy.

---

# Stage 5 — actual OLMoE canary

Run multiple bounded canaries that collectively cover:
- at least one selected instruction proven to read EXPERT_DOWN_INPUT
- at least one selected instruction proven to read EXPERT_DOWN_WEIGHT
- at least one selected instruction proven to write EXPERT_DOWN_OUTPUT
- at least one LDGSTS/global-source path if the 243-set contains such a path

For each canary:
- fresh process/output root
- exact frozen expert58 replay
- actual A fingerprint guard
- exact selected static instruction
- exact source register
- function occurrence closed
- sufficient capacity
- terminal closure
- drop=0
- overflow=0

Same-process ADDRESS_CONTEXT:
- EXPERT_DOWN_INPUT
- EXPERT_DOWN_WEIGHT
- EXPERT_DOWN_OUTPUT
- WORKSPACE_IF_PROVEN
- OTHER_OR_UNCLASSIFIED

Canary PASS requires:
- trace exists
- terminal exists
- target function/fingerprint proof exists
- events map to expected typed object for the chosen instruction
- no stale selector

Empty trace is NOT a zero-execution proof at canary stage.

---

# Stage 6 — complete formal variant-A capture

After canary PASS, capture one formal run:

`C16R_olmoe-1b-7b-0125-instruct_s2-text_decode_nvbit1771-warp-mref-shard_v39-l1-d32-natural-expert58-down-jitA_<timestamp>_<suffix>`

Formal policy:
- semantic target = natural expert58 down_proj
- implementation condition = actual JIT variant A
- complete 243 selected static set
- one selected static instruction per independently replayed shard
- fresh process per shard
- A fingerprint guard in every process
- B/unknown -> typed retry, never instrumented with A selector
- exact source register per row
- receiver terminal closure
- drop=0
- overflow=0
- same-process ADDRESS_CONTEXT
- executed/zero partition derived only from clean terminally closed shards

A clean zero-event shard is allowed only when:
- A fingerprint guard passed
- selected instruction identity passed
- tracer lifecycle passed
- terminal record exists
- drop=0/overflow=0
- no events occurred

This is distinct from V38's empty-output failure.

If a shard overflows:
- exclude that attempt
- recapture only that shard in a fresh recovery root with higher capacity

Use a bounded natural-A retry policy; if A unexpectedly becomes unavailable across many shards, diagnose environment/tool drift rather than forcing cuBLAS.

---

# Stage 7 — formal analysis

Report:
- selected static count = 243 or scientifically explained closed delta
- executed / zero partition
- total active-lane events
- per-executed-shard event min/max/median
- per-shard unique 128B lines min/max/median
- per-shard unique 4K pages min/max/median
- per-shard unique 64K pages min/max/median
- per-shard unique 2M pages min/max/median
- typed event fractions:
  - EXPERT_DOWN_WEIGHT
  - EXPERT_DOWN_INPUT
  - EXPERT_DOWN_OUTPUT
  - WORKSPACE_IF_PROVEN
  - OTHER_OR_UNCLASSIFIED
- full-scope result

Do not construct:
- cross-shard VA union
- global shard chronology
- reuse distance
- cache/TLB causality

---

# Stage 8 — serial formal admission

Mandatory:
`FORMAL_ADMISSION_CONCURRENCY=1`

Complete:
`source manifest -> transfer -> destination verification -> catalog admission -> positive ACK`

Only one OLMoE formal anchor is required.

---

# Stage 9 — third-lineage handoff

If formal capture + positive ACK close, authorize exactly:

`OLMOE_VARIANT_A_NVBIT1771_FORMAL_ANCHOR_CLOSED_FOR_THREE_LINEAGE_MOE_CONSUMER`

Handoff must state:
- OLMoE anchor is variant-A conditioned
- actual runtime A was naturally obtained under the V39 formal protocol
- historical V36 B remains an unformalized alternate instrumentation-context variant
- no OLMoE implementation-variant invariance claim
- no matched-input causal claim across three lineages

Do not authorize more OLMoE operators/scenarios unless the later consumer identifies a concrete scientific gap.

---

# Required review pack

Create:

`docs/vm_tlb/review_packs/C16_OLMOE_NVBIT1771_FORMAL_TRACER_109_V39/`

Include at least:
- `UPSTREAM_V38_AUTHORITY.json`
- `NVBIT1771_BASE_RECEIPT.json`
- `WARP_REGSOURCE_1771_BUILD_RECEIPT.json`
- `LIFECYCLE_C0_NOSELECT.json`
- `LIFECYCLE_C1_SELECTED.json`
- `VARIANT_A_FUNCTION_IDENTITY.json`
- `VARIANT_A_ALL_STATIC_INSTRUCTIONS.tsv`
- `VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv`  **all 243 rows**
- `VARIANT_A_SELECTOR_IDENTITY.json`
- `FORMAL_PROTOCOL_VARIANT_PROBES.tsv`
- `VARIANT_A_CANARY.json`
- `VARIANT_A_FORMAL_SUMMARY.json`
- `VARIANT_A_FORMAL_SHARDS.tsv`
- `VARIANT_A_ADDRESS_MEMBERSHIP.json`
- `VARIANT_A_ADMISSION_ACK.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full PASS:

`C16_OLMOE_NVBIT1771_FORMAL_TRACER_109_V39_PASS`

Only PASS after:
- 1.7.7.1 lifecycle C0/C1 closes
- complete A selector identity closes to V38
- OLMoE canary closes
- all formal shards are clean
- positive admission ACK closes

## Valid fail-closed reasons

Scientific/evidence blockers:
- actual A static identity materially changes
- complete 243-set cannot be reproduced
- actual A cannot be naturally obtained under V39 formal protocol
- same-process target attribution fails
- formal shard drop/overflow/terminal/full-scope cannot be repaired
- admission/ACK fails with an evidence-integrity issue

Routine tracer build, callback, channel, receiver, teardown, output-path, retry orchestration, and capacity bugs are engineering problems: solve and continue.

## Git / cleanup / retention

Use node109 existing Git transport. Do not install/configure `gh`.

At end:
- review pack -> SHA256SUMS -> commit -> push -> canonical git ls-remote verify
- release GPU lock
- unload GPU
- no stale NVBit/profiler/CUDA processes
- GPU baseline restored
- retain valid OLMoE replica
- retain the new NVBit 1.7.7.1 formal tracer + source under durable C16 tools
- clean worktree
