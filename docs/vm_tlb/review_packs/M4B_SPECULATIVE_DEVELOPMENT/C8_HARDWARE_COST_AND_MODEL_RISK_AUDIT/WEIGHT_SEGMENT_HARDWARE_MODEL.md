# Weight Segment：硬件模型审计

标签：`SPECULATIVE_CANDIDATE`。本文件审计冻结 Core `c21137bc` 的模型含义；不把 C++
range vector 或 C4 state-machine telemetry 当成硬件实现。

## 结论

“一个 range descriptor 加速 Weight 翻译”可以成为合理的 GPU translation architecture，
但**当前模型还不是一个可公平 replay 的硬件定义**。它缺少 PA 映射、可信的 Weight
分类/安装来源、端口和排队，以及 address-space 生命周期规则。尤其当前 `SimPA` 为
identity-like `ppn=vpn`，会绕过真实 VA→PA 映射问题，定为 `HIGH_MODEL_RISK`。

在 C4 配置（49-bit VA、64KiB 页、35 个 cluster）下，令：

- `V=49`：VA 位数；`P`：实现所需 PA/PPN 位数（证据没有给出，不能假定）；
- `A`：ASID/PASID 或 address-space context 位数；`Q`：保护、访问权限和必要的 memory
  attribute 位数；`Z`：page-size/translation granularity class 位数；`E`：generation/epoch
  位数；`N`：每个 context 或表的 descriptors 数；
- `M`：PA mapping state（见下）；`R`：descriptor replacement/priority/状态位。

一个物理可信 descriptor 至少是：

```
D = valid(1) + context(A) + VA_base(V) + VA_limit(V) + Z + Q + M + E + R
  = 1 + A + 2V + Z + Q + M + E + R
```

当前 C++ `weight_segment_map` 只有 `start,end` 两个 64-bit 值；若只将它视作 range
matcher，其**不含 context、mapping、权限和生命周期**的存储下界为 `1+2V=99` bits。
这是缺项下界，不是一个可部署 descriptor 的面积估计。

## 1. VA→PA、context、权限与 state（W1/W4）

冻结实现的 `weight_segment_map::translate()` 对完整落入 range 的请求返回
`vpn(start,page_size)`；`present_page_mapper`/radix backend 同样解析为 `ppn=vpn`。也就是
Segment hit 没有从 descriptor 获得真实 PA。真实实现必须在下面两种语义中选择一种：

| mapping 选择 | `M` 的最低内容 | 必要 invariant / 代价 |
| --- | --- | --- |
| 连续物理映射 | `PA_base` 或 base PPN，宽度 `P` | 运行时必须证明并 pin 整个 `[VA_base, VA_limit]` 的物理连续性与同一 granularity；命中用 `PA_base+(VA-VA_base)`。迁移、碎片或 promotion/demotion 可破坏该 invariant。 |
| 间接映射 | page-table root/pointer 或 compressed per-page mapping，宽度至少 `P_root`，最坏可接近 `N_pages*P` | 仍需一次可时序建模的读取、cache/coherence、权限与失效；若是 per-page table，不能把它免费视为一个 descriptor。 |

未建模但命中正确性必需的字段包括 `A`、有效位、`Q`、`Z`、PA mapping、`E` 以及
context ownership。64KiB 的 C4 固定配置可把 `Z` 作为全局常量；一旦支持多 page size 或
superpage，`Z` 及匹配优先级就必须成为合同的一部分。当前调用点传入 ASID `0`，所以
multi-process、PASID、MIG/VM partition 或 context switch 都没有被压力到。

因此 identity-like mapping 不是“保守的硬件近似”：它避开了给出 `M`、连续性、权限和
remap 代价的义务。任何把 C4 的 Segment hit latency 或资源抑制外推到真实 PA 映射的说法
都是不成立的。

## 2. 当前软件 range vector 对应的 lookup 硬件（W2/W7）

软件 vector 逐个检查范围；当前 config 是 `N=1`，且 Segment lookup 没有端口、bank、
comparator 或 queue 状态。下面给出可实现的拓扑选择，而不是声称已有其中之一：

| N | 合理候选拓扑 | 每 lookup 的符号比较工作 | 端口/复制问题 | 评价 |
| ---: | --- | --- | --- | --- |
| 1 | 每 context 单 descriptor，两个 `V`-bit range compare 后 AND | `2V` 比较输入位 | 若每 SM 一条输入，需每 SM comparator 或集中式多入口 | 对连续 PA 方案可很小，但仍需 context/epoch/权限检查。 |
| 4 | 小 CAM/并行 4 descriptor compare，或按 context bank | `N*2V`，再 priority select | 单 shared port 会串行化；per-SM replication 复制 35 份 | 可实现，软件 vector 尚可作为功能原型，不是时序模型。 |
| 16 | banked descriptor SRAM + compare，或 16-entry range CAM | 取决于 bank 命中；最坏 `N*2V` | 需要 bank select、冲突、多个 in-flight 请求和 update arbitration | 不能再把 vector search 记为固定 10 cycles。 |
| 64 | coarse prefix/interval index 后小 CAM，或多 bank hierarchical range table | index compare + candidate range compare | 要定义 index false positive、bank conflict、跨 context policy、flush/update | 若仍做全并行 64 range compare，比较器和布线会线性放大。 |

每个 range 需两个 `V` 位不等式（`VA>=base` 与 `VA<=limit`），故比较器输入量的透明
proxy 为 `2NV` bits/lookup port，尚未包含 context match、priority、PA arithmetic、权限、
更新逻辑或 wire load。它只说明 scaling 趋势，绝非面积/能耗数字。

