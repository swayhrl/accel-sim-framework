# AWMA Q05 Contiguous Prefix Capture and Warm Replay Contract V1

Date: 2026-09-18

Stage:

`AWMA_Q05_CONTIGUOUS_PREFIX_WARM_REPLAY_V1`

## Scientific question

Determine how much the accepted isolated-Q05 translation/cache behavior changes when Q05 is executed after its real contiguous Prefill predecessors from the same frozen model run.

This stage studies **initial-state/context sensitivity**. It does not authorize any new TLB/PTW/cache mechanism.

## Frozen workload and target

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
target     = Q05_PREFILL_ATTN_FLASH
Q05 occurrence = 0
```

The existing isolated-Q05 SIM_INPUT/SIM_BASELINE/SIM_RUN/SIM_EVIDENCE identities remain read-only.

## Accepted parent evidence

109 native-context characterization:

```text
hrl/awma-q05-native-context-109-v1
64a2e51943a6737b84132bc7daa5f4d7c74f8099
```

It closes the exact predecessor sequence: Q05 is Prefill launch 34 and has exactly 34 contiguous Prefill predecessor launches, positions -34..-1. The authoritative sequence table is:

`docs/vm_tlb/review_packs/AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1/Q05_PREDECESSOR_SEQUENCE.tsv`

The previous lightweight same-process page observer is rejected and MUST NOT be treated as science.

174-new warm-replay feasibility:

```text
hrl/awma-q05-warm-replay-feasibility-174new-v1
e2fa35f045e0b4f977a964d9c92974c9f6d3e240
```

It proves same-simulator-instance sequential dispatch can preserve translation state and target-only statistics can be obtained by before/after counter deltas without resetting at Q05 entry.

Self-warm remains diagnostic only:

```text
Q05 #1 = 885681 cycles
Q05 #2 = 821426 cycles
Q05 #2 L2 TLB = 2922 access / 2922 hit / 0 miss
Q05 #2 adds zero walks and zero translation-MSHR merges
```

This proves modeled warm-state persistence. It does **not** prove real predecessor behavior and the cycle reduction MUST NOT be attributed solely to translation because data-cache state may also persist.

Accepted simulator-native producer authority remains:

`5143b4e10aaf2fc47bb60492155d2464b0b726fd`

## Main methodological pivot

Do NOT spend another mainline stage repairing the rejected lightweight page observer.

Because the true Q05 prefix contains only 34 predecessor launches and the eventual simulator experiment requires full predecessor traces anyway, node109 shall capture one bounded **same-run contiguous simulator-native context bundle** containing launches 0..34.

Page-overlap analysis is then derived offline from that complete context bundle. No second lightweight observer is needed.

## Context-bundle identity

A formal bundle is:

```text
one frozen model/input/runtime execution
one CUDA context
ordered members 0..34
members 0..33 = all real contiguous Q05 predecessors
member 34      = exact Q05
no missing interior member
per-member exact kernel function + grid/block
sequence matches the accepted predecessor table
per-member terminal closure and grammar validation
same-run address context
```

Global launch numbers are navigation aids inside this exact frozen run. Scientific identity is the frozen workload plus the exact ordered per-member function/shape sequence.

Independent-process traces MUST NOT be concatenated into this context bundle.

## Prefix rows

After admission, warm replay rows are suffixes of the real predecessor sequence:

```text
ISOLATED_Q05
P1  = launch 33 + Q05
P2  = launches 32..33 + Q05
P4  = launches 30..33 + Q05
P8  = launches 26..33 + Q05
P16 = launches 18..33 + Q05
P34 = launches 0..33  + Q05
```

Each row starts from a fresh simulator process/state. State is preserved only within that row across its predecessor kernels into Q05.

## Native page-overlap analysis

From the same-run simulator-native members, compute page sets using the same address extraction scope for every member.

Report separately at least:

```text
4 KiB page identity
64 KiB page identity
```

For each P1/P2/P4/P8/P16/P34 report:

- predecessor-union page count;
- Q05 page count;
- intersection count;
- Q05 page coverage by predecessor union;
- for each Q05 page, nearest preceding kernel position when observable.

These are trace-address overlap metrics, not hardware-TLB residency claims.

Do not force-join native/offline VPN identity to simulator translation keys. Simulator translation key remains `{asid,vpn,page_size}`.

## Simulator measurement boundary

Within each warm-prefix row:

```text
fresh simulator
-> run predecessor suffix normally
-> snapshot monotonic counters immediately before Q05
-> run Q05 without reset
-> snapshot immediately after Q05
-> Q05 metric = after - before
```

No call at Q05 entry may flush/reset TLB, PWC, cache, walker, replacement or queue state.

Use accepted F0 semantics unchanged.

## Required Q05 metrics

For every replay row, report Q05-only deltas for at least:

- cycles;
- completed active thread-instructions;
- issued/completed CTA as source-supported;
- L1 TLB access/hit/miss;
- L2 TLB access/hit/miss;
- translation MSHR alloc/merge/full/high-water;
- walk start/complete;
- PWC access/hit/miss;
- PTE request/response and L2-only/DRAM split;
- requester-latency decomposition;
- L2 data-cache and DRAM traffic/hit metrics where the accepted simulator exposes units unambiguously.

Where source-safe, also classify the first Q05 translation outcome per simulator translation key. A read-only diagnostic path is allowed only if disabled by default and neutrality-gated.

## State-semantics closure before interpretation

174-new must explicitly close, for the actual F0 configuration:

- L1 data-cache kernel-boundary behavior;
- L2 data-cache kernel-boundary behavior;
- L1 TLB behavior;
- L2 TLB behavior;
- PWC behavior;
- translation MSHR/PWQ/walker drain behavior.

Do not merge L1/L2 TLB into one unsupported statement.

Any Q05 cycle change under warm prefix is initially a **combined modeled context effect** unless translation and data-cache contributions are separately supported by counters/controlled evidence.

## 109 capture engineering contract

Extend the accepted Route-B producer minimally for contiguous multi-kernel capture.

Required properties:

- one CUDA context/channel/receiver lifecycle across the whole selected prefix;
- no receiver/channel teardown between members;
- each selected member flushes/drains and atomically closes its own trace sink;
- writer state can re-arm for the next selected member;
- global final terminal only after member 34/Q05 closes;
- default one-target producer behavior remains regression-compatible;
- raw formatter/trace grammar is unchanged unless a separate scientific review authorizes a fix.

Before formal P34 capture:

1. one-target Q05 regression;
2. two-member same-run canary using launches 33..34;
3. only then full launches 0..34.

If any interior member fails grammar/terminal/identity closure, the bundle is incomplete and MUST NOT be admitted by skipping that member.

## Resource bounds

Formal full-prefix capture is bounded by:

```text
16 GiB compressed bundle guard
45 minute capture guard
35 selected members exactly
```

If a guard fires, retain diagnostic receipts only and STOP for review. Do not publish a partial bundle as formal.

## Durable storage

node164 remains authoritative for large context data.

A formal context bundle must be hash-closed and published through the already-qualified producer->node164 verify/admit/ACK path.

Git stores only source, manifests, summaries and review evidence.

## Claim boundaries

Allowed:

- same-run trace-page overlap;
- modeled warm-prefix Q05 behavior under accepted simulator semantics;
- how Q05 translation counters change as real predecessor suffix length increases;
- whether isolated Q05 materially differs from contextual replay, stated quantitatively.

Not allowed from this stage alone:

- claiming RTX4080 hardware TLB persistence equals simulator persistence;
- calling trace page overlap a TLB hit rate;
- attributing self-warm or warm-prefix cycle changes solely to translation without supporting decomposition;
- new TLB/PTW/cache mechanism speedup claims;
- stitching independent-run absolute addresses.

## Global STOP conditions

STOP for review on:

- ordered sequence mismatch;
- different CUDA contexts/address spaces inside the formal bundle;
- missing interior predecessor;
- terminal/drop/overflow failure;
- unsupported trace grammar in any member;
- need to weaken existing trace semantics;
- need to change accepted F0 reset/flush behavior;
- guard-triggered partial capture;
- inability to preserve same-instance warm state during replay.

Routine build, wrapper, indexing, hash, storage and diagnostic-counter plumbing is solve-and-continue.
