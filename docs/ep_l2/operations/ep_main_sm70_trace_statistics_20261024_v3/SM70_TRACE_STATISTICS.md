# EP当前V100/SM70 trace资产全表（2026-10-24）

当前EP最近正式运行加载V100/Volta基础及EP研究overlay。以下按既有四套资产逐程序家族统计；不是4080资产表，也不表示所有输入已通过EP模拟资格。

本轮复用0bc1aa9f3bfb3cceccdea32af4af668037769027的双账户文件级清点，并新增逐成员header检查：原174 16,883个文件、174-new 8,641个文件，所有binary version均为70；无读取错误、无文件身份变化。只读取每文件至多2048B解码前缀，不解析指令正文、不重算整个trace SHA；压缩读取实际字节另记。两账户包含共享/重复视图，不相加为独立文件或存储占用。

**已发现trace：53个suite内程序家族；46个有常规目录版本，7个仅裁剪。174-new目前可读取27个，其中18个常规、9个仅裁剪。** Rodinia3.1的ParticleFilter float/naive合计一个家族，两实现分别保留；与2.0-ft分开。

“常规”仅表示存在成员齐备、路径未标记裁剪的版本，原始捕获是否完整仍需进一步来源/正文资格；“未找到”只针对已核查展开文件。大型tgz和tar.zst未展开，不能排除另含输入。

## 总计

| Suite | 统计口径 | 常规 | 仅裁剪 | 未找到 | 174-new有trace |
|---|---|---:|---:|---:|---:|
| CUDA Samples | 已知trace程序，完整SDK分母未冻结 | 10 | 0 | 不作全SDK缺口计数 | 3 |
| Rodinia | 23个程序家族 | 19 | 0 | 4 | 7 |
| Parboil | 11个程序家族 | 8 | 1 | 2 | 4 |
| PolyBench/GPU | 15个程序家族 | 9 | 6 | 0 | 13 |

## CUDA Samples

| 程序 | 原174 | 174-new | SM | EP历史/备注 |
|---|---|---|---|---|
| BlackScholes | 常规 | 未找到 | 70 | 待EP资格 |
| convolutionSeparable | 常规 | 常规 | 70 | 指定旧输入已接受；其余输入不继承 |
| fastWalshTransform | 常规 | 常规 | 70 | 指定旧输入已接受；其余输入不继承 |
| histogram | 常规 | 未找到 | 70 | 待EP资格 |
| mergeSort | 常规 | 未找到 | 70 | 待EP资格 |
| scalarProd | 常规 | 未找到 | 70 | 待EP资格 |
| scan | 常规 | 未找到 | 70 | HOLD: extended/shared address semantics |
| sortingNetworks | 常规 | 未找到 | 70 | 待EP资格 |
| transpose | 常规 | 未找到 | 70 | 待EP资格 |
| vectorAdd | 常规 | 常规 | 70 | Vector 4M原生已接受 |

## Rodinia

| 程序 | 原174 | 174-new | SM | EP历史/备注 |
|---|---|---|---|---|
| b+tree | 常规 | 常规 | 70 | HOLD: active mask/address record contract |
| backprop | 常规 | 未找到 | 70 | 待EP资格 |
| bfs | 常规 | 未找到 | 70 | 待EP资格 |
| cfd | 常规 | 常规 | 70 | 指定旧输入已接受；其余输入不继承 |
| dwt2d | 常规 | 常规 | 70 | 指定旧输入已接受；其余输入不继承 |
| gaussian | 常规 | 常规 | 70 | 待EP资格 |
| heartwall | 未找到 | 未找到 | — | 源码/目录存在，未找到齐备展开trace |
| hotspot | 常规 | 常规 | 70 | 待EP资格 |
| hotspot3d | 常规 | 未找到 | 70 | 待EP资格 |
| huffman | 未找到 | 未找到 | — | 源码/目录存在，未找到齐备展开trace |
| hybridsort | 常规 | 未找到 | 70 | 待EP资格 |
| kmeans | 常规 | 未找到 | 70 | 待EP资格 |
| lavamd | 常规 | 未找到 | 70 | 待EP资格 |
| leukocyte | 未找到 | 未找到 | — | 源码/目录存在，未找到齐备展开trace |
| lud | 常规 | 常规 | 70 | 待EP资格 |
| mummergpu | 未找到 | 未找到 | — | 源码/目录存在，未找到齐备展开trace |
| myocyte | 常规 | 未找到 | 70 | 待EP资格 |
| nn | 常规 | 常规 | 70 | 待EP资格 |
| nw | 常规 | 未找到 | 70 | 待EP资格 |
| particlefilter | 常规 | 未找到 | 70 | 待EP资格；float and naive both present, counted as one family |
| pathfinder | 常规 | 未找到 | 70 | 待EP资格 |
| srad | 常规 | 未找到 | 70 | 待EP资格；3.1 v1 present; 3.1 v2 only commandlist placeholder; do not substitute 2.0-ft |
| streamcluster | 常规 | 未找到 | 70 | 待EP资格 |

