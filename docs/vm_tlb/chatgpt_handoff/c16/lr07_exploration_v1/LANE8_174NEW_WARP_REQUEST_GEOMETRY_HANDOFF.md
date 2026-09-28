# Lane8 Handoff：MoE warp请求结构筛查

执行节点：**174-new**
Lane：**8，新Codex窗口**
角色：CPU-only raw consumer / architecture characterization
GPU：**禁止**；GPU锁：禁止申请；109：本轮无动作。
可并行：Lane4@174-new、Lane7@109。不得触碰Lane4进程/配置/binary/output或读取partial结果。

Goal：`C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1`
状态：`READY_TO_DISPATCH`；本文是执行合同，不是任务已经启动的声明。

## 0. 一轮做完什么

核现有输入与记录格式 → 小型synthetic tests → 一次流式消费三条accepted MoE shard bundles → 统一解释 → commit/push/回读 → STOP。

不建设新profiler，不重抓trace，不改模拟器，不做cache simulation。普通路径/解析/包装缺失如果可由accepted provenance确定性恢复，自行修复继续；真实科学字段不足则限制相应分析范围，不补造。

## 1. 科学问题

三条MoE expert down_proj的weight/input各约一半，目前指active-lane address events。问：同一动态warp访存中去掉重叠地址、统计sector覆盖以后，两类需求是否仍然相似？差别来自广播、连续合并还是离散sector覆盖？

这不是重新计算per-shard footprint，也不是Lane6的token级时间结构。观察对象是**同一条动态访存记录内的lane集合**。

高重复地址可能已由硬件广播/合并有效处理，不能直接说存在可节省的DRAM流量。三模型共享cuBLAS gemvx家族，仍不构成实现独立性。

## 2. Read first / immutable authorities

仓库：`swayhrl/accel-sim-framework`。

文献：`hrl/c16-chatgpt-literature-notes-v1@b0533583a6207a48cd4fa309e8dc4d925f20adce`

读取：
`docs/vm_tlb/literature_notes/c16/rounds/2026-09-28_LR07_WARP_GEOMETRY_WORKSPACE_AND_RESOURCE_BALANCE.md`

总账：`hrl/c16-work-history-audit-20260928-v1@1f999e62000178feb7e657a79cdf9e5a64db182f`；先查已有MO15/EXP03/EXP04及相关边界，不重新做已闭合时间统计。

三lineage accepted consumer：
`hrl/c16-three-lineage-moe-consumer-174new-v1@08536be9940590be101c7f5bac2117ba82056db5`

重点文件：
- `docs/vm_tlb/chatgpt_handoff/c16/three_lineage_moe_consumer_v1/ANALYSIS_CONTRACT_V1.md`
- `docs/vm_tlb/review_packs/C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1/`
- `util/vm_tlb/c16/three_lineage_consumer/recompute.py`
- `util/vm_tlb/c16/olmoe_nvbit1771_warp_regsource_v39/c16warp1_v39_common.h`

后者ABI仅直接证明该OLMoE实现；Q30/DeepSeek需各自核既有producer/static/manifest，不能因格式类似而跳过。

## 3. 分支与资源

从三lineage consumer准确commit `08536be9940590be101c7f5bac2117ba82056db5`新建独立worktree：

`hrl/c16-moe-warp-request-geometry-screen-174new-v1`

旧consumer、raw/catalog只读。不要merge整条其他实验分支。

资源：单CPU worker，BLAS/OpenMP线程1；流式读单shard、用完释放；不常驻全部lane地址。优先沿用已admitted raw挂载；内存目标不超过2GiB。G2若过大，可明确省略，不要增加并发。不得修改Lane4 affinity/priority、停止任何进程或扫描D1-D3 full-SASS。

## 4. Exact raw inputs

沿用accepted consumer CONFIG的三个RUN_ID，从node164 durable authority读取：

Q30：
`C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

DeepSeek：
`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

OLMoE：
`C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf`

根目录按既有accepted consumer/admission定位，不凭新文件名猜。每条bundle核manifest/positive ACK/catalog/file SHA。只访问这三条小型warp bundles及必要static/context文件，不读取模型权重。

校验参考（不得作为统计输入）：

| Lineage | selected | executed/zero | warp records | active-lane events |
|---|---:|---:|---:|---:|
| Q30 | 243 | 41/202 | 100352 | 3147776 |
| DeepSeek | 243 | 169/74 | 362496 | 11538432 |
| OLMoE | 243 | 129/114 | 132096 | 4196352 |

这些closure与新统计可在同一遍raw读取中完成；不要为相同字段重复读取三遍。

## 5. 记录/操作语义先核清

历史parser使用HEADER `<8sIIQQQ`、RECORD `<6I32Q`。记录包含static_index, active_mask, CTA xyz, warp, addr[32]。transport序号不在科学payload中。

对每个path绑定：
- exact kernel/function/static index；
- memory space与global-source operand；
- load/store/atomic/reduction分类；
- predication/active_mask含义；
- per-lane **访问宽度**及其static/source依据；
- 单record是否代表一个memory operand的动态warp访问；
- process/launch/CTA/warp身份。

不能由tensor BF16推断每lane只读2B，vector指令可能更宽；不能把opcode中的不相关数字当width。无法唯一恢复时标`WIDTH_UNRESOLVED`，该path只做G0，绝不猜值。

常规global loads和stores分开。Atomic/reduction或特殊路径只有数据读取/写入语义明确时才能单列G1；不合格的先隔离。LDGSTS只能消费已证明的global-source operand，不混入shared destination。

