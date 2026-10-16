# Round A74｜A73 W/H并行Discovery独立科学审查：真实请求身份与面积受限非矩阵资源再平衡

**日期：2026-10-16；执行：ChatGPT／AI-ARCH Discovery。审查状态：W_SOURCE_INCOMPLETE_ACCEPTED；H_SOURCE_HYPOTHESIS_RETAINED_NATIVE_NOT_ADMITTED。**

本轮只使用GitHub固定报告与源码、作者HTML/官方公开技术文章及纯算术复算；没有109/174/164登录、CUDA/GPU、模拟器、下载模型/数据/依赖、清理或重新启动Codex。A70四线0候选和历史C16/AWMA/GNN/ScanNet结论保持原样。

## 0. Git身份和证据层次

| Lane | final commit / tree | 独立Git核验 | 交付与科学状态 |
|---|---|---|---|
| W / 109 | `e7f2438aec9ee5c3ab677027c48a08dcd40c75b0` / `ba20263794bd7b9b94f0050b4e985347578ae7ad` | A73固定Goal `9afcdf6faa5b8351b56c9cbbefd3530c19c89537`→final ahead1；仅W自身4文件；final→W远端HEAD identical；Git-data parent/tree一致 | 23条15列证据，无字段数异常、ID唯一；1个PARKED、0晋升；`SOURCE_INCOMPLETE/STOP` |
| H / 174-new | `06b17a72f683316a4088292a4b424c9d97c7437c` / `0e53a3747c069f82322eea003f045c1b54ac1804` | 同Goal→final ahead1；仅H自身4文件；final→H远端HEAD identical；Git-data parent/tree一致 | 14条20列PAPER_GROUPS，ID唯一；12项初筛、6个深读组；1个源码问题、0备；`SOURCE_QUESTION_READY_FOR_CROSS_REVIEW`原状态保留 |

读取了两Lane各自REPORT、证据表、QUESTION_CARDS及RECEIPT四文件；独立回读TraceLab缓存记账/合成回放、SWE-chat公开README、FA4固定源码和论文v1、Twill正式摘要，核旧A70/C16对应范围；B200/B300新增原始硬件近邻见第3节。本审查核远端Git blob身份、执行commit/tree/branch和表格结构，不冒充重新计算执行者私有下载的全套SHA256，不检查109/174现时CPU资源。两Lane用户回报已push/fetch-back/clean、CPU/source-only；本审查没有重复执行。

## 1. W科学裁决：输入不闭合是合法STOP，不是没有自然负载

W选择的两个真实任务入口：
1. **BurstGPT真实聊天记录**：有session/请求提交、输入输出长度、完成耗时与失败标记，但没有原模型面对的全部文本/token。已有会话ID只能提示可能共享历史，不能恢复Qwen真正前缀。
2. **TraceLab日常编码Agent**：公开的是经过隐私清理的事件、工具、usage和cache统计，而非原model-facing字节。固定`uw-syfi/TraceLab@37402b4098dc65de56727b4c204fb71c8a59ddac`的`docs/prompt_cache_accounting.md`明确`prefix_tokens=cache_read_input_tokens`；同版本`replay/README.md`明确使用**synthetic text corpus**构造shape replay，保留session/依赖不恢复原私有prompt。

因此严格分开：
- `provider_cached_input_tokens`：原提供方在原配置中的缓存读量，属于内生运行时结果；
- `LCP(target_model_visible_prompt)`：新目标模型与tokenizer/template下真正可共享的token前缀；
- `necessary_prefill / checkpoint / restore / exposed_GPU_wall`：新runtime对该请求必须执行的计算与状态服务。

以上量不能由公开usage字段相互推导。抽象相同长度甚至相同provider缓存计数都不能证明目标请求相同。将TraceLab shape replay称原始会话的逐token faithful replay是错误；这不是作者bug。XPerf已发表基于真实token ID及依赖守恒的agent replay，Marconi/SegLen已有多轮缓存和重算软件近邻；不能以“Agent任务有依赖”作为首创机制。

WQ01（编码Agent在人类恢复/上下文改写与工具追加的资源准备差别）本轮科学价值是**输入与因果资格问题**。官方SWE-chat含真实内容但固定README要求access request，且实际model-facing隐藏模板及目标Qwen身份仍需另外核；用户未授权申请/下载，不能代其接受。由于同语义输入未闭合而且最直接机制已有近邻，接受`PARKED_SOURCE_INCOMPLETE`，0主、0备，不用W生成新native Goal，不回到A70-M已被直接覆盖的P/D资源分区。W只有真实trace来源资格卡，不是“真实GPU竞争已测”。

