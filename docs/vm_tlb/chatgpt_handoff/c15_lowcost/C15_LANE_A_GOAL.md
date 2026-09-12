# Lane A Goal — 静态指纹与只读协调

Goal：`C15_A_STATIC_FINGERPRINT_AND_INTEGRATION`。
分支：`hrl/vm-c15-static-v0`。完整遵守共同authority/data/resource/test合同。连续执行，不每阶段等待用户。

## A的交付目标

让大模型先进入元数据与存储特征库，而非完整模拟库。首轮目标8–12个已确认配置；真实模型数量和配置数量分开。最后只读整合B/C结果，提取有证据的跨部署区别和未决问题。A没有GPU运行、trace捕获或simulator授权。

## C15-0.1 / C15-0.2：隔离、资产与bootstrap

输入：本包固定commit、已有clone/manifests、已授权模型缓存目录。
动作：检查自己worktree/HEAD/dirty/owner；读取已有模型和trace轻量索引，优先Llama3.2-1B、用户已有DeepSeek/GLM资产，但具体型号由证据解析。记录框架/版本/phase/dtype/revision/文件可访问性，未知为NA。
验证：T00/T01/T23。至少能解析C12锚点及明确列出其他资产是否可用；禁止从系列名推MoE/MLA。发现GPU不存在只记能力缺口，不影响A。
产物：`ASSET_INVENTORY.tsv`、`EVIDENCE_LINEAGE.md`、`BOOTSTRAP_REGISTRY.tsv`。完成后立刻commit/push，让B/C可提前消费，不等静态库全部完成。

## C15-1.1：候选覆盖计划

冻结`MODEL_SELECTION_PLAN.tsv`。候选角色：已有锚点、较大同类Dense、Attention/KV表示差异、MoE、与Dense成对量化、超大静态-only型号。维度正交，不能把同一变化算成多个互斥“类”。
优先本地真实元数据；必要时只取公开配置和Safetensors header。resolve revision为不可变提交或可核验版本。每候选写加入理由、来源、可访问状态、T0/T1 readiness和预计成本；先不按运行结果挑模型。
验证：T01/T14。目标8–12配置，不强凑虚假型号；少于8时列出逐项缺口和已尝试来源，仍完成工具和可行部分。无许可模型不得自动接受条款。

## C15-1.2：有界元数据读取器

实现仅标准库可运行的config/index/header读取器及缓存。先单元测试HTTP Range失败、超限和revision变化，再联网。读取index列出的shard header；大文件服务若忽略Range必须在读取整个body之前中止。缓存按model revision、URL和ETag/hash绑定。
验证：T02/T03/T21/T24；truncated header、错误offset、数据越界、重复tensor、malformed length均fail-fast。fixture和真实来源目录隔离。
产物：`METADATA_FETCH_RECEIPTS.tsv`、`HEADER_VALIDATION.tsv`及可复现reader。

## C15-1.3：Weight实际存储与共享关系

生成tensor catalog并按对象/层/专家统计。分别列payload、scale、zero、packing/padding，runtime repack为未知直到B测到。校验header data offsets差值与存储dtype/shape在已知格式下匹配；未知packing不强推逻辑参数量。
共享tensor只在实际storage证明下去重；config声明tie但header两份storage时同时记录语义共享声明和物理存储事实，不静默改其中一项。Embedding/lm_head保留语义用途。
验证：T03/T04。至少BF16/FP16、packed INT4+metadata、tied与untied fixture手算精确；真实header的总bytes可回到同源offset区间并集。
产物：`TENSOR_STORAGE_CATALOG.tsv`、`WEIGHT_STORAGE_BREAKDOWN.tsv`、`TENSOR_ALIAS_AUDIT.md`。

## C15-1.4：KV表示适配器

普通K/V适配器按layer/request累计resident tokens×rank-local K/V头/维度/dtype，明确payload不含reserved blocks。检查B线性、token线性、GQA/MQA头数、TP复制/分片、sliding-window封顶、混合layer、KV量化元数据。
MLA/未知压缩表示仅在实际config+代码/元数据足以证明存储对象时实现；否则`UNSUPPORTED_REPRESENTATION`，不是套普通公式。不能用series名称默认适配器。
验证：T05/T01；公式fixture手算及至少2个不同表示的真实元数据核验（不支持者合法报告unresolved）。
产物：`KV_REPRESENTATION_AUDIT.tsv`、`KV_CAPACITY_CURVES.tsv`、公式版本。

## C15-1.5：页粒度情景和指纹库

按4KiB/64KiB/2MiB生成已知布局/对齐假设下页数；明确不是实际GPU页配置或TLB miss。范围并集正确处理unaligned、跨页、零长度、别名、多个allocation。静态total-active-expert-allocated分开。
生成短/中/长context和B=1/一个受支持较大batch的解析曲线；无需GPU、权重下载或token生成。
验证：T06/T01/T20；catalog/registry/curve主键一致，未知没有变0，bytes可追溯，分析可确定性再生。产物`MODEL_REGISTRY.tsv`、`DEPLOYMENT_MANIFEST.json`、`STATIC_FOOTPRINT.tsv`。

## C15-1.6：发布A并继续协调

所有结果通过schema、hash、fixture、真实来源检查后发布manifest。报告模型数/部署配置数/静态-only数，不报告未经运行的miss率或机制收益。保存元数据下载与总CPU成本。发布后继续5.1–5.4，不等用户。

## C15-5.1：跨lane只读集成

在阶段边界或约15分钟fetch一次B/C，不busy-loop。只取固定commit中publish manifest列出的文件，验证SHA和schema。不要merge所有B/C代码或读其live partial。
B/C未发布时继续A适配器和缺口分析；无其他可做工作时先发interim。最终把consumed commits写入`integration/CONSUMED_INPUTS.tsv`。
验证：T22/T01；同model多个scenario不重复计模型；来源不等价的native/historical/trace-header目录不可混成同样证据；atomic publish和错误hash会被拒绝。

## C15-5.2：跨模型结论与升级表

静态层可比较8–12配置的容量/形状，但不得上升为动态共性。只有B有至少两个可比真实部署、C通过相应特征校验时，才作该维度的动态对比。若模型、dtype、实现同时变，标多因素比较，不声称某一变量因果。
输出每条“共同模式/例外/未知”的来源、覆盖模型、phase/operator/object、证据等级和外推边界。相似指纹只给候选归类，至少一个审核窗口一致才标`KNOWN_CLASS_PROFILED`。
验证：T22/T18。产物`integration/CROSS_MODEL_FINDINGS.md`、`UPGRADE_DECISIONS.tsv`。

## C15-5.4：收口

汇总36个小阶段的执行和科学验收状态，分别回答：工具是否可用、低成本采样误差是否达标、当前到底覆盖了多少真实部署、哪些需要下一轮。
缺GPU/新模型只给`PARTIAL_READY_FOR_REVIEW`，不能用fixture填表。C误差不达标必须保留`SAMPLER_NOT_QUALIFIED`。正文不把C12/C13回测称为独立盲测。
完整成本不双计共享输入和parent/child任务。下一轮最多3个升级建议；每个给信息增量、上下文、成本和新授权需求。本轮不执行这些建议。
最终输出`integration/FINAL_REPORT.md`、`integration/STAGE_ACCEPTANCE_SUMMARY.tsv`、`integration/COST_LEDGER.tsv`和自己的LATEST_REPORT。只commit/push A分支，规划authority保持不动。
