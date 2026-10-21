# CONSUMED: three accepted new-binary capacity/data-service pairs

E authority `0f7394855ade7f9c2e970acd16246003728bb3f8`, pack `MS20261021_E2_CAPACITY_DIAGNOSTIC_r1`. D has now consumed the three CURRENT_ACCEPTED pairs, separately from E's delivery. Exact pointers and endpoint SHA/config/input/run-key/qualification identities are in `accepted_snapshot_03/EXACT_ACCEPTED_IDENTITIES.json`; `CONSUMED.json` names each pair and its E authority. This projection uses the existing D acceptance-pointer, snapshot and mechanism readers; no E native qualification is rerun.

| Input | OFF | ON | ON−OFF | OFF/ON−1 | ON class |
|---|---:|---:|---:|---:|---|
| CFD | 79,093 | 79,742 | +649 | **−0.813875%** | UNKNOWN |
| Vector | 73,696 | 42,788 | −30,908 | **+72.235206%** | UNKNOWN |
| SAD | 110,773 | 110,634 | −139 | **+0.125639%** | UNKNOWN |

All six endpoints use binarySHA256 `93a9f28ddb9c0c9ceb93409764a5664666589477778fe5d41d90a179704706eb`, Core `fe7e1fc1e8f40b5c4c6d0f232a528483891389c5`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`. Each pair has its own complete input and equal instruction totals. CFD uses the exact E parser-recovery accepted receipts; original E037/E038 failed decoder receipts remain untouched and are not substituted for accepted pointers. There is no simulator rerun for that recovery.

The three-diagnostic-subset GM is1.195930804×, with the membership explicitly CFD/Vector/SAD; **complete-five diagnostic GM UNKNOWN**. These are the same original applications, not three new workload samples. Original main61 five-MAIN S/F GM remains0.997733135×, and original-seven MAIN GM UNKNOWN. Neither this aggregate nor an ON endpoint replaces MAIN F.

## Where elapsed time changes

- **CFD:** K1/K2/K3 unchanged7056/7055/7031; K4 9998→10003(+5); K5 flux47953→48597(**+644**); residual0→0. The flux stage contributes99.23% of the signed total+649. K4 lower reads remain12144; K5 reads fall200164→194304, and WB bytes3983744→0. K5 copy reads/writes31123 each disappear; observed data-service waits42294→0 and same-WB waits disappear, yet elapsed time increases. This establishes an unfavorable joint conditional effect in flux; it does not identify649 cycles of any one queue or bank stall. Unchanged ROP/completion and downstream scheduling/arrival-history effects are plausible hypotheses, not a proven critical path. Zero enlarged-resource waits does not remove DRAM/ROP/dependency timing.
- **Vector:** named VecAdd73557→42788(**−30769**), residual139→0(**−139**), net−30908. OFF lower reads1000000/32000000B and WB12872704B become0/0; copy reads/writes100568 each become0, WB created/lower-accepted/completed100568 each become0. The ON final resident count375000 fits within the enlarged total resident geometry; no successful valid-victim Tag replacement is observed in any of the64 slices. Source-derived: host-prefill installs actual native Tag/payload/ready-sector state using the configured larger geometry, so retaining the HtoD-initialized footprint is a supported explanation for the eliminated timed lower traffic. It is not a forced-hit configuration. Existing complete snapshots do not provide an intervention isolating host-prefill residency, changed set geometry, capacity and free data service; **72.24% is not the contribution of W, V, T, M or banks alone**. The measured scope includes the existing host initialization policy, not a cold-cache experiment or proof that the GPU performs no writes.
- **SAD:** K1 84641→84641 and K2 15076→15076 unchanged; K3 10957→10917(**−40**); residual99→0(**−99**), net−139. Lower reads remain399/12768B; all508800B lower-WB traffic and3975 copy read/write events disappear in K3. No zero-copy-prefix speedup is reproduced in K1 here. This joint diagnostic does not solve the prior main61 S/F prefix effect, and its final residual is not asserted to be entirely DRAM drain.

## Measured terminal mechanism counts

| Quantity | CFD OFF→ON | Vector OFF→ON | SAD OFF→ON |
|---|---|---|---|
| Physical bank grants | 1638275→0 | 2801704→0 | 483611→0 |
| Logical copy reads (writes same count) | 31123→0 | 100568→0 | 3975→0 |
| Lower read packets | 212308→206448 | 1000000→0 | 399→399 |
| Lower read bytes | 6793856→6606336 | 32000000→0 | 12768→12768 |
| Lower WB bytes | 3983744→0 | 12872704→0 | 508800→0 |
| ANY-first-block-to-admission request observations | 95772→0 | 1762049→0 | 6218→0 |
| Copy wait request-cycles | 31123→0 | 100568→0 | 3975→0 |
| Data-service wait request-cycles | 42977→0 | 84555→0 | 2206→0 |
| MissQ wait request-cycles | 0→0 | 1131061→0 | 0→0 |

V/RO are disabled on both sides; absent V/RO metric families remainUNKNOWN, rather than new measured zeros or inherited main61 F events. Physical grants0 means exempted service in a diagnostic with `hardware_P1_throughput_eligible=false`, not free hardware throughput. Logical copy0 reflects no dirty-victim replacements in these ON runs, not activation of COPY_FREE: fixed copy-latch semantics remain if a copy is actually needed. Existing data/free/native observations do not establish that every possible L2 stall vanished. Request-wait sums overlap across slices/requests/reasons and never form a GPU elapsed-time budget.

## UNKNOWN is retained, not upgraded

All three ON results are E-classified **UNKNOWN**. No binding enlarged resource is identified in the accepted classification, and the maximum covered highwater/conservative-bound fractions are CFD2.396%, Vector8.945%, SAD1.669%. All64 successful Tag valid-victim replacement counters are covered and zero, including timed clean, timed dirty and host-prefill replacements. Nevertheless **MissQ complete capacity/full-check coverage is missing on all64 slices**. Its reported peak/refusal zero does not fill that coverage gap. This is not a failed application; it is an unproved near-unbounded classification. D neither reruns qualification nor relabels it as near-unbounded.

Only the enlarged vector is in scope. Native ROP remains explicitly outside that vector; ON ROP per-slice highwaters are actual observations, not evidence of unlimited completion resources. Index extension and host-prefill residency differ with native capacity geometry. Thus this is a **joint large-capacity/free-data-service diagnostic**, not a hardware upper bound, capacity-only marginal effect or complete removal of the memory hierarchy.

## Incremental interfaces and preservation

`capacity_incremental.py --e-commit SHA --out NEW_REVISION --cache PREVIOUS_SNAPSHOT` uses E's frozen accepted-pair declarations, exact accepted pointers and unchanged existing D tools. It never accepts a result independently, reads an active raw, polls in the background, writes the registry or starts a native/application process. On a later E publication it consumes only CURRENT_ACCEPTED declarations present there, reuses exact hash-bound observations and keeps all previous revisions. A withdrawn/repointed declaration cannot silently reuse a different endpoint. No old notification adapter is restarted.

Six completed accepted raw logs were decoded once; the OFF schema gaps encountered during projection are retained as D-only failed preparatory snapshots01/02 and repaired in03. They are not new E failures or simulation attempts. Missing OFF highwaters remainUNKNOWN. Five focused offline counter-coverage regressions pass. Each named-kernel UID sequence matches and named deltas plus residual close exactly to accepted program cycles. DWT ON active raw and Conv ON absent/nonaccepted data are unread. Future delivery can update independently; no five-pair wait gate is added.

Three measured-data PDF/PNG figures and LaTeX/CSV inputs accompany this brief. English text is a proposal only; no paper mother is overwritten. All prior main61 negatives, original failed receipts, FWT INCOMPLETE and Btree HOLD are preserved.
