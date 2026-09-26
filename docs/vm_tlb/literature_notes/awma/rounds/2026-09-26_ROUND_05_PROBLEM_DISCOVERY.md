# Round05｜动态AI执行：工作有效性与安全资源交接

日期：2026-09-26。维护：ChatGPT。**文献与研究设计笔记，不是执行Goal；未启动109/174实验、未下载模型、未运行论文代码。**

## 1. 决策与范围

核心15篇：13篇正文关键机制/实验/局限章节，2篇原始摘要；另2份NVIDIA官方文档。不是15篇全部全文精读，也不是15篇全部新增。正式会议PDF与所读arXiv版本分别登记。

优先核查R51“异步/persistent kernel安全交接代价”，把R52“在线已知失效后的推测工作”作为同组特例；R53扩散动态任务保留；R54循环checkpoint全成本、R55微缩放双方向表示低优先级。均为我们的候选问题，不是作者声称未解决的问题或已证明的硬件瓶颈。

P1/P2项目STOP与原始提交ce5918d837b76e95ad4000c50bbe1465707a2ebd保留；不重跑、不改原始结果。后续引用需收紧：未过3×CV不是统计等价证明；graph-online减eager-ready小于另测selector时间，也不能单凭大小关系证明全部残差来自算术。这些是推进门槛结果，不是整个领域被排除。

## 2. 原文能力与实验边界

| ID | 所读论文/版本与位置 | 已有能力/本轮核验的边界 |
|---|---|---|
| R501 | PipeInfer，2407.11798v1，IV-C/IV-D/V-A | 已在同步点取消失效推测；部分非推测工作须完成以提供有效KV。评估是CPU集群，不是GPU细粒度抢占。 |
| R502 | SMART，2604.09731v1，3–4 | 已按draft/verify代价与接受收益选择树；设备拟合不能当所有GPU复杂度规律。 |
| R503 | LithOS，SOSP2025会议PDF，Special Kernels/7，PDF第10页 | 对persistent或跨block同步kernel禁用atomization/stealing；单A100混部实验。 |
| R504 | GPREEMPT，ATC2025会议PDF，3–5，PDF第6页 | driver timeslice上下文切换及预提示；A100/MI100，非任意tile免费切换。 |
| R505 | ExpertPlex，2607.18002v2，4.2–4.3/6.4/7.1 | 修改DeepGEMM/DeepEP/SGLang，在tile提交后协调异步状态并切换；H800集群。 |
| R506 | MPK，2512.22219v1，4–6 | device任务图、调度、KV元数据管理已有；该版本worker/scheduler角色launch时固定；主评估离线prompt64/decode1024。 |
| R507 | PipeThreader，OSDI2025 PDF，Figure6/设计/6 | 归约分块、流水、片上容量联合优化已有；图中的1KiB是示例，不是硬件参数。 |
| R508 | Marconi，2411.19379v3，4/5 | 混合状态admission/eviction已有；cache指标配置与Jamba TTFT评估分开。 |
| R509 | Sparse Prefix Caching，2605.05219v1，5–7 | entry内exact稀疏checkpoint+后缀重放；原型只计Qwen3.5-0.8B层组，capture在独立不计时运行。 |
| R510 | Tail-Replay，2608.30310，原始摘要 | 近似恢复循环状态；正文未取得，不能视为exact方案。 |
| R511 | Nemotron-Labs-Diffusion，2607.05722v1，3–4/评估 | SOL先获串行最终输出再判断并行接受，不是可部署的在线跳算信号。 |
| R512 | BiCache，2606.07571v1，2.2–5/实验 | 固定token的深层KV仍可能变化；浅层复用+深层刷新已有；B200场景，非物理cache一致性故障。 |
| R513 | dInfer，2510.08666v2，2–4 | 解码、刷新、smoothing与可选蒸馏分别作用；8×H800，B1/gen1024/block64，不是纯runtime加速。 |
| R514 | Is Finer Better?，2601.19026v1，3–5/AppendixA | scale量化使更细block不保证更准确；质量评估不能作为格式转换时间证据。 |
| R515 | FIBER，2608.19628，原始摘要 | 线程—寄存器归属解耦已有直接硬件近邻；未依据摘要猜测全部限制。 |

官方文档：D501 CUDA Green Contexts的On Concurrency说明不相交SM分区不保证并发/forward progress；D502 Transformer Engine页面显示2.17.0，说明MXFP8双方向量化从原高精度输入分别生成，NVFP4权重二维scale已实现。

## 3. R51：安全交接，而不是泛泛的动态调度

问题：高优先级或下一阶段任务ready以后，等待来自调度反应，还是旧kernel必须完成/排空的活动状态？强软件safe-point方案之后还有多少值得降低的成本？

三类比较：LithOS的透明atomization、GPREEMPT上下文切换、ExpertPlex的修改kernel并在tile提交后让出；MPK/PipeThreader提供任务图及流水强基线。不能拿某一种方案的限制替代所有软件能力。

建议四个同一时基时刻：

`t_ready → t_notice → t_quiescent → t_first_useful_work`

分别是新工作输入ready、调度/旧工作看到请求、相关资源达到合法安全边界、新工作真正执行。按task/epoch和交接资源范围定义；不要求整个GPU空闲；CPU/GPU异步时钟需先关联。