## 2. H保留的是什么，不是什么

H的H73-Q1询问：**在已优化的Attention内核之外，固定面积/功耗下重新配置TensorCore、指数SFU、SMEM/TMEM服务的边际供给，逐点重选强软件后，完整Qwen3-8B BF16 Prefill会否净加速？** 这区别于固定GPU做warp schedule的Twill，及A70-M在GPU上动态划分SM给P/D。但这个区别仅达到`SOURCE_HYPOTHESIS`，仍无新硬件机制、实测资源敏感度、PPA预算或校准模拟器。

H对六组区分事实/作者仿真/作者native kernel/我们推导是合理的；Kitsune v1不当最终TACO相同数值、LLMCompass只用单层模型估算、Twill是固定机器的kernel调度、Syncopate为分布式算子，均没有被伪装成完整Qwen服务原生测量。H的CPU tile max下界 `MMA=1024,EXP=1024,SMEM=768`、两类一起翻倍得到4/3，仅是**抽象不受面积约束的下界算术**，不是硬件加速上界或固定预算点。

**源范围需要收紧：** FA4原文针对forward的核心非矩阵压力主要是指数吞吐，针对backward另有SMEM/TMEM与2-CTA；未来题目固定为**推理Prefill前向下的exp/MUFU或相应FMA服务与TensorCore的取舍**。SMEM/TMEM保留为相关瓶颈和机会成本对照，不应同时把forward与backward的资源收益合成一个不可证伪硬件承诺。

## 3. 独立查出的两个重要近邻补充（H报告未完全覆盖）

### 3.1 FA4正式版本已发表

