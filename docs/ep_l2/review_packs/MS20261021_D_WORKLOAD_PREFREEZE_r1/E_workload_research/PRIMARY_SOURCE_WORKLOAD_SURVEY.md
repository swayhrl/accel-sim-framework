# EP-L2有限workload扩展：一手资料审查

审查日期：2026-10-21。只阅读项目/原作者网页、发布说明及小型源码；未下载trace、构建、启动或修改中央状态。本报告是候选调研，不授予实验资格。建议按缺失机制选少量代表，不按已知F加速比筛选。

## 当前五项能支持多大结论

声明集合为Conv、CFD、DWT、SAD、Vector五个distinct workload；多kernel、多profile和重复配置不能计作新的独立workload。它们可支撑“在这五个准确输入、指定架构/配置与已接受配对中观察到的机制效果”，也可支撑有严格控制的案例归因。不能单凭五个名字推断对GPU应用总体、整个suite或所有输入规模有代表性。是否已接受仍以E终验回执为准，不能把原主矩阵四对与capacity诊断五组计划混为同一分母。这是本次科学范围判断；不存在本报告可引用的统一“至少N个benchmark”投稿门槛，故不编造最低数。

关键是补足访问行为和负例，而非先定一个更大的数量。suite、输入、算法版本应一并披露；Rodinia作者将CFD归为unstructured grid、Hotspot归为structured grid、BFS归为graph traversal，说明同为一个suite仍可提供不同结构。[Rodinia作者主页](https://rodinia.cs.virginia.edu/)

## 必须注意的新发布变化

2026-10-20官方v2.0.1将trace发布移至GitHub release assets，取消旧FTP下载路径及pre-2.0列表；第一批是H200 ML/NVBit1.8 `.tracez`，并明确剔除了部分不能模拟完成的kernel。其存在不证明老Rodinia/Parboil完整trace目前仍可公开下载，也不能直接当成本项目冻结runtime的完整应用输入。[官方v2.0.1发布说明](https://github.com/accel-sim/accel-sim-framework/releases/tag/v2.0.1)

当前README说明SASS从真实GPU采集，可按YAML运行CUDA程序；同时介绍新`.tracez`及legacy `.traceg`输出。格式可转换不等于新Hopper指令/架构语义自动兼容本项目binary。未审查兼容性前，不推荐为凑应用数引入H200 ML或重建生产模拟器。[官方Framework README](https://github.com/accel-sim/accel-sim-framework#readme)

一次网页读取的`dev/get-accel-sim-traces.py`仍返回FTP版本；这与昨日发布说明不一致，可能是分支/缓存差异。它仅证明存在旧获取脚本，不是服务器今天可用、内容完整或身份匹配的证据。[旧脚本当前URL](https://raw.githubusercontent.com/accel-sim/accel-sim-framework/dev/get-accel-sim-traces.py)

## suite与实际可用性

| 来源 | 已由一手资料确认 | 尚未证明、不能默认成立 |
|---|---|---|
| Accel-Sim GPU App Collection | 维护CUDA应用源码和统一构建；数据不在Git中，另从大学服务器获取；原项目及collection commit应同时引用。[README](https://github.com/accel-sim/gpu-app-collection#readme) | 对应数据服务器、特定旧trace包今天可取；本机输入完整；该版本在冻结binary上有效 |
| Rodinia3.1 | 作者下载页列出3.1及版本变更，也明确若干旧版本不再提供。[作者下载页](https://www.cs.virginia.edu/~skadron/lava/rodinia/downloads.html) | 网页列出下载不等于本轮已下载/验证archive；不采用其他作者“v4”改写自动替换旧版本 |
| Parboil | Collection明确集成spmv、histo、stencil、sgemm等构建目标；同一Makefile对Python2维护问题有注释。[官方collection Makefile](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/Makefile) | 本轮访问原Illinois技术报告/首页超时，未验证原数据下载；代码存在不等于完整trace可取 |
| PolyBench/GPU与PolyBench/ACC | 原作者GPU/accelerator项目提供CUDA等实现、参数化规模、初始化及结果dump；collection集成GPU1.0的GEMM/2MM等。[作者项目](https://cavazos-lab.github.io/PolyBench-ACC/)、[collection构建映射](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/Makefile) | 不把PolyBench/C、ACC和GPU1.0视作相同binary/input；编译期维度必须从对应源码与binary证据核定 |

## 候选：四类缺口，各选一个代表

以下“机制价值”是基于源代码结构的候选假设，不是已观察到的EP-L2瓶颈。实际L2命中、读写、拒绝、dirty eviction、访存并发必须由中性统计确认。

| 类别与少量代表 | 源码/语义依据 | 对EP-L2的独立信息价值与准入重点 |
|---|---|---|
| 不规则读取：Parboil SpMV；备选Rodinia BFS | SpMV读矩阵及向量、转换JDS，当前主程序调用kernel50次。[SpMV源码](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/parboil/benchmarks/spmv/src/cuda/main.cu) BFS通过edge间接访问visited/cost并更新mask。[BFS kernel](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/rodinia/3.1/cuda/bfs/kernel.cu) | 检查不规则gather、地址集中及并发占用；优先有完整输入且成本较低者。SpMV必须保存矩阵/向量具体身份、布局转换及全部50次调用；BFS须绑定图/起点和完整迭代，不能仅截一层 |
| 跨kernel迭代与写回：Rodinia Hotspot；备选Parboil stencil | Hotspot在两个温度buffer间交换src/dst，计算中共享内存复用并向global写回；参数包含grid、pyramid、迭代数、温度与功率文件。[Hotspot源码](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/rodinia/3.1/cuda/hotspot/hotspot.cu) | 补跨kernel复用/dirty生命周期；不能由“热模拟”名称断言L2瓶颈，也不能降低迭代数而沿用旧输入标签。完整trace须包含所有规定步数及host transfer |
| 密集复用与算术负例：PolyBench/GPU GEMM；备选已登记来源的Parboil SGEMM | GPU1.0 GEMM源码定义NI/NJ/NK=512、float、CPU对照与误差阈值；kernel反复读取A/B并更新C。[GEMM源码](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/polybench-gpu-1.0/CUDA/GEMM/gemm.cu) | 看大量复用/算术是否使capacity或data-service诊断收益较小，保留负结果。必须明确实现是否tiling，不能拿不同SGEMM/WMMA版本互作端点；512仅是当前公开源，不等于本地trace实际维度 |
| 高科学语义风险、非首批：Parboil histo；备选CUDA SDK histogram | Parboil histo源码同时有global与shared atomicAdd和overflow处理。[histo源码](https://raw.githubusercontent.com/accel-sim/gpu-app-collection/dev/src/cuda/parboil/benchmarks/histo/src/cuda/histo_main.cu) | 补非普通load/store的语义边界；先审核冻结runtime对实际ATOMIC/RED路径及idealized ON的科学适用性，不能把共享原子都归因于L2；分布/范围/overflow参数与oracle不可遗漏 |

Streaming已有Vector；没有证据表明缺少该类时，不优先新增transpose来凑数。上述四类中先挑**两个**最有增量且具有完整现成trace、非原子可独立资格、成本可承担的候选（优先评估Hotspot/stencil及来源完整的密集复用；SpMV/BFS只有输入与旧HOLD边界闭合后才可入选）；若第三类现成SGEMM已完整登记则可成为低准备成本替代。histo/atomic列为P2高科学语义风险：当前完整data/oracle认证可能只覆盖非原子路径，须A2/E重新审核实际ATOMIC/RED支持；源码可编译不能替代正确性或科学资格，不推荐首批。旧HOLD不因本报告升级，不推荐直接复用旧SpMV/Scan回执；BFS也不能由源码存在推断新完整输入已经就绪。此优先级不使用任何F加速比。

## 从候选到可运行的最短闭合

1. 先与本地inventory合并：绝对路径、GPU/CUDA/tracer与源码commit、参数、数据文件身份、完整kernel清单和host memcpy记录。外部网页不代替input provenance。
2. 完整应用语义单独审核：不删除失败/慢kernel，不以ROI/某kernel重复伪称full application；迭代与初始化、输出oracle绑定。任何子集只能单独标subset，并另走科学批准。
3. 用可复用的输入头部/manifest及已有中性统计预估成本、结果增长和资源需求；本轮未测候选walltime、instruction总数、RAM或trace总量，全部标UNKNOWN，不给虚构小时数。
4. 独立资格必须覆盖实际新profile/runtime与所有64slice、完整指令、真实exit0、drain及计数闭合；既有五项输入资格不能自动移植到新输入。通过后才提出有限精确新增配对范围，保留现有主结果及所有负例。

不建议现在clone全部suite、下载整套trace或盲跑网格。先解决完整性、身份、覆盖增量和可承担成本，再由唯一E中央流程接纳新科学范围。
