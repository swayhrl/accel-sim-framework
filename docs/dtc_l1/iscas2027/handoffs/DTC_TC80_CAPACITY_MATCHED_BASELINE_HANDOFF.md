# DTC TC80 Capacity-Matched Conventional Baseline Handoff

## 0. Purpose

This handoff defines a bounded ISCAS-2027 fairness experiment that adds an **80-KiB tightly-coupled conventional GPU L1 baseline** (`TC80`) to the already frozen FAST64 / Lane-E evidence.

The experiment answers one specific reviewer-facing question:

> If the additional on-chip data storage used by Decoupled-Tag Cache were instead exposed as ordinary searchable capacity in a conventional tightly-coupled L1 cache, how much of the DTC performance benefit would remain?

This is **not** an area-matched experiment. It is a **data-capacity-matched conventional-cache experiment**.

Authoritative frozen starting point:

- repository: `swayhrl/accel-sim-framework`
- frozen Lane-E branch: `hrl/decoupled-l1-fast64-post-analysis-v0`
- frozen starting commit: `b201b03f8100b5df0010fb64849a3e826b5a2183`
- new experiment branch: `hrl/iscas2027-dtc-tc80-baseline-v0`
- frozen FAST64 authority: `18a68dcccd795f1b6cda75504e9450d00c9cee02`

The frozen Lane-E package and all prior accepted Base/IO/OO rows are read-only scientific inputs. Do not modify them.

---

## 1. Scientific comparison and terminology

Use these names consistently.

### `B16`
Frozen conventional baseline from FAST64:

- tightly-coupled conventional L1 behavior;
- 16 KiB searchable L1 data capacity;
- 128-B line;
- frozen Base PIB = 8;
- frozen Base MSHR = 32;
- frozen memory system, trace payload, latency model, policies and GPU shell.

### `TC80`
New **tightly-coupled conventional** L1 baseline:

- exactly **80 KiB searchable conventional L1 data capacity**;
- exactly **640 cache lines × 128 B = 81,920 B**;
- ordinary tightly-coupled Tag/Data allocation;
- no tag-to-physical-line renaming;
- no DTC IO/OO lifetime semantics;
- Base-style PIB and MSHR must remain 8 and 32 unless an explicitly separate future ablation is approved;
- all non-capacity architecture parameters must remain identical to B16.

### `IO16/80` and `OO16/80`
Existing frozen DTC configurations:

- logical Tag capacity equivalent to 16 KiB;
- physical data pool = 80 KiB / 640 lines;
- IO PIB = 256;
- OO PIB = 128;
- frozen semantics and accepted results only.

### Claim boundary

`TC80` is a **data-capacity-matched** conventional baseline, not an area-matched baseline. It deliberately gives the conventional cache all 640 lines as searchable cache capacity, whereas DTC retains only the frozen logical Tag space and uses the extra physical lines to hold in-flight / still-referenced state.

Therefore:

- it is valid to compare DTC against `TC80` as “ordinary cache capacity vs decoupled physical state under the same 80-KiB data-array budget”;
- it is **not** valid to call the comparison total-area matched until RTL/DC data explicitly proves that;
- it is **not** valid to change TC80 PIB/MSHR at the same time in this experiment.

---

## 2. Hard boundaries

### Must not modify

- `docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL/**`
- `docs/dtc_l1/post_fast64/lane_e/qa_records/**`
- frozen FAST64 accepted artifacts/results
- accepted IO/OO scientific semantics
- frozen FAST12 trace payloads
- workload membership
- memory-system configuration unrelated to L1 capacity
- L1 hit latency, L2/DRAM latency, scheduling, clocks, memory partitions, CTA/core counts, write policy, replacement policy, line size or trace ordering unless source audit proves the TC80 capacity field necessarily encodes one of these and the user explicitly approves

### Preferred implementation rule

**Config-only TC80 is strongly preferred.**

Do not change simulator/Core source merely to make an 80-KiB conventional cache representable.

If source inspection proves exact 80 KiB cannot be legally represented by the existing conventional cache model without a source change, stop at CM0/CM1 and report the exact constraint plus safe options. Do not silently approximate 80 KiB and do not patch indexing logic without approval.

### Execution safety

- preserve raw run directories once created;
- no destructive cleanup of prior FAST64/Lane-E evidence;
- no force push;
- no timeout-based scientific acceptance;
- terminal runs must naturally finish and pass the same class of fatal/assert/deadlock/error scans used by FAST64;
- negative or zero performance results must be retained.

---

# 3. Stage plan and acceptance gates

