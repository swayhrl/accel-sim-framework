# REVIEW — 174 Translation Frontend READY-Application V2

Date: 2026-09-23
Owner: ChatGPT
Status: REOPENED_FOR_CORRECTNESS_REQUALIFICATION

## 1. Remote authority independently verified

Execution branch:

`hrl/awma-174-translation-frontend-ready-application-v2`

Remote HEAD:

`1a5f4dc49273c9640b981fb1b946d146dd15f21b`

The remote branch exists at the reported HEAD.

The V2 review pack lists 15 files in `SHA256SUMS`.
ChatGPT independently re-hashed the exact remote contents of all 15 listed files:

`15 / 15 EXACT SHA256 MATCH`

The scoped T2 cycle results are therefore provenance-closed as published artifacts:

```text
T2 V2 10/80 = 111607
T2 V2  0/80 =  71743
reported residual = 35.7182%
```

T0/T1 partial runs are correctly labeled:

`PARTIAL_NONTERMINAL_NOT_MATRIX / STOPPED_AFTER_T2_DECISION_BOUND`

and are not scientific matrix evidence.

## 2. Critical source-contract mismatch

The published V2 semantic contract says:

> V2 consumes existing controller READY once for the exact resident mem_access_t.

The published V2 source patch does not implement that contract.

V1 introduced:

```cpp
translate(..., bool consume_ready = true)
```

with the following semantics in the READY path:

```cpp
if (!consume_ready) {
    *sim_pa = ...
    *source = inflight->source;
    return READY;
}

// consume_ready == true:
// note completion
// erase inflight from m_lookups
// return READY
```

V1 prelaunch correctly passes `false` so that it observes READY but leaves the existing accessq-head path as sole consumer.

V2 currently calls:

```cpp
translate(..., !ready_application_v2)
```

Therefore when:

`ready_application_v2 == true`

the call passes:

`consume_ready == false`

The V2 prelaunch path then:

1. observes READY;
2. obtains PA/outcome;
3. applies PA/outcome to the exact resident `mem_access_t`;
4. marks that access translation-applied;
5. does NOT erase the READY controller lookup.

Because that `mem_access_t` is now translation-applied, its later head path skips `translate()`.

Therefore the retained READY entry has no later requester consumer.

## 3. Published telemetry proves this path dominates T2

Published `READY_APPLICATION_ACCOUNTING.tsv`:

```text
T2 10/80:
prelaunch_ready   = 411008
prelaunch_applied = 411008
head_applied      = 0
duplicate         = 0
ready_unapplied   = 0

T2 0/80:
same values
```

Thus all 411,008 unique logical accesses are reported as applied through prelaunch and zero are consumed through the head path.

Under the published V1 controller API, those prelaunch READY observations do not consume their `m_lookups` entries.

This is not a rare corner case.

## 4. Quiescence evidence is insufficient and inconsistent with the source path

The published T2 receipts report only:

- active MSHR = 0;
- PWQ = 0;
- walkers = 0;
- Segment inactive.

They do not report:

- `m_lookups.size()`;
- count of `LOOKUP_READY` entries;
- `quiescent_invariants_hold()`.

The accepted controller definition of quiescence requires:

```cpp
m_mshrs.empty() &&
m_lookups.empty() &&
invariants_hold()
```

Therefore MSHR/PWQ/walker drain alone is not translation-controller quiescence.

The user-facing statement that translation quiescence passed is not supported by the published V2 pack.

## 5. Likely explanation for the extreme host-time growth

The accepted controller's `find_lookup()` searches `m_lookups` linearly.

If V2 leaves READY entries resident while applying their results to accessq entries, `m_lookups` can grow with completed unique requesters.

That creates increasing host-side lookup/search cost while simulated cycle progress continues.

This is consistent with the observed V2 behavior:

- forward simulated progress;
- no simulator deadlock;
- rapidly worsening host-time per simulated cycle.

This is a source-supported explanation, not yet a measured host-profile claim.

## 6. Scientific status of the published V2 conclusion

Published classification:

`READY_APPLICATION_HOL_NOT_PRIMARY`

is NOT YET ADMITTED.

Reason:

The candidate implementation violates its own hard semantic contract:

`consume each controller READY exactly once`

and does not establish terminal controller quiescence.

The exact equality:

```text
V2 T2 == V1 T2
111607 / 71743
```

is useful diagnostic evidence, but it cannot close the scientific question until the READY ownership leak is repaired and the T2 pair is requalified.

This is a local implementation/bookkeeping defect, not evidence that the conceptual V2 semantic axis is invalid.

Do not discard the published V2 run. Preserve it as:

`PRE_REPAIR_READY_RETENTION_INVALID_FOR_FINAL_CLASSIFICATION`

## 7. Minimal repair

The intended V2 behavior is already supported by the V1 controller API.

For V1 mode:

- prelaunch should observe READY without consuming it.

For V2 mode:

- prelaunch should consume READY and immediately apply the returned PA/outcome to that exact resident `mem_access_t`.

The simplest source behavior is equivalent to:

```cpp
consume_ready = ready_application_v2;
```

for the pipelined prelaunch call:

- V1: `false`
- V2: `true`

Do not mechanically apply this text without checking the exact candidate source and zero-latency recursion, but no new controller state machine should be required.

The repaired V2 must prove:

1. each READY completion is consumed exactly once;
2. applied resident entry receives the same returned PA/outcome;
3. downstream accessq order is unchanged;
4. no duplicate data side effect;
5. terminal `m_lookups.size() == 0`;
6. terminal `quiescent_invariants_hold() == true`;
7. MSHR/PWQ/walker drain;
8. full unique translation coverage;
9. Segment dormant.

## 8. Requalification scope

Do NOT rerun T0/T1.

Only re-run:

```text
T2 V2-fixed 10/80
T2 V2-fixed 0/80
```

after directed READY-consumption tests.

Compare exact terminal cycles to:

```text
V1 T2:
10/80 = 111607
0/80  = 71743

pre-repair V2:
10/80 = 111607
0/80  = 71743
```

If repaired V2 reproduces the same cycle pair with true controller quiescence, then:

`READY_APPLICATION_HOL_NOT_PRIMARY`

becomes strongly admissible.

If cycles change, use the repaired results and do not tune toward equality.

## 9. Mainline boundary

Do not start Native↔simulator cross-calibration until this correctness requalification closes.

109 remains idle.

No TLB/PTW/cache architecture mechanism is authorized.
