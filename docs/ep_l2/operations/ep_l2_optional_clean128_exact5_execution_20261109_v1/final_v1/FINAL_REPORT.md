# EP-L2 optional CLEAN128 五点正式收尾与同源对照

**任务：**`EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1`。**现场核查：**2026-11-10 15:02:53 UTC。本文供 EP-L2-8 审查。五点沿原两份 request、原 Source5/Spec 和每点一次消费完成；本轮没有登记、启动或重跑模型，没有新科学 Goal 或预算。

## 1. 正式验收和保全

五点均经共享 Native 唯一入口 `experiment accept <cohort> --project EP_L2` 验证自然 DONE、同一 PID 世代已退出、实际 argv/env/maps/strace、冻结 Spec/Source/Host pin、完整人口、lossless raw、64 slice 守恒和硬件排空。验收后，各点在真164 `admin-wcx@10.208.130.164:/home/shared` 的 `fuse.sshfs` 上生成不可变 `result.tar`、逐成员 SHA manifest、`ARCHIVE_RECEIPT.json` 与末尾 `COMMIT.json`；同一个全局 128 MiB 窗口内依次对**两个不同的新 Native 目标**做全成员 SHA/元数据恢复，随后释放临时窗口。原 Source 和本机结果保留。

| 家族/点 | UUID | cycles | 指令 / CTA / kernel | 真164 tar SHA256 | 成员 / 双恢复 |
|---|---|---:|---|---|---|
| GEMM EXT0 | `aa15408e-0d48-4b89-ad2e-781160b0c419` | 550642 | 739246080 / 1024 / 1 | `7735c714caced80b3198313909e19203717fb001929ba87450e8e13decde1d70` | 20 / PASS×2 |
| GEMM EXT1 | `a79fe296-1b89-4687-a59f-6a80a526f362` | 550109 | 同上 | `ce20ea1c8b603fad4b52bea382961df3f7e82c6c787c2c6135292d82f6d055e7` | 20 / PASS×2 |
| GEMM EXT2 | `9d617336-e18b-4c14-a1ad-6ac323486242` | 550109 | 同上 | `f1dd204566bd8c8105c85d9404d1144f60f78c6437ac728c8271b6b05f6589fb` | 20 / PASS×2 |
| Stencil EXT0 | `90644325-58b7-4eaf-bf07-102128f2868c` | 4768893 | 2193446000 / 6400 / 100 | `8b3daca5f3b8519cdf1f813fb360c8f9cfbf256f4934042ad76b44c389e94826` | 22 / PASS×2 |
| Stencil EXT2 | `aede460f-6e30-4416-b5af-c64c92127db6` | 4786427 | 同上 | `348757026e615e8502afccdc2e8d5a6ad4902b2f465957828756100b076bea56` | 22 / PASS×2 |

当前 Native epoch 2 与 registry SHA `04f11b84af86728dd854a5734622839e15f6e84052def40de0fc4c0a2732d1d2` 匹配；五行均为 `CLOSED_ACCEPTED`，GEMM/Stencil 原预算分别 3/2、剩余均 0，own dispatch claims 为空。上述为该采样时点的现场状态，registry SHA 之后可能随其他 owner 的合法事务改变。五份 archive tar SHA 已从真164回读核对；五份 manifest SHA 与 receipt ref 一致，双恢复目标逐点不同。正式状态以 Native registry 和关闭回执的外层联合证明为准；消费者 bundle 内的 `scientific_acceptance_granted=false` 是归档前生成的待 Main 状态，不应单独解释成最终未接受。

审查原件：执行根 `R=/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1`。每点 `R/cases/<cohort>/run/<UUID>/` 下有 `NATIVE_EXIT.json`、`VALIDATED_APPLICATION_BUNDLE.json` 和 `ACCEPTED_POINT.json`；`R/cases/<cohort>/control/ARCHIVE_RECEIPT.json` 指向真164 `ep_l2_optional_clean128_exact5_20261109_v1/{gemm|stencil}/accepted/<cohort>/<UUID>/` 的完整归档及两个 Native 恢复回执。GEMM/Stencil bundle SHA256 依表顺序分别是 `0445cf7568c76edc80e68d7b4bf54087bcf55ffc323a874f76294b2ac40576e6`、`36ad80bf6572a09f3a66e884a7a6619971cb5d4f6d10609a0539a98b814cc5f9`、`f5e94602260fd786cd3848d19169a7249f3b2c00fd8dca7d1b8f462fa5ac204a`、`00c90f7c592f8de6042a2b0a3f05cbb4ce89070a8ceda0bda293a7fabccfd396`、`e160382e7c778fd78decac89b377cdcc89dbe3f6fa705c704561f7ef1aa4c779`。

## 2. 同源人口与四组对照