最小对照：一个优化背景operator与一个前景任务；相同计算/结果/到达序列，比较完整kernel等待、有限tile协作让出、保守资源预留；只有平台合法可用时才加入driver抢占。既计前景等待，也计背景吞吐损失。

否定条件：软件tile方案成本已足够低；等待实际来自输入未ready；收益只靠删掉必要同步或不现实到达频率。

潜在贡献仅在残差存在时讨论有限的状态归属/就绪跟踪或更低代价safe point。tile抢占、给decode更多SM本身都不新。先读一个真实异步kernel的边界，不搭通用OS、不改109驱动。

## 4. R52：失效可知以后还有多少可取消工作

问题：异步推测的失效信息已在线可知，但旧任务仍执行/占资源的成本是否超出队列取消和同步点检查？PipeInfer已有取消，SMART已有树收益控制；总拒绝率不是硬件机会。

先做低成本逻辑筛选：为每个task绑定失效首次可知时刻、完成时刻和有效消费者。只统计失效已知后且不再供有效消费者使用的工作。验证后才知道被拒、且那时早已算完的部分不计机会。

该工作量不是speedup上界；取消、异步完成与buffer回收均需付费。固定draft/verify/随机性，用真实可得信号比较队列取消与safe-point取消，分开停止计算和安全复用buffer。

否定条件：已知时全部结束；软件已覆盖；剩余工作仍供有效KV/消费者；需要未来接受结果才有收益。

与R51共用生命周期分析，作为特例而非再建一条平台。没有合法取消窗口就不占GPU。

## 5. R53：扩散动态任务的执行粒度

固定decoder、sampling和refresh规则后，合法任务数量随迭代变化；强runtime是否仍因图/bucket/tile粒度产生额外工作或等待？

token ID已确定不代表hidden/KV不变；这由双向attention语义决定。BiCache/dInfer的复用是有质量/刷新边界的；Nemotron SOL依赖预知最终答案。不据mask稀疏直接删模型计算。

最小对照：同一合法operator集合，比较静态bucket/图、成熟runtime、有限动态打包；计重排、复制、同步与完整请求时间。必须固定工作与结果要求，不能把更少denoise迭代归给硬件。

否定条件：活跃mask不改变必要计算；差别来自decoder/质量；成熟runtime已足够；只在随机人工mask有效。

当前保留而非搭环境；dense Qwen trace不能充作DLM证据。

## 6. R54：checkpoint生产与复用的总成本

Marconi与Sparse Prefix Caching分别覆盖跨entry管理与entry内位置。后者原型capture在计时外是范围缺口，不证明捕获昂贵。

待问：将产生、保存、驻留、命中、restore、eviction全部计入，exact状态复用还有什么结构成本？先核原生scan已返回哪些中间状态，是否可直接保留，及真实复用次数；不要免费扣除命中节省而省略生产成本。

否定条件：原生结果可零额外复制利用；管理/恢复微小；现有软件策略已够；仅靠把近似Tail-Replay与exact恢复混比获利。

低优先级系统/测量问题，尚无硬件归因，不先开发state cache。

## 7. R55：同一张量的多方向微缩放表示

待问：冻结量化recipe以后，不同归约方向是否迫使同一张量产生/保存多副本，且强融合仍留实质额外成本？

TE双方向生成、NVFP4二维scale已是强基线。scale格式/block变化不是免费语义不变；Is Finer Better已提示更细block也可能更差。

先为一个linear前后向消费链做生命周期/逻辑字节账本，核能否单pass融合生成各表示。没有必要副本并存或融合已消掉成本，就停止。RTX4080格式模拟不能当Blackwell原生吞吐。

这是训练/多消费者的长期候选，不是AWQ推理问题换名。

## 8. 执行与判断规则

当前优先次序：R51与R52合并边界核查 → 条件R53 → 低优先R54/R55。不是五项立即实验。

不要求软件“完全做不到”才允许硬件研究；同功能更低同步/存储/面积/能耗也可成立，但需实际成本。廉价原型可帮助发现原因，不必先完成论文级所有因果；不把一项近邻未覆盖的特性直接称新颖。

之后测量需匹配数值/质量合同与执行模式；不同batch总时长不是固定工作开销；独立分段时间不能直接相加分解并行critical path；不使用未来答案；高噪声标不确定，证据缺口与低效益分开。

## 9. 原文登记

- R501 https://arxiv.org/html/2407.11798v1
- R502 https://arxiv.org/html/2604.09731v1
- R503 https://www.pdl.cmu.edu/PDL-FTP/BigLearning/lithos_sosp25.pdf
- R504 https://www.usenix.org/system/files/atc25-fan.pdf
- R505 https://arxiv.org/html/2607.18002v2
- R506 https://arxiv.org/html/2512.22219v1
- R507 https://www.usenix.org/system/files/osdi25-cheng.pdf
- R508 https://arxiv.org/html/2411.19379v3
- R509 https://arxiv.org/html/2605.05219v1
- R510 https://arxiv.org/abs/2608.30310
- R511 https://arxiv.org/html/2607.05722v1
- R512 https://arxiv.org/html/2606.07571v1
- R513 https://arxiv.org/html/2510.08666v2
- R514 https://arxiv.org/html/2601.19026v1
- R515 https://arxiv.org/abs/2608.19628
- D501 https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html
- D502 https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html

新增笔记基于文献分支082dd8b36b199e135585c0ba61cab587d6814e60；仅文献目录写入，不修改任何accepted实验分支或raw。
