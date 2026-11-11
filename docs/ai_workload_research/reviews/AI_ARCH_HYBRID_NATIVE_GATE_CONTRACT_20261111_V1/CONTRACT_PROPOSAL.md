# AI-ARCH｜Qwen3.5-4B 原生资格最小合同提案 V1

状态：**供 AI-ARCH-5 审查，尚未冻结，未获 GPU 执行准入。** 目标仅为判断固定 Qwen3.5-4B、固定自然输入和固定 vLLM main 在 109 上能否形成可审计的纯文本原生执行基点。即使通过，也不构成 GDN/KV 机制、性能收益或硬件候选证明。

## Authority 与当前边界

| 对象 | 固定身份 |
| --- | --- |
| 资产资格 | commit `8e836c7bb0b0428fe2c04630ef21ddf6b9d3269f`，`AI_ARCH_HYBRID_ASSET_QUALIFICATION_20261110_V1/REPORT.md`；Qwen `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`，WildChat `f66566ceaaeb619dd98ffb0f3bf3ce1f86775ac4` 的单份固定分片。 |
| 环境安装 | commit `e82218cd73240ee4307603daa18390d3af7197d0`，vLLM wheel 对应源码 `ca3c154d26749c2b59d9d99050d2bd631d2c63f7`，`torch 2.14.0+cu132`；只通过 CPU 入口检查。 |
| 109 硬件 | RTX 4080 16 GiB，驱动 `580.178.04` 报告 CUDA `13.0`；cu132 的实际兼容、模型加载与容量未知。 |
| 旧科学结论 | Q1/shN 已 STOP；Qwen 旧路线 PARKED。此提案只调查 Hybrid/GDN/KV 候选的原生资格，不重开旧 Qwen 性能 Goal。 |

源文件与私有资产原位保留。模型原精度为 BF16，检查过的两份 safetensors 与 tokenizer 身份沿用资产资格回执。GPU 执行前仅在资产元数据变化时重新核完整哈希，或按执行合同明确要求在锁外重核；不得为了装载失败换权重、精度、模型或 runtime。

## 拟冻结的研究语义

主对象为 **Qwen 自生成的两轮纯文本对话**。从 WildChat 固定分片取自然 `user₁`、`user₂`：以 `user₁` 生成 `assistant₁`，再以 `[user₁, assistant₁, user₂]` 生成 `assistant₂`。第二轮不得插入原数据的 GPT assistant 文本。原 GPT 历史只用于此前 CPU 模板／长度诊断；Exgentic 的 GPT-4.1 轨迹不作 Qwen 质量 oracle。输入与输出全文仅保留在权限受限的 109 私有目录，Git 只收 hash、长度、状态和去内容的回执。

固定分片的过滤和划池沿用资产资格脚本：`turn ≥ 2`、消息数 `2×turn`、角色严格交替、内容非空、行与消息的 `redacted/toxic` 均为 false；`SHA256(conversation_id UTF-8)` 前 8 字节大端模 5，余数 0 为保留池。本提案的**技术入门样本**是探索池内完整 SHA-256 最小的 4 条，不在运行后换样本。CPU 复算仍得 27,628 候选、22,079 探索、5,549 保留；四条首轮模板输入长度为 `42/15/12/855` token。使用原 GPT 历史构造的第二轮长度 `212/85/33/1095` token **仅为诊断**，不代表 Qwen 自生成后的第二轮长度。选择承诺见 `candidate_selection.json`；无 ID 或内容公开。保留池本 Goal 不触碰。

若 AI-ARCH-5 认为自然 `user₂` 对原 GPT 回复的依赖使上述自生成语义不适合作为质量对象，应在 GPU 前改定研究问题；不能在运行后改用固定 GPT 前缀并称为同一结果。

## 拟议的一次有界 GPU 资格窗口

以下均是**待审参数**，不是当前运行指令。建议 109-AI-ARCH 仅一个窗口、单卡、累计共同锁内最长 `30 min`，模型加载最多一次、最多 4 条探索会话共 8 次生成，无性能重复样本、无热修复后重跑。仅在独立 GPU Goal、当前资源窗口、Image-Lab 共同 `flock`、预约、loaded gate 和实时身份准入均明确后执行；超时、门控失效或资源冲突立即清理并 STOP。

