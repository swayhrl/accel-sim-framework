# AWMA Round17 unattended preparation window

Date: 2026-09-30
Window: six hourly preparation passes beginning 18:00 Asia/Singapore.

Scientific parent:
- Round16 final closeout: `31d585dc44f90eb70f83603c8b87a2d06efff01a`
- Round17 literature/preparation authority: `5ff0287ce45c3909d53ac44975f6fa488664b085`

## Purpose

Advance problem discovery and preparation without waiting for per-round user review.

Primary candidate at window start:
- GPU-resident graph vector search: low-concurrency online traversal after mature CAGRA/Jasper-class software.

The six passes may merge literature/source/input/preparation rounds when useful. If the primary candidate is closed by strong existing capability, missing scientific input, or lack of a concrete residual question, continue screening other literature-driven candidates with real AI/datacenter workload grounding.

## Allowed unattended work

- read/update literature notes and problem cards;
- inspect public source code, APIs, artifacts and dataset metadata;
- prepare capability matrices, input authority receipts and experiment contracts;
- create or update handoff-preparation documents;
- fix ordinary documentation/source-analysis engineering issues;
- commit/push/fetch-back verify remote state.

## Hard unattended boundary

Do NOT:
- run formal CUDA/NSYS/NCU jobs on node109;
- acquire the GPU campaign lock for a scientific experiment;
- run 174/Accel-Sim/NVBit/SASS capture;
- download large model/dataset payloads merely to keep the lane active;
- substitute synthetic payload for missing scientific input;
- change an accepted scientific contract;
- claim a new architecture mechanism or begin hardware design.

These require user review after the unattended window.

## Method

For each candidate:

```
real workload / public input authority
-> closest existing capability
-> bounded question not already answered by that capability
-> minimal measurement contract
-> explicit stop conditions
```

Do not create a candidate only because a count/traffic/state metric appears large.
Do not require a universal 5% proof before all characterization; use quantitative screens only when the candidate reaches an investment decision.

## Persistence

This branch is the coordination surface for the unattended window:

`hrl/awma-round17-unattended-prep-v1`

Every pass should first read:
1. this file;
2. the current branch HEAD;
3. Round17 literature notes/problem card;
4. any new unattended status files created by prior passes.

Each pass should leave a short timestamped status file under:
`docs/vm_tlb/chatgpt_handoff/awma/round17_unattended_prep_v1/status/`

A status file records:
- sources/capabilities newly verified;
- candidate state changes;
- files/commits added;
- what remains for the next pass;
- whether any boundary requiring user approval has been reached.

Do not create empty progress commits if nothing substantive changed.

## Initial execution state

- Lane E / 174-new: STOP
- Lane F / 109: STOP
- Lane G / 109: STOP
- R102: dormant pending real update authority
- VLA/VJP: workload real, architecture residual not qualified
- exact-loss zero-init: software-removable, current hardware line closed
- no authorized simulator/hardware follow-up
