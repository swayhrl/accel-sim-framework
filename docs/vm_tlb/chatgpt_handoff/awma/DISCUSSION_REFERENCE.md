# AWMA Discussion Reference — Q05 Context Warmup Sensitivity V1

Date: 2026-09-17

## 1. Why the next mainline is initial-state/context sensitivity

The project has already proven that the complete selected Q05 FlashAttention kernel is highly sensitive to the modeled translation path when replayed in isolation.

That result is useful, but it leaves one important realism question open:

> In the original frozen full-model run, predecessor kernels may have already touched some of the same virtual pages or related page-table prefixes before Q05 begins. If Q05 is replayed alone, those predecessor-created TLB/PWC/data-cache states are lost.

Therefore the current isolated R0/I0 gap may combine:

```text
intrinsic Q05 translation demand
+
selected-kernel initial-state effect
```

Before proposing a TLB/PTW mechanism, these effects must be separated.

This stage therefore studies context/warmup methodology, not a mechanism.

## 2. What the previous Q05 timeline established

The timeline stage preserved the accepted R0 10k result and exposed the real simulator translation key:

`{asid, vpn, page_size}`

Observed:

```text
10k:  19 keys / 19 fills / 106 merges
50k: 104 keys / 104 fills / 374 merges
full: 240 keys / 240 fills / 393 merges
```

This pattern is important:

- strong same-key fanout is front-loaded;
- approximately 95% of merge events have occurred by 50k;
- but only about 43% of final translation keys have appeared by 50k;
- new translation demand therefore continues after the strongest fanout phase.

So the current behavior is neither a simple one-time cold front nor a pure capacity-thrashing story.

However, `first seen in isolated Q05` is not equivalent to `first touched in the full application`.

A Q05 page that appears late in the isolated kernel may still have been touched by an earlier native kernel before Q05 starts.

## 3. Why predecessor page overlap is useful but not sufficient

Node109 will measure predecessor/Q05 address overlap in one exact frozen native execution.

If a Q05 page was touched earlier, that establishes a warm-state opportunity.

It does NOT prove:

- that the translation still resides in the hardware TLB;
- that a data-cache line is still resident;
- that the same SM holds the private state;
- that a prior page-table walk leaves the same intermediate state in the real GPU;
- that the simulator should be initialized by simply preloading that translation.

Intervening kernels can evict or perturb state.

Therefore the native study reports `PREDECESSOR_PAGE_OVERLAP_OPPORTUNITY`, not a measured TLB hit rate.

## 4. Why the predecessor sequence must stay contiguous

Suppose the real program order is:

```text
producer A
-> large unrelated kernel
-> producer B
-> Q05
```

If a warmup replay keeps only A and B because they overlap Q05 pages, it creates an unrealistically favorable initial state by omitting the unrelated kernel that may evict cache/TLB entries.

Thus future warmup uses continuous predecessor windows ending immediately before Q05.

Page overlap helps decide how long the continuous prefix should be; it does not justify skipping interior launches.

## 5. Same-run address identity is mandatory

The historical Q05 trace and a new predecessor trace cannot be concatenated purely because their absolute virtual addresses look similar if they come from independent processes/runs.

Allocator state, CUDA context and object placement may differ.

A future scientifically faithful context bundle must close a same-run or formally remapped address identity across the ordered predecessor sequence and Q05.

The current V1 stage therefore stops before expensive predecessor simulator-native capture. First it determines:

1. the real native predecessor sequence/page overlap;
2. the simulator's kernel-boundary state semantics;
3. the exact address/context contract needed by the next capture stage.

## 6. Why node109 and node174-new run in parallel

### node109

Answers the native-program question:

> What actually executes before Q05, and which Q05 pages were touched before Q05 in the same frozen run?

It may use a lightweight Native/memory-only observer because page-set context does not require a full instruction trace.

The observer must retain per-kernel identity and same-run addresses.

### node174-new

Answers the simulation-method question:

> If multiple kernels are replayed sequentially, what simulator state persists, what resets, and how can Q05 statistics be measured without clearing the state being studied?

