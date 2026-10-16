# Round A75｜R-A75 主流GRPO后训练完整阶段 Discovery（109）

日期：2026-10-16；执行者：Codex／R-A75。固定启动`1eb14b0395bc898c3707ba850c36f17a9ec07b4e`；科研协调起点`05c1722066bda6a079d92fdfca34bdd28249a72f`。**终态：SOFTWARE_NEARBY_NO_SURVIVOR / STOP；推荐0、备选0。**

本轮把Qwen3真实RL训练步及完整group边界放回当前强软件审视。生成加速、合法组流水、弹性GPU池及有滞后异步都有直接近邻；当前证据尚未将一个新限制定位为芯片内服务需求。这里的0是限定研究范围的判断，既不是RL全域硬件否决，也不是原生负结果。没有为0候选重启模型、native或模拟器。

## 0. 合同、任务与来源层级

已完整读取本Goal0—5节，执行共同合同及R任务；完整读取A75研究笔记0—4节（连同其固定身份披露）、当前状态及协调协议1—8。A74-C的PPA/SM100停车边界、A72四线source-only结论保留；不再调研vLLM通用adaptive verification，不接管D的视频任务，不等或轮询D。独立sparse worktree/branch、私有output/tmp，提交只限本R四文件。

科学对象是**Qwen3-8B RL-Think／Qwen3-8B-Base RL-Zero、DAPO-Math-17K训练与AIME-2024验证的GRPO完整循环**，不是静态推理或缩维proxy。论文的checkpoint revision、采样K/温度、batch与native precision等未充分披露项在证据中保留，不从别的recipe或模拟器FP8配置补造。

