# E023/E024 terminal follow-up — all four requested controls consumed

The bounded D notification adapter consumed **each new E current acceptance independently**, first E024 at 15:32:13 UTC and then E023 at 15:36:15 UTC, and exited normally after both. It did not restart a Goal or simulator, modify E's ledger/controller, or scan trace bodies. Each new raw log was observed once; previous snapshots were reused. The final exact E pair references and qualifications are in `accepted_event_1792510573934001466/`. The earlier three-control event and r2 two-control report remain frozen.

| Conv condition | Rows | Columns | Total | Total − S |
|---|---:|---:|---:|---:|
| S | 161236 | 131696 | 292932 | 0 |
| W_ONLY | 160844 | 130681 | 291525 | −1407 |
| S_COPY_FREE (diagnostic) | 163051 | 130620 | 293671 | +739 |
| F_MINUS_V | 162539 | 130924 | 293463 | +531 |
| F_MINUS_R | 160278 | 132154 | 292432 | −500 |
| F (original main) | 160984 | 130485 | 291469 | −1463 |

All named-kernel sums close exactly, with zero final residual. The four original main S/F pairs remain unchanged, interim four-pair GM stays **1.001679**, and original seven-input GM remains **UNKNOWN**. Diagnostic/control endpoints do not replace main F or enter that GM.

## New adverse diagnostic: copy-free is slower

E024 S_COPY_FREE is **739 cycles slower than S**: Rows +1815, Columns −1076. W_ONLY is 2146 cycles faster than S_COPY_FREE, with Rows −2207 and Columns +61. Thus W_ONLY's 1407/1463=96.172% recovery of the main net improvement must not be called a copy-saving fraction. Removing the modeled copy cost in the traditional finite organization does **not** reproduce W_ONLY's whole-program benefit in this experiment.

The exact frozen-source interpretation is important: `gpu-cache.h:2257–2260` exempts COPY_READ/COPY_WRITE physical services, and `ep-l2-ft-cache.inc:461–464` also bypasses the fixed copy-latch staging retry. This is broader than a port-contention-only diagnostic. Fixed finite static WB organization and other native services remain. It is neither a realizable hardware design nor a guaranteed monotonic performance upper bound. `COPY_FREE_SOURCE_BOUNDARY.json` binds numbered source excerpts to Core d010. This supplements the earlier “copy-service” shorthand without changing any frozen runtime/configuration.

Measured whole-program bank services fall from **9217033 to 8120936**, and copy-pipeline wait goes from **546865 to 0**, yet elapsed cycles rise. Logical copy reads and writes remain **546640 each**, versus 546865 each in S: the diagnostic exempts service and delay, it does not eliminate all logical copy events or preserve every microarchitectural event count. WB-space request-wait sum rises **848913→1016858**. Lower-read bytes fall slightly (**75504832→75503616**) and WB bytes fall (**69787264→69768640**). These observations are compatible with changed arrival/lifetime/backpressure under the finite static WB pool, but do not identify the 739 critical cycles. Existing per-kernel snapshots omit WB-space reason 0, so its per-kernel distribution remains **UNKNOWN**; no rescan is performed to fill it. Rows data-service wait falls (191987→131172) despite Rows taking 1815 more cycles. This is another direct counterexample to treating wait sums or service counts as program stalls.

## New RO conditional contrast: net advantage appears in Columns

E023 F_MINUS_R is **963 cycles slower than F**, but the complete scheme is **706 cycles slower in Rows and 1669 faster in Columns**. F's RO query/admission increments occur in Rows; F's Columns has zero new RO query/admission increments. RO is OFF in F_MINUS_R and its native RO records are absent, rather than measured zeros. The Columns improvement can include inherited state and V/queue effects; it is not a measured direct payoff from newly admitted Columns RO transactions.

F and F_MINUS_R both keep V and strict client/UID/generation retry matching. This is a valid **RO-enabled conditional net effect on the W+V background**, including query, allocation, retention and downstream timing interactions; it is not an isolated M or T contribution. F has **371495 avoided line allocations and zero successful Tag detach**. These counts do not divide the 963 saved cycles into mechanism contributions.

F_MINUS_R records 42 V direct responses (all Rows) versus F's 36 (32 Rows, 4 Columns), yet is slower overall. It has 8122142 bank services versus F's 8118075, 75504192 lower-read bytes versus F's 75502720, and 69832448 WB bytes versus F's 69826496. In Rows it has 193665 MissQ wait cycles versus F's observed zero but still executes **706 cycles faster**. In Columns it has more line-MSHR wait (195803 vs 150118) and same-address-WB wait (757814 vs 538426), but less MissQ wait (568443 vs 590686). These overlapping request/slice/reason observations cannot be added into 1669 elapsed cycles or used to select a unique bottleneck.

## Combined interpretation and remaining identification limits

The original first-two-control findings remain: W_ONLY saves 392+1015=1407 cycles, and F_MINUS_V costs 1555+439=1994 versus F. Complete F is only 56 cycles faster than W_ONLY, despite conditional advantages of 1994 over F_MINUS_V and 963 over F_MINUS_R. **1994+963 is not an additive V+RO cycle contribution.** W_ONLY uses weak role/id/write retry matching; all three V/RO-enabled conditions use the stronger rule because dirty V or RO is enabled. W_ONLY→F_MINUS_V and W_ONLY→F_MINUS_R consequently include an identity-rule change, as well as query/state effects. A2's frozen audit 04f255e4 supplies this source boundary; no actual first-UID divergence or new correctness failure has been established.

T/M four-corner inference is still incomplete: C00=F_MINUS_R=292432 and C11=F=291469 are accepted, while WV_T and WV_M are pending. The signed interaction remains **UNKNOWN**. All four full-F successful Tag-detach totals stay zero. DWT's separate V/RO effects and SAD's zero-copy prefix remain unresolved; no unapproved DWT F_MINUS_R or SAD W_ONLY is inferred or requested.

The accompanying English candidates, six-condition table and figure remain separate from the EN-v20 mother. No new control, input, instrumentation, native test or full-application run is requested. E continues owning all execution and qualification.