This requires source audit before any warmup experiment.

## 7. Kernel-boundary state is component-specific

Do not use a generic phrase such as `the cache is warm`.

The next 174 audit separates:

```text
L1 data cache
shared L2 data cache
L1 TLB
L2 TLB
PWC
translation MSHR/PWQ/walkers
memory queues/interconnect
replacement metadata
```

A component may:

- persist;
- be reset;
- drain outstanding requests but preserve resident metadata;
- not be modeled;
- remain unknown.

Simulator behavior must be derived from source, not assumed from GPU intuition.

Hardware behavior and simulator behavior are also separate claims.

## 8. Why statistics must use snapshots/deltas

A common warmup methodology is conceptually:

```text
run warmup/prefix
-> preserve state
-> start measurement
-> run target
-> stop measurement
```

The dangerous step is `start measurement`.

An existing simulator `init()` or stats-reset routine may reset more than counters. If called at Q05 entry it could destroy the warm state we wanted to study.

Therefore node174 first audits all initialization/reset code and prefers counter snapshots/deltas around Q05.

If a new diagnostic snapshot path is needed, it must be disabled by default and timing/functionality neutral.

## 9. Why self-warm Q05->Q05 is allowed only as plumbing

A two-kernel diagnostic:

```text
Q05 #1 -> Q05 #2
```

is useful to test:

- whether state persists across a kernel boundary;
- whether target-only deltas can be measured;
- whether a framework reset accidentally clears TLB/cache state.

But it is not a model-context experiment.

The real predecessor kernels have different memory behavior and can both prewarm and evict Q05 state.

Therefore all such outputs must be labeled:

`SELF_WARM_DIAGNOSTIC_ONLY`.

## 10. Native timing and NCU role

Node109 should establish normal-context Q05 timing stability across repeated exact full-application runs.

A targeted NCU comparison may be used only as a secondary data-cache sensitivity check when the installed tool can reliably target Q05.

Important boundary:

- profiler cache-control settings concern the documented profiler/cache handling;
- they must not be described as a proven TLB flush/preserve operation without explicit evidence;
- failure to obtain a clean NCU comparison does not block the main page-overlap study.

The core native evidence remains same-run predecessor page overlap plus exact launch order.

## 11. Prefix candidates

The native track will compute nested continuous prefixes ending immediately before Q05:

```text
P1, P2, P4, P8, P16, P32 when available, PFULL
```

For each it will report the fraction of Q05 pages that had any prior touch.

The final expensive simulator prefix set will be smaller, normally no more than four conditions such as:

```text
ISOLATED_Q05
SHORT_PREFIX
MEDIUM_PREFIX
FULL_AVAILABLE_PREFIX
```

But these final boundaries are chosen only after seeing the actual native overlap curve and simulator feasibility report.

## 12. Carry-forward 240 vs 228 issue

Previous evidence contains:

```text
228 unique offline 64KiB VPN
240 simulator translation keys
```

This mismatch cannot be ignored when joining native page sets to simulator translation behavior.

Node174 must reconcile or safely classify the difference before the next scientific warm-prefix replay.

Possible causes must be demonstrated from source/evidence, not guessed.

## 13. Mainline priority

The current M1/M2 stage has priority over side work.

While node109 is performing Q05 native context characterization, do not start:

- LDC.U8 grammar repair;
- Qwen3/DeepSeek campaigns;
- unrelated NCU work;
- additional selected-kernel capture;
- cleanup tasks.

Side work resumes only when the mainline explicitly releases the resource.

## 14. Decision after this V1 stage

After both reports return, ChatGPT should decide:

1. which continuous predecessor windows are scientifically useful;
2. whether the current simulator can preserve the intended state without semantic changes;
3. what same-run simulator-native context bundle must be captured;
4. whether real prefix+Q05 replay is ready or blocked by kernel-boundary/address-context semantics.

Only after that should the project capture predecessor simulator-native traces and run the first warm-context Q05 comparison.

No TLB/PTW mechanism sweep begins in this V1 stage.
