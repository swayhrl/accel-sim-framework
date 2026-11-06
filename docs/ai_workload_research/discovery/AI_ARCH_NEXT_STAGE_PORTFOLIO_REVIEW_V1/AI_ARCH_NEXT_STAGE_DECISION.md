# AI-ARCH｜下一阶段决策 V1

日期：2026-11-06。决策：**NO_GPU_PROBE_READY**；没有新硬件候选晋升。本轮完成的是一次可供ChatGPT独立审查的研究组合与最小合同，不是新的执行授权。

## 实际排序

| 档位 | 科研问题与理由 | 现在可说什么 | 现在阻断什么 |
|---|---|---|---|
| PRIMARY | Q1：Rubble晚期CPU–GPU关键路径，在强线程／placement／现有overlap后是否还有具体暴露成本？已有真实训练，是三线中最强落点 | 保留OMP16下的有范围现象；A44/A45H/A46已把线程并集和软件混杂说清 | 完整late-state authority缺失；旧sampled RSS约24.53GiB，不能套Qwen16GiB；还无同语义强软件对照 |
| SECONDARY | Q2：动态Hybrid state与KV容量转折／迁移，对完整请求有何实际代价？ | 源码已有allocator、checkpoint、Replay和hierarchical IO；需检验兼容组合后的残余 | 缺合法完整权重、真实model-facing会话、状态端点／质量、SM89运行与容量资格；HybridKV不是GDN |
| CONDITIONAL | Q3：自然路由经过Mono／tuned grouped／适用placement后，还剩何种专家供给成本？ | 有清晰Hopper条件式问题，可设计同route完整算子诊断 | H200未取得或授权；109不支持该SM90a接口；旧BF16 prefill loop／随机router不能替代 |
| PARKED | Qwen基点、A81 W4、VLM、DiT、GNN储备、iso-PPA／RL源假说 | 保留已测事实、软件反证及未测范围 | 不凭已有模型、Git ref或旧工程投资自动复开 |

PRIMARY不是GPU_READY，也不是硬件提案。Q1若缺完整state，不安排“先再训15k步看看”或重复A44/A45H CPU小Goal。条件变化后，可以用同一新合同连续完成资格、canary、最小native与诊断、独立分析和归档；不要再拆成若干准备轮次。

## 为什么没有立即GPU点

1. 数据／状态缺口是实质的。原A26GR1完整收口时有pending gradient；splat-only文件不能恢复deferred optimizer、counter、RNG与loader。稳定N也不是完整state或稳定ID。
2. 物理资源变量尚未独立。线程数、布局、缓存策略首先改变软件与并发；不是单独调CPU DRAM／PCIe／GPU SM的旋钮。没有合法独立资源轴时，最多MODEL_CONSISTENT／PARTIALLY_ATTRIBUTED。
3. 创新碰撞很直接。CLM已处理camera reuse、选择性appearance搬运和optimizer重叠；TideGS已处理跨SSD/CPU/GPU的working set与异步，但语义不同。Strata已有GPU-assisted IO和cache-aware scheduling；MonoMoE已有weight-major fusion；Patterns已有自然路由预测与placement。不能重命名这些工作。
4. 模型与设备资格不能借用。Qwen2.5 token bank不能自动成为Qwen3.5自然会话；source config不是完整模型；H200论文不是4080实测；ACL HybridKV的多模态压缩不是Hybrid GDN exact-state管理。
5. 不需要先有正残余才能设计发现探针，但必须已有真实输入、可运行强基线和可否定的变量。当前三条都还缺其中必要部分，不能用合成热点补齐。

## 下一次若条件满足，做什么、为什么、怎么做

优先考虑NEXT_THREE_SCIENTIFIC_QUESTIONS中的Q1一份合同：合法完整post-refine state、固定自然camera序列、线程与placement对照、observer OFF完整完成窗口，加一个同输入GPU-service诊断。目的先排除软件producer策略，再讨论CPU／传输／GPU物理限制。独立相机窗口只验证输入泛化，不冒充第二scene。只有必要时、经单独权利与资源审查才增加第二真实scene。

Q2其次：先锁一个实际兼容的强hybrid runtime，再以自然分支／恢复／迁移轨迹测unique physical storage、checkpoint flush和完整请求。不得把互斥的UnifiedMambaPool与Replay等功能拼在一起。Q3只有同格式真实自然路由与H200资源都闭合，才考虑小型完整算子＋应用分母的发现测量；不是现在租卡。

## 提议资源，不是本轮授权

| 问题 | 未来提议边界／资格 | 关键说明 |
|---|---|---|
| Q1 | 独立109窗口；own NVML≤14GiB、host RSS/cgroup≤48GiB、GPU累计≤1800s；新增盘为获准完整state本体S加≤2GiB工具/日志 | 48GiB源于旧合同／26.34GB观测，仍需当前owner确认；允许cpuset、P/E核与NUMA须先核；不宣称64请求等于64物理核 |
| Q2 | 若SM89实际支持且完整模型能留足headroom：NVML≤15400MiB、host≤32GiB、GPU≤1800s、私有cache/trace≤4GiB | 已合法存在的完整权重另做准入；无权重不在后台下载；所有page／ring／mirror／graph副本计入 |
| Q3 | 单独获准H200/SM90a；提议NVML≤120GiB、host≤96GiB、GPU≤1800s、cache/trace≤4GiB | 不是当前109合同，不构成租用／迁移授权；全模型容量与ABI先验证，一层能放下不算整请求合格 |

数值、质量、设备和资源上限必须在新执行合同中冻结；上述仅是可审查的资源草案。当前Goal所有GPU/锁/CUDA/模型执行为0。没有设置任意完整仿真次数上限，因为本轮不执行、也不准入任何模拟器；未来如需，先有被校准的目标模型与资源/时间合同。

## 收口

建议ChatGPT先独立审查本包的证据与三个合同。若full late-state／合法自然trace／合格设备均没有变化，就保留NO_GPU_PROBE_READY，不再为同样缺口连续派CPU准备Goal。Qwen作为成熟分析基点归档；其它AI负载的资源取得应基于更具体残余与独立验证价值，而非再追一次公开加速比。
