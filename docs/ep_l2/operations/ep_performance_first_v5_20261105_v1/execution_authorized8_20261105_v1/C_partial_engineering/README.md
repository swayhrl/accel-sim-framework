# C frontend followup V3: first real nonzero CLEAN update

The selected final private Core is 0ab3af3d6aecf0e123f7b4fa4bfa85783c99bf8a. This is a successor of sealed fd1a187 and preserves every preceding C source, ELF, archive and review file. It remains a partial production prototype; no C application science scope is admitted.

## Production change

The real tvd_frontend MISSING_SECTOR path now waits for bounded row/count READ/COMMIT service before removing its directory row or returning to ordinary frontend processing. For a CLEAN row it publishes the actual CLEAN count decrement of one during the paid COMMIT, then releases that exact payload generation. READ/HOLD has no count, row, payload-release or lower-request-admission effect.

The transaction uses the existing frontend request UID, selected row incarnation, payload generation and state. The new preview/commit API checks the actual production row, reader count, sectors and identity. Allocator owner/generation, reader pins, pending sectors and generation exhaustion are checked before destructive publication. Incarnation exhaustion is rejected before the existing erase routine could decrement count and then overflow. A stale ticket cannot perform a second decrement.

Only the selected frontend owner can cancel its READ reservation. Pin-related refusal cancels without publishing any row/count change; later retry pays service and commits once. A payload generation mismatch fails closed before erase/release. No new buffer, payload array or packet field is added.

## New finite-port issue found and fixed

A new partial-cancellation negative case found that cancelling one of two K2 READs could let a third distinct row reuse the now-empty slot during the same READ beat. That would refund a physical metadata lane. The original failing return23 is retained against private Core0e69f1b.

The final governor retains each consumed READ identity until the batch ends. Empty/cancelled slots that have already used a physical READ lane cannot accept another row in that beat. Existing key fields provide this accounting; no extra register, lane or queue is introduced. The new bounded owner-cancel test preserves the other producer and prevents the third READ and same-beat refund.

## Cost and remaining boundary

This connects exactly one real nonzero producer: missing-sector reclaim, with CLEAN delta -1 (or WB_COMPLETE delta0). K1/K2 service remains nonoverlapped READ/COMMIT. Lower-WB acceptance and completion share the same governor and have zero CLEAN delta. At most one selected frontend reclaim can make a nonzero count update in one COMMIT beat.

Other installation/replacement increments, general reclaim, promotion, reader lifetime updates, rollback and cleanup still use their previous synchronous paths. Therefore this is not full-pipeline atomic count integration or proof that all producers meet one hardware commit lane. All-row fairness, complete epoch drain, payload-control metadata mux/port timing, RTL CDC and physical PPA remain unqualified. Functional indexed pin/owner checks do not certify a free hardware metadata read view.

The READ identity is a validation ticket, not exclusive row ownership. A legal other producer may invalidate it. COMMIT revalidates the current row and count before publication; unrelated row/count changes are not silently treated as the same snapshot. Global count/revision ordering for every other producer remains a separate integration task.

The final artifacts incrementally rebuild the changed production cache TU and Core-version TU into new copies of fd1-based libraries and a new ELF. Header changes add methods and nested plan types, not persistent fields or virtual methods; old/new l2_cache/directory/governor sizeof values are checked. Full application qualification is not inherited.

All large artifacts and runtime logs are on genuine164. CPU concurrency is at most2 and nice15; Native keeps its5GiB floor. Shared Native, scientific registry, budgets, deployments, full models, Trace and GPU work remain unchanged. Old12/3185/four-handshake cases are not rerun. Only this new reclaim delta and the new cancellation/exhaustion counterexamples are checked.

## Final evidence

Final ELF SHA256: f0d5eb603bbe550eb00bf7fd51c4f688b09841f71fd970c174e9100fe1c06749. Final libgpgpusim SHA256: 5867c3e43f38c9e5cdcaaba49a8ffb8cbc8e5aaadb80b7c64394ff5ed54ff101. Seven selected production/cache-directory cases and two new cancellation/exhaustion boundary cases pass. Old/new class sizes match: 13528 10400 192 bytes for l2_cache/directory/governor. These are CPU engineering statements, not application cycles or an assertion of complete quota hardware qualification. Initial Core0e69 evidence and its newly found negative are retained; final selection is Core0ab3af3 only.
