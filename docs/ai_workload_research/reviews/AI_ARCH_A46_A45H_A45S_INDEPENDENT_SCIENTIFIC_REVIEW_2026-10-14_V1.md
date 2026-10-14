# Round A46｜A45H原CPUAdam软件反证＋A45S下一发现实验选择：独立科研审查

**审查：ChatGPT／AI-ARCH Discovery；2026-10-14。固定协调起点：`773d3a7279d6d60693d54ab3ba956343fa33b776`。**

**科学裁决：**
- **A45H：`ACCEPT_SCOPED_CPU_COMPONENT_NATIVE_SOFTWARE_SENSITIVITY / STOP`**。实际用原CPUAdam模块、FP32合成参数/状态和新鲜进程取得36条件×7＝252正式值；OMP8优于16在两个合成Adam形状中稳定。但这**不是**真实15k Rubble late训练wall、作者OMP64最优或物理硬件headroom。
- **A45S：`ACCEPT_QA_ONE_CONDITIONAL_DISCOVERY_PROPOSAL / NO_GPU_AUTHORIZATION`**。下一最小候选选GloVe100＋cuVS CAGRA，同图同recall、AUTO与调优过的SINGLE_CTA+SMALL、batch1/256四个正式点。它是低成本**发现性问题**，不能把已有参数策略性能差直接说成新资源机制。
- **本轮所有执行Lane已STOP**。不续跑原A26GR1/A45H/A45S，不新增GPU、训练、模拟器、trace或机制。下次唯一合理执行申请是单个有界109 CAGRA canary→小矩阵（如用户单独批准），失败即NO_GO；若条件不成立继续Discovery而非重型移植。

## 1. 固定Git和完整性验证

| 项目 | A45H / 109 CPU-only | A45S / 174-new source-only |
|---|---|---|
| 父Goal提交 | `7b59349979dc77ec0a671c0ca96d7ebaadf3d8dd` | `65130892533d92c04a704deee1f037865fee5367` |
| 最终提交 | `1936dffd204043a1ab6c0fad5e7aebf565497c1a` | `e0236f9e34f25dc7c96d048b31754bcb74e05764` |
| Git-data tree | `bf2eed65fdc6c0fe4ee2602c28c3b6e5c0a3be33` | `3cd993c33d94a55a30f5d954756f92bbff9bc000` |
| 报告blob | `6ca6e43895f468f6de8ebb85fca12fa17e07aa2f` | `df46a84b7500defa52a4be7001f0adffcd5a9637` |
| 差分和HEAD | parent→branch仅4个新增文件，ahead1/behind0；branchHEAD identical | parent→branch仅1个新增报告，ahead1/behind0；branchHEAD identical |
| 独立内容校验 | measurements JSON SHA256 `c691a4f45151ca26687db3b672a64545ace78b23e3dacd677663686ccc51b846` **本窗口重新计算一致** | 报告SHA256 `4da908111d8e856cf0315d897e0b9ea8482caed9fdd1a0e6b0c64b2f8fb881da` **本窗口重新计算一致** |

