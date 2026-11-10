# AI-ARCH｜Hybrid/GDN/KV 自然会话与模型资产资格 V1

日期：2026-11-10 至 11。执行端：109-AI-ARCH API。承接 [CPU 资格调查](https://github.com/swayhrl/accel-sim-framework/blob/06e60d3b4c9aa6d1324601027f8c2bd51ec88ff0/docs/ai_workload_research/reviews/AI_ARCH_HYBRID_GDN_KV_CPU_QUALIFICATION_20261110_V1/REPORT.md)。本轮只在 109 的独立私有目录取得固定公开资产，并用 CPU 验证字节、结构、会话和 tokenizer；没有加载模型、初始化 CUDA、运行 GPU、训练或测量模型性能。原 A70N `SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE` 及其它 STOP 保持原样。

## 裁决

**`CPU_ASSET_SCOPE_QUALIFIED_WITH_LIMITS / NO_GPU_RESULT`。** 固定的 Qwen3.5-4B checkpoint、tokenizer 和一个自然多轮 WildChat 分片已可为后续合同提供实际字节；WildChat 在本轮固定分片中有 27,628 条通过结构与非空/标记过滤的至少两轮会话，按会话 ID 的 SHA-256 预分为 22,079 条探索池和 5,549 条保留池。Exgentic 小分片也确有完整输入/输出和明确的逐调用 `stop`，但原运行模型是 GPT-4.1。**这些是资产与输入资格，尚不是 Qwen 原生服务、质量、容量、速度或硬件候选资格。**

WildChat 的 ODC-BY 是数据库许可，许可文本明确不自动解决每条内容的独立权利或隐私权。本轮不对原始会话文本作再发布；本地目录权限限制，Git 仅保存来源卡、摘要、hash 和无内容的分析脚本。标记过滤不能证明零 PII。未来若要公开任何具体 prompt 或派生数据，需另核其使用和披露条件。

## 固定实体与实际读取

| 实体 | 固定来源、字节和用途 | 资格边界 |
| --- | --- | --- |
| Qwen3.5-4B | `Qwen/Qwen3.5-4B@851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`；Apache-2.0；两份 safetensors 分别 `5,329,398,688` 和 `3,990,429,408` 字节，整文件 SHA-256 分别 `26a93f…e74c61`、`cb544b…0e188`，均与固定 LFS OID 一致。`tokenizer.json` 的 `12,807,982` 字节及 SHA-256 `5f9e4d…cb42` 亦一致。 | **资产字节与结构 PASS**：738 个 tensor、逻辑参数字节 `9,319,737,856`，header/index 的名称、偏移、dtype/形状及文件末端通过核对。固定配置为多模态 checkpoint 的纯文本候选；不能据此宣称 4080 可加载或部署通过。 |
| WildChat | `allenai/WildChat@f66566ceaaeb619dd98ffb0f3bf3ce1f86775ac4`；ODC-BY。只取 `data/train-00005-of-00006.parquet`，`231,061,961` 字节，SHA-256 `2023b66a16cf095fcd3686e10259dc089eca95f739fa1c863b07af56029f9f00` 与固定 LFS OID 一致。 | 本轮只审一份分片。README 叙述 650K 会话，当前 metadata 的 train 为 529,428 条；不把叙述数字当实际冻结行数。没有逐回复 API finish reason、Qwen 回答或任务质量 gold。 |
| Exgentic | `Exgentic/agent-llm-traces@70036b93a04e61b0ea2706a68b962f4f26774587`；card 标记 CDLA-Permissive-2.0。只取 `data/train-00022-of-00039.parquet`，`265,853` 字节，SHA-256 `38bd8d57ceb882de7d2afb7354fec558687dbc67621c2293e92a3f9ce4d3351a` 与固定 LFS OID 一致。 | 本分片全是 `tau2_airline`，并以 GPT-4.1 变体采集；不能作为 Qwen 任务成功证据，也不代表全部 39 分片。 |

官方 Hugging Face API 在本机及 109 均连接超时，本轮使用 `hf-mirror.com` 的固定 revision 路径读取公开 Git/LFS 对象。旧 A70N 曾固定同一 Qwen revision；本轮本地文件的 Git blob 或 LFS SHA 与镜像固定树一致。镜像是取得渠道，不能被写成独立的官方实时确认。`sources/` 留存小型 card、许可、模型 config/index/template 的字节快照；模型与原始会话文件保留在 `/data/c16/aiarch_hybrid_asset_qualification_20261110_v1/`，不进 Git。

权重采用固定 LFS 大小与 SHA-256、HTTP Range 分段获取；部分 128 MiB Range 的连接失败。主下载进程最终对第一份一段报告 `curl=56`、HTTP `206`、`Recv failure: Connection reset by peer`；一次补取又遇到 `curl=28` 连接超时。`scan_weight_ranges.py` 排除 `.tmp` 并核对每段长度后，定点补取脚本将已确认失败的 Range 划分为 32 MiB 子段重取、核长度并组装。下载重试不改变预先固定的权重身份；两份整文件 SHA-256 最终均与固定 LFS OID 一致。失败临时文件与失败过程保留到最终核验，原始权重不进入 Git。

`model_header_summary.json` 是不加载 tensor payload 的 CPU 结构回执：第一份 87 项、第二份 651 项，合计 BF16 690 项和 F32 48 项；`model.language_model` 逻辑字节 `8,411,510,272`，`model.visual` `667,028,480`，其余含 MTP。它是 checkpoint 的逻辑分组，不能当作运行时纯文本驻留峰；vision 是否真正裁剪仍取决于后续服务版本和动态验收。

Parquet 结构检查使用只装在该私有目录 `tools/` 的 CPU `duckdb==1.4.1`；未更改共享 vLLM 环境。tokenizer 调用复用 109 既有 `transformers-5.18.0` 环境，且显式离线、隐藏 CUDA 设备并核查未初始化 CUDA。

## 109 运行时静态边界

固定 Qwen 模型卡在 vLLM 部分明确要求 main 分支，并给出纯文本服务命令 `--language-model-only`。109 现有环境是 `/data/c16/envs/c16-vllm-v0.30.0-sm89-v1` 的 `vllm==0.30.0`，不是已核对的 main 构建。CPU 静态源码检查表明这一安装版的 CLI 确实声明 `--language-model-only`，`MultiModalConfig` 会对该模式禁止多模态输入；registry 有 `Qwen3_5ForCausalLM` 和 `Qwen3_5ForConditionalGeneration`，后者声明 `supports_multimodal_pruning=True`。因此不能简单称此参数或模型入口缺失，但这些静态证据也不能证明固定权重可正确加载、vision encoder 实际被裁剪、GDN 后端在 SM89 可运行、状态与质量正确或内存可容纳。

**`RUNTIME_VERSION_GATE_OPEN`。** 模型卡的 main 要求与已装 0.30.0 尚未通过同一 checkpoint 的原生执行消解；本轮不升级或安装新的服务环境，不启动 Runner/CUDA。即使权重和会话字节核验通过，GPU 原生准入仍未 ready；后续合同必须先固定经过核对的运行时提交/版本、纯文本参数与模型加载路径，再在另立获准 GPU Goal 内做动态验收。

## 自然输入结构复核

WildChat 固定分片含 `88,238` 条唯一会话；`28,941` 条至少两轮且最后一条为 assistant。所有行的消息数等于 `2 × turn`，分片共 `174,864` 条 user 和 `174,864` 条 assistant 消息。`464` 个会话有 redacted 标记；有 `1,774` 条空或 null 消息。预冻结候选过滤要求：`turn ≥ 2`、消息数准确、user/assistant 严格交替、全部内容非空、行级和消息级 `redacted/toxic` 均为 false。结果 `27,628` 条；按 `SHA256(conversation_id UTF-8)` 前 8 字节大端整数模 5，余数 0 为保留池，其余为探索池。两个池只按身份分配，尚未使用保留池调算法或性能门。

Exgentic 固定小分片有 `46` 个 session、`273` 个 chat span；全部 span 的输入和输出消息都是可解析 JSON，逐调用 `finish_reasons` 含 `stop` 且 status code 为 1；全部 46 个 session 有至少两次带成对 JSON 的 chat 调用。此处的“完成”是逐调用，不是 Qwen 原生 agent 成功；该分片的模型列表只有 GPT-4.1 名称，不能把原答案当 Qwen 质量 oracle。

已安装的 `transformers-5.18.0` 用固定本地文件载入 `Qwen3_5Tokenizer` 并完成纯文本 chat template CPU 调用，`torch.cuda.is_initialized()` 为 false。对探索池按 hash 最小的 64 条会话，仅以**原数据中的 assistant 历史**构造第二轮与末轮输入：第二轮 token 数 min/中位/p90/max 为 `33/429.5/1059/3032`，末轮为 `68/785.5/3029/4169`。这是格式和输入规模核查；原历史来自 GPT-3.5/4，不能称为 Qwen 自身生成的多轮轨迹，也不能外推到所有候选或 GPU 同活容量。

## 给 AI-ARCH-5 的最小后续合同建议

1. **先冻结语义。** 研究主对象可选“Qwen3.5-4B 在自然 user 轮次上自行生成 assistant 回复”的纯文本路径；原 WildChat assistant 文本只用于 CPU 格式检查或单独的固定前缀诊断，不混作 Qwen 生成轨迹。Exgentic 仅作带 `stop` 的 agent trace 对照材料，不将其 GPT-4.1 任务成功迁移到 Qwen。
2. **先做有界原生准入，再谈机制。** 若以后有单独明确的 109 GPU Goal、当前资源窗口与 Image-Lab 共享锁/预约/loaded gate，通过同一固定 checkpoint、tokenizer、原精度和实际 SM89 可用的 vLLM 强路径，先核模型加载、完整请求、跨轮状态和 prefix/checkpoint 正确性、输出及容量。记录模型权重、GDN/conv 状态、FA KV、graph/scratch 的同活物理峰，Host 与 GPU 事件时钟分账。加载、语义、质量或容量任一失败立即 STOP，不能降精度、换模型或用合成 prompt 追求通过。
3. **预留独立验证。** 在固定 WildChat 分片和上述过滤下，探索/保留池由公开的 SHA 规则确定；后续任何样本数、token 上限、seed、输出容差和质量判据应在 GPU 前固定。保留池不能用于调参。若原 user 后续轮次依赖 GPT 回答而使 Qwen 自行生成轨迹不连贯，应作为质量失败记录；是否改用固定前缀模式属于研究对象变更，交科学窗口裁决。

当前仍无 Qwen 原生运行结果、同语义软件对照的动态身份、完整生成质量或容量 PASS，且没有获准 GPU 窗口。本轮交付资产与输入资格后 STOP，不自动开始原生 probe。
