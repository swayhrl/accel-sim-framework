# C16 OLMoE NVBit 1.7.7.1 variant-A formal closure — node109 V39R2

## Goal mode

Execute in **GOAL MODE** on node109.

This is the final execution continuation of V39. The NVBit 1.7.7.1 C16WARP1 producer/receiver implementation is now accepted engineering baseline evidence. Do not redesign it unless a real regression appears.

Suggested implementation branch:

`hrl/c16-olmoe-nvbit1771-formal-capture-109-v39r2`

## Accepted implementation baseline

Implementation branch/HEAD:

`hrl/c16-olmoe-nvbit1771-formal-tracer-109-v39@b60aaf9bad28f56a8ef494e25f084ee4c7072330`

Accepted:
- new tracer is NVBit 1.7.7.1, not V20/1.7.5 binary
- official 1.7.7.1 mem_trace lifecycle/channel/receiver base
- exact historical C16WARP1 final wire semantics
- G1 nonzero fixture:
  - producer 128
  - receiver 128
  - serialized 128
  - sequence 0..127
  - overflow 0
  - terminal count 1
  - unchanged historical parser PASS
- G2 engineering zero fixture:
  - producer=receiver=serialized=0
  - overflow 0
  - terminal count 1
  - valid binary
  - unchanged historical parser classifies ZERO_EXECUTION_PROVEN
- G4 corrupted producer/receiver count is rejected by independent accounting validator
- sequence is transport-only and is not written into C16WARP1
- no fake legacy raw drop field

## Scientific target remains frozen

Model:
`allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Scenario:
`S2_TEXT B1/T2048/D32`

State:
- Layer1 decode32
- natural top-8 `[58,59,47,51,25,15,12,48]`
- rank-0 expert58

Semantic target:
`experts[58].down_proj`

Shapes:
- input `[1,1024]` BF16
- weight `[2048,1024]` BF16
- output `[1,2048]` BF16

Implementation condition:
- actual SM89 cuBLAS BF16 `internal::gemvx`
- natural JIT variant A under the fixed formal protocol
- historical V36 variant B remains unformalized alternate implementation evidence and is not a blocker

Do not reopen model/input/target/variant-B policy.

## Asset residency

Node164 remains sole model authority.

Reuse retained node109 replica after hash closure:

`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Do not recopy from node164 if the required 11-file subset still closes to receipt SHA:

`01319b411b07ccd7b53c4f653bd5986a51604d9c2c16be7412257e994ff49d13`

Retain the valid replica at Goal end.

---

# Stage 0 — close the final engineering-baseline review evidence

The implementation commit contains G1/G2/G4, but the final committed V39R2 pack must also contain auditable baseline evidence for C0/C1/G0/G3.

Do a bounded regression using the **current committed 1.7.7.1 producer/receiver**.

Record:

### C0
No-selected lifecycle control:
- rc=0
- valid lifecycle closure
- no segfault/hang
- no scientific zero claim

### C1
Known-selected lifecycle control:
- nonzero dynamic trace
- terminal/lifecycle closure

### G0
Run the unchanged historical C16WARP1 parser/auditor on at least one previously accepted historical shard and record PASS.

### G3
Negative parser regression:
- missing terminal rejected
- terminal/header count mismatch rejected
- overflow nonzero rejected
- callback_records != records_written rejected
- truncated/trailing binary rejected

Do not change the historical parser to make tests pass.

Bind source/parser SHAs and exact test artifact hashes.

Do not spend substantial GPU time here; these are bounded final-pack regressions.

---

# Stage 1 — regenerate exact actual-A static authority with the committed tracer toolchain

Use the same NVBit 1.7.7.1 actual-JIT static enumeration family.

Naturally obtain variant A under the formal runtime.

Require exact V38 identity unless a normalization-only difference is proven:

- static instruction count = `1096`
- normalized all-static SHA256 =
  `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
- complete selected GLOBAL/GLOBAL_TO_SHARED/address-bearing count = `243`
- normalized selector SHA256 =
  `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

Persist **all 1096 static rows** and **all 243 selected rows**.

For each selected row include:
- static index
- PC/offset
- opcode
- memory-space/path class
- load/store
- MREF operand index
- exact load source-register pair where required
- width/vector metadata where available
- static fingerprint

Do not reuse the two old example rows as if complete.

If hashes differ:
1. check exact normalization/serialization
2. compare row-by-row
3. fail closed only if actual A static identity materially changed

---

# Stage 2 — current-formal-protocol A probes

Run at least 4 fresh processes with the **committed 1.7.7.1 C16WARP1 tracer environment**.

For each record:
- actual function name
- variant
- static fingerprint
- selected-set hash
- grid/block
- nregs/shmem
- replay output hash

