# Round A4｜训练源审：MegaScale-MoE 扩展证据与准入裁决（174-new V1）

**范围：CPU/source-only；证据级别为 PAPER_AUTHOR、SOURCE_AUDITED 和 OUR_INFERENCE，无本机 GPU、训练或模拟器结果。** 结论：**NO_NEW_TRAINING_PROBLEM_QUALIFIED**。352B 多机扩展是作者报告的真实训练实验；自然训练输入、逐点并行配置、微批和气泡/暴露通信时间不足以资格化新的单卡 P01/P13 问题。

## 1. 来源、去重与工作环境

主论文为 [MegaScale-MoE，arXiv:2505.11432v3，2025-10-17 / EuroSys 2026](https://arxiv.org/html/2505.11432v3)，核 §3–6、Table 2/3/5、Figure 12/13/16–20；[PDF](https://arxiv.org/pdf/2505.11432v3)第 9 页核 Figure 12 图内数值。作者固定对照为 [NVIDIA/Megatron-LM@f1f039224584f0bc6ba89c21ef4f491d7136e3ce](https://github.com/NVIDIA/Megatron-LM/commit/f1f039224584f0bc6ba89c21ef4f491d7136e3ce)。仅查此 commit 的 [arguments.py](https://raw.githubusercontent.com/NVIDIA/Megatron-LM/f1f039224584f0bc6ba89c21ef4f491d7136e3ce/megatron/training/arguments.py)、[schedules.py](https://raw.githubusercontent.com/NVIDIA/Megatron-LM/f1f039224584f0bc6ba89c21ef4f491d7136e3ce/megatron/core/pipeline_parallel/schedules.py)、[distributed_data_parallel.py](https://raw.githubusercontent.com/NVIDIA/Megatron-LM/f1f039224584f0bc6ba89c21ef4f491d7136e3ce/megatron/core/distributed/distributed_data_parallel.py)、[num_microbatches_calculator.py](https://raw.githubusercontent.com/NVIDIA/Megatron-LM/f1f039224584f0bc6ba89c21ef4f491d7136e3ce/megatron/core/num_microbatches_calculator.py)，未克隆或执行。

先读本分支 [Round A3](../literature/AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md)、[Round A2](../literature/AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)、[证据索引](../AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)、[协调规则](../COORDINATION_PROTOCOL.md) 去重；AWMA [Round09](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md)和[Round22 ledger](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)仅作已审范围指针，不重审 R24–R27 或恢复其任务。

174-new 启动前：512 逻辑 CPU，load 2.92/3.68/3.71；377 GiB RAM、available 347 GiB；2 GiB swap 已满；根盘约 14 GiB 可用、inode 使用 8%。进程表无活跃高 CPU 任务，有旧 AWMA 监视 shell 和其它 SSH 窗口，故仅进行轻量文本源审。远端目标分支初始 HEAD 等于协调起点 **4631fd56248bd23451b302401c07c625c920d593**；独立 worktree 为 /root/workspace/accel-sim-framework-aiarch-a4-training-source-174-v1，未切换原工作区。

## 2. 352B 实验身份与控制表

[Table 2](https://arxiv.org/html/2505.11432v3)：Internal-352B 为 60 层、hidden 4096、32 attention heads、query/KV head 比 4、expert FFN hidden 14336、32 experts、top-3。§6.1 给 sequence length 8192、vocabulary 65536、H800。这是内部多 GPU MoE 训练，不能用单卡的虚拟 352B 形状代替。**训练语料名称/版本、真实 token 序列与采样顺序、tokenizer 资产、seed、输入分布和可获取位置：UNDISCLOSED_IN_CHECKED_VERSION。** “Production”只说明作者部署背景。

| 组 | 论文明确固定 | 变化/软件选择 | 未披露 |
|---|---|---|---|
| Table 3 强扩展 | 352B 配置、seq 8192、global B=720、H800、PP=15；同点两系统 B 相同 | GPU 240/480/720/960/1440；Mega attention SP、expert EP 限节点内；Megatron 以节点内统一 TP；两系统各自选最优并行配置 | 各 GPU 点确切 TP/SP/EP/DP、micro-batch size、虚拟 PP stage 数、launch 命令、352B token 身份 |
| Figure 12 弱扩展 | 同模型、H800、PP=15；同点两系统 B 相同 | GPU 480→1440，B 360→1080 同比例增加；图含 720/960 GPU | 中间 B 未由正文逐点明列；各点并行宽度与微批、输入 token |
| Figure 13 不同模型 | Mixtral-8×7B，32 GPU，DP=4；对照 TP=8，Mega SP=EP=8 | GPU 类型 H800/A100/H20 | 这组 DP/TP/SP/EP 不可搬到 352B |

若另外假设每个 PP stage 有效模型并行宽度 q=8，352B DP 才按 GPU/(15q) 算出 2/4/6/8/12；**这是条件算术，并非论文逐点披露**。TP 与 EP 分组可重叠，未知宽度不能直接相乘。固定 Megatron 源码的微批公式为 M=B/(DP×b)，其中 b 为 micro-batch size。论文未给 b 与逐点 DP，故不反推 M；仅在 q、b 跨点不变的额外假设下，强扩展 M 会减少、弱扩展 M 可维持。这不等于测得的每 stage ready 队列或 bubble 比例。

## 3. 强扩展、弱扩展、气泡和通信暴露

| 定位/级别 | 原始指标或作者说法 | 可支持 | 不能升级为 |
|---|---|---|---|
| Table 3，PAPER_AUTHOR 实测 | 强扩展 B720，240→1440 GPU；Megatron iteration 39.94→7.90 s、吞吐 151.1k→746.6k token/s；Mega 21.61→4.19 s、272.9k→1407.7k token/s；Mega/Megatron 同点 1.65–1.88×；Mega MFU 32.48%→27.89% | 固定 global B 时整体吞吐增加而效率下降，Mega 同点更快 | 单独的 PP bubble、ready task、通信或物理计算资源因果量 |
| Table 3，PAPER_AUTHOR 估计 | 1T token 所需天数：Mega 240/1440 为 42.41/8.22；Megatron 为 76.61/15.50 | 按短段吞吐的换算 | 已完成 1T token 的真实训练墙钟、收敛或质量 |
| §6.1，PAPER_AUTHOR 解释 | 作者称固定 B 时每 pipeline 的 micro-batches 随 GPU 增加而减少，bubble 因而增加 | 明确的机制解释 | 论文没有 352B 每点 b/M、逐 stage bubble 时间线或隔离气泡消融；解释不是直接测量 |
| Figure 12，PAPER_AUTHOR 图值 | 弱扩展 480/720/960/1440 GPU normalized throughput：Megatron 0.574/0.566/0.564/0.558，Mega 1.000/1.000/0.997/0.998；作者报告 2.74% 与 0.2% 降幅 | 同比例扩大 B 时，Mega 归一化吞吐更稳 | 绝对 token/s 下降；作者把 Megatron 降幅解释为通信，图未给逐点 exposed communication |
| Figure 13，PAPER_AUTHOR 不同模型 | Mixtral-8×7B、32 GPU，H800/A100/H20 iteration breakdown 中 “Exposed Communication” 定义为未被 compute 重叠的通信时间 | 原文确有暴露通信的可测量定义及另一个模型的分项 | 352B 强/弱扩展每点的通信分解或单变量硬件资源实验 |
| Table 5，PAPER_AUTHOR 累积消融 | 240 H800、352B、B720，Mega 内部 TP+TP/no-overlap baseline=1；加 SP+EP=1.13；再加 inter-op overlap=1.22；再加 intra-op overlap=1.28 | 此条件下并行策略和两级重叠都影响吞吐 | +13/+9/+6 不能当独立可加 speedup；此内部 baseline 不是 Table 3 固定 Megatron 二进制 |

表值一致性注：Table 3 的 240 GPU Megatron 39.94 s×151.1k token/s≈6.034M token/iter，而 B720×seq8192≈5.898M；多数其它点较接近后者。保留作者原表值，不重算成替代数字或据此提出新性能结论。Figure 12 的 2.74%/0.2% 为归一化扩展效率，不是绝对吞吐的下降。

## 4. 最强软件基线、真实性与数值/质量

作者 §3–5 已提供节点内 SP+EP、inter-operator 调度、tile 级 intra-operator overlap、selective activation rematerialization、BF16 DP 梯度通信压缩与 FP8 路径。§4.2 明说直接依赖的前向通信若靠额外 micro-batch 重叠会增加激活容量；其 tile 通信与 ready 通知已有软件实现。Table 5 是累积消融，不表示尚有同幅硬件余量。

Table 3 的公开最强对照是作者固定 Megatron-LM commit，加双方均启用的既有 MegaScale DP/PP overlap，并为两系统各选并行配置，非朴素串行基线。固定源码确有 interleaved 1F1B、PP P2P overlap 参数、DP gradient async overlap 与微批计算器；**源码仅证实能力存在，不证明论文逐项 launch 开关或精确配置**。论文说 DP/PP overlap 在双方启用，但未给 352B 完整运行命令、调优搜索记录和 MegaScale-MoE 可审源码，独立复现 baseline 等价性仍缺证据。

数值与质量须独立审：§5 BF16 梯度压缩保留局部 FP32 累加；Figure 18 loss 对照是 **7B** MoE；Figure 19 BF16/FP8 收敛是 **35B 从头训练、176B checkpoint 续训**；Figure 20 的 200B 生产 loss 也不是 352B Table 3。该表未逐项披露 352B precision、目标 loss/任务质量合同、完整训练轨迹。1T 换算天数不是收敛证据；短 loss 曲线不代替梯度/优化器状态和长期质量验收。

## 5. P01/P13 可辨识性与科学 STOP

| 资源轴 | 原文有的控制/测量 | 仍缺 |
|---|---|---|
| compute | Table 3 固定 H800、改变 GPU 总数；Figure 13 跨 GPU 型号真实 Mixtral breakdown | 跨 SKU 同时改变算力、内存、NVLink；未隔离单卡 SM 数或计算能力 |
| communication | Table 5 策略/重叠累积干预，Figure 13 暴露通信分项，Figure 16 局部算子时间 | 352B 各扩展点的 exposed communication 与关键路径分母 |
| pipeline occupancy | PP15、固定 B 强扩展、MFU 两端与作者 bubble 解释 | b、DP、逐 stage ready 微批数、调度及 bubble 时间线 |
| activation capacity | §4 rematerialization；Figure 17 的 Mixtral-8×7B/22B SAR vs No SAR：activation memory 减 45.5%/57.2%，总内存减 21.3%/35%，性能差在 0.5% 内 | 不是 352B 的容量响应；也未隔离多一微批的容量成本 |

**P01：** 可记录“固定 B 扩展效率下降、同比扩 B 接近线性”的作者系统现象；尚非独立 ready 任务数的因果曲线。**P13：** 网络、pipeline 填充与激活容量耦合；无单变量增加 SM、片上缓冲、计算或网络带宽的 352B 控制组。109 单卡无 PP15、跨节点网络或 352B 自然输入，不可验证同一曲线；构造类似矩阵形状也缺完整训练语义和时间分母。

**NO_NEW_TRAINING_PROBLEM_QUALIFIED / SCIENTIFIC_STOP。** 不登记新小模型 source-only 候选：论文虽列 Mixtral 等公开模型配置，本次所查组未披露可固定自然训练语料/token 流和同语义完整强基线命令。后续若重审，最少需合法自然输入版本/采样记录、两系统逐点 launch 配置（TP/SP/EP/DP、micro-batch、PP virtual stages、precision、开关）、同一时间边界的逐 stage ready/bubble 与 exposed communication、activation peak、可审数值和质量合同。此证据到位前不产生 GPU Goal、训练或旧实验恢复。