## 6. G0：不依赖width的地址结构

每条record按有效mask取lane：
- active_lane_count E；
- distinct_start_address_count A；
- start_address_multiplicity E/A（E=0输出null）；
- max multiplicity；
- all-active-lanes-same-start flag。

按lineage/path/role输出总数、分布。role优先沿用原始object mapping并保留原role标签。G0不称字节量。

## 7. G1：width-qualified的字节并集与sector覆盖

每条record内，对每个active lane形成半开区间 `[addr, addr+width)`。

- `L = sum(width)`：逻辑lane字节，重复也计；
- `U = size(union of intervals)`：同record去重后的字节并集；
- `S32 = count(distinct floor(byte_address/32) over covered intervals)`；
- `C32 = 32*S32`：sector覆盖字节proxy；
- `lane_byte_multiplicity = L/U`；
- `sector_fill = U/C32`；
- 可一并记录覆盖128B line数，但不将其当cache miss。

必须处理跨sector/跨line边界，不能只对lane首地址做`addr//32`。

严守：U<=L，U<=C32；zero-active record不产生虚构请求。这里的record_count不是直接测得的L1/L2 hardware request count；C32也不是实际L2或DRAM bytes。

### Role归属

对完整访问区间核object bounds，而不仅是起始addr。越界或多对象重叠标记`CROSS_BOUNDARY_OR_AMBIGUOUS`，不擅自分配。

对于同record不同role覆盖相同sector：全record sector并集只计一次；role各自覆盖可单列，但注明non-additive，禁止相加冒充互斥硬件流量分摊。报告MIXED/shared-sector数量。

### 聚合

同时提供ratio-of-sums与per-record分布，不用unweighted mean掩盖不同访问次数。nearest-rank quantile定义与旧consumer一致并显式记录。

每条lineage给出G1 coverage：qualified paths、records、active-lane events、unknown比例。非全覆盖时只能比较共同已定义的范围，不能用G0总量作G1分母。

按typed role列：lane events、logical bytes L、unique bytes U、sector proxy C32、pure-role record数、mixed数。并列比较旧lane-event share与新qualified-byte/sector-proxy share；不同分母明确写出。

## 8. G2：可选、同CTA的warp共享描述

在同一shard/process/launch内，以CTA xyz与warp一起区分身份，计算每个sector被多少不同warp访问。warp ID在不同CTA复用，不能只用warp字段。

不跨shard拼VA、不建立跨path时间顺序、不推SM placement、不做reuse distance或cache simulation。G2只叫distinct-warp sharing descriptor；同sector多warp访问不证明它被多次从DRAM取回。

若身份或内存预算不足，输出`G2_NOT_AUTHORIZED_BY_AVAILABLE_SCOPE`，不阻塞已合格G0/G1。

## 9. Synthetic tests最小集合

至少覆盖：
- 32lane×4B全同地址：L128/U4/C32；
- 32lane×4B对齐连续：L128/U128/C128；
- 每lane间隔32B：L128/U128/C1024；
- 单lane addr31,width4跨2sector：L4/U4/C64；
- masked/zero-active、partial overlap、16B vector；
- role边界、mixed roles同sector、无object map；
- 相同warp编号不同CTA；相同VA不同shard不能合并；
- unresolved width只产生G0，不偷算G1；
- known per-shard/history counts闭合。

这些是算子定义的正确性测试，不是性能微基准。

## 10. 解释与结束条件

允许组合标签：
- `WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED`
- `ROLE_EVENT_SHARE_DIFFERS_FROM_SECTOR_PROXY_SHARE`
- `FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY`
- `NO_MATERIAL_NEW_STRUCTURAL_DIFFERENCE_OBSERVED`
- `WIDTH_AUTHORITY_PARTIAL_G0_ONLY_OR_SCOPED_G1`

差异的量值照实列出，不事后新造显著性/性能门槛。最多保留一个需要native检验的问题；没有就明确negative closure。不能只为高L/U或低U/C就建议加新缓存/广播硬件。

禁止结论：MoE普遍规律、L2/DRAM bytes节省、实际cache hit rate、SM瓶颈已证、cache机制已获授权。现有三lineage同gemvx-family耦合继续注明。

## 11. Compact outputs

目录：`docs/vm_tlb/review_packs/C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1/`

- `README.md`：问题、合同、raw锚点、结果与限制；
- `AUTHORITY_AND_VALIDATION.json`：manifest/ACK/ABI/旧count再闭合及测试；
- `PATH_WIDTH_AUDIT.tsv`；
- `ROLE_GEOMETRY.tsv`；
- `PER_SHARD_GEOMETRY.tsv`，需要时另附G2摘要而非巨大逐地址表；
- `SCIENTIFIC_INTERPRETATION.md`，含是否值得下一实验；
- `FINAL_DECISION.json`；
- `SHA256SUMS`。

生成器和tests放`util/vm_tlb/c16/`。不复制全部raw进Git，不制造几十个重复receipt。

## 12. STOP政策

普通工程问题solve-and-continue；未定义width只限制对应path，不停整条任务。真正raw identity/count不匹配必须停止受影响lineage并报告，不编造三模型共性。绝不以缺少字段为理由自动去109重抓。

完成后：validate → diff check → commit → push → fetch-back exact commit/tree → clean → 报告 → STOP。

报告首行写`Lane8 / 174-new / CPU-only`。此任务不会占用Lane6窗口，Lane6保留给正在进行的OLMoE producer后续独立消费。
