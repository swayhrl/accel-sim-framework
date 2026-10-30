# 程序特性与缩减审阅 V1

本文件只报告实际读取的源码与当前小元数据，不启动GPU、不修改原输入历史。冻结153行/115 binary，当前ledger1项整体闭合/152项未闭合；本文分析不增加完成数。所有新缩减仍由主Lane接受方案、冻新身份并执行验证。

最重要的边界：保留N/分配大小不等于保留实际访问工作集；算法循环、跨阶段依赖、收敛与时间演化不能按计时重复删除。

## 优先复用，避免重采

当前已存在完整原空间scan R2/all17（66 launches、182048256 records），CUDA118 aligned R2（24/60755776）、transpose R2（24/18874368）、convolution R2（6/67903488）。两个smallscan仅工程入口；SDK429版本不是CUDA118同父。actual counts来自对应ASSET原字段，不由源码冒充。

## SCAN_DEFAULT

uint4读取、CTA共享扫描、short单kernel/large三阶段

**循环决定：** iCycles100可减为2，保持同输入覆盖输出；全17length与offset倍增/三阶段必须保留

**损失：** 减少重复丢热态；删length改变同步深度；减N改变访问工作集

**用途：** 原容量与全case研究优先既有R2

**计数／成本依据：** 源码17case=9short+8large，每cycle33launch，100轮3300；不是17kernel

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/2_Concepts_and_Techniques/scan/main.cpp；SHA256 fcc83b0d651fb07927654f9c4a1576135eb650459dd7611fb12c03aee7c15402；行 44-84, 130-168。

## SCAN_R2_ALL17

原N6815744/seed2009/全17length

**循环决定：** 已接受host重复100→2，无需重采；保原空间与全部length

**损失：** 丢98轮计时/稳态，不丢这17case

**用途：** 原空间机制研究比pilot更合适

**计数／成本依据：** 实际public66launch/182048256records/333216CTA

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/2_Concepts_and_Techniques/scan/scan.cu；SHA256 4eb9723c93d98fd792461f3949ffdae5aca962d3b1ab1b73ce104ee652b24d01；行 46-164, 170-177, 232-264。

实际公共身份：SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1_ORDINARY_V1；binary SHA 47b3c71bccbab917fd5c358e29d5d529b013a5e7d47c7071658f18fc28a6f999；argv ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/scan_repeat_only_R2_20261029_v1/build/scan_repeat_only_R2_sm89"]。

## SCAN_PILOT_SHORT

N262144/L1024/256短数组/iter1

**循环决定：** 独立新profile非default等价；保选定短扫描完整CTA

**损失：** 丢16length/26倍batch/原容量/重复热态

**用途：** 轻量工程兼容、局部机制，不代原容量

**计数／成本依据：** 实际1kernel/229376records

源码：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/scan_small_research_profiles_20261029_v1/scan_profile_config_v1.h；SHA256 8a9ca43d42aacf06f5fd9a07156c0842d904bd1d6750f0ff92938a04f9ff8383；行 27-45。

实际公共身份：SCAN_SMALL_SHORT_N262144_SEED2009_ITER1_PILOT_V1_ORDINARY_V1；binary SHA 0bcb102ac67c4402eafdb35aa19808cfc52e7a72a3737b06b67ff2f0a62fbc64；argv ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/scan_small_research_profiles_20261029_v1/build/scan_research_small_sm89", "--profile=short", "--elements=262144", "--seed=2009", "--iterations=1", "--device=0"]。

## SCAN_PILOT_HIER

N262144/L16384/16长数组/iter1；top size16

**循环决定：** 独立新profile非default等价；局部scan/top scan/uniform update三阶段全保

**损失：** 丢其它length，尤其最大top size256的同步/共享跨度

**用途：** 层次扫描入口；不是最大case代表

**计数／成本依据：** 实际3kernel/272200records

