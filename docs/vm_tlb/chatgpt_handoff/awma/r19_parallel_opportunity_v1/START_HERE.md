# START HERE — AWMA R19 parallel opportunity push

Date: 2026-10-01

Purpose: run three complementary lanes in parallel without duplicating one scientific question.

## Lane map

- **Lane F / node109 / RTX4080** — real Ada FP8 representation-readiness boundary using Transformer Engine.
- **Lane G / node109 / RTX4080 conditional** — fast-weight / test-time-training real-artifact authority and, only if qualified, a bounded Native state-update boundary.
- **Lane E / node174-new CPU/source only** — IBP lossless-compression consumer-boundary opportunity scout. No CUDA or simulator.

Lane F and G may do CPU/source/input work concurrently. They share one GPU and must serialize every CUDA/NSYS/NCU action through:

`/data/c16/locks/c16_gpu_campaign.lock`

Whichever lane first has a frozen, qualified GPU command gets the lock. The other lane continues CPU/source/report work or quiesces. Do not busy-poll.

Lane E never acquires the GPU lock and never starts Accel-Sim.

## Current authority

Literature/coordination parent:
`b915c64bab7e4b16bc5a03b969c66b150a877632`

Round18 erratum:
R53 was actually executed:
- branch `hrl/awma-r53-online-legal-workset-native-qualification-v1`
- commit `843ad43ad33153bf73a0e51aed6d8ac309356cae`
- final `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`

Therefore no lane may restart the old R53 legal-workset experiment.

## External pinned references

Lane F:
- NVIDIA Transformer Engine stable v2.19 / v2.19.0
- commit `5e52befd5262c06289106338c308079d6adb391f`
- Ada FP8 is a supported path; NVFP4/MXFP8 are not to be claimed as Ada performance evidence.

Lane G:
- TTT-NTP `yancyou/TTT-NTP@c11da918d9a5aebf3f3cb0f45a79c2e66d9ad79a`
- In-Place-TTT `ByteDance-Seed/In-Place-TTT@be2324829b0e91c8fd10a74d4b43714fde6676e1`
- public third-party In-Place-TTT HF artifacts may be inspected, but they are not silently upgraded to official-paper checkpoints.

Lane E:
- IBP `AKKamath/InvariantBitPacking@b2f71003113defb4e387caf18843b241f6280ba9`

## General rules

- ordinary engineering problems: solve and continue;
- scientific input/semantic/claim boundary change: stop at the lane's bounded classification;
- no lane creates a hardware mechanism automatically;
- no lane starts a fourth research topic because time remains;
- large durable assets/raw -> node164; node109 only active replicas;
- Git transport failure is not a scientific rerun reason.

## Execution branches

Lane F:
`hrl/awma-r19-fp8-readiness-109-v1`

Lane G:
`hrl/awma-r19-fastweight-authority-109-v1`

Lane E:
`hrl/awma-r19-ibp-consumer-scout-174new-v1`