| 项 | 拟议冻结值／要求 |
| --- | --- |
| 服务 | 新隔离环境；本地固定模型目录；`HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`；只绑定 `127.0.0.1`。 |
| 模型路径 | `--language-model-only --tensor-parallel-size 1 --dtype bfloat16 --reasoning-parser qwen3`；不得启动视觉输入、MTP speculative、量化、CPU offload 或替代模型。 |
| 容量界 | `--max-model-len 8192 --max-num-seqs 1 --gpu-memory-utilization 0.85`。这是 16 GiB 上的**短上下文资格范围**，不证明模型卡 262,144 token 上下文可运行。不得通过降低精度或继续缩短输入来追求 PASS。 |
| 生成 | 两轮各至多 256 output token；模型卡的非思考模式 `chat_template_kwargs.enable_thinking=false`，采样 `temperature=0.7, top_p=0.8, top_k=20, min_p=0, presence_penalty=1.5, repetition_penalty=1.0`；固定 seed `42`。若当前 API 不接受任一字段，记录不兼容并 STOP，不静默省略。 |
| 缓存与默认项 | 不人为关闭 prefix caching 或强制 eager；实际有效配置、cache 命中和图／scratch 策略按日志记录。此 Goal 不用缓存命中声明跨轮状态收益。 |

## 顺序门与可证伪结果

1. **锁外 CPU 准入。** 对照固定 commit、冻结清单、目录身份和文件大小；确认私有模型/数据可读，下载封闭。准备四条样本的私有 ID 映射，不输出原文到 Git。无匹配资产或环境漂移则 `PREFLIGHT_FAIL / STOP`。
2. **GPU 加载门。** 在共同门控内核驱动与 `cu132`、SM89 算子实际初始化；同一 BF16 checkpoint 按上表加载，确认纯文本路径和是否实际裁掉视觉模块，记录启动峰值显存、加载时间与错误。驱动、算子、OOM、隐式下载或视觉裁剪证据缺口均分别记录；前四者立即 `RUNTIME_FAIL / STOP`，裁剪未知不得登记容量 PASS。
3. **生成门。** 四条会话按预定次序各做两次请求；核每次实际 token 序列、首轮 Qwen 输出如何进入第二轮、finish reason、错误、截断、有效上下文长度和显存峰值。任一请求失败、非预期截断、第二轮混入 GPT 历史或超过 8192 token，则 `SEMANTIC_OR_CAPACITY_FAIL / STOP`。输出全文私有保留；公开只含 hash/长度/错误类型。生成速率和延迟可作诊断，不作跨方案性能结论。
4. **质量边界。** 本窗口的机械完成只给 `RUNTIME_TECHNICAL_PASS`；不能以非空输出或 `finish_reason=stop` 宣称回答质量 PASS。AI-ARCH-5 需在执行前决定是否采用下文的人工质量门；未定则即使前三门通过，也保持 `QUALITY_GATE_OPEN / NO_GPU_PROBE_READY`，不进入机制实验。
5. **结束。** 记录进程身份、有效配置、窗口内时间、Host/GPU 计时口径、CPU RSS 和 GPU allocated/reserved/设备峰值，释放自身服务、GPU context、预约与共同锁。原始错误和负结果不覆盖。

建议人工质量门：由能访问私有全文的独立审查者逐会话判断 `assistant₁` 是否回应 `user₁`、`assistant₂` 是否在 Qwen 自生成历史下回应 `user₂`；逐项只给 `accept / reject / indeterminate` 和简短私有理由。任一 `reject/indeterminate` 均不登记完整质量 PASS；若后续 user 轮次依赖原 GPT 回复，应如实记为语义不适配。该门只判四条短会话的有限可用性，不证明总体任务质量。AI-ARCH-5 应审定是否足以作为下一阶段资格门；若不够，先改合同再执行。

## 必须保持的结论界限

通过以上技术门仅表明此具体环境、短上下文、单卡、四条探索会话可运行。它不证明 128K/262K 上下文、独立保留池质量、真实长期会话分布、同语义强软件性能、GDN/FA KV 容量机制或硬件收益。若失败，报告确切阶段和原始错误；不自动安装另一个版本、重开 GPU 窗口或改算法。后续机制 Goal 仍须另立对照、分母、质量与资源合同。
