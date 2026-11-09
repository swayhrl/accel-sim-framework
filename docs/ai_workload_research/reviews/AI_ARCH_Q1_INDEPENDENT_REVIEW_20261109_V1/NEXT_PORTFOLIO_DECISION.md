# 下一阶段研究组合建议与最小可证伪合同

2026-11-09，提交 AI-ARCH-5 审查；这是 CPU-only 决策建议，没有新 GPU Goal。Q1 作为已收口、独审接受的晚期 3DGS 分析基点；`NO_HARDWARE_CANDIDATE_PROMOTED`。优先把下一项工作放在 **Hybrid GDN/KV 的真实执行资格调查**，但当前 `NO_GPU_PROBE_READY`。理由是 A70N `5076223db5db0256fd0ccacec50b5347a0cab8c5` 只得到 `SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE / NO_SURVIVOR_IN_SEARCH_SCOPE`，尚无完整合法模型、自然会话、状态/质量与强 runtime 的配对证据。资格缺口真实存在，不能用源码/config 或缓存名替代。

| 组合 | 当前处理与证据边界 |
| --- | --- |
| Hybrid/KV | 首选 CPU 只读真实资格调查；找到合法可读模型、自然会话、精度/质量、状态和强 runtime 后，才讨论受控原生 probe。若任何必要实体缺失，结论为 `NO_GPU_PROBE_READY`，不补造 synthetic 输入。 |
| MoE | 保留自然 route、FP8 格式及 MonoMoE 等强软件对照；A30T `1a8b9317de4c16e3dd19018f7f42cae1ebf5750e` 是 H200/SM90A 条件路线，109 RTX4080/SM89 不可替代。未有 H200 当前资源资格时停在条件研究。 |
| Qwen | V11 `339559f6972f25ac1aec78fb3577b7bd2640410e` 是成熟真实 native/profile 分析基点，PARKED，不自动 V12。 |
| 3DGS Q1 | 若继续，先提出具体强软件残余反事实和质量门；不重复完整 late 状态生产、线程矩阵或把 T16 原基线说成新优化。 |
| 其它 | Low-bit 缺合法真实 tensor；VLM、DiT、GNN、serving、RL、PPA 等维持各自 SOURCE_ONLY/STOP/PARKED，不能因现成分支而重开。 |

## 建议的单一最小合同：Hybrid/KV 真实资格调查（CPU-only）

**问题**：在可合法读取的真实 Hybrid GDN/KV 模型及自然会话下，是否存在一组固定模型/input/runtime/precision/质量条件，使动态状态与 KV 的完整生命周期可被观察，同时强软件实现后仍有待定位的资源约束？本合同只判定能否进入 GPU 设计，不要求产生正候选。

**输入与对照冻结前置**：固定模型权威版本、权重来源与可读资格、实际 tokenizer/自然会话字节身份、状态初始化与跨请求生命周期、输出质量判据；固定同语义强 runtime 和 Strata/HybridKV 适用性差异，明确容量、精度、batch/长度及完整请求分母。只读核来源/许可/现有资产，不能下载模型或改变 dtype、精度、质量门来凑资格。

**最小证据与 STOP**：交付逐项身份表、自然会话可复现性、模型与 runtime 可调用接口、状态/KV 生命周期及强软件最近邻矩阵，明确“可验证/缺失/不适用”。任一合法实体、自然输入、质量门或可比强 runtime 缺失，即 `NO_GPU_PROBE_READY / STOP`，保留负证据，不改成性能负例。若全通过，只形成一份有资源上限、观察字段、停止条件和当前共享 GPU 准入的后续 **提案**，不在本合同中启动 GPU。

**未来 GPU 门**：须由用户/AI-ARCH-5 明确新科学对象与预算，取得当前 109 资源所有者窗口并核实共同 `flock`、预约、loaded gate、实时身份和 context 清理；H200 条件不能借用 109。没有授权时不运行 Profiler、模拟器、RTL、模型下载或训练。
