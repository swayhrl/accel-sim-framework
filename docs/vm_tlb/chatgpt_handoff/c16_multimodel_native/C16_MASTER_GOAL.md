# C16 Master Goal

Goal: `C16_MULTIMODEL_NATIVE_MEMORY_CHARACTERIZATION`。

## 总体问题

C15 已经得到：T0 静态多模型信息可低成本获得；仅依赖 phase + opaque kernel order 的 Sampling V1 不合格；当前缺失的是廉价但真实的 native semantic/shape/duration 目录。C16 因此把重点转向真实 GPU workload characterization，而不是继续扩大单一 Llama3.2-1B 的 full-ROI 仿真。

## C16-0 — Local Preparation

全部尽量在现有本地服务器完成。

- 0.0：C15-A metadata/provenance closeout；冻结 C15 A/B/C 最终输入。
- 0.1：冻结模型矩阵与角色。
- 0.2：准备本地模型资产与逐文件 SHA256 receipt。
- 0.3：准备离线 Python/wheel/AutoDL bootstrap、Nsight/NVBit/Tracer 版本审计。
- 0.4：完成统一 native runner、NVTX 标记、scenario driver、profile wrapper。
- 0.5：完成 runtime object-map V2 设计与 observer fixture。
- 0.6：冻结输入文本、tokenizer、token IDs/长度/hash。
- 0.7：冻结场景矩阵。
- 0.8：完成本地解析/selector/fingerprint 工具和 fixture。
- 0.9：生成 `C16_GPU_PACKAGE`、`EXPECTED_HASHES.tsv` 和 transfer plan。

Gate：`C16_LOCAL_GPU_PACKAGE_READY`。

## C16-1 — AutoDL Bring-up + Inline Qualification

资格验证与正式运行连续执行，不单独长时间占 GPU。

- 1.1：实例与资源 receipt；确认独占 GPU、VRAM、driver/CUDA、磁盘。
- 1.2：rsync/import + asset hash closure。
- 1.3：G0 native canary；通过立即放行 native baseline。
- 1.4：G1 nsys/NVTX canary；通过立即放行 full lightweight census。
- 1.5：G2 NCU canary；不支持的 metric 明确 `COUNTER_UNAVAILABLE`，不阻塞 G1。
- 1.6：G3 NVBit canary；通过才可做选择性地址采集。

## C16-2 — Multi-Model Native Census

- 2.1：native baseline：warmup + measured repeats。
- 2.2：完整轻量 kernel census，不输出完整 SASS。
- 2.3：运行实现审计：attention backend、KV representation、quant/dequant、MoE routing。
- 2.4：operator/layer/shape/dtype/implementation 归因；按累计 GPU time 统计覆盖。
- 2.5：heavy-tail / certainty-unit 识别。
- 2.6：Wave-1 先发布，让 C/H 立即开始消费；GPU 同时继续 Wave-2。

Wave-1：Llama3.2-1B、Qwen2.5-0.5B、Qwen2.5-7B raw、Qwen2.5-7B AWQ。
Wave-2：Qwen3-8B、Qwen3-30B-A3B、DeepSeek-V2-Lite（资源/兼容允许时）。

## C16-3 — Stratified Sampling V2

- 3.1：strata key = Phase × Operator × Implementation × ShapeBucket × DType；必要时再加 KV representation/quant mode。
- 3.2：Selector-R 概率抽样 + Selector-M representative/medoid 分离。
- 3.3：certainty units 权重 1；普通 stratum 用 N_s/n_s。
- 3.4：预算 12/24/48；保留随机 audit。
- 3.5：C12/C13 只作 `RETROSPECTIVE_ORACLE_CALIBRATION`。
- 3.6：prospective holdout：selector 版本先冻结，再看保留部署结果。

## C16-4 — Bounded Memory Characterization

- 4.1：代表窗口优先做 NCU counter。
- 4.2：根据 census + counter 决定哪些窗口值得 NVBit。
- 4.3：GPU 上有界 trace：每窗口 ≤4GiB 或 ≤20min；首轮 raw 总量 ≤64GiB。
- 4.4：本地 memory-only observer/proxy；若安全且验证充分可用于后续，但 full tracer 始终保留 fallback。
- 4.5：本地 address fingerprint：page/line/sector/read-write/object attribution。
- 4.6：跨 kernel set overlap / local reuse；禁止无证据 global-L2-order claim。

## C16-5 — Cross-Model TLB/Cache Analysis

- 5.1：统一 `deployment × scenario × phase` fingerprint。
- 5.2：优先做同部署变量：context、batch、Prefill/Decode。
- 5.3：再做受控 pair：Qwen scale、raw/AWQ、Qwen3 Dense/MoE。
- 5.4：共性证据分级：至少 3 个独立 lineage 同方向才可称 cross-model common pattern。
- 5.5：提出 TLB/Cache 问题，不直接跳到机制结论。

## C16-6 — Qualification & Architecture Handoff

- 6.1：按指标逐项给 Sampling 资格，不允许一个总 PASS 覆盖所有指标。
- 6.2：完整成本模型：准备/上传/加载/profile/capture/解析/retry/传输分账。
- 6.3：形成行为类别；如果数据不支持聚类则明确不强行分类。
- 6.4：最多 3 项下一阶段高保真请求，全部 `requires_new_authorization=true`，不自动执行。

## 模型与场景主矩阵

Dense 主场景：
- S0 B1 T128 Decode4 — canary only
- S1 B1 T256 Decode16
- S2 B1 T2048 Decode32
- S3 B1 T8192 Decode16
- S4 B4 T2048 Decode16

MoE/大模型第一轮只做 B1 T256 与 B1 T2048，稳定后再升级。MoE 在 T2048 额外使用多个冻结输入审计 expert routing。

## 强制停止条件

- 身份/hash 不闭合：该 deployment/run 不得进入科学表。
- profile perturbation 过大：可保留语义目录，但 profile duration 不作自然性能权重。
- G3 失败：不得批量 NVBit；继续 G1/G2。
- 采样误差不达标：保留 `NOT_QUALIFIED`，不改阈值、不挑 seed。
- raw trace 超预算：保留 `BOUNDED_PARTIAL`，不延长预算。
- 没有足够跨模型证据：不得称 common pattern。
