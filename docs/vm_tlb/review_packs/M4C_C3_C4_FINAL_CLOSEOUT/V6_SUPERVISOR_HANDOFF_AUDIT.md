# V6 supervisor handoff audit

Status: **PASS — controlled C4 offline-locality handoff completed**

The legacy V6 supervisor was an inline, non-versioned shell process. It
treated any `pswpout` increment and any non-zero memory PSI `avg60` as a
resource failure. This caused resumable final-trace children to receive
`SIGTERM` despite GREEN host conditions and was replaced under the explicit
`A_V6_CONTROLLED_SUPERVISOR_HANDOFF_AND_C4_CLOSEOUT` authorization.

| Item | Evidence |
| --- | --- |
| Old supervisor | PID 651573; TERM at `2026-09-08T04:53:55Z`; exited within one second; no direct locality child remained. |
| Legacy code identity | Inline process, not a versioned file. Captured legacy V6 launch-spec transcript SHA256: `a84ed035907d8775f63df8e72526205bfdf7da6a018889fdd56e043247a6ff6a`. Its decisive legacy rule was `pswpout > 0` or non-zero memory PSI `avg10/avg60` ⇒ hold/TERM. |
| New supervisor | PID 989825, child PID 990129; Framework source `d440f6806459219f3f45b4b8893b02e2194b27f8`, a descendant of resource-policy commit `c02a7bff8e6f1bb46827dac02dc6d78c8693fbb0`. |
| New code identity | `supervise_m4c_locality_dynamic.py` SHA256 `d607bf20ec5a7b615d962580402748e36442cd8b4566a6a3e5cd3c27306d764d`; analyzer SHA256 `ad176a99f4d119ddaf4f030409447d396f2d9485d63b7afc32616ff54f13af5f`. |
| Pre-handoff locality | 691/692 kernels, 2073 rows; DB SHA256 `7a904785cc50969cb89322421689e45d2fa331a37d0d6f77a63d1d39853abece`. See `PRE_HANDOFF_STATE.tsv`. |
| Post-handoff locality | 692/692 kernels, 2076 rows; all three classes for index 691; DB SHA256 `6488b7af248fcea1ba3c5b0665b48f801c1e96b3a043ac56cf8b203194eea00c`. |
| Resume validation | Decode locality 740/740 and prefill locality 692/692 passed schema/identity checks. Prefill durable SQLite prefix conservation passed: Weight 7,906,336 lines; KV_CACHE 32,768; UNKNOWN 1,104,535. |
| Dynamic-gate behavior | V7 retained the child during small host-wide swap-out windows (including 0.394, 0.957, and 2.437 MiB/s). No RED pair occurred; V7 did not pause or restart the child. |
| Partial old-builder output | The legacy watcher exposed a control-flow bug after detecting missing prefill rows. Its incomplete scratch output was moved, not deleted, to `/workspace/m4c-c4-final-inputs-20260908-v3/failed_attempts/20260908T045514Z_partial_locality_builder`; it is not evidence. The builder now validates locality before creating any output. |
| C3 rerun | **NO** |
| C3 evidence modified | **NO** |
| Previously completed locality recomputed | **NO** — V7 resumed from the durable 691-kernel prefix and processed only semantic index 691. |

The final C4 builder ran only after the 692/692 gate passed. It reads frozen
C3 logs/exports and immutable trace-derived locality; it launches no simulator.
