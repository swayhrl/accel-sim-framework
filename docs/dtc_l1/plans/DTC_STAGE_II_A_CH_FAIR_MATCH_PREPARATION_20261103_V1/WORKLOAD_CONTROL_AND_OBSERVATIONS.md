# Workload机理、对照及后续观测

详见Agent B的25 kernel矩阵（11程序），每行已有源码/trace/runtime证据等级、循环/访存方向、潜在复用、依赖、并发及不能确认项。固定Atlas47a097aa不是新的capture-source认证。

## 对照为什么保留

- convolutionSeparable/scan/2DCONV：不同阶段与邻域结构的正响应。已知加速仅是同冻结trace的全程测量；不能据此给某个kernel分配收益。
- hybridsort：多轮分桶/散写/归并；原F128负例保持null，F256仅作补充四方，不从IR借值。
- ATAX/MVT/BICG：访问方向、执行顺序、中间依赖及有限CTA并发的比较。不把源码步幅直接转成cache冲突次数。
- vectorAdd：已观测F256负响应，保留边界对照，不能用它代表所有memory workload。
- GEMM/3MM/particlefilter_naive：F扩张零响应但可有L1设计差距，用于区分两层条件。naive粒子滤波host/CPU段不等于模拟的GPU工作量。

## 当前证据缺口

候选conv主机源码参数与trace3072²、scan候选N与traceN6815744不一致；捕获源码/ELF尚未认证。保留现有trace身份，不换输入或提升“完整应用”结论。多数kernel级runtime延迟/阻塞/并发没有实测。原始计数器缺失不是零：B从旧L提取44个同SHA结果行，43条有计数器，hybrid-F128负例为null；这些主要是全trace总量。最终REPORT的NOT_COLLECTED字段与旧L总量来源是两个不同证据层，不能混写。

已见的反例必须进入因果审查：conv/scan提速时最后打印avg_mrq可上升；vectorAdd-F256变慢时reservation failures可下降。末端MRQ不是全kernel平均；reservation失败次数受指令数、执行时间与重试节奏影响。二者都不能单独证明critical-path排队改善或性能原因。

## 最多5项观测优先级（本轮均不执行插桩或模拟）

1. **只读可完成：**逐已接受日志/trace metadata确认launch边界、kernel顺序与ROI；仅按实际存在字段制作阶段索引。无逐kernelcycles则明确WHOLE_TRACE_ONLY，不按CTA/名称估分。
2. **只读可完成：**对匹配RESULT SHA的现有kernel标识/总量做单位与分母核查，分清DRAM32B atom、L2 32B sector、L1 128B line、global/texture/constant/atomic；计数器未测保持UNKNOWN。
3. **需另授权插桩与验证：**按精确kernel boundary累计周期及关键停顿，检查跨kernel排空和并发kernel重叠，避免错误相加；加观测代码必须单独记录Core/binary并做telemetry-neutral对照。
4. **需另授权插桩与验证：**MSHR allocation/merge/full与missQ阻塞、DRAM调度占用/排队年龄/服务等待分布，区分时间加权occupancy和最后打印值，定位请求因果路径。
5. **需另授权插桩与验证：**L1 Tag/data/PIB/有限完成服务、L1→L2发送与重复请求关联，给请求生命周期来源标识；先做事件守恒/重试去重，再分析潜在L1与下游瓶颈，不由静态地址重复推断实际命中/合并。

这些是现有证据允许的后续设计，不能在本Goal自动改代码、抓trace或执行模型。
