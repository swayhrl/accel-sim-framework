# DTC 高收益应用微架构归因（Agent C）

本报告只读核查五个预先指定的正例，共 20 个原始 accepted cell；不代表完整 23 项分布，不新增模拟，不修改 v0.23。原 Core 固定 `2e3bef4364e578cddd0e881c0baace2e51c55930`，不以新修复 Core 代替。

## 关键结论

**2DCONV 的 3.347× 主要是整个 DTC 模型的收益，不能写成 Hash 收益，也尚不能单独写成 Tag/Data 解耦的因果收益。** 传统 Hash 仅 1.006686×、DTC Hash 仅 1.016608×；无 Hash 时 CM/DM 已有 3.314588×。CH→DH 的 L2 读字节仅降 0.767%，DRAM 读量完全相同。当前最强的微架构关联是传统路径反复触发 8 项 merge 上限，而 DTC 使用独立物理所有权、128 项 PIB 的 pending 合并和 OO 退休；两边的命中与完成时序也不同，尚无匹配服务消融来隔离贡献。

| 程序 | CM/DM | CH/DH | CM/CH | DM/DH | CH→DH L2读量下降 | CH→DH DRAM读字节 |
|---|---:|---:|---:|---:|---:|---:|
| 2DCONV | 3.314588 | 3.347255 | 1.006686 | 1.016608 | 0.767% | 67,108,864 → 67,108,864 |
| 3DCONV | 1.323365 | 1.344380 | 1.000000 | 1.015880 | 5.038% | 67,108,864 → 67,108,864 |
| particlefilter_naive | 1.329003 | 1.329003 | 1.000000 | 1.000000 | 8.163% | 64 → 64 |
| 3MM | 1.462780 | 1.744357 | 1.101613 | 1.313668 | 65.334% | 0 → 0 |
| GEMM | 1.410609 | 1.688942 | 1.083225 | 1.296961 | 64.211% | 0 → 0 |

## 2DCONV：优先案例

输入 SHA `d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0`，`NO_ARGS`，kernel `_Z20Convolution2D_kernelPfS_`，65,536 CTA，620,347,492 active-thread instructions。四配置工作量和 kernel 身份相同。cycles 为 CM 1,559,265 / CH 1,548,909 / DM 470,425 / DH 462,740。

- **CONFIRMED：** CH 记录 315,294,062 次 MSHR merge-full 拒绝；配置 `A:512:8` 的 512 是地址项总容量，8 是同一地址的待返回请求列表上限，不能用“MSHR 有 512 项”否认合并上限。源 `gpu-cache.h:583-586`、`gpu-cache.cc:581-593,1463-1523`。
- **CONFIRMED：** DH 有 5,749,925 个 pending-reference 命中；5,240,320 次 PIB 退休中 4,846,419 次计为存在更老未就绪项的 OO 退休。这个总退休数含 source-observed stores；load service retire 为 4,716,288，二者不可混用。
- **SUPPORTED_ASSOCIATION：** CH 的 merge 拒绝与 DH 深合并/OO 完成伴随 3.347× 加速。没有仅调整 merge 上限、仅改变退休策略且服务等价的对照，不能分配各机制加速份额。
- **CONFIRMED：** DH 1,885,986 次 Tag 淘汰中仅 12 次 deferred reclaim；大多数被淘汰数据已经 Ref=0，可立即回收。故不能用“频繁保留失去 Tag 的在用数据”解释这一 DH 正例的主要收益。Hash 从 DM 到 DH 显著减少 deferred reclaim，但 cycles 仅改善 1.634%。
- **CONFIRMED：** DH 服务采样得到 PIB 平均 125.47 项、物理行平均 502.77 项；这只是模型各 SM/core-cycle 的占用积分均值，并非独立请求并发度或实测硬件队列。未打印的 OO PIB-full、Tag 冲突、物理耗尽不能写为零。
- **静态局部证据：** 唯一共享地址 producer 的 16 MiB 前缀包含 155,787 个 line-reference events、10,683 个 distinct 128B lines，静态复访因子 14.5827。仅为有界前缀，不是完整 kernel 或真实跨 SM 时间复用。详见 `../../shared_address_index/2DCONV_K1.json`。

