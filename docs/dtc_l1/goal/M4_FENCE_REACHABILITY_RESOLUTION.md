# DTC-L1 M4 Fence Reachability Resolution

Status: **AUTHORIZED SPECIFICATION REFINEMENT — RESUME M4**

Purpose: resolve the M4 HARD stop caused by a verified limitation of the current PTX frontend, without inventing unsupported fence semantics and without weakening DTC correctness requirements for source-reachable operations.

## 1. Verified source limitation

The M4 audit established that the current source contains a dynamic `FENCE_OP` / async proxy-fence handling path in `ldst_unit`, but the PTX input frontend cannot construct such an instruction:

- `src/cuda-sim/ptx.l` has no `fence`/`fence.proxy` opcode rule and does not return `FENCE_OP`;
- `src/cuda-sim/ptx.y` has no `FENCE_OP` token/production/mapping;
- static PTX decode has no fence opcode case;
- no PTX-originating path calls `set_proxy_fence()` or `set_fence_proxy_kind()`;
- PTX `membar` is a distinct `MEMBAR_OP` and must not be substituted;
- the dynamic path explicitly rejects unsupported regular fences.

This limitation is documented in `implementation/M4_MEMORY_OP_SEMANTICS.md` and is independent of DTC Tag/physical/PIB semantics.

## 2. Scientific disposition

The original F01-F03 end-to-end PTX fence tests were project validation requirements added during M1-M4 planning. They are not executable on the frozen current source without implementing a new PTX parser/decode/semantic extension.

Implementing that frontend extension is **not required for the Chapter-4 DTC mechanism reproduction** and would expand the project into unrelated PTX-frontend work. Therefore:

- do **not** add `fence` lexer/parser/decode support in M4;
- do **not** map `membar` to proxy fence;
- do **not** synthesize regular-fence behavior;
- classify F01-F03 as `SOURCE_UNREACHABLE_NA` for the frozen source anchor, supported by the completed reachability audit;
- retain the source limitation explicitly in the M4 review pack and final project limitations.

This is a refinement of the validation boundary, not a change to the frozen DTC architecture.

## 3. Replacement HARD requirements

M4 fence/order acceptance is replaced by the following source-domain gates.

### F00A — Fence reachability audit — HARD

PASS when the review evidence proves the current PTX frontend cannot generate `FENCE_OP` / proxy-fence state and distinguishes `membar` from fence. The existing audit/evidence may be reused.

### F00B — No silent substitution — HARD

Source/diff review must show:

- no new lexer/parser/static-decode fence semantics were added;
- no `membar -> FENCE_OP` substitution was added;
- no forced proxy-fence bits were injected into ordinary instructions;
- regular-fence unsupported behavior was not silently bypassed.

### F00C — Current-domain fence accounting — HARD

For every accepted M4 workload triplet:

- source-reachable `FENCE_OP` count must be identical across Base/IO/OO;
- under the frozen source it is expected to be zero unless a future source-backed producer is discovered;
- if a workload/source path does produce a real `FENCE_OP`, STOP and reopen fence validation rather than ignoring it.

A PTX workload requiring unsupported `fence` syntax cannot count toward the accepted bring-up set.

### F00D — Existing dynamic proxy path preservation — HARD source review

The M4 source changes must not alter the existing `ldst_unit` proxy-fence handling path except for non-semantic observability that is demonstrably inactive for normal PTX workloads.

A synthetic direct-object test of the existing dynamic proxy-fence path is permitted as DIAGNOSTIC evidence if it can be implemented without modifying production semantics, but it is not required to claim end-to-end PTX fence support.

## 4. MIX01 refinement

For the frozen current source, `MIX01` must cover the source-reachable mixed sequence:

`Load / Store / Atomic / architectural-bypass`

and validate lifecycle, side effects, ordering already provided by the simulator, accounting, and drain behavior.

Fence is not silently replaced by `membar`. Record `Fence count = 0` for accepted current-source runs.

If a future source update makes proxy fence reachable from the input frontend, F01-F03 become active again before that updated source can be accepted for formal M4 results.

## 5. M4 continuation

Resume M4 from the existing checkpoint. Do not redo already-passed M2/M3 or M4 Store/Atomic/bypass evidence without a reason.

Required remaining work:

1. mark the fence reachability audit as `F00A PASS / F01-F03 SOURCE_UNREACHABLE_NA`;
2. satisfy F00B-F00D;
3. close W01-W04, A01-A04, BP01-BP02 and refined MIX01;
4. create/finalize `WORKLOAD_MANIFEST.md`;
5. run at least five provenance-resolved representative Chapter-4 compute workloads under PAPER_BASE/PAPER_IO/PAPER_OO;
6. require identical dynamic Load/Store/Atomic/FENCE_OP counts across each accepted triplet, with current-source FENCE_OP expected zero;
7. close all invariants, counters, parser outputs and repository hygiene;
8. create `review_packs/M4_COMPUTE_BRINGUP/` only after every active HARD gate passes.

If M4 passes under this refined frozen-source validation domain, set `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`, push, and STOP. M5 remains unauthorized.

## 6. Reporting requirement

The M4 review pack/final report must state clearly:

> The frozen GPGPU-Sim PTX frontend cannot generate the existing dynamic proxy-fence path. End-to-end F01-F03 were therefore not executable and were classified SOURCE_UNREACHABLE_NA after source audit. No fence semantics were invented or substituted. M4 correctness claims apply to the source-reachable Load/Store/Atomic/bypass domain used by the accepted workloads.