源码：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/scan_small_research_profiles_20261029_v1/scan_profile_config_v1.h；SHA256 8a9ca43d42aacf06f5fd9a07156c0842d904bd1d6750f0ff92938a04f9ff8383；行 27-45。

实际公共身份：SCAN_SMALL_HIERARCHICAL_N262144_SEED2009_ITER1_PILOT_V1_ORDINARY_V1；binary SHA 0bcb102ac67c4402eafdb35aa19808cfc52e7a72a3737b06b67ff2f0a62fbc64；argv ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/scan_small_research_profiles_20261029_v1/build/scan_research_small_sm89", "--profile=hierarchical", "--elements=262144", "--seed=2009", "--iterations=1", "--device=0"]。

## ALIGNED_CUDA118_R2

约50MB grid-stride copy/12 packed或aligned类型

**循环决定：** host32→2可缩，覆盖同输出；类型12种及pos覆盖全空间不能删

**损失：** 丢长时带宽/缓存热态；packed QA不证明padding全字节

**用途：** 对齐/宽度/coalescing对照；独立revision

**计数／成本依据：** 实际24kernel/60755776records/effective49999872B

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/6_Performance/alignedTypes/alignedTypes.cu；SHA256 de74fd994fda7ca43f9ded9454cdf85074ccd1698f86cb5e8b41e1835ebb3c6c；行 134-155, 168-196。

实际公共身份：CUDA118_ALIGNEDTYPES_MEM49999872_GRID64X256_TYPES12_REPEAT2_OBJECTLINK_V2_ORDINARY_V1；binary SHA 4e4b92b56342c2c6d5e228b1f7f399035c5eba0735b31254d3fcde8926e99bc7；argv ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/aligned_repeat_only_research_20261029_v1/build_object_link_a002/alignedTypes_repeat2_object_link_sm89"]。

## ALIGNED_SDK429_R2

官方4.2.9不同source/ELF，12类型约50MB

**循环决定：** host32→2；12type/原空间/packed字段QA

**损失：** 不与CUDA118转移资格，原RAW384launch未重标POST完

**用途：** 需本版本新QA/采集；不重编已有新binary

**计数／成本依据：** 源码预计24kernel，未据此冒实际

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/toolchains/sdk429_unpacked/sdk/C/src/alignedTypes/alignedTypes.cu；SHA256 c70e8073789dfd641212f59d7e83786270c63dce96de67b09ba03ec23abd801d；行 269-295, 306-336。

## TRANSPOSE_CUDA118_R2

8variants：copy/shared/naive/coalesced/padded/diagonal/coarse/fine

**循环决定：** host100→2；warmup1与8variant/完整tile

**损失：** 丢98轮热态；coarse/fine gold=h_odata原自比弱点仍在

**用途：** coalescing/bank/camping机制，非全8数值强证明

**计数／成本依据：** 实际24kernel/18874368records；1024²/tile16

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/6_Performance/transpose/transpose.cu；SHA256 dcf3aed1fa38fb0e32f197ad4a9b4e56b228951509145eb614315451583a5580；行 88-112, 132-186, 492-579。

实际公共身份：TRANSPOSE_CUDA118_REPEAT2_ORIGINAL1024_OBJECTLINK_V2_ORDINARY_V1；binary SHA f1acafdc1220275c2a99ef201fa11d6ef2e9684dc6435f9354d6b295e1466608；argv ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/transpose_repeat_only_research_prepare_20261029_v1/objectlink_v2/transpose_cuda118_repeat2_OBJECTLINK_V2"]。

## TRANSPOSE_SDK429_R2

8variants且host/inner双测量，非CUDA118同父

**循环决定：** host100→2及最终kernel inner100→2，非host-only；warmup1/8variant/tile load-barrier-store

**损失：** 丢长kernel内部重访与外部统计，原816未重标POST完

**用途：** 独立SDK429原空间profile

