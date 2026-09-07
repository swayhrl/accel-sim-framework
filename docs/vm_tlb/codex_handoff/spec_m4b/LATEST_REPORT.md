# Window C — SPECULATIVE M4B DEVELOPMENT 当前交接

状态：`SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`。C9 architecture decision 已完成；C10-A/C10-A2 已完成 source/static 实现与 blocker closure，但 final Core 尚未经过完整 build/regression。

## authoritative 身份

Framework branch：`hrl/vm-m4b-speculative-v0`

- C10-A2 evidence SHA：`447ad52cf867e35a616fa16ab12e32b8914f50b9`
- C10-A2 Core SHA：`12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`
- C10-A original functional parent：`c21137bcb86010215c008292f272aacefac175d3`
- C9 architecture SHA：`04be2899a19b1fe756956dbe5e459494ae1da8df`

## 已冻结架构/实现

C9 v1：real PA registered Weight extents、privileged registration、local N=8 replicas、single provisioned ASID、`HIT_FIRST / MISS_JOIN`、5/10/20 Segment latency points、pinned epoch；object map telemetry-only。

Fair budget：standalone sub-entry G96，charged Segment+sub-entry G32；historical 768-group arm 永不作为 equal-cost official arm。

C10-A2 已 source/static 闭合：

- transactional semantic registration rejection -> zero live descriptor -> conventional fallback；
- explicit install/revoke lifecycle and per-replica ack；
- production READ/WRITE/ATOMIC classification；
- F0-F4/F6-F9 runtime selector plumbing；
- F5 hard-blocked；H0 permanently rejected；
- conventional ASID generation and stale lookup/MSHR/fill discard；
- Segment epoch 与 conventional generation 分离。

## 正常 post-terminal C10-B

完整 C10-B handoff：

`docs/vm_tlb/codex_handoff/spec_m4b/C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION.md`

正常路径仍要求 A `A_TERMINAL_CONFIRMED` + fresh resource gate，然后严格执行：compile/link -> standard regression -> B2-B7 focused runtime -> telemetry conservation -> F5 -> bounded fair-arm sanity -> STOP before C5。

## 当前额外授权：C10B0 concurrent focused compile canary

若 A C3 尚未 terminal、但 A 独立 concurrent resource gate PASS，可执行：

`C10B0_CONCURRENT_FOCUSED_COMPILE_CANARY`

严格阅读：

- `docs/vm_tlb/codex_handoff/spec_m4b/C10B0_CONCURRENT_FOCUSED_COMPILE_CANARY.md`
- `util/vm_tlb/run_c10b0_concurrent_compile_canary.sh`

需要 fresh：

`/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt`

第一行必须为 `A_CONCURRENT_RESOURCE_GATE_PASS`，且未过期、`allowed_c_compile_jobs=1`。

并发 canary 只允许在一个不与 A/B 同 physical core 的空闲 logical CPU 上，以低 host priority，顺序直接编译并运行：

1. `tests/vm_c10a2_static_model_test.cc + src/gpgpu-sim/vm_translation.cc`
2. `tests/vm_c10a_registered_segment_test.cc + src/gpgpu-sim/vm_translation.cc`

可以修复由这两个 focused compile/test 暴露出的普通 C10-A2 integration/correctness bug，并在 fresh gate 下重试；禁止新增架构 feature。

并发模式严格禁止 full simulator build、full regression、F5、C5、trace workload、KV/12K/M5。

Canary PASS 后必须 STOP。其结果只能作为 exact SHA 的 focused evidence；A terminal 后仍需完整 C10-B compile/link 和 standard regression。