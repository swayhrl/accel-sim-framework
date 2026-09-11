# FAST64.3 — 2DConvolution sector-MSHR tag-identity repair

Status: **SOURCE-CLASSIFIED; REPAIR BUILT AND UNIT-REGRESSED; FORMAL
REPLACEMENT PENDING.**  This is not a FAST64.3 result and does not alter any
existing accepted or historical result.

## Scope and preserved evidence

The formal `2DConvolution/Base` attempts under the historical and Core-41
identities remain invalid attempts.  The terminal dc6062 observation is
retained as `NONFORMAL_DIAGNOSTIC_NOT_RESULT`:

- namespace: `fast64_3_2DConvolution_base_coredc6062_transition_diag_v2`
- UUID: `482ca8b3-fa7c-4a8b-b99d-494e349961a6`
- diagnostic Core: `dc6062c69843ffb467ceabd32eed625fbc5776bf`
- compact diagnostic:
  `generated/fast64_3_transition_diagnostics_v2/fast64_3_2d_base_coredc6062_transition_diag_v2.json`
- source follow-up:
  `generated/fast64_3_transition_followup_v1/fast64_3_2d_base_coredc6062_transition_followup_v1.json`

Its terminal dump has no conventional MSHR, miss-queue, or fill-owner entry,
but has ownerless `RESERVED` ways in L1D_003, L1D_029, and L1D_051.  The
diagnostic-only Core remains separate from the formal Core and added no
functional behavior.

## Source-backed root cause

The dc6062 records contain 87,908 read `TAG_ALLOC` records and 87,880
same-UID read `OWNER_CREATE` records: 28 read tag allocations have no fill
owner.  Write allocations are excluded from this comparison because their
lazy-write lifecycle is distinct (22,916 write allocations and zero matching
read-owner records).

Source inspection establishes the lost identity transition:

1. `tag_array::access()` allocates a tag on `MISS` or `SECTOR_MISS`.
2. In the old `baseline_cache::send_read_request()` MSHR-merge branch, the
   code called that access before `m_mshrs.add()` without checking whether the
   current tag still represented the existing sector-MSHR root.
3. The root miss records its cache index in `m_extra_mf_fields`; a merge does
   not create another such owner.
4. `baseline_cache::fill()` fills only the root's saved cache index and then
   erases that root owner.  Therefore a merge-side allocation on another tag
   has no fill-owner transition that can turn its reservation into a valid
   line.

This is neither a BK_CONF diagnosis nor a justification to weaken tag,
pending-write, scoreboard, deadlock, or accounting assertions.

## Minimal repair

Core branch `hrl/decoupled-l1-m5-2d-reserved-tag-repair-v0`, rooted at the
accepted formal Core `95ccdb7a056f2d53f740d90869785cac6d4ee0f5`, contains
`6587238c60214d99491f4048e28ce8a3458c1509`:

```text
fix(l1): preserve tag identity across mshr merge
```

The only source change is in `src/gpgpu-sim/gpu-cache.cc`.  Before a read can
merge into an existing MSHR, it re-probes the tag and permits the merge only
for `HIT` or `HIT_RESERVED`.  A `MISS` or `SECTOR_MISS` returns to the
ordinary retry path *before* calling `tag_array::access()` or `m_mshrs.add()`.
Thus no second reserved tag can be allocated against an MSHR whose eventual
fill owns a different cache index.  The repair does not change DTC policy,
counter semantics, payloads, configs, lower-credit behavior, or completion
assertions.

## Isolated build and focused regression

The branch was built in the dedicated non-live directory
`/tmp/dtc-fast64-2d-reserved-tag-repair-v1` with `CMAKE_BUILD_TYPE=Release`
and the normal trace-enabled DTC test option.  It produced:

- `accel-sim.out` SHA-256:
  `29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1`
- `dtc_l1_m1_common_test`: PASS
- `dtc_l1_bad_generation_test`: PASS
- `dtc_l1_completion_accounting_test`: PASS

These tests establish that the new source compiles and preserves the existing
common, generation, and completion-accounting unit contracts.  They do not
substitute for the required fresh formal 2DConvolution/Base result below.

## Required remaining proof

The dedicated Release runtime hash and focused unit regressions are recorded
above.  A fresh 2DConvolution/Base row must now use that exact Core/runtime
together with the frozen Base config, payload, A1 observer, immutable runner,
atomic receipts,
and a new UUID.  It must naturally exit zero, strict-parse, close
lower/dependency accounting, drain PIB/inflight/lower state, have
lower-cap-full resolved, and materialize complete structural metrics.

Only after that Base gate may 2DConvolution IO and OO be acquired, and both
must share the same final Core/runtime identity.  Historical bbcbb IO/OO
evidence cannot be mixed into that triplet.

## Future-only execution path

`util/dtc_l1/dispatch_fast64_3_2d_base_tag_identity_v2.sh` and
`util/dtc_l1/collect_fast64_3_2d_base_tag_identity_v2.sh` are separate from
all Core-41 and live-controller bytes.  The dispatcher pins the Core commit,
Release-binary hash, frozen Base config/payload/trace, A1 observer, immutable
runner, fresh namespace, and UUID receipt path.  Its no-dispatch identity
check passes.  The paired collector's pre-terminal check reports only
`WAIT_TERMINAL`; it has not written result evidence.

Dispatch is deliberately deferred until a fresh resource admission is safe;
the current populated FAST64 pool is not altered to make room.  This path
therefore prepares, but does not itself produce, the required formal row.

The paired future-only Core-658 IO/OO files are
`dispatch_fast64_4_2d_tag_identity_v2.sh` and
`collect_fast64_4_2d_tag_identity_v2.sh`.  They pin the same Core/runtime,
payload, observer and immutable runner, and require the Base JSON plus
structural companion above to agree on that identity before either mode can
launch.  Both IO and OO no-dispatch checks currently reject with
`BASE_STRICT_GATE_REQUIRED`, as required; neither has created a run directory.

The pre-existing FAST64.4 registry bridge defaulted to an obsolete Core-41
Base registry.  Future-only
`prepare_fast64_4_primary_registry_v2.py` instead requires explicit final
Base-registry, IO/OO-coverage, generated-root, and output paths; it binds the
reused V1 schema validator by SHA-256.  Its positive exact-36-cell and
nonzero-lower-cap negative fixtures pass.  It has not produced a primary
registry and cannot promote FAST64.4.

The SHA-pinned future-only controller
`auto_continue_fast64_2d_tag_identity_v2.sh`
(`9f1185d85f057836ff666b058c73df58447ec09666bba2f383008e783f098baf`)
is the sole automatic continuation path for this replacement.  It only
collects after natural terminal receipts, revalidates the Base gate, performs
a fresh two-worker V3 resource admission, dispatches distinct-CPU IO/OO rows,
and strictly collects those rows at natural terminal.  Its `--once` check
currently returns `WAIT_BASE_TERMINAL` without launching work.  Once its
watch instance starts, none of its pinned helper bytes will be edited.

`prepare_fast64_3_tag_identity_registry_v2.py` is the future-only Stage3
registry bridge.  It replaces only the retained invalid 2D source row after
pinning the existing Stage3 matrix validator, verifying the new strict and
structural evidence, and revalidating all twelve Base rows.  Its static
negative fixture confirms that absent evidence cannot manufacture a candidate
registry; no FAST64.3 registry or PASS marker exists yet.