当前 35 cluster × 每 cluster 1 个 L1 lookup port，潜在每周期可接纳 35 个新 translation
lookup。若 descriptor table 放在每 SM，本地 1 port 能匹配该 ingress，但 descriptor storage
与 compare logic 乘以 35；若共享一个 1-port table，则同一周期只能接纳 1 个、最多产生 34
个净新增排队请求。共享表要不伤害该上限，至少要提供等效的多 bank/multiport throughput，
或显式建模 `Tseg<35` 时的 queue/backpressure。两者目前都不存在。

更关键的是冻结状态机对**所有**初始 translation lookup 都 launch Segment；它在 lookup
完成后才凭 object map 允许 Weight hit。C4 累计为 `1539` launch、仅 `512` hit、`1027`
miss。因此即使最终加速对象是 Weight，当前并行路径的 ingress 压力不是只由 Weight
traffic 决定。一个真实设计可在 table matcher 本身完成 range classification，或由前置的
受信分类器 gating；两种选择都必须有端口和时延定义。

## 3. 固定 10-cycle 与 parallel Segment+L1（W3）

冻结配置为 L1 lookup 10 cycles，Segment 固定 10 cycles。状态机发射时先消耗 L1 port，
然后等待两者完成；其 ready time 是：

```
Tready = max(TL1, Tsegment_service + Tsegment_queue)
```

因此在未建模队列、`Tsegment_service=10` 的软件世界，L1-hit 没有额外时延；这只是
`10=10` 的参数恒等式，**不是**并行硬件无需代价的证据。若 Segment 有 queue/bank conflict
使 `Tsegment_queue>0`，任何 L1 hit 都会因为等待 Segment result 而被延迟。C7 的
`Lseg<=10` 才不伤 L1-hit、`Lseg<90` 才在 L1-miss/L2-hit 下有解析余量，必须补上 queue
后的 `Lseg` 才可用于设计判断。

| 情形 | 当前模型 | 真实实现必须决定 | 对 C5 影响 |
| --- | --- | --- | --- |
| L1 hit | 等待 Segment completion | 是继续等待、L1 先完成即返回、还是可取消 Segment？ | 政策会改变 L1-hit 时延与 Segment observability。 |
| Segment hit | 抑制 L2/MSHR/PWQ/walker/PWC/PTE/fill | PA/权限/epoch 检查在哪一级完成？ | 必须保证与普通 PTE 相同的 protection/mapping 语义。 |
| Segment miss | 复用已完成 L1，不重探 | descriptor table queue 时何时重放/背压？ | 决定 ingress throughput 和 MSHR 时序。 |
| 多个 SM 同时 lookup | 无 segment port counter | shared banks、per-SM replicas、或 ingress queue？ | 10 cycles 不再足以定义 latency。 |

可作为**待批准**的低风险实现方向是：每 SM 一个只读 descriptor cache（1 input/cycle），
由 context-tagged immutable descriptor snapshot 驱动；但这会有 35 倍复制、更新广播和
epoch invalidation。共享设计则必须以同等 aggregate port/bank 数或测得的 queue 模型说明
它不会把原来 per-SM L1 hit 排队。没有选择前，10-cycle 是
`MODEL_ASSUMPTION_NEEDS_VALIDATION`；无端口/queue 是 `HIGH_MODEL_RISK`。

## 4. Weight 分类不是硬件天赋（W6）

当前流程先以 immutable object map 将 VA classify 为 `OBJECT_WEIGHT`，再调用 range map。
object map 注释将 label 定义为 observability metadata；但 Segment eligibility 仍依赖这个
外部标签。range descriptors 本身若被可信驱动安装，可以以 VA+context 范围自然选择
“加速范围”，不需要硬件知道机器学习对象名。相反，若“Weight”是软件 annotation，必须
定义 provenance：谁在模型加载时证明 range、谁有权限安装、何时撤销、如何防止其它 tenant
将任意 VA 标成 Weight 以绕过 translation/protection。

可接受的合同是 privileged GPU driver 根据已验证 allocation/loader metadata 生成
context-tagged descriptor，硬件只匹配地址/权限/epoch；object map 仅保留为 telemetry
oracle，而不作为硬件判定事实。当前 parser 仅检查 map header/hash 字段存在，并未在硬件
路径复算或 bind immutable artifact，这不足以构成 provenance。

## 5. descriptor 生命周期与 stale 防护（W5）

所有下列事件必须使 descriptor 与普通 TLB 同步失效或 generation-mismatch；当前模型均未
覆盖：page fault/permission change、page migration/remap、UVM CPU/GPU ownership change、
unmap/free、context switch、ASID/PASID reuse、TLB shootdown、descriptor replacement 和
model unload。

最低正确性协议在 `SOFTWARE_RUNTIME_CONTRACT.md`：安装前记录 context、VA range、mapping
form、权限和 epoch；所有 Segment hit 检查 context/epoch；更新先阻止新命中，广播
invalidate/epoch，再等待旧请求 drain 或按 epoch retry；仅 ack 后允许映射改变或 ASID reuse。
这使 stale descriptor 成为可验证的协议问题，而不是把永不变化的 C4 map 误当作普遍性质。

## 审计判定

| 问题 | 判定 |
| --- | --- |
| 一个 1-entry、物理连续、context-tagged Weight descriptor 是否可能实现？ | 是，若驱动能证明/维持物理连续、权限和 epoch 合同。 |
| 当前 identity-like / object-map / fixed-10cy 模型是否已经证明该硬件？ | 否。 |
| N=1 到 64 是否可线性沿用 current vector latency？ | 否；必须选 topology、ports、replication 与 update policy。 |
| C5 能否在上述问题未决时解释为 GPU architecture 性能？ | 否，见唯一 gate `ARCHITECTURE_DECISION_REQUIRED`。 |
