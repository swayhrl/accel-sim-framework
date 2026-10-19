# AG6 V2 → BA consumer handoff

Producer branch: `hrl/iscas2027-dtc-ag6-v2-prep-gate-174-v1`.

已发布、回读的完整审查HEAD为`13c08ad37445ba8bc1dc32862a18861a091bd12e`，tree为`4eba1bfe5de72471b03f67f212947bfb90c57090`，56个review blob逐一核对且clean。精确收据为`PUBLICATION_READBACK.json`。本publication follow-up仅增加该收据、HEAD通知与索引，不改变BASE/源码/提案裁决。早期源码HEAD `29b1eb5428c42c692e031c65b540b132e208c0f5`已被BA引用。BA按此明确review SHA消费，不将移动branch tip作为Core/机制基底。

| Anchor | Exact commit / verdict |
|---|---|
| Coordination V2 | `f81ca1c5054a78ed2c09f316bac0501c3bbc9322` |
| AG5 CPU repair | `9793e998d60cb5a7f064a46ecd6be242eda61b7c`；53旧收据保留，不自动qualify BA |
| AG4 terminal | `d8d0401dab0a1d9cb949302bcc05148328421cc2`；2/5启动、1完整strict观测、0优化结论；qualification gap不改 |
| AG3 terminal | `2f3a8c4b27780e2bf3818949a6e5356d9fd62327`；GEMM完整1,071,405 cycles，旧失败/UUID不恢复 |
| BA initial published source | `7cdc27a7f4d7f13e11f942d6afdc5529121e6c3c`；初始接口比较保留 |
| BA latest reviewed source | `25cf0ab03d6cc68f964eeb03f42347452ac23abb`；AG5一体化源码review PASS，targeted runtime/shared-caller资格pending |
| Core / compiled Framework | `c8090115bd57512b1b23fca7d925301fa620c751` / `8e43c75a5e2eb60a8466084602b7df8117111e89` |
| GEMM BASE reuse | `PASS_REUSE_EXACT_V2_AG6_FROZEN_BUILD_ONLY`，dossier `BASE_REUSE_GEMM.json` |
| Gaussian BASE reuse | 同范围PASS，dossier `BASE_REUSE_GAUSSIAN.json`；原executor不足/synthetic negative永久披露 |

机器消费：每份dossier将`ORIGINAL_FULL_STRICT`、`HISTORICAL_EXECUTOR_SCOPE`、`NEW_COHORT_REUSE_ELIGIBILITY`分开。两份新reuse eligibility均为true，仅适用原精确runtime/loader/cache/Core/input/options tuple；任何变化撤销适用性。它们的`dispatch_permission_granted_by_this_dossier`均为false。

BA集成检查：

- `25cf0ab0…`已一体化guard/ownership/current instance与read-only shared peer view，generation image、父事件时继承快照和逐实例历史均在；无需重复移植。接着资格新的exact source/注册closure。
- 新源码已采用AG5原reviewer及BA严格wrapper。保留BA自己的publication capability、四点ledger与exact external roles；本地pack-prefix、basename或CPU-only政策不能变成fullsim authority。
- 不重跑整套53；仅按接口审查中的7组changed-path条件审查/测试，先真实host+cgroup双采样与exact-role登记。旧两root caller证据不覆盖新共享caller。
- 本四点仍未登记新UUID。BA唯一创建四个新UUID和actual-start records，失败也消耗4上限；新共享integration/准入/immutable preregistration与remote readback闭合前不派发。
- 保持原4Tag banks/finite服务/clock/quotas；只AE或只AD单开。最大两个sim还需独立事前资格，不新增canary；单worker可以作为默认。
- 四个完整合格结果后写新`SELECTION_V2`，保存旧selection和负结果；任一缺格/失败不提升，保持provisional O。BA32独立科学可继续，但不能补AG6格或自动借用本BASE到变化后的模型。

AG本窗口只source/历史收据review：compile/fixture/test/sim、新UUID、执行lease、old/foreign signals均0；无后台待发任务。未申请AG运行角色，未向BA roles插入权限。磁盘迁移完全未触碰。
