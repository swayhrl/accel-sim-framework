# 来源索引与阅读等级

**后续补证：** P03 已取得并阅读本机 12 页 PDF，v0.23 私有母稿也已核验和阅读。以下表格保留首轮阅读等级，新增来源身份、页码与边界见 [补充报告](REPORT.md)。

阅读日期：2026-11-10。`P` 为外部论文，`R` 为项目既有材料。`元数据+摘要` 表示 Crossref 出版身份与 OpenAlex 摘要核对，并非全文审读；`PDF 重点段落` 表示下载原 PDF、核首页标题并读取与本任务有关的段落。检索原始记录在同目录 `openalex_search.json`、`openalex_targeted.json`、`verified_metadata.json`，脚本用于可重复检索，不是科学模拟。任何 DOI 记录自身也可能有版本或索引错误，以下以实际 PDF 标题/出版商记录交叉判断。

## 外部论文

| 编号 | 论文与稳定入口 | 阅读等级 | 在本报告中的用途与限制 |
|---|---|---|---|
| P01 | González 等, *Eliminating Cache Conflict Misses Through XOR-Based Placement Functions*, ICS 1997, [DOI](https://doi.org/10.1145/263580.263599), [作者 PDF](https://people.ac.upc.edu/jmanel/papers/ics97.pdf) | 远端既有笔记核作者原文；本轮核 Crossref | XOR placement 先例；没有重新逐页读 PDF。 |
| P02 | Seznec, *A Case for Two-Way Skewed-Associative Caches*, ISCA 1993, [DOI](https://doi.org/10.1145/165123.165152) | 远端既有笔记 + Crossref | skewed cache 先例；AE 单 set hash 不是该结构。 |
| P03 | Li 等, *Tag-Split Cache for Efficient GPGPU Cache Utilization*, ICS 2016, [DOI](https://doi.org/10.1145/2925426.2926253) | Crossref + OpenAlex 摘要 | GPU 细粒度 data/tag 直接近邻；性能数字仅该文摘要。 |
| P04 | Li 等, *An Efficient GPU Cache Architecture for Applications with Irregular Memory Access Patterns* (Elastic-Cache), TACO 2019, [DOI](https://doi.org/10.1145/3322127) | Crossref + OpenAlex 摘要 | 非连续 32/64B 数据打包和 shared memory 辅助 tag；摘要中的 GM 不能移植。 |
| P05 | Lal 等, *A Quantitative Study of Locality in GPU Caches for Memory-Divergent Workloads*, IJPP 2022, [DOI](https://doi.org/10.1007/s10766-022-00729-2) | Crossref + OpenAlex 摘要；Springer PDF URL 返回 HTML，全文未获 | sector 过取、lost spatial locality 的双向权衡。 |
| P06 | Xu 等, *ATA-Cache: Contention Mitigation for GPU Shared L1 Cache With Aggregated Tag Array*, TCAD 2024, [DOI](https://doi.org/10.1109/TCAD.2023.3337192), [2023 预印本 PDF](https://arxiv.org/pdf/2302.10638) | Crossref + 预印本 PDF 重点段落；PDF SHA256 `54b1e334056b146fc34b40d0c69eb444f6af4d3c27c055482874ad4b95105d42` | 跨 SM Tag 聚合，非单 SM DTC。预印本摘要 12%，OpenAlex 期刊摘要 14.5%，版本数值不混引。 |
| P07 | C. Li 等, *Locality-Driven Dynamic GPU Cache Bypassing*, ICS 2015, [DOI](https://doi.org/10.1145/2751205.2751237) | Crossref + OpenAlex 摘要 | 低重用旁路先例。 |
| P08 | A. Li 等, *Adaptive and Transparent Cache Bypassing for GPUs*, SC 2015, [DOI](https://doi.org/10.1145/2807591.2807606) | Crossref + OpenAlex 摘要 | footprint 适应旁路；摘要陈述七平台/16 应用。 |
| P09 | Koo 等, *Access Pattern-Aware Cache Management for Improving Data Utilization in GPU*, ISCA 2017, [DOI](https://doi.org/10.1145/3079856.3080239) | Crossref + OpenAlex 摘要 | 静态 load 的四类局部性、bypass/pin。 |
| P10 | Oh 等, *APRES: Improving Cache Efficiency by Exploiting Load Characteristics on GPUs*, ISCA 2016, [DOI](https://doi.org/10.1109/ISCA.2016.26) | Crossref + OpenAlex 摘要 | load 特征、warp 调度与预取/合并共同作用。 |
| P11 | Zhang 等, *CIAO: Cache Interference-Aware Throughput-Oriented Architecture and Scheduling for GPUs*, IPDPS 2018, [DOI](https://doi.org/10.1109/IPDPS.2018.00025), [预印本 PDF](https://arxiv.org/pdf/1805.07718) | Crossref + PDF 重点段落；SHA256 `6eaca86dff66c8ce8fd432261c1fcfbcc74024595d7ba8700e6e5e976d30baee` | 干扰隔离、shared memory、限流与 TLP 权衡。 |
| P12 | Jog 等, *Exploiting Core Criticality for Enhanced GPU Performance* (CLAMS), SIGMETRICS 2016, [DOI](https://doi.org/10.1145/2896377.2901468) | Crossref + OpenAlex 摘要 | latency tolerance 与调度优先级；不同于 DTC 退休。 |
| P13 | Jog 等, *Application-aware Memory System for Fair and Efficient Execution of Concurrent GPGPU Applications*, GPGPU 2014, [DOI](https://doi.org/10.1145/2588768.2576780) | Crossref + OpenAlex 摘要 | 多应用 FR-RR-FCFS 公平性；不直接推单应用结论。 |
| P14 | Khairy 等, *Accel-Sim: An Extensible Simulation Framework for Validated GPU Modeling*, ISCA 2020, [DOI](https://doi.org/10.1109/ISCA45697.2020.00047) | Crossref + OpenAlex 摘要；**未取得同标题全文** | native trace、逐计数器验证方法。OpenAlex 误关联的 PDF 已按 P15 纠正。 |
| P15 | Khairy 等, *Exploring Modern GPU Memory System Design Challenges through Accurate Modeling*, 2018 [arXiv](https://arxiv.org/abs/1810.07269), [PDF](https://arxiv.org/pdf/1810.07269) | 实际 PDF 重点段落；SHA256 `e5ee7b7c6982b51bd1e893bae6a78c4f47eb5377d731ce173b1842fa33c43cf7` | Volta 内存系统、sector/tag 统计和模型改变决策；**不是** P14 正文。 |
| P16 | Huerta、Abaie Shoushtary、González, *Analyzing and Improving Hardware Modeling of Accel-Sim*, [arXiv:2401.10082](https://arxiv.org/abs/2401.10082), [PDF](https://arxiv.org/pdf/2401.10082) | PDF 重点段落；SHA256 `230c6c4c4aa631cbf01470c8cee33b42f6e23905f4dd1925aae5b6c9458ecabc` | 前端/result bus/memory pipeline 模型敏感性。PDF 自标 CAMS 2023；其内印 DOI `10.1145/3589236.3589244` 在 Crossref 指向不同标题，故不引用该 DOI。 |
| P17 | Vasilakis 等, *Decoupled Fused Cache*, TACO 2018, [DOI](https://doi.org/10.1145/3293447) | Crossref + OpenAlex 摘要 | DRAM cache 与 LLC tag 融合，广义 tag/data 设计先例；非 GPU L1 同机制。 |
| P18 | Liu 等, *A Partial Tag–Data Decoupled Architecture for Last-Level Cache Optimization*, IEEE CAL 2025, [DOI](https://doi.org/10.1109/LCA.2025.3623137) | Crossref + OpenAlex 摘要 | CPU LLC 复用确认后分配 data 的先例；非直接 GPU L1 对照。 |

## 项目内远端来源

以下 `R01–R08` 在 174-new 历史 DTC 文档工作树 `/root/data/dtc_main_v100_sweep_20261025_v1/docs-worktree/` 只读读取，读取时 HEAD `b7a654356b75caeb45fbec392eb488151c600a9e`。这是历史文档身份，不是当前科学状态优先级。相对路径均从该树起算；每项 SHA256 为远端原字节。

| 编号 | 相对路径 / 其他固定身份 | SHA256 / 用途 |
|---|---|---|
| R01 | `docs/dtc_l1/README.md` | `2dae2b65f00ff9f76638ad021ec665f34ca5c47aead26546adc059edcb8bdf58`；项目起源和旧 M5 目标。 |
| R02 | `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md` | `e014528c9edae22f96e2a1e917531eec7c0edd218712fd59b6eeda5b4c71cca5`；2026-09-25 下游队列与理想服务讨论。 |
| R03 | `docs/dtc_l1/review_packs/DTC_LANE_AG_OPT_SCREEN_V1/inputs/AE/RELATED_WORK_BOUNDARY.md` | `1674057f7a5f5c6a69b7b03e6b56b8e49439c2d8a6a2007b931adcd70d7c186e`；XOR/skewed 边界。 |
| R04 | `docs/dtc_l1/review_packs/DTC_LANE_AG3_AE_AD_SCREEN_V1/inputs/ae/RELATED_WORK_BOUNDARY.md` | 同 R03 SHA，远端两个副本内容相同。 |
| R05 | `docs/dtc_l1/review_packs/DTC_LANE_AG3_AE_AD_SCREEN_V1/PAPER_MINIMAL_CHANGE_PROPOSAL.md` | `be134fcc7f15d9678e08d3a5ed2f8b28ed27d11230f64aca736150feaf258577`；历史编辑边界，不改 v0.23。 |
| R06 | `docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL/PAPER_RESULTS_ANALYSIS.md` | `34fceafa04e620118f3da15b9178f10a74f9107a412b4889376c0e81b1aef347`；旧 FAST12 与负例。 |
| R07 | `docs/dtc_l1/iscas2027/service_closure_174_v1/FINITE_SERVICE_CONTRACT_V1.md` | `c489e6cc4ddfd85672a1c9af7d92856279bbdf676fcbd1667cdf33a3145df3bb`；有界端口、backpressure、完成语义。 |
| R08 | `docs/dtc_l1/iscas2027/service_closure_174_v1/RESOURCE_AND_RESIDENCE_METHOD_V1.md` | `d07ebe28b9944473a098c5728f4c1b0b84e737788c884d109d97c1c2fc09771b`；资源向量、计数器分母及旧格式 HOLD。 |
| R09 | [CORE32 Main 固定报告](https://github.com/swayhrl/accel-sim-framework/blob/b9ff89f00ea8ff889e4189136501c714c5d7e345/docs/dtc_l1/review_packs/CORE32_ORACLE_FINAL_SCIENTIFIC_REVIEW_20261109_V1/REPORT.zh.md) | 174-new 原字节 SHA256 `93f19ef93c8ad72026bb2ec3b104d8f9229c647dd0be4bc6f02965d03c5949c8`；接受范围和正零负。 |
| R10 | [CORE32 后续结构草案](https://github.com/swayhrl/accel-sim-framework/blob/b9ff89f00ea8ff889e4189136501c714c5d7e345/docs/dtc_l1/review_packs/CORE32_ORACLE_FINAL_SCIENTIFIC_REVIEW_20261109_V1/NEXT_STRUCTURE_DRAFT.md) | 174-new 原字节 SHA256 `62b10445cd654216d74c105ca89883691d92d2bcdc4e5ff18e315bd0b06b6133`；E1/E2/E3 和历史 F/Tag HOLD。 |
| R11 | 174-new `/root/data/dtc_finite_service_completion_v1_20261109/core/docs/dtc_l1/DTC_L1_SPEC.md` | `9492dba2adc86a04e1d8498da1fb7ae9fde931ac9701e4729a7dbfdf8b157d0a`；M0 冻结结构规格，384 行。 |
| R12 | 本机 DTC-L1 CONTEXT.md | 当前优先状态：Short-Collect Native R0 HOLD、17/17 CPU、0 新科学格、原稿 v0.23 冻结。 |

## 检索边界与错配记录

- 174-new 历史 DTC 文档树中，针对 `doi.org`、`arxiv.org`、`related work`、`prior work` 的 Markdown 搜索，仅上述两份直接相关工作边界文档命中。框架 `CITATION.bib` 是通用软件引用，不是 v0.23 稿件书目。
- 109 的 DTC native coverage 工作树中，按相关工作/论文/文献命名找到的是 `DISCUSSION_REFERENCE.md` 和 FAST64 文档副本；其他项目的文献笔记未纳入。没有把 164 `dtc_paper_suite` 文件名误当文献综述。
- v0.23 可编辑原包路径未获可靠交接确认，本轮不声称读了其 Related Work 章节，也没有改它。
- OpenAlex 为 P14 所列 `arxiv:1810.07269` 实际是 P15，已核 PDF 首页。P16 PDF 自印 DOI 与 Crossref 返回标题不一致，按 arXiv/PDF 身份保守引用。P06 的预印本与期刊摘要平均数不同。以上三处均禁止把不同版本的数字混写。
