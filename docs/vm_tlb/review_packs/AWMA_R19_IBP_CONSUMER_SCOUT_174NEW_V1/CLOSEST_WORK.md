# 最近原始工作与 claim 边界

| 来源 | 已提供能力 | 与 R19 Reddit/GraphSAGE 准备项的关系 |
| --- | --- | --- |
| [IBP EuroSys 2026](https://akkamath.github.io/files/EuroSys26_IBP.pdf) | invariant-bit 无损格式；pinned-host 压缩行；GPU 发起 PCIe 取数与并行解压；Legion GPU cache/lookup/fetch/decode 合核 | 强基线本身。仍将完整 sampled-feature buffer 写入 GPU global memory、再交付训练模型。 |
| [DFloat11](https://arxiv.org/html/2504.11651) | BF16 权重动态长度无损编码、两阶段 GPU 解压，之后 GEMM | 不执行直接融合；压缩格式和数据对象均不同。 |
| [ZipServ](https://arxiv.org/html/2603.17435) | TCA-TBE 固定长 BF16 格式；decode 的 ZipGEMM 直接将解码权重供 Tensor Core，prefill 则独立展开 | 已直接覆盖 LLM 权重“解压+GEMM”概念，阻止宽泛创新 claim；不是 pinned-host GNN feature fetch。 |
| [Tan 等 2026 tile-rANS/GEMM](https://arxiv.org/html/2606.15789) | 压缩权重 tile 流式解码到 shared memory 并与 GEMM 流水 | 另一强 direct-compute 近邻，进一步限定 R19 不能泛称首个 decode-consume。 |
| [nvCOMP Device API](https://docs.nvidia.com/cuda/nvcomp/device_api.html) / [nvCOMPDx](https://docs.nvidia.com/cuda/nvcompdx/index.html) | 可在 GPU kernel 中调用的通用 device 解压构件 | “device 内解压”已是公共软件能力；文档本身未构成 IBP+GraphSAGE 实例。 |
| [UCCL-Zip](https://arxiv.org/html/2604.17172v2) | GPU 通信场景中的压缩与传输/collective 合并 | 属于通信路径的强先例；不证明本卡的首层 GraphSAGE 消费融合。 |

四个概念必须分开：压缩**格式**、PCIe/通信**重叠**、GPU **设备解压**、真实计算算子的**直接压缩执行**。本轮仅把最后一个概念在 IBP 的真实 GNN consumer 上留作有界证伪问题；最近邻差别仍是假设，不是已证明的新颖性。
