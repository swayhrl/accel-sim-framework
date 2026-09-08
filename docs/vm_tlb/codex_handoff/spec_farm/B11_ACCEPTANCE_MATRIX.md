# B11 Goal acceptance matrix

Goal: `B11_POST_TERMINAL_E01_E10_EXECUTION_GOAL`

| Gate | PASS requirement | On failure |
|---|---|---|
| A terminal | attestation first line `A_TERMINAL_CONFIRMED`; A checkpoint `14edbe200859f6ddf42bc3d459334f184a920a82` remains valid | hard stop only if terminal evidence itself is invalid |
| B provenance | B9 manifest/whitelist, simulator SHA, trace/config provenance match frozen identities | diagnose; hard stop if immutable identity cannot be restored |
| resource admission | 10 s gate: memory-full <=0.5%, io-full <=1.0%, no swap-in/out, memory/swap/iowait thresholds pass | record, sleep ~5 min, retry; not final failure |
| shared slot | `/workspace/vm_tlb_post_terminal_heavy_slot.lock` acquired for each heavy job | wait/retry |
| E01–E06 | exact B9 arms complete with exit/provenance/required observables | debug harness/infrastructure; preserve experiment semantics |
| E07–E08 | one-kernel RSS calibration complete with `/usr/bin/time -v` evidence | debug/retry under resource gate |
| E09–E10 | deterministic 16+16 selection, mining and conservation pass | diagnose selector/miner/input; no silent substitution |
| result integrity | valid outputs never overwritten; incomplete attempts quarantined with provenance | repair resume logic |
| evidence discipline | smoke/static/full evidence labels remain distinct; A/B numerical evidence not pooled | repair report |
| synthesis | H1–H6 update + complete B11 review pack | continue until complete |

Final PASS state only:

`B11_E01_E10_COMPLETE_READY_FOR_REVIEW`

Final hard-stop state only:

`B11_HARD_BLOCKER_WITH_EVIDENCE`

`RESOURCE_DEFERRED` is never a final B11 state.