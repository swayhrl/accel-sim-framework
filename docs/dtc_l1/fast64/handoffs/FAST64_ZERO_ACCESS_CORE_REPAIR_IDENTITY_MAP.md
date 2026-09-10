# FAST64 zero-access Core repair identity / reuse map

Status: **FINALIZED FOR CORE/RUNTIME TRANSITION — HOTSPOT1 REPAIRED-CORE TRIPLET STRICT-VALID**

This is the required explicit old-to-new identity map. It is not a result
promotion and does not replace `FAST64_RESULT_IDENTITY.md`; it records exactly
which historical evidence remains literal bbcbb evidence and which classes may
be reused under source proof after the source-local zero-access guard commit.

## Repair candidate

The isolated candidate starts from formal Core
`bbcbb5e7565417102087bc80b14c349b4e568c05` and changes only
`ldst_unit::issue()`:

```c++
(dtc_l1_paper_io_active() || dtc_l1_paper_oo_active()) &&
!inst->accessq_empty() && m_L1D != NULL && ...
```

The pre-existing `assert(n_accesses > 0)` remains inside the nonempty DTC line
reference path. `memory_cycle()` already returns complete before DTC admission
for an empty access queue. Thus the candidate creates no fake line reference,
PIB entry, lower request, dependency, pending-write mutation, allocation,
merge, or retirement-side exception for a no-effective-access load.

## Adoption proof (closed)

All of the following must be recorded before this map becomes final:

1. Hotspot1/PAPER_IO and PAPER_OO exact isolated guard qualifications naturally
   terminate with clean error scans, conservation, and terminal drain. **PASS:**
   IO has `85,206` cycles / `377,291,004` instructions and OO `83,439` /
   `377,291,004`; both close lower/credit/dependency state and drain all
   mode-specific terminal state.
2. A clean Release build with `GPGPUSIM_BUILD_DTC_L1_TESTS=ON` passes
   `dtc_l1_m1_common_test`, `dtc_l1_bad_generation_test`, and
   `dtc_l1_completion_accounting_test`.
3. The minimal diff is committed to the active Core branch and a fresh formal
   runtime SHA-256 is recorded. **PASS:** Core
   `95ccdb7a056f2d53f740d90869785cac6d4ee0f5`, trace-enabled Release runtime
   `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`.
4. Focused Base/IO/OO differentials prove the candidate does not change a
   nonempty-access lifecycle; Base is source-inert because its outer DTC
   IO/OO predicate is false. **PASS:** the fresh common repaired-Core Hotspot1
   triplet is recorded in
   `generated/fast64_repaired_core_qual_v1/FAST64_HOTSPOT1_REPAIRED_CORE_TRIPLET_V1.json`;
   its Base is exact against historical bbcbb Base on cycles (`160,486`),
   instructions (`377,291,004`), PIB admit/retire, lower acquire/release,
   final PIB/lower state and lower-cap-full.
5. Every legacy class is explicitly classified below. No literal Core SHA
   mismatch is silently ignored.

## Final row classes

| row class | old-Core observation | source proof | required action after adoption | promotion rule |
| --- | --- | --- | --- | --- |
| `PAPER_BASE` any successful row | formal bbcbb terminal | outer IO/OO predicate is false, so the new conjunct is unreachable; Hotspot Base exact differential is recorded above | preserve literal bbcbb evidence as `REUSABLE_SOURCE_INERT_BASE` | may be reused with original SHA and this map; never relabel |
| successful bbcbb `PAPER_IO` / `PAPER_OO` row | natural terminal, strict-valid | old source would have asserted if a cacheable DTC load reached this predicate with an empty access queue; repaired-Core Hotspot IO/OO confirms the repaired lifecycle/terminal contract | preserve literal bbcbb evidence as `REUSABLE_ZERO_ACCESS_UNREACHABLE_MODE` | requires each row's own strict provenance/drain check and this map; never relabel |
| Hotspot1 bbcbb `PAPER_IO` / `PAPER_OO` | abort at `shader.cc:4279` before a valid epoch | source-reachable zero-access case observed | retain as failed/obsolete raw evidence | rerun only after the repair Core/runtime is authoritative |
| Hotspot1 `PAPER_BASE` | bbcbb strict-valid | Base guard is source-inert, but a primary triplet requires common Core/runtime | preserve as pre-repair anchor | fresh repaired-Core Base is required with repaired IO/OO for the accepted Hotspot1 triplet |
| live bbcbb FAST64.3/4 rows | not yet terminal | no result identity exists yet | let terminate naturally and strict-collect under literal bbcbb identity | classify under the preceding mode rule only after collection; never relabel |

