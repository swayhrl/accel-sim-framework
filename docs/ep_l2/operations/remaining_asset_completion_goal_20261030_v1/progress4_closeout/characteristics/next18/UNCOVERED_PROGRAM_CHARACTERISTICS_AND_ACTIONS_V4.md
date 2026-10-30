# 第二批程序特性与行动审阅 V3

本批18个profile，避开第一批22profile重复。源码事实与旧ELF当前SHA、编译来源、动态支持和完成资格分开；本批未授予任何新执行/科学资格。“快路径”是预估工程依赖少，不保证无新ISA，也不填动态record数。

## 2DCONV（优先级1）

4096² float A64MiB+B64MiB，9项邻域，单kernel，j方向warp相邻；无shared tile

循环/缩减：无benchmark重复可缩，保9邻域/边界/原N；空间缩减必须另身份

原QA及弱点：原interior percentDiff阈值0.05且ep_correctness_fail累积；不比较未写B边界，非全数组强QA

计数/成本：1kernel仅源码预计；sync HtoD A64MiB，已有CPU构造hash候选，须actualsource/lifetime

最短下一步：最快候选：精确C8 sync域+原NativeQA→loadedcode→boundedcapture；不能凭primarygate说新ISA已全清

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_v3/polybench-gpu-1.0/CUDA/2DCONV/2DConvolution.cu；SHA 9f5c892b1518dbea1bc1206f10bb34ae4fc79f29cf1f9b3153d2515413cad9a8；行27-32,62-95,109-148。

## ASYNC429（优先级1）

N16M int，64MiB pinned a零值，GPU memsetFF后同stream0 HtoD0→increment26→DtoH→event

循环/缩减：无GPU benchmarkloop；CPU eventQuery等待非多余GPU循环，不改sync替代其异步语义

原QA及弱点：correct_output逐N检查26；原shrQAFinishExit；需实际非waive/错误而非exit0泛判

计数/成本：1kernel源码；HtoDAsync hosta直到stop完成无改写；255setup被同流HtoD覆盖

最短下一步：最快async代表：原ELF已CPU合同，需async实际success/order/allocation/completion源域，不能伪SYNC C8

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/toolchains/sdk429_unpacked/sdk/C/src/asyncAPI/asyncAPI.cu；SHA 9028f696a66e6d27bdd16a48b6ba584cfc9ba95d7c165ea721c84947adc4b735；行193-209,223-256。

## CPP11（优先级2）

真实warandpeace corpus3223503B；kernel1 gridstride+atomic计数，kernel2 Thrust device计数覆盖count

循环/缩减：两次top-level launch不是重复，应保；内部scan全corpus是算法输入遍历，不能随意截前4KB冒原分布

原QA及弱点：原程序只打印count且exit0，无CPU断言；已有新scalarQA变体860b检最终107310，不授中间/全branch

计数/成本：源码2个top-level，device-Thrust是否额外child需实际census；已有新ELF待原corpus NativeQA

最短下一步：快路径是已有修复变体而非重写oracle；需精确文件staging、memset count、device执行域及currentmap

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/modern_complete_build_v1/cuda-samples-11.8/Samples/0_Introduction/c++11_cuda/c++11_cuda.cu；SHA c8f0cf6d9508f776f1a2439cab84cbfee178a1877d3b96921c4198a853149ffa；行54-79,96-139。

## QUASI429（优先级2）

N1M/3维方向表，QRNG整数bit31循环与inverseCND，symbol table初始化

循环/缩减：numIterations20两测量段各含warmup-1，可新20→2；位循环/方向表/整个N不删

原QA及弱点：原第一QRNG L1只打印；最后inverseL1<1e-6控制退出，不能说双强QA

计数/成本：源码42=(20+1)×2→6=(2+1)×2；新计数未实测；actualsymbolwrite/lifetime必须取证

最短下一步：高收益重复缩减候选；先复用已CPU表/原reference，不新oracle；Root审批后新ELF身份

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/toolchains/sdk429_unpacked/sdk/C/src/quasirandomGenerator/quasirandomGenerator.cpp；SHA 47dbc9336a606e986f230c45b27dfd32d321d6b6bf077ec8af6953ec2de88d64；行121-142,153-208。

## NW2048（优先级2）

