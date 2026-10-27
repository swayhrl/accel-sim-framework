# Qualified registry journal instance wrapper candidate V1

This package is **not applied to production**. It wraps the actual frozen
`l2_registry.extend()` in one module instance owned by the existing sole parent.
No frozen file, previous contract, result identity or dispatcher is changed.

The actual-source audit in sibling `audit_v1/` reproduced the ordinary recovery
gap: an authority commit followed by matrix write failure leaves admitted grants
absent from the matrix and the original exact retry asserts. This wrapper adds a
durable PREPARED/COMMITTED journal and reconciles exact existing grants without a
second authority mutation.

## Interface for DTC-MAIN review

```python
manifest = {
    "wrapper_sha256": "PIN_FINAL_DELIVERY_SHA",
    "registry_sha256": "193feb11c91945ae5c675042e42b0f87f9e5ae714e30e937a4f918040d4d834d",
    "execution_plan_sha256": sha(ROOT / "control/EXECUTION_PLAN.json")
}
guard = journal_module.RegistryJournal(existing_registry_instance,
                                      existing_engine_instance, manifest)
# Only after qualified main-owner activation and explicit versioned readback:
startup = guard.recover_pending()  # scans ALL unfinished proposals, grants nothing
existing_registry_instance.extend = guard.extend
original_recommend = existing_adaptive_instance.recommend
def guarded_recommend(*args, **kwargs):
    return guard.guard_decision(original_recommend(*args, **kwargs))
existing_adaptive_instance.recommend = guarded_recommend
```

The manifest must be independently archived/pinned before activation; never derive
a replacement expected hash from a changed file during use. Main must verify its
existing parent lease/owner identity before installing the instance wrapper.
`fault_hook` is for CPU fixtures only and must be omitted in production.

Every call invokes the existing engine's actual `registered()` source/authority
checks, independently checks all plan source pins plus wrapper/registry/plan SHA,
and checks budget/remaining invariants. Scope validation retains every immutable
initial matrix row, exact frozen input domain, base scope SHA and unique cohorts.

The wrapper saves before-authority evidence: exact proposal, each expected new
point, predicted spec SHA, scientific-spec SHA, configs, option count, matrix base
SHA/revision, prior authority accounting/consumed UUID summary and pin manifest.

Within the original extension call, only that registry module instance's `load`
and `put` are temporarily bridged; they and each loaded native module's original
authority function are restored in `finally`. No shared Python module or frozen
source is globally patched. The original function performs the legitimate grant.

## Recovery conditions

All intended grants must either be absent or present. Partial or inconsistent
grants, unknown input links, config SHA mismatch, same-name parameter conflict,
source pin mismatch, or changed scientific spec cause a review hold. The wrapper
never silently grants a missing part of an inconsistent batch.

For exact present grants, recovery only completes missing matrix/history links.
It never calls `update_authority`, adds budget, refunds remaining starts, clears
spent entries, or launches a model. Existing consumed UUIDs and receipt fields
are preserved; concurrent newly completed receipt fields can be appended normally.

Only `estimated_peak_model_RAM_bytes`, `max_process_tree_rss_bytes`, and
`max_process_tree_vms_bytes` may differ from the prepared spec after a legitimate
resource amendment. All other fields, including timeout and result cap, must
match. Both canonical aliases must match the authority's **current** exact spec
SHA; any allowed memory-only amendment is explicitly recorded.

A failure before any grant becomes `UNGRANTED_ENGINEERING_HOLD_SAFE_TO_RETRY` and
returns no new points. A later same proposal can retry without consuming an old
identity. An unreconciled mismatch becomes
`EXTENSION_RECONCILIATION_HOLD_REQUIRES_REVIEW`; `last_issue` and immutable error
events retain evidence. Such a hold is not scientific completion. The scheduler
should surface `guard.last_issue` and monitor the journal; do not hide it behind
an empty proposal list. `guard_decision()` preserves proposals/statistics but
blocks `adoption_ready` and `scientific_stage_complete` while any PREPARED lacks
COMMITTED. It explicitly keeps healthy models running. `recover_pending()` never
creates an absent grant on installation; normal authorized retry can do that
later. Pin mismatches and changed immutable initial identities raise before any
original grant call.

Repeated committed proposals return no new points. A stale but still scientifically
valid matrix snapshot is rebased by appending missing rows to the **current**
matrix, preserving later valid rows and incrementing its current revision.

## Qualification scope

Fixtures use actual frozen source, canonical P0 specs, actual350-row/35-input
matrix, complete270-option expected maps and actual generator. Only authority
updates and filesystem roots are isolated. They inject failures after PREPARED,
authority, matrix and history; preserve a consumed UUID and natural receipt;
exercise valid memory amendments, science/config/source mismatches, partial grants,
changed initial identities, duplicate retries and a stale prepared base.

All qualified registrations are synthetic fixture registrations. They are not
simulations, performance evidence or production authority changes. Draft candidate
preimages remain in this package's 164 `draft_preimages/`; no source was frozen or
activated by Agent E.
