# Codex Goal T — DTC-L1 有界Tag/PIB探索（原174，先CPU gate、后新模拟）

**执行合同**：同目录`SCIENTIFIC_CHARTER_AND_PREREG.md`。用户2026-10-17同意机理补证及有界性能调优。**新独立lineage，最多7条新模拟；不是原Lane A Goal延续/重启。** 本Goal不自动运行holdout或T2服务改造。

## A. 可与M并行的CPU准备（0个模拟）

1. 在原174账户/容器（非174-new），fetch并回读Framework `hrl/iscas2027-dtc-mechanism-tuning-plan-v1` 最新HEAD，完整读本Goal及SCIENCE合同。检查原A已完结的最终HEAD`f5c37d6edcce832a72cb0830021bffa78df6cc13`和最新liveness/lock；不reset、不restore旧A Goal。新建**独立**worktree与分支 `hrl/iscas2027-dtc-tag-pilot-174-v1`，输出目录独立；同名/活动运行冲突则STOP。
2. 仅CPU核冻结finite Core`6fba0136f8465b59fe5858a950fa39efb265f654`、binary`fe2d2737...`、Framework`18a68dcc...`、原GEMM/Gaussian完整trace/list及已验UUID/strict/有效config和source SHA。检查 `gpu-sim.cc` 中 `-gpgpu_dtc_l1_logical_sets`、`-gpgpu_dtc_l1_logical_ways`、IO/OO有效PIB参数，和`dtc-l1-common.h`真实tags/physical构造及set/bank映射。验证不存在隐藏常量假设：Tag bank4、1/bank/cycle、core实际II1、物理640行，普通side16KiB与shared96KiB均保留。
3. 静态为7个新attempt生成固定source/config/trace/UUID/strict审计表。T0=GEMM IO128；T1=OO128的 (32sets,8ways)、(64sets,4ways)、(64sets,8ways) × GEMM/Gaussian。只允许改指定参数；其余包含finite-service=1、lower cap32768、时钟、64SM、原Core/binary、all4sector whole-line返回、ordinary side/atomic path均一致。新配置必须确认effective解析结果，不因旧模拟器默认值省略关键配置。
4. 完整七点预登记和执行脚本SHA提交到T分支，**push并fetch-back核验后才可启动任一模拟**。提交的`PRE_REGISTRATION.tsv`必须明确每条新UUID、候选名、输入身份、是否discovery、原对照UUID/原stdout SHA、有效选项差异、预期active-thread instruction和kernel范围。不能在看到第一条结果后改变后面候选、输入、资源或停止规则。
5. 等M的CPU日志consumer分支`hrl/iscas2027-dtc-mechanism-consumer-174-v1`交付可核报告，至少确认原输入及机制字段没有影响本轮假设的科学身份冲突。如果M的C+字段不可比，仍可研究**相对原OO的Tag参数效应**，但不能声称已解释C+差额。任何活跃锁、内存、swap、端口、源支持域不明，则CPU STOP。

## B. 严格新运行（通过全部CPU门槛后，最多7次）

- 从合格manifest独立启动，不改原44行/旧UUID和所有原raw；只运行**冻结完整**原GEMM、Gaussian。不得裁剪kernel、从头重复旧点、跳过zero-mask或只跑局部来产生正式性能。
- T0 的GEMM IO128单点与现有OO128/IO256在有效PIB、Core、pool、trace和服务参数上做精确差异对照；承认它只分离DTC内部的深度差异，不直接解释与C+关系。
- T1三组Tag点各2arm。受控探索只改变logical_sets/ways两个尺寸参数（每组与原32×4对照），不修改模拟器源码；如果现有Core不能合法执行该配置或会改变非预期语义则保留前置FAIL并停止该候选，不通过改程序逻辑让它“通过”。
- 调度安全：对原A残留监视/lock及其它项目只读，不终止它们、不接管保留的lock；由本T窗口唯一合法临时authority在独立输出/锁边界派发，最多2个新模拟并行（若RSS/IO或其它项目紧张则1个），没有多套persistent dispatcher。先观察资源再决定；必要时等待。每个attempt只发起一次；确有runner错误可以在不修改科学条件下进行确定性修复，但不得因性能差而选择性重跑。正常timeout/resource终止也保留失败收据。
- 每次运行核自然终止及严格源/输入/list、complete ordered kernels/CTAs/active-thread instructions、effective mode/logical_sets/ways/PIB/pool/cap/tag banks/clock/ICNT/DRAM，stdout/hash，credit/reference/physical/PIB/lower/sector/ordinary Store 排空、64SM采样与11项finite统计。数据未在Core内真实输出者标UNAVAILABLE，不补造。
- 按新旧**同一原GEMM或Gaussian**的完成周期算探索速度比。所有失败、HOLD、负收益/无收益均保留，且候选前预定义的用户选择规则（`min >=0.98, GM>=1.02`）不可临时修改。GM仅2个预注册**探索输入**对原OO的改善评分，不是原GM12或论文总体加速比。不可以挑逐负载最优配置。
- 每点保存新lineage/attempt UUID、严格收据、资源状态、source/input/runtime/config/raw SHA；最终写全矩阵（含失败）、`DISCOVERY_SCORE.tsv`、`SCIENTIFIC_SCOPE.md`、`CONTROLLED_DELTA.tsv`、`LATEST_REPORT.md`及`FILES_SHA256.tsv`，推到执行分支 `docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/`。大raw仍留原174/164只读位置，只推小文件和hash。fetch-back核HEAD/tree与clean。
- 七点或合法已停止的子集收口后STOP，不自动运行DWT2D/BICG holdout；不做服务T2、物理池调整、128KiB modern、LUD/2D/Hotspot/SpMV/LayerNorm，不算新论文GM或称等面积。给ChatGPT审报结果，届时才决定独立holdout与PPA是否值得。

## 执行者必须主动STOP的科学边界

出现场景如：输入有原producer格式疑点、新Core/解释器binary改变、比较端身份不一、通过改clock/cap/延迟让性能变好、出现容量死锁需改机制、严重调度/资源冲突、观测统计干扰性能、需要第二个持久scheduler、审计不能区分额外Tag比较硬件成本。不能通过调整阈值、隐藏负例或按结果换负载解决上述问题。**优化的合法目标是找到一个值得后续真实硬件计价和holdout验证的配置，不是把探索点冒充最终架构性能。**
