# AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1

Final status: **AI_RESOURCE_MAP_COMPLETE_NO_ACTIONABLE_PROBLEM**

## Scope and execution

The stage used only qualified traces and the frozen WARP_VPN_DEDUP_REFERENCE.
Seven non-control targets received at most two preregistered 2x diagnostics and
one deterministically selected upper bound. M2 remained control-only.

New execution comprised one missing SPLITKV Level-1 baseline, eleven valid 2x
runs, one retained pre-result source-coupling abort, and seven upper-bound runs.
Two SFU runs were skipped after the same source coupling was established. No
parameter sweep, new capture, target replacement, simulator platform change,
or prototype was performed.

Every completed scientific run conserved instructions and CTA count and passed
translated coverage, untranslated/unobserved zero, duplicate-application zero,
terminal, and controller/reference quiescence gates.

## Bounded responses

| target | selected 2x | baseline -> 2x | upper | baseline -> upper | interpretation |
|---|---:|---:|---:|---:|---|
| T0 | L1 latency 32 -> 16 | 488,559 -> 448,768 (+8.145%) | latency 1: 463,760 | +5.076% | non-monotonic |
| T1 | L2 sets 2048 -> 4096 | 619,514 -> 619,514 (0%) | 8192: 619,514 | 0% | low response |
| T2 | L1 MSHR 384 -> 768 | 94,034 -> 91,362 (+2.842%) | 1536: 91,362 | +2.842% | finite, diminishing; pressure migrates |
| SPLITKV | L2 MSHR 192 -> 384 | 72,817 -> 72,372 (+0.611%) | 768: 72,372 | +0.611% | low cycle response after large reservation relief |
| L2 | L2 MSHR 192 -> 384 | 28,335 -> 28,353 (-0.064%) | 768: 28,353 | -0.064% | reservation pressure not cycle critical |
| L1 | DRAM data ratio 4 -> 2 | 320,808 -> 296,316 (+7.634%) | ratio 1: 305,651 | +4.725% | finite but non-monotonic |
| M1 | L1 MSHR 384 -> 768 | 57,107 -> 55,867 (+2.171%) | 1536: 55,867 | +2.171% | finite, diminishing |

The non-selected 2x controls are retained. Notably, SPLITKV DRAM 2x regressed
5.828%; L1 MSHR 2x improved 7.415%; M1 DRAM 2x improved 1.905%; and T2 DRAM 2x
improved 1.295%. These are simulator causal contrasts, not predicted hardware
speedups.

## Main findings

1. There is no single stable limiting resource across the suite. Prefill Flash,
   prefill GEMM, decode GEMV, and attention respond differently.
2. Reservation-failure magnitude is a location signal, not sufficient proof of
   cycle criticality. SPLITKV and especially L2 remove most L2 reservation
   failures with little or no performance gain.
3. The exact-function L1/M1 pair has identical per-CTA architectural work but
   different resource response: L1 gains 7.415% from L1-MSHR 2x versus 2.171%
   on M1, and 7.634% versus 1.905% from DRAM 2x. Aggregate execution scale
   changes the modeled balance; this is not a model-family claim.
4. T0 latency and L1 DRAM upper bounds are non-monotonic. The stronger modeled
   resource is not automatically faster, so these results cannot justify a
   simple capacity-scaling mechanism.
5. T1 L2 capacity is exactly insensitive at both bounded points. Its large
   eligible-structural signal remains unresolved because the accepted
   Observatory cannot attribute a ready-but-not-issued instruction to a single
   functional unit.

## Research gate

The strongest remaining observation is the scale-dependent L1 reservation /
DRAM balance in exact GEMV implementations. It is finite and has online
signals, but cache-aware warp throttling, MSHR/congestion-aware cache bypass,
and pressure-aware scheduling already cover this generic problem space. The
current evidence does not establish a distinct AI-specific interaction.

The non-monotonic memory-service response is not a second problem candidate:
the DRAM diagnostic intentionally changes derived turnaround terms together
with its data-service ratio, and the response does not isolate a new online
control objective.

Therefore no architecture problem card passes all gates and candidate/control
runs equal zero.

## Limitations

- Resource changes are Accel-Sim model interventions, not claims about physical
  RTX4080 configurability, area, timing, or realizable bandwidth.
- `eligible_structural` lacks per-FU denial provenance, and scoreboard stalls
  lack producer-domain provenance.
- The local-xbar source has no clean bandwidth knob; no ICNT scaling result is
  claimed.
- Scenario runtimes are not cross-model comparable and are never averaged.
- One specialized-unit point exposed an issue-width coupling before a complete
  result. It is retained as invalid engineering evidence, not performance.