五点的实际 Source archive SHA256 均为 `7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b`，ELF SHA256 均为 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`。GEMM 三点输入 SHA256 均为 `140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b`；Stencil 两点均为 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`。各点实际 283 个选项；同族比较仅 `-gpgpu_ep_l2_victim_extension` 为 0/1/2。固定 `WV_ZERO_RO`、`REF32x8_L100`，全人口完成且硬件排空。cycles 取最终 Native `gpu_tot_sim_cycle`，不对 slice 求和。

| 同源对照 | 起点→终点 cycles | 变化（终点减起点） | 相对起点 | 可解释范围 |
|---|---:|---:|---:|---|
| GEMM EXT0→EXT1 | 550642→550109 | −533 | −0.0968% | 扩展硬件/查询迁移包的净效果；数值很小，不能拆作单个端口或查询收益。 |
| GEMM EXT1→EXT2 | 550109→550109 | 0 | 0% | 同扩展硬件下启用 CLEAN 后，本输入没有观察到额外服务或性能增量。 |
| GEMM EXT0→EXT2 | 550642→550109 | −533 | −0.0968% | 含扩展硬件及策略的总净效果；与 0→1 相同。 |
| Stencil EXT0→EXT2 | 4768893→4786427 | +17534 | +0.3677% | 扩展硬件加 CLEAN 的总净结果为变慢；本轮无 Stencil EXT1，不能分拆迁移成本和保留增量。 |

这是一轮每点一次的确定性模拟结果，没有重复样本方差或真实 GPU 性能区间；GEMM 的 533 cycles 不应被表述为跨负载稳健增益。

## 3. 机制与成本边界

| 量（64 slice 汇总或完整运行计数） | GEMM EXT0 | GEMM EXT1 | GEMM EXT2 | Stencil EXT0 | Stencil EXT2 |
|---|---:|---:|---:|---:|---:|
| Base retained read responses | 609858 | 597299 | 597299 | 4930426 | 4933062 |
| Ext retained read responses | 0 | 0 | 0 | 0 | 56712 |
| Ext CLEAN installs | 0 | 0 | 0 | 0 | 6729 |
| Ext indexed reads | 0 | 0 | 0 | 0 | 77538 |
| Ext queries / selector reads | 0 / 0 | 8436 / 8436 | 8436 / 8436 | 0 / 0 | 2410324 / 2388405 |
| Actual lower reads | 33760 | 33744 | 33744 | 3474210 | 3407781 |
| Actual lower read bytes | 1080320 | 1079808 | 1079808 | 111174720 | 109048992 |

GEMM EXT1/2 的扩展区没有 spill、install 或 response，且计数和 cycles 一致；本输入没有显示 CLEAN 容量收益。GEMM 0→1 少 16 次 lower read，同时有 8436 次扩展区查询与选择；当前统计不能把 −533 cycles 唯一归因于其中某项。

Stencil EXT2 的 56712 次扩展区 response 与 6729 次 CLEAN install 证明扩展机制被使用；相对 EXT0，实际 lower read 减少 66429 次、2,125,728 B，但 cycles 增加 17534。扩展区查询 2410324 次，另有 77538 次 indexed read、6729 次 spill。计数说明局部服务与下游流量变化，并不能把每个 retained response 等同于一个避免的 DRAM 请求，也不能把重叠等待累计成独占关键路径。缺少 Stencil EXT1，尚不能证明净回退由 CLEAN 本身或硬件迁移中的哪一项造成。

建模成本为 Base128 之外每 slice 增加 optional CLEAN128 metadata；原申请估算 **58,880 逻辑位/slice**，另有比较器、端口、选择与控制成本。`metadata_PPA`、时序闭合、能耗、真实芯片面积均为 `UNKNOWN`。消费者标记 `MECHANISM_STUDY_LOCAL_SERVICE_V1`、`data_correctness_qualification=false`，数值输出 `UNKNOWN`：本轮接受的是约定的完整模拟与机制证据，不是应用数值 oracle 或物理 PPA 证明。

## 4. 判断与下一件工作

现有五点已完成，不能再等待所谓未启动模型，也不应借旧预算重跑。optional CLEAN128 在 GEMM 上没有增量激活收益，在 Stencil 上产生局部服务及 lower read 减少，却出现约 0.368% 的全应用净回退；因此目前**没有证据支持扩大该结构作为普适性能方案**。后续优先对已保留的 Stencil 100 kernel 结果按阶段核对查询/选择、bank 与下游读的关键路径关系，并补物理成本估算。若 EP-L2-8 需要拆分 Stencil 的硬件迁移与 CLEAN 策略作用，可提出**另行明确授权的同 Source Stencil EXT1** 精确申请；本报告不授权或启动它。Source KEEP，109 历史队列、论文正文和其他 owner 账本均不在本轮动作内。
