# C16文献阅读笔记｜ChatGPT独立支线

维护者：ChatGPT。更新时间：2026-09-27。分支：`hrl/c16-chatgpt-literature-notes-v1`。

本支线只存文献核读、相关工作比较与研究假设，不修改实验、Core、配置或原始数据。文献建议不是执行授权。与AWMA文献笔记分开，避免跨项目混淆。

## 当前入口

[LR02：从容量公平到跨轮复用存活](rounds/2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md)

本轮最重要的区分：**对象识别、容量分配、具体cache line的跨轮存活、完整窗口的周期效用并不是同一个问题。** 不能仅凭class份额均衡或protected_hits增加宣称跨token驻留成功。

LR02接续此前聊天中的C16调研，不声称仓库里存在同结构的LR01文件。此前聊天中的“fairness可能是新机制”判断在本轮收紧为待验证假设。

## 本轮来源登记

| ID | 工作/来源 | 本轮阅读深度 |
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

共9项研究条目、2份官方文档、1份实现说明；其中4项核读正文关键章节。不同版本、摘要和延伸工作不能累加成更多已全文精读的论文。各条目原文URL、定位、作者贡献、对C16的启发及不可声称的结论见LR02正文。

后续队列：PIPP、RRIP、GPU APCM、MLP/关键路径感知缓存管理，以及本轮仅有摘要条目的原始全文。队列不算完成阅读。

## 配套数学反例

[每类等份但类内仍循环抖动](examples/toy_scan_counterexample.py)

```bash
python3 docs/vm_tlb/literature_notes/c16/examples/toy_scan_counterexample.py
```

这是本轮自行构造的CPU小例子：两个类、每类8行、每类2行容量。全量admit的类内LRU与固定地址子集有相同边界占用量，但预热后分别0/16和4/16命中。它不是C16 trace、CUDA硬件、Talus复现或性能模拟，不包含真实系统代价。

## 项目证据锚点

- Lane 1：`4214398782159022907081dbcc36854cf21fb4b5`。
- Lane 3：`a402828860ced26124ddbf3c9d87baa6f6774d55`，也是本分支创建基点。
- 本轮不消费Lane 4未闭合性能结果，不改变Lane 1B/Lane 4任务。

原论文PDF不提交仓库；读不到的正文保持未核实。作者陈述、项目事实和我们的推断分别标注。对“首次”“优于已有工作”“系统加速”的判断必须等待确切比较，不能靠名称或仅与LRU的单点差异成立。