**计数／成本依据：** 源码32=8×(1+2+1)，最后8个各内部2轮

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/toolchains/sdk429_unpacked/sdk/C/src/transpose/transpose.cu；SHA256 839fa0efc2abae36e5b7179c0ff02fd46bd052b9ec69425336e4583e39bfd4eb；行 197-226, 254-309, 614-699。

## CONV_R2

3072²两步row→column/shared tile+halo，固定半径8

**循环决定：** host16→2；-1原warmup保留；row/column/halo与半径累加必须保留，非递归图像滤波

**损失：** 丢14轮稳态；改image/halo改变边界与工作集

**用途：** 已有R2复用，不重采

**计数／成本依据：** 实际6kernel/67903488records

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/2_Concepts_and_Techniques/convolutionSeparable/main.cpp；SHA256 cafadb44d0f60e7607e628f857733f119490c6c7016b5732406b344a79e10a15；行 64-118, 137-150。

实际公共身份：CUDA118_CONVOLUTION_SEPARABLE_ORIGINAL_3072_REPEAT2_V1_ORDINARY_V1；binary SHA 69d956ee76196128a47851881c424f6fafdc7482425d19382d243c685f6395e7；argv ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/conv_repeat_only_research_prepare_20261029_v1/build/convolutionSeparable_repeat2_sm89"]。

## STREAMS_R2

N16M int/64MiB，4分区streams+default，inner5累加/事件/async下载

**循环决定：** 两个host nreps100→2；结果2500→50需新QA；inner5、4流/分区/事件必须保留，不把内循环当无损冗余

**损失：** 丢98轮累计状态/热态；工具flush扰动原物理重叠

**用途：** 源级HB与单kernel机制；整App并发需consumer

**计数／成本依据：** 实际11launch/141557760records，压缩2821375861B；custom非ordinary7

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/0_Introduction/simpleStreams/simpleStreams.cu；SHA256 109f9b030162d8da88fac96af55d856090f34ae84840af5b3bad75f8c1446ab6；行 78-84, 192-274, 369-428。

## MULTICOPY_CUDA118

N4M int、4缓冲轮转、当前compute/下一上传/当前下载，event代际复用

**循环决定：** 保现nreps10；10→8省少，已有RAW不值得默认重采；inner5和roundrobin/event关系保留；inner是重复写非累加但影响compute-copy比

**损失：** 1或2轮会丢四流复用/代际；逐kernel不证明HB

**用途：** 复用完整逐kernel资产；不主张物理重叠

**计数／成本依据：** 每版本实际22kernel/144179200records

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/0_Introduction/simpleMultiCopy/simpleMultiCopy.cu；SHA256 57e64633bc80a890345ff833bf5a23fc90a24b5cf3c02baf4d9ca6a6169c8434；行 58-89, 296-346。

## MULTICOPY_SDK42

SDK4.2-v3独立source/ELF，同22计数不等SHA同输入

**循环决定：** 保10轮，至少8轮才有4流两次复用；保内5及流事件复用

**损失：** 不可转移CUDA118资格

**用途：** 已有逐kernel完整资产，HB明确缺口

**计数／成本依据：** 实际22kernel/144179200records

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/sdk/4.2/simpleMultiCopy/simpleMultiCopy.cu；SHA256 848c7232935abc04fbf5519ca155e89bcb7e8218eb0e80e12c889b1d60b89ddc；行 176-207, 425-457。

## MODERN_K0_LEGACY_ALIAS

旧七个split -kernel N参数实际都选0（原helper+ELF证据）

**循环决定：** 先实际语义去重，不能默认七算法；更正=6需新profile，不写旧历史

**损失：** 更正参数改变算法，不能以k6完成旧7

**用途：** 按实际kernel0/输入同一性分组

**计数／成本依据：** CLI/ELF为证据，非七profile已采证明

