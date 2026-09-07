# Window B — SPECULATIVE EXPERIMENT FARM 当前交接

状态：`SPECULATIVE_DIAGNOSTIC`。B7/B8 analysis-only 已完成；B9 execution preflight 已完成并通过。没有将任何 B 结果合入 Window A。

## authoritative 身份

- Framework branch：`hrl/vm-spec-farm-v0`
- B9 evidence SHA：`b9119d4dfe0f8c04f432caa2b7974c3ccfc38152`
- Core branch 起点：`0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`
- simulator binary SHA-256：`2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`
- scratch：`/workspace/vm-spec-farm/`

## 已有证据边界

- B1：prefill `134/692`、decode1 `96/740`，均为 `REAL_PARTIAL`。
- B2：37/54 one-kernel smoke；其余历史缺口未因 B9 自动补跑。
- B7：0 `REAL_PASS`、2 `REAL_PARTIAL`、37 `SMOKE_ONLY`、38 `PLANNED_ONLY`、12 `STATIC_ONLY`、17 `MISSING`。
- B8：6 个可证伪假设、18 个最小信息实验 bundle。
- B9：E01-E10 exact execution manifest、arm delta whitelist、observable contract、deterministic selector、resource gate 和默认 dry-run runner 均静态通过；最终状态 `EXECUTION_PACK_READY_AFTER_A_TERMINAL`。

## Window A 外部证据

A formal C3 仍可能非终态。B 不读取 A 私有工作树或运行数据作为数值 baseline。

A progress-review/early-C4 evidence 只用于方法学：miss 减少不自动意味着 cycles 下降，因此 B future runs 必须保留 TLB、MSHR/PWQ、walker、PWC、PTE wait、cycles/IPC 及 downstream pressure observables。

## 正常 post-terminal 路径

完整 B9 executor 仍要求：

`A_TERMINAL_CONFIRMED`

并且逐 job 通过 B 自己的 resource gate。A terminal 后才允许按 B9 正常执行 E01-E10。

## 当前额外授权：B10 concurrent E01 canary

若 Window A 在 C3 非终态期间通过独立 concurrent resource gate，可执行：

`B10_CONCURRENT_E01_CANARY`

严格阅读：

- `docs/vm_tlb/codex_handoff/spec_farm/B10_CONCURRENT_E01_CANARY.md`
- `util/vm_tlb/run_b10_concurrent_e01_canary.sh`

它只允许顺序执行：

1. `E01-generic`
2. `E01-pwc32`

需要 fresh：

`/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt`

且第一行必须是 `A_CONCURRENT_RESOURCE_GATE_PASS`，未过期。

并发模式下有效 B worker 永远是 1；必须选择不与 A SMT sibling 冲突的空闲 physical core，并以低 host priority 运行。任意 resource gate 失败立即 `RESOURCE_DEFERRED`。

完成 E01 canary 后必须 STOP，不得自动执行 E02-E10、B1 resume、full ROI 或 trace mining。