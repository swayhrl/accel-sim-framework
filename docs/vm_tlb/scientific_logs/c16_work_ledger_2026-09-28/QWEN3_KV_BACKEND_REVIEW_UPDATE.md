# 最新增量：Qwen3 KV后端依赖审查与当前Lane状态

日期：2026-09-28。本文件晚于Lane8 warp请求几何与OLMoE多输入路由采集记录。

## 1. Lane8 Qwen3 KV结果

174-new / Lane8 完成CPU-only独立审查：
- branch `hrl/c16-qwen3-kv-context-backend-audit-174new-v1`
- commit `b2975f163f319b5e339808877246c49cbf8a64cd`
- tree `bab608dbe421d59048b698b1cecf964821c5fe0d`
- review pack `docs/vm_tlb/review_packs/C16_QWEN3_KV_CONTEXT_BACKEND_AUDIT_174NEW_V1/`

远端分支与commit一致。

独立raw闭合：
- S2/S3各8个shard全部执行，header/count/terminal/overflow/hash闭合；
- S2 CTA范围0..16391、union16392、总active-lane events 16,785,408；
- S3 CTA范围0..65543、union65544、总active-lane events 67,117,056；
- 四个source LDG静态路径100%映射到同一replay内的`KV_POST_UPDATE_K`；
- 四个destination STG静态路径100%映射到`KV_DERIVED_REPEAT_K`；
- 不使用跨process/cross-replay VA关系。

上下文扩张：
- source LDG与destination STG都从8,392,704 events增至33,558,528；
- grid、source events、destination events和总events的S3/S2比均为3.998535871156662；
- 2049→8193 endpoint使其不是精确4倍；
- tensor storage层面，[1,8,T,128]到[1,32,T,128]的repeat-K展开是精确4倍；
- 128B footprint同样约3.9985倍；更粗页面比例受边界量化影响。
这些page数据只是footprint descriptor，不是TLB miss率；lane-event也不是DRAM流量。

## 2. 后端适用范围

审查绑定Transformers v4.51.0 tree commit `0720e206c6ba28887e4d60ef60a6a089f6c1cc76`，四个指定Git blob全部精确匹配。

对Qwen3-8B：
- eager：显式调用repeat_kv扩展K/V；
- SDPA integration：调用PyTorch SDPA前同样显式展开；
- FlashAttention2 integration：HF层不显式repeat，传递原始KV-head数；
- FlexAttention：接受的32 query heads配置走enable_gqa正常路径，不触发显式repeat fallback。

因此V20的显式repeat-K kernel是eager/SDPA式实现路径的有效证据，不是Qwen3模型固有必须发生的KV-cache行为。后端无关的部分只包括compact K-post本身随上下文增长，以及32 query heads / 8 KV heads的GQA语义关系。

该结果不提供：
- 跨后端性能排序；
- TLB/cache因果；
- DRAM流量结论；
- 新TLB/cache机制的直接动机。

如果未来项目问题转向“真实部署中不同attention backend的访存/性能差异”，同输入eager与一个合法优化backend的matched native比较才有条件性价值；当前不自动授权。

## 3. 当前调度

- 174-new / Lane4：原R0/M1/diagnostic长跑继续，不读partial、不修改。
- 174-new / Lane6：OLMoE多输入路由独立consumer按已发布handoff推进/等待用户下发状态，不与Lane8混用。
- 174-new / Lane8：Qwen3 KV后端依赖审查已完成并STOP，窗口可复用。
- 109 / Lane7：用户明确说明split-K访存状态实验已经下发，当前正在执行；不再记录为“handoff prepared but not dispatched”。

本文件只更新项目记录，不读取Lane7运行中的partial结果。

## 4. 来源S45

固定commit：
`b2975f163f319b5e339808877246c49cbf8a64cd`

主要来源：
- `AUTHORITY_AUDIT.json`
- `S2/S3_FULL_SCOPE_AUDIT.json`
- `S2/S3_OBJECT_JOIN.tsv`
- `S2_VS_S3_CONTEXT_SCALING.json`
- `SOURCE_DESTINATION_AMPLIFICATION.tsv`
- `PAGE_FOOTPRINT_DESCRIPTORS.tsv`
- `BACKEND_SOURCE_AUDIT.tsv`
- `BACKEND_REPRESENTATIVENESS.md`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`

与原70条总账、EXP06、EXP07合并后，本次新增EXP08，总计73条逻辑工作记录，不是73次独立实验。