A must be naturally available.

If historical B appears:
- mark `NATURAL_VARIANT_MISMATCH_B`
- do not apply A selector
- retry naturally

If unknown:
- preserve evidence
- do not trace with stale A selector
- retry naturally

Do not set cuBLAS algorithm/backend/workspace/determinism/stream controls to force A.

Bound: if A cannot be obtained in 16 probes, fail closed as runtime drift.

---

# Stage 3 — exact same-process semantic address context

For every scientific canary/formal shard, generate same-process address context from the exact replay.

At minimum:
- `EXPERT_DOWN_INPUT`
- `EXPERT_DOWN_WEIGHT`
- `EXPERT_DOWN_OUTPUT`

Optional only if independently proven:
- `WORKSPACE`

Store:
- base
- bytes
- end-exclusive
- dtype
- shape
- semantic role

No absolute VA relation across different shard processes.

---

# Stage 4 — dynamic selector audit and canary choice

Before formal capture, run a bounded dynamic audit of the complete 243 selected set with the new tracer/introspection tools to identify representative canary rows.

Choose canaries that collectively prove:

1. one actual instruction reads `EXPERT_DOWN_INPUT`
2. one actual instruction reads `EXPERT_DOWN_WEIGHT`
3. one actual instruction writes `EXPERT_DOWN_OUTPUT`
4. one GLOBAL_TO_SHARED / LDGSTS global-source path if such a path exists in the 243 selected set

Do not assume a row's object class from opcode alone.

Persist the row->typed-role evidence.

---

# Stage 5 — scientific canaries with the new 1.7.7.1 C16WARP1 producer

For each chosen canary:

- fresh process
- exact frozen expert58 replay
- actual variant-A fingerprint guard
- exact function occurrence
- exact static index
- exact address-source mode
- sufficient capacity
- valid C16WARP1 binary
- exact one terminal
- producer/receiver/finalized counts close
- sequence closure
- overflow=0
- accounting validator PASS
- unchanged historical C16WARP1 parser/auditor PASS
- expected same-process semantic object receives nonzero hits

A known B/unknown process is a non-formal retry.

Empty file/missing terminal is never a valid zero.

Canary PASS is mandatory before the 243-shard campaign.

---

# Stage 6 — complete 243-shard formal capture

After canary PASS, capture exactly one formal OLMoE variant-A anchor.

Suggested run ID:

`C16R_olmoe-1b-7b-0125-instruct_s2-text_decode_nvbit1771-warp-mref-shard_v39r2-l1-d32-natural-expert58-down-jitA_<timestamp>_<suffix>`

Formal set:
- exact 243 selected static instructions
- one independently replayed selected static instruction per shard
- fresh process per attempt
- exact variant-A fingerprint guard
- exact function occurrence
- exact per-row source-register/MREF address mode
- same-process address context

For every clean shard require:
- selector identity passes
- A fingerprint passes
- lifecycle closes
- valid C16WARP1 binary exists
- exact terminal exists
- producer==receiver==serialized count
- sequence gaps=0
- duplicates=0
- malformed packet=false
- overflow=0
- unchanged historical parser/auditor accepts

Classification:
- count > 0 -> `EXECUTED_SHARD`
- count == 0 with all closure conditions above -> `ZERO_EXECUTION_PROVEN`

If:
- B/unknown -> retry naturally
- overflow -> exclude and recapture at higher capacity
- accounting mismatch -> exclude and repair/recapture
- missing terminal -> exclude and repair/recapture

No failed attempt may enter the formal shard set.

Use bounded automated retries rather than manual babysitting.

---

# Stage 7 — local complete-set audit

Require exact coverage:

`executed_set UNION zero_set == complete_243_set`

and:

`executed_set INTERSECT zero_set == empty`

Produce:
- shard manifest
- complete-set SHA
- all per-shard trace SHA256
- all ADDRESS_CONTEXT SHA256
- terminal/accounting status
- retry/excluded-attempt ledger

Do not mistake a natural variant-mismatch retry for a zero shard.

---

# Stage 8 — formal descriptive analysis

Compute independently from clean shards:

- selected static count
- executed count
- zero-execution-proven count
- total active-lane address events

For **per-executed-shard distributions**:
- event count min/max/median
- unique 128B lines min/max/median
- unique 4K pages min/max/median
- unique 64K pages min/max/median
- unique 2M pages min/max/median

Typed event fractions:
- `EXPERT_DOWN_WEIGHT`
- `EXPERT_DOWN_INPUT`
- `EXPERT_DOWN_OUTPUT`
- `WORKSPACE_IF_PROVEN`
- `OTHER_OR_UNCLASSIFIED`

Primary page/line evidence is per-shard.

