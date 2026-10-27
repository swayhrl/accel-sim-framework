# DTC-MAIN current progress review V3

Snapshot: 2026-10-28T01:04:18.363937+08:00. **240/350 accepted = 234 new strict/archive/native-restore PASS + 6 exact historical P0 references. 46 actual live models, 63 unstarted grants, one spent engineering failure without accepted cycles. This is not a completed scientific stage.**

## Read first

- [All 350 cells](ALL_350_CELLS.csv.txt): program, suite, full input SHA, design/profile, exact cohort, status, cycles only when accepted, UUID and source SHA.
- [Performance and fixed-population statistics](PERFORMANCE.json): per-input values, paired profile GM and an explicitly separate fixed-all-profile common population. Missing values are null. No per-program best-of construction. Non-P0 CH remains missing; do not infer a new relative DTC advantage or a final uniform winner.
- [Actual status](STATUS.json), [request grant/consumption](snapshot/REQUEST_STATE.json), source and member manifests provide path/SHA provenance. Raw RESULT snapshots are included. Large traces/logs/binaries remain on164/native stores.

## Immediate execution status and memory

The sole existing owner PID1498278 and executor continue; the new-admission gate currently says `ENGINEERING_ADMISSION_HOLD_JSON_IO`. Healthy already-running models were not stopped. The direct gate reason is a confirmed shared-JSON publication engineering defect, **not memory exhaustion**. One scan DH-M16 run is spent engineering evidence, not accepted or automatically retried. Concurrent truncated PID/map JSON is strongly supported by exact parse-offset reproduction and timing, but the original exception did not capture the unique pathname. Do not overstate that causal attribution.

Host MemAvailable is 110.16GiB; cgroup current 160.04GiB /256GiB, effective headroom including eligible clean file-cache credit 111.49GiB. These quantities differ. A read-only observation at 00:59 CST measured 113.78GiB model RSS and59.66GiB reserved future growth, admission budget84.03GiB and slack24.37GiB. Thus free100GiB is not all uncommitted. Cgroup OOM counters and current PSI averages were zero. Native free space is 43.37GiB; bulk result archives use true164.

Padding overhead was already reduced, after strict actual mergeSort DH-F256 pilot (111917cycles, natural rc0, base+extra strict,164 archive and native restore), for the registered initial344 future identities. This does not lower historical peakRSS. Large-job aging avoids repeatedly filling memory with small jobs before large jobs qualify. Its actual activation and CPU stale-binding repair are included. These changes preserve scientific configurations, input identities, spent UUIDs and same sole owner.

Pausing a model does not release its existing RSS. It can arrest further growth but cannot turn that RSS into new capacity. Current supervisors reject stale progress/resource samples after about30seconds; SIGSTOP without a separately qualified pause-aware contract risks invalidation/termination. No real model SIGSTOP/SIGCONT has been used. Prefer completion of short jobs and temporary suspension of **new admission** over stopping almost-finished short models. A future pause-aware policy would prioritize low-progress, high-growth jobs and protect the supervisor/evidence clock; it cannot fabricate progress or count stopped RSS as free.

## Qualified repair, deliberately not presented as deployed

`qualified_not_installed/shared_json_outer_v1` contains four pinned sources, templates and42 CPU checks: atomic same-directory no-replace JSON publication, bounded parse retries, actual frozen native prefixes with/without padding flag, parent consumer atomic publication and additional strict AND. All model launches in CPU tests were mocks. Production deployment, current-route preservation and a real eligible canary remain pending at this snapshot. The guard package also passed isolated tests; it is not installed here. An unchanged old supervisor's remaining write windows are not claimed repaired retroactively.

Keep the failed scan's original INTENT/spent identity and raw error. No synthetic DONE/EXIT, cycles, refund or replacement accepted identity has been created. Evidence under `scan_engineering_failure/`. Original 72-input, repair-validation and historical three failed recovery tasks remain separate. Those old three are no longer live; their real SIGTERM failures are not called natural completions.

## Review questions for ChatGPT

1. Does this350-cell coverage and each paired/fixed-population statistic preserve missing and failed identities without selecting winners from different populations?
2. Does the padding-only change retain peak-growth evidence and full candidate charge? Is there defensible additional headroom beyond current88% policy once the IO fix is qualified?
3. Audit shared-JSON sources/42 mocked CPU tests, original strict AND, immutable bindings and no-replace behavior. What minimal actual rollout check is missing?
4. Assess the separate typed engineering-negative closure and new-trial lineage required for scan, without rewriting its original failed cell.
5. Confirm that no conclusion about CH/DH relative improvement is drawn before matched CH exists and that current queue evidence is not mistaken for whole-application latency.

Core9eedb3131937748f0492fa83aad37d3691118d70, Framework02775fd795cde5aae1480d81cee6eb481d0a08f4, binary02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d, DRAM850MHz, L2 capacity/geometry/mapping and DTC architecture stay fixed.35 frozen ordinary inputs,7 UNRESOLVED, no72-input sweep, no derived/fraction/trim promotion. Englishv0.23 remains the last user-confirmed manuscript; no automatic edits.

Live root: /root/data/dtc_l2_mlp_exploration_20261027_v1

True164 archive: /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1

Parent source/review commit: 285448215c42b0dd210bb3b0617ff134ea2b64c2. Current snapshot packaging itself starts/signals0 models and changes0 science/dispatch authority files.
