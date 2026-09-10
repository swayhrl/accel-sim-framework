# DTC FAST64 Stage Handoff Schema

Status: **ACTIVE**

For FAST64.3 and FAST64.4, the prepared handoff files and detailed promotion/
acceptance rules in `FAST64_3_4_EXECUTION_CONTRACT.md` are mandatory operating
authority in addition to this schema and `FAST64_ACCEPTANCE_CONTRACT.md`.
Goal-mode resume may use `FAST64_3_4_GOAL_RESUME_PROMPT.md`.

Create/update the following stage handoffs as execution proceeds:

- `handoffs/FAST64_0_PIVOT.md`
- `handoffs/FAST64_1_PLATFORM.md`
- `handoffs/FAST64_2_REPAIR_QUALIFICATION.md`
- `handoffs/FAST64_3_BASE_CHARACTERIZATION.md`
- `handoffs/FAST64_4_PRIMARY_MATRIX.md`
- `handoffs/FAST64_5_CAUSAL_ANALYSIS.md`
- `handoffs/FAST64_6_SENSITIVITY.md`
- `handoffs/FAST64_7_FINAL.md`

Every handoff must contain:

1. stage name and status;
2. input Framework/Core SHAs;
3. previous-stage PASS anchor;
4. resolved configuration SHAs;
5. observer identity;
6. workload/payload identities used;
7. exact completed experiment IDs;
8. terminal/parser/accounting status per row;
9. acceptance checklist with HARD items explicitly checked;
10. issues encountered and their resolution IDs;
11. invalidated/obsolete rows and reasons;
12. current worker-pool/resource calibration;
13. compact result paths and raw-log index;
14. mechanism/scientific finding appropriate to the stage;
15. exact next executable action;
16. do-not-redo list.

## Stage-specific minimum content

### FAST64.0

- Tier A/B/C evidence map;
- heavy payload dispositions;
- frozen FAST12 roster;
- pivot parent SHAs.

### FAST64.1

- Base/IO/OO resolved-config diff;
- 64x1 shell proof;
- FAST12 payload hash table;
- lower-cap qualification evidence;
- smoke results.

### FAST64.2

- natural triplet result table;
- forced queue-full stress setup and observed stall counts;
- exact lower/dependency/drain conservation;
- paper-category mapping proof for queue-full stalls.

### FAST64.3

- all 12 Base rows;
- structural-pressure table;
- live-miss table;
- host runtime/resource table;
- any workload-local issue resolution;
- exact-identity promotion/reuse audit for precomputed rows;
- metric-completeness closure for every frozen FAST12 member;
- identity/evidence manifest and raw-log index.

### FAST64.4

- all 36 primary row identities;
- Base/IO/OO cycles and instruction identity;
- correctness/drain status;
- speedups and GM-FAST12;
- retry/obsolete map;
- triplet identity audit and mode-specific accounting table;
- identity/evidence manifest and raw-log index.

### FAST64.5

- causal classification for all 12;
- required compact CSVs;
- plot paths/data;
- outlier explanations;
- unresolved issues must be zero before PASS.

### FAST64.6

- sensitivity roster proof frozen pre-benefit;
- exact one-dimensional config diffs;
- physical-line mapping for capacity points;
- per-point terminal validity.

### FAST64.7

- final review-pack index;
- final aggregate membership;
- Tier A and Tier C evidence indices;
- limitations;
- branch cleanliness/push proof;
- terminal state.