源码审计固定NeMo RL [`540d2568c9cd184e01964c7de0a42026334f0a38`](https://github.com/NVIDIA-NeMo/RL/tree/540d2568c9cd184e01964c7de0a42026334f0a38)、Libra [`506a54edf3854fbf25537a758707df83a623e1c2`](https://github.com/NetX-lab/Libra/tree/506a54edf3854fbf25537a758707df83a623e1c2)。**此代码snapshot不自动等于论文原运行SHA**。主要原文实验组及源码/文档分别标`AUTHOR_NATIVE`、`AUTHOR_SIMULATED_PROJECTION`、`VERIFIED_CODE`、`FIXED_AUTHOR_GUIDE`；本轮只有源审与CPU算术。详细字段/路径/版本/未披露项见[STAGE_EXPERIMENT_GROUPS.tsv](STAGE_EXPERIMENT_GROUPS.tsv)。

## 1. NeMo原生Table1与完整阶段分母

[NeMo论文2604.26779v1 §3/Table1](https://arxiv.org/html/2604.26779v1)的部署为8节点×4 GB200，每GPU186GB；Megatron训练＋vLLM rollout。默认spec组使用同训练域初始化、固定offline EAGLE3、k=3。R01—R04逐项对回原表；不是在线draft、async或235B模拟组。

| Stage，平均秒/step | Think AR | Think EAGLE3 | Zero AR | Zero EAGLE3 |
|---|---:|---:|---:|---:|
|Data|0.3|0.2|0.2|0.2|
|Prepare|2.1|1.6|1.9|2.1|
|Generation|133.6|87.0|100.0|56.6|
|Logprob|17.9|18.1|17.8|18.1|
|Training|31.4|30.5|31.3|30.5|
|Overall|185.3|137.4|151.2|107.5|

表内阶段相加等于overall；精确比值为1.3486×与1.4065×。优化后generation占63.3188%/52.6512%，logprob＋training均48.6s（35.3712%/45.2093%）。这些是**DERIVED作者同步wall份额**，不是单GPU的TC/HBM/SFU忙闲比例、每GPU峰值或可直接交换的硬件配额。

Reward在原表没有独立行，不能视为0，也不能硬从某行拆出其时间。当前`grpo_sync.py`则有单独`reward_calculation`和`advantage_calculation` timer；源码不同快照的timer名不能代替论文raw时间归属。Prepare含权重同步/后端准备；训练含优势与优化。完整未来周期还需说明起止policy版本、权重发送和接收完成、KV失效/恢复，以及验证/保存的摊销，不能只测GPU optimizer完成。

[NVIDIA作者说明](https://research.nvidia.com/labs/nemotron/rl-speculative-decoding/)与论文区分8B实测和235B投影，并强调draft alignment与验证开销。较好in-domain固定drafter已经是必须比较的软件基线；更高acceptance并不自动更快，在线维护也不是免费收益。本轮不把质量曲线接近升格为逐token、逐梯度或optimizer state bitwise一致。

异步组另列R05：16节点、12generation／4training、lag1，75.0→60.5s effective step；暴露generation10.4→0.6s。该分母已改变，不能把全量同步87s再加到并发train/logprob上。R06的235B／512或2048 GB200、FP8数字来自作者专用性能模拟器；没有本轮native或Accel-Sim权威，也未运行任何模拟器。

## 2. NeMo当前source能力、互斥与版本合同

| 审计项 | 固定源码/文档与已核事实 | 科学后果 |
|---|---|---|
|Generation-only/offline EAGLE3|guide的`generation.vllm_kwargs.speculative_config`控制vLLM；trainer不拥有固定draft|可保留普通policy训练路径；仍需实际vLLM/模型/权重版本资格，不默认所有新AV机制可用 |
|Online draft|guide＋`lm_policy.py:209—251`：只Megatron；CP=1；packing允许，但packing时PP=1；与`use_fused_linear_logprobs=true`硬互斥|示例packingfalse不是“禁止packing”；不能拼packing/CP/PP/fused-logprob为无条件超级基线 |
|Teacher数据与梯度|`megatron_worker`、`train.py`有hidden capture、位置/segment对齐、DraftLossWrapper；guide描述detached teacher，worker区分draft grad-norm；online refit可导出`draft.*`|重用policy forward不等于省去policy backward；hidden/logits、draft LM head/optimizer与通信仍有成本。没有独立运行验证全部梯度不变 |
|Policy/reference/生成logprob|`lm_policy.get_logprobs`与reference API分开；`grpo_sync`生成token logprob、prev与reference分别读取；`_resolve_logprob_skip_flags`受force-on-policy、序列error masking及reference设置约束|不能把draft概率替代verifier政策概率，也不能随意关闭old/reference forward并称等价删除18.1s；reference skip另受KL条件限制 |
|权重发布|`refit_policy_generation`先sync deferred policy params；factory选backend transport；collective synchronizer等待sender/receiver futures并检查success；worker导出policy/draft|send启动、optimizer完成和新策略可见是不同事件；SGLang某export路径明确不接收trainer draft，不能照搬vLLM guide |
|同步TQ和CPU优势actor|`grpo_sync.py`有独立同步流程；SingleController `AdvantageActor`可移出controller；`advantage_stage`按group ID切完整组并对不适合布局fallback|group归属先于DP分片；CPU actor的等待不是GPU内核stall；不同entrypoint能力不可凭名字合并 |
|异步vLLM|guide要求async engine和non-colocated；collector跟踪generation/target版本；in-flight路径pause/refit/resume，可按flag重算KV；managedDynamo另有drain|允许lag、保留旧KV、重算KV不是同一训练合同；不能把Megatron支持colocated async外推到vLLM |
|当前recipe与论文身份|公开online Eagle recipe为真实Qwen3-1.7B、4prompts×4generations、8GPU、trainGBS16、MBS1、k3|这不是8B主论文的完整运行recipe，也不是RolloutPipe的K8；继承默认值未做launch资格，不能偷换 |

guide blob`cb8285334ba3eff9799eb4ae5c702f871b2bb233`与`grpo_sync` blob`cdb5f9471c6e73f98be58dac4150cc5bdfa26be5`回读匹配；其余少量文件也逐一验证Git blob及SHA256。以上为配置/数据流资格事实，**不证明任意组合在109或论文机器上已可运行或最优**。

## 3. 同变量的直接强近邻与合法group

### RolloutPipe：同轮固定采样策略、完整group流水

[2606.26997v2 §3—5](https://arxiv.org/html/2606.26997v2)核定Qwen3-1.7B；训练池8×RTX4090-24GB（TP4/DP2），rollout池2×A100-40GB PCIe（TP2/SGLang）。四任务LSAT-AR、Sci-XW、Sci-JL、OlyPhys；K8、B16、U2，Slime/CGP/CGP+FGD同init与超参数，每点4轮均值和sample SD。R07—R09保留各R边界：

| R（prompt groups） | responses=R×K | U-group logical updates=R/2 |
|---:|---:|---:|
|32|256|16|
|64|512|32|
|96|768|48|

同组K个response须完成reward/verifier、组统计、advantage和mask后才可训练；不是单条先结束就合法。同轮rollout权重固定，trainer按原logical-update边界更新，每轮全部group消费后才刷新rollout权重。这是匹配原serial基线的合同，不等于每个optimizer更新后都即时采样最新权重。

主分母是rollout-start→train-end；R32组缩短30.7—32.9%、R96组39.8—42.3%，不是每GPU内核加速。相近response长度／active trainer compute支持“改变工作放置”的作者解释，不能据此证明逐梯度同轨迹。next-round权重可见ack未单独给出，不能自动升级为含发布、验证/保存的全事务。本文只核HTML披露的数值，不从图中补造R64各任务标量。

### Libra：固定总资源预算下，分池与弹性本身已有软件

[2606.03077v3 §6—7](https://arxiv.org/html/2606.03077v3)的GPU组为48×A800-80GB、NVSwitch/200Gb/sRoCE；Qwen3-14B/30B-A3B、GRPO、16samples/prompt、最大40960、one-step async，包含DAPO/Search-R1/R2E-Gym，比较静态、同池与动态强基线。native precision、逐panel模型映射与exact checkpoint未充分转录，未补造。160NPU组保持独立，不复制最高倍数当GPU结论。

固定source确有staleness capacity和完整n_samples组收集；失败/拒收、timeout返回完整组构成的部分batch、pending组边界等属于训练数据/质量合同，不能当“同样数据更快”的无条件证明。原文资源管理与worker transition已直接覆盖普通pool比例/弹性建议；它不提供当前问题的芯片内因果证据。另用[AReaL v5 §4—5](https://arxiv.org/html/2505.24298v5)核语义边界：混合policy版本需要staleness与objective处理，不将它的PPO变体或最终质量相似拼进同步GRPO当无代价组合。

## 4. 本轮选定变量与三类相反解释

**唯一保留的阶段变量：策略版本v推进时，真实输出长度与complete-group就绪前沿如何改变有效token训练微批的供给/服务比。** NeMo RL-Zero的早期step由短输出向更长推理过渡是作者观察；本轮没有生成长度分布或取模型数据。该变量需要同时保留group ID、K、每样本采样/训练/KV版本、reward、mask、effective token数与microbatch划分，不能只比较generation平均占比。

| 解释 | 能区分它的事实 | 若成立如何分类 |
|---|---|---|
|Q：纯排队/算法就绪|缺完整K组或版本/weight ack未合法；没有ready训练工作；idle与组前沿缺口一致|不能用增加SM/L2改善没有就绪工作的间隔 |
|S：强软件分配/流水|已有完整组但仍挡在barrier/FIFO外，或pool/TP比例不当；CGP/FGD/planner后wait下降而active compute近似|直接软件邻居已覆盖，不能换pipeline名晋升架构 |
|D：实质设备级需求|在同一合法ready batch、固定梯度/采样合同与强可兼容内核后，活动设备window仍有独立可重复的计算/内存/通信服务响应|才值得之后审芯片/设备资源；阶段wall、GPU整体idle或利用率标题不足以定位 |

当前直接反证主要支持Q/S的已知解释；没有在D层形成新的可检验芯片内约束。也不能反向说D永不存在。本轮拒绝的弱动机是“rollout占比高所以改芯片比例”、“训练池空闲所以GPU执行低效”、“可重叠所以硬件需要新pipeline”。不是仅因本轮不能GPU就机械交0。

## 5. 数据、质量与独立验证门

[DAPO固定README revision](https://huggingface.co/datasets/BytedTsinghua-SIA/DAPO-Math-17k/blob/65877096c24ffa7abc4e4fa5edb95cf3413a5674/README.md)标Apache-2.0；“17k”不能当去重后的实际行数或独立题目数。本轮没有下载payload、接受条款、验证sample ID或训练数据窗口。

AIME-2024官方README/固定commit说明含32次重复以支持Best-of-32一类指标；不能将重复行当独立验证题，也不能从该数据卡推断NeMo实际eval采样器。论文质量曲线是作者结果；数学上的verifier采样分布保证，也不能直接等同不同batch/seed的逐token、梯度及optimizer状态一致。

未来如存在新问题，必须先冻结：原模型/权重与draft身份、数据revision与problem-ID去重/overlap、sampler温度/top-p/长度截止、K/group/materialization、reward/verifier、KL/IS/ratio与mask、microbatch/global-update/weight-publish边界和数值门。低精度、lag、旧KV保留及提前缺组训练都是科学合同变化。AWMA参考梯度重复性STOP不继承为RL负结果，但提示baseline自身重复性应先核，不放宽原数值门。

## 6. 条件式最小反证方案（模板，不是推荐卡或执行授权）

0候选时`QUESTION_CARDS.json=[]`，不申请新资源；以下连续模板只说明怎样将一个未来真实阶段变量归类，而非自动创建后续Goal。

1. **自然基准**：先source资格，保持NeMo主对象真实Qwen3-8B／Base与DAPO/AIME身份；另获模型/小数据/训练批准后，在同一baseline自然训练轨迹保存早期/过渡/后期少量合法完整group及policy/optimizer/sampler状态。离线固定rollout bank仅作设备诊断，不冒充在线学习进度。不能换任意缩维模型或合成热点。
2. **可兼容强配置**：sync零lag与async bounded-lag分开；先比较真正可用的in-domain fixed-EAGLE3 k3与同合同强实现，不强塞互斥online-draft/fused-logprob/CP/PP。若用RolloutPipe式CGP/FGD，保持K8/U2及相同logical update、sample集合与发布边界；它在不同系统的复现不能与NeMo百分比相乘。
3. **计时/设备诊断**：记录每group就绪、奖励/优势、入train队列、实际训练、发送权重、receiver ack与next-rollout-policy-ready。完整周期以一致版本边界计wall；data/reward CPU与GPU活动window分开，nested/并发timer用wall union。相同ready group上的合法packing/已有最佳kernel对照，先区别Q/S/D；移除另一阶段只是诊断，不称完整训练加速。Profiler/资源扰动若需要必须另获批准。
4. **数值/质量与holdout**：先同baseline重复性，再比较相同samples、reward、advantages、mask、old/reference logprob、全梯度及optimizer状态；容差先冻而非看完再放宽。完整自然训练另核学习曲线和准确率/固定质量所需wall。holdout用未选参题目/group与独立策略checkpoint；AIME按独立problem-ID与预冻采样指标留作质量验证，先检查DAPO/draft数据重合，不把重复32行称32个holdout。
5. **资源与STOP**：10916GiB不能承担作者32GB200完整8B训练。仅按8×10^9参数量级和假定BF16估算，权重＋同精度梯度已约29.8GiB；若再计FP32 master和Adam moments，参数/梯度/优化器payload约119.2GiB总量，尚不含activation/reference/draft/rollout KV。此为明确假设的容量推导，**不是作者native precision或峰值显存**；单32GiB也不能据此认定完整可行。未来须给实际sharding/offload/互联与多GPU预算，不能先申请后选问题。若合法group/版本/数值不守恒、强软件已消除新残余、差异只来自队列/组缺口、holdout无效，结束；若只剩软件优化，报告软件。不存在D类可复核变量就不进入芯片机制。

## 7. 自审、资源与发布

四份轻量交付是本REPORT、STAGE_EXPERIMENT_GROUPS.tsv、QUESTION_CARDS.json、RECEIPT.json。源码只读文本/AST，没有import外部模型栈、执行actor/训练/rollout、运行任何模拟器或Profiler；CPU只核Table1守恒/份额、R*K/R/U及常数大小8奖励归一化依赖示例。示例不是实际rollout，也不是GRPO实现的std/epsilon合同。

任务工具单CPU worker，affinity7（既有shell允许、未重绑其他任务），OMP/BLAS/Git pack/index为1；独立tmp/output，实测RSS与累计下载/新增盘见收据。未接触GPU锁、164、模型盘、数据/权重、安装/构建或清理。`.private/`只保存本Lane可追溯材料，由worktree独立excludesFile排除；没有git clean/gc/repack/reset。

提交前后校验TSV/JSON、引用、少量source blob/SHA256、diff与唯一输出路径。commit、push、单次fetch-back核最终commit/tree/四blob并确认clean，精确结果私存readback及用户回执，避免receipt自引用。正常完成后STOP，不等待D，不自动native，也不把未获资源当芯片性能负结果。
