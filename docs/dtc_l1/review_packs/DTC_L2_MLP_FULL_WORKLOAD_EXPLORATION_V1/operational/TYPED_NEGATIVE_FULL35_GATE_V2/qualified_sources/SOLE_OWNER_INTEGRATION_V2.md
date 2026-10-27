# Sole-owner candidate V2: exact interface and containment

No production installation was performed. Original faulty view source b30495 and
its schema-only receipt are retained as preimages; they must not be installed.
The real verifier returns `certificate` as a path string. Current view b03766
checks its exact basename, absolute parent/PROD scope, absence of symlinks,
regular-file identity before/after read, returned+pinned SHA, schema and identity,
then parses the bytes. It never trusts the earlier fake fixture's dictionary.

Producer must remain loaded from this exact path, because its __file__ is pinned:
`A/agents/scan_m16_diagnosis_v1/terminal_impl_v1/scan_m16_engineering_negative_v1.py`
SHA `08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013`.
Published producer commit: `f322aa9cd21446e5391c0254b86a8a1eb830a153`.
Actual bundle binding is recorded in REAL_BUNDLE_READONLY_INTEGRATION.json;
certificate SHA `37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7`.

Factory (does not install):

```python
new = owner_recommend_adapter.make_owner_recommend(
    previous_recommend, existing_registry_journal_object,
    source_paths, source_pins, [exact_binding],
    exact_verifier_path, exact_verifier_sha256)
```

`source_paths` maps `base` to frozen R/tools/l2_adaptive.py and `supplement` to
A/agents/E/boundary_validation_v2/l2_boundary_validation.py; corresponding pins
are f21bc123... and a7e47660.... The exact binding contains cohort, uuid,
input_digest, cell=DH, profile=M16, bundle_path and certificate_sha256.

Main must pass the SAME live journal instance already wrapping registry.extend,
not create a second registration owner. The factory captures its bound
guard_decision and calls it LAST after typed view -> private base -> full35
proposal fence -> private V2. Only Main may assign the returned callable to the
current private `adaptive.recommend`, saving the exact previous callable for
restore. Do not add the old V2 augmentation after this callable. Do not replace
registry.extend, resources, choose_dispatch, claims, consumer.summary or any
executor. Restore only if adaptive.recommend is still the installed callable;
set it back to new.previous_recommend. This document supplies the design, not an
automatic apply routine.

Every recommendation freshly calls the real pinned verify_bundle, then makes an
explicit copy of the raw summary. Original RESULT/DONE/EXIT, raw state counts,
cycles, accepted flags, aggregates and consumed entries are not written. The
scan row in the copied view is typed-terminal, cycles=null/unaccepted, with its
original row and certificate pins attached. Unknown/pending engineering events
still block initial completion. The failed M16 profile remains34/35; useful
complete35 profiles can progress. V1 common34 proposals are retained for audit
but excluded from dispatch before V2 runs.

Permission/I/O/JSON/source assertion/verifier HOLD and malformed-return errors
become explicit recommendation ENGINEERING_HOLD with proposals=[] and final
flags false; they cannot unwind the scheduler. The old recommendation is kept
as fallback provenance when available, with its proposals/final flags forced
closed. The same existing journal guard is reapplied; if it also fails, a visible
`EXISTING_FINAL_GUARD_UNAVAILABLE_FAIL_CLOSED` status blocks finalization. No fake
resource or accepted snapshot is created. Resource providers and the conservative
1.392GiB failed-generation growth reservation remain untouched.

Qualification: original full35 gate7 checks; corrected schema4; actual frozen
verifier4 checks using its full CPU archive/restore transaction and actual path
return; owner exception-containment4. Main's real scan bundle also passed read-only
project + recommend through the FINAL factory and actual journal source at
2026-10-28 02:23:33 CST. That check instantiated a read-only journal for validation;
it did not attach to or alter the live owner's journal. Result remains
WAIT_INITIAL_TERMINAL, no proposals, no adoption, engineering review required;
the other real inputs have not all finished. Only synthetic fixtures demonstrate
future full35 directions, not actual performance choices.

Main must announce this versioned typed-terminal/full35-inference policy before
activation. Manual final negative-review disposition remains required. Neither
this module nor its tests clear the original engineering review or claim350
accepted results. Zero model starts, signals, grants or production mutations.
