# Pre-performance source-derived conservation contract

Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`, `dtc-l1-common.h` SHA `798b3b416ce3223799af870438273167f0d257f1f432a1f0aad9dced06f81510`; source observer header SHA `85dbad1028354142c5f3ca9873fe612aca89d8d6cd666652bcbd28c8280ab2b9`.

The original OO identity was new_misses−immediate_reclaims−final_ref_reclaims=physical_allocated. The new invalidate_lookup branch has an additional ready/Ref0 owner-free release: it calls release(identity,cycle), increments lookup_invalidation_result.reclaimed and then the observer's reclaimed_at_event. It does **not** increment the existing victim immediate_reclaims counter. Conversely, event-retained live-reference lines released at last retirement still increment the existing final_ref_reclaims.

The complete candidate identity is therefore:

`new_misses = physical_allocated + immediate_reclaims + final_ref_reclaims + source_reclaimed_at_event`.

For K1, source_reclaimed_at_event is the sum of the last same-terminal-boundary summary for each of64SM; intermediate kernel cumulative summaries must not be summed. The independent event identity remains changed=retained_at_event+reclaimed_at_event. Retained_at_event is not another release count, and must not be subtracted a second time.

For K0, no source invalidation branch executes; its release contribution is structurally0 by verified OFF code. This is a conservation term, not a claim that absent K0 event-summary fields measured0. The metric dictionary keeps those fields UNAVAILABLE.

Finite release() closes exactly one existing map-loss interval and increments map_loss_to_free_count, including zero-cycle releases. Thus a second check is `map_loss_to_free_count = immediate_reclaims + final_ref_reclaims + source_reclaimed_at_event`. Still-mapped or hidden-but-live intervals are censored until release; their durations cannot be silently inserted into completed conditional means.

This adjustment is derived from fixed source before any new Gaussian performance. No Core, counter, service rate or run is changed, no assertion is weakened, and no result is used to fit the equation. Applying the old formula unchanged to K1 would omit a real newly exposed release category. New full-run conservation is NOT_RUN until admission; a missing K1 reclaimed_at_event field is UNAVAILABLE/fails required physical closure rather than being filled with0.
