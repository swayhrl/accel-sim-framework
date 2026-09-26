# 后续阅读队列（不是已读论文清单）

日期：2026-09-26。队列由下一条真实研究问题决定，不要求为了“全面”把所有论文完整复现。

| 条目 | 已有状态 | 何时优先 | 下一步所缺 |
|---|---|---|---|
| Marching Page Walks，HPCA2025，10.1109/HPCA61900.2025.00123 | L008仅作者摘要 | PTW排队/单walker并发成为剩余瓶颈 | 全文结构、并发协议与实验配置 |
| Avatar，MICRO2024，10.1109/MICRO61859.2024.00029 | L009仅一级摘要/作者介绍 | 候选使用地址推测、先访问后验证 | 全文校验/失败恢复与实现约束 |
| Compiler assisted coalescing，PACT2018，10.1145/3243176.3243203 | 既有调研未取得全文；用户亦暂时无法下载 | 仅当新候选区别依赖编译器翻译合并细节 | 全文；不阻塞其他方向，不反复请求用户 |
| Pichai等，ASPLOS2014 / DCS-TR-703 | 旧协调已核技术报告关键段；本轮不冒称新读完整会议版 | 经典warp去重的精确语义/作者基线 | 需要时补会议版与技术报告差异 |
| GCStack / GCStack+GCScaler，CAL2024 / ISCA2025 | 既有公开实现线索；本轮未新增全文核查 | 要把Observatory当方法贡献、需要更强周期归因 | 正文计数归属、重叠处理、验证及源码 |
| Towards Segmentation-Based Address Translation for LLM Inference | 旧项目已有阅读线索；本轮不纳入已读统计 | 权重/张量连续映射成为候选前提 | 重新按具体版本核虚实连续性、分配与生命周期 |

## 本轮查找边界

检索了GPU page-walk scheduling、neighborhood、virtual caching、MASK、Marching Page Walks、Avatar、core partitioning/RBA等作者/机构原始来源；使用用户提供LATPC与Memento全文。未进行全数据库系统综述，不宣称覆盖所有2026工作或已经排除全部先例。

失败入口与阅读深度保留在SOURCE_REGISTER.json。找不到全文不等于论文未包含某项机制；同样，只有相似标题也不等于机制完全相同。

## 下轮维护规则

固定paper ID；升级阅读深度时记录日期与新增定位。修正原记录时在CHANGELOG中说明；不把旧假设静默改写成作者结论。需要新实验的想法只放在问题卡/待办，不以文献笔记授权Codex执行。


## Round 02追加：用户可协助的全文优先项

1. **Marching Page Walks: Batching and Concurrent Page Table Walks for Enhancing GPU Throughput**，HPCA2025，DOI `10.1109/HPCA61900.2025.00123`。作者页面可读，出版PDF入口仍未获得正文。用于核不同页的batch条件、单walker并发资源及各workload实验，不以摘要的平均数代填数据。
2. **A Case for Speculative Address Translation with Rapid Validation for GPUs（Avatar）**，MICRO2024，DOI `10.1109/MICRO61859.2024.00029`。作者介绍/机构摘要可读，出版入口无法获得正文。需要核推测校验、失败回退、压缩限制及逐workload条件。

NeuMMU预印本已有可读正文，本轮L011已登记，会议版差异尚未核但暂不要求用户优先补。Valkyrie已有正文；CAC继续非阻塞。此次请求不是要求暂停Codex等待。
