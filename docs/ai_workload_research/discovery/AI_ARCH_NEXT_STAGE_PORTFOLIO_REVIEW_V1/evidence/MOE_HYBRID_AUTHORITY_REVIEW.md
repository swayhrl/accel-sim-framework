# MoE / Hybrid 状态资格审查

Q2=动态KV/Hybrid State，Q3=MoE自然路由。两者当前均未建立新的native准入。A70N/O的0候选是源码范围结论；A30T仅保留H200条件性设计；A81仍停在真实权重authority门。旧STOP均不变。

## 历史结果与独立接受层级

| 对象 | 固定source commit | 独立审查 | 接受层级 |
|---|---|---|---|
| A70N | 5076223db5db0256fd0ccacec50b5347a0cab8c5 | A71及A72 | NO_SURVIVOR；SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE |
| A70O | 94ca01df352cf4cf707cd35e5f9f63d4eff014c6 | A71及A72 | 同上；0主/0备，不是全MoE性能负例 |
| A30T | 1a8b9317de4c16e3dd19018f7f42cae1ebf5750e | A32 | H200/SM90a条件性source candidate；SM89未准入 |
| A81 | 492c7c79e130d60cb344d723c15751afe81a5a82 | 本范围未找到后续独立native接受 | NO_REAL_TENSOR_AUTHORITY；G1未准入 |

原报告：[A70N](https://github.com/swayhrl/accel-sim-framework/blob/5076223db5db0256fd0ccacec50b5347a0cab8c5/docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/REPORT.md), [A70O](https://github.com/swayhrl/accel-sim-framework/blob/94ca01df352cf4cf707cd35e5f9f63d4eff014c6/docs/ai_workload_research/discovery/A70_O_MOE_EXECUTION/REPORT.md), [A30T](https://github.com/swayhrl/accel-sim-framework/blob/1a8b9317de4c16e3dd19018f7f42cae1ebf5750e/docs/ai_workload_research/reviews/AI_ARCH_A30T_MOE_OPERATOR_RESOURCE_DISCOVERY_174NEW_V1.md), [A81](https://github.com/swayhrl/accel-sim-framework/blob/492c7c79e130d60cb344d723c15751afe81a5a82/docs/ai_workload_research/discovery/A81_GROUPWISE_LOWBIT_FEASIBILITY/REPORT.md)。独立审查：[A71](https://github.com/swayhrl/accel-sim-framework/blob/94f2b2f7d7def1adac47c76ee279eb78977c654a/docs/ai_workload_research/reviews/AI_ARCH_A71_A70_N_O_P_PARALLEL_DISCOVERY_INDEPENDENT_REVIEW_2026-10-16_V1.md), [A72](https://github.com/swayhrl/accel-sim-framework/blob/df7e11bc1206a53e4dd28c021309baf26142a333/docs/ai_workload_research/reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md), [A32](https://github.com/swayhrl/accel-sim-framework/blob/53a333f2b38236632f1c371bb72119dbf52f2b14/docs/ai_workload_research/reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)。

source commit与review commit已分开记录；较晚审查接受旧source STOP，不等于较晚执行authority。本次查了非shallow本地Git、固定CURRENT_STATE/证据索引及相关all-ref提交摘要，没有建立能替代A70N/O的新accepted同族native authority。该结论仅限显式检索范围，不能由ref存在认定执行，也不声称全局不存在其它证据。JSON记录全部commit/tree/blob/SHA256及关键行。

## Q2：动态KV / Hybrid State

模型source锚是Qwen3.5-4B revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a：24 GDN+8 full-attention，dense FFN，不能借家族MoE标签。历史BF16权重/FP32 state合同不是本机权重、backend或容量已合格的证明。

强软件反证包括vLLM mixed-page packing、prefix命中交集/合法checkpoint及融合state路径，SGLang unified/radix/所有权捐赠，以及ReplaySSM的ring+checkpoint/flush。固定版本SGLang unified与linear Replay不能共同启用；GDN fork不能冒充上游Mamba2默认能力。不可把这些组件拼成虚构的超级baseline。

缺口包括：完整合法权重/tokenizer；真实会话、prefix分支/更新轨迹及预冻holdout；state方向/dtype、conv与recurrent同端点以及未flush ring正确性；实际可启用的强backend/ABI/显存预算；完整请求/decode的copy/flush暴露wall。49.125MiB状态内容/序列只是几何，不是DRAM或时间测量。

只有明确不同的自然生命周期变量，才适合另审有界、可证伪的发现合同。无需先有完整硬件上界才能提出发现探针，但模型、输入、质量、软件和资源门不能省略。若只剩allocator工程、copy/flush不在关键路径、强软件吸收差异、质量失败或资源未资格化，STOP。旧source结果不自动授权GPU。

## Q3：MoE自然路由

A70O的BF16 Qwen3.5-35B-A3B config revision 41adbc1e50345066ac5153217957e9910204e632，与A30T的FP8 revision b955db3baa2e2fe51de7455fdfa08d7c29865abd是不同表示身份。两者都没有在本审查建立完整本机权重/自然输入/强后端准入。

兼容H200/SM90a、E256/H2048/I512、M≤8的block-FP8合同，需要正面对照MonoMoE和真正调优且支持的vLLM/FlashInfer grouped路径，不能退回逐expert循环制造空间。公开MonoMoE输入已有router_logits；同边界须锁为logits→routed输出，router projection、shared expert、残差和通信等量纳入或明确单列。现有软件融合/排序/重叠收益不是强软件后的硬件剩余。

旧E3固定提交378487015e513ed666c0929ca3f6c00392ff11c3只支持Q30 Layer24/S2/T2048 Prefill expert-loop诊断。CPU独立复核16384 assignments、93活跃expert、活跃min/median/max=1/14/1602，与元数据一致。它不是Qwen3.5自然B1/4/8 Decode，没有新强fused完整wall；合成热点H改变激活集合，不能作为同任务免费上界。

缺口包括真实逐层逐步logits/selected ID/score/n_e、相同权重与scale/packing、top-k/tie/renormalization及输出质量、固定backend完整operator/请求配对、独立自然输入。探索prompt重用不是holdout；独立prompt也不自动证明跨模型泛化。

SM89不能承接公开SM90a MonoMoE。目标40层routed FP8 payload约30GiB且未计其它组件；单层fit不是16GiB完整请求资格。H200设计只是另需审批的条件，不是资源已到位或已经执行。若无法保持路由/表示/输出、同边界强后端不合法、普通tile/layout/preparation解释差异、自然负载不出现目标区或完整效果在噪声内，STOP。

## A81跨题约束与资源

A81验证了历史activation摘要，但缺exact frozen W4权重字节；G1 A/B未执行、numeric_pass=null。不能用activation哈希、代码ref或条件等式补齐真实tensor pair，也不能迁移AWQ容差或低bit结论作为Q2/Q3质量PASS。此处仅git show历史记录，没有再查资产路径或恢复旧Goal。

本审查串行执行CPU Git/JSON/整数复核，只新增本md及json。没有GPU/CUDA/NVML、设备扫描/锁、164连接、活动GPU raw、模型/数据扫描、下载、安装、merge或旧输出修改。固定对象本地已有，fetch=0。CPU RSS及非连续全任务峰值边界见JSON。
