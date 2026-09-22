# Translation Frontend Pipelining Recalibration 174-new V1

Status: `COMPLETE_WITH_DIAGNOSTIC_CANDIDATE`

## Result

The opt-in `GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH` candidate completed all six V3R1 matrix points after a bounded READY-ownership liveness repair.

## Provenance

- Coordination authority: `hrl/awma-mainline-reset-crossview-v2 @ 9d093efec8d50775fd7298a4683cb0b7790a32d0`.
- Canonical T0 payload: `kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz`, grammar PASS, derived index SHA256 `a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5`.
- Legacy T0 10/80 exactly reproduced 1,654,548 cycles, 368,696,302 instructions and 224 CTA.
- Repair patch SHA256: `0a31011fbb955f2751019c577dd6ff37071755c080c47cfc231bbbdc7b3f5563`.

## Candidate matrix

| Target | Candidate 10/80 cycles | Candidate 0/80 cycles | Instructions | CTA |
| --- | ---: | ---: | ---: | ---: |
| T0 | 756,812 | 693,548 | 368,696,302 | 224 |
| T1 | 1,320,195 | 1,251,826 | 369,131,520 | 384 |
| T2 | 111,607 | 71,743 | 43,357,696 | 1,216 |

Every completed matrix point had terminal completion, full translated-unique coverage, zero untranslated/unobserved accesses, and zero Segment functional activity.

## Liveness repair

The first candidate consumed READY lookups during prelaunch before the corresponding accessq head could consume them, causing a deadlock. The repair makes prelaunch observe READY without consuming it; existing head admission remains the unique consumer.

## Decision

