# EP-L2 M0b Source / Producer Interim ChatGPT Review

Date: 2026-08-30

Status: **PASS_FOR_PREFINAL_DATA_REVIEW** — not final M0b PASS.

Reviewed source candidate:

```text
Parent Core  1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
M0b Core     9907b7e617ea0ee6580fb8156e985838720f08fa
```

## 1. Observation-only source gate

PASS for pre-final review.

The M0b source delta is additive observation/config state. The `m_ep_l2_m0b_stats` switch defaults OFF and the recorded counters/maps are not consumed by admission, MSHR allocation/retirement, payload allocation, WAD ownership/release, bank arbitration, lower routing, scheduler, or DRAM decisions.

## 2. Line-MSHR identity / lifetime producer

PASS with bounded semantics.

The producer assigns a monotonically increasing epoch at each newly accepted tracked Line-MSHR allocation and keys active observation state by MSHR address. Address reuse therefore creates a new observation epoch rather than merging historical samples.

Supported exact/derived milestones:

```text
allocation
allocation -> first lower issue
allocation -> first fill
allocation -> all required sectors ready
```

Unsupported final-retirement/tail milestones remain explicitly `NOT_EMITTED`.

The measured intervals are candidate pending-state/lifetime opportunity only. They are not proof that the traditional Line-MSHR can safely be removed for that interval.

## 3. RO eligibility discipline

PASS for observation, but no functional RO eligibility has yet been proven.

The implementation intentionally records ordinary non-write/non-atomic/non-writeback tracked allocations as `candidate_uncertified`. This is the correct conservative label because request type alone does not prove alias/order/write-policy safety.

Therefore the current M0b producer may quantify the size and lifetime of an uncertified candidate population, but it may not promote that population to `SAFE_RO_ELIGIBLE` without an additional source-proven certification contract.

## 4. Dirty-victim / TVD premise producer

PASS for the narrow current-model question.

M0b observes the previous resident payload handle only after a native writeback event has been created and after the static payload slot has been reassigned to the new incarnation. Testing `handle_live(old_handle)` at this point directly answers whether the old resident payload identity remains live after replacement/reassignment.

If representative data consistently show old handle non-live while WAD remains outstanding until `set_done`, the supported conclusion is narrowly:

```text
CURRENT_MODEL_DOES_NOT_RETAIN_OLD_RESIDENT_PAYLOAD_HANDLE_TO_SET_DONE
```

This would reject the specific M4 motivation "free a resident payload slot earlier than set_done" in the current modeled payload identity. It does not prove that every possible victim-data decoupling mechanism is useless.

## 5. Shared/non-resident payload producer

PASS for the precondition audit.

The source does not manufacture bypass traffic. Current non-resident allocation count reflects real production payload-role use. If it remains zero over the completed representative set, standalone shared-payload capacity borrowing lacks a real producer-side consumer in the current model.

## 6. Pre-final decision

The source/producer is sufficiently well-defined to review all completed M0b units before long `scan` finishes.

`scan` is treated as a late breadth/temporal validation gate. It is not required to repeat the source review unless the final row reveals a producer/config/source mismatch.

Before selecting a functional M3 RO mechanism, the final/pre-final evidence must still distinguish:

```text
large/long-lived UNCERTIFIED candidate population
```

from:

```text
source-proven SAFE_RO_ELIGIBLE population
```

The former can justify a focused certification/design study, not immediate functional bypass by itself.
