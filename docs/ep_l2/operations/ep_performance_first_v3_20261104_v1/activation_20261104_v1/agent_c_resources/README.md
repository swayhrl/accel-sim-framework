# V3 shared resource admission

Engineering status: **PASS**, qualified global EP caps2 and10. No application, Native, ledger, controller or Git writer was started or changed by this task. This packet covers only approved A8+B2; CLEANquota6 is not authorized.

Stable API: each `resources_midtag.py` / `resources_vector1700.py` implements `snapshot()`, `admit(snapshot, own_pending_additional_RAM, own_remaining_writes, policy=...)`, and `forecast(...)`. Both wrappers SHA-pin common `resources_v3.py`. Bind `RESOURCE_POLICY_CAP10.json` for approved10-way operation or CAP2 for fallback. Pass host-only `requested_host_cpu`, `requested_request_id`, `requested_cohort` from the exact immutable dispatcher binding. The science282 config and Source5 are unchanged.

A request:EP_L2_MID_TAG_850MHZ_V1_20261104, rootJ/execution_midtag_v3_20261104_v1/midtag. B request:EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104, rootJ/execution_vector1700_decomposition_v3_20261104_v1/vector1700. J=/root/data/ep_l2_full_workload_performance_20261027_v1.

## Reused pinned mathematics and guarantees

The adapter reuses the V2 immutable recovery/H/base modules by SHA and adds only exact V3 owner roots, DTC48 mapping, loader-aware process identity, global cap and CPU checks. Existing RSS is already in MemAvailable/cgroup.current and current files are already in df; admission adds only future growth and remaining writes. DTC legacy35GiB pool is a ceiling, not an extra reserve. Existing foreign floors remain real promises: current DTC48 requires5GiB native emergency floor and8GiB host/cgroup headroom; Main1GiB is combined by MAX, not added. New A/B restoration uses one maximum window under Main's existing ARCHIVE_SHARED_WINDOW.lock; per-owner2MiB metadata remains separate. No extra window is added per model or multiplied by10.

DTC48 actual loader identity is joined from registered exact spec/INTENT/UUID/PID-startticks, exact ELF+ordered argv/config suffix, and loaded ELF maps. Strace is a wrapper, not a second simulator. `observed_model:false` in a stale claim is never treated as absence of a running loader model. Finished archives are checked through existing owner DONE/EXIT/INTENT/archive contracts. Only active/nonarchived remaining source/restore writes plus explicit metadata are projected; published9.4GB lifetime ceiling is checked, not added again. Shared parent future RAM margin is deduplicated by exact PID/generation against older DTC16 accounting.

CPU checks require actual allowed affinity, cgroup CPU quota, current model affinities and registered claims. Only this exact request/cohort **CLAIMED** row is excluded from self-conflict; RUNNING or another cohort is never exempted. Main selects CPU under the same global ADMISSION.lock and passes the exact binding to the engine. The adapter does not allocate, alter affinity or claim CPUs itself. Snapshot age, RAM/cgroup/SSD/inodes/true164/errors may HOLD new work, never stop healthy models. Missing/unmapped foreign owners fail closed.

## Qualification

`CPU_RESOURCE_QUALIFICATION.json`:37 checks PASS including ninth->tenth allowed, tenth->eleventh denied, cap2 fallback, stage hold, host/cgroup/SSD/true164/inodes, growth minus actualRSS, no35GiB pool add, loader/strace classification, exact CPU own-claim exclusion and conflict negatives, unknown owner rejection, both archive paths using Main shared lock, and private flock mutual exclusion. The actual passive snapshot joined8 DTC48 models with zero metadata errors. Actual values are point-in-time, not a future admission promise. Runtime resamples before every consumption.

The adapter is only a resource gate. It cannot grant Source/input/NI/scientific authorization or release stages/budget. Main must bind the approved USER_AUTHORIZATION, fresh A8+B2 requests, frozen runtime/specs and qualified global Main concurrency policy. Scientific stage ordering remains in Native/sole dispatcher; the optional stage_ready=False resource flag also holds. This resource packet adds no NI applications, no source change and no model starts.