2048×2048 DP矩阵，BLOCK_SIZE波前tile，上半diag增长/下半收缩，int penalty10/srand7

循环/缩减：两个diag循环是真依赖，不是benchmark；不能少做i；保tile内部DP

原QA及弱点：无独立CPU数值比对；TRACEBACK需按actual编译宏判断；源执行/traceback不等新oracle

计数/成本：若actualBLOCK16，255launch/16384tile仅源码条件推导；需真实blockdim核而非header猜

最短下一步：sync输入/固定seed7候选；先Native执行+actualcompiledblock/image，原16.8MiB²两个数组，内存可行

源码：/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nw/needle.cu；SHA 6152a04e5cd37a0c3f78efdc5cb4d8269bd10694840c23cb9b8345ac525962ee；行109-138,146-172。

## HUFFMAN（优先级2）

文件test1024_H2.206587...固定熵分布→host codewords/lengths；shared LUT256与变量码长/atomics，scan/pack阶段

循环/缩减：NT10是同输入encodebenchmark，可提案10→2；scan/pack前缀依赖和数据熵不能删

原QA及弱点：源TESTING分支compare_vectors返回被忽略，仅打印PASS/FAIL；actual旧ELF编译flags未本Lane重证；原已执行QA应按真实弱范围

计数/成本：预计少8次encode；scan递归/pack计数取决实际block与宏，不乱报总数；已有5images/8380map

最短下一步：原ELF可优先，但符号/输入域和actualCALL/control须取证，不把static45sites当dynamic资格

源码：/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/huffman/main_test_cu.cu；SHA 09789aa2cf33de35836d5824934870d1d81b090140645edd5af9f63a2658e9bd；行41-60,117-171。

## HOT3D（优先级2）

512²×8点，z register滚动、x/y邻居global，thermal100时步pingpong，GPU约24MiB三数组

循环/缩减：100是物理演化不可当benchmark；另2步short-horizon需明确丢演化/新profile

原QA及弱点：3D.cu198–203只打印RMS无阈值return0；swap后导出tOut/CPUanswer存在奇偶前态域，不授100步最终oracle

计数/成本：原100次launch仅源码；grid8×128/block64×4由opt1，actualgeometry仍需核

最短下一步：原map2images658已CPU闭合且原NativeQA有弱回执，可做精确input/lifetime及boundedcapture；不默认新oracle

源码：/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/hotspot3D/opt1.cu；SHA f8987fd50ab42b57303bc98c3bc4d91c81346573275be8967b20c89c66fe1257；行7-54,71-96。

## PARTICLEFILTER（优先级3）

128²视频10帧/1000particles，CPU likelihood/CDF/normalization→GPU resampling，RNG/state逐frame延续

循环/缩减：frame循环非benchmark；-z10→2是新短序列，不是同工作负荷；NP/Nx变访问分布

原QA及弱点：原execution/坐标输出不是CPU重采样强oracle；旧time-seed+signedoverflow已CPU证据，优先新seed7/wrap32变体8afdc

计数/成本：源码Nfr10有9frame迭代；实际launch数未测，findIndexSeq早停依CDF/分布，不能估固定records

最短下一步：先新变体Native execution，随后each-frame actualHtoD epochs；新seed不完成旧time-seed输入

源码：/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/particlefilter/ex_particle_CUDA_naive_seq.cu；SHA 927a58af8122dced9e336d1850f5a749874b76b0c4bba1f5e0cf3ef596049680；行58-89,174-193,473-560。

## NBODY_QA（优先级3）

qatest比较一步update，不是benchmark10；4096默认条件需actualbind；allpairs/sharedbodytiling

循环/缩减：qatest不进runBenchmark，改numIterations不能缩此argv；保body/velocity state

原QA及弱点：原tol0.0005，仅for i<numBodies（position有4N标量），未授全4N/全finite强oracle

计数/成本：float+设备支持double时两个Create/reset都发生；one-reset131072B不是全进程输入闭合

最短下一步：可行sync-HtoD族但更复杂：rejection采样/RNG epochs/softening symbols/FP precision domains，不能只seed猜

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/5_Domain_Specific/nbody/nbody.cpp；SHA cfc39ae1a95e2ba9b61e3cb95d71149232d579955778d626127cfa70c725aadd；行368-398,1231-1283。

## RADIX_CUDA118（优先级3）

