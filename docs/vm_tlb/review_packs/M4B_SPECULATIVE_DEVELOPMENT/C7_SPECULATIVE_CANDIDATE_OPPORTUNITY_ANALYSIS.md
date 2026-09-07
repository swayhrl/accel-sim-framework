# C7：SPECULATIVE_CANDIDATE opportunity analysis

状态：`ANALYTICAL_OPPORTUNITY_ONLY`。本报告保持
`REFERENCE_APPROX_SUBENTRY_16` 与 `SPECULATIVE_CANDIDATE` 标签；它不是性能模拟、
不是正式 M4B 结果，也不改变 C0--C6 的实现、配置或 C5 冻结决定。

## 范围与可复现性

本分析只读取既有 Window C 输入和产物：decode1 object/segment map、C4 已提交版本的
三 kernel telemetry/log、已选 trace 的前三个文件，以及同一冻结 740-file trace list 的
确定性前缀 25 个 trace。没有重新 build、没有启动 Accel-Sim、没有生成 trace，也没有
扫描完整 740-file ROI；后者含一个 28,035,977-line trace，保留给资源恢复后的 C5，而
不是在 analysis-only 窗口制造新的重负载。

| 输入 | 绑定 |
| --- | --- |
| trace list | 740 files；SHA-256 `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` |
| decode1 object map | SHA-256 `b1dd8745d5a9fd418d03c4bab82627d820c161b6f990f913e6f90583e72e3340` |
| decode1 Segment map | SHA-256 `be59d94e859976b04643b63463389bf9a51368b7810810a73e8298cc37d20323` |
| C4 runtime | Framework `5dd4501a`；Core `c21137bc`；committed-rerun1 manifests retained in C scratch（文档 closeout 的当前 Framework tip 为 `fd828e3d`） |
| offline reader | `C7_offline_trace_analysis.py`，SHA-256 `e8cab086dfd0bc17f8da21f1564401aa1f59ac119b309f3176ac91c07db4a4c2` |

脚本逐行复现 trace parser 的 list/base-stride/base-delta 地址解压，并以每条指令去重的
32-byte sector 作为**离线几何代理**。它不是 Accel-Sim transaction、TLB lookup 或周期
模型；所有下文以此代理得出的数均不能与 telemetry 的实际请求数混用。

## 1. Weight Segment opportunity

### 描述符覆盖与边界

decode1 Segment map 的一个 immutable descriptor 与 object map 中的唯一 Weight range
完全相同：`[0x7f7ec6000000, 0x7f7f02520fff]`，共 1,012,011,008 bytes。因此它按对象
**字节范围覆盖 100%** 的声明 Weight 区间。范围包含 15,442 个完整 64KiB 页和第
15,443 页的前 4KiB；故若把这个尾页视为完整页需求，完整页覆盖率为 99.9935%。任何
跨过该尾部的请求会按实现保守 miss，而不会被伪造为 Segment hit。

在 C4 选定的三个 trace 中，离线 lane/sector 代理没有发现 descriptor boundary、64KiB
page 或 16-leaf group 边界跨越。前三个 kernel 的几何代理如下：

| kernel | global 32B-sector proxy | Weight proxy | Weight proxy share | descriptor boundary cross |
| --- | ---: | ---: | ---: | ---: |
| 1464 | 2,560 | 1,024 | 40.00% | 0 |
| 1465 | 1 | 0 | 0% | 0 |
| 1466 | 2 | 0 | 0% | 0 |

这解释了为什么 `kernel-1464` 是唯一的受限 Weight opportunity。C4 的**权威 runtime
telemetry**（而非上表代理）在它上面观测到 512 Segment hit；1465/1466 增量均为零。
前三个 kernel 的 Segment launch/hit/miss 是 `1536/512/1024`、`1/0/1`、`2/0/2`。

为了避免把前三个 kernel 误当作全 ROI，额外的确定性 0--24 trace 前缀只作为几何
sentinel：2,881,565 global lane references 中 229,376 个（7.9601%）落在 Weight；
1,025,730 个 sector proxy 中 100,352 个（9.7835%）为 Weight，且全部完整落在
descriptor 内、boundary crossing 为零。这是 opportunity sample，不是对 740-kernel
ROI 的比例外推。

