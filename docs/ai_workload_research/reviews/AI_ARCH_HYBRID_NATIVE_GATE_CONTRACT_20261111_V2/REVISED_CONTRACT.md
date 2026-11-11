# AI-ARCH｜Qwen3.5-4B Hybrid/GDN/KV 原生技术资格合同 V2（科学修订）

**裁决：REVISE_V1；V2为冻结的待授权设计，不是GPU执行许可。** 原V1固定于 `d750e4a7d3477f93198f419b7682756ab661c88f`，Draft PR #2保持Draft。本修订不修改原V1或历史raw。109-AI-ARCH 当前状态仍为 `NO_GPU_PROBE_READY / STOP`；只有用户未来明确将这一**固定V2**作为GPU Goal派发、并取得当次109资源owner时段批准及共享准入，才可执行。不得由本审查、PR更新、合并或本地安装回执推断GPU已获授权。

## 0. 目标、固定输入和可宣称的结果

目标仅是检查：固定Qwen3.5-4B官方BF16权重、固定WildChat自然user轮次、固定vLLM main wheel在109 RTX 4080上是否具备**纯文本、短上下文、完整双轮请求**的可执行技术资格。不是GDN/KV优化、缓存命中、长上下文支持、品质泛化、硬件创新或性能加速实验。

固定引用：
- Qwen3.5-4B修订 `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`；WildChat修订 `f66566ceaaeb619dd98ffb0f3bf3ce1f86775ac4`，单分片 `data/train-00005-of-00006.parquet`；资产资格 `8e836c7bb0b0428fe2c04630ef21ddf6b9d3269f`。
- 独立环境安装 `e82218cd73240ee4307603daa18390d3af7197d0`：vLLM `0.34.0rc1.dev167+gca3c154d2` / 源码 `ca3c154d26749c2b59d9d99050d2bd631d2c63f7`，Torch `2.14.0+cu132`，Triton `3.8.0`；原共享vLLM `0.30.0`不变。
- CPU四候选身份：沿V1 `candidate_selection.json` / `select_candidate_sessions.py`；27,628候选、22,079探索、5,549保留；选择规则为探索池完整SHA256最小的四条，选中digest列表的SHA256为 `a5f4cfb551054561d6353d096143679bb8603c7ab0a2831d5f409ea86feee701`。首轮user输入42/15/12/855 token，使用旧GPT历史的第二轮212/85/33/1095 token只是CPU诊断，**不是**本次Qwen第二轮实际长度。保留池完全不触碰。
- Q1/shN、旧A70N、其它项目原已接受负例/STOP不变。Qwen旧V11继续PARKED；本资格探针不能重开旧V11。

技术结果、逐会话语义适用性、独立质量和机制资格分别标记，不能用一个PASS概括。

## 1. 研究对象：接受有条件的“自然user + Qwen自生成assistant”

每个会话固定 `user₁`、`user₂`来自WildChat原文；先请求 `[user₁] → Qwen assistant₁`，再请求 `[user₁, Qwen assistant₁, user₂] → Qwen assistant₂`。原GPT assistant消息既不进入模型输入，也不作答案gold；Exgentic GPT-4.1轨迹同样不作Qwen质量oracle。

称呼必须是**“真实来源user轮次上的Qwen反事实自续对话”**，不得称“原始自然Qwen会话”或“已复现WildChat原对话”。第二次是一个包含完整Qwen历史的新Chat请求；除非有实际缓存/版本/命中证据，**重发历史并不证明跨请求的FA KV、GDN recurrent或conv状态直接复用**。

### G0：GPU之前的私有内容、合法性和语义适配门

四条候选已经冻结；在任何GPU预约/锁前，仅在109的受限私有目录读取其两条user文本；有权限的源适配核查者可额外**只读**原GPT assistant₁以判断user₂是否依赖它，但该原回答不得进入Qwen输入、不得成为质量gold，也不展示给后续盲评者。记录去内容审计：来源、同一conversation绑定、角色与message数量、非空、tokenizer身份；额外人工核验潜在PII/敏感数据及使用/访问范围。WildChat ODC-BY数据库许可与标记为false都**不**自动保证每条文本的再披露权或无PII。不得将原文、生成文本、会话ID、私人数据或派生prompt传到Git、第三方模型/云评测器或174节点。

**事前判定user₂可适配性**：是否依赖原GPT回答中的特定不可由user₁确定的事实、名单、措辞、链接、格式或承诺。通用“继续/展开上文”不是自动不合格，但必须记录条件性；真正依赖原GPT独有内容或无法判定时，标记 `ORIGINAL_GPT_DEPENDENT` / `INDETERMINATE`。质量/安全审查无法合法完成亦标记 `CONTENT_REVIEW_BLOCKED`。

**所有四条必须事前达到 `SOURCE_COUNTERFACTUAL_ADMISSIBLE` 且获合法私有处理确认，否则 `SOURCE_GATE_NO_GO/STOP`，不进入GPU。** 不能换第五条、移动到保留池、删改user₂、插入GPT历史、用合成文本或把不合格会话改成单轮技术PASS。若四条不合格，应另立CPU-only样本合同并重新冻结，不能在本Goal临场补样。