## CM0 — Source/config feasibility audit

### Goal

Prove how the frozen conventional Base capacity is represented, and determine a legal exact-80-KiB tightly-coupled geometry without running the full experiment.

### Required investigation

Inspect the actual source/config path used by FAST64 Base and answer, with source references:

1. Which structure/fields determine conventional Base Tag entries and data entries?
2. Does Base mode use `-gpgpu_cache:dl1`, DTC logical/physical parameters, or both?
3. What indexing assumptions exist for number of sets?
4. Must set count be a power of two?
5. Can associativity be non-power-of-two (e.g. 20-way)?
6. Can exactly 640 conventional lines be represented without source changes?
7. Does changing cache geometry alter modeled L1 hit latency automatically, or is latency independently fixed?
8. What runtime/config echo proves the effective capacity?
9. Which DTC-only counters/state must remain inactive in conventional mode?

### Geometry selection rule

Target exact capacity is fixed:

`640 lines × 128 B = 80 KiB`.

If multiple legal exact geometries exist, select the primary geometry using this precedence:

1. preserve the frozen B16 set-index mapping / set count where practical, so the experiment isolates additional conventional searchable capacity;
2. preserve 128-B line size;
3. preserve the same bank count/request bandwidth and replacement policy;
4. avoid source changes;
5. record all alternative legal geometries and why the selected one is preferred.

A likely candidate such as `32 sets × 20 ways × 128 B = 80 KiB` may be used **only after source audit proves it is legal**. Do not assume this in advance.

### Outputs

- `docs/dtc_l1/iscas2027/tc80/CM0_SOURCE_AND_CONFIG_AUDIT.md`
- `docs/dtc_l1/iscas2027/tc80/CM0_GEOMETRY_CANDIDATES.tsv`

Suggested TSV fields:

`candidate_id,sets,ways,line_bytes,total_lines,total_bytes,exact_80k,source_legal,indexing_legal,config_only,selected,reason`

### CM0 PASS

Only PASS if:

- exact B16 conventional path is source-proven;
- exact TC80 = 81,920 B / 640 lines is representable config-only;
- selected geometry and its indexing legality are source-proven;
- no simulator source modification is required;
- frozen Lane-E/FAST64 artifacts remain untouched.

If not, status must be `CM0_BLOCKED_EXACT_TC80_REQUIRES_SOURCE_CHANGE` and stop for review.

---

## CM1 — TC80 configuration lock

### Goal

Create one immutable TC80 configuration and prove that it differs from frozen B16 only in sanctioned conventional-cache capacity geometry.

### Requirements

Create a dedicated TC80 config/overlay. Resolve the final effective configuration exactly as FAST64 did.

The following must remain frozen relative to B16 unless the source audit proves a capacity-encoding exception:

- conventional/DTC mode selector = Base/conventional mode;
- line size = 128 B;
- PIB = 8;
- MSHR = 32;
- L1 modeled hit latency;
- allocation/request widths except those mechanically implied by legal cache geometry;
- replacement/write policy;
- core/cluster count;
- memory partitions;
- L2/DRAM config;
- scheduler;
- trace payload.

### Required machine-readable diff

Produce a resolved `B16 vs TC80` config diff. Every changed field must be classified as one of:

- `REQUIRED_TC80_CAPACITY_GEOMETRY`
- `DERIVED_FROM_REQUIRED_GEOMETRY`

Anything else is a HARD FAIL pending user approval.

### Outputs

- immutable TC80 config/overlay under `docs/dtc_l1/iscas2027/tc80/config/` or the project’s established config location
- `CM1_TC80_CONFIG_LOCK.md`
- `CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv`
- config SHA-256 manifest

### CM1 PASS

- exact runtime-effective data capacity = 80 KiB;
- 640 conventional searchable lines;
- tightly-coupled conventional behavior;
- Base PIB/MSHR unchanged;
- no unrelated resolved-config difference;
- config and manifest hashes frozen.

---

## CM2 — Smoke, identity and capacity sanity

### Goal

Prove TC80 launches correctly, truly behaves as a conventional 80-KiB cache, and preserves payload/platform identity before launching FAST12.

### Smoke set

Use at minimum:

- `NN` — fast sanity anchor;
- `Btree` — irregular/low-latency anchor;
- `BICG` — memory-sensitive anchor.

If an existing FAST64 smoke convention is more authoritative, reuse it and document why.

### Checks for every TC80 smoke row

