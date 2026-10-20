# Conv: first two accepted controls

Consumed requested E2 `5d1c1d5169170afc7bb9847d21cecf0a2af070d6` and its latest read-only descendant `a2c7b23ef` (exact SHA in evidence index). E021 W_ONLY and E022 F_MINUS_V are CURRENT_ACCEPTED; E023 F_MINUS_R and E024 S_COPY_FREE remain under E's active controller. Cumulative starts **24/40**, not reset. main61, full Conv input and original S/F anchors are unchanged. No simulation, trace scan, acceptance, production modification or controller action by D.

## Actual measurements

| Conv condition | Rows | Columns | Total cycles | Saved vs S |
|---|---:|---:|---:|---:|
| S / E010 | 161236 | 131696 | 292932 | 0 |
| W_ONLY / E021 | 160844 | 130681 | 291525 | 1407 |
| F / E009 revalidated | 160984 | 130485 | 291469 | 1463 |
| F_MINUS_V / E022 | 162539 | 130924 | 293463 | −531 |

All four have zero final residual after the two reported named-kernel durations. Exact qualified/config/input/run-key/receipt identities are in the snapshot CSVs; E009 uses its **revalidated accepted receipt**, not its original failed terminal classification.

W_ONLY reproduces **1407/1463 = 96.172%** of the main F-versus-S **net cycle improvement**. Its savings are 392 Rows cycles plus 1015 Columns cycles. This is a descriptive ratio of two complete-program differences, **not the fraction of performance caused by copies**. W changes finite payload allocation, WB organization and queue/arrival state as well as eliminating copy service. S→W removes 546865 copy reads and 546865 copy writes, but its total bank-service reduction is 1092963 (copy operations total 1093730), and line-MSHR/MissQ wait aggregates increase despite faster execution. The accepted S_COPY_FREE diagnostic is still needed to test copy-service removal in the traditional organization; it will not by itself isolate every W structural interaction.

F improves on W_ONLY by just **56 cycles**, but this combines **Rows +140** (F slower) and **Columns −196** (F faster). Therefore near-equal whole-program times do not show that V/RO have no timing effects.

F_MINUS_V is **1994 cycles slower than F**: **1555 Rows (77.984%)** and **439 Columns (22.016%)**. F is 0.684% faster than F_MINUS_V using the latter as the baseline. On the W-only background, F_MINUS_V costs 1938 cycles, while re-enabling V in the RO-enabled configuration saves 1994. The resulting −56 is a telescoping identity between observed endpoints; **1938 and −1994 are conditional net differences, not independent module costs**.

## Mechanism evidence and bounded explanations

| Actual terminal observation | F | F_MINUS_V | F_MINUS_V − F |
|---|---:|---:|---:|
| Physical bank services | 8118075 | 8121829 | +3754 |
| Lower read packets / bytes | 2359460 / 75502720 | 2359496 / 75503872 | +36 / +1152 |
| Lower WB bytes | 69826496 | 69758848 | −67648 |
| V direct read responses | 36 (32 Rows, 4 Columns) | OFF; native counter absent | Not a measured delta |
| RO admissions | 1251551 | 1259956 | +8405 |
| RO transactions / avoided line allocations | 371495 | 357819 | −13676 |
| RO merges | 880056 | 902137 | +22081 |
| RO queries | 1251627 | 1260007 | +8380 |
| Successful Tag detach | 0 | 0 | 0 |
| Concurrent duplicate RO lower sectors | 0 | 0 | 0 |

All RO admission/transaction/merge/query snapshot increments occur in Rows in both configurations. F's 589923 Rows V queries coexist with a 1555-cycle advantage over F_MINUS_V, rather than a linear query penalty. Rows has only 3447 fewer bank services and 1024 fewer lower-read bytes in F; F_MINUS_V introduces 12683 MissQ request-wait cycles versus F's observed zero and changes RO admission/merge organization. Data-service wait is actually smaller without V (178273 vs 181130), showing why a single wait counter cannot stand in for elapsed time.

Columns has **zero new RO admission/query increments** in either condition; the 439-cycle regression without V coexists with 4 extra lower reads (128 B), 307 extra bank services, fewer WB bytes, and no V query charge. F_MINUS_V nevertheless has more line-MSHR wait (192706 vs 150118), MissQ wait (636800 vs 590686), and same-address-WB wait (780296 vs 538426). These are overlapping **request-wait snapshot increments**, not a sum of critical GPU stalls. Prior Rows state and current V retention/promotion/arrival effects remain possible. Total V promotions are 1152, all in Columns; this establishes state movement, not 1152 performance-critical reuse events.

**Hypotheses, not established causes:** (H1) paid V-path pacing changes Rows admission/merge overlap and downstream queue timing; the observed transaction/merge and MissQ changes are compatible but do not locate the first critical request. (H2) V retention/promotion and inherited Rows state change Columns MSHR/WB scheduling despite little read-traffic change; fewer WB bytes without V do not guarantee earlier key completions. (H3) direct victim responses explain some service changes, but total event counts do not identify how many of the 1994 cycles they cause. A decisive direct-read account would require matching response UID/dependency timing, absent from current logs. Existing approved F_MINUS_R and T/M corners test adjacent conditional backgrounds; no new workload, instrumentation or experiment is requested here.

## Frozen-source boundary from A2 04f255e4

At Core d010, `gpu-cache.h:2882,2888` enables extended bank retry identity when dirty V **or RO requested** is set. `ep-l2-tvd-bank-identity.h:10–15` always compares role/id/write, and additionally client/token(UID)/generation when enabled. Release cancels corresponding pending/granted identities when this rule is active (`gpu-cache.h:2519`).

| Comparison | Matching rule | Identification limit |
|---|---|---|
| S → W_ONLY (also S → S_COPY_FREE) | Weak → weak | Net W organization or traditional copy-free diagnostic; not an independent full-F mechanism decomposition |
| W_ONLY → F_MINUS_V / F | Weak → strict | Includes identity semantics with RO/V/query/allocation changes; not isolated RO, V or copy gain |
| F_MINUS_V → F | Strict → strict, RO requested in both | V-enabled conditional net effect at fixed W+RO background; identity activation itself does not switch, but timing/state effects remain |
| F_MINUS_R → F; WV four corners | Strict throughout, dirty V retained | RO/T/M conditional net effects, pending exact accepted endpoints |

This difference can matter before any WB or successful V/RO response. It is **source-derived**, not evidence that a particular UID collision happened or that weak matching caused a data error. A2/E2 have not declared a new correctness failure. Do not invalidate accepted endpoints or invent a numerical identity contribution from this review.

A2 also refines the old landing interpretation: the blocker bitmap is computed **before same-bank reclaim**. If reclaim succeeds but a later P1/other guard fails, a pre-reclaim landing bit may still be reported. Thus landing wait counts are not proof of final no-slot refusals or exclusive bank-port contention. Preserve this qualification for the earlier DWT discussion.

## Main-result and paper boundary

The original four full-F pairs and interim GM **1.001679** remain unchanged; original seven-application GM remains **UNKNOWN**. Controls do not replace main F or enter the main GM. SAD's zero-copy prefix remains unexplained; no SAD W_ONLY or DWT F_MINUS_R is approved by this analysis. The EN-v20 mother is untouched. See the separate English candidates and paper figure/table. E023/E024 enter only after E's explicit current acceptance; their live progress is not a result.
