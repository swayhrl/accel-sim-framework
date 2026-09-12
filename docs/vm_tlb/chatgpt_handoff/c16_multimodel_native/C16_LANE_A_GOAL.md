# C16 Lane A — Local Preparation, Static Coordination, Final Integration

Goal: `C16_A_LOCAL_PREP_AND_INTEGRATION`。

Branch target: `hrl/vm-c16-a-static-coord-v0`。

Lane A 不是 GPU 执行窗口。它负责把租 GPU 前能做的工作尽量做完，并最终整合 G/C/H 的固定提交结果。

## 负责阶段

主责：C16-0.0~0.2、0.6、0.7、0.9；C16-5.4；C16-6.2~6.4。
协作：C16-5.1~5.3/5.5 的身份、静态上下文和最终证据分级。

## A0 — C16-0.0：先闭合 C15-A

C15 Lane A 在 C16 开始时仍需一个 metadata/provenance-only closeout。只读参考 C15-B/C final accepted commits。

必须修正/标明：
1. planning authority 与 A producer implementation/artifact/handoff 分离；
2. B 的 artifact checkpoint `57e2ef203befc96cfcefe00de2aaf8b0baab5d8b` 与 final handoff `721e30f3...` 分离；
3. checkpoint file-range alias 与 semantic tying 分离，缺 header 不得写 `CONFIG_AND_HEADER_CONSISTENT`；
4. `fields_verified` 逐 deployment 实际生成，不使用固定模板；
5. `physical_bytes` 若保留为 legacy schema，明确其含义是 checkpoint/file storage，不是 GPU PA；
6. MoE `intermediate_sizes` 当前不足以完整表达 routed/shared expert widths，必须在 C16 registry 中升级或明确 unresolved。

不重新下载完整权重，不修改 C15 科学数值，不启动 GPU/simulator。

输出 `C15_A_CLOSEOUT_RECEIPT.md` 与 `C16_BASELINE_MANIFEST.json`，后者固定 C15 A/B/C 可消费提交。

## A1 — C16-0.1：冻结模型矩阵

Primary Wave-1：
- Llama3.2-1B historical bridge；
- Qwen2.5-0.5B-Instruct；
- Qwen2.5-7B-Instruct；
- Qwen2.5-7B-Instruct-AWQ。

Wave-2：
- Qwen3-8B；
- Qwen3-30B-A3B；
- DeepSeek-V2-Lite。

模型选择在任何新动态结果前冻结。每行记录 role、revision source、desired dtype/backend、是否 training/tuning 或 prospective holdout 候选。

## A2 — C16-0.2：本地模型资产

尽可能在本地服务器下载/准备模型，GPU 服务器只做 rsync/import。

每个 deployment 生成：
- immutable revision；
- tokenizer identity；
- file list；
- per-file size/SHA256；
- config/tokenizer hash；
- weight format；
- total bytes；
- required runtime adapter/backend。

不得为了填满模型矩阵下载未授权/无法验证的模型。Wave-2 缺失不阻塞完整 Wave-1。

## A3 — C16-0.6：输入集

冻结至少三类输入：TEXT、CODE、STRUCTURED。保存原始文本 hash。调用各 deployment tokenizer 生成实际 token IDs/length receipt。

同样文本不等于同样 token 数；后续表同时记录 requested scenario 与 actual tokens。

## A4 — C16-0.7：场景

冻结 S0~S4：
- S0 B1/T128/Decode4 canary；
- S1 B1/T256/Decode16；
- S2 B1/T2048/Decode32；
- S3 B1/T8192/Decode16；
- S4 B4/T2048/Decode16。

MoE/30B first-wave 只要求 B1/T256 与 B1/T2048；资源稳定后才能新增场景。不要因 OOM 悄悄改 batch/context，而应 `SKIPPED_RESOURCE`。

第一版 scenario 明确关闭或固定：continuous batching、prefix caching、speculative decoding、TP/PP/EP；若框架无法关闭，作为 deployment identity 一部分记录。

## A5 — C16-0.9：GPU package

只在 G/C/H 的本地工具达到对应 offline gate 后发布 `C16_GPU_PACKAGE_MANIFEST.tsv`。A 负责确认：
- assets；
- inputs；
- code commit；
- wheels/env；
- wrappers；
- expected hashes；
- transfer plan；
- required vs optional Wave-2 files。

Package 发布不代表 G0~G3 已通过。

## A6 — C16-5.4：共性分级

使用固定 G/C/H 提交，只在同一 metric definition/method 下做 lineage-level 聚合。

`cross-model common pattern` 必须 >=3 independent lineages 同方向。两点只允许 family-level；单点 deployment-specific。

不要用静态参数差异解释动态性能因果。

## A7 — C16-6.2~6.4：收口

整合完整成本；建立/否决行为类别；最多 3 项 T3 request。

最终报告必须明确区分：
- static source facts；
- real native measurements；
- address structural metrics；
- retrospective simulator evidence；
- unavailable/unresolved。

如果 G 没有至少 3 个真实 deployment 的 native census，或者 C16-6.1 没有任何关键指标达到可用 screening 级别，最终状态只能 `C16_MULTIMODEL_NATIVE_FOUNDATION_PARTIAL_READY_FOR_REVIEW`。

## A 允许/禁止

允许：本地模型下载、hash、tokenization、small metadata、CPU分析、固定提交整合。
禁止：AutoDL GPU profiling、NVBit、Accel-Sim新回放、修改G/C/H结果。

普通工程问题自行解决并继续；缺数据就保留 gap，不等待用户逐阶段确认。