# LR13：DeepSeek weight-line revisit 的 GEMV 最近邻护栏

日期：2026-10-01。性质：CPU/literature/source-only；不复做LR12 broad survey。审查包：`docs/vm_tlb/review_packs/C16_DEEPSEEK_WEIGHT_LINE_REVISIT_NEAREST_NEIGHBOR_GUARD_V1/`。

本轮把weight访问重访明确拆为：同128B分析line但不同32B sector；同sector但可能不同byte；严格同byte。仅line重访不能自动推导sector重复、L2 miss、DRAM重复或周期损失。[CUDA官方coalescing说明](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#coalesced-access-to-global-memory)是32B warp transaction granularity；不同warp的请求及其实际缓存结果须另行证据。具体判词见`GEMV_WEIGHT_REVISIT_NEIGHBORS.md`。

最近邻能力已很密：AWQ源码有每warp输出通道、packed weight vector load和warp reduction；CUTLASS提供GEMV映射以及独立的GEMM staging/sliced-K/split-K/persistent/warp-specialized能力；MARLIN将weight tile暂存shared memory供多warp使用，并用warp-K/striped分工；QUICK以离线重排跳过dequantized-weight shared-memory writeback；FLUTE做packed weight staging与Stream-K；GemLite提供低比特GEMV和RevSplit-K；vLLM Marlin MoE已有专家对齐及M tile策略。各能力的**适用格式、版本、架构和是否真处理weight重复**详见`CAPABILITY_MATRIX.tsv`，不把“家族有此功能”冒充“当前DeepSeek kernel用了此功能”。

因此给一般性论文主张`NEAREST_NEIGHBOR_CROWDED`。这仅否定“看见多个warp访问同一weight line→缓存机制新颖”这条直线，不否定一个未测的DeepSeek-specific residual。若未来有独立授权，先验证字节/sector重复、实际cache service和critical-path暴露，再与保持同量化/路由语义的kernel dataflow强基线比；本轮不运行这些操作、不设计新机制。cuBLAS公开GEMV API没有披露`gemvX`内部CTA/warp方案，保持`UNKNOWN`。

原文/源码阅读等级：MARLIN v1§3.4、QUICK v1§2–3、FLUTE v3§3、CUDA Best Practices §10.2.1、CUTLASS Efficient GEMM相关章节为`SECTION_VERIFIED`；CUTLASS GEMV源码、AWQ GEMV源码、GemLite README/blog与vLLM Marlin MoE dispatcher为`CODE_OR_AUTHOR_DOC_VERIFIED`；cuBLAS仅API文档。作者代码均`NOT_RUN`。源码固定到CUTLASS `0b55a2f691d69981583568fd9eb69687b1f0de8a`、AWQ `d6e797a42b9ef7778de8ee2352116e0f48a78d61`、GemLite `89d9bc705c5dfca9115d3a5620f97a17ba0111a7`、vLLM `bcee730b1a9d25f0fd283a0ef6c19133ebeebf4f`。
