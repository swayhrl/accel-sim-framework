# Round06｜R53扩散推理的合法工作集与在线组织

日期：2026-09-27。维护：ChatGPT。**文献与实验设计，不是执行Goal；没有启动109/174、下载模型或运行论文代码。**

## 1. 决策和范围

状态：`R53_DESIGN_READY_NATIVE_NOT_AUTHORIZED`。尚未确认新硬件问题。

只保留问题 `R53_N1_ONLINE_LEGAL_WORKSET_REALIZATION`：

> 固定每请求的解码与KV刷新规则，真实变化的合法工作集经过共享forward、continuous batching、varlen/分桶与已有图优化后，是否仍留下有实质成本的在线组织问题？

R51在已测试lm_head/Flash组合中冻结，R52无真实在线失效证据而休眠；不重跑、不扩展原结论到所有persistent kernel。

核心9篇：8篇正文关键机制/实验/局限章节，1篇只有原始摘要。不是全部全文精读，也不是全部新增。另核官方源码、模型配置/关键分支、runtime README与API。指定版本不冒充最新最终稿；原文事实与以下设计分开。

## 2. 原文证据与边界

| ID | 指定来源与阅读位置 | 已有能力 | 不能继承的结论 |
|---|---|---|---|
| R601 | Fast-dLLM，2505.22618v3，缓存/并行解码相关正文 | 双向模型的近似KV复用、confidence并行提交 | 缓存相似不等于exact；多token提交收益不是纯映射优化 |
| R602 | Fast-dLLM v2，2509.26328v1，§3–4 | 训练适配的块因果模型、已完成块缓存、块内DualCache、batch | 块间因果不证明块内近似cache精确；训练质量表与吞吐设置分开 |
| R603 | dInfer，2510.08666v2，§2–4 | decoder/KV manager分层；compile、graphs、循环展开；多种刷新/平滑 | 8×H800 B1实验不是4080全模型能力；算法/蒸馏收益不归给runtime |
| R604 | dLLM-Serve，2512.17077v2，§3–4/§6.1 | query-token packed batch、Refresh/Reuse混排、logits分块、每头物理稀疏KV | RTX4090/L40S实验已有关联强能力；Fast-dLLM比较臂关闭parallel decoding，综合speedup不能直接继承 |
| R605 | BiCache，2606.07571v2，§3–5 | 浅层prefix跨请求复用、深层请求内周期刷新 | 相似性门槛是近似；固定token不等于深层KV固定；不是物理cache一致性问题 |
| R606 | BlockServe，2607.08930v1，§II/III-A | block-cycle退出/补入、mixed-state位置、预算、gather/scatter | 单H200 LLaDA8B/Dream7B BF16；相近质量不等于完整轨迹一致；block-cycle不是GPU kernel抢占 |
| R607 | Sangam，2607.04206v1，§2–6.1 | 重复re-prefill deficit预算、混部/分离/混合；FlashInfer+graphs | 8×H100测试床；刷新语义不适用于所有块因果模型；AR式prefill切分不合法不等于不能tile任何算子 |
| R608 | Nemotron-Labs-Diffusion，2607.05722v1，§2–4.1 | 三模式训练/推理；SOL分析 | SOL先串行取得目标序列，不是在线跳算信号或GPU加速上界 |
| R609 | Serving Masked Diffusion LLMs: Characterization and Design Principles from Real Hardware，2608.23807v1，原始摘要 | LLaDA8B+D2F LoRA/H200服务行为研究 | 正文未取得；CPU dispatch和短生成截断观察不扩成所有DLM规律 |

## 3. 先证明合法工作，而不是数mask

本轮分析框架区分：

1. 待提交位置U。
2. 各层合法query集合Q_l。
3. KV读取范围与KV刷新/提交范围。
4. decoder、平滑、fallback、下一块seed所需logit集合O。
5. 尚未结束的request集合A。

