# C16 Asset Readiness V6 — Current Scope and Guardrails

## Context

Node109 is currently executing the V5 LDGSTS special-path capture goal. Do not compete with or redirect that work.

Node174-new has completed Qwen0 Decode consolidation at:

- branch: `hrl/c16-qwen0-decode-analysis-174new-v4`
- final commit: `1447bf9bb19bd249c116f53287a1f768170848c7`
- implementation commit: `01fe0b1181f06c4d572ac33da52cf42f7e8f69e4`

This V6 task is waiting-time preparation only. It must reduce future setup cost without starting a new scientific campaign.

## Canonical storage

Long-term C16 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Expected classes:

- `assets/models/` — canonical reusable model assets
- `assets/sources/` — reusable source/tool assets such as AutoAWQ kernels
- `provenance/historical_snapshots/` — historical read-only evidence
- current formal capture data — discover from catalog; do not assume path layout
- `derived/` — parsed/features/datasets
- `catalog/` — formal entries/snapshots

The catalog and hash-closed receipts are authority. Directory naming alone is not authority.

## Known canonical model identities

Audit, do not silently replace:

- Llama-3.2-1B: `4e20de362430cd3b72f300e6b0f18e50e7166e08`
- Qwen2.5-0.5B-Instruct: `7ae557...a775` (resolve full revision from archived authority; do not guess)
- Qwen2.5-7B-Instruct raw: `a09a35...bc28` (resolve full revision from archived authority; do not guess)
- Qwen2.5-7B-Instruct AWQ: `b25037...d641` (resolve full revision from archived authority; do not guess)
- Qwen3-8B: `b96882...1218` (resolve full revision from archived authority; do not guess)
- DeepSeek-V2-Lite: `604d56...2de0` (resolve full revision from archived authority; do not guess)

Do not create new Qwen3/DeepSeek frozen input bindings in this goal.

## Existing input authority

Preserve these semantics:

- Qwen historical inputs: 21 exact bindings = 3 Qwen2.5 model variants × 7 scenarios, hash-closed.
- Llama adopted S0 input is future-use adopted authority, not reconstructed historical R5 authority.
- Qwen3-8B and DeepSeek-V2-Lite: `NO_HISTORICAL_FROZEN_BINDING`.

No retokenization in V6.

## Qwen2.5-7B raw status

Full-resident RTX4080 status remains:

`NOT_ADMITTED_MEMORY_CONFIRMED_16GB`

Do not reinterpret or overwrite this.

Separately, prepare for a future:

`SEMANTICALLY_EXACT_LAYER_REPLAY`

route inspired by the Qwen3-30B layer-streaming plan. V6 prepares metadata and loaders only; it does not execute model layers or claim replay equivalence.

Reference planning document:

`docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/QWEN3_30B_A3B_4080_TRACE_PLAN_V1.md`

## AutoAWQ source state

174-new has already acquired and frozen AutoAWQ kernels source on node164.

Reported archive SHA256:

`49304506a87ef74c3a3dd07ddc839d796c25432d2cdd721e1b968977fa78f398`

Use the canonical source receipt on node164 as authority; verify the reported archive SHA against the receipt. Do not fetch a second copy merely for convenience.

## Non-negotiable guardrails

This goal is CPU-only and low-I/O.

Do not:

- run GPU workloads;
- retokenize any frozen input;
- mutate formal raw capture data;
- move/delete canonical model assets;
- bulk-rehash tens of GB when a valid archive receipt already closes the payload;
- create Qwen3/DeepSeek prospective bindings;
- start simulator/TLB/cache inheritance work;
- change Pipeline paths while node109 V5 may still be writing/ACKing data;
- claim layer-replay scientific validity before a future semantic/equivalence qualification stage.

If a valid archive receipt already proves exact relative path/size/SHA closure, verify the receipt and spot-check structure instead of re-reading every model byte.
