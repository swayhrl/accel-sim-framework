# ChatGPT review entry - EP-L2 Main V2

Snapshot: 2026-11-03T15:15:56.243599+08:00. This is a review checkpoint, not final Stencil performance. Eight newly authorized models from the preceding W2/T6 batch are CLOSED_ACCEPTED, archived on genuine164 and independently restored twice. Four older accepted S/WV reference points are reused for matched W decomposition. Both new Stencil points are running. They are not accepted results and have no final cycles in this packet. No model was started or changed for this publication.

## Read first

1. SOURCE_SCOPE_AND_STATUS.json and RUN_STATUS.csv: populations, separate Source5 lineages, live status and scope.
2. analysis/PRELIMINARY_ANALYSIS_AND_NEXT_DECISION.md: measured primary outcomes, per-kernel tradeoffs, PROVEN/LIKELY/UNKNOWN boundaries. Its original pre-NI wording is superseded only for NI completion by the closeout evidence below; its measured primary numbers remain unchanged.
3. COMPLETED_EIGHT_RESULTS.json and analysis/MATCHED_WV_COMPARISONS.json: exact mode comparisons, no cross-binary T arm and no combined GM.
4. evidence/completed_closeout/MAIN_NI_OFFLINE_CLOSEOUT_ADDENDUM.json and evidence/NI_RESULTS/: all3 actual same-arm NI comparisons PASS.
5. STENCIL_LIVE_SNAPSHOT.json and evidence/stencil_qualification/ACTIVATION_AND_HANDOFF_REPORT.md: the current two-point continuation and exact boundaries.

## Findings ready for review

Conv16x8 uses the same new Core1e07b263ca0879798387d2a712914a914f298775 / ELF54c3fbba9bb152d1a26539cccb617ac4a3368547a06509f427a202eeda6d8505 in all three arms. F_MINUS_T/LEGACY_F/CORRECTED_F cycles are362791/367152/364463. The sum of final64slice detached counters is0/237/360. Corrected-F reduces cycles0.7324%versus Legacy-F but increases cycles0.4609%versus F_MINUS_T. Its Rows kernel is654cycles slower than Legacy-F, Columns3308faster, final residual35lower. These localizations do not assign those deltas to individual detaches. The corrected policy pays a shared set-eligibility query cost:2954issued and2954one-cycle slice-exposures, not2954exclusive critical-path GPUcycles.

GEMM Source78 S/W_ONLY/WV cycles are558588/558957/550642. FWT S/W_ONLY/WV cycles are181827/181635/178951. W_ONLY is almost neutral in these two inputs; the V-enabled package reduces cycles about1.48%versus W_ONLY in each. W_ONLY includes pooling and in-place WB, so it is not a pure free-copy counterfactual. V includes allocation, retention, lookup and service. Completed DRAM write reduction does not prove stores permanently disappear: the commandlist+hardware-drain contract does not flush all dirty resident/Victim data.

All3 OFF/ON NI pairs now have equal cycles, instructions, CTA, real kernel counts, hardware drain and checked model/application compact projections. The existing pure comparator and criteria were unchanged. An automatic invocation had omitted importing json and recorded NI_ANALYSIS_HOLD before doing the comparison. Main preserved those original failures and the original executor finish record, then completed comparisons offline using accepted artifacts. The old EXECUTOR_FINISHED status FINITE_SCOPE_TERMINAL_OR_REVIEW_HOLD is chronological evidence, superseded for this resolved analysis error by MAIN_NI_OFFLINE_CLOSEOUT_ADDENDUM. It is not an active model or protocol blockage. No model was retried for that repair.

Stencil uses unchanged accepted Source78 ELF,64slice32set8way,dram_latency100,1168physical Payload slots per slice, descriptor512/WAD128/ordinaryMSHR128/P1, unchanged clocks/queues and282 effective options. W_ONLY/WV both have M=T=OFF and no RO certificate. The exact reused S anchor has5242939cycles,2193446000instructions,6400CTA and100kernels. Both new treatments must complete all100kernels and drain before performance can be compared. Current budget2 is consumed by those two active runs. Scan remains conditional and has not been started.

## Questions for an independent reviewer

- Are W/S, WV/W and the three T contrasts interpreted within their exact Source/input/geometry/config populations? Flag any inference attributing a whole package to one operation or comparing old/new ELF T arms.
- Does the P1 implementation preserve RO owner/generation/pin/sector/late-fill and repeated-preview protections, and does its explicit query-port/latency model support the claimed scope? Distinguish the demonstrated correction from unproven PPA/timing closure.
- Are the first-block/request-wait, bank, lower-queue and DRAM counters being used with correct populations and clock domains? Their slice exposures overlap and cannot be added as exclusive GPU stalls. Peak occupancy alone is not causal saturation.
- Is the present recommendation justified: finish accepted NI/joint analysis, use Stencil W/WV to decompose the strongest positive, retain Scan as a later negative control, and defer retention-policy changes until that decomposition?
- Identify actual P0/P1 defects or unsupported claims, and separate them from valid resource costs, P2 policy limits and P3 hypotheses. Do not infer T benefit from nonzero detach or classify partial Stencil progress as accepted performance.

## Evidence navigation

All new accepted point records and their genuine164 archive/restore receipts are under evidence/accepted_points and evidence/archive_receipts. Four reused accepted references are under evidence/reused_reference_points. The selected compact metric projection and kernel arithmetic are under analysis. Full raw, Trace bodies and binary bulk are kept on genuine164; archive paths and full SHA appear in the receipts. Exact Stencil specs include all282 expected options, source/input pins and native/Host eligibility. SNAPSHOT_MANIFEST.json records copied-byte SHA and original paths; mutable live status is explicitly an as-of snapshot.

Additional existing engineering reports are in the parent directory agent_d/ORDINARY_RO_DETACH_P1_CORRECTION_QUALIFICATION_V2.md and agent_b/W_ONLY_FORMAL_QUALIFICATION_V2.md. Code review anchors:
- https://github.com/swayhrl/gpgpu-sim/tree/1e07b263ca0879798387d2a712914a914f298775/src/gpgpu-sim
- https://github.com/swayhrl/gpgpu-sim/tree/78f4b59e865b136eede74df74c44c210f5b4ca04/src/gpgpu-sim

Source KEEP, original histories/failures and foreign resource guarantees remain unchanged. Numerical application output, strict demand-unique NEW, later UID completion chain, ordered request trace NI and physical PPA retain their documented UNKNOWN/NOT_INSTRUMENTED boundaries.
