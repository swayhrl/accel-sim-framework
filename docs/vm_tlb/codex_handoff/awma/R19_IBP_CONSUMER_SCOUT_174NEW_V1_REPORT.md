# R19 Lane E IBP consumer scout — 174-new

Stage：`AWMA_R19_IBP_CONSUMER_SCOUT_174NEW_V1`。

Decision：`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`，仅限公开 Reddit / Legion GraphSAGE 的一次未来 Native 证伪准备。

固定 IBP 的 host 压缩保留原大小行槽，GPU 只取压缩前缀。`decompress_fetch` 或 Legion transfer kernel 将所选行重构到完整 GPU dense 输出；Legion 已将 cache lookup、fetch、解压合核。trainer 仍通过 `get_next` 接收完整 sampled-feature tensor，随后运行 GraphSAGE。作者 Figure 9 对真实 Reddit 显示 IBP 后仍有暴露的下一批等待，但尚未隔离 dense-buffer 成本。

FlexGen/InfiniGen 和 ColossalAI 的固定路径也先重构 dense tensor/cache 后再由各自 compute consumer 读取。IBP 提供 `__device__` helper，但所审源码中未见 GraphSAGE、GEMM 或 embedding 算子内的真正解压融合。ZipServ 与 tile-rANS/GEMM 已直接覆盖 LLM 权重的解码+GEMM 概念，故准备项不以 GEMM 为新意。

准备卡：`docs/vm_tlb/literature_notes/awma/problem_cards/R19_IBP_DIRECT_CONSUMER_PREPARATION.md`。详细来源和 claim 限制见 review pack：`docs/vm_tlb/review_packs/AWMA_R19_IBP_CONSUMER_SCOUT_174NEW_V1/`。

本 Goal 仅 CPU/source；无 CUDA、GPU lock、Accel-Sim、109 capture、模型/数据下载或新 execution Goal。R53 更正已存在并核对，未复跑。
