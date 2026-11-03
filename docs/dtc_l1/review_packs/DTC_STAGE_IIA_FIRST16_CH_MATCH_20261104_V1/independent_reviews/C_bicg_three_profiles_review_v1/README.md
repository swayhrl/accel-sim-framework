# Independent BICG six-source interim review

Decision: **PASS_WITH_EXISTING_SOURCE_AND_COUNTER_SCOPE_LIMITS**. All56 check groups pass for B_bicg_three_profiles_v1, manifest `86f42a916bfed26773e559f87e4556ab0504a5efb95d07c49a1e940346a165ed`.

The six closed RESULT/raw/natural-exit identities and fixed build/input match. Both new CH results pass strict, full21-entry native restore and genuine164 archive-chunk SHA checks. The original four-source packet remains unchanged; its historical OO-prefixed CH diagnostic label is not reused as an OO measurement.

| Design | P0 | F128 | F256 cycles |
| --- | --- | --- | --- |
| CH | 26298698 | 24464891 | 24651923 |
| DH | 28685812 | 29210480 | 28883488 |

BICG actual K1 is bicg_kernel1 with74285056 active-thread instructions; K2 is bicg_kernel2 with71380992. This order differs from ATAX. K1 cycles remain exactly1749396 for CH and1655347 for DH across all three profiles. Every total cycle change occurs in K2. F256 saves DH326992 cycles relative to F128, but remains197676 cycles worse than P0 and17.1653% more cycles than matched CH. Neither F profile improves DTC relative to CH versus P0.

All consumed additive raw snapshots and explicit-endpoint intervals were rechecked, with20-controller read/write atoms and GLOBAL32B sectors kept distinct. Means/gauges/peaks are not differenced. Missing positive-only reasons remain unavailable. Direct F256-versus-F128 tables match the same explicit fields; these completion-print intervals are not intrinsic request-origin attribution.

DH F256 versus F128 creates more lower requests and accepted L2 read sectors, issues496700 fewer DRAM read atoms but388 more write atoms, and increases L2 retries151329 plus ICNT admission-block events960145. Read entry-capacity failures increase159204818 to159372674. CH F256 has more read traffic/retries but fewer writes. Thus neither universally lower traffic nor universally fewer retries explains DH recovery. Event counts are not occupancy, critical-path durations or a guarantee that more MSHR entries improve performance.

Typed frontend domains remain CH active common PIB256 versus DH active OO PIB128. Generic DH PIB8 does not set OO admission; unprinted OO pressure fields remain null. Fixed FR-FCFS expansion couples shared credits255/319/447. Cross-design L1/Tag/queues/timing/area differences remain disclosed.

Recovered candidate source maps K1 to s=A^T*r and K2 to q=A*p, with separate output vectors rather than an ATAX-style tmp edge. This is candidate-source evidence; captureELF/numeric linkage remains unproven. It does not upgrade the frozen input to native full-application or numerical certification. Static address overlap is not a measured hit/merge mechanism.

The report keeps facts, associations and hypotheses separate. Printed DH MRQ rises across F despite recovery relative to F128; no reduced average DRAM waiting or isolated queue/credit cause is established. A literal wording check was corrected from not occupancy to the report wording neither occupancy before freeze; no scientific source changed.

This is one-program six-source interim review, not all16 terminal acceptance or authorization for48/new experiments. No model, source, owner, registration, old packet, history or v0.23 manuscript was changed. REVIEW.json carries paths, hashes and all checks; independent_audit.py reproduces the read-only audit.
