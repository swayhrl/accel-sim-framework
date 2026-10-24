# CUDA/PolyBench 4080资产准备与原生核查交付

本临时子Lane完成源码、输入分母、私有构建、原生运行和批量采集候选清单；未生产正式trace，未启动模拟器，未改变EP/DTC/AWMA科学资格。正式采集、164封存和公共入口由总采集Lane继续执行。

## 固定来源和分母

|来源|精确身份|核查范围|
|---|---|---|
|已有SDK4.2源码快照|`b059fdae25c2aabf737486aada743fca114469ce`|73目录；594个Git blob全匹配|
|完整NVIDIA GPU Computing SDK4.2.9|官方安装原包SHA `b6a53afcf8f8422b5075aa37cec6730b0b9896d50867ee9105da05d62e95b8bb`，152436489B|C/src实际82目录，旧快照漏9项；仅无执行解包，未安装系统软件|
|现代CUDA Samples映射|`81992093d2b8c33cab22dbf6852c070c330f1715`，v11.8|旧73名称对应的完整有限测试分母103调用；3615个原包Git blob全匹配|
|PolyBench/GPU1.0|`dad09cb0487845edc7524ded814c6cde9f0ef6a1`|15程序完整默认尺寸；299个Git blob全匹配|

现代版本是明确记录的新实现，不能替旧4.2或历史路径9.1标签证明源码、参数或数值完全相同。82个SDK目录也不能全部算成可产生常规SASS的工作负载：deviceQuery/Drv无kernel，bandwidthTest主要是copy API，simpleAssert是预期断言诊断，simpleP2P需要两GPU，两个图形程序仍需合适的非交互GL上下文。`MonteCarlo`与`MonteCarloMultiGPU`以及Runtime/Driver实现均保留实现身份。

## 已实际执行

- 现代映射73/73真实ELF均已构建；有检查Makefile“waive且exit0”的陷阱，没有把它算成成功产物。72项包含静态sm89，matrixMulDynlinkJIT有独立动态JIT代码资格要求。
- 旧73快照当前50项已产ELF，其余23保留编译/依赖/API移植状态；它们有现代对应实现，不等于旧版本已移植成功。完整官方额外9项均已产ELF，因此旧/官方来源合计59项。版本路线表逐一列82行，79个程序名称已有某个明确版本的exit0原生记录；剩余2个GL上下文和1个P2P硬件需求不是永久exclusion。
- 103个现代预定义/有限默认调用和Scan修复共104条原生队列终结。旧源码其余45个可构建默认调用也已全部终结，失败与平台限制均留存。
- 完整SDK新发现9项都构建并在4080原生执行通过；其中2项只有设备查询，另外7项包括Driver/JIT/多context/printf，不能直接继承普通producer profile。
- Poly原完整默认13项通过；FDTD-2D和GRAMSCHM原失败保留，另建完整尺寸修复输入，两项均通过。FDTD不降2048×2048×500，Gram不降2048²。源目录FDTD-2D归一为FDTD2D，避免多算程序。
- 用官方SDK4.2.9真实lena/barbara数据补通旧dct8x8、simpleTexture、simpleSurfaceWrite；不再用现代teapot当作旧原数据。
- 旧histogram选源码已有共享atomicAdd分支后通过；旧Scan补warp同步并恢复合法完整N=6815744后通过；旧threadFence修字符串device-symbol API后通过；旧eigenvalues恢复完整2048矩阵后通过。所有都是独立variant，原失败不覆盖。
- Dxtc旧完整512图仍失败，RMS12.17；独立使用NVIDIA现代同步安全device区域回移后，同官方Lena/reference RMS0.015238，小于原0.02阈值。该GPU kernel明确是新端口，不称原kernel未改。

所有运行有独立attempt、binary/source/input SHA、PID/start_ticks、退出状态和stdout。全部本Lane有限native supervisor已终结。原174源码和所有Git跟踪源码/输入字节最终复核仍全匹配。

## 数值与来源不能合并成一个PASS

原始classifier只作运行证据，不能靠“PASSED”或exit0直接赋科学资格。独立qualification与原始回执并存：