源码：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/modern6_repeat2_source_prepare_20261030_v1/reduction.cpp；SHA256 e25585f7cb2dc2ccd32861cf4457a43ddfdae4ff242f33d7ee11c256047ce2c9；行 242-302。

## MODERN_K6_R2

N16M int，grid64/block256首级+32thread末级；CALL/RET/WARPSYNC域

**循环决定：** 仅runTest testIterations100→2，shmoo未执行100不动；warmup及while s>threshold的64→1数学末级保留

**损失：** 丢98轮噪声/热态/平均计时；ISA需求仍在

**用途：** 新的归约/同步代表profile；非旧7完成

**计数／成本依据：** 源码5launch/2D2D/194CTA/1538warps；实际计数须新observer

源码：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/modern6_repeat2_source_prepare_20261030_v1/reduction.cpp；SHA256 e25585f7cb2dc2ccd32861cf4457a43ddfdae4ff242f33d7ee11c256047ce2c9；行 242-302, 504-513。

## LUD256

blocked LU16，diagonal/perimeter/internal依赖与递减负载/shared tile

**循环决定：** offset不是timing重复，不能删；tile内消元/dot16及全部offset依赖必须保留

**损失：** 减N/offset丢尾阶段/负载递减/容量；单CTA不代表全分解

**用途：** 共享复用与实测CALL-terminal机制；入口仅局部

**计数／成本依据：** 实际46launch/10056warps/1014768rawrecords

源码：/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/lud/cuda/lud_kernel.cu；SHA256 fe3d0a5f06c82947f54cbf6fd9a75342b61263808a1587ead929fc3f8763fdc0；行 22-51, 167-205。

## KMEANS400

400×34真实文件/5中心/SoA invert一次/tex1Dfetch，CPU更新中心并收敛

**循环决定：** 16次实际迭代不可默认减2，delta/threshold驱动真实状态；维度/类数/分布/invert/纹理资源必须保留

**损失：** 提前停丢收敛与后期分歧；AoS替SoA实际地址错误

**用途：** 线性TLD精确代表，不推广filtered/opaque array

**计数／成本依据：** 实际QA16iter，观察17launch；完整trace/consumer另行

源码：/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/2.0-ft/kmeans/kmeans_clustering.c；SHA256 e176c35ce94545f4619a249d209570b0a27d945a882fe1d8af8ece6e105eef22；行 105-131。

## SYR2K2048

warp j相邻，a[i,k]/b[i,k]uniform；a[j,k]/b[j,k]stride8192B；48MiB arrays

**循环决定：** k2048是真rank2k数学，不能删作重复；M/N与完整k累加

**损失：** 缩k改结果/触及行跨度，缩N改容量

**用途：** 可轻量完整CTA入口，原容量结论保N/M

**计数／成本依据：** 131072warps×2048=268435456 warp-k，非动态记录计数

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_v3/polybench-gpu-1.0/CUDA/SYR2K/syr2k.cu；SHA256 91c377db88661effcb089df5e612bf0bdc4dbaae0c3304734184ba7f3a105f64；行 26-31, 120-133。

## 2MM2048_REPAIR

C=A*B再E=C*D，naive全局uniform/相邻读；5矩阵80MiB

**循环决定：** 两k循环与两kernel不是重复；阶段2必须吃真实C；修初始化是新身份

**损失：** 少k改数学；随机中间C不能冒原第二阶段

**用途：** 两阶段/容量；原旧未定义输入不继承修复资格

**计数／成本依据：** 源码总536870912 warp-k，两kernel；动态记录未知

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_v3/polybench-gpu-1.0/CUDA/2MM/2mm.cu；SHA256 7e637b6e0ddfe6f0e95adcd19caf75d20e43eeede2611bf90e74f6e2da651279；行 25-33, 109-138, 195-204。

## GEMM512

此revision512³、无shared tiling，A laneuniform/B相邻j/C相邻写，3MiB arrays

**循环决定：** k512是真dot不可删；N与k/原alpha beta

