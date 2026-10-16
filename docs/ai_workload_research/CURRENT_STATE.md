# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A72：A70主流大模型四线并行Discovery全部完成并经独立审查，M/N/O/P均为`NO_SURVIVOR_IN_SEARCH_SCOPE / STOP`（四线合计0主＋0备）。** 这是四次`SOURCE_ONLY`范围内没有可晋升native的问题，不是主流LLM、MoE、混合注意力、VLM的GPU性能负结果。

固定历史导航：[A71（三线完成、M运行中）](https://github.com/swayhrl/accel-sim-framework/blob/0c891b59e28177bfbff1ce6a6744a26fa6d30ad2/docs/ai_workload_research/CURRENT_STATE.md)、[A70初次派发](https://github.com/swayhrl/accel-sim-framework/blob/5abd9245f24da230cc8f53431601a91d27254bfd/docs/ai_workload_research/CURRENT_STATE.md)。本次替换导航文字不改执行Branch、原始报告、raw、CANDIDATES或各STOP。

## 1. 四Lane的科学终态与固定Git authority

| Lane/宿主 | 固定final commit/tree | 原报告与审查边界 | 终态 |
|---|---|---|---|
| M／109：通用LLM长KV混合服务 | `f2d6324da298be26f39cda427f3e7db1a7e7031d` / `5cbb8f8eaa4fb00efcd51bc963bf68c6b3263d52` | [M原报告](https://github.com/swayhrl/accel-sim-framework/blob/f2d6324da298be26f39cda427f3e7db1a7e7031d/docs/ai_workload_research/discovery/A70_M_LLM_SERVING/REPORT.md)，21条证据 | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP` |
| N／174-new：混合递归state | `5076223db5db0256fd0ccacec50b5347a0cab8c5` / `592e12903c8fa029fb5108a967f8a00bb9cb9458` | [N原报告](https://github.com/swayhrl/accel-sim-framework/blob/5076223db5db0256fd0ccacec50b5347a0cab8c5/docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/REPORT.md)，21条证据 | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP` |
| O／109：MoE真实专家执行 | `94ca01df352cf4cf707cd35e5f9f63d4eff014c6` / `b5b3d7f8f925c50aa845cebec2cb3057fe91b261` | [O原报告](https://github.com/swayhrl/accel-sim-framework/blob/94ca01df352cf4cf707cd35e5f9f63d4eff014c6/docs/ai_workload_research/discovery/A70_O_MOE_EXECUTION/REPORT.md)，24条证据 | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP` |
| P／174-new：通用VLM视觉—语言交接 | `f2399777a30f4fdafa26858b3cd418e497538db2` / `811616c50e4594e1884d4ee4e4c622a72fb953d1` | [P原报告](https://github.com/swayhrl/accel-sim-framework/blob/f2399777a30f4fdafa26858b3cd418e497538db2/docs/ai_workload_research/discovery/A70_P_VLM_PIPELINE/REPORT.md)，17条证据 | `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP` |

固定A70共同Goal：`8f24af162ba37b4fa37f7a18d89b0fdb62697942`。全部四条从共同起点各ahead1且仅四份本Lane文件，final→各自远端HEAD identical；Git-data commit tree与各Lane回执一致，CANDIDATES.json均为空。独立TSV结构检查每条11列且ID唯一，四线合计83条（含代码/历史/模型配置，并非83个原生实验组）。

[A71 N/O/P独立审查](reviews/AI_ARCH_A71_A70_N_O_P_PARALLEL_DISCOVERY_INDEPENDENT_REVIEW_2026-10-16_V1.md)保留；**最新[A72 M及四线综合独立审查](reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md)**新收口。

## 2. 研究含义：哪些已被直接近邻覆盖，哪些仍未回答

- **M**：Sarathi-Serve/DuetServe/Nexus/NanoFlow等直接涉及chunked Prefill、attention-aware长KV调度、按需SM划分或算子级重叠；DuetServe ICML2026基于H100与Qwen3-8B/14B，报告mean TTFT/TBT和请求吞吐，不是当前最新vLLM在所有自然长KV/SLO条件下的覆盖证明。固定vLLM确有按batch模式选择Graph的代码，但109实际图命中/竞争wall未测。M的Qwen3-8B BF16两条32K KV+参数内容约24.256GiB，已超16GiB RTX4080，不是完整服务原生实验资格。M起步阶段一次Git双线程配置/实际并发未测，receipt如实保留，不要求重跑已完成研究。
- **N**：混合页、递归state checkpoint及GDN逐token写回已有成熟代码/ReplaySSM直接论文，不能重命名；真实拷贝/flush对暴露wall和多种合法配置的适用性仍UNKNOWN。
- **O**：FlashInfer MonoMoE和当前融合/分组实现限制了常规token-sort／expert融合创新性；C16 E3真实历史对象是Q30 Prefill expert loop，非现代fused Decode，不能反推现有强后端已无残余。
- **P**：vLLM已支持视觉Graph、缓存、编译/分离服务等；公开Qwen3-VL-30B-A3B GB200 VisionArena单图mm-processor实验不能代替Qwen3-VL-8B多图/视频完整TTFT/ITL或质量。
- **共同裁决**：四条均为`SOURCE_SCOPE_NO_SURVIVOR`而非`NEGATIVE_MEASURED`或全域`SOFTWARE_ABSORBED`。不使用逻辑字节、padding、模型容量直接算硬件stall或性能利益。不因0候选追加H200、多卡、CUDA、编译/模型下载，GNN、Q-S、AWMA、C16/ISCAS的冻结边界未变。

## 3. 下一阶段：调整发现方法（A73候选组织，尚无新执行Goal）

继续优先**主流通用模型与真实任务**，但不再给四个Codex重复“找服务软件没有实现的特性”。A73拟三条互补研究流：

1. **Workload-first｜真实输入及模型阶段组成**：从合法真实请求/输入中寻找被现有论文忽略的部署变量，产出可复现来源、质量／SLO约束、自然分布和明确能否否定的假说；不为造差异创建合成极端热点。
2. **Architecture-first｜GPU资源限制与已发表硬件反事实**：重点审近期ISCA/MICRO/HPCA/ASPLOS/MLSys/OSDI的具体模型、实验组、软件基线、硬件变量和因果约束，寻找新的资源敏感度问题；不只调查最新runtime API。
3. **Measurement-first｜最小原生资格计划（依赖前两条提出问题）**：用被选问题倒推最小主流真实模型及软件对照，区分109 RTX4080可验证的有范围样本与真正需大显存的科学对象；只做CPU静态资源／ABI合同草案，GPU资格另行批准。

先并行第一、第二流，待获得初步问题变量再启动第三流的具体实验设计，避免四个Lane都因相同强软件近邻交空候选。此为A72协调建议，**未派发新Codex Goal、未建立新GPU任务或下载许可**；能否进入native由下一次科学合同决定。普通工程问题在获准Goal范围内自解，不人为拆轮。

## 4. 当前Lane/资源权限

A70的M/N/O/P全部据用户报告完成并STOP；AI-ARCH本线此刻无待审执行回执或已授权的新GPU/CPU作业。本窗口只读Git和公开原文、控制端算术，协调写入不产生节点执行。

C16/AWMA/ISCAS原branch/STOP和资源授权不因本线更改。109共享GPU campaign lock继续遵守，174-new/164不接收本阶段新任务。旧A61/A65/A67 GNN与A69 ScanNet已冻结/停投，A62/A63稀疏训练储备未晋升。

**Round A72状态：四线Source Discovery科学收口；下一轮要换工作量和架构变量，而不是仅换模型名、重复调缓存API。**