## 时序、吞吐与建模风险：已做反证核查

| 维度 | CH 实际路径 | DH 实际路径 | 可以得出的结论 |
|---|---|---|---|
| 命中前端 | 4 bank、20 stage L1 latency queue；每 bank 可每 LDST 周期入队一个，stage 逐周期前移 | cacheable load 转入 OO；Tag grant 需过至少一核心周期才能 commit，可预取下一 reference Tag | 20 是流水延迟，不是一次访问独占 20 周期；不能声称传统吞吐仅 1/20 |
| 待请求跟踪 | 512 地址 MSHR，每地址最多 8 个 conventional mem_fetch；base PIB 256 | 128 项 instruction PIB、512 logical Tag slots、640 physical lines；physical waiters/Refs 随 live PIB 约束，无同样 8 项列表上限 | 跟踪粒度和 merge 上限不同，同名字段不能直接比较 |
| 返回 | 常规 L1 fill/MSHR ready 列表；依请求逐项取出，L1D writeback 客户端仲裁 | 真实下行请求与 response FIFO，1 whole-line refill/core-cycle；返回后 +1 metadata edge，最多 4 waiter notifications/core-cycle | DH 没有忽略所有返回服务，但与 CH 不等价 |
| 数据收集与完成 | L1 latency HIT 队首直接更新 pending writes/scoreboard；miss 走正常 WB | gather 4 个 32B sector/core-cycle；ready 同周期不能 gather，最后 gather 后至少过一周期；1 instruction retire/core-cycle，仍请求共享 operand collector | DH 有 gather/WB 代价，不能声称每一服务维度都更快 |
| 数据容量/物理面积 | 96 KiB、768 conventional lines，24 ways ×32 sets | 80 KiB physical data、512 logical Tags、64 sets ×8 ways、额外 refs/PIB/仲裁 | 不等容量、面积与电路时序；结果属于完整模型对比 |

核查源为 `shader.cc:2525-2572,3286-3394,3529-3596,3738-3849,3949-3956,5104-5137`，`dtc-l1-common.h:59-113,709-790,833-861`，`shader.h:2151-2155`。DH cacheable load 未经过相同 20-stage conventional latency queue，也未发现为其补上同等固定延迟；但其余显式服务代价真实存在。**因此已确认路径不同，尚未证明传统模型低估吞吐或 DTC 高估真实硬件能力。**

DTC ready→complete 均值只涵盖“所有所需返回/通知已满足”之后到完成的后段，不含先前 Tag、网络与 DRAM 等待。不能直接与传统 20-cycle 参数相减。完整服务求和与计数器分母保存在 JSON。

## 其余正例

**3DCONV：** 254 个 `_Z20convolution3D_kernelPfS_i` kernel、65,024 CTA；CH→DH cycles 2,958,083→2,200,332（1.344380×）。CM/CH 精确为 1，DM/DH 仅 1.015880×。L2 读量下降 5.038%，DRAM 读量同为 64 MiB；传统 278,428,752 个 merge-full 事件与 DH 5,258,451 个 pending hits 是关联证据，不是独立因果证明。不同 kernel 的所有原始 cycles 和计数器末值位置均在 JSON cells 中。

**particlefilter_naive：** 输入参数 `_x_128__y_128__z_10__np_1000`；9 次 `_Z6kernelPdS_S_S_S_S_i`，共 72 CTA。CM=CH=511,136 cycles，DM=DH=384,601 cycles；Hash 严格零收益，CH merge-full=0、DH Tag evictions=0。DH 有 157,266 valid hits、7,594 pending hits、仅 903/168,351 个 OO retire；因此“Hash、merge 上限解除、频繁 Tag 淘汰保留、广泛 OO 退休”均不能单独解释 1.329×。最有价值的候选解释是命中路径时序/完成服务与少量流量合并差异；这是 UNPROVEN，不能直接写成结构收益。DH load-service ready→complete 均值 2.1823 core cycles（167,775 loads），是后段延迟而非完整访问延迟。CH/DH DRAM 读量都只有 64 B，不是大量 DRAM 带宽收益。所有 9 个 kernel 均变快，不能只挑最有利的一个。