这些集合不同。全双向模型中固定token的深层状态可受其他位置变化影响；原生块因果模型的已完成prefix不受未来块影响，但当前块内缓存仍按具体策略判断。BiCache还指出固定输入下第一层注意力前KV是特殊精确情况，不应泛化到全部层。

只有某工作既不供当前消费者也不供未来合法状态使用，才能称可删。最后一层无消费者logit与中间Transformer行不能等同。Fast-v2有token shift，不能直接把masked position当作对应logit row。

## 4. 代码核查

C601：`NVlabs/Fast-dLLM @ a9b81e4caa240c8cad4f7dc1889ff4852a0fca5b`，`v2/generation_functions.py`；blob `76fc22d1d4eb2d9f959fc5d3148cd9067651d5b1`。静态阅读，未运行。

`batch_sample`已在块边界移除finished requests并裁切各层KV。sub-block循环用整batch的mask归约决定继续；block cache分支使用整batch的`any()`选择full-block refresh或sub-block reuse。

因此不能说官方代码没有batch退出。也不能把重新分组后的加速直接当映射收益：改变cohort可能改变一个请求的刷新序列。Python归约/控制代码存在只是诊断线索，不证明它占主耗时。

C602：公开模型 `Efficient-Large-Model/Fast_dLLM_v2_1.5B @ 25093b6f63300adfd57f72145083c8a528fe4f16`。配置28层、hidden1536、12Q/2KV、BF16、block32；目录权重约3.09GB。已读config和modeling的mask/cache/logits_to_keep关键分支；未下载权重。它是真实训练后的块扩散模型，不是原Dense Qwen。

其体量适合优先做109可行性canary，但没有实测峰值显存或SM89/backend兼容性；不代表全双向LLaDA/Dream刷新。模型代码依赖与历史C16环境不同，后续隔离环境，不覆盖accepted环境。

C603：dInfer官方README（blob `a456079bb5de51d4b1b04537b6b26b013335205f`）明确batched支持。C604：FluxServe官方README（blob `4e385c5e89867b52cf6daa1977cb2f76b6c11853`）声称varlen block-decode、graphs、C++control plane；本轮只核README，不继承性能或Fast-v2兼容性。

D601：CUDA已有IF/WHILE/SWITCH conditional graph nodes。D602：FlashInfer相关wrapper在graph模式下固定batch_size，但有paged/ragged接口和预分配metadata。某wrapper限制不是GPU物理不支持动态执行；新方案须考虑bucket与已有控制能力。

## 5. 最小实验设计（尚未启动）

### 5.1 只做一条小型qualification

复用C16计时/NSYS/哈希/传输，不建新服务系统、不下载多个模型、不跑模拟器。

候选Fast-v2-1.5B，BF16，block32/subblock8/threshold0.9/temperature0。0.9是论文一个部署点，不是唯一默认。选定cache策略保持；关闭cache的简化臂只能作语义诊断，不能唯一代表强软件。

GSM8K与HumanEval各四个discovery请求，另各四个holdout，共16个逻辑输入上限；并发上限4，必要bucket仅1/2/4。按冻结dataset revision及ID确定性取样，不按已知耗时/动态性挑样。生成上限512，正常EOS停止，截断必须记录。dataset版本、ID/hash和runtime build尚未绑定，故本笔记是设计而非可执行manifest。

### 5.2 三种对照

- A0：官方batched参考，保留原有cache/退出；不是唯一强baseline。
- A1：相同算法下共享forward、合法mixed-state/varlen或bucket图、buffer复用等已有能力。可移植直接相关能力，不必完整复现三套服务系统。未适配成功标BASELINE_NOT_QUALIFIED，不宣称软件无解。
- D：必要时同执行模式下让当前迭代metadata提前就绪的诊断。不是部署方案，不用未来接受信息指导主线，不称严格性能上界；预计算与cache差异单列。

