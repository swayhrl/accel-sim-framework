# C16 Split-K 工作集容量阈值机制定位 — Master Pipeline V1

日期：2026-09-28。

## 0. 当前科学问题

已接受的跨规模结果显示：

- 旧Qwen UP_M256：split1 相对 split8，warm约 **+30.0%**；
- GPT-3公开尺寸代理 EXPAND_M256：split1 相对 split8，warm约 **-71.0%**；
- 两者使用同一 accepted AutoAWQ split8/split1 内核家族和相同M=256；
- 旧Qwen qweight约32.4MiB，小于64MiB L2；
- GPT-3 proxy qweight=288MiB，远大于64MiB L2；
- GPT-3 EXPAND_M256 warm NCU：split8总DRAM约0.945GB，split1约2.993GB。

本阶段不再问“哪个split更快”，而问：

> **split-K是否通过改变同一M tile之间反复消费的有效权重工作集，使其跨越L2容量区间，从而造成策略方向翻转？**

这是待验证机制假设，不是既成事实。

---

## 1. 精确AutoAWQ源码事实

公开历史源码：

- repo：`casper-hansen/AutoAWQ_kernels`
- commit：`c7b0e88c327694c715b0a758d9ce8fd414a1fa21`
- file：`awq_ext/quantization/gemm_cuda_gen.cu`
- Git blob：`98f49efac8626388039912e6aabc8a84d9f8303b`

目标kernel：

`gemm_forward_4bit_cuda_m16n128k32`

已由ChatGPT先行核到、但仍要求Lane8独立复核的源码关系：

1. `j_factors1 = ceil(OC/128)`。
2. `blockIdx_y = blockIdx.x % (ceil(M/16) * j_factors1)`。
3. `blockIdx_z = blockIdx.x / (ceil(M/16) * j_factors1)`，即split维。
4. M tile = `blockIdx_y / j_factors1`；N tile = `blockIdx_y % j_factors1`。
5. qweight的B地址依赖N tile、K tile和thread/warp，但**不依赖M tile**；因此同一N tile/split的权重会被不同M tile重复消费。
6. K循环：
   `k_0_0 = iteration * split_k_iters + blockIdx_z`。
   所以split8不是8个连续K段，而是按32-row K tile的模8 residue交错取样。
7. 对线性block ID而言，split z为外层；同一split内，N tile随blockIdx_y先变化，跨过全部N tiles后进入下一个M tile。
8. CUDA真实CTA调度顺序不能仅由线性block ID证明，因此源码只建立**静态可复用集合与线性ID局部性**；真实cache复用仍需native counter/后续trace验证。

## 2. 为什么“37MiB一个连续K段”这个说法不准确

因为split8访问的是交错K32 tile，不是连续K range。

对GPT-3 proxy，K=12288、N=49152、group_size=128：

- qweight总量：288MiB；
- qzeros+scales总量：11.25MiB；
- split1完整W4权重+metadata：299.25MiB；
- split8每个split的qweight唯一集合：约36MiB；
- group_size=128而K32 tile按mod8分配，使单split访问的metadata唯一集合约为总metadata的一半，而不是1/8；
- 因此一个split的静态唯一weight+metadata集合约 **41.625MiB**，仍低于64MiB L2。

Lane8必须从源码地址公式独立验证上述metadata重叠关系；若不成立，不得使用41.625MiB结论。

旧Qwen UP权重：
- qweight 33,947,648B；
- qzeros 265,216B；
- scales 1,060,864B；
- split1完整W4权重+metadata约 **33.64MiB**，本身已低于64MiB。

因此一个可检验的解释是：

- 旧Qwen split1：完整权重集合已可落在L2容量范围；
- GPT-3 split1：完整集合远超L2；
- GPT-3 split8：每个split静态唯一集合重新落到L2容量范围。

但“落到容量范围”不等于真实命中；需要下一步实验。

---

## 3. 最干净的native验证：固定M/N，只改变K

与其立即抓10GB级地址trace，本阶段优先做一个更小、混杂变量更少的容量阈值实验。