该预审只说明“可以合理测试自生成历史”，不保证后来Qwen回答实际满足user₂。

## 2. GPU参数建议（保持为**待用户授权**的精确范围）

- **一次且仅一次**共享GPU非阻塞窗口，含全部加载/运行/退出，累计共同锁最多1800秒；同一owner、一个服务实例、一次模型加载、最多四会话八次生成。禁止自动第二窗口、无限重试、追加性能点或恢复旧shN。
- RTX4080一张，TP=1；本地固定checkpoint、tokenizer、BF16；仅文字 `--language-model-only`、`--dtype bfloat16`、`--max-model-len 8192`、`--max-num-seqs 1`、`--gpu-memory-utilization 0.85`、`--reasoning-parser qwen3`，本地服务仅绑`127.0.0.1`。禁vision输入、MTP speculative、量化、CPU权重offload、自动精度降级、改变模型分片或runtime。保留vLLM正常prefix caching、graph和后端选择，但记录实际生效配置；不以“未主动关cache”作为状态复用PASS。
- 两轮每次最多256**新输出token**、输出预算计入8192全长限制；seed42、`temperature=0.7`、`top_p=0.8`、`top_k=20`、`min_p=0`、`presence_penalty=1.5`、`repetition_penalty=1.0`；请求必须确实应用 `chat_template_kwargs={"enable_thinking":false}`。不支持的字段或默认项无法确认则停止；不静默移除，不现场改温度/seed/输出预算。固定随机种子不保证跨环境bitwise可重复。
- 请求无tools、无视觉部分、无截断补丁；第一轮只将模型最终可见answer文本作为assistant₁输入第二轮，不携带私有chain-of-thought/reasoning、原GPT答案或中间工具内容。逐请求记录**有效chat template、输入token数、生成token数、finish_reason、reasoning/content分离、输出hash与错误码**。非思考配置不生效、`finish_reason=length`、上下文超限、空/异常文本均不得登记双轮完整请求PASS；同时区分“预算不足/格式不兼容”和真正模型质量错误。
- 资源硬门以实际owner reservation及实时样本为准：own GPU NVML显存≤14GiB、Host采样RSS≤40GiB、可信charged memory≤48GiB、MemAvailable≥10GiB、新私有文件≤4GiB、文件系统剩余≥32GiB。`gpu-memory-utilization=0.85`是服务自己的配置预算，**不是实际显存的安全上限**。采样峰与连续峰分开；资源owner有更严格限制时按严格者执行。
- GPU资源必须有**本Goal独立的用户派发**和**当次资源owner明确时段批准**，再通过Image-Lab的非阻塞共同flock、预约、loaded gate、owner进程/设备身份与清理协议。冲突不等待/轮询；退出释放服务、CUDA context、预约和锁。旧shN W2的通用授权字符串不可复用。

## 3. CUDA 13.2/cu132与R580的动态门：不是静态版本FAIL，也不是兼容PASS

109当前 `580.178.04` 驱动在CUDA 13.x的**有限minor-version兼容范围(≥580)**，但不满足CUDA 13.2对应发行驱动R595的完整特性期望。其限制包括较新driver API特性及PTX JIT；Qwen3.5/GDN的实际SM89 Triton/FLA路径尤其不能从 `pip check` 或CPU CLI推断成功。

公开依据：NVIDIA CUDA 13.2 Release Notes <https://docs.nvidia.com/cuda/archive/13.2.0/cuda-toolkit-release-notes/index.html>；Minor Version Compatibility <https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html>。这只支持“允许在明示风险下**试行已授权的fail-closed动态资格**”，不等于预先允许训练/推理或证明兼容。

G1：锁外CPU验证固定文件长度/hash和不漂移的wheel、Torch/Triton/vLLM完整身份，模型卡的非思考模板、离线辅助资源、字段/API和实际参数解析。冻结命令、禁外网/禁下载，加载不得触发在线自动获取或pip/install。模型/样本/G0不合规则STOP。

G2：**只在G1合格、取得独立GPU授权及资源owner时段批准之后**，一个窗口内按序：检查driver/runtime实际版本、设备SM89和基础CUDA初始化/最小同步张量运算；检查真实使用路径的Triton/PTX JIT/算子能力；随后加载完整Qwen BF16纯文本模型并验证GDN prefill/decode与FA backend、vision module是否实际被裁剪、权重/MTP与同活物理存储。任何不支持PTX、requires-newer-driver、driver API不兼容、OOM、隐式下载、实际路径不明或自动替代precision/backend：以原错误STOP。不得在同Goal升级驱动、换cu12 wheel、注入compat库、force eager或降max length/精度“救活”。

G3：G2合格后按事前冻结顺序执行最多四条×两次完整请求，不重试失败样本，不为了观察更好答案重新生成。检查同一会话内Qwen assistant₁确切进入请求2、tokenizer/模板/语义、自然user₂是否在真实自生成历史下仍适配，并记录端到端请求时延与生成结束状态（仅技术诊断，非性能对照）。硬件状态是否跨请求复用、cache命中、GDN状态字节及物理服务量如无直接证据，明确 `UNKNOWN`。

