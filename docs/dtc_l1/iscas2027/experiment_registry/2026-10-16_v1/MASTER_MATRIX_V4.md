# V4 最新已核验实验台账与三项辅助审查

**状态时间**：Lane A `e81690db02af419041bd0fce284b451f2a80304f`，其中R2严格检查点`2026-10-16 11:22:34 UTC`。Lane B `d9f896a5`、C `d6f0a330`、D `d58e75ce`。表格只记录这些提交的状态，不代表机器此刻的实时进度。无新增仿真和科学输入准入。V1—V3保留。

| 证据状态 | 最新审查 |
|---|---|
| 原注册44行 | **17 terminal/invariant PASS（其中Hotspot两行科学HOLD）、16 running、3 admission HOLD、8 registered**；不能称17条无条件science PASS |
| 完整有限服务主三臂 | Btree、2DConvolution、DWT2D、MRI-Q四项三个arm均严格验收；所有regression和小收益保留 |
| 同等待深度 | **Btree IO128 / OO128**已严格加入配对：周期247940/173210；mean full-ready-to-complete167.6345/10.2981 cycles/cacheable warp instruction；old map-loss-to-free316.3103/0.9616 cycles/release，需保留分母与成本边界 |
| Hotspot V2 | 历史来源family bug确定；**185个PC全部opcode-root/GPR签名匹配，20,671,252条明确地址参考匹配**；6PC、122,760记录需修，2,944,024个active lane地址改变。**确切采集binary绑定未完成**，原trace旧结果不提升；建议优先审查为**新派生输入**，不静默放行 |
| 4080容量 C | 固定80KiB独立池不能在128KiB L1/shared中保持64/100KiB shared全域；候选端口/清退/普通服务均需新合同。**此次只保留现代baseline-only，不授权现代DTC行** |
| SpMV D | CPU-only审查发现缺少常量地址、LDC64高目的寄存器及uniform/predicate依赖。**不准89映射86、SpMV trace不准入**；原生109仍有效 |
| 109 LayerNorm | Native有效，SASS NOT_ADMITTED，未改动 |
| 主性能GM | 尚未具备原定义的完整科学有效12项，**不计算GM12、GM11冒名或GM14** |

## Hotspot推荐路线，非自动科学批准

优先选择Lane B窗口的**V2重建解释科学审查**（选项1），而非无具体路径地长期找原采集包，或直接抛弃Hotspot。决策含义是**允许使用已有候选作为新派生输入接受审查**，不等于“确认原ELF/native真实地址”或“修复已发生并可算旧GM12”。

后续审查必须明确源模型推导与独立原始字节两层证据；复核6PC每处变化、mode0过量向量及shared sparse/first-lane anchors，检查V2假定捕获家族的适用范围和未覆盖的predicate/immediate差别；对另外11负载进行**限定format applicability的CPU-only审计**，不要因此重跑11个程序。只在可证闭合后，独立记录 `DERIVED_HOTSPOT_SOURCE_PROFILE_V2` 新输入SHA、来源、局限，保留旧全部尝试/失败。

主Lane A在科学准入前继续所有非Hotspot合法行，不改变44行runner/locks。若新Hotspot输入准入，A另外注册**与新输入完全配对**的最小B16-N/IO256/OO128，以及确实进入正文claim所需的TC80/TRAD96/IO128/WAIT128；不允许新IO除以旧B16，也不允许默默修改原44行数值。新的集合定义及GM身份要独立审核。若审查不能支持派生解释，保留HOLD，转入明确用户批准的来源恢复或新输入路线。

## 实验效率和停点

- 继续Lane A原Goal与滚动调度，脚本的唯一launcher不变；已启动16条不重启、终止后strict verify、再滚动补位。缓慢的GESUMMV/GEMM/ATAX与较短控制同时推进；已有matched Btree可先进入论文解释。
- Lane B先做轻量语义审查和局部格式适用性，停止无路径的全盘原ELF搜索；不启动任何simulation。C、D已产出有证据的NO-GO，暂时关闭辅助工程任务，不继续开发现代DTC大改或SpMV适配器。
- RTX3070、第三负载族、额外DRAM/queue/ICNT矩阵、logical80和冻结FAST64/TC80重跑均不在这轮范围内。
- 本文件是科研建议和已验收checkpoint的账本，不是对Lane B修复输入或Lane A新运行的已批准执行合同。