固定：

- M=256
- N=49152
- group_size=128
- split arm只用1和8
- output/workspace shape、CTA grid对同一arm保持不变
- synthetic W4公式沿用`GPT3_SHAPE_SYNTH_V1`

只改变K：

| K | 完整W4权重+metadata | /64MiB L2 | split8单split静态集合（预估） |
|---:|---:|---:|---:|
| 2048 | 49.875MiB | 0.779× | 6.938MiB |
| 2560 | 62.344MiB | 0.974× | 8.672MiB |
| 3072 | 74.813MiB | 1.169× | 10.406MiB |
| 4096 | 99.750MiB | 1.559× | 13.875MiB |
| 12288 | 299.250MiB | 4.676× | 41.625MiB |

K=12288直接复用accepted GPT-3 producer，不自动重跑。

之所以选2048/2560/3072/4096：

- 2560略低于完整W4总footprint≈L2的容量线；
- 3072略高于；
- M/N不变，因此split1/split8的CTA grid、output size和reduction/scratch大小不随K变化；
- K只改变循环长度和weight工作集，是比扫M/N更干净的机制诊断。

不能把64MiB当硬阈值：真实有效容量还受其他数据、组相联和调度影响。看的是趋势/crossover，不是要求恰在64MiB发生跃迁。

---

## 4. 三Lane流水

### Lane8 / 174-new
CPU-only static mechanism audit。

第一阶段尽快发布：
`STATIC_GATE.json`

只要核心源码映射、精确footprint公式和K点合法性闭合，即可push，不必等完整报告。

Gate允许：
- `SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN`
- `NOT_SUPPORTED_STOP_NATIVE`
- `AMBIGUOUS_STOP_FOR_REVIEW`

### Lane7 / 109
可以与Lane8同时开始**CPU-only**准备：

- worktree；
- old binary/source hash；
- runner生成；
- tiny CPU formulas/tests；
- 新K的预期grid/scratch；
- 不初始化CUDA。

轮询Lane8 gate。
若SUPPORTED，直接用一次GPU lock完成最小native threshold screen。
若NOT_SUPPORTED或AMBIGUOUS，停止，不碰GPU。

### Lane6 / 174-new
可以同时准备consumer：

- 复用旧Qwen + GPT3 K=12288 accepted endpoint；
- 冻结threshold comparison schema；
- 等Lane7完成后独立重算新K点。

### Lane4
完全不动。

---

## 5. Lane7 native threshold screen

只做WARM_SAME_ARM；不做EVICT状态。

新K：
- 2048
- 2560
- 3072
- 4096

每K：
- A=split8
- B=split1
- correctness；
- launch audit；
- 10 global warmups/arm；
- 25 ABBA blocks，50 samples/arm；
- 2 same-arm warmups/sample；
- NCU A_W/B_W各1次。

总新timing：
4 K × 2 arms × 50 = 400 samples。

总新NCU：
4 K × 2 arms = 8 profiles。

复用K=12288 accepted endpoint，不重测。

冻结NCU：
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- duration
- A的GEMM/reduction分列
- B只有GEMM

禁止tensor级归因。

---

## 6. 判读

真正支持容量/工作集机制，需要看到至少以下联合趋势：

1. K从完整工作集<L2区间进入>L2区间时，split1相对split8显著恶化；
2. split1 DRAM相对split8同步增大；
3. grid/reduction/workspace保持固定，因此不能由CTA数量变化解释；
4. K=12288 endpoint与趋势方向一致。

如果没有趋势，当前“split切小工作集进入L2”假设应降级或否定，不继续SASS/模拟。

如果趋势明确，再考虑：
- qweight-targeted bounded trace；
- 或paired Accel-Sim容量counterfactual。

不自动执行。

---

## 7. 证据边界

这仍然是GPT-3公开尺寸W4机制代理，不是：
- GPT-3 checkpoint；
- GPT-3量化质量；
- GPT-3自然激活；
- 完整模型；
- 唯一L2因果。

这个K threshold screen本身是人工机制实验，价值在于隔离工作集变量。
