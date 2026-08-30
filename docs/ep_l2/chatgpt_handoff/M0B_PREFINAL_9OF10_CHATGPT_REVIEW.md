# EP-L2 M0b Pre-Final 9-of-10 — ChatGPT Review

Date: 2026-08-30

Status: **PASS_FOR_MECHANISM_DIRECTION_AND_M3A_PREP** — not final M0b closeout.

Reviewed M0b producer:

```text
Integrated parent Core   1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
M0b Core                 9907b7e617ea0ee6580fb8156e985838720f08fa
Frozen runtime Framework 8a0299cab19a658d34b7a2dc0b6d91e8373c121b
Helper Framework          63084e5117640bc6fa4c729280517b25820e328d
```

The source/producer semantics were independently accepted earlier in `M0B_SOURCE_INTERIM_CHATGPT_REVIEW.md`.

## 1. Completed-data gate

PASS for pre-final mechanism-direction decisions.

Completed required campaign units in the published pack:

```text
M0B ON:
  convolutionSeparable
  spmv
  vectorAdd_4M
  sad
  dwt2d
  cfd_097k

M0B OFF controls:
  convolutionSeparable
  dwt2d
  sad

running:
  scan ON
```

All nine published units are `COMPLETE_VALID`. The three completed OFF/ON controls have exact cycles and instructions and exact retained deterministic target summary/slice/L1/DRAM artifacts under the one-bit M0b config delta.

The final closeout should compare every deterministic parsed artifact family actually emitted by both modes. If kernel/bank/window artifacts are not produced in this M0b runner, final packaging must say `NOT_EMITTED_BY_M0B_RUNNER` rather than silently implying they were compared.

## 2. RO / pending-state opportunity

Classification for mechanism direction:

```text
PROMISING_BUT_UNCERTIFIED
```

This is not `SAFE_RO_ELIGIBLE` and is not yet authorization for a functional MSHR-bypass implementation.

Across the four completed RO-focus workloads available before scan:

```text
Line-MSHR allocations / uncertified candidates = 1,131,194
source-proven SAFE_RO_ELIGIBLE               = 0
```

Every tracked allocation in these rows is an ordinary non-write/non-atomic/non-writeback candidate, but no source predicate proves alias/order/write-policy safety.

The available exact milestone data nevertheless show a substantial long-lived candidate population. Weighted over the four rows:

```text
allocation -> first fill   ~988 cycles average
allocation -> all-ready    ~1125 cycles average
```

This is evidence that a potentially cheaper pending-state representation could remain live for a long interval. It is not evidence that the current Line-MSHR can safely be removed for that interval.

The next useful engineering/scientific question is therefore **certification and state-minimality**, not another broad opportunity sweep.

## 3. Dirty-victim / TVD premise

For the specific mechanism motivation:

> keep dirty victim data by moving it into TVD so the old resident payload slot can be released before `set_done`

the current modeled premise is rejected.

Completed data contain:

```text
dirty-victim old handles observed = 683,333
old handle live after reassignment = 0
old handle not-live                = 683,333
```

The WAD still remains live until true `set_done`, but the old resident payload handle is already invalid/reassigned. Therefore the current model does **not** couple old resident payload ownership to WAD no-return completion.

Accepted narrow classification:

```text
NO_OPPORTUNITY_IN_CURRENT_MODEL
```

for **early release of the old resident payload handle**.

This does not reject every future WAD/victim-data optimization; it rejects the specific M4 payload-lifetime story previously proposed.

## 4. Standalone shared/unified payload

Completed M0b ON rows report:

```text
resident production allocations     = 1,842,117
non-resident production allocations = 0
```

No synthetic bypass demand was created.

Accepted pre-final classification:

```text
NO_REAL_CONSUMER_YET
```

Standalone 1152-slot role sharing is therefore not a current first functional mechanism. It can become relevant only after another mechanism creates a real non-resident/transient payload role or changes the payload lifetime contract.

## 5. `scan` late gate

The existing `scan` ON process remains a useful breadth/temporal validation row but does not block the source/semantics review or M3A design preparation.

After natural completion, final review only needs to determine whether scan:

```text
- uses the same frozen source/config;
- parses cleanly with 64 slices;
- preserves the current RO candidate interpretation;
- introduces any counterexample to old-handle non-liveness;
- introduces any real non-resident production allocation;
- materially changes mechanism priority.
```

No completed row should be rerun for the final delta review.

## 6. FWT_7_21 contract discrepancy

The original M0b handoff listed `FWT_7_21` as a WAD/TVD focus workload, but the current campaign/pack contains no FWT_7_21 row and calls scan the only remaining unit.

This must not be silently represented as original-contract completeness.

ChatGPT grants a **scope waiver for the current M0b TVD premise only**:

```text
FWT_7_21 = WAIVED_AS_REDUNDANT_FOR_CURRENT_TVD_PAYLOAD_HANDLE_PREMISE
```

Reason: the source question is path-semantic, and 683,333 dirty-victim events across four completed workloads already exercise the same old-handle reassignment/liveness contract with zero counterexamples. Running FWT_7_21 cannot restore an old handle whose production lifecycle invalidates it at reassignment.

If a later WAD mechanism studies a different property such as WAD occupancy duration, writeback scheduling, or phase-local WAD hazard overlap, FWT_7_21 may again become relevant.

## 7. Next-stage decision

Before scan finishes, authorize **M3A RO Certification / Pending-State Minimality preparation** as source/design work.

M3A must answer:

```text
1. Is there a conservative source-proven safe request class?
2. What exact state must survive if a traditional Line-MSHR is replaced or released?
3. Which current Line-MSHR fields can be removed versus merely moved?
4. What is the metadata/storage/timing cost of the alternative pending object?
5. Is a safer first mechanism release-at-all-ready / response-tail decoupling preferable to pre-fill MSHR replacement?
6. Which missing lifetime milestones need a small observation-only callback before functional implementation?
```

No functional M3 behavior is authorized by this pre-final review itself.
