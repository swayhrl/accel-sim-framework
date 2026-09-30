# C16 E1 Lane 4 project terminal review opinion

Status: `BOUNDED_TERMINAL_REVIEW_COMPLETE; PROJECT_FOLLOWUP_DECISION_REQUIRED`. This is an independent CPU-only review of the published B16 canary, not a Paper V2 result or authorization to start another run. The deterministic packet was committed at `84a43ac95279893c69c6e4be54a156ef02a5bb3a` before the frozen Lane 3 evaluator was invoked.

## What this M1 result establishes

The source chain closes. Publication Framework `71324d46435293edab3b7a0ff6ee999e675be0d0` (tree `9d022115e0407eceb145e4f6f6dc69b1907f865f`) descends from historical preregistration snapshot `8dfd9c0f`. Actual launch Framework commits were `21074f6c` for R0/M1, `297ee71b` for diagnostic, and `ab61ea68` for the bounded repeat; all precede that snapshot and publication. Each raw launch authority and terminal receipt binds Core `0271de82`, binary SHA `6be09869...02186`, condition config, trace config and kernelslist. Publication HEAD, historical snapshot and execution HEAD are distinct identities.

Hash-verified single-pass parsing of the four indexed completed stdout files independently recovered the ordered 1,565-kernel scope, matching R0/M1 executed instruction and CTA counts, and exact M1-versus-diagnostic cumulative cycles/instructions/CTA at every UID. Primary and diagnostic terminated normally; the R0 repeat retains its original intentional nonterminal exit 143 and proves only `BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168`. The diagnostic therefore qualifies for interpretation after the three primary gates. No full-window repeat or dispersion/materiality conclusion follows.

| Bounded range | R0 cycles | M1 cycles | R0−M1 | Arithmetic response |
|---|---:|---:|---:|---:|
| D1 through D2 L0 up, 1,565-kernel `C_window` | 134,571,764 | 134,848,220 | −276,456 | −0.205434% |
| D2 prefix `C_D2_prefix` | 3,535,452 | 3,520,859 | +14,593 | +0.412762% |
| D2 L0 up `C_L0_up_D2` | 1,286,074 | 1,289,645 | −3,571 | −0.277667% |

The M1 mechanism activated but did not improve the selected local timing or entire measured window by arithmetic sign. D2 prefix moved in the opposite direction; this is a bounded decomposition, not statistical significance. `C_window` is not a whole-decode or steady-state TPOT result.

## Churn, retention and admission

At the terminal checkpoint, the source-defined counters are 57,099,207 target accesses, 7,691,289 committed protected fills, 7,560,217 quota-full target→protected replacements, zero protection admissions denied and zero normal-fallback protected victims. Class-1 protected occupancy was 131,072 after D1 L0 up and 0 immediately before D2 L0 up. This directly supports **class-level loss of the protected L0 reuse entry** under the measured interval. It does not measure whether each original address/fill generation survived; that exact field remains `null/UNKNOWN`.

Between those two checkpoints, *global cumulative* target accesses increased 53,158,524, protected fills 7,160,857 and protected→protected replacements 7,160,857; class-1 occupancy changed −131,072. These deltas support substantial target-to-target competition during the interval. They are across all target classes and L2 instances. They do not by themselves assign each replacement to class 1 or uniquely explain its loss. The zero admission-denial and normal-fallback counts make hard denial and ordinary fallback unsupported explanations for this particular class-1 zero endpoint. The exact old-address survival and unique microarchitectural cause remain unestablished.

## Two separate classifications

- **Lane 4:** `CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT` is the published bounded canary interpretation. The Case 4 *exact zero-retention subset* is false because its named constraint events were absent; no unregistered definition of qualitative “almost” or “large” is added.
- **Lane 3 A/B/C/D:** A is the leading **candidate** because global protected→protected churn and class-1 occupancy loss are observed, but exact old-address survival and preregistered high/low materiality cutoffs are missing. B is not established because good old-address survival is unobserved. C lacks positive local/window arithmetic signs. D is unsupported by the observed zero denial counts. The frozen evaluator correctly leaves every A/B/C/D entry `REQUIRES_PROJECT_REVIEW` and reports `old_address_survival_fraction: null`.

“Case 4 not satisfied” does **not** imply “M1F unnecessary.” It only removes a particular admission/fallback explanation for this endpoint. Conversely, the class-1 zero endpoint does **not** prove M1F will restore useful reuse or net cycles.

## Next comparator and cost, if separately authorized

M1F is the first focused *candidate* after project review: a stable subset could reduce competition among target fills, which is the observed pressure channel. Reuse the already frozen `C16_M1F_STABLE_ADMISSION_HASH_V1` selector from `HASH_FREEZE_RECEIPT.json`: SplitMix64 finalizer, seed `0x6a09e667f3bcc908`, key `(target_class << 32) xor region_relative_128B_line_index`, threshold `0x0484baf3b723b966`, unchanged sidecar and B16 scope. No seed search, new eligibility fraction or post-result threshold is justified.

The minimum stage-gated comparison is: (1) CPU-only identity/neutrality and selector distribution check; (2) one M1F B16 primary plus diagnostic if authorized, reusing R0 only if binary/config/trace and workload comparability close; (3) if M1F shows a qualified local/window signal, run `PRIORITY_STABLE` with the **same frozen selector** but without M1's hard quota. That paired comparison separates stable selection from quota enforcement; physical L2 capacity and actual protected occupancy must be reported. If M1F is unhelpful, stop its timing expansion before a full strong-baseline matrix. Any C3 mechanism claim would later still need appropriate generic DRRIP and equal-information SHiP-SW comparisons.

The historical R0/M1 primaries consumed roughly 78/78 hours per run and the diagnostic roughly 88 hours. Thus an M1F primary+diagnostic would be about 166 simulator-slot hours if similar, and a conditional `PRIORITY_STABLE` primary about another 78, up to roughly 244 slot hours before qualification or variance. This is a rough capacity estimate from receipts, not a schedule guarantee or authorization. No experiment is launched here.

Lane 1 strong-baseline and old-address observer implementation qualification is recorded only as **prep evidence**: it reports no full timing and no measured D1→D2 old-generation survival. It creates no Paper V2 result row and does not change the current `null` survival field. Lane 6 FFN patch work remains outside this review.