G4：完全释放GPU资源，再进入独立质量审查，绝不持锁等待人工打分。

## 4. 四会话的独立质量与隐私门（不能与技术执行混为一谈）

输入池、四会话顺序和生成预算事前固定；四条是**探索技术样本，不是独立holdout、随机代表样本或统计意义的质量估计**。原GPT回答不得作为Qwen oracle，独立保留池不得提前用于训练/调参/选择。

对每条会话先检查技术门（完整请求、非截断、历史正确、有效token/状态），再由**至少两名未参与109执行、获准读取本机私有全文的独立评审者**分别盲评；不得向评审者展示延迟、GPU配置失败、原GPT assistant正文或另一名评审者评分。如无法安排符合数据权限的评审者，返回 `QUALITY_GATE_OPEN / NOT_REVIEWED`，不把109执行者的自评当独立质量PASS。

逐条评审时显示 `user₁, Qwen assistant₁, user₂, Qwen assistant₂`；事先列明四个维度：
1. A1是否合理回应user₁，含安全拒答的合理性，不强制迎合不安全请求。
2. 在**Qwen已生成的A1**而非原GPT历史下，user₂是否仍语义明确；是否暗中要求仅原GPT曾提供的内容。
3. A2是否准确遵从user₂的可判定要求，并与本次A1一致；禁止幻构从未出现在本轮上下文的历史承诺/引用。
4. 文本是否完整且无明显角色错置、重复退化、虚假工具/网络执行声明；主观质量证据不足时给 `INDETERMINATE`，不为了通过强给PASS。

每维 `ACCEPT / REJECT / INDETERMINATE`，以最弱维度决定每会话状态。两评审一致才通过；分歧须由事先授权的第三名独立评审作有界仲裁，否则 `INDETERMINATE`。拒答若符合任务与安全要求不自动REJECT。非完整输出、窗口耗尽和max_tokens触发单列技术未通过/预算受限，不把这种结果归咎于模型知识能力。

**四会话全部达到技术完整且独立两人逐维ACCEPT**，最多登记 `LOCAL_4_SESSION_CONTEXTUAL_ACCEPT`。任一reject/indeterminate/不可评，登记 `QUALITY_GATE_NOT_PASSED` 或 `QUALITY_GATE_OPEN`，逐条保留原因（私有），不替换样本、不追加生成。即使全部ACCEPT，也**不证明整体WildChat质量、长上下文、真实Qwen用户互动分布、跨请求GDN/KV状态复用或硬件候选**；这些需新的独立验证合同。

评审原文、原始会话ID、输出、PII不进入Git/外部LLM评审服务；公开仅hash、token长度、各维状态、双评审一致性和不泄露内容的原因类别。若本地数据使用或审阅权限不合法，停止并报告，不能把有来源/数据库许可等于可任意复制。

## 5. 收据、状态与停止规则

一个日志同时登记G0/G1/G2/G3/G4各门状态，不能跳级、不能因G3 8/8 HTTP成功就跳到科学候选。至少交付：
- 固定模型与shard/tokenizer/hash、vLLM/wheel/runtime/driver/SM89、有效CLI参数、vision pruning和实际backend身份。
- 每条固定会话去内容来源承诺及G0适配结果；每次请求的输入/输出token、SHA、finish reason和历史重放关系；不得公开原文、ID或PII。
- 资源owner时段准入、GPU共同锁持有时间、所有子进程/服务context完全释放，真实NVML/RSS/charged与采样限制。
- 隐式下载/新driver/PTX/ABI/kernel/容量/质量失败的未修改原错误和fail-closed收据。
- G4两名独立评审每维结果及仲裁状态（如合法开展），公开去内容摘要。

状态分层：
`ASSET_CPU_QUALIFIED`不等于`CUDA_DYNAMIC_PASS`；
`CUDA_DYNAMIC_PASS`不等于`FULL_TWO_TURN_TECH_PASS`；
`FULL_TWO_TURN_TECH_PASS`不等于`LOCAL_4_SESSION_CONTEXTUAL_ACCEPT`；
以上均不等于`GDN_KV_MECHANISM_READY`或`HARDWARE_CANDIDATE_PROMOTED`。

进入任何下一GDN/KV机制或性能对照之前，必须有新的科学假设、相同模型/质量/精度、实际FA/GDN/conv状态与缓存版本测量、强软件基线和独立holdout；本V2 **禁止**追加机制实验、训练、Profiler、跨模型切换或GPU重试。

## 6. 允许授权方式

当前只完成科学修订合同。用户如欲启动，应另行明确派发**固定V2 commit/文件、单次1800秒窗口和上述资源限制**，由109-AI-ARCH按当次资源owner准入执行；如无授权或任何事前门未满足，继续 `NO_GPU_PROBE_READY / STOP`。本PR保持Draft，不自动合并、不启动Runner，不复用旧Q1/shN GPU预算。