## Non-negotiable boundary

The accepted Hotspot1 Base/IO/OO triplet will use one repaired-Core/runtime
identity. Existing bbcbb rows remain preserved historical/formal candidates
with their original identity. This map may authorize narrowly proven reuse; it
does not alter payloads, configs, observer identity, workload membership, DTC
mechanism semantics, or any existing raw artifact.

## Repaired-Core Hotspot1 triplet (closed)

The fresh immutable-v2 runs below use the same frozen Hotspot1 payload,
scientific Framework snapshot, A1 observer and only the documented mode config
differences. All three naturally exited `0`, strict-collected, and pass the
immutable triplet validator as
`FAST64_TRIPLET_STRICT_VALID_PENDING_STAGE_ACCEPTANCE`. IO naturally exited
`0` and strict-collected to
`generated/fast64_repaired_core_qual_v1/fast64_hotspot1_io_core95ccdb7a_a1_v1.json`:
`85,206` cycles / `377,291,004` instructions, immutable attempt
`b362f344-86b1-4b73-9f09-8be4d5e71f2e`, clean simulator logs and matching
Core/runtime/config/payload identity.  OO also naturally exited `0` and
strict-collected to
`generated/fast64_repaired_core_qual_v1/fast64_hotspot1_oo_core95ccdb7a_a1_v1.json`:
`83,439` cycles / `377,291,004` instructions, immutable attempt
`05ee615d-0402-40a2-87a6-fa282e1054cf`, clean required log scan, lower-cap-full
`139,750` and OO lower-create-queue-full `35,982` (diagnostic structural
events, not errors). Base records `160,486` cycles / `377,291,004`
instructions and balanced PIB/lower lifecycle. The three rows together are
the final common-identity Hotspot1 triplet; their owning FAST64.3/4 stage
promotion remains separately gated.

The original v1 repaired-Core collector only recorded its initial wait line in
this execution environment, so it cannot be relied upon for final closeout.
It remains unchanged.  Future-only
`monitor_fast64_repaired_core_row_v2.sh` preserves the same validator and
receipt contract but scans the optional launcher log only when it exists.  Its
read-only Hotspot1/IO smoke replay passes and produces byte-identical compact
JSON (`f2080ee37d08b8f7b93e7dddcd7633132ec5f0efc6adb1767ca2d5eff6918fef`);
this is a host collector correction, not a simulator or DTC semantic change.

## Transition decision

`FAST64_FORMAL_REPAIRED_CORE = 95ccdb7a...` and runtime `462d105c...cc4dbc9`
are frozen for new formal acquisition. Existing bbcbb results retain their
original Core/runtime values and carry one of the explicit classes above. The
transition neither rewrites historical FAST64.1/2 acceptance nor allows a
mixed-identity triplet. It authorizes new repaired-Core rows and mapped reuse
only; logical FAST64.3/4 acceptance remains governed by its own HARD gates.

| mode | CPU | attempt UUID | namespace |
| --- | ---: | --- | --- |
| Base | 5 | `4c9e8862-9279-4357-8ffe-b107816db613` | `fast64_hotspot1_base_core95ccdb7a_a1_v1` |
| IO | 6 | `b362f344-86b1-4b73-9f09-8be4d5e71f2e` | `fast64_hotspot1_io_core95ccdb7a_a1_v1` |
| OO | 8 | `05ee615d-0402-40a2-87a6-fa282e1054cf` | `fast64_hotspot1_oo_core95ccdb7a_a1_v1` |