1M uint32 keys+sequence values，clock-seeded Thrust RNG；每轮从host未排序原数据重置，再sort_by_key

循环/缩减：默认100可新argv --iterations=2；保1M/keybit/type/key-value形态；不能把sort算法passes当计时repeat删

原QA及弱点：原仅is_sorted(keys)，不验证values permutation；help/invalid参数可能exit0，需实际非waived路径与Testpassed

计数/成本：节省98套重置/sort，actualThrust host-device lowering/CUBkernel census未测

最短下一步：Root接受新argv/同sourceprofile，实际bytes或精确seed/engine取证；不能把SDK42资格转来

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/2_Concepts_and_Techniques/radixSortThrust/radixSortThrust.cu；SHA 46a46254b8403b63cfe4f6581a713e9132f0707d321ab9438fb9ee6e1bcfd971；行48-76,118-168,179-214。

## RADIX_SDK42（优先级3）

独立SDK42 v4 ELF，1M keys+values，clock-seeded RNG；Thrust runtime实现可不同

循环/缩减：默认numIterations1已小，不再建议repeat缩减

原QA及弱点：仅keys有序+原shrQAFinish；values不授强QA，invalid/help也有exit0

计数/成本：没有100→2收益；现逻辑input8MiB一次，不同CUDA118逻辑800MiB

最短下一步：先actualinput/transfer-lowering证据，不把相同N/算法名称做SHA去重

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/sdk/4.2/radixSortThrust/radixSortThrust.cu；SHA 0fd3ae01f749320095e65d6adba50ce837fc8e2dffed7d4339ac1ab462c5fafe；行24-49,86-131,143-179。

## SIMPLEMPI（优先级3）

每rank2.56M float→sqrt GPU→host sum→MPI_Reduce；world topology和device choice决定输入

循环/缩减：无benchmark；保sqrt与MPI依赖；不默认切数据量

原QA及弱点：rank0无条件PASSED在Finalize后；没有CPU sqrt参考，仅执行检查；Average需只当展示

计数/成本：源码每rank1kernel/grid10000/block256，10.24MB输入；World1不是multi-rank性能

最短下一步：可先显式World1/单UUID functional profile、sync-HtoD/hash；MPI环境/Rank必须冻结

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/modern_repair_mpi_v1/simpleMPI.cpp；SHA 223e3f66ea08e8583aea99ddfaa700ae627fba379e02b7b0ec0790a3173fe8e7；行61-106,108-121。

## MULTIGPU_CUDA118（优先级3）

DATA_N32Mfloat按可见GPU_N分区，异步copy/reduce与CPU partial汇总，无重复

循环/缩减：grid-stride pos是真总和输入遍历；不减作timingloop

原QA及弱点：原relative diff<1e-5；不能用一GPU成功主张多GPU拓扑/重叠

计数/成本：128MiB input；actualGPU_N决定每设备N/launch/epochs，未测

最短下一步：冻结visible4080可做GPU_N1 profile；需ASYNCHtoD+lifetime/device-partition记录

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/0_Introduction/simpleMultiGPU/simpleMultiGPU.cu；SHA 8312a8644304cc5a3616821c7a3ea25e6b80493d80b4a8dbe20b93e68c82fbc7；行60-74,109-190,212-235。

## MULTIGPU_SDK42（优先级3）

SDK42独立ELF/source，32M数据device partition+stream同步

循环/缩减：无benchmark；保持实际device partition

原QA及弱点：原diff<1e-5/shrQAFinish；profile域限actual可见devices

计数/成本：128MiB static input不是两个版本trace等价

最短下一步：独立实例化async域，不能转移CUDA118资格

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/sdk/4.2/simpleMultiGPU/simpleMultiGPU.cpp；SHA cd8e3fc10e81e5bd818a11552892b744e5c9f495ef6317ac0c997fd94221ebc2；行212-276,288-321。

## ZEROCOPY_CUDA118（优先级4）

1M float a/b/c host-pinned mapped，vectorAdd一kernel；a/b交错rand生成

循环/缩减：无benchmark；不能去掉mapped alias当普通HtoD

原QA及弱点：原relative L2<1e-6；canMapHostMemory不支持/帮助等可能exitSuccess waiver，需真实kernel/完整检查

计数/成本：输入a+b8MiB；HtoD-only C8看不到实际kernel输入；输出c全写不需预像

