# Round A70｜主流通用大模型四线并行Discovery Goal包

**日期：2026-10-16；协调：ChatGPT／AI-ARCH Discovery；执行者：四个独立Codex窗口。**

用户已明确：优先主流通用模型／大模型，尽量并行发现，发挥多个Codex的作用。本包将该指示落实为四项相互无数据依赖的轻量研究任务。**发布只表示READY_FOR_USER_DISPATCH；只有对应窗口收到启动指令并回执，才登记该Lane运行。不得把Git分支创建写成已启动进程。** 此包不授权任何GPU、模型加载、训练、模拟器、环境构建、大数据下载或清理。

## 0. 共同起点与如何阅读

Repository：`swayhrl/accel-sim-framework`。科学基线：科研协调提交`10f3a51ee39884bcec3d3180e81cc405872cccb1`；四线均从包含本包的同一个固定Goal发布HEAD分支，具体HEAD由协调窗口派发，不追随移动main。

每个窗口读本包第0—4节、自己的M/N/O/P节、第9—10节。只按需读其他Lane的题目以避免范围重叠，不必重复其他Lane整份调研。

必须先读基线下`docs/ai_workload_research/CURRENT_STATE.md`，并按自己问题查`AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md`相关条目及对应已接受报告；`COORDINATION_PROTOCOL.md`第1—8节为共同规则。不要求每Lane重新阅读全部A1—A69历史，更不要求逐文件hash旧环境、模型或trace。索引不是性能原始数据的替代品，涉及负结果时回到对应scope和固定报告。

**共同目标：** 找到主流模型真实执行中一个可检验、且尚未被成熟软件与项目历史充分解释的问题；或者用明确反证结束本Lane候选。不是凑论文数量、承诺发现硬件收益、复现完整论文或把一处工程缺陷包装成微架构机会。

## 1. 四线分工、节点和独立分支

| Lane／窗口 | 默认宿主 | 独立分支 | 主问题 | 唯一输出前缀 |
|---|---|---|---|---|
| M-A70 | 109新窗口 | `hrl/aiarch-a70m-llm-serving-discovery-109-v1` | 通用LLM长上下文与Prefill/Decode混合服务的资源竞争 | `docs/ai_workload_research/discovery/A70_M_LLM_SERVING/` |
| N-A70 | 174-new新窗口 | `hrl/aiarch-a70n-hybrid-state-discovery-174new-v1` | 混合注意力／递归状态模型的状态组织与执行约束 | `docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/` |
| O-A70 | 109新窗口 | `hrl/aiarch-a70o-moe-execution-discovery-109-v1` | 主流MoE自然token工作量与分派—计算—合并 | `docs/ai_workload_research/discovery/A70_O_MOE_EXECUTION/` |
| P-A70 | 174-new新窗口 | `hrl/aiarch-a70p-vlm-pipeline-discovery-174new-v1` | 通用视觉语言模型的视觉编码—语言推理阶段交接 | `docs/ai_workload_research/discovery/A70_P_VLM_PIPELINE/` |

这些是本轮逻辑窗口名，不接管其他项目中同字母的Lane。109/174-new各两个轻量窗口；不得打断AWMA/C16/ISCAS或旧Codex。没有164资产访问/传输授权。

M主要控制请求与批次构成；N主要控制单个混合模型内状态类型／布局／生命周期；O主要控制专家侧自然工作粒度和后端；P主要控制视觉输入与编码/语言阶段。允许共享少量强软件文档，但**不让四个窗口分别重复完整部署vLLM或做相同KV调研**。边界重合时在候选中标注应由哪个Lane主责，不等待跨Lane协调即可完成自己范围。

## 2. 首轮允许做什么与资源上限

### 2.1 允许

- 查公开原始论文、作者仓库、官方模型卡/config、小型输入说明，以及项目已提交的文本证据；对选中的关键源码固定commit/path，模型配置固定revision，记录论文version/section/table和访问日期。
- 使用现有工具进行文本解析、AST/JSON静态检查、可复算的维度/容量/工作量公式或微型纯CPU验证；纯计算必须标为DERIVED或CPU_DIAGNOSTIC，不能宣称模拟/测得GPU性能。
- 原始材料已足够时，连续完成问题筛选、强软件反证、近邻比较、自审、未来最小native实验提案及归档，不人为拆成多轮审批。

### 2.2 不允许

GPU和CUDA初始化/JIT、Torch/vLLM/SGLang模型import或运行、NCU/NSYS/NVBit、模拟器、编译器构建、pip/conda安装、下载权重/真实数据集/视频包、实际LLM服务请求负载、访问164/扫描模型盘、删除文件、改现有缓存或环境、接受数据许可、恢复A61/A65/A67/C16 Stage A/AWMA执行。仅设置CUDA_VISIBLE_DEVICES为空不是完整隔离；本轮根本不要调用模型运行栈或GPU工具。