### 离线 lookup-latency sensitivity / break-even

C4 固定 L1 lookup latency 为 10 cycles，L2 lookup latency 为 80 cycles，Segment
lookup latency 为 10 cycles。对于 C4 中 512 个 Segment hit，它们的 raw parallel L1
结果全为 miss；不含端口排队、MSHR merge、walk 和响应竞争时，候选 gated delay 的
下界为 `max(10, Lseg)`，而 conventional L1-miss/L2-hit 下界为 `10 + 80 = 90`。

| `Lseg` (cycles) | gated delay lower bound | 对 90-cycle L2-hit 下界的解析余量 |
| ---: | ---: | ---: |
| 0 / 5 / 10 | 10 | 80 |
| 20 | 20 | 70 |
| 40 | 40 | 50 |
| 80 | 80 | 10 |
| 90 | 90 | 0（break-even） |
| 100 | 100 | -10 |

所以，在这个**仅限 L1-miss 且 conventional L2-hit 的解析模型**中，严格获益要求
`Lseg < 90`；当前 10-cycle 参数处于该区间。若 conventional path 是 walk，理论余量
会更大；若它是 L1 hit，非回退条件则是 `Lseg <= 10`。这些都不是全核 latency 或
speedup 预测，因为实际请求会合并、排队并与 execution 重叠。

**Weight Segment opportunity：HIGH（受限、分析性）。** 证据是一个完整覆盖的描述符、
512 个实际 C4 Segment hit、零观测边界拒绝，以及当前参数下清晰的 L1-miss/L2-hit
lower-bound 余量。该等级不主张 512 次独立 page walk 或 512 次物理 L2 请求被消除。

## 2. sub-entry opportunity

### 实际 C4 leaf occupancy 与为何没有收益

C4 sub-entry 与 standard profile 在前三个 kernel 的 L2 access/miss 轨迹相同：累积
`16/16`、`17/16`、`18/16`（access/miss）。sub-entry telemetry 显示：

| 截止 kernel | valid leaves | group fills | existing-group fills | selected-leaf misses | group evictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1464 | 1 | 1 | 0 | 0 | 0 |
| 1465 | 1 | 1 | 0 | 0 | 0 |
| 1466 | 1 | 1 | 0 | 0 | 0 |

base-tag/leaf hit 累积为 `0/0`、`1/1`、`2/2`：后两个只是同一 leaf 的普通重用。也就是
这个受限重放到达 L2 的实际 occupancy 始终是 `1/16`，没有 sibling leaf fill、没有
group replacement pressure；因此不能期望相对 exact-page L2 出现 sub-entry 收益。
这与 C4 的无差异结果一致，而不是候选失败。

### 离线空间几何与压力边界

同一冻结 trace list 的前 25 文件提供不同的、仍然仅为 proxy 的空间图像：62 个不同
64KiB 页落在 10 个 group，平均 6.2 leaf/group，leaf histogram 为
`1:5, 3:1, 6:1, 16:3`；52 个唯一页首次出现时已存在 sibling group。这相当于静态
`1 - 10/62 = 83.871%` group-entry compression opportunity。该前缀中每个 hash set 最多
只有一个 group，故没有代理 replacement pressure。

完整 Weight descriptor 的静态地址跨度则说明相反的容量边界：15,443 个 64KiB 页跨
966 个 16-leaf group，理论 group-entry 压缩为 93.745%，但大于候选的 768 group
entries。按冻结的 C1 generic hash，全部 48 个 set 都会有 20 或 21 个静态 group，超过
16-way 容量 198 个 group。它不是“会有 198 次替换”的动态结论；它只说明若完整
Weight range 同时成为活跃工作集，sub-entry 会显著缓和、但不能消除 replacement
pressure。C4 很小的实际工作集尚未触及这个边界。

