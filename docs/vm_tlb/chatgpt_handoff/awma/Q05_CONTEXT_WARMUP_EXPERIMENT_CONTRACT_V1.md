# AWMA Q05 Context-Warmup Experiment Contract V1

Date: 2026-09-17
Ownership: ChatGPT
Status: ACTIVE MAINLINE CONTRACT

## 1. Mainline question

The accepted Q05 simulator-native trace is a complete whole-kernel trace, but current R0/I0/P2/M8 and translation-timeline results begin from the simulator's isolated selected-kernel initial state.

The next scientific question is:

> How much of the observed Q05 translation/cache behavior is intrinsic to Q05, and how much is caused by losing the hardware state created by the real predecessor kernels in the frozen full-model execution?

This is an initial-state/context question, not a new TLB/PTW mechanism experiment.

## 2. Frozen workload and target

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
input      = frozen TEXT binding
prefill    = 2048 tokens
decode     = 32 tokens
dtype      = FP16
backend    = SDPA

target     = Q05_PREFILL_ATTN_FLASH
function occurrence = 0
kernel     = pytorch_flash::flash_fwd_kernel<...>
```

The existing isolated Q05 SIM_INPUT and all accepted IDs remain read-only.

## 3. Evidence boundary

The current isolated result means:

> Q05 is highly sensitive to the modeled translation path when replayed as the selected kernel under the current isolated initial-state contract.

It does NOT yet mean:

> the same cold/walk behavior occurs when Q05 executes at its real position in the full model.

A page that is first-touched by the isolated Q05 replay may already have been translated or cached by an earlier kernel in the native program. Conversely, earlier kernels may also evict useful state or create contention.

Do not use `cold` or `warm` without saying which scope is meant:

```text
ISOLATED_Q05_FIRST_TOUCH
FULL_APPLICATION_FIRST_TOUCH
PREFIX_WARMED_Q05
SELF_WARM_DIAGNOSTIC
```

## 4. State dimensions to audit

At minimum distinguish:

```text
L1 data-cache state
L2 data-cache state
L1 TLB state
L2 TLB state
PWC / page-walk intermediate state
translation MSHR / PWQ / active-walk state
memory-system outstanding traffic
replacement/recency metadata
```

Do not assume these all persist across CUDA-kernel boundaries on hardware or in the simulator.

For every component report one of:

```text
PERSISTS_BY_SOURCE
RESET_BY_SOURCE
DRAINED_BUT_METADATA_PERSISTS
NOT_MODELED
UNKNOWN
```

Hardware behavior and simulator behavior must be documented separately.

## 5. Real-GPU evidence is context evidence, not simulator state

Node109 may determine:

- exact predecessor launch sequence;
- same-run page-set overlap;
- page last-touch distance;
- normal-context Q05 timing;
- data-cache-sensitive hardware counter differences when a supported profiling mode can measure them.

These observations may show that predecessor state matters, but they do NOT by themselves specify the exact simulator TLB/PWC/cache contents at Q05 entry.

In particular:

- page overlap != TLB hit;
- prior access != guaranteed residency;
- NCU cache-control behavior must not be described as a TLB flush unless tool documentation/source proves it;
- structural trace-file order must not be used as a global GPU-time order.

## 6. Same-run address identity rule

Any future predecessor context used for address-level warmup must belong to one scientifically closed execution context.

Do not stitch arbitrary predecessor traces from one process/run to the historical Q05 trace from another process solely by absolute virtual address.

A future context bundle must close, at minimum:

```text
frozen workload/input/model revision
same address-context contract
ordered kernel sequence
phase
exact kernel functions
occurrences
CUDA context/ASID policy
trace member identities
```

If exact same-run address identity cannot be proven, the result is structural context evidence only and cannot be used as a faithful warm-state replay.

## 7. Continuous-prefix rule

A realistic predecessor warmup must use a CONTIGUOUS predecessor prefix/suffix in program order.

It is not valid to keep only predecessor kernels that overlap Q05 pages while dropping intervening kernels, because those intervening kernels may evict or perturb state.

Page-overlap analysis may be used to choose how long the continuous prefix should be, but not to selectively skip interior kernels.

## 8. Measurement boundary rule

For a future prefix+Q05 simulation:

```text
run predecessor prefix normally
-> retain the modeled state that is supposed to persist
-> mark Q05 measurement boundary
-> measure Q05 only
```

Do not call a simulator reset routine at Q05 entry unless source audit proves that it resets counters only and preserves all intended warm state.

Preferred accounting is counter snapshot/delta across Q05 when possible.

The warmup work may be excluded from the reported Q05-only timing metric, but it cannot be presented as free end-to-end performance.

## 9. Self-warm is plumbing only

Running:

```text
Q05 -> Q05
```

may be used on 174-new as a diagnostic to prove state persistence and measurement-boundary plumbing.

It is NOT evidence of the real predecessor context and must be labeled:

`SELF_WARM_DIAGNOSTIC_ONLY`.

## 10. Prefix selection study

Node109 should build nested continuous predecessor windows ending immediately before Q05, based on the exact frozen application execution.

Preferred candidate windows when available:

```text
P1    = immediate predecessor only
P2    = last 2 predecessor kernels
P4    = last 4
P8    = last 8
P16   = last 16
PFULL = all kernels from the relevant Prefill region start to Q05
```

Deduplicate windows if Q05 occurs too early.

For each prefix compute, without claiming residency:

```text
fraction of Q05 64KiB pages touched by prefix
fraction of Q05 4KiB pages touched by prefix when available
closest prior-touch kernel for each Q05 page
kernel-distance since prior touch
unique-page activity between prior touch and Q05
```

The final prefix set for expensive simulator-native predecessor capture will be chosen only after both node109 and node174-new reports are reviewed.

## 11. Current mainline stage scope

This V1 stage is methodology + real-context characterization.

Authorized:

- bounded real-GPU context observation around Q05;
- lightweight same-run memory/page observer if required;
- targeted NCU only for context/data-cache sensitivity and only with explicit semantic caveats;
- simulator source audit;
- diagnostic multi-kernel/self-warm feasibility tests;
- timing-neutral diagnostic state/counter observation with neutrality checks.

Not authorized yet:

- full predecessor simulator-native capture campaign;
- new SIM_INPUT admission for predecessor prefixes;
- warm-prefix scientific Q05 simulation claiming real context;
- L2-TLB latency/PTW/walker/capacity/page-size/Segment experiments;
- any new TLB/cache mechanism.

## 12. Mainline priority

This stage has priority over all side work.

Node109 may start a side task only when the active mainline specification explicitly does not need the RTX4080 and the side task can release the GPU immediately at a safe checkpoint.

A side task may never make the mainline wait.
