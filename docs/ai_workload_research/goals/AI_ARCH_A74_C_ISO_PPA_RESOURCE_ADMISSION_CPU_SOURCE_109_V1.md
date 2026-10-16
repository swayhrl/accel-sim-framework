# Round A74-C｜SM100非矩阵资源与TC固定预算取舍：新颖性、模型和实验可行性最小CPU准入

**状态：READY_FOR_USER_DISPATCH / NO_GPU_AUTHORIZATION。** 本文件是CPU/source研究Goal，不等于已经发给109 Codex，也不许可访问RTX4080/CUDA、B200、模拟器或模型数据。发出固定HEAD指令并实际启动后才登记RUNNING。建议执行者：node109一个独立新Codex窗口，唯一输出目录`docs/ai_workload_research/discovery/A74_C_ISO_RESOURCE_ADMISSION/`。

## 0. 科学起点与唯一判断

Repository: `swayhrl/accel-sim-framework`；独立执行分支`hrl/aiarch-a74c-iso-resource-admission-109-v1`。该分支从包含本文的固定发布commit创建；启动HEAD由协调ChatGPT单独派发。必读：
- `docs/ai_workload_research/reviews/AI_ARCH_A74_A73_W_H_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-16_V1.md`；
- `docs/ai_workload_research/discovery/A73_H_ARCH_COUNTERFACTUAL/{REPORT.md,PAPER_GROUPS.tsv,ARCH_QUESTION_CARDS.json}`只读固定H commit`06b17a72f683316a4088292a4b424c9d97c7437c`；
- `docs/ai_workload_research/CURRENT_STATE.md`和`COORDINATION_PROTOCOL.md`第1—8节；A73-W只需第0、6节及WQ01边界，不重复读其23条全部来源。
- 只查上述直接近邻相关的原作者、官方版本与当前公开代码，不再广泛扫A70已有的所有软件论文。

**唯一问题：** 在Blackwell Ultra已翻倍exp SFU、FA4已软件模拟exp且正式发表于MLSys2026之后，H73-Q1的**固定面积/功耗单元配比＋逐点强软件重调＋完整通用模型Prefill**是否仍有可以被检验而非仅口头描述的不同问题？在没有测量GPU或模拟器时，判定它进入未来native机会门是否具有足够具体的模型、实现和可行资源反事实，或应当PARKED/STOP。

明确层次：作者FA4/GB300的局部数字不等于我们的Qwen FP32/BF16完整Prefill；黑盒切换GPU或软件策略也不构成TC换SFU的iso-PPA因果。禁止在源码阶段宣布硬件headroom或“FA4没优化好”。不要求最终一定留阳性。

## 1. 必须回答的四个闭合门

### G0：反证和版本

核官方`MLSys 2026 FlashAttention-4`会议版真实存在及具体相关实验版本，和作者`arXiv:2603.05451v1`版本差异/冲突；若无法取得正式PDF可依据官方HTML准确限定其公开信息，缺图不要猜。核原固定`Dao-AILab/flash-attention@e9d8944c855489e03c66262d07ba4c81d9d8dd31`的SM100 forward和softmax，列出真实可用exp native/emulation、FMA、SMEM/TMEM/TMA、causal、GQA、head_dim选路，不把注释/开关当运行PASS。核NVIDIA官方Blackwell Ultra/GB300相对GB200的exp吞吐2x与约35%特定FP8 forward实验组，记录**其它同时变动的硬件/精度/分母和TDP或容量差异**，不称iso-PPA。至少补一项最接近的硬件级softmax/资源平衡近邻；若仅粗略摘要无配置，标SCREEN而不是新颖性否决。

结论表至少区分：已有“更多SFU”，已有“软件exp补偿”，已有“固定硬件下自动优化调度”，本问题剩余的“跨单元比率的面积/功耗预算与完整模型机会成本”。如果前者已包含所有真实预测，`DUPLICATE_NO_GO`。

### G1：完整模型分母和强软件选择

固定Qwen3-8B`b968826d9c46dd6066d109eabc6255188de91218`真实model config的Prefill BF16/GQA/FFN，选择4K/8K/16K三个自然业务可能长度仅作结构规模敏感性（**不制造这些长度的假自然文本**）。复算第A74审查中的投影、FFN、因果QK/PV MAC比例，并给softmax score数的条件数量；绝不从MAC直接换算GPU wall或资源busy。静态检查推荐支持的CUDA/FA4/cuDNN release、SM100 kernel、mask/GQA shapes、数值/precision条件；没有设备时标`BACKEND_RUNTIME_UNQUALIFIED`，不为了完成Goal安装/编译或运行任何GPU栈。明确当前最强合法后端**必须在真正资源点重选**，H73给的source可用性不是“在B200跑得通”。

输出完整Prefill机会成本符号表：attention原时间占比f、注意力加速s、非目标FFN/投影损失r；报告公式`f/s+(1-f)*r`的适用条件和反例；若本问题所需f只能通过B200运行获得，将其准确列为后续**机会门**而不是本轮缺材料导致全域STOP。

