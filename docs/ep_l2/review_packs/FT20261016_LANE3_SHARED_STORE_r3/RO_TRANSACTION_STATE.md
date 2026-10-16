# Executable shared-store boundary

| Step | Real shared-store binding |
|---|---|
| Landing | Caller preview_free(RO, tag_bank), then reserve(...RO, RO_FILL_ATTACHED); no second allocator |
| Admit | Same D512 free-list plus pin(handle); existing clean resident sector-miss landing can transfer to RO only when it has no unrelated pending fill |
| Lower accept | Actual callback adds only newly accepted issued sectors to common pending mask |
| Return | accept_return borrows existing return-packet version tokens for one callback; request(RO_FILL_WRITE) must grant before mark_sector_ready; denied return stays in its original queue |
| Attach completion | Matching Tag callback sees sector readiness; all required data ready transfers primary ownership to RESIDENT without losing pending requester pins |
| Detach | Only single-request, no-reuse, still-pending Tag; visibility callback removes current Tag, common RO role becomes RO_FILL_DETACHED |
| Response | Common RO_RESPONSE_READ bank service plus version observer, same-cycle successful enqueue commit; backpressure rereads and keeps landing pin |
| Detached retirement | Every issued sector ready and every descriptor committed; unpin then release exact handle |

Tag lookup/visibility callbacks in the new store test are a small reference adapter, not the final simulator tag_array binding. Sector-version tokens are validation labels as in the Lane-1 candidate; they are not reconstructed SASS byte values. The earlier r2 seven-group byte reference and all certificates remain available separately. No extra return/response RAM is created by this adapter; its only temporary data carrier is a borrowed packet pointer, cleared after each callback.

RO roles, pins, ready/pending masks and owner identities are included in the common store. New RO operation counters are observation only; FREE+RESIDENT+BYPASS+WB+RO equals the configured physical budget.
