# EP-L2 / ISCAS2027 r19 — 下游减压受控实验立即推进，与论文并行

2026-10-17。用户明确要求主动尝试解除下游压力，检验机制有效性/适用边界，并行推进实验与论文。**本合同将r18的“诊断设计待审”推进为下述有界配置实验的执行范围；不等待EN-v6完成。** 用户将本指令发给既有Lane1/Lane5/Lane6后各自执行；GitHub发布本身不启动服务器任务。若窗口已结束，在原worktree/分支开始新有界CONTINUE；若还在执行，增量续接而不重启。

## 0. 主线、不可变证据与目标

当前基线：Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`，Framework producing `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`，vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`，binary SHA256 `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`。五组原条件H0已在Lane5 V2 generation8科学接受，原数据包 `e6714dadb6cd5deb45185939a1bb3a2c488892c3:docs/ep_l2/review_packs/FT20261017_LANE5_R0_1_A1_B1_PRIMARY_COHORT_r1`；最新核对Lane5 HEAD `534338ed2219a3e719189c470414152987795fd8`。H0五组geomean1.0016002037656606是必须保留的事实，不能用新的敏感性结果覆盖。

Lane1原发布 `05145b19cc7c165ef8ae448b14324585dfa286ef`，Lane6目前 `62e0972863aab5ba2e391e6d6dcfe221d7ab80ae` 仅独立数值接收SAD，另四组metadata已备。执行前重新核查HEAD/STATUS/RECEIPT、真实PID/registry、两个写盘文件系统；上述是快照而非实时许可。

**要回答的是：** 下游服务速度/缓冲是否掩盖了U-WB的copy和配额改善？什么资源配比能产生可复现的应用收益？更快下游也可能缩短B16的WB驻留、减轻原配额压力，所以收益不一定随下游速度单调增加。应查找并解释适用区间，而不是预先要求“无限快内存一定使U更好”。

## 1. 本轮已核读源码对应的实验旋钮

- 原有序overlay `tests/ep_l2/b0_banked_d512_850.config`：队列 `64:128:64:64`，FR-FCFS scheduler128、DRAM return192，时钟 `1132:1132:1132:850`。
- Core `l2cache.cc` constructor明确队列依次为 **ICNT→L2 / L2→DRAM / DRAM→L2 / L2→ICNT**。不能只凭字段名称猜顺序。
- `arbitration_metadata` 下游共享credit上限来自scheduler+return-(subpartitions-1)。原两subpartition时为319；下面Q4为1279。扩缓冲也增大这部分下游credit，必须明确记账，不能称“只改FIFO、不改任何并发”。WAD128和D512不变。
- `dram_cycle()`从L2→DRAM队列向partition latency队列每DRAM tick至多接收一个请求，且会检查DRAM scheduler/return/credit。固定 `dram_latency` 的ready_cycle以 **gpu_sim_cycle+gpu_tot_sim_cycle** 计算。因此只提高DRAM时钟不会自动缩短这段100 GPU-cycle固定延迟。
- `gpu-sim.cc::memory_config::reg_options`已有 `-gpgpu_simple_dram_model`；`simple_dram_model_cycle()`走真实packet/credit/return/WB set_done，但绕过详细DRAM bank时序。它是后备低延迟诊断路径，不是已经验证合格的“无限带宽内存”。其c7e采样与详细DRAM不完全相同，禁止将未记录的统计当作0或把两种模型的带宽计数直接混用。

## 2. 首轮固定矩阵：两个代表负载，8个新full-application运行

代表负载预先固定为 **convolutionSeparable与FWT_7_21**：它们有明显B16 WBUF-full、U更高的下游阻塞；保留CFD退化和SAD负对照的原结果。每一种条件都同时执行B16_BANKED和U_WB16，原H0配对按完整身份验证后复用，不重跑已完成数据。

### H0 — 原始生产配置（冻结、直接复用）

- ICNT→L2 / L2→DRAM / DRAM→L2 / L2→ICNT = 64/128/64/64。
- scheduler128、DRAM return192、DRAM850MHz、固定dram_latency100 GPU cycles。

### Q4 — 只扩下游缓冲与由其推导的credit，不提升DRAM服务速度

在原五层有序config之后附加独立overlay：

```text
-gpgpu_dram_partition_queues 64:512:256:64
-gpgpu_frfcfs_dram_sched_queue_size 512
-gpgpu_dram_return_queue_size 768
```

时钟与dram_latency保持H0。原ICNT入口、L2→ICNT、L2内部miss queue、WAD、MSHR、Tag、Payload及bank服务完全不变。下游新增接收存储是额外成本，两模式相同，不冒充EP-L2零成本效果。Q4是成组的下游缓冲/credit对照，不能再将结果唯一归因于某一个FIFO。

### D4 — 在同一Q4缓冲上，将DRAM时钟域服务加速4倍

在Q4基础上再加：

```text
-gpgpu_clock_domains 1132.0:1132.0:1132.0:3400.0
```

