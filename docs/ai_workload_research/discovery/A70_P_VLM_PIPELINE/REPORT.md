# AI-ARCH A70 P-A70｜主流 VLM 视觉—语言阶段交接源码审

- 执行者：Codex Lane P / 174-new / Round A70
- 固定启动 HEAD：`8f24af162ba37b4fa37f7a18d89b0fdb62697942`
- 范围：Qwen3-VL-8B-Instruct 完整推理链；官方模型 revision `0c351dd01ed87e9c1b53cbc748cba10e6187ff3b`；强软件对照 vLLM `v0.20.1`（tag commit `132765e3560659ff63ebd236203672e991b70e08`）。证据访问日期：2026-10-16。
- 本轮终态：**NO_SURVIVOR_IN_SEARCH_SCOPE；0 候选**。这是限定源码与公开实验组的判断，不是宣称 VLM 没有硬件问题。

## 1. 完整模型与输入路径

官方 [8B 模型配置](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/config.json) 的语言主干为 36 层、hidden size 4096、32 个 query heads/8 个 KV heads；视觉塔为 27 层、hidden size 1152、patch 16、temporal patch 2、spatial merge 2，DeepStack 特征索引 8/16/24，视觉输出维度 4096（P01）。它是完整公开模型；不能用孤立 ViT 或缩维假模型等价替代。官方 [技术报告 §2.1–2.3](https://arxiv.org/html/2511.21631v1) 明确 2×2 merger、三个视觉中间层特征注入语言模型最初三层，并以文本时间戳与交错 MRoPE 表示视频（P04）。

固定 revision 的 [图像配置](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/preprocessor_config.json) 给出像素面积预算 65,536–16,777,216，[视频配置](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/video_preprocessor_config.json) 给出所有帧合计像素预算 4,096–25,165,824；两者都使用 patch 16、temporal patch 2、merge 2（P02–P03）。[Qwen 官方 README](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/README.md) 区分单图与全视频像素预算，并提供 fps/num_frames 控制及批量 padding 示例（P05）。静态预算不能推出自然请求实际分辨率、帧数或 token 直方图；每条请求的视觉 token 必须由固定 processor 对实际输入核算，不能仅用预算上限替代。图像面积约每 32×32 像素对应一个合并后视觉 token、视频还涉及时域压缩，是结构**推导**，需以 processor 输出与时间戳/特殊 token 校验。

[vLLM Qwen3-VL 实现](https://docs.vllm.ai/en/v0.20.1/api/vllm/model_executor/models/qwen3_vl/) 先按图像/视频构造视觉 embeddings，再把主视觉特征并入文本嵌入；DeepStack 多尺度特征另写缓冲区并送入语言前几层，随后语言 Prefill 建立 KV，Decode 继续生成（P06）。因此“预先计算视觉 embedding”会删掉完整任务中的编码成本，只能作阶段归因。源码未给出该 8B revision 的自然输入端到端阶段时间、显存峰值或 Graph 命中率，均为 **UNKNOWN**。

## 2. 已成熟的软件反证

[vLLM v0.20.1 多模态处理文档](https://docs.vllm.ai/en/v0.20.1/design/mm_processing/) 已把视觉占位符映射到特征 token，以支持 chunked prefill/prefix caching；对重复媒体缓存 processor 输出并合批处理未命中项（P07）。[优化文档](https://docs.vllm.ai/en/v0.20.1/configuration/optimization/) 还描述默认处理缓存、P0/P1 IPC 缓存、4 GiB 默认预算、API 进程扩展和视觉编码器 batch 级数据并行；API 扩展可能关闭 IPC 缓存，故不能把单一配置视作全场景免费（P08）。[编码器缓存管理器](https://docs.vllm.ai/en/v0.20.1/api/vllm/v1/core/encoder_cache_manager/) 按媒体 hash 在请求间复用 embeddings，并按占用/引用驱逐（P09）。[前缀缓存](https://docs.vllm.ai/en/v0.20.1/features/automatic_prefix_caching/) 仅省共享前缀的 Prefill，不省新 token Decode（P10）。

[vLLM v0.20.1 视觉 Graph 设计](https://docs.vllm.ai/en/v0.20.1/design/cuda_graphs_multimodal/) 已按视觉 token 预算预捕获、贪心打包、超预算 eager fallback；图像、视频及同 prompt 混合输入受支持，EVS 动态视频剪枝时视频 Graph 关闭（P11）。同页作者用 Qwen3-VL-30B-A3B-Instruct、GB200、VisionArena-Chat 3000 prompts/300 warmup 报告视觉 Graph 的局部均值 5.13→4.52 ms、P99 9.16→6.26 ms（FLASH_ATTN）；这是该模型、设备和 `vllm bench mm-processor` 分母，不是 8B 端到端 TTFT、ITL 或 Decode 收益（P12）。[编译文档](https://docs.vllm.ai/en/v0.20.1/design/torch_compile_multimodal/) 描述可选视觉 encoder 编译，Qwen2.5-VL 视觉模块约 4.5% 端到端改善，但编译与 CUDAGraph 组合行为在该文档中仍未定；不可把该数值移植到 Qwen3-VL-8B（P13）。[分离编码器文档](https://docs.vllm.ai/en/v0.20.1/features/disagg_encoder/) 已有 encoder→Prefill/Decode 及 encoder→Prefill→Decode 参考路径和跨进程 embedding 传递/复用；单纯提出“分离视觉编码器”不是新空间（P14）。

## 3. 真实输入、质量与不可外推范围

[VisionArena-Chat 数据卡](https://huggingface.co/datasets/lmarena-ai/VisionArena-Chat/blob/main/README.md?code=true) 说明 199,036 条 train 会话、用户真实图文对话，但其数据结构明确为**单图会话**，覆盖多轮文字而不覆盖自然多图/视频负载；该卡含使用协议，本轮只读元数据，未访问、下载、接受许可或复制图片（P15）。vLLM 的上述 Graph 性能组因此不能支撑多图/视频结论。Qwen [技术报告 §5.7/§5.9/§5.12.3](https://arxiv.org/html/2511.21631v1) 提供跨图任务与视频质量实验，其中 long-video needle 组是 **235B-A22B**、1 FPS、动态分辨率保持视觉 token 预算；不是 8B 的时延或质量—时延配对组（P16）。该论文中的质量实验不能证明改帧率、降分辨率仍是同语义任务。

项目旧证据 [E-C03/E-C11/E-C14 索引](https://github.com/swayhrl/accel-sim-framework/blob/8f24af162ba37b4fa37f7a18d89b0fdb62697942/docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md) 仅有文本 LLM 的 B1 编译/Graph 同点局部结果、Stage A 四问未完成及编译后 hook/名字映射不足；[DQ2 固定报告](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/DQ2_FINAL_STATUS.md) 明确不能外推 B4 或执行机制（P17）。它们既未覆盖 VLM，也不能作为 VLM 的阳性 oracle。

## 4. 科学判断与最小下一步

本轮直接搜索到的“重复预处理/视觉 embeddings”“图像或视频编码器 Graph”“多图打包”“视觉编码器分离”都已有强软件实现，分别落在 **SOFTWARE_ABSORBED（局部想法）**。余下可疑处是自然输入中 Graph 预算悬崖、processor/embedding 缓存命中与 Prefill/Decode 的真实端到端资源竞争；现有公开组只给局部 Graph 数值，且单图数据、不同模型/设备，没有足够同语义、同版本的阶段分解把这类疑点升格成硬件候选。故交 **NO_SURVIVOR_IN_SEARCH_SCOPE**，`CANDIDATES.json=[]`。这不是性能负结果，也没有执行 native 实验。

若未来另获数据和 GPU 授权，最小**证据门槛**为：固定本报告的 8B 模型/processor 与 vLLM v0.20.1，在合法可用的真实单图请求上记录完整请求 TTFT/ITL/吞吐、处理器时间、视觉编码、视觉到语言嵌入交接、Prefill、Decode、Graph hit/fallback、缓存 hit/miss 和峰值显存；同输入同输出质量下比较已开启默认缓存/批处理/decoder Graph 的强基线与额外视觉 Graph。诊断只改变 Graph 预算或相同 processor 输出的阶段计时；预计算 embeddings 只核成本构成。多图/视频需另外取得真实且可用的输入集，并以与选参集独立的 BLINK/MuirBench 或 Video-MME 一类任务核质量，不能拿 VisionArena 单图复制凑多图。若强软件已消除暴露端到端差距、显存代价抵消收益、或答案质量/输入语义变化，则停止硬件路径；若仍有可重复、占主要成本的 GPU 资源冲突，再由新 Goal 审批 native 诊断。本轮未申请、未执行这一步。

## 5. 执行边界

仅源码/官方文档/模型配置/数据卡元数据与旧文本报告；无 GPU/CUDA/JIT、模型 import/加载、权重或数据/视频下载、依赖安装、Profiler、模拟器。未改其他 Lane、AWMA/C16、协调文件或旧工作区。证据与缺口逐项见 `EVIDENCE.tsv`，提交前后 Git 校验见 `RECEIPT.json`；最终 commit/tree 由远端回读回执给出，避免 Git commit 自引用。