H准确标记其审阅的是`arXiv:2603.05451v1`，但是“尚未核会议”缺口现在可以具体更正：官方[MLSys 2026 FA4 Proceedings](https://proceedings.mlsys.org/paper_files/paper/2026/hash/ae8b0b5838ba510daff1198474e7b984-Abstract-Conference.html)已公开，同名工作已成为MLSys正式论文。该事实不自动使v1每项表格等同正式版，也不能直接消解其AppA.1 B100 vs正文B200身份冲突；下一资格门先核正式版本中相关实验组、版本/设备、cuDNN比较和当前固定内核源码是否一致。v1论文的直接事实是SM100资源不对称及exp用FMA模拟、条件rescale、TMEM流水优化；固定[FA4源码](https://github.com/Dao-AILab/flash-attention/blob/e9d8944c855489e03c66262d07ba4c81d9d8dd31/flash_attn/cute/flash_fwd_sm100.py)按is_sm103与causal/head_dim等选择ex2 emulation频率，证明软件在条件性适配，**不能假设硬件指数单元增加就必然改善最优kernel**。

### 3.2 Blackwell Ultra已经实际增加SFU资源——这是直接硬件先例

[NVIDIA 2026-02-25 官方技术文章](https://developer.nvidia.com/blog/making-softmax-more-efficient-with-nvidia-blackwell-ultra/)指出：Blackwell Ultra相对原Blackwell将指数相关SFU吞吐翻倍，GB200/GB300 `MUFU.EX2`微基准约2×，并在特定FP8 GQA forward场景报告约35%的吞吐提升；[2025年官方架构说明](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)也有相应SFU增强描述。因此**“增加SFU加速attention”已有量产设备与作者性能近邻**，比H只读FA4和Twill更直接。

这一真实GPU跨代比较**不是固定面积/功耗单变量**，GB300的功能单元、FP4能力、容量、功耗等均可能同时变化；不能据报告的FP8前向倍数直接声称BF16 Qwen3-8B完整Prefill收益或由“面积不变”推出iso-PPA。反之，它证明该硬件方向不是空想，**仅保留iso-area/iso-power资源交换＋合法逐点软件重调＋完整模型代价这个更窄问题**，新颖性比H原报告更难成立。

H若要主张新体系结构贡献，至少必须区别：
- 只增加exp throughput：量产Blackwell Ultra已有；
- 在给定B200上调软件exp/FMA/warp流水：FA4已有；
- 在固定架构内求最优SWP/WS：Twill已有；
- **改变芯片单位比例，在同面积/功耗与完整模型目标下得到可复现Pareto点**：尚未见该固定源码与论文组合直接证明，但本轮没有详尽检索全部chip DSE文献，不冒称已经证明首创。

## 4. 完整模型的额外静态机会成本（本审查新推导）

对H冻结的Qwen3-8B `L=36`层、hidden4096、GQA32Q/8KV/head128、FFN intermediate12288，若理想因果三角QK/PV、忽略token padding和Softmax、以MAC数而非wall为分母，则每层：
- 线性投影MAC/token `P=4096²+2×4096×1024+4096²=41943040`；
- gate/up/down FFN MAC/token `F=3×4096×12288=150994944`；
- Attention QK/PV MAC `A(N)=4096×N×(N+1)`。

按此理想算术式，N=4096/8192/16384时，Attention QK/PV占这三类矩阵MAC总和约**8.00%/14.82%/25.81%**。这不包括Softmax SFU、访存、实际tile填充、pipeline气泡、其他服务或其wall时间，不得据此宣称Attention的wall份额只有8%或14.8%。

若真实原始Attention wall份额f，改动后Attention加速s、其它阶段因硬件让渡慢r，且可合法近似为串行加权模型，则 `T_new/T_old=f/s+(1-f)*r`；纯假设`s=1.2,r=1.05`须`f>3/13≈23.08%`方有全段净收益。f/s/r全未测，未校准并发关键路径。**这把模型分母和成本反证提前列为硬条件：面积预算点若把FFN/投影拖慢，而Attention暴露时间不足，局部硬件优化没有完整模型价值。**

H选择的Qwen3.5-4B holdout仅8/32完整Attention层，另有24 GDN，的确可能产生反向的资源收益预测。但两模型dtype/state/head_dim及自然请求需单独数值资格，不得以模型差异直接检验同语义性能加速。

## 5. 关键方法缺口：一张B200无法直接改变SFU/TC的物理配比

H未来方案建议一张B200做20分钟强软件native。这可以回答：当前机器强后端是否存在局部exp/片上服务压力？Attention对完整Prefill时间占比多大？不同合法软件策略如何变化？

**它不能直接回答“同面积从TensorCore拿走面积给SFU会发生什么”**：B200上的TC/SFU/SMEM/TMEM单元数量不是软件可独立改写的参数；禁用TC、切换kernel或跨B200/GB300对比，均不等于iso-PPA反事实，模拟器扩展又必须支持tcgen05/TMEM/TMA/异步同步的目标语义并经原生校准。

因此必须先决定路径和可观测范围：
1. 原生强软件可作**机会门**，但不是架构互换门；不先申请昂贵B200，只为拿一个FA4 kernel speedup。
2. 未来架构论证要有**可实现单位级成本模型**及目标SM100支持的受控性能模型；面积、功耗、布线、issue/scoreboard、寄存器共享、时钟等不是一个免费标量。若现有模拟器无法合法重构目标对象，为`SIM_MODEL_GAP / NO_HARDWARE_CLAIM`，不能把旧Ada/Accel-Sim拟合成SM100。
3. 至少将`native可观测压力`与`未来硬件互换可证伪`分成两道科学资格门。没有资源对价和强基线前，H应为`HYPOTHESIS_RETAINED / NATIVE_NOT_ADMITTED`，而不是GO实验。

## 6. 最终裁决与下一阶段

| Lane | 原报告状态 | 独立接受后的用途与权限 |
|---|---|---|
| W | `SOURCE_INCOMPLETE`，WQ01 PARKED | **同意STOP。** 不从provider缓存统计生成原Qwen文本请求；没有合法model-facing数据权限/身份时不做native。已有XPerf/Marconi/SegLen等近邻的回放、前缀策略不重命名为新机制。 |
| H | `SOURCE_QUESTION_READY_FOR_CROSS_REVIEW`，H73-Q1 | **作为source级研究假说有条件保留**，但发现了Blackwell Ultra硬件直接先例与MLSys FA4正式出版；新颖性和iso-PPA可证伪尚未过门。**不批准B200/Profiler/模拟器/下载/新机制**。 |

下一步可开**一次有界CPU/source-only的C-A74资格任务**，只核：FA4正式版与Blackwell Ultra具体实验组、正向exp是否还有区别变量、面积/功耗及目标SIM backend能够怎样表示资源交换、Qwen完整模型机会成本/输入合法性。必须给出明确的`SOURCE_FEASIBILITY_GO`/`PARKED`/`SOURCE_NO_GO`，而不是继续广泛搜10篇文献。该任务如准备Goal，仍需用户派发才启动；不把Git文档创建当执行授权。W冻结待合法输入来源，除非能直接解决身份否则不安排重做。

四线A70、A73 W/H的所有原始report/STOP和其它C16/AWMA/ISCAS/GNN科研权限不改。本次更新只写协调分支，不merge实验HEAD；无新节点执行回执。

**A74终态：W STOP接受；H唯一待问题缩窄到iso-PPA单元配比×强软件重新调优×完整大模型Prefill，但原生和硬件立项都不准入。**