**3MM/GEMM：** 同设计 DM→DH 是合法 Hash 控制：只有固定 bank-preserving XOR 选项改变，3MM/GEMM Tag evictions 分别下降 78.697%/80.749%，下行创建请求下降 78.265%/79.484%，cycles 下降 23.878%/22.897%。这些是强映射敏感性证据；零 DRAM read atoms 表明这里的读流量改善是片上路径，不可写成 DRAM 读量下降。CH→DH 也仍包含 MSHR/PIB/完成时序/容量等设计差异。

## 计数器语义与不能作的运算

1. `DTC_L1_baseline_mshr_merge_full_events` 从 cache failure events 聚合；`nonexclusive_mshr_merge_full_cycles` 只是把同一个值换名打印。2DCONV 的 315M 甚至超过 64 SM×1.549M GPU cycles，不能当 GPU stall-cycle 并集，也不能从总 cycles 相减。
2. `DTC_L1_oo_pending_hits` 是 logical 128B reference 命中 pending physical generation；CH `L1D_total_cache_pending_hits` 是 conventional cache request 状态，分母与粒度不同，不能直接相减来计算“消除多少重复请求”。
3. DH `L1D_total_cache_*` 主要覆盖剩余 conventional fallback/store 路径，不覆盖 OO cacheable loads；不能把 DH 这个计数当完整 DTC L1 miss/hit rate。
4. L2 读量使用相同下游 `GLOBAL_ACC_R` 接受状态的 32B sector 聚合（保留完整 traffic buckets），不是 128B unique line。DRAM 读量使用各 controller issued read atoms×32 B，不是 `n_req` 或 unique request。
5. OO out-of-order retire 只定义为存在更老未就绪 entry 时退休；并不说明提前了多少 cycles。Tag eviction 是目录映射替换，不等同 DRAM cache miss。
6. 所有缺失计数器为 null/MISSING。原始失败、HOLD、pending、修复验证不进入这 20 个原始 accepted cell。

## 最小后续区分实验（只设计，未启动）

- **优先 1：2DCONV 与 particlefilter_naive 匹配命中/完成服务消融。** 原始配置另立合同，给 OO cacheable hit 引入可流水化、吞吐保持的等延迟对照，保证 miss ownership、Hash、trace 与其他队列不变；同时记录 admit、Tag、ready、gather、scoreboard release 时间戳。用 CH、DH、DH-matched-service 的变化判断短服务路径的份额。禁止简单串行 sleep-20 冒充同吞吐匹配。
- **优先 2：2DCONV conventional merge 上限对照。** 固定 CH geometry/Hash/timing，把 per-address merge 8 扩到预先约定上限；记录地址级 occupancy/reject 和每 SM blocked-cycle 并集。此实验改变资源预算，结果只能证明 merge 敏感性，不能声称等面积。
- **优先 3：固定有限服务下的 OO/IO 退休对照。** 保持 Tag、physical pool、PIB 和返还/collect 端口匹配，只改变可退休项选择；原 quartet 没有这一消融。Tag/Data 保留可以用单独 retain/reclaim 操作事件证明，但不能仅凭总 Tag evictions 归因。

以上均为 `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED`。当前 PQ/PS 不覆盖上述正例与服务匹配问题，不重复发送或控制它们。

## 可追溯性

`POSITIVE_CASE_MECHANISM_REPORT.json` 的每一个 cell 包含完整 input SHA、cohort/UUID、真实 Core/Framework/binary、实际 argv、config path+SHA、effective options、原始 spec 的旧声明、accepted result/strict/DONE/archive/launch 位置与 SHA、raw 压缩及解压 SHA、kernel 身份及 cycles、计数器最终原始行号。运行身份来自 actual launch+strict；spec 的旧 binary 声明独立保留，不覆盖真实执行身份。`SOURCE_SEMANTICS.json` 提供精确 Core commit 源码全文 SHA 与逐行证据。`RAW_EVIDENCE_EXTRACT.json.gz` 保留 20 个已关闭原始 raw 的逐项提取（仅解压读取验证，未修改原文件）。

正式引用须保留 registered-trace scope：完整 trace 验收不等于新授予完整应用或数值正确性认证。23/42 覆盖率和其它负例由 Agent A 报告，五个正例不产生新的总体 GM。