最多A0/A1×2 discovery bundle四个主点；D至多一个；残差成立才用相应独立holdout的一对，最多七个主配置。canary通过立即继续，无需为每项验收另开轮次。

### 5.3 语义与度量

要求每请求的提交位置和值、confidence/fallback离散决定、逻辑推进、cache refresh/reuse版本和EOS一致。内部logits逐bit不是通用要求；若数值差改变轨迹，不能称纯执行组织比较。最终文本相同不足以证明算法工作相同。

global-any刷新必须保留cohort逻辑并计成本，或单列为算法策略改变；不得静默切成更少刷新。

先收不计时逻辑账本：`request_id, logical_step, block/subblock, cache_epoch, commit_positions, Q_required_by_layer, KV_read/refresh, logits_consumers, request_done, actual_shape, graph_bucket`。未知required集合保持UNKNOWN，不填mask数。计时版不增加逐层CPU读取。

主指标：完整请求集合墙钟、有效tokens、请求完成时间、GPU union时间。另记录forward数、实际/合法query行、KV读取/更新、logits峰值、packing字节、metadata、launch/graph、host等待。

同operator可以比较required与executed query行，Attention另记KV长度及Q×K。工作量差不是speedup；少做行可能因打包更贵而更慢。不同运行模式的独立分段时间不能直接相加作critical-path分解。

每点至少2warmup+7完整重复，配对/交错执行，保存单次值；拟以5%完整生成成本为投资筛查并结合不确定性，不是等价性检验，不宣称可靠P99。主观察如GPU瓶颈未出现或成本仅是Python控制，先按软件解释收口。

### 5.4 允许的终点

`NO_OBSERVED_EXCESS_WORK_IN_SCOPE`；`SOFTWARE_BASELINE_SUFFICIENT_IN_SCOPE`；`ALGORITHM_CHANGE_NOT_MAPPING_GAIN`；`INPUT_OR_BASELINE_NOT_QUALIFIED`；`HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED`；条件`RESIDUAL_READY_FOR_REVIEW`。

最后一个需要真实动态性、强软件基线、稳定成本与区分解释的证据，不自动等于机制新颖。小型诊断原型可用于找原因，不把论文级完整因果证明设为所有探索前置条件。

## 6. 交付与下一步

已完成语义分类、直接近邻、源码分支、真实小模型候选和一组资格设计。未完成native轨迹、strong baseline适配、VRAM峰值或性能/质量结果。

不再建议一轮泛选题；若继续执行，应一次合并：准备/canary→合法工作账本→强软件对照→必要诊断与holdout→决策。**本次仅研究设计，不授权启动。**

## 7. 原始来源

- R601 https://arxiv.org/html/2505.22618v3
- R602 https://arxiv.org/html/2509.26328v1
- R603 https://arxiv.org/html/2510.08666v2
- R604 https://arxiv.org/html/2512.17077v2
- R605 https://arxiv.org/html/2606.07571v2
- R606 https://arxiv.org/html/2607.08930v1
- R607 https://arxiv.org/html/2607.04206v1
- R608 https://arxiv.org/html/2607.05722v1
- R609 https://arxiv.org/abs/2608.23807
- C601 https://github.com/NVlabs/Fast-dLLM/blob/a9b81e4caa240c8cad4f7dc1889ff4852a0fca5b/v2/generation_functions.py
- C602 https://huggingface.co/Efficient-Large-Model/Fast_dLLM_v2_1.5B/tree/25093b6f63300adfd57f72145083c8a528fe4f16
- C603 https://github.com/inclusionAI/dInfer/blob/master/README.md
- C604 https://github.com/FLX-OSS/FluxServe/blob/main/README.md
- D601 https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html
- D602 https://docs.flashinfer.ai/api/attention.html （所取快照header0.6.18，不称最新）

本轮基于文献分支d6a10f0209a024edb4612b1f53edb61d6e39bd18，只写文献目录，不修改accepted实验或raw。