固定文件：[A45H报告](https://github.com/swayhrl/accel-sim-framework/blob/1936dffd204043a1ab6c0fad5e7aebf565497c1a/docs/ai_workload_research/reviews/AI_ARCH_A45H_CPUADAM_CPUONLY_SOFTWARE_REBUTTAL_109_V1.md)；[A45H原始JSON](https://github.com/swayhrl/accel-sim-framework/blob/1936dffd204043a1ab6c0fad5e7aebf565497c1a/docs/ai_workload_research/reviews/AI_ARCH_A45H_CPUADAM_CPUONLY_SOFTWARE_REBUTTAL_109_V1.measurements.json)；[A45S报告](https://github.com/swayhrl/accel-sim-framework/blob/e0236f9e34f25dc7c96d048b31754bcb74e05764/docs/ai_workload_research/reviews/AI_ARCH_A45S_SPARSE_ANNS_ONE_PROBE_ADMISSION_174NEW_V1.md)。

Git、原始JSON和文献/源码读取可独立审查逻辑；“机器无CUDA/工作区clean/进程资源峰值”由Lane执行侧receipt报告，本窗口未SSH实机复测，不把Git commit等同真实机器监控。

## 2. A45H：作者CPU软件敏感性成立，硬件推论仍不成立

**来源与数值：** 同一冻结`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`，旧编译模块SHA256 `c451fda99327e5969da9f0476ef3f4915815dc9ff314c22cce002e5551379a55`。FP32、seed42、原Adam函数，200k×48与400k×48均令合成U=N/counter0，数值每项max abs error=0，既有门1e-5。正式7次采样前有3次warmup/numeric check；修正前的168个prequalification scan保留但不作正式结论，正式252和180个warmup均有raw。7次同一fresh process**不是7次独立进程显著性**。

| CPU函数和合成shape | OMP1 median | OMP8 median | OMP16 median | OMP16/OMP8时间比 |
|---|---:|---:|---:|---:|
| deferred update 200k×48 | 28.092ms | 4.552ms | 5.884ms | 1.293 |
| deferred update 400k×48 | 56.163ms | 9.417ms | 12.412ms | 1.318 |
| parameter forwarding 200k×48 | 27.995ms | 4.020ms | 5.973ms | 1.486 |
| parameter forwarding 400k×48 | 55.965ms | 8.004ms | 12.131ms | 1.516 |

在200k和400k两种合成形状的四组Adam函数测试中，各自七次正式采样的最小—最大区间于OMP8和OMP16间**互不重叠**，说明本次同机同fixture的软件敏感性不只是某次均值偶然；但线程亲和性、P/E核、CPU频率/cache、采样守护与背景负载未被因果控制，不能宣布全局最优线程策略。

`calculate_update_ids` 1%可见IDs条件下，OMP1从N200k `0.090517ms`到N6684932 `3.215151ms`，时间增35.52倍、N增33.42倍；源码多次full-N循环及U处理，支持有限尺寸的`O(N+U)`解释，不是纯DRAM带宽实测/渐近数学证明。OMP16时大N扫描中位`0.703853ms`，本轮也证明线程16在扫描上可能优于8：**不能从Adam的OMP8优势推导所有CPU部件都应选8**。ID、counter用的U是合成可见ID与counter15行的并集；不是真实late U。early/late不同分母不能套用。

**补充源码审查：** 本次保留的原C++`cpu_adam.cpp`在`calculate_update_ids`、`update_counter`与两个Adam更新中都显式`omp_set_num_threads(64)`。A45H Python probe源码在进入前调用`torch.set_num_threads(1)`，但已提交raw的probe终态`torch_threads`字段为`64`，所有six observed processes如此，同时实际`omp_get_thread_limit`返回1/8/16。合理的解释是C++函数内部再次请求64改变之后的OpenMP请求状态；**本窗口没有实机证实该因果**。后续引用时应报告原请求64、实际`OMP_THREAD_LIMIT`合法封顶及`torch_threads`终态64，不能不加说明写“PyTorch线程始终为1”。这不推翻当前有界OMP策略敏感性，但禁止把它包装成线程1/8/16在所有框架算子的普适结论。

**A44影响：** 原晚期修正窗口主线程阻塞并集14.084/14.746ms，CPUAdam调用57.746/64.779ms与下一步前递41.855/45.489ms来自真实OMP16、GPU并发与真实动态Gaussian。A45H不能将200k/400k合成U=N的28→4ms差套成晚期加速百分比。真正需要的还是自然N_visible/U、late完整optimizer state、CPU/GPU临界路径与强软件/NUMA对照。先把3DGS解释视为软件未排除，**当前不推荐长期重训或硬件机制**。

## 3. A45S：源审选择合理，执行前补两处机械门

**同意四点发现性选择。** Spira的完整artifact对环境/数据/多后端补丁要求显著高于单文件GloVe检索，而ANNS可在RTX4080 SM89上尝试现成cuVS。但“平台没有被架构门排除”≠“109环境已资格PASS”；GPU probe若批准，必须先在单个连续有界Goal中做ABI/资产/功能canary。

**新增独立固定源码核验：** `NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`（v26.10.00 tag所属提交）的`python/cuvs/cuvs/neighbors/cagra/cagra.pyx` blob `27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7`，与`cpp/src/neighbors/detail/cagra/search_plan.cuh` blob `da42f637dcd6fd1b299c425d353c77b3f1fe2f85`。已确认IndexParams的`metric="cosine"`、`build_algo="ivf_pq"`合法；SearchParams的`algo="auto"/"single_cta"`、`hashmap_mode="auto"/"small"`及min_bitlen字段确有实际Python接口。旧A33 main快照blob不同，不可用其字节账假装26.10实机行为。

**必须随正式canary绑定的两个细节：**
1. **save/load不仅是“读回图”。** 此v26.10源码`cagra.save(filename,index,include_dataset=True)`默认保存dataset；反序列化API为`cagra.load(precreated_index,filename,out_dataset=Dataset())`，如只反序列化图而不包含dataset，则需显式`cagra.update_dataset`附着原向量。必须保证graph、向量、metric、index的身份和寿命一致；不得把漏dataset造成的错误升级科学NO_GO。
2. **AUTO生效模式需要验证，不是读取参数字串。** 当前planner在非persistent情况下按`itopk_size`、`max_queries`及实际SM数选择single/multi-CTA；在multi-CTA或filtered场景可将hash模式变为HASH，而显式SMALL不在所有模式合法。正式记录resolved effective算法/数据结构；若Python API只回传请求模式`AUTO`，要通过受支持的plan/log/source＋实例化尺寸区分`SOURCE_DERIVED`和`DEVICE_OBSERVED`，不能默默称硬件采集。该细节是软件设计门，不强制第一轮先制造NVIDIA调试插桩框架。

**更重要的科学解释门：** 正式两臂为`AUTO`和在校准集选择h9或h11的`SINGLE_CTA+SMALL`；前者是官方**自动启发式**，未必是所有可用search参数的最优软件路径。B1更可能触发不同并行策略；两臂差异混合算法、清表、历史/线程工作，**不是独立改变SMEM容量**。如果SMALL胜AUTO，首选解释是启发式选择/软件参数改进；若AUTO胜或差异低于误差，停机，不发硬件解释。甚至两者差异显著也仅支持继续定位，不是缓存/SMEM机制资格。

**数值/数据门：** GloVe100 angular原HDF5字节、版权许可、GT、cosine定义/零向量、固定FP32需在首次canary真实核对；独立报告集要求recall@10≥0.95且差异≤0.005；不能为达标事后更换索引、dtype或GT。若该固定`itopk128/width1/iterations64`条件不能达标，`QUALIFICATION_NO_GO`，不等于ANNS整个领域无收益。读取`auto_sync_resources`与实际GPU计时实现时，必须把GPU search区域、端到端H2D+D2H、构图/序列化分母分开，记录频率/allocator等背景问题。

## 4. 下一次最小执行建议及权限

- A45H正式STOP，无需追加合成OMP4/12/24网格；真实3DGS优化要另有自然后期同语义/软件因果资格，而当前再次15k训练和CLM重新工程投入都不划算。
- A45S不需返回174继续阅读相同API。若用户明确授权，建议**仅一个109/RTX4080原生CAGRA Goal**，将version/ABI/source/数据哈希→索引build＋序列化/重新附着→功能/recall→少量调参→未插桩四点wall→小报告/STOP放在一条受控Goal。遵守A45S建议预算：下载≤6GiB（HDF5网络≤0.6GiB），新盘≤12GiB，RSS≤8GiB，GPU显存≤12GiB，CPU≤4 workers，GPU共享lock累计≤45min，≤12总实验/校准点。**这些均是待批准上限，不是现有权限**。不要在canary未经核准之前自动加NCU/NSYS/trace、第二数据集、模拟器、硬件修改或holdout。
- **结果筛选：** software AUTO与校准SMALL同recall且差异稳定→只保留software/census性能现象；下一阶段资源因果单独讨论。否则如无合法输入/运行条件或强软件已足够，正常STOP。点云稀疏卷积仍为后备，没有自动启动工程。

## 5. 范围边界

本审查的Git、数值、代码与官方文档均为只读；没有109/174/164登录、模型/CPU/GPU执行、依赖下载、shared lock、历史改动、GPU机制或新holdout。论文引用和作者源码都不能替代将来的本机实际测试。A26GR1、A45H、A45S、C16、AWMA历史权威保持不变。