- Bicubic官方-file模式只保存图，附带reference不对应当前默认视图。我按实际源参数独立CPU计算全部512² RGB；五模式最大误差0/0/1/1/1，全部通道满足原source epsilon5。陈旧reference差异仍保留。
- ImageDenoising四模式同样只有保存图；独立全图reference比较最大误差0/1/1/1，全部通道满足原epsilon5。
- FDTD3d、HSOpticalFlow、Interval逐源码核实退出值确实传递CPU reference结果；HS完整输入L1=0.044308，小于原0.05。
- Mandelbrot/marchingCubes/volume样例日志出现mismatched但在原容差内，并不自动是失败。宽松容差本身也不等于严格数值相同。
- marchingCubes和volumeFiltering的官方-file同时被用作raw体数据输入，原调用会读reference前32768B。原调用保留；另建-volume=Bucky.raw的独立输入，所有GPU kernel不改。VolumeRender原本已分-volume，未误改。
- canonical Gram rank1产生NaN、FDTD ghost边界未初始化、旧Scan缩小N后产生零grid、旧Eigen小矩阵分支返回false等，均保留真实状态。不能把修复输入PASS写成原canonical PASS。

## 本轮修正的输入隔离问题

v1的attempt/data是指向本轮109新源码副本的目录链接。simpleTexture会写data/teapot512_out.pgm，导致私有源码副本新增输出。没有改变原174或任何Git跟踪源码/输入文件。该输出已完整保留并记录SHA；在GPU锁释放边界只终止自身等待队列，未重跑已完成12项，余33项用v2续跑。v2把manifest列出的输入独立复制进新attempt/data，输出不能写透。不能声称v1源码目录零新增；详见DATA_STAGING_INCIDENT_AND_REPAIR_V1.json。复核3615/594/299原文件均零变化。

## 交付入口

109工作根：`/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1`。

- `manifests/ALL_NATIVE_ASSET_STATES_V1.json`：全部尝试与数值、平台、capture disposition，失败不省略。
- `manifests/ALL_CAPTURE_CANDIDATES_PROFILE_PENDING_V1.json`：176个内容候选，须经过producer/consumer具体profile后才能生产，不是176个科学验收workload。
- `manifests/CUDA_SAMPLES_V118_ALL_TESTRUN_QUEUE_V1.json`：103个现代官方/有限默认调用及85个data/reference文件SHA。
- `manifests/SDK429_OFFICIAL_SOURCE_EXTRA_CANDIDATES.json`：完整82分母与漏掉9项。
- `manifests/SDK429_82_PROGRAM_VERSION_ROUTE_MATRIX_V1.csv/json`：82行版本、构建、原生与真实可达路线。名字含MultiGPU的MonteCarloMultiGPU/simpleMultiGPU已在1卡通过；simpleP2P还需第二卡且cudaDeviceCanAccessPeer实际为真。
- `native_control/`：逐attempt回执、独立CPU/reference证明、隔离问题回执和终结证明。
- `build/run_cuda_native_v2.py`：有限原生执行器；修改R后可复用，CLI为manifest与batchname。输入必须独立副本。

工具依赖均为私有目录：CUDA11.8/GCC11复用总Lane固定前缀；CCCL11.8、GL/freeglut/GLEW/X11及OpenMPI只下载/解包，未修改全局服务或停止ComfyUI。

## 下一轮完整补齐顺序

1. 采集Lane用状态清单固定每一条source/version/implementation/argv/input，不把现代映射替代旧exact身份。先完成可核普通profile全kernel常规输入，再保留独立裁剪派生及父SHA/选择规则。
2. 原始数值失败、预期断言、copy/query、CPU-only和平台缺项分别存档。需要的失败执行可采为诊断资产，不冒称正常完整应用验收。
3. TEX/TLD/SULD/SUST、shared atom/RED、BAR.WARP.SYNC、旧Driver launch API、JIT、多stream/context、库加载架构均须相应语义profile。4080身份由GPU UUID证明；实际库cubin可合法sm80/86，保留实际ISA，不改header89。
4. 两个当前需GL context的程序先验证独立offscreen上下文与CUDA-only trace范围，不使用GDM凭据、不修改显示服务。原生平台问题不是GPU本身不支持。
5. 大输入先冻结逐项时间/空间预算和源数据snapshot要求；完整原包、适配补丁、工具、输入、所有attempt经总Lane单流写164并独立重读。NAS封存状态不能从本报告推断。
6. 公共项目入口由总Lane发布。这里不授予EP/DTC/AWMA模拟资格，也不更改任何历史Goal、科学预算或运行配置。