最短下一步：新mapped prelaunch actualsource hash+allocation/alias/epoch/host-no-mutation直至sync；interleaved RNG需同序

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/0_Introduction/simpleZeroCopy/simpleZeroCopy.cu；SHA 19ef19e62abd63636039fbda03a60273fabf20b245215ad8809b8bec5ad23e3f；行156-207,211-246。

## ZEROCOPY_SDK42（优先级4）

独立SDK42映射内存版本，数据形态同但实际源/ELF不同

循环/缩减：无benchmark；内存访问域是主要特征不能替普通buffer

原QA及弱点：原relative norm<1e-6，waive/unsupported早退出可打印PASSED，不能仅exit0/marker

计数/成本：actualhost/device aliases和register/allocate分支未测

最短下一步：复用mapped observer家族但每输入独立取证；未知不等不可用

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/sdk/4.2/simpleZeroCopy/simpleZeroCopy.cu；SHA a902393bc93a25a16c9b898253163447a5c1101168bb1e3c30b772192ce0e0fa；行288-347,381-381。

## TFENCE_CUDA118（优先级4）

single-pass lastblock atomic retirementCounter+threadfence vs可选multipass；输入浮点rand小量

循环/缩减：默认benchmark100可新2但保原warmup与每次retirementCount reset；kernel内读全N/lastblock协议不能删

原QA及弱点：原float CPU sum diff<1e-8*size，不可借int reduction exact-equality oracle

计数/成本：warmup与benchmark可能不同kernel路径；不把sourcefor100等实际100kernels

最短下一步：需typed-symbol4B初始化/epochs和sync输入闭合；actualfence/atomic consumer不得仅凭staticmap赋权

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/2_Concepts_and_Techniques/threadFenceReduction/threadFenceReduction.cu；SHA 460190689bda1bb83689c2fa297fc7b521fd9125105b4d76423fcedd45b004dd；行199-249,395-453。

## TFENCE_SDK42（优先级4）

SDK42 typed-symbol变体独立binary；counter reset cudaMemcpyToSymbol前置

循环/缩减：此src defaulttestIterations1，不建议把CUDA118100缩法套来

原QA及弱点：同float CPU tolerance原QA，source强弱不混int算法

计数/成本：输入262400B静态合同；实际symbol-address-generation/ABI与路线仍未测

最短下一步：优先源码已有typed-symbol路线；新producer域需Root接受，非普通C8足够

源码：/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/adapted_sdk42/threadFenceReduction_typed_symbol_v1/threadFenceReduction.cu；SHA 97a0d13d9f9be1f8f5bcaa10efdcc2f5c92ed4b98087980db544d56d633d29bd；行214-264,410-462。

## 批量推进次序

1. 2DCONV和asyncAPI先进入现有精确源域/NativeQA流程；不要因缺实际input标签继续只登记。
2. c++11现成scalarQA新版本、NW原输入、huffman原输入及hotspot3d可推进，但保留各自弱QA范围；hotspot/NW演化不能当计时重复裁去。
3. QRNG20→2与CUDA118 radix --iterations=2是具体高收益新profile候选，先由Root接受source/binary/argv；SDK42 radix默认1无需缩减。
4. MPI与MultiGPU在单4080可明确单rank/单device功能profile，不为程序名自动判不可用，也不假测多卡通信。
5. ZeroCopy必须补mapped alias/prelaunch hash/lifetime；ThreadFence必须补symbol reset/atomic fence域；不能借同步C8一律PASS。
6. nbody_qatest不进benchmark，particlefilter frame是真迭代；优先已有准确输入/新defined RNG变体，不增加独立全数值oracle或假算法无损。

未执行GPU/新服务/Scope/大正文hash；CPU2/nice15/AS512M读取小源码和已有metadata。

## 内存与拓扑模型额外界限

ZeroCopy的host-mapped输入/输出并非普通设备DRAM的延迟域。alias/hash取证与单CTA退休只证明具体入口；尚不证明PCIe/host内存延迟和cache coherence模型。归档应保留allocation/mapping域，consumer是否实际使用它须另查，不能把它改成普通buffer而仍称原程序性能。

SimpleMPI的World1和simpleMultiGPU的单visible4080可作明确的功能profile，但不证明原多rank/多卡通信、物理重叠或拓扑性能。