**sub-entry opportunity：MEDIUM（受限、分析性）。** 前 25-file geometry 有强的
sibling-leaf 空间复用，静态 Weight 地址范围也有高压缩上限；但 C4 真正到达 L2 的
工作集只有一个 leaf，且完全没有 existing-group fill。L1 filtering、动态 locality 和
768-group 容量决定真实收益，必须由将来的 C5 验证。

## 3. C4 Weight Segment 资源抑制与守恒

下表是 `subentry-segment` 已有 telemetry 的**逐 kernel 增量**。`suppressed` 的每一列
是状态机语义计数：表示 hit requester 没有进入该 conventional path；它不是对应物理
资源事件的反事实数量。

| kernel | Segment launch / hit / miss | raw L1 H/M | effective L1 H/M | L2 实际增量 | MSHR / walker / PWC / PTE 实际增量 | 每项语义 suppressed (L2, MSHR, PWQ, walker, PWC, PTE, L1-fill) |
| --- | --- | --- | --- | --- | --- | --- |
| 1464 | 1536 / 512 / 1024 | 1008 / 528 | 1008 / 16 | 16 miss | 1 alloc + 15 merge / 1 / 3 / 4 | 512, 512, 512, 512, 512, 512, 512 |
| 1465 | 1 / 0 / 1 | 0 / 1 | 0 / 1 | 1 hit | 0 / 0 / 0 / 0 | 0, 0, 0, 0, 0, 0, 0 |
| 1466 | 2 / 0 / 2 | 1 / 1 | 1 / 1 | 1 hit | 0 / 0 / 0 / 0 | 0, 0, 0, 0, 0, 0, 0 |

累计守恒均成立：

```
1539 launches = 1539 completions = 512 hits + 1027 misses
1539 raw-L1 completions = 1009 raw hits + 530 raw misses
1027 Segment misses = 1009 effective-L1 hits + 18 effective-L1 misses
530 raw misses - 18 effective misses = 512 discarded raw results = Segment hits
18 L2 launches = 2 L2 hits + 16 L2 misses
16 L2 misses = 1 MSHR allocation + 15 MSHR merges
1 walk start = 1 walk completion; 4 PTE requests = 4 responses
```

因此每一个 Segment hit 都既完成了并行 raw L1 观察、又没有 conventional TLB fill；
Segment miss 只消费既有 raw L1 结果。telemetry 没有 PWQ enqueue 总数，故它只能由
state-machine suppression counter 而非独立物理 enqueue counter 验证。

作为量级交叉检查，kernel-1464 截止点的 standard/sub-entry profile 均记录 32 L2
launch、2 MSHR allocation、30 merge、2 walk、6 PWC access、7 PTE request；segment
profile 记录 16、1、15、1、3、4。这个已观测 profile 差异与 Weight conventional path
被绕开方向一致，但 lookup request 总数也从 1568 变为 1552，所以不把差值伪称为严格
逐 request 的反事实节省。

## 4. 资源恢复后的 C5 优先级

资源恢复并重新通过 farm gate 后，C5 **值得优先运行**，因为它是区分“C4 恰好只有
一个 L2 leaf”与“完整 ROI 存在真实 sibling reuse/descriptor coverage”的唯一受控方法。
建议顺序如下，所有输出继续标记 speculative：

1. `decode1 paper` → `decode1 subentry`：先隔离 `REFERENCE_APPROX_SUBENTRY_16` 的
   full-ROI group reuse 与 replacement pressure。
2. `decode1 subentry-segment`：紧接同一 ROI 检验高等级的 Weight descriptor opportunity
   是否跨越 C4 kernel-1464；并保存上述资源分解和守恒计数。
3. `prefill paper` → `prefill subentry` → `prefill subentry-segment`：在不以 decode1
   采样替代 prefill 的前提下作同样的隔离比较。
4. `ideal` 只在前三组候选均健康且剩余资源允许时作为诊断上界，而非主结果。

不得据本报告启动 C5、修改实现或进入 KV segmentation、12K KV、M5。C5 仍保持
`SKIPPED_POLICY`，直至 scratch 空间、swap 和 Window A 优先级的原有闸门全部恢复。
