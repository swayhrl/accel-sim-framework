# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A71。A70四线并行Discovery：N、O、P三条已STOP且经独立审查接受；M仍据用户回报处于执行中。** 科研协调者：ChatGPT／AI-ARCH Discovery。本页是Git证据导航，不是实时Codex进程状态。已完成的三条均为`NO_SURVIVOR_IN_SEARCH_SCOPE / SOURCE_ONLY`，无native测量、无新增GPU建议；**三个0候选不是大模型问题已被实测否定。**

此前完整A70派发快照：[CURRENT_STATE@5abd9245](https://github.com/swayhrl/accel-sim-framework/blob/5abd9245f24da230cc8f53431601a91d27254bfd/docs/ai_workload_research/CURRENT_STATE.md)；完整并行合同：[A70 Goal包](goals/AI_ARCH_A70_MAINSTREAM_PARALLEL_DISCOVERY_GOAL_PACK_2026-10-16_V1.md)（固定发布HEAD `8f24af162ba37b4fa37f7a18d89b0fdb62697942`）。旧快照、原始Goal、报告、运行和候选JSON均保留，不合并任何执行HEAD。

## 1. 本轮Lane状态及原始科学权威

| Lane | 逻辑研究对象／宿主 | 用户回执与Git固定执行 | 科学状态 |
|---|---|---|---|
| **M-A70** | 主流LLM长上下文、Prefill/Decode混合服务／109 | 用户明确仍在执行；**不推测其最终commit，不轮询、不追加任务** | `RUNNING_USER_REPORTED / PENDING_REPORT` |
| **N-A70** | 混合Gated DeltaNet/KV状态／174-new | [原报告](https://github.com/swayhrl/accel-sim-framework/blob/5076223db5db0256fd0ccacec50b5347a0cab8c5/docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/REPORT.md)，commit `5076223db5db0256fd0ccacec50b5347a0cab8c5`，tree `592e12903c8fa029fb5108a967f8a00bb9cb9458` | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP`，0候选 |
| **O-A70** | MoE自然路由和融合后端／109 | [原报告](https://github.com/swayhrl/accel-sim-framework/blob/94ca01df352cf4cf707cd35e5f9f63d4eff014c6/docs/ai_workload_research/discovery/A70_O_MOE_EXECUTION/REPORT.md)，commit `94ca01df352cf4cf707cd35e5f9f63d4eff014c6`，tree `b5b3d7f8f925c50aa845cebec2cb3057fe91b261` | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP`，0候选 |
| **P-A70** | 通用视觉语言模型视觉→语言交接／174-new | [原报告](https://github.com/swayhrl/accel-sim-framework/blob/f2399777a30f4fdafa26858b3cd418e497538db2/docs/ai_workload_research/discovery/A70_P_VLM_PIPELINE/REPORT.md)，commit `f2399777a30f4fdafa26858b3cd418e497538db2`，tree `811616c50e4594e1884d4ee4e4c622a72fb953d1` | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP`，0候选 |

**独立审查入口：[Round A71 N/O/P三线科学审查](reviews/AI_ARCH_A71_A70_N_O_P_PARALLEL_DISCOVERY_INDEPENDENT_REVIEW_2026-10-16_V1.md)，首次独立审查commit `94f2b2f7d7def1adac47c76ee279eb78977c654a`。** 三条Goal→final均ahead1、只有自身目录四文件；final→各自远端branch `identical`；Git-data tree与回执三项一致。N/O/P分别21/24/17条11列EVIDENCE（共62条、每条本Lane ID唯一、列数结构正确），三个`CANDIDATES.json=[]`已实际读取。独立只抽查关键原始论文/固定源码和原E3元数据，不自称重新运行或逐项重hash全部12个文件SHA256。

## 2. 三条零候选究竟证实了什么

- **N**：模型`Qwen3.5-4B`纯文本路径24个GDN层+8个完整注意力层；vLLM/SGLang已有混合页、状态checkpoint、前缀reuse和部分状态copy路径；ReplaySSM针对Qwen3.5-4B有直接软件论文与fork实现，GDN研究fork能力不等同当前upstream全部默认启用。独立复算24层GDN每active序列49.125MiB FP32+BF16历史内容、全attention KV约32KiB/token，属于内容容量公式而非HBM/时延。新的copy/flush暴露wall、真实部署及多配置差异仍`UNKNOWN`；没有足够区别于已有软件的native推荐问题。
- **O**：FlashInfer MonoMoE已覆盖SM90a、block FP8、E256/H2048/I512、小token融合，普通分组/排序/融合属于强软件近邻。旧C16 E3 `NATURAL_ROUTING.json@378487015e513ed666c0929ca3f6c00392ff11c3`的真实对象是Q30 Prefill expert loop，**不是现代fused Decode**；16384 assignments、93活跃专家、最大1602。独立从该直方图重算按expert BM16/32/64/128的条件scheduled/padding为17248/864、18304/1920、20544/4160、25344/8960，均不能当现代实际kernel的工作量或wall。H200条件式方案不是已准入任务。
- **P**：vLLM v0.20.1已经提供视觉编码器Graph、预算捕获、处理/embedding缓存、分块与部分分离服务。官方单GPU性能表实为GB200、Qwen3-VL-30B-A3B、VisionArena-Chat单图、`vllm bench mm-processor`局部分母，**不代表Qwen3-VL-8B多图/视频TTFT或完整wall**。自然多图/视频的Graph预算变化、阶段竞争和质量成本仍`UNKNOWN`；不以“未披露”自动晋升硬件问题，也不声称所有VLM问题已被解决。

**结论类型准确标注：`SOURCE_SCOPE_NO_SURVIVOR`；局部想法可以记`SOFTWARE_NEARBY_DIRECT`，但不能将整个模型线写成`SOFTWARE_ABSORBED`或`NEGATIVE_MEASURED`。** 不将论文单卡H100/H200/GB200指标迁移为109 RTX4080的实测或合法优化上界。

## 3. 下一动作和防止保守筛选失真

- **Lane M继续按原A70完整合同独立执行。** 当前仅据用户“Lane M正在执行”确定状态，没有轮询其分支/进程，也不发重启、扩范围或追求阳性的消息。M完成后收到final回执即可独立审查，然后四线横向去重，最多保留2—3个可证伪主问题，可以仍为0。
- **先不安排下一波四个Codex，也不租H200、不部署新vLLM、不触发GPU或模型下载。** 三条结束后确实释放了研究窗口，但简单再读同一批最新kernel/缓存源码预计无法增加研究信息。
- **修正筛选方法而不降低科学标准：** Discovery阶段不要求预先拿到强软件之后的原生wall，才允许设计受控最小探针。若存在明确尚未覆盖的**工作负载或部署变量**、一个成熟软件允许的公平对照、能区分软件/硬件解释的最小真实数据和便宜的否定条件，可作为`NATIVE_PROBE_PROPOSED`候选供另审；但是只有“作者没测/这里可能慢”不够。局部算子、自然coverage与完整请求应分开；强调主流模型价值优先于现有资产方便性。
- 用户此前确认ScanNet当前无许可/资产，Q-S A69已转储备，不为维持并行回到小众数据任务。GNN A61/A65/A67、C16、AWMA、ISCAS原科学冻结与资源权限保持。
- 三线资源来自各自RECEIPT而非本窗口现场核验，尤其P的进程树RSS与网络量未连续测得；正常保留缺口，不为补无关监控另起研究Goal。

**当前实际新GPU/下载/安装/模拟器授权：0。A71审查只读，协调文档更新不产生节点作业。**
