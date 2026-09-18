# AWMA Discussion Reference — Contiguous Prefix Warm Replay

Date: 2026-09-18

## 1. What changed after the first context-warmup stage

The isolated Q05 study is no longer the only evidence about initial state.

174-new has now proved a methodological fact inside the accepted simulator: sequential dispatch in one simulator instance can retain translation state across kernels while Q05-only counters are measured by deltas.

The self-warm diagnostic produced:

```text
first Q05  = 885,681 cycles
second Q05 = 821,426 cycles

second-Q05 L2 TLB:
2,922 accesses
2,922 hits
0 misses

new walks  = 0
new merges = 0
```

Therefore an isolated-kernel start state can materially differ from a warm sequential state in the simulator.

This self-warm result is not a model-context result. Running Q05 twice gives Q05 an artificially favorable copy of its own working set.

Also, the cycle reduction cannot be labeled a translation-only gain because F0 kernel boundaries may preserve state outside the translation hierarchy, especially shared L2 data-cache state. The next stage separates those counters.

## 2. What node109 established despite the observer stop

The native-context stage did not produce valid page sets, but it did close a highly useful structural fact:

Q05 is the first Prefill FlashAttention target at navigation launch 34 and has exactly 34 contiguous Prefill predecessor launches.

The accepted sequence is fully enumerated in:

`Q05_PREDECESSOR_SEQUENCE.tsv`

This changes the cost/benefit tradeoff.

The original plan used a lightweight page observer to choose how far back to trace. But the full prefix is only 34 launches. A formal context replay ultimately needs complete instruction/memory traces for those predecessor kernels anyway.

Therefore repairing a second, lightweight observer first would duplicate work.

## 3. Why the next capture is the complete same-run prefix

The scientifically clean input is:

```text
launch0
launch1
...
launch33
Q05 launch34
```

all from one frozen workload execution and one CUDA context.

That single capture provides simultaneously:

- the exact real predecessor ordering;
- same-run absolute address identity;
- per-kernel full simulator-native replay input;
- offline 4KiB/64KiB page sets;
- page-overlap curves for P1/P2/P4/P8/P16/P34;
- the data needed for actual contextual replay.

No independent-run trace stitching is needed.

## 4. Why a suffix-prefix matrix is used

The relevant history for Q05 is the continuous suffix immediately before it.

Rows are:

```text
P1  = only the immediate predecessor
P2  = last 2 predecessors
P4  = last 4
P8  = last 8
P16 = last 16
P34 = all 34
```

Interior kernels are never skipped.

This lets us ask whether Q05's initial state converges with a short recent history or depends on the full Prefill setup.

## 5. Two different overlap domains must remain separate

Native/trace page overlap uses addresses grouped into 4KiB or 64KiB pages.

Simulator translation identity is:

`{asid, vpn, page_size}`

The historical 228 offline 64KiB VPN versus 240 simulator-key mismatch is not forcibly reconciled.

The next stage uses page overlap as an opportunity/trend measure and simulator first-touch outcomes/walk counts as the actual modeled translation evidence.

## 6. What warm replay will and will not tell us

Warm-prefix replay can answer:

- whether the isolated Q05 replay overstates walk/miss demand;
- how quickly real predecessor history warms translation state;
- how much Q05 total modeled execution changes;
- whether a short contiguous prefix is enough for future Q05 studies.

It cannot by itself prove that RTX4080 hardware preserves exactly the same TLB/PWC/cache state across kernels as the simulator.

That hardware question remains separate.

## 7. Why F0 state semantics need a V1.1 closure

The feasibility pack compressed several components too aggressively.

Before interpreting real warm-prefix cycles, 174-new must state separately:

```text
L1 data cache
L2 data cache
L1 TLB
L2 TLB
PWC
translation in-flight state
```

For each, report whether the actual F0 configuration resets, flushes, drains, or preserves it.

In particular:

- F0 L1 data-cache flushing is already observed as enabled;
- L2 data-cache behavior must be closed for the actual config, not left merely CONFIG_DEPENDENT;
- L1 and L2 TLB persistence must not be merged into one unsupported row.

## 8. How the producer is extended safely

The accepted Route-B producer currently assumes one selected kernel.

Its trusted lifecycle already has the pieces we want:

```text
one per-context channel
one receiver thread
selected kernel executes
flush channel
receiver drains
raw sink closes atomically
```

The multi-kernel extension should keep the context/channel/receiver alive and re-arm only the per-member writer/counters after each member closes.

It must not destroy/recreate the channel inside callback teardown.

The record formatter and grammar stay unchanged.

Default one-target behavior must pass regression before formal prefix capture.

## 9. Interpretation after warm-prefix results

If longer prefixes remove most Q05 walks and materially change cycles, isolated-Q05 mechanism studies may need a contextual baseline.

If translation counters remain similar despite real predecessor history, the isolated result becomes much stronger.

If cycles change but translation counters do not, data-cache/context effects become the more likely explanation.

If both move, the result is mixed and any later translation-specific mechanism must be evaluated under the accepted contextual baseline.

No mechanism starts automatically from any of these outcomes.