### G2：iso-PPA反事实的可实现性

**独立明确物理可操作性：** 在真正一张B200上不能改变现有SM的TC/SFU单元数量和面积；跨GB200/GB300也不是固定资源比。检查现有项目模拟器的冻结配置和源码是否具有SM100的tcgen05/TMEM/TMA、MUFU.EX2、FMA/issue、共享内存服务和异步依赖的有效性能模型，**只读代码与文档，不build/run/修改模拟器**。对未知能力标`MODEL_CAPABILITY_UNVERIFIED`，确认不存在的关键功能标`MODEL_MISMATCH`，切勿用模拟器名义把H100/Ada效率直接等价到B200。

列出初步的面积/功耗对价需要什么权威：同工艺TC/EXP/MUFU端口/SMEM服务/时序、面积、动态静态功耗、端口/issue/寄存器/频率耦合；若所有单位对价都没有公开可信范围，不能用峰值FLOPS线性换面积。可提出显式不确定区间与仅理想oracle的科学上界，但不能叫可制造Pareto点。

### G3：最小可证伪未来路径

给出**真正能分隔三种解释**的最小证据阶梯：
- 已有FA4/兼容最优cuDNN时，目标业务的attention/full-Prefill wall及stage权重；软件选优后是否有暴露的指数服务压力；
- 片上算子与软件可能争抢TC/FMA/exp/SMEM/TMEM：哪个直接可观测、哪个只靠kernel切换不可识别；
- 要验证iso-area取舍，需要哪个可信硬件建模/模拟器扩展和哪种可能的PPA估算；如果没有这一链，应该止于源码假说，不因外部设备租金已花而追加机制；
- 真实输入：给一个可合法获取、明确tokenizer与任务质量的主流自然文档请求入口，尚未下载/接许可，则写`INPUT_AUTHORITY_PENDING`，**不能把W TraceLab provider cache counters拼成自然Qwen输入**。

不得自动申请B200或宣称用户已同意购买／下载。若模型、代码、数值或最小反证无法形成闭合定义，允许`SOURCE_NO_GO`。

## 2. 控制资源、工程收口

CPU/source-only：任务工具单CPU worker（OMP/BLAS/Git pack/index均1线程），进程树RSS≤2GiB、新增盘≤128MiB、可下载公开PDF/源码≤64MiB、GPU/CUDA/JIT/模型权重与真实数据集下载／依赖安装／Profiler／模拟器编译与运行／清理全为0。独立worktree、临时区、输出前缀，不改旧H/W原始分支/STOP，不访问164、不破坏C16/AWMA/ISCAS。60分钟为本轮最晚收口上限，证据足够立即STOP，不为凑论文数延长。普通网络404、路径/格式问题有界solve-and-continue，不进行多轮待批准工程碎片。

交付：
- `REPORT.md`：明确最终判断（下节）与最强反证、剩余不同变量、明确无GPU资格；
- `PRIOR_AND_FEASIBILITY.tsv`：至少包含FA4正式版/预印本/代码、NVIDIA Blackwell Ultra、至少一项直接硬件近邻、Qwen算法／输入、模拟器/面积模型的证据与缺口；每项标作者实测/源码/静态派生或未披露；
- `DECISION.json`：无歧义的下一步和禁止动作，包含三个判断门：nearest-hardware-prior、compatible software & full scope、iso-PPA model legitimacy；
- `RECEIPT.json`：固定source commit/blob、可用文件SHA、未披露、CPU资源、无GPU/下载模型/安装、四文件publish/fetch-back/clean的实际状态。
- 不能写协调CURRENT_STATE、图谱、另一个Lane目录或旧raw。完成后push/fetch-back精确Git commit/tree/4 blobs并STOP，向用户回执，不轮询等待W/H。

## 3. 终态分类

- `SOURCE_FEASIBILITY_FOR_NATIVE_GATE_PROPOSED`：至少一组可实现的iso-area或受控理想资源反事实路径、已有直接硬件近邻被准确区分、主流自然模型/强软件与充分明确的后续机会门都已找到。**不等于现在可运行GPU，更不等于硬件设计成立**。
- `PARKED_FOR_PPA_OR_SIM_MODEL`：问题有范围但没有可信硬件可调参数/成本/建模链；不得直接以B200 profiling代替资源互换。
- `DUPLICATE_OR_SOFTWARE_ABSORBED`：论文/量产硬件/最强软件已经覆盖全部本轮真正可区分预测；不再写新机制。
- `SOURCE_INCOMPLETE`：关键原始资料不可访问而不能准入；明确究竟缺哪一页/版本、不能夸大全域NO_GO。
- `RESOURCE_DEFERRED`：CPU内存、网络、纸本文献或工作区资源无法合法完成，保留已取得成果。

用户要求持续并行，但**这是一条信息密度更高的准入研究，不为凑节点数量另设同质窗口**。用户没有明确派发前，状态一直是`READY_FOR_USER_DISPATCH`。
