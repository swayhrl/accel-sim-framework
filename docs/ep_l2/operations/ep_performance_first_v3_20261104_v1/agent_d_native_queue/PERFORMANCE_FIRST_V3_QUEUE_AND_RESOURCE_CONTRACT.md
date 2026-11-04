# Performance-First V3 queue and resource contract

Status: **PREPARED / NOT_AUTHORIZED / NOT_ACTIVATED**. No dispatcher, runtime or budget was installed.

## Prospective exact scopes

| Family | Fresh request | Proposed starts | Prospective data root |
|---|---|---:|---|
| Mid-Tag850 | EP_L2_MID_TAG_850MHZ_V1_20261104 | 8 | J/execution_midtag_v3_20261104_v1/midtag |
| Vector1700 W/WV | EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104 | 2 | J/execution_vector1700_decomposition_v3_20261104_v1/vector1700 |

J = /root/data/ep_l2_full_workload_performance_20261027_v1. Ten points are proposals, not consumed starts. Old system remaining2 is condition-false and cannot fund V3. Old repaired six-point allowance is exhausted. Source/mode/input/exact282 qualification is family-specific and remains Main/A/B responsibility.

V3 explicitly returns to **global maximum 2 EP formal models**, overriding V2's temporary cap10. One Main owner/scheduler consumes both families. No separate candidate dispatcher or Git auto-writer is created. If one family is held, another qualified family may proceed; local HOLD does not stop healthy foreign or EP models.

## Single transaction and one-shot contract

Reuse global J/execution_performance_first_20261103_v1/control/ADMISSION.lock, MAIN_GIT_PUBLICATION.lock and ARCHIVE_SHARED_WINDOW.lock. Include all EP-scoped claims and live PID+start-tick generations in the global count, not two independent per-family caps. Under that lock: verify authorization and immutable spec/Source5/config/mode/input/RO identities; take fresh host and foreign snapshots; validate Native routing; atomically bind a unique one-shot intent and claim before starting. Repeated admission of an already consumed identity, technical retry and refund are forbidden. A completed or failed model stays consumed. Failure is retained and releases only live resources after terminal proof.

Resource observation does not itself grant scientific permission. Unknown mappings or changing claims cause bounded local resampling/HOLD, not guessed zero or blanket shutdown.

## Actual snapshot, not a reservation

At 2026-11-04T03:49:19.611427+00:00 the read-only sample has host MemAvailable about223.9GB; cgroup memory.max274,877,906,944 bytes and memory.current66,343,755,776 bytes; quota384 CPUs and affinity512 CPUs; no cgroup OOM events observed. Local native filesystem free40,941,817,856 bytes and genuine164 free45,238,762,147,840 bytes. No scoped V2 simulator/finite executor remained. A corrected loader-aware follow-up identifies eight live foreign DTC48 models plus eight strace wrapper parents; the latter are not additional models. These are changing observations, **not launch admission**.

Some older registry rows still advertise RUNNING or nonzero write carriers after their models ended. The snapshot deliberately records them without releasing or summing every historical pool. In particular, an old35GiB pool and its current files cannot both be charged as new growth. DTC remaining48 has an explicit carrier and eight claim rows at this observation. The loader-aware exact join confirms all eight claim-to-model matches, with combined model RSS18,145,693,696 bytes and estimate-minus-current-RSS future growth7,278,021,016 bytes. Claim metadata observed_model=false was stale and is not used as a liveness test. Their owner, terminal/archive state, real future writes and already allocated bytes still must be joined by the complete current read-only adapter before an actual consume. A historical state label alone is not evidence of a live model, available RAM or a released promise.

## Incremental admission math

- RAM supply = min(host MemAvailable, effective cgroup remaining). For each live model/controller use only predicted future growth above its already counted RSS, deduplicated by PID/start generation. For committed but unstarted claims use the qualified estimate once. Do not add process hardcap and RSS and estimate together. New-family forecast must come from exact input/profile history; hardcap is protection, not an extra reservation.
- CPU = actual cgroup quota/affinity, current process load and registered peer CPU commitments. Pick uncommitted CPU resources; no peer-affinity edits or all-CPUs-idle requirement.
- SSD requirement = new output/build increment + all other committed but unwritten growth + at most one shared restore-window increment + max(about1GiB emergency, existing explicitly guaranteed foreign minimum). Existing disk contents are already removed from df free. Do not multiply archive working space by family or all future runs.
- Genuine164 requirement = actual pending archives + required existing promises. Trace stays at its validated true164 path; no local full Trace copy or redundant body hash.
- Two independent restores are serialized through the same cross-family archive lock. Reuse the temporary window after proof, preserve Source KEEP and immutable raw. Two independent restores need not mean two simultaneous native working sets.
- Unknown foreign ownership, inconsistent remaining arithmetic, claims drift, unknown RSS generation, ENOSPC/OOM risk or exhausted permission is a local fail-closed condition. Main may wait and resample; never delete someone else's data or reduce their promises.

The pure candidate admission_math function proves numeric cap2/no-double-charge decisions only. It does not yet implement a complete new live foreign-owner adapter, actual CPU affinity allocator, or native consume wrapper. Those must be bound and CPU/Host-qualified by Main before activation. Physical free space alone is insufficient to declare launch-ready, and no arbitrary additional multi-GiB reserve was introduced.

## NI, completion and archiving

Preserve actual Observer profile; CPU guard tests do not establish application NI. Any new observer/source/profile coverage not previously established remains NOT_MEASURED or NOT_PROVEN, per mode. Do not insert unapproved NI runs into proposed10 starts. If scientific qualification requires an extra application NI point, Main must HOLD that point and request its separate scope.

Accept only complete kernel/CTA/instruction/drain/resource/identity checks, then true164 full SHA and two native restores, followed by Main-only Git commit/push/readback. Keep all positive, negative, zero, failure and HOLD records. No fixed global project budget is inferred from this ten-point proposal.
