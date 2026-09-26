# Closest-work map

The screen uses primary papers/project pages and distinguishes their proposals
from our accepted evidence.

| family | closest work | author contribution | overlap with candidate | residual after comparison |
|---|---|---|---|---|
| A | FlexGen (ICML 2023), PagedAttention/vLLM and the accepted HELM/UVM screen | object-aware weight/KV placement, paging and offload | persistent weights/KV lifetime and movement | no accepted object-attributed material cost beyond covered placement/offload |
| B | [ClusterFusion](https://arxiv.org/abs/2508.18850) | cluster collectives keep QKV/attention/projection intermediates on chip and reduce launches/HBM traffic | real producer-consumer state and intermediate materialization | only a trace/sampling-methodology question survives until retained-state cause is localized |
| B | [Deep Kernel Fusion](https://arxiv.org/abs/2602.11808) | deep transformer fusion cuts HBM traffic and improves cache reuse | predecessor/consumer locality and intermediate traffic | generic fusion is excluded; no new fusion mechanism claim |
| C | [AWQ](https://proceedings.mlsys.org/paper_files/paper/2024/file/42a452cbafa9dd64e9ba4aa95cc1ef21-Paper-Conference.pdf) | activation-aware W4 weights plus TinyChat packing/fusion | exact deployment uses AutoAWQ weight-only quantization | representation benefit and software-kernel optimization are covered |
| C | [QServe/QoQ](https://arxiv.org/abs/2405.04532) | W4A8KV4 co-design addresses 20-90% dequantization overhead with reordering/register parallelism | dequantization/runtime overhead and low-throughput CUDA-core work | generic dequantization tax is directly covered |
| C | [StreamDQ](https://arxiv.org/abs/2607.08993) | moves dequantization into custom HBM to avoid GPU on-chip traffic and writeback/reload | hierarchy-level traffic amplification from dequantized weights | memory-side dequantization is directly covered |

Broad pressure-aware scheduling and cache/MSHR controls remain excluded by the
accepted Lane F closest-work map. No family may claim novelty merely from AI
object names, predecessor context, or quantized representation.