Core、ICNT、L2时钟不变，DRAM buswidth/burst/atom size、bank数量、地址映射和DRAM timing的整数参数不变；`dram_latency=100`仍保留。**这是DRAM域速度敏感性，不是纯带宽实验，也不是声称现成硬件能以3.4GHz和原整数时序运行。** DRAM tick加速同时改变详细bank时序的物理时间以及partition服务频率，需如实报告。

### 执行顺序

先做两个代表的D4配对，尽快看明显减压后的反应；随后做Q4配对，拆分仅扩缓冲与实际服务提升的区别。每个配置先由Lane1确认有效字段并做必要定向，Lane5独立接受后立即启动；**不用等待所有后备条件或论文任务完成。** 无法获得资源时不持lease等待。

H0已有2负载×2模式=4个旧观察；Q4和D4合计2×2×2=**8个新运行**，构成两个2×3的完整设计。配置合法性/小定向不算应用样本。

## 3. 不是一次不显著就停：预先规定的有界继续规则

首轮后最多再选择下面**两个**条件（每条件2负载×B/U=4运行，最多8运行），选择依据先写入分支checkpoint：已测压力、固定延迟或驻留变化；不能只按哪个已见speedup较大挑结果。被触发条件的B/U必须都完成并保留。

1. **D8：D4后下游仍明显绑定**。只把DRAM域改到6800MHz，其它与D4一样。检查压力是否进一步显著下降、bank/返回/credit是否成为新的限制。D8仍只是模型敏感性，不是产品配置。
2. **D2：D4使B16原WBUF压力也基本消失，或需要界定有意义收益的服务区间**。DRAM域1700MHz、其余Q4，补中间点。更快下游可能同时帮助B16，不能只测极端值就说弹性无效。
3. **L25：D4仍受GPU-cycle固定接口延迟影响，或需区分详细DRAM服务与固定时延**。只在D4上加 `-dram_latency 25`。因此D4/L25可隔离这项固定时延变化。不能同时修改ROP延迟/SM吞吐/L2命中来使对照失去含义。
4. **LOWER_CEILING：明确解除详细DRAM约束的后备诊断**。仅当已有旋钮仍无法形成有用的下游非绑定情形/需要机制潜力观察时，考虑Q4+D4时钟、`-gpgpu_simple_dram_model 1`、`-dram_latency 1`。Lane1先证明该现有路径在读、WB实际lower accept/set_done、credit、response/drain、symbolic reference上的功能等价，Lane5新路径独立定向通过才允许应用。不得设置 `-l2_ideal 1`，不能免费丢WB、命中所有cache、取消所有返回或给L2增加端口。若此路径无法在本轮轻量闭合，停止该后备条件而不阻塞Q4/D4。名称只代表乐观诊断，不声称为严格数学上界或无限服务。

**只扩大队列，队列full变少但驻留/DRAM利用仍高，不等于下游压力被去掉。** 对比每条件中的full机会比率/窗口最大占用、服务完成率、WB staging与WAD lifetime、实际GPU cycles，保留源定义和分母。可将两主要下游full-block的归一化指标均下降约90%且其它下游资源没有替代成为主阻塞，作为“观测压力明显缓解”的预设工程判据；达不到只说PARTIAL_RELIEF，不能宣称非绑定。没有正确分母不伪造百分比，使用明确的原始计数与窗口证据。

选定一个解释清楚的条件之后，在 **vectorAdd_4M和sad** 上各补一对（共4运行），作为诊断稳健性及负对照，不称这两者为未见过的holdout。btree/dwt2d仍留作以后真正验证，不抢用。

本轮总上限 **24个新full-application运行**（首轮8＋最多8自适应点＋4补充配对＋最多4个必要完整输入canary）；不能拿用例/失败重试凑成功矩阵。T0起最多10小时或先完成矩阵即结束，阶段性发布；无新条件时不为了用满额度而多跑。单点超过原timeout则保留失败，不把时间裁剪变成完整样本。需继续扩展时依据结果另审。

## 4. 必须读懂的科学比较

对每个workload与下游条件h，计算：

- S(h) = C_B(h)/C_U(h)，表示**同一下游条件**下EP-L2的相对效果。
- J(h) = S(h)/S(H0)，衡量观察到的机制效果随下游条件如何变化。
- 同时给C_B(H0)、C_U(H0)、C_B(h)、C_U(h)与绝对delta；不能用C_B(H0)/C_U(h)当EP-L2 speedup。

若两模式都加快而S几乎不变，说明下游减压帮助了应用，但未显露更大的U-WB相对收益。若S提升且copy/Bank等待/配额/下游证据一致，支持“原下游服务掩盖部分机制潜力”；真实可实现的2x配置与极端D8/ceiling的解释分层。若下游已缓解但S仍近1，继续检查copy不在关键路径、WB驻留变短、前端/ROP/计算限制等实际原因，再决定强静态对照、TVD/RO是否更有价值。不要立即把原0.16%当方案最终结论，也不能保证新的减压一定产生更大加速。

Q4/D4/等条件**不替代原H0五对**，也不混入原5-workload geomean。只对完整同条件、预定义群组计算诊断均值。保持当前C1旧resident headroom禁用；WB-full事件和Bank累计等待不是互斥全GPU停顿，不能相加/从cycles直接相减。新增较快DRAM允许内存调度与WB数量变化，不强求模式间内部WB数量完全相等；独立instruction/request/data/lifecycle资格仍需成立。