- exact frozen trace identity;
- exact resolved TC80 config SHA;
- natural exit code 0;
- strict parser success;
- no assertion/fatal/deadlock/trace/payload error;
- instructions match the accepted frozen payload identity;
- runtime/config echo proves selected conventional geometry and 80-KiB effective capacity;
- no IO/OO DTC mechanism is accidentally active;
- Base-style PIB/MSHR values remain 8/32;
- all terminal request/dependency/drain accounting closes according to existing framework checks.

Do **not** require performance to improve. Performance regressions are valid data.

### Outputs

- `CM2_SMOKE_RUN_MANIFEST.tsv`
- `CM2_SMOKE_VALIDATION.tsv`
- compact raw-log/provenance hashes

### CM2 PASS

All smoke rows satisfy all identity and terminal checks.

---

## CM3 — Exact FAST12 TC80 campaign

### Goal

Run only the new TC80 conventional baseline on the exact frozen FAST12 payload and reuse frozen B16/IO/OO accepted results by identity.

### Scope

- exact same 12 primary workloads/order as frozen FAST64;
- exact frozen trace members and ordering;
- no Extended-20 or auxiliary workloads in the primary aggregate;
- no post-FAST64 observer runs in the primary aggregate;
- do not rerun B16/IO/OO merely to reproduce already-frozen accepted values unless an identity check cannot otherwise be completed.

### Run acceptance per workload

Each of the 12 TC80 primary rows must have:

- exact trace/payload identity;
- exact TC80 config identity;
- natural terminal exit 0;
- strict parse PASS;
- instruction count matching frozen accepted workload identity;
- no fatal/assert/deadlock/output error;
- closed terminal accounting;
- unique immutable run/attempt identity;
- no mixed execution epochs;
- raw output preserved and compact evidence hashed.

### Primary outputs

- `CM3_TC80_FAST12_RUN_MANIFEST.tsv`
- `CM3_TC80_FAST12_SUMMARY.tsv`
- `CM3_TC80_INPUT_AND_OUTPUT_MANIFEST.tsv`

`CM3_TC80_FAST12_SUMMARY.tsv` must include at least:

`workload,instructions,b16_cycles,tc80_cycles,io_cycles,oo_cycles,speedup_tc80_over_b16,speedup_io_over_b16,speedup_oo_over_b16,speedup_io_over_tc80,speedup_oo_over_tc80`

All B16/IO/OO values must be imported from the frozen accepted package with source SHA/commit lineage, not copied by hand.

### CM3 PASS

- exact 12/12 TC80 primary rows accepted;
- no missing or duplicate primary workload;
- exact ordered membership;
- accepted B16/IO/OO frozen sources hash-bound;
- no diagnostic rows enter the aggregate.

---

## CM4 — Capacity-matched fairness analysis

### Goal

Produce the paper-facing answer to the storage-budget fairness question without overclaiming area fairness or causality.

### Required arithmetic

Recompute from unrounded integer cycles:

1. GM(`TC80/B16`) = geometric mean of `B16_cycles / TC80_cycles`;
2. GM(`IO/B16`) from frozen accepted data;
3. GM(`OO/B16`) from frozen accepted data;
4. GM(`IO/TC80`) = geometric mean of `TC80_cycles / IO_cycles`;
5. GM(`OO/TC80`) = geometric mean of `TC80_cycles / OO_cycles`.

Retain every workload including regressions and near-neutral results.

### Required workload classification

For each workload classify, using a tolerance explicitly stated in the artifact:

- `TC80_BEATS_IO`
- `IO_BEATS_TC80`
- `TC80_BEATS_OO`
- `OO_BEATS_TC80`
- `NEAR_TIE`

Do not use the classification to replace numeric results.

### Optional comparable counters

If and only if the source semantics are already established and exactly comparable across B16/TC80/IO/OO, derive compact explanatory fields such as L1 miss count/rate or lower requests. Do not invent an MLP metric from cumulative counters.

### Required interpretation boundary

The final analysis must explicitly state:

- TC80 exposes all 80 KiB as ordinary searchable cache capacity;
- DTC uses 16-KiB logical Tag capacity with an 80-KiB physical pool;
- TC80 therefore tests `ordinary locality capacity` versus `DTC decoupled in-flight physical state` under the same data-array byte budget;
- TC80 has more searchable Tag entries than DTC and is intentionally a strong conventional-capacity baseline;
- no total-area equality is claimed;
- no RTL timing effect is modeled unless separately measured later;
- PIB/MSHR are intentionally kept at B16 values in TC80, so this stage does not answer a future “large-PIB/large-MSHR conventional cache” ablation.

### Outputs

