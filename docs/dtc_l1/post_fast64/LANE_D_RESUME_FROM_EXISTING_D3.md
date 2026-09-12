# Lane D resume from existing D3 qualification

Status: **RESUME AUTHORITY — do not discard existing D3 evidence**

The observer branch already contains a completed Core95 qualification at Framework commit `03ef14b1b7476c5edc15ab8063fd3ba2251171d6` using observer Core `f2c28217be36c9756afab3d937d6aaf35f23cd7b`. NN/Btree IO/OO telemetry-off/on comparisons passed exact equality for all pre-existing compact scientific counters, cycles/instructions, accounting and terminal observer drain.

That D3 PASS remains valid for the telemetry families implemented at that commit: alloc-to-ready latency, pending-Tag eviction, IO pending-eviction-to-response latency, OO deferred-eviction-to-final-reclaim latency, OO duplicate-after-eviction and observer live-record drain.

The reviewed A/B/C follow-up adds one new required observer family not covered by the old D3 PASS: exact time-integrated physical/inflight exposure (`observer_sample_sm_cycles`, `physical_allocated_line_cycles`, `physical_full_sm_cycles`, `inflight_request_cycles`).

Therefore:

1. do **not** rerun/reimplement the already-qualified observer families without a concrete defect;
2. source-audit and add only the missing occupancy/inflight integral family;
3. because that changes observer code/runtime, perform a focused `D3B_OCCUPANCY_EXTENSION_EQUIVALENCE_PASS` before D4/D5 data from the extended binary are scientifically retained;
4. reuse the existing D3 fixtures/comparator and at minimum requalify NN IO/OO and Btree IO/OO; a Base control is needed only if common stats/plumbing changes;
5. exact pre-existing simulated output equality remains mandatory; only the newly added occupancy/inflight counters may be additional;
6. once D3B passes, continue directly to D4 physical telemetry and D5 OO duplicate waves under `LANE_D_OBSERVER_EXECUTION_HANDOFF.md`.

The older conclusion in `OBSERVER_EQUIVALENCE_REPORT.md` that D4/D5 were not required described the previous bounded question. It is superseded operationally by the researcher's reviewed decision and the newer Lane-D execution handoff: D4/D5 are now authorized post-FAST64 exploratory work. The old report remains valid historical evidence and must not be rewritten.