### 2.3 每Lane控制上限

- **任务工具子进程：最多1个CPU计算worker，进程树RSS≤2GiB；单Lane新增盘≤256MiB，公开论文/源码/配置下载累计≤128MiB；GPU/模型数据下载/安装=0。** 文献检索可以并发网络I/O，但不派生多层子agent/本地计算池。
- 每主机本轮两个Lane合计最多2个CPU计算worker、4GiB任务工具RSS、512MiB新增盘；这不含已有Codex会话服务自身的基线开销，不能把未知的系统总资源写为实测。若宿主正在承压，不争抢资源；先只做远端文献读取，无法安全继续则RESOURCE_DEFERRED并交付已得研究结果。
- 工具作业设OMP/BLAS和Git pack/index线程为1；不要改用户全局Git配置。CPU affinity只从本进程允许集合选择，两个同机Lane尽量选不同可用CPU；不得重绑其他任务。无权限时用单线程约束并报告，不为绑核另建工程。
- 用独立sparse worktree/output/tmp；只检出所需研究文本，历史报告可`git show <fixed_sha>:<path>`只读查阅，不把整个含大raw的仓库重复checkout或clone。共享Git对象只读复用，任何写入只在自己的分支/工作目录，不执行gc/repack/reset/clean，不改别的worktree。
- 本Goal自接收派发起90分钟为研究收口上限，不是要求占满或性能估计；达到证据或反证闭合即可提前结束。额度用尽交付已有结论和缺口，不为凑阳性延长。普通超时、404、PDF入口缺失允许有界查原作者替代入口，不能无限重试或绕过访问限制。

轻量资源记录即可：执行起止、下载与新增文件大小、实际CPU限制/可用RSS记录。**不为一项只读Discovery搭一套GPU监督器、全盘hash框架或重复校验万级旧依赖。**

## 3. 各Lane共用的发现方法和终态

先宽看相关工作，再对最直接的2—4项原始工作及其关键实现深入；数量是工作尺度提示，不是完成门槛。优先最近的直接近邻，同时纳入仍决定问题定义的成熟基线。每个论据记录确切实验组：模型/任务、输入与分布、平台/部署、precision、变量/控制、指标分母、真实运行/局部模拟/估算、作者声明、我们的推导、未披露字段。不能从摘要或repo README中的最高倍数补造具体配置。

查到软件能力不等于已知其运行成本；查到TODO不等于仍未解决。移动文档可能落后当前实现，尤其不能用旧hybrid-KV设计说明的WIP句子宣称新版本无此能力。只对承载最终判断的路径固定源码与模型身份，不盲目归档整库。

每Lane提交**0—2个候选，最多1个推荐主候选**，候选必须回答：

1. 哪个主流真实模型/任务为何重要？为何不只是现有硬件方便跑？
2. 目前有什么观测或作者证据？模型/输入/软件范围如何限定？
3. 最强直接软件反证是什么，已排除什么、未排除什么？
4. 与项目旧实验相比，新变量在哪里？旧负结果是否真正覆盖它？
5. 最小native验证中的基准、诊断对照、独立验证对象分别是什么？哪个结果会使其停止？
6. 预期改变的是GPU计算/存储/执行/资源协调中的什么可观察量？若仅是服务策略或普通软件优化，诚实归类，不硬转成硬件。

不要求在发现阶段预先证明完整机制上界，也不要求现在获得全部权重/样本/ABI。资料足够设计区分解释的小实验即可为NATIVE_PROBE_PROPOSED；实际数值、数据、资源资格明确留到未来获批原生Goal。每个未来提案写最小必要资源和不得外推的范围，**当前不执行**。需要多GPU/更大显存时说清必要性，可作为资源不满足的储备，而不是假造单4080等价证明。

终态选自：NATIVE_PROBE_PROPOSED / SOFTWARE_ABSORBED / ALREADY_TESTED_SAME_SCOPE / NO_SURVIVOR_IN_SEARCH_SCOPE / SOURCE_INCOMPLETE / RESOURCE_DEFERRED。均须有中文科学解释；没有阳性也是合格交付。不能把单个材料缺失写成整个模型领域无价值。

## 4. 共同冻结与去重

- Q-S/ScanNet已因用户主线选择及无现有权限/数据退出当前候选，不申请、不搜镜像、不部署。GNN A67全驻留软件反证在原scope保留；A61/A65数值STOP不改写。
- C16 E1驻留、Split-K分组局部性、FFN双流/融合、E3自然路由和Stage A等先查证据索引；区分性能负结果、软件已覆盖、数值/观测未回答。不能换模型名重复旧问题，也不能把旧B1/短上下文负结果外推成所有LLM无空间。
- AWMA已有翻译服务、在线选择与训练梯度结论只读，未经对应项目授权不得修改其实现或结果。
- 受控合成输入可在未来提案中作为诊断对照，不可替代真实负载主体；真实请求分布、质量目标与holdout不要用自造热点/极端token长度代替。跨模型验证对象需独立于探索选参对象；现在只提案，不声称已验证。

