# Overflow fallback feasibility — STOP_RAW_RETENTION_CAPACITY

Candidate design, NOT installed in production:

1. IDLE: fully admitted, frontend-ready, older-same-warp fence clear; compute S.
2. S<=128: reserve free4KiB collector bank, use original4-sector absolute-cycle
   quota; completed collector promotes only into an empty WB stage. Keep data
   and Refs on RFU denial; success alone releases the original Ref/PIB ownership.
3. S>128: stop claiming new small owners; existing finite stages naturally drain
   subject to ordinary eventual RFU grants. Then enter SERIAL_FALLBACK.
4. SERIAL_FALLBACK must still collect all S before one successful WB on a later
   cycle. Both proposed banks are empty, but total capacity is only256 sectors.
5. For S>256, either reject before collection, or fill256 and enter
   CAPACITY_STALL with sectors_left=S-256>0. Neither path has a legal terminal
   transition under the authorized contract. Rejecting a valid admitted input
   is fail-closed diagnostics, not a working finite-progress fallback.

Proof: R is retained sectors. Until successful WB, R cannot decrease; before WB,
all S sectors must have been collected, hence R=S. Bound R<=256 is incompatible
with S>256. At R=256 and sectors_left>0, further collect overflows, WB is disabled,
and no other owner remains to drain. Every permissible wait preserves this state.
This is an invariant argument, not an inference from a watchdog timeout. The CPU
witness exercises the unchanged service_entry and also tests the claim assertion
for128/129,256/257 and256/512 in forked children; it does not install a stall in
production or run an indefinitely hanging job.

For128<S<=256, a two-bank serial owner is conceivable but requires reviewed
cross-bank cursor/role/print semantics. It does not solve larger inputs and is
not partially enabled. The single-bank128-sector positive and both-bank denial/
later-drain test are resource-component evidence only, not compact LDST PASS.

Not authorized remedies: hide an80KiB serial output buffer; release Ref while
waiting; overwrite a live bank; truncate masks; mark partial data complete;
stream architectural WB before collection done; re-read physical sectors with
free ports; add a delay or use >=. No such remedy is made. A separately reviewed
output extraction/assembly path or explicitly larger bounded fallback resource
is required before implementation can resume.