**损失：** 缩k/N改数学与缓存，不是统一2048的PolyBench

**用途：** 全局复用/算术代表，非高性能tiled GEMM

**计数／成本依据：** 源码8192warps×512=4194304 warp-k；1kernel

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_v3/polybench-gpu-1.0/CUDA/GEMM/gemm.cu；SHA256 39b62b7ac94db98149557d14e86dd0beee65b43e42dd2b91c80eb68aa17c081f；行 26-40, 125-138。

## 3DCONV256_REPAIR

固定15项邻域表达式含重复地址，不泛称标准27point；host逐i平面

**循环决定：** i1..254是输出平面，非benchmark；另设ROI须新用途；j/k边界与邻域公式/真实halo

**损失：** 即保N而只选plane，实际touched工作集也变slab，丢volume容量/跨plane复用

**用途：** 连续3+plane ROI仅局部机制提案，不代whole-volume

**计数／成本依据：** 源码254kernel/65024CTA/520192warp；A+B128MiB

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_v3/polybench-gpu-1.0/CUDA/3DCONV/3DConvolution.cu；SHA256 4c055125a6287b93da4dc227ad80ab884252fb74b6a17c5eadb1480f6dd57206；行 26-33, 122-169。

## FDTD2D_V3_V4

ex/ey/hz三相互依赖，fict[t]边界时变；旧v3有已记录stride/halo域问题

**循环决定：** tmax500不是benchmark；若2步必须新short-horizon身份；先用修好v4；三步顺序和合法边界保留

**损失：** 丢长程演化/边界数值/热态；lateROI需真实前态，不造快照

**用途：** 固定v4入口或明确两步机制，不代表500步数值

**计数／成本依据：** 旧source500×3=1500kernel，仅计数不给v3正确性

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_v3/polybench-gpu-1.0/CUDA/FDTD-2D/fdtd2d.cu；SHA256 0083d95dd5655d2b4a74eae063163a8b23478420fd9b8f8c3e6438a51d3de040；行 25-35, 130-169, 198-205。

## FDTD3D_CUDA118

radius4；xy shared与z register rolling，timestep pingpong；defaultDim随GPU memory

**循环决定：** default5 timestep是真演化，可另定义2步但非无损重复；z遍历/radius4/rolling window必留

**损失：** 改z改空间reuse；5→2丢演化；不能以名字假定固定尺寸

**用途：** 必须冻结实际dim/step，才可容量对照

**计数／成本依据：** source default5/radius4，动态dim/记录未测

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/5_Domain_Specific/FDTD3d/src/FDTD3dGPU.cu；SHA256 ad3e9df8caa5a1572b423d1d9719df54d064b0faf7aecd598bf2cae5ee74bf1e；行 65-89, 186-205。

## 批量推进建议

1. 直接使用已有scan/all17、CUDA118 aligned/transpose/conv R2与其完整CTA样本；不再为论文式全量性能重放或重复证明而重采。
2. 收完已采simpleStreams完整源、两份MultiCopy与LUD的实际POST/归档/风险CTA接入；stream HB、物理重叠与普通格式分开判定。
3. SDK429 aligned/transpose用新精确身份完成本版本QA及采集，不沿用CUDA118的资格；保全部类型/变体。
4. kmeans保原400x34/5中心/收敛16次，先用实际线性TLD数据建立严格consumer，不裁算法迭代；modern k6 R2保真实partial reduction和同步，旧七split argv按实际kernel0审别名。
5. 对SYR2K/2MM/GEMM先用完整CTA做工程入口与精确成本试验；k是真数学不能删。3DCONV只选少量plane、FDTD只选少量timestep都必须单列新用途与工作集/演化损失，不能包装成无损重复缩减。
6. 维持完整153台账；相同ELF不等argv/输入相同。原始缺陷版本与已修新binary分开，未测动态计数/总成本保留unknown。

