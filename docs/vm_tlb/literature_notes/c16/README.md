# C16文献阅读笔记｜ChatGPT独立支线

维护者：ChatGPT。更新时间：2026-09-27。分支：`hrl/c16-chatgpt-literature-notes-v1`。

本支线只存文献核读、相关工作比较与研究假设，不修改实验、Core、配置或原始数据。文献建议不是执行授权。与AWMA文献笔记分开，避免跨项目混淆。

## 当前入口：LR03

[LR03：近邻能力、论文故事与最小强基线](rounds/2026-09-27_LR03_NEIGHBORS_STORY_STRONG_BASELINES.md)

状态：`RESEARCH_DESIGN_ONLY_NO_EXECUTION_AUTHORITY`。当前不启动新simulation，不修改Lane 4，不授权M1F full timing，不修改冻结的Lane 3 V1。

本轮新增重点：

- 把P_all/P_stable与M1/M1F组织成“保护资格×硬quota”的能力对照；P_stable是简单稳定子集加priority，不是假装独立的M1F副本，也不是完整Talus复现。
- 最终至少覆盖通用抗扫描与软件辅助语义学习两类强能力；DRRIP为前者候选但原文实现合同待补，后者参考AutoScratch附录SHiP-SW并明确C16适配。
- 复核AutoScratch附录的固定L2序列功能模型/DRAM流量边界；不把其比较当成完整timing结果。
- CUDA文档不保证本项目所需的跨token地址稳定性，也不证明实际硬件每次独立重抽；自定义event-fractional对照不能叫NVIDIA真实实现。
- 论文主线以“局部驻留价值→旧地址有效存活→净周期收益”为中心，cost-aware是目标而非已有功能，新颖性与M1F性能均未预设。

阅读增量：复核Talus、AutoScratch、Vantage正文相关章节；Cache-Resident LLM从摘要补到正文机制与实验分层；新增APCM正文§4–5；复核CUDA/PTX官方接口。未运行论文代码。DIP、RRIP、原始SHiP、MICRO 2025 eviction hints完整原文实现合同仍待闭合。不要把复读、摘要升级或官方文档计为多篇新论文。

## 历史入口：LR02

[LR02：从容量公平到跨轮复用存活](rounds/2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md)

LR02最重要的区分：**对象识别、容量分配、具体cache line的跨轮存活、完整窗口的周期效用并不是同一个问题。** 不能仅凭class份额均衡或protected_hits增加宣称跨token驻留成功。

LR02接续此前聊天中的C16调研，不声称仓库里存在同结构的LR01文件。此前聊天中的“fairness可能是新机制”判断在该轮收紧为待验证假设。

## LR02来源登记（保留当轮阅读深度，后续升级见LR03）

| ID | 工作/来源 | LR02阅读深度 |
|---|---|---|
| P01 | UCP，MICRO 2006 | 原始摘要转载 + SIGMICRO官方说明 |
| P02 | Adaptive Insertion Policies，ISCA 2007 / IEEE Micro 2008延伸 | 原始摘要与作者机构摘要；合计一个研究条目 |
| P03 | Vantage，ISCA 2011 | 作者全文关键章节 |
| P04 | Talus，HPCA 2015 | 作者全文关键章节 |
| P05 | SHiP，MICRO 2011 | 作者机构原始摘要；PDF获取超时 |
| P06 | AutoScratch，MLSys 2023 | 会议正文及附录关键章节，特别是SHiP-SW |
| P07 | PRESERVE，arXiv 2025 v1 | 正文机制与实验设置；Ascend NPU |
| P08 | GPU Cache Eviction Priority Hints，MICRO 2025 | 作者书目与项目说明；未取得全文 |
| P09 | Cache-Resident LLM Inference in GB-Scale LLCs，arXiv 2026 v1 | 原始摘要 |
| D01 | CUDA L2 Cache Control | 官方接口文档相关章节 |
| D02 | PTX eviction hints / createpolicy | 官方ISA文档相关章节 |
| I01 | Marlin README | 作者实现说明，未复现kernel |

LR02共9项研究条目、2份官方文档、1份实现说明；其中4项核读正文关键章节。不同版本、摘要和延伸工作不能累加成更多已全文精读的论文。各条目原文URL、定位、作者贡献、对C16的启发及不可声称的结论见LR02正文。

当前后续队列：PIPP、RRIP、DIP/原始SHiP全文实现合同、MICRO 2025 eviction hints全文、MLP/关键路径感知缓存管理。APCM已在LR03补正文；队列不算完成阅读。

## 配套数学反例（LR02）

[每类等份但类内仍循环抖动](examples/toy_scan_counterexample.py)

```bash
python3 docs/vm_tlb/literature_notes/c16/examples/toy_scan_counterexample.py
```

这是LR02自行构造的CPU小例子：两个类、每类8行、每类2行容量。全量admit的类内LRU与固定地址子集有相同边界占用量，但预热后分别0/16和4/16命中。它不是C16 trace、CUDA硬件、Talus复现或性能模拟，不包含真实系统代价。

## 项目证据锚点

- Lane 1：`4214398782159022907081dbcc36854cf21fb4b5`。
- Lane 3：`a402828860ced26124ddbf3c9d87baa6f6774d55`，也是本分支创建基点。
- LR03阅读基点：`49c01401200f7944db31d066ebb331a9ba701882`。
- LR03项目事实来源：2026-09-27 M1F_READY_LANE4_RUNNING完整handoff；不将本文档视为历史实验的重新验收。
- 本支线不消费Lane 4未闭合性能结果，不改变Lane 4任务；是否运行M1F仍由预注册project-level gate决定。

原论文PDF不提交仓库；读不到的正文保持未核实。作者陈述、项目事实和我们的推断分别标注。对“首次”“优于已有工作”“系统加速”的判断必须等待确切比较，不能靠名称或仅与LRU的单点差异成立。
