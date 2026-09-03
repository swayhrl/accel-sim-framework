# M5 Extended-20 Formal Experiment Matrix

Status: **APPROVED — EXECUTE UNDER M5 v3 DEPENDENCIES**

Authority:

- `M5_V3_PARALLEL_TRACKS_APPROVAL.md`
- `M5_EXTENDED20_APPROVAL.md`
- `M5_PARALLEL_BATCH_POLICY.md`
- existing M5 v1 compute definitions and problem-resolution policy

## Scientific question

The Extended-20 track asks whether the already-validated DTC mechanism generalizes beyond the ten thesis compute workloads. It is not a second attempt to fit the thesis' numeric speedups.

Primary causal chain remains:

`Base structural pressure -> live-miss limitation -> IO/OO DTC changes concurrency/latency hiding -> performance effect`.

## M5.E1 — Formal identity and runner readiness

### Inputs

Use exactly the 20 workloads approved in `M5_EXTENDED20_APPROVAL.md`, subject only to the ranked-alternate rule there.

### Required work per workload

Freeze and record:

1. suite/project and exact source commit/tag/version;
2. source and wrapper paths;
3. deterministic build command/toolchain;
4. executable SHA-256;
5. PTX SHA-256 and PTX target;
6. canonical/frozen input path and byte SHA-256;
7. output checker/reference and hash;
8. launch geometry/work amount;
9. historical prior-run evidence used only for runtime planning;
10. expected operation classes relevant to M4 semantics (Load/Store/Atomic/architectural bypass/FENCE_OP source-domain count where available).

Correct the BlackScholes metadata as required by the approval file.

### Common experiment anchor

M5.E2 may not start until M5.2 has supplied/frozen:

- Core formal behavior SHA;
- Framework formal orchestration/parser SHA;
- PAPER_BASE / PAPER_IO / PAPER_OO config hashes;
- ratio-zero conventional-L1 policy;
- Figure-4.2 counter semantics;
- Figure-4.7 live-miss lifecycle/denominator;
- parser schema and result identity tuple.

E1 may prepare manifests/builds earlier, but must recheck hashes against the final M5.2 anchor before launching E2.

### E1 acceptance

`CORRECTNESS_HARD`:

- all 20 have deterministic source/input/output-check identities;
- build/PTX extraction is reproducible;
- no unsupported feature silently changes DTC interpretation.

`FIDELITY_HARD`:

- no workload/input is changed because of observed DTC speedup;
- no selected workload duplicates Paper-10 under another name;
- any alternate substitution is pre-performance and rechecks P1-P6.

### Handoff

`docs/dtc_l1/m5/handoffs/M5_E1_EXTENDED20_FORMALIZATION.md`

PASS -> wait for/verify M5.2 anchor, then M5.E2.

---

## M5.E2 — Primary 60-run generalization wave

### Matrix

For every selected workload run exactly one primary triplet:

- `PAPER_BASE`
- `PAPER_IO`
- `PAPER_OO`

Total primary configurations before retries: `20 * 3 = 60`.

Do not add logical/physical/PIB sweeps to the primary Extended-20 wave.

### Required measurements from the same primary runs

At minimum collect:

- simulator cycles and instruction count;
- output/correctness result;
- source-domain Load/Store/Atomic/FENCE_OP counts;
- Figure-4.2 structural stall counters for Base plus diagnostic Tag-bank/other channels;
- Figure-4.7 average concurrent live misses and audit peaks/totals;
- PIB occupancy/full counters;
- MSHR entry/merge pressure for Base;
- true Tag/cacheline allocation pressure;
- lower/miss-queue/downstream pressure;
- DTC new miss / pending hit / duplicate lower traffic;
- physical pool pressure/reclaim where applicable;
- IO HOL evidence;
- OO ready-younger/out-of-order retire and Ref/reclaim evidence;
- L2/NoC/DRAM traffic/pressure fields already approved for M5 causal analysis.

### Triplet correctness/fidelity acceptance

For each workload:

`CORRECTNESS_HARD`:

- Base/IO/OO complete with valid output;
- no unclassified simulator assertion/deadlock;
- all request/dependency/PIB/inflight/lower accounting drains;
- exactly-once completion invariants remain valid;
- source-domain dynamic operation identity is compatible across Base/IO/OO. Any mismatch must be classified/resolved before the triplet becomes FORMAL.

`FIDELITY_HARD`:

- same source/input/PTX and unrelated platform configuration across the triplet;
- only DTC mode/mechanism-specific frozen parameters differ;
- ratio-zero policy remains identical where conventional L1 policy is instantiated;
- no per-workload architecture tuning.

`MECHANISM_EXPECTATION`:

- positive, zero, or negative DTC speedup is allowed;
- live-miss increase is not mandatory for every workload;
- surprising behavior triggers causal classification rather than result deletion.

### Scheduling

All 60 jobs enter the resumable worker pool defined by `M5_PARALLEL_BATCH_POLICY.md`. Serial workload-by-workload execution is not the default.

### Handoff/review pack

- `docs/dtc_l1/m5/handoffs/M5_E2_EXTENDED20_FORMAL.md`
- `docs/dtc_l1/review_packs/M5_E2_EXTENDED20_FORMAL/`

Required compact outputs include at least:

- `extended20_summary.csv`
- `extended20_stalls.csv`
- `extended20_live_misses.csv`
- `extended20_traffic.csv`
- `extended20_io_oo.csv`
- `RESULT_MANIFEST.tsv`
- `RAW_LOG_INDEX.tsv`
- parser/counter sanity evidence.

PASS -> M5.E3.

---

## M5.E3 — Extended causal/generalization synthesis

### Required results

Per workload report:

- Base cycles;
- IO and OO speedup relative to Base;
- average live concurrent misses Base/IO/OO;
- Base structural-bottleneck classification;
- IO-vs-OO HOL/retirement opportunity;
- traffic/downstream consequences;
- causal class for weak/negative/outlier behavior.

Use the same causal vocabulary as Paper-10, including at least:

- conventional-structure limited;
- workload/input low-pressure;
- compute-bound;
- downstream/platform limited;
- traffic-sensitive;
- IO-HOL-sensitive;
- OO-reclaim-sensitive;
- genuine mechanism non-beneficiary;
- implementation/modeling issue (must be resolved before final acceptance).

### Aggregate labels

Compute:

- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` using Paper-10 + Extended-20 only after all 30 primary triplets are correctness/fidelity clean.

Keep `GM-PAPER10`/`GM-GP` separate.

### Targeted follow-up rule

Do not blanket-run Figure-4.8/4.9/4.10 sweeps over all Extended-20 workloads.

Targeted one-dimensional follow-ups are permitted only to resolve a specific causal ambiguity, for example:

- high live-miss gain but no speedup;
- strong IO/OO divergence;
- unexpected physical pressure;
- unexpected PIB sensitivity;
- negative speedup with otherwise clean correctness.

Each targeted run is `DIAGNOSTIC_EXTENDED`, records the hypothesis it tests, and does not change the primary 60-run aggregate definition.

### E3 acceptance

- all 20 have a causal classification;
- no unresolved correctness/fidelity defect remains;
- negative results are retained;
- all aggregates have explicit membership and missing-data policy;
- selection remains demonstrably pre-performance.

### Handoff

`docs/dtc_l1/m5/handoffs/M5_E3_EXTENDED20_SYNTHESIS.md`

PASS contributes to the `M5.COMPUTE_FREEZE` join barrier.
