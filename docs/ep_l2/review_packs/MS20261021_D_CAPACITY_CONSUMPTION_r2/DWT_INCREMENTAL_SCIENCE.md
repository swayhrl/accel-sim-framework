# DWT accepted event consumed immediately: fourth capacity pair

After D published the first threeCONSUMED pairs atf93add1ef2e22e5f8b04e1dce7de5b7ddfd15a80, E advanced toc6dfbecc9ffcd1eb661c6e61657f69326d8eec5c with `CAPACITY_DIAGNOSTIC_dwt2d_OFF_ON_NEW_RUNTIME`. D consumed this new pair immediately while neutral workload preparation continued, without waiting for Conv or restarting an adapter/simulator.

DWT OFF E043_c96ede71 / ON E044_4c4350db are **166,519 / 157,034 cycles**,148,684,429 instructions each, same new binary93a9/Corefe7e/Framework9dd. SpeedupOFF/ON−1 is **6.040093%**, while ON cycle reduction is5.696047% using a different denominator. Exact source/config/input/run-key/receipt/qualification identities are in `accepted_snapshot_04/EXACT_ACCEPTED_IDENTITIES.json`; both newly consumed raw logs are complete E-accepted endpoints, not partial running output.

| Kernel | OFF | ON | ON−OFF |
|---|---:|---:|---:|
| K1 |22169|17866|**−4303**|
| K2 |25759|25047|−712|
| K3 |12262|12258|−4|
| K4 |9075|9074|−1|
| K5 |28101|25127|**−2974**|
| K6 |12260|12258|−2|
| K7 |9074|9074|0|
| K8 |26496|25000|**−1496**|
| K9 |12249|12255|+6|
| K10 |9074|9075|+1|
| Residual |0|0|0|
| Total |166519|157034|**−9485**|

K1/K5/K8 save8773 cycles; the remaining net712 comes fromK2 while K3/K4/K6/K9/K10 differences cancel. Matching named kernels and launchUIDs plus explicit final residual close exactly to accepted program time. These are elapsed stage differences, not sums of waits.

Measured whole-application OFF→ON: physical grants2522456→0, copy reads/writes163840 each→0, lower reads388844→0, lower read bytes12443008→0, lower WB bytes20971520→0. K1/K2/K5/K8 lower reads48688/78012/131072/131072 all become0; their WB bytes5688192/5196800/5892224/4194304 become0. This is consistent with the enlarged native residency under the existing host-prefill policy and free data service; it is **not** a forced-hit mode or capacity-only/bank-only/W-only counterfactual. COPY_FREE remainsOFF: zero actual copy activity reflects no dirty-victim replacement, not removal of the fixed-latch rule.

OFF request-cycle observations: WAD41770, WB-space30282, same-addressWB24436, data93039, copy163840; ON reports0 for these observer reasons. They overlap and cannot be added or assigned as9485 causal stall cycles. ON still executes the full program and finite residual completion/data dependencies. No unique critical request/warp path is available in these snapshots.

E's ON classification remains **UNKNOWN**: maximum covered highwater/conservative bound5.2734375%, no reported binding resource, covered successful Tag replacements0, but complete MissQ full-check coverage remains missing. The valid complete-input performance is not upgraded to a near-unbounded or hardware-bound claim.

The current capacity table is now CFD79093/79742(−0.813875%),Vector73696/42788(+72.235206%),SAD110773/110634(+0.125639%),DWT166519/157034(+6.040093%). These four pairs are diagnostic only; **complete-five diagnostic GM remainsUNKNOWN** and Conv's accepted OFF alone is not a pair. Original main61 five-MAIN GM0.997733135 and original-sevenMAIN GMUNKNOWN remain unchanged. All first-three observations and unfavorable CFD result are preserved inr1.

Six prior endpoint observations were reused after their manifests/raw hashes matched; only E043/E044 were newly decoded. The helper now also projects the original E canonical current accepted pointers under a shared read lock: withdrawal or repointing holds only the affected pair, while old publications remain. Three new offline withdrawal/repointing checks plus five missing-counter checks pass; no E gate is reexecuted and no second acceptor is introduced. E remains the sole qualifier and application owner. DWT is markedCONSUMED in this pack and will be delivered after exact remote readback.

Paper paragraph candidate: “A fourth accepted joint diagnostic reduces DWT runtime from166,519 to157,034 cycles (6.04% OFF/ON speedup). Most savings occur in kernels1,5 and8, accompanied by the elimination of timed lower reads and writebacks under the existing host-prefill policy. This contrast jointly changes capacity/residency and data service, and does not identify their independent critical-path shares. Missing MissQ check coverage leaves the ON near-unbounded classification unknown.”