## 5. M-A70｜通用LLM混合推理与资源竞争

**唯一主轴：** 对使用常规完整注意力的主流开源通用LLM，长上下文、请求并发和Prefill/Decode组合在成熟分块Prefill、批处理、前缀缓存、注意力后端与Graph优化后，是否仍产生值得通过GPU资源组织解决的限制？

从主流Qwen/Llama等实际完整模型或真实同家族小版本入手，具体名称/revision先核实，不把任意缩维模型当真实部署。M不展开混合递归state内部布局（交N）、专家重排kernel（交O）、视觉处理链（交P）。

重点交付：
- 原始论文的请求长度/到达分布、SLO、TTFT/ITL/goodput分母与GPU部署，成熟软件的实际调度/计算路径；例如Sarathi-Serve、DistServe、NanoFlow可作为搜索入口，名称不是已读资格，须回原文及后续直接近邻。
- 至少区分“请求排队与服务策略”与“GPU执行中资源竞争”，不默认Prefill永远compute-bound或Decode永远memory-bound。
- 形成一个最小对照：相同合法请求集合和质量目标下，隔离Prefill、隔离Decode、成熟混合路径；之后若要区分计算/访存/执行粒度，仅提出足够小的可实施诊断。不能把改变到达分布或删工作当免费上界。
- 对照旧C16 Stage A/B1/FFN范围，说明新问题为何不是其重复；可以否定所有候选而交NO_SURVIVOR。

建议原始入口：https://docs.vllm.ai/en/latest/configuration/optimization/ 与论文/作者仓库。当前文档已描述分块Prefill与Decode混合调度，这项能力本身不是新机制。

## 6. N-A70｜混合注意力／递归状态的组织与执行

**唯一主轴：** 在已经发布的主流通用混合模型中，完整注意力KV与递归/线性注意力状态的不同大小、更新时间与复用规则，是否在成熟runtime之后留下重要的容量、状态准备/迁移或执行代价？

Qwen3.5官方模型卡可作为真实结构入口，必要时以其他真实混合模型作独立对象；不得将所有线性注意力、Mamba和Gated DeltaNet当成相同算法，更不把model-card理论state大小当实际峰值显存。

重点交付：
- 固定一个实际model config，明确每类层、state形状/dtype、更新/恢复与prefix reuse要求；纯文本输入路径可以研究，不因模型含视觉编码器就重复P。
- 当前vLLM/SGLang已有的hybrid allocation、分组/对齐、prefix state checkpoint和kernel融合能力；文档与源码冲突时，分别给版本和证据，而不是选择更容易制造“缺口”的旧描述。
- 至多一个源码导出的可复算容量/准备代价模型，单列有效state、padding、共享/别名、scratch、并发请求及生命周期；不把未使用bytes直接等价于真实stall。
- 未来最小验证必须固定相同请求/算法与数学要求，区分容量优势和时间优势；若只剩软件分配器可修正的碎片问题，归SOFTWARE_OPPORTUNITY，不强行升硬件。

原始入口：https://huggingface.co/Qwen/Qwen3.5-4B 、https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/ 、https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/ 。它们是核验入口，不保证不同页或不同commit的能力完全同步。

## 7. O-A70｜主流MoE自然执行与小工作粒度

**唯一主轴：** 主流MoE模型的真实请求/Prefill与Decode下，每专家token数量、分派/排列、分组计算、合并及共享专家执行，在现有强后端后是否还形成可重复的GPU执行代价？

优先核真实Qwen-MoE/DeepSeek等官方模型及其当前runtime路径。单卡本地expert执行与多卡expert-parallel是两个不同科学部署，不能将all-to-all通信指标移植成单卡访存代价；大模型参数规模可保留为研究意义，未来小实验必须说明合法代表性。

重点交付：
- 自然路由的实际来源/披露方式与每专家工作量，不能随机均匀路由当主体；对照C16 E3 N/U接近、H改变语义的既有反证。
- 当前fused MoE、grouped GEMM、动态选择、量化、permute/unpermute以及双batch/共享expert重叠的具体可用路径；不要拿无融合fallback代替成熟强实现。
- 选一处真实的工作粒度变化或阶段交接问题，区分padding/并行度几何浪费、算法必需工作、物理访存和暴露wall代价。
- 一条最小native提案必须保留router选择/权重身份，诊断改变执行组织而不是激活集合；同时给未来独立模型或请求验证。没有真实自然证据就标待补，不能凭低occupancy数字宣布收益。