- `CM4_CAPACITY_MATCHED_COMPARISON.tsv`
- `CM4_CAPACITY_MATCHED_ANALYSIS.md`
- one plot-ready table for the paper

### CM4 PASS

All arithmetic is regenerated from integer cycles, source lineage is explicit, and no area-matched or causal overclaim is present.

---

## CM5 — Geometry robustness gate (conditional)

### Why this exists

An exact 80-KiB conventional cache may require a nonstandard geometry such as high associativity. We must ensure a paper conclusion is not an artifact of one odd geometry.

### Trigger conditions

CM5 becomes mandatory if any of the following is true:

- selected TC80 associativity is substantially larger than B16 (for example >8 ways);
- multiple exact-80-KiB legal conventional geometries exist with meaningfully different indexing;
- CM3 results show an unexplained discontinuity suggesting geometry-specific behavior;
- the source audit identifies a modeling artifact tied to selected set/way geometry.

### Preferred robustness experiment

Use only existing conventional model/config mechanisms.

Priority order:

1. if a second exact-80-KiB legal geometry exists, run that geometry;
2. otherwise run capacity bracketing with legal conventional geometries around 80 KiB (for example 64 KiB and 96 KiB if source-legal) while preserving line size/policies;
3. use at least `BICG`, `Btree`, and `2DConvolution` as representative workloads, unless CM0 identifies a better source-justified set.

No source modification is allowed under CM5 without approval.

### CM5 PASS

Either:

- `NOT_TRIGGERED` with documented reason, or
- required robustness rows terminate and show that the primary TC80 conclusion is not solely an invalid geometry artifact.

CM5 need not enter the paper unless it materially changes interpretation.

---

## CM6 — Final paper-evidence package and freeze

### Goal

Close this fairness experiment as a new, separate scientific artifact without changing frozen Lane E.

### Required final package

Under:

`docs/dtc_l1/iscas2027/tc80/review_pack/`

include compact versions of:

- CM0 source/config audit;
- TC80 config + resolved diff + SHA manifest;
- smoke validation;
- FAST12 run manifest and summary;
- capacity-matched comparison;
- geometry robustness result if triggered;
- claim/evidence boundary;
- reproduction instructions;
- output SHA manifest.

### Final status

If all mandatory stages pass:

`ISCAS2027_TC80_CAPACITY_MATCHED_BASELINE_READY_FOR_PAPER`

If any primary row or identity check is unresolved, do not emit READY status.

### Freeze rule

After CM6 PASS, this TC80 package becomes read-only paper evidence just like Lane E. Further large-PIB/MSHR ablations, RTL/DC area matching, or other baselines must use a new handoff/stage.

---

# 4. Explicitly out of scope for this handoff

Do not broaden this campaign into:

- total-area-matched conventional cache;
- RTL/DC synthesis;
- Base with 128/256-entry PIB;
- enlarged conventional MSHR studies;
- DTC mechanism changes;
- L2 DTC;
- duplicate-request mitigation mechanism;
- new workloads outside frozen FAST12 primary set;
- re-opening Lane-E observer science.

Those may be follow-up experiments after TC80 results and RTL/DC cost are known.

---

# 5. Goal-mode behavior

Codex should continue through ordinary implementation/config/runtime problems instead of stopping at the first failure.

For each failure:

1. preserve evidence;
2. identify whether it is configuration, controller, parser, environment, or scientific-model related;
3. make the smallest bounded fix that does not alter frozen scientific semantics;
4. rerun the affected gate;
5. continue when the gate truthfully passes.

Stop and report before proceeding only when:

- exact TC80 requires simulator/Core source changes;
- frozen trace/input identity would need to change;
- an unrelated architecture parameter must change;
- a destructive action against prior evidence is required;
- scientific interpretation requires user choice.

Never manufacture PASS and never replace exact 80 KiB with a nearby capacity without explicit approval.

---

# 6. Final report requirements

At completion report:

- branch, starting commit, final commit and remote HEAD;
- selected TC80 geometry and source proof of legality;
- exact B16→TC80 resolved config differences;
- smoke results;
- 12/12 TC80 campaign status;
- GM TC80/B16, IO/B16, OO/B16, IO/TC80, OO/TC80;
- per-workload DTC-vs-TC80 classification;
- any geometry robustness experiment and result;
- exact files changed/added;
- confirmation that frozen Lane-E and FAST64 accepted artifacts were untouched;
- confirmation of whether any simulator/Core source file changed (expected: NO);
- raw-run/provenance preservation paths;
- final status.