## 5. 三个Lane真正并行，各自唯一owner

### Lane1 — 配置/语义与生产侧定向（现在恢复原窗口，短交付后可退出）

首先复用已通过31项的**同一个官方binary**，不因加overlay就重新完整编译。核读上述参数落点、有序覆盖、credit与固定延迟时钟域，生成Q4/D4精确overlay、禁止变更字段白名单、实际生效配置和针对读/WB/bank/credits的短定向证据。特别检查旧fixture是否在命令行后又硬编码队列/时钟，避免“测试PASS但没测试新配置”。保留原31项正确性，不再重复所有静态审查。

必要的小的测试入口/监测/证据包装改动可在隔离工具分支完成；若要改模拟器runtime算法、clock逻辑或返回语义，先报告新源与原因，**不能默默复用旧binary资格**。第一对D4有效即可给Lane5，不等所有后备实验。当前输出：`HEADROOM_CONFIG_MANIFEST`、有效参数dump、受影响定向范围与未覆盖项、代码路径/credit账。

### Lane5 — 唯一应用执行与独立验收（现在恢复原窗口，不等待Lane6）

并行准备原Convolution/FWT输入spec、已验证全trace/non-atomic/legacy语义证明、Q4/D4执行计划和current V2接收。Lane1逐条件交付后，对实际配置独立准入、运行并逐pair接受；其它安全准备可与sim并行。

现有`authorize_launch`按release/feature/ideal向量查许可，并不自动限制所有下游config值。本轮必须追加**显式配置白名单/条件manifest核验**：只允许r19确认过的完整有效参数，新的runtime_config_sha256产生新run_key。扩展是针对这些诊断配置的正向支持，旧unknown-config/撤回/输入hash/资源保护不能被跳过。沿既有V2/registry工作，不重新搭一套接受系统；必要的新qualified envelope绑定条件与受影响证据，保留旧envelope和H0接受原样。

准确区分`experiment_id=EPL2_DOWNSTREAM_HEADROOM_R19`、`regime=Q4/D4/...`；用完整run-key/config身份选择结果，不仅以workload+mode查“最新一行”而混掉H0。主case TVD/RO/Ideal开关均OFF；LOWER_CEILING为另记的内存模型诊断，虽然缓存ideal_vector仍OFF，也必须有新的下游路径资格，不能伪装成详细DRAM实测。

原11项科学要求保留，未变code/输入的既有证据可以按适用范围复用；只补新配置/clock/credit/lower路径受到影响的实际生产检查。各pair terminal独立64slice/request/WB/sector/drain、scope、pre/post身份验证，接受后立即交Lane6。维持最多2长期sim、原8CPU/32GiB登记及64GiB available RAM/48GiB workspace/40GiB Share门槛，DTC-L1/C16等用户任务不动。不启用迁移/新删除，不新建磁盘等待器。

### Lane6 — 写作、图表和结果解释（与上述两线同时进行）

先完成r18原H0五组独立论文侧接收、EN-v6主图；不能等D4跑完才开始写，也不能用诊断结果替换原0.16%。加入一节/一个有位置的“下游服务敏感性与交互”，每个新的CURRENT_ACCEPTED配对到达后事件驱动接收。默认/新条件图形分别标明，统一轴单位；合理保留negative、CFD退化、低速/高速所有已跑条件。四技术页+一参考页预算可用归并面板/精简计划性段落实现，不为装新图隐去H0。

优先解释“copy减少—WB配额—Bank服务—下游接受—周期”链条，新增PPA/静态重划分未执行仍待测；无需此时反复全文润色或新搜一大批文献。小配置问题或数据包装自行修正，不为了过度抽象审计推迟实际图/结论。最终交付主配置及headroom分开的完整数据表、可复算图源、英文稿修订与下一研究决策。

Lane2/3的已修TVD/RO候选与Lane4原Ideal矩阵保留，不将其尚未生产验证的机制混入此次mainline。Storage-Ops保持已完成状态。不需要六窗口都busy才叫并行。

## 6. 最小交付与停止边界

各Lane在自己的原分支和新revision中写STATUS/RECEIPT、准确source/config/trace/binary/条件身份和真实测试/应用计数，push并远端回读；不要每个小步骤新建一套平台。已有科学或配置证据不重复制造。参数本身合法且落在本合同范围内，普通工程问题solve-and-continue，不必逐个GiB/频率再次等待用户确认。

仅这些情形停止受影响条件：功能/atomic作用域改变、不可解释的request/数据/credit泄漏、需要修改原Tag/Payload/Bank预算、现有模型不支持该时钟/内存路径、实际host资源不足、超过本轮范围或所有者不明。**“在某个减压条件下speedup不大”不是工程失败**；继续完成同组B/U并按上述条件分支定位原因，而不是换输入或丢弃。

首要短期交付不是更长的实验设计文档，而是**D4的两个真实配对、Q4的两个对照配对，以及同步更新的论文证据**。
