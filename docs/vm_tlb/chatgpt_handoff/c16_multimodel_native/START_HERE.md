# C16 — 多模型原生访存表征与分层采样：总入口

Goal family: `C16_MULTIMODEL_NATIVE_MEMORY_CHARACTERIZATION`。

共同基线：C15 A 集成提交 `a69ee630a8e3bc509029edc5d27c2daf7d2089f4`。C16 不修改 C12–C15 冻结结果；所有旧结果只读消费。

## 研究目标

C16 不默认新增 full-ROI Accel-Sim 矩阵。核心目标是：

1. 在租用的 AutoDL GPU 上完整运行多个真实模型，但只做低开销 native baseline / kernel census；
2. 基于真实的 phase / operator / implementation / shape / dtype / native-duration 建立 Sampling V2；
3. 只对被冻结的少量代表窗口执行 NCU / NVBit 地址采集；
4. 在本地服务器完成页、Cache-line、对象归因、采样验证和跨模型 TLB/Cache 行为分析；
5. 最终最多提出 3 项需要高保真模拟的架构问题，不自动执行。

## 四个并行窗口

| Lane | Goal | 主要阶段 | 角色 |
|---|---|---|---|
| A | `C16_A_LOCAL_PREP_AND_INTEGRATION` | C16-0；C16-5.4；C16-6.2~6.4 | 本地资产、模型/场景冻结、C15-A小修、最终集成 |
| G | `C16_G_AUTODL_NATIVE_EXECUTION` | C16-0.3/0.4/0.9；C16-1；C16-2；C16-4.1~4.3 | AutoDL GPU 真机运行、kernel census、NCU/NVBit执行 |
| C | `C16_C_STRATIFIED_SAMPLING_V2` | C16-0.8；C16-3；C16-6.1 | Sampling V2、历史回测、prospective holdout、逐指标资格 |
| H | `C16_H_MEMORY_FINGERPRINT` | C16-0.5/0.8；C16-4.4~4.6；C16-5.1~5.3/5.5 | 对象映射、页/Cache-line访存指纹、TLB/Cache联合分析 |

四个窗口使用独立 worktree / branch，只通过已提交的 manifest 和内容 hash 消费彼此结果。不得读取其他窗口 live partial 作为科学输入。

## 推荐执行顺序

### 租 GPU 前必须完成

A/G/C/H 同时启动：
- A 冻结模型、输入、场景、资产清单和传输包；
- G 完成 native runner、AutoDL bootstrap、nsys/ncu/nvbit wrapper 的 offline dry-run；
- C 完成真正的 strata-specific estimator、certainty-unit 逻辑和历史 sanity；
- H 完成 runtime object-map、page/line parser、mask+width、集合/重叠 fixture；
- 只有当 `C16_LOCAL_GPU_PACKAGE_READY` 后才建议开始 AutoDL 计费。

### AutoDL 开机后

G 执行 G0/G1/G2/G3 inline canary。某能力通过后立刻放行对应正式任务，不等待所有能力一起通过：
- G0 → native baseline；
- G1 → full lightweight kernel census；
- G2 → bounded NCU；
- G3 → bounded NVBit。

A/C/H 在本地并行消费 G 已提交的小型 manifest / catalog；大 raw trace 通过受控 exchange path + SHA256，不提交 Git。

## 强制科学边界

- Native A100/AutoDL 测量与 C12/C13 模拟平台是不同测量域，不混写 IPC/Cache/TLB 结果。
- 完整 native inference ≠ 完整 SASS trace ≠ full simulator replay。
- `.traceg` CTA 文件顺序不得直接称为共享 L2 全局时间顺序。
- VA 页桶不得称为真实硬件 TLB miss；VA 连续不得称为 PA 连续。
- Unknown object 不补成 Activation。
- Sampling 对 native duration 合格，不自动意味着对 TLB/Cache/机制 speedup 合格。
- 小收益如果小于估计分辨率或不确定范围跨 0，必须 `INCONCLUSIVE`。

## 必读顺序

1. `C16_MASTER_GOAL.md`
2. `C16_STAGE_ACCEPTANCE.tsv`
3. `C16_DATA_AND_PROVENANCE_CONTRACT.md`
4. `C16_RESOURCE_BUDGET_AND_TRANSFER.md`
5. 自己 Lane 的 Goal 文档
6. `C16_LAUNCH_PROMPTS.md`

C16 终态目标：`C16_MULTIMODEL_NATIVE_FOUNDATION_READY_FOR_REVIEW`；若原生动态证据不足，则只能 `C16_MULTIMODEL_NATIVE_FOUNDATION_PARTIAL_READY_FOR_REVIEW`。