If reporting sums of unique counts across shards, label exactly:
`SUM_OF_PER_SHARD_UNIQUES`

Do NOT compute or claim:
- cross-shard VA union
- cross-shard chronology
- cross-shard reuse distance
- cache/TLB causality
- global hardware arrival order

---

# Stage 9 — formal container and serial admission

Build one immutable formal run bundle with:
- frozen static map
- complete selector
- per-shard binaries/logs/accounting/address contexts
- logical shard manifest
- local close receipt
- RUN_MANIFEST

Mandatory:
`FORMAL_ADMISSION_CONCURRENCY=1`

Perform serially:
1. local close
2. transfer to node164 inbox
3. destination verification
4. catalog admission
5. positive ACK

Node164 accepted raw/catalog is immutable.

Require positive ACK before declaring the producer line closed.

---

# Stage 10 — third-lineage handoff

After positive ACK authorize exactly:

`OLMOE_VARIANT_A_NVBIT1771_FORMAL_ANCHOR_CLOSED_FOR_THREE_LINEAGE_MOE_CONSUMER`

Handoff fields:
- model/revision
- exact input authority
- S2/L1/decode32
- natural top-8
- selected expert58
- semantic target
- variant-A condition
- function/fingerprint/grid/block
- shapes
- complete static selected count
- executed/zero
- active events
- per-shard event/page/line distributions
- typed object fractions
- source manifest SHA
- destination verification SHA
- catalog entry SHA
- positive ACK SHA

Explicit boundaries:
- historical variant B exists but is not formalized
- no OLMoE implementation-variant invariance claim
- no matched-input causal claim across Q30/DeepSeek/OLMoE
- no cache/TLB causality claim

Do not authorize another OLMoE operator/scenario unless the later independent consumer identifies a concrete scientific gap.

---

# Required final review pack

Use/finalize:

`docs/vm_tlb/review_packs/C16_OLMOE_NVBIT1771_FORMAL_TRACER_109_V39/`

The final pack must include at least:

- `UPSTREAM_V38_AUTHORITY.json`
- `NVBIT1771_BASE_RECEIPT.json`
- `WARP_REGSOURCE_1771_BUILD_RECEIPT.json`
- `C16WARP1_SOURCE_AUTHORITY.json`
- `C16WARP1_SCHEMA_CONTRACT.md`
- `C16WARP1_1771_IMPLEMENTATION_RECEIPT.json`
- `C16WARP1_INTERNAL_PACKET_CONTRACT.md`
- `C16WARP1_ACCOUNTING_CONTRACT.md`
- `C0_NOSELECT.json`
- `C1_SELECTED.json`
- `G0_HISTORICAL_REGRESSION.json`
- `G1_NONZERO_FIXTURE.json`
- `G2_ZERO_FIXTURE.json`
- `G3_PARSER_NEGATIVE.json`
- `G4_ACCOUNTING_NEGATIVE.json`
- `VARIANT_A_FUNCTION_IDENTITY.json`
- `VARIANT_A_ALL_STATIC_INSTRUCTIONS.tsv`
- `VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv`
- `VARIANT_A_SELECTOR_IDENTITY.json`
- `FORMAL_PROTOCOL_VARIANT_PROBES.tsv`
- `VARIANT_A_TYPED_DYNAMIC_AUDIT.json`
- `VARIANT_A_CANARY.json`
- `VARIANT_A_FORMAL_SUMMARY.json`
- `VARIANT_A_FORMAL_SHARDS.tsv`
- `VARIANT_A_ADDRESS_MEMBERSHIP.json`
- `VARIANT_A_ADMISSION_ACK.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred final decision:

`C16_OLMOE_NVBIT1771_FORMAL_TRACER_109_V39_PASS_WITH_FORMAL_VARIANT_A_ANCHOR`

Only PASS after positive admission ACK.

---

# Stop boundary

Routine engineering problems are solve-and-continue:
- tracer build
- callback/lifecycle
- channel drain/accounting
- output path
- variant-A retry
- per-shard capacity
- malformed attempt replacement
- parser invocation
- transfer mechanics
- Git mechanics

Stop only for:
- actual-A static identity materially changes
- scientific WRec/count semantics must change
- same-process target attribution cannot close
- complete 243-set cannot be captured after bounded repairs
- evidence-integrity admission/ACK cannot close

---

# Git / cleanup

Use node109 existing Git transport. Do not install/configure `gh`.

At end:
- finalize review pack
- regenerate SHA256SUMS over final pack
- commit
- push
- canonical `git ls-remote` verification
- clean worktree
- release GPU lock
- no stale CUDA/NVBit/profiler process
- GPU baseline restored
- retain valid OLMoE replica
- retain the new NVBit 1.7.7.1 tracer/tool source
- STOP
