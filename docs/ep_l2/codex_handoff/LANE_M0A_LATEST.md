# Lane M0a latest — interim checkpoint

Status: **M0A_INTERIM_REVIEW_READY** (interim only; not final PASS).

Frozen implementation candidate used by all completed formal rows:

| source | parent D512 SHA | candidate SHA | published branch |
|---|---|---|---|
| Core | `878f80869ce212e779df20b6421e4dc7f987825d` | `666f0ba2d7b6a027f395346e274a934c19fdd3c1` | `fork/hrl/ep-l2-m0a-observability-v0` |
| Framework | `aae62b66685f15437cecf0193934f628e6fac6ae` | `2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d` | `origin/hrl/ep-l2-m0a-observability-v0` |

Runtime config composite SHA256:
`d3aaf8a1a090c13e52985d60a70e7b3839aa0793d7db56722a7b3e8da3389b10`.
The approved, verified OFF/ON delta is exactly
`-gpgpu_ep_l2_m0a_stats 0 -> 1`.

Completed formal rows: five M0a-ON representative workloads
(`vectorAdd_4M`, `convolutionSeparable`, `spmv`, `cfd_097k`, `sad`) and all
three required OFF/ON pairs. Each completed row is `COMPLETE_VALID`; the
three controls have matching terminal cycles and instructions.

`scan` remains **RUNNING** at
`/workspace/results/ep_l2_m0a/ON/scan/`, using its original PID/process and
result path. It has not been stopped, restarted, duplicated, moved, or rebuilt.

Review pack: `docs/ep_l2/review_packs/M0A_OBSERVABILITY_INTERIM_r1/`.
M0a remains observation-only. This checkpoint does not authorize M0b, Unified,
RO, TVD, borrowing, a baseline change, or a mechanism performance claim.