原始入口：https://docs.sglang.io/docs/advanced_features/expert_parallelism 及vLLM/FlashInfer等作者实现；先核单卡/多卡与阶段适用范围。

## 8. P-A70｜通用多模态模型的阶段交接

**唯一主轴：** 对Qwen-VL等主流通用视觉语言模型，真实多图/分辨率/视频帧输入所引起的视觉编码、视觉token交接、语言Prefill与Decode变化，是否在成熟处理/缓存/批处理之后留下重要执行或资源协调问题？

从一个官方完整模型/processor/model config到真实输入任务链，不退回ScanNet、小众点云或没有语言模型的独立ViT跑分。若小版本更适合最小实验，要说明与真实同家族大版本保留的结构及差异，不以压缩分辨率改变任务质量制造硬件收益。

重点交付：
- 固定视觉预处理、分辨率/帧采样、token数、投影/多层特征注入和decoder入口；记录实际模型差异，不把不同VL家族混为单一路径。
- 查视觉编码器图捕获/编译、processor/embedding缓存、batch调度或分离encoder执行的已有实现；Python图像解码耗时与GPU计算/状态交接分开，不靠关掉强软件产生基线。
- 原文真实多模态输入来源与实验质量/任务设置、局部encoder与整请求的分母；可见图片URL不等于已获得将来分发/训练使用授权，本轮只读元数据。
- 一个最小基准＋一个诊断＋一个独立输入集合的提案；同语义processor输出预计算只能当成本分解，不能把删去encoder工作称完整同任务改进。

原始入口：https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct 、https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct 及官方Qwen-VL代码、vLLM多模态处理/优化文档。具体backend/model revision必须在结论中固定。

## 9. 交付、分支卫生与无等待规则

每Lane只在自己的输出前缀增加下面四份轻量文件：

1. `REPORT.md`：中文解释“观察/来源—已有解决—新问题或否定—最小下一步”，含最多1个推荐主候选和最多1个备选；不让内部状态标签替代科学解释。
2. `EVIDENCE.tsv`：每行具体论文实验组或关键源码证据；列`id,source_type,source_url,version_or_commit,section_or_path,model_input_platform,comparison_and_metric,author_claim,our_inference,undisclosed,old_evidence_relation`。直接来源与推导分别填写，空缺用NOT_DISCLOSED/NOT_CHECKED。
3. `CANDIDATES.json`：可为空数组。每候选含`question,mainstream_relevance,scope,strong_baseline,old_evidence_delta,supporting_ids,counterevidence,baseline_probe,diagnostic_probe,independent_validation,required_resources,stop_if,unknowns,status`。所有probe均为未执行提案。
4. `RECEIPT.json`：Lane/宿主/固定start/final refs（避免最终commit自引用）、读过的关键source身份、实际资源/缺口、无GPU/权重/安装、正常结束/STOP。可用私有回读收据单独记录最终commit/tree。少量必要脚本/源码摘录只放本前缀下；PDF与版权全文不要复制入Git。

自己的branch/worktree不共享输出、不改CURRENT_STATE/图谱/共同manifest，不merge或cherry-pick其他Lane或旧实验HEAD。不要等待、反复poll其他Lane；有相邻问题只记录指针。全部过程保持审查来源，不将别人的未审候选当accepted结果。

终态前对本次少量文件进行语法/引用/候选去重自审，commit、push、单次fetch-back核自身HEAD/tree/blob与工作区clean。正常工程缺口有界solve-and-continue；科学范围/资源改变STOP。任务有同分支实际正在运行迹象时不启动第二份，先报告身份冲突。

用户回执最短包括：固定最终commit/tree、实际状态、推荐问题一句话或为什么0候选、最强反证、未来是否需要GPU/更大资源、已STOP。**本轮无自动后续GPU或循环任务。**

## 10. 协调审查与后续并行

ChatGPT负责跨Lane问题去重、原文/源码证据独立抽核和科学裁决。收到哪条完成回执就审哪条，不以其余Lane未结束为阻塞；相同来源的重复阅读不是独立native验证。最多择2—3个总体问题，必要时保留0个，不强求每Lane晋升一个实验。

后续若某候选值得native，可在其余Lane继续只读研究时单独准备有界GPU Goal；**同一109 GPU的真实性能实验仍由既有campaign lock独占，不能为了Codex并行而并发污染测量**。GPU任务须另行明确批准、确认科学数据/数值和资源；当前A70只读包不能自动解锁。其它CPU研究可以在不抢CPU/I/O、不干扰测量前提下继续并行。

A70是一次四线Discovery协作，不是四个新硬件项目立项。完成本轮后统一回收问题和证据，保持主流通用大模型优先。
