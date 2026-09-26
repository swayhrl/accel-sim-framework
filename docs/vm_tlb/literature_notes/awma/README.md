# AWMA论文阅读笔记｜ChatGPT支线

维护者：ChatGPT。首轮日期：**2026-09-26**；最近更新：**Round 02，2026-09-26**。

用途：留下已查原文及创新边界，帮助构思、避免重复、为未来Related Work保留可追溯依据。**不是执行Goal，不是源码/实验权威，不自动授权任何机制。**

## 论文目录（固定ID）

| ID | 论文 | 主要问题/决策层 | 实际阅读深度 |
|---|---|---|---|
| [L001](papers/L001_ISCA2018_SIMT_Page_Walk_Scheduling.md) | Scheduling Page Table Walks，ISCA2018 | 指令级walk调度 | 一级来源正文关键章节＋部分图 |
| [L002](papers/L002_MICRO2018_Neighborhood_Translation.md) | Neighborhood-Aware Translation，MICRO2018 | 页表cache-line邻域共享 | 一级来源正文关键章节＋图表 |
| [L003](papers/L003_ASPLOS2018_MASK.md) | MASK，ASPLOS2018 | 共享翻译/数据干扰 | 一级来源正文关键章节；Round 01截图失败 |
| [L004](papers/L004_ASPLOS2018_Virtual_Caching.md) | Filtering Translation Bandwidth，ASPLOS2018 | 虚拟cache与翻译边界 | 一级来源正文关键章节；Round 01截图失败 |
| [L005](papers/L005_HPCA2023_Core_Partitioning.md) | Mitigating Core Partitioning Effects，HPCA2023 | RFbank与warp子核分配 | 一级来源正文关键章节＋图 |
| [L006](papers/L006_ISCA2024_Memento.md) | Memento，ISCA2024 | OCU缓存、编译提示与调度 | 用户全文已读；本轮整理并复查 |
| [L007](papers/L007_MICRO2025_LATPC.md) | LATPC，MICRO2025 | 多VPN miss跟踪及batch walk | 用户全文已读；本轮整理并复查 |
| [L008](papers/L008_HPCA2025_Marching_Page_Walks_PRELIMINARY.md) | Marching Page Walks，HPCA2025 | PTW批处理/并发 | 仅作者摘要；全文待得 |
| [L009](papers/L009_MICRO2024_Avatar_PRELIMINARY.md) | Avatar，MICRO2024 | 推测翻译及快速校验 | 仅作者介绍/机构摘要；全文待得 |

新增Round 02：

| ID | 论文 | 实际阅读深度 |
|---|---|---|
| [L010](papers/L010_PACT2020_Valkyrie.md) | Valkyrie，PACT2020 | 作者PDF关键章节；页面截图失败，不取柱高 |
| [L011](papers/L011_ASPLOS2020_NeuMMU_PREPRINT_REVIEW.md) | NeuMMU，ASPLOS2020 | 实际读2019 arXiv v1关键章节与图表；未核最终版差异 |

**累计9条有正文依据、2条只有摘要/作者介绍；不是11篇全文精读。** 原有笔记未因目录更新自动升级阅读深度。

- [第2轮总结](rounds/2026-09-26_ROUND_02.md)
- [带配置的实验观察账本](empirical/README.md)
- [34条workload表格行＋17条观察](empirical/ROUND02_DATA.json)

实验数据只作为有条件参考。数字记录区分原表、正文明确数值、作者均值和定性观察；不盲从论文结论，不填补未披露配置，不把不同benchmark缩写拼成同一对象。

- [能力关系与Related Work地图](RELATED_WORK_MAP.md)
- [第1轮总结与AWMA使用入口](rounds/2026-09-26_ROUND_01.md)
- [待补全文/后续队列](READING_QUEUE.md)
- [来源登记](SOURCE_REGISTER.json)
- [新增笔记模板](NOTE_TEMPLATE.md)
- [维护记录](CHANGELOG.md)

## 使用约定

每篇将作者内容、我的比较判断、未验证想法分开。作者报告的“创新/首次”只在其对照与范围内理解，不当成全球无先例的保证。原文没披露的内容不从常识或二手综述补齐；有相似关键词也不直接宣布机制等价。

每个数量必须保留指标分母、平台及样本范围。不会将page-walk latency当kernel时间、将storage比例当面积、把模型视作真实GPU已公开内部实现。

这不是全领域穷尽综述；新候选仍需按其实际操作规则定向查重。已读论文不要求全数复现，未得全文只阻塞依赖其细节的判断。

## 与执行分支隔离

独立文献分支：`hrl/awma-chatgpt-literature-notes-v1`。

仓库位置：`docs/vm_tlb/literature_notes/awma/`。

基于已核协调提交`d1b58f8a4a0beac3f9c760f5933faf7e701a1152`，不修改Lane B/E、历史baseline、原论文资格报告或任何源码。无须reset/rebase活动worktree来阅读本目录。未来在新对话中从本README与队列继续即可。
