# C16 Lane H — Runtime Object Mapping and Memory Fingerprints

Goal: `C16_H_MEMORY_FINGERPRINT`。

Branch target: `hrl/vm-c16-h-memory-fingerprint-v0`。

Lane H 主要在本地CPU服务器工作，负责把G产生的真实runtime/capture证据转成可审的对象、页、Cache-line和局部复用指纹。它不是GPU执行窗口，也不启动新full-ROI模拟。

## 负责阶段

C16-0.5、0.8；C16-4.4~4.6；C16-5.1~5.3、5.5。协作 C16-4.2、6.3。

## H0 — Runtime Object Map V2

提前实现observer/schema，不等GPU到位。

最小对象：
- WEIGHT
- QUANT_METADATA
- KV_CACHE
- UNKNOWN_RUNTIME

只有直接runtime证据充分时才增加ACTIVATION/WORKSPACE。

对象事件需要：storage ID、generation、view range、allocation/grow/replace/release evidence、stream/context、timestamp/ordering evidence。相同指针复用必须通过generation区分。

fixtures至少覆盖：
- 同地址不同generation；
- storage多view；
- tied/shared weight；
- KV grow/replace；
- unknown release；
- cross-stream ambiguous order；
- quant payload + scales/zeros；
- architecture MLA but runtime expanded K/V 的表示差异。

没有release证据就保持UNKNOWN_ACTIVE/AMBIGUOUS，不根据Python析构猜GPU释放。

## H1 — Address parser与访问语义

在本地实现/复用NVBit trace parser，必须正确处理：
- active mask；
- memory width；
- per-lane addresses；
- cross-line访问；
- load/store/atomic分类；
- kernel/run identity；
- incomplete/partial trace。

fixture必须包含：unaligned 128B line crossing、4K/64K page crossing、inactive lanes、重复地址、同storage alias、partial terminal。

## H2 — memory-only observer/proxy

评估是否能在现有tracer上增加默认关闭的memory-only模式，只保留characterization需要的memory event字段。

GO条件：
- tiny fixture与full tracer提取出的memory events bit/exact等价；
- target过滤与terminal语义保持；
- 不改变被测程序；
- 输出明显降低。

NO_GO条件：
- 需要侵入性改变时序/程序；
- 无法证明地址/active mask/width等价；
- API/版本风险超过本轮价值。

NO_GO时保留full tracer fallback，不阻塞C16。

## H3 — C16-4.5 Memory Fingerprints

对每个qualified captured window至少输出：

### Page scale
- unique 4KiB/64KiB bucket count；
- per-object page footprint；
- page occupancy / bytes touched proxy；
- contiguous virtual-range length distribution；
- adjacent-window page-set overlap；
- page revisit metrics only when local order is actually preserved。

这些是observed GPU VA structural metrics，不能称hardware TLB miss/page size事实。

### Cache-line scale
- unique 128B lines；
- sector utilization if definition is explicit；
- read/write/atomic event counts；
- bytes requested/touched with exact semantics；
- per-object line footprint；
- adjacent-window set overlap；
- local chronological reuse where order model is valid。

### Object
WEIGHT / QUANT_METADATA / KV_CACHE / UNKNOWN分别统计。无法归属的访问保留UNKNOWN，不按比例分给其它对象。

## H4 — C16-4.6 Order model

`.traceg`按CTA分组时，文件顺序不是全GPU共享L2真实到达顺序。

每个reuse/MRC类指标必须标：
- `SET_ONLY`
- `LOCAL_STREAM_ORDER`
- `SYNTHETIC_INTERLEAVING_PROXY`
- 或其它明确模型。

禁止把synthetic/file order称真实global-L2 order。若要做合成交错敏感性，至少使用两种预先规定的interleaving并标proxy。

## H5 — C16-5.1 Unified Fingerprint

建立 `deployment × scenario × phase` 行，合并但不混淆证据域：

Static：Dense/MoE、layers、weight storage、KV representation、quantization。
Native：operator time mass、implementation、heavy-tail fraction。
TLB-oriented structural：pages/window、Weight/KV page footprint、range continuity、context scaling。
Cache-oriented：lines/window、sector/read-write、reuse/overlap、NCU L1/L2/DRAM counters。

所有字段带unit、evidence tier、source receipt、missing reason。

## H6 — C16-5.2 Within-deployment

优先分析同一deployment：
- Prefill vs Decode；
- T256/T2048/T8192；
- B1 vs B4。

先检查implementation是否发生切换。如果context变大同时FlashAttention/kernel实现改变，结论写成“deployment behavior changed with context including implementation switch”，不归因于单纯working set。

## H7 — C16-5.3 Pairwise

分析：
- Qwen0.5 vs Qwen7 family scale；
- Qwen7 raw vs AWQ；
- Qwen3 Dense vs MoE。

raw/AWQ需审计runtime backend、activation/KV dtype、input/scenario一致性。未控制项必须列confound；不得把所有差异归因quantization。

## H8 — C16-5.5 TLB/Cache Problem Map

只提出“问题/现象/机会”，不直接宣布机制有效。

TLB问题候选示例：
- Weight virtual contiguous-range结构是否跨模型稳定；
- Decode KV page footprint随context增长的共性；
- MoE active Weight working set是否改变翻译压力；
- quantization是否系统降低Weight page footprint；
- translation latency exposure是否可能集中在少数operator。

Cache问题候选示例：
- Weight streaming/reuse模式是否跨模型稳定；
- KV reuse何时随context超过cache容量；
- quant metadata是否引入额外line traffic/pollution；
- MoE expert Weight是否存在token间reuse。

每项必须列supporting deployments、counterexample、evidence tier、未验证因果。

## H禁止事项

- 不运行AutoDL正式任务；需要GPU canary时由G执行。
- 不把checkpoint file offsets当GPU addresses。
- 不把observed VA bucket当hardware TLB miss。
- 不把CTA file order当global L2 order。
- 不把UNKNOWN补成Activation。
- 不创建新的Accel-Sim full replay。

终态：`C16_H_MEMORY_FINGERPRINT_READY_FOR_REVIEW` 或明确列出缺capture导致的partial状态。