## Parboil

| 程序 | 原174 | 174-new | SM | EP历史/备注 |
|---|---|---|---|---|
| bfs | 常规 | 未找到 | 70 | 待EP资格 |
| cutcp | 常规 | 未找到 | 70 | 待EP资格 |
| histo | 常规 | 未找到 | 70 | 待EP资格 |
| lbm | 未找到 | 未找到 | — | 源码/目录存在，未找到齐备展开trace |
| mri-gridding | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| mri-q | 常规 | 常规 | 70 | 待EP资格 |
| sad | 常规 | 常规 | 70 | 指定旧输入已接受；其余输入不继承 |
| sgemm | 常规 | 常规 | 70 | 指定旧输入已接受；其余输入不继承 |
| spmv | 常规 | 未找到 | 70 | HOLD: missing IADD3 source operand in legacy input |
| stencil | 常规 | 未找到 | 70 | 待EP资格 |
| tpacf | 未找到 | 未找到 | — | 源码/目录存在，未找到齐备展开trace |

## PolyBench/GPU

| 程序 | 原174 | 174-new | SM | EP历史/备注 |
|---|---|---|---|---|
| 2DCONV | 常规 | 常规 | 70 | 待EP资格 |
| 2MM | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| 3DCONV | 常规 | 未找到 | 70 | 待EP资格 |
| 3MM | 常规 | 仅裁剪 | 70 | 待EP资格 |
| ATAX | 常规 | 常规 | 70 | 待EP资格 |
| BICG | 常规 | 常规 | 70 | 待EP资格 |
| CORR | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| COVAR | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| FDTD-2D | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| GEMM | 常规 | 常规 | 70 | 待EP资格 |
| GESUMMV | 常规 | 常规 | 70 | 待EP资格 |
| GRAMSCHM | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| MVT | 常规 | 未找到 | 70 | 待EP资格 |
| SYR2K | 仅裁剪 | 仅裁剪 | 70 | 待EP资格 |
| SYRK | 常规 | 仅裁剪 | 70 | 待EP资格 |

## 版本、缺口和使用边界

- CUDA：上表完整列出当前找到trace的10程序；不是完整CUDA Samples只有10程序。实际还存在SDK4.2的73个源码样例目录，其中63个未在本轮trace表找到同名程序；源码4.2与捕获路径9.1不可直接当成同一版本全集。73项另表列出，尚未建立逐项同源捕获关系。
- Rodinia3.1：23个程序家族中19个有trace；缺Heartwall、Huffman、Leukocyte、MUMmerGPU。SRAD已有v1，但v2缺齐备展开trace。ParticleFilter的float/naive两实现均有。
- Parboil：11程序中8个有常规版本，MRI-Gridding仅裁剪；LBM、TPACF未找到齐备展开trace。109新采的SM89 SpMV small不混入此SM70表。
- PolyBench/GPU1.0：15程序全部有SM70 trace；2MM、CORR、COVAR、FDTD-2D、GRAMSCHM、SYR2K当前仅找到裁剪版本。174-new缺3DCONV、MVT的展开输入；其3MM/SYRK只发现裁剪版本。

## Rodinia2.0-ft另存资产

174-new另有11个SM70输入：Backprop、BFS、Heartwall、Hotspot、Kmeans、LUD、NN、NW、Pathfinder、SRAD v2、Streamcluster。它们是另外一个版本，不用于填补Rodinia3.1的缺口，也不重复加进53个程序家族。