本Lane无新GPU/模拟/服务、无scope/工具激活、无payload正文哈希；只SHA小源码与元数据。没有授予科学或性能资格。

## 精确身份补表（V2）

旧family输入列表不是本profile等价声明。新冻结job仅证明声明，不证明执行；已Root实际接受另标。

- MODERN_K6_R2：{"binary_sha256": "012e461ee371ec19892fbe42fca3c7dd9240bc1b604e1fe26f59ef392ea9b92f", "argv": ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/modern6_repeat2_source_prepare_20261030_v1/nvcc_host_sm89/modern_reduction_kernel6_repeat2_candidate", "-kernel=6", "-type=int"], "input_profile": {"CTAs": 194, "D2D_bytes_each": 256, "D2D_copies": 2, "HtoD_source_bytes": [67108864, 256], "N": 16777216, "benchmark_iterations": 2, "block_full": [256, 1, 1], "final_partial_launches": 2, "full_input_launches": 3, "grid_full": [64, 1, 1], "kernel": 6, "physical_threads": 49216, "physical_warps": 1538, "total_launches": 5, "type": "int32", "warmup_launches": 1}, "stage": "SOURCE_CPU_PLAN_COUNTS_NOT_ACTUAL_NEW_GPU_COUNTS", "ref": {"path": "/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/actual_input/modern6_repeat2_source_prepare_20261030_v1/ROOT_MODERN6_REPEAT2_CPU_BUILD_AND_LOOP_REDUCTION_REVIEW_ENTRY_V1.json", "bytes": 5884, "sha256": "38b0c5b9dfb648f760306083d08abd32147c8f2fd96b82c557dcae43f3b122cb"}}

- ALIGNED_SDK429_R2：{"binary_sha256": "f8a07c78171d88c0609a30ebf000a78781f9736651ed21bc4110771437d8abcf", "argv": ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/remaining_asset_completion_goal_20261030_v1/multistream_CPU_build/sdk429_alignedTypes_repeat2_v1/build/alignedTypes_repeat2_sm89"], "input_profile": {"family": "alignedTypes", "parameters": {"MEM_SIZE": 50000000, "effectiveMemorySize_required": 49999872, "NUM_ITERATIONS": 2, "grid": [64, 1, 1], "block": [256, 1, 1], "types": 12, "expected_launches": 24, "warmup": "ORIGINAL_NONE", "input_formula": "uchar((i&0xff)+1)", "QA": "ORIGINAL_PACKED_FIELDS_ALL12_TYPES; NO_PADDING_OR_BITWISE_CLAIM"}, "expected_kernels": 24, "declared_launch_count_not_actual_observation": true, "source_version": "SDK4.2.9_HOSTCOMPAT14_REPEAT2_NOT_CUDA118"}, "stage": "FROZEN_JOB_DECLARATION_NOT_GPU_SUCCESS", "ref": {"path": "/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/remaining_sdk429_RAW_repeat2_nativeQA_prepare_20261030_v1/runtime/jobs/SDK429_ALIGNEDTYPES_ORIGINAL50MB_TYPES12_REPEAT2_V1.json", "bytes": 5500, "sha256": "a89392e6733e7e6f15c3d2aca23986427e158ad6f14c99e8359060e0eec1270b"}}

- TRANSPOSE_SDK429_R2：{"binary_sha256": "869eb6f02a58d7cd121edb8fb16fab6d61a997d9870141f12ac97dd11386d24d", "argv": ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/remaining_asset_completion_goal_20261030_v1/multistream_CPU_build/sdk429_transpose_repeat2_v1/build/transpose_repeat2_sm89"], "input_profile": {"family": "transpose", "parameters": {"matrix_required": [1024, 1024], "tile": 16, "block": [16, 16, 1], "grid": [64, 64, 1], "NUM_REPS_outer": 2, "NUM_REPS_inner_experiment_argument": 2, "warmup_per_variant": 1, "variants": ["copy", "copySharedMem", "transposeNaive", "transposeCoalesced", "transposeNoBankConflicts", "transposeCoarseGrained", "transposeFineGrained", "transposeDiagonal"], "expected_launches": 32, "launches_per_variant": ["warmup inner1", "outer0 inner1", "outer1 inner1", "inner_timing inner2"], "input_formula": "float(i)", "QA": "ORIGINAL_COPY_GOLD_AND_TRANSPOSEGOLD_BOTH_PHASES; COARSE_FINE_SELFCOMPARISON_WEAKNESS_RETAINED; tolerance0.01/0"}, "expected_kernels": 32, "declared_launch_count_not_actual_observation": true, "source_version": "SDK4.2.9_HOSTCOMPAT14_REPEAT2_NOT_CUDA118"}, "stage": "FROZEN_JOB_DECLARATION_NOT_GPU_SUCCESS", "ref": {"path": "/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/remaining_sdk429_RAW_repeat2_nativeQA_prepare_20261030_v1/runtime/jobs/SDK429_TRANSPOSE_ORIGINAL1024_OUTER2_INNER2_ALL8_V1.json", "bytes": 6485, "sha256": "dddf67a87b76d8c47ef8b78551d0f300a631a25695c269af0d68867f44c07af1"}}

- LUD256：{"binary_sha256": "8e7bab5264010f03c8b8c1fa31379d6baa5ad6fc3480027f55f4c76ad44a0753", "argv": ["/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/lud/cuda/lud_cuda", "-s", "256", "-v"], "stage": "ROOT_ACTUAL_UNINJECTED_QA_OWNED_ACCEPTANCE", "ref": {"bytes": 2792, "path": "/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/isa_lud_cfi5_native_pipeline_20261030_v1/runtime/ROOT_LUD256_ACTUAL_UNINJECTED_QA_OWNED_ACCEPTANCE_V1.json", "sha256": "2c94d591755ec0aeb4dcc591d86454cb8fa54233e162daaaec66629dbf6b4c94"}}

- KMEANS400：{"binary_sha256": "f39660593eab12675634c447a201a3ef12ae30e82dcabb5e1117534a38c95bed", "argv": ["/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/bin/linux/release/kmeans-rodinia-2.0-ft", "-i", "data/400.txt", "-g", "data/400-result.txt", "-o"], "stage": "ROOT_ACTUAL_UNINJECTED_QA_OWNED_ACCEPTANCE", "ref": {"bytes": 3200, "path": "/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/tex_kmeans400_nativeQA_prepare_20261030_v1/runtime/ROOT_KMEANS400_ACTUAL_UNINJECTED_QA_OWNED_ACCEPTANCE_V1.json", "sha256": "91cba358a5f3c9964649b2bdef405c7bd673c0ea80788125e6ce9ab3c56f995a"}}

- STREAMS_R2：{"binary_sha256": "f9f09cad9e265e54569a760982ea9c9f232ba964748e19dff56be46f2d55d3cc", "argv": ["/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates/remaining_asset_completion_goal_20261030_v1/multistream_CPU_build/simpleStreams_repeat2_v2/build/simpleStreams_repeat2_sm89"], "stage": "ROOT_FULL_CUSTOM_SOURCE_POST_ACCEPTED_NOT_ORDINARY7", "ref": {"path": "/root/share/mnt164/huangrulin/traces/receipts/remaining_asset_completion_goal_20261030_v1/root/ROOT_SIMPLESTREAMS_R2_FULL11_CPU_POST_SOURCE_FINAL_ACCEPTANCE_V1.json", "bytes": 3505, "sha256": "958cf7f82405c6b18ebc5b45af8483b35eb9d191adcac44f0a2966ef5c08a437"}}

本报告未对所有历史ELF重新证明编译来源；原始源码SHA/行号与对应实际ASSET/job原字段分别保存，不跨套件/argv推资格。