## 输入、路径与接受边界

- 每个程序的双账户绝对入口见PROGRAM_STATISTICS.csv/JSON；所有候选输入尺寸、参数、kernel数和成员元数据仍以父级[完整账户清点](../ep_main_account_workload_audit_20261024_v2/ACCOUNT_WORKLOAD_AUDIT.md)的EXACT_INPUT_INDEX.json.gz为准。路径副本、S/F与多个runtime不重复计程序。
- 旧接受的7程序是Vector、Conv、FWT_7_21、CFD、DWT、SAD及独立SGEMM，限其精确输入和runtime；原MAIN6/7保持。Scan、B+Tree、旧Parboil SpMV仍HOLD。
- 只有Vector的指定4M输入有EP native完整应用证据。当前文件已迁入/可读不等于资格或启动授权。
- 全部核查只读；模拟、编译、采集、输入搬运和科研账本改写均为0。

## CUDA SDK4.2源码候选附表

以下仅为73个源码目录的完整名称对照；不把它作为捕获包9.1的覆盖率分母。

| 源码样例 | 本轮找到同名trace |
|---|---|
| BlackScholes | 有；同源版本未认证 |
| FDTD3d | 未找到 |
| FunctionPointers | 未找到 |
| HSOpticalFlow | 未找到 |
| Interval | 未找到 |
| Mandelbrot | 未找到 |
| MonteCarlo | 未找到 |
| SobelFilter | 未找到 |
| SobolQRNG | 未找到 |
| alignedTypes | 未找到 |
| asyncAPI | 未找到 |
| bandwidthTest | 未找到 |
| bicubicTexture | 未找到 |
| bilateralFilter | 未找到 |
| binomialOptions | 未找到 |
| boxFilter | 未找到 |
| clock | 未找到 |
| concurrentKernels | 未找到 |
| convolutionFFT2D | 未找到 |
| convolutionSeparable | 有；同源版本未认证 |
| convolutionTexture | 未找到 |
| cppIntegration | 未找到 |
| dct8x8 | 未找到 |
| dwtHaar1D | 未找到 |
| dxtc | 未找到 |
| eigenvalues | 未找到 |
| fastWalshTransform | 有；同源版本未认证 |
| fluidsGL | 未找到 |
| histogram | 有；同源版本未认证 |
| imageDenoising | 未找到 |
| inlinePTX | 未找到 |
| lineOfSight | 未找到 |
| marchingCubes | 未找到 |
| matrixMul | 未找到 |
| matrixMulDynlinkJIT | 未找到 |
| mergeSort | 有；同源版本未认证 |
| nbody | 未找到 |
| newdelete | 未找到 |
| oceanFFT | 未找到 |
| particles | 未找到 |
| postProcessGL | 未找到 |
| quasirandomGenerator | 未找到 |
| radixSortThrust | 未找到 |
| recursiveGaussian | 未找到 |
| reduction | 未找到 |
| scalarProd | 有；同源版本未认证 |
| scan | 有；同源版本未认证 |
| segmentationTreeThrust | 未找到 |
| simpleAssert | 未找到 |
| simpleAtomicIntrinsics | 未找到 |
| simpleCubemapTexture | 未找到 |
| simpleGL | 未找到 |
| simpleLayeredTexture | 未找到 |
| simpleMPI | 未找到 |
| simpleMultiCopy | 未找到 |
| simpleMultiGPU | 未找到 |
| simpleP2P | 未找到 |
| simplePitchLinearTexture | 未找到 |
| simpleStreams | 未找到 |
| simpleSurfaceWrite | 未找到 |
| simpleTemplates | 未找到 |
| simpleTexture | 未找到 |
| simpleTexture3D | 未找到 |
| simpleVoteIntrinsics | 未找到 |
| simpleZeroCopy | 未找到 |
| smokeParticles | 未找到 |
| sortingNetworks | 有；同源版本未认证 |
| template | 未找到 |
| threadFenceReduction | 未找到 |
| transpose | 有；同源版本未认证 |
| vectorAdd | 有；同源版本未认证 |
| volumeFiltering | 未找到 |
| volumeRender | 未找到 |
