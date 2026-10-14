# Round A25｜A21–A24四份3DGS源审与109 CPU资格联合独立审查

**审查执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-14。**  
**总科学结论：`A21_A24_ACCEPT_SCOPED_SOURCE_AND_PLATFORM_METADATA / NATURAL_INPUT_BYTES_NOT_ADMITTED / STRONG_SOFTWARE_NO_HARDWARE_RESIDUAL_PROVEN / NO_GPU_OR_MECHANISM_ADMISSION`。**  
**复核方式：** GitHub固定提交、四份完整Markdown、独立Git compare与四文件UTF-8 SHA256、自选GS-Scale固定原始源码行、作者原始arXiv HTML（GS-Scale、GS-Cache）及IEEE GSArch**摘要**交叉核查。**未**连接109/174/164运行代码、安装环境、下载数据或验证真实GPU性能。报告中的CPU平台数据来自Lane M只读元数据，非ChatGPT现场再次查询。

## 0. 唯一执行身份与独立提交检查

| 工作 | 固定执行commit、tree与Git report blob | 独立审查结果 |
|---|---|---|
| **A21 / Lane T** | [`9575a674e5aa5af60e5803c07399fb64ae2c8488`](https://github.com/swayhrl/accel-sim-framework/commit/9575a674e5aa5af60e5803c07399fb64ae2c8488)；tree `5a474286c265798fc4cf2d44d9a29e1fb9e032d9`；[report](https://github.com/swayhrl/accel-sim-framework/blob/9575a674e5aa5af60e5803c07399fb64ae2c8488/docs/ai_workload_research/reviews/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md)，blob `c35d28c59cdd83d426fb4a8b1b5271e822cdb095`；本窗口SHA256 `1b42ea3307982aa6059a9b81cc60663c266e1e32aad11a0c09523bde26957848` | `ACCEPT_SCOPED_SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS` |
| **A22 / Lane T** | [`3b46ae8f94b5a72d1af4e06d352058bd2140abe6`](https://github.com/swayhrl/accel-sim-framework/commit/3b46ae8f94b5a72d1af4e06d352058bd2140abe6)；tree `f4bc52a41216c29647e75bc99c7712599bed2127`；[report](https://github.com/swayhrl/accel-sim-framework/blob/3b46ae8f94b5a72d1af4e06d352058bd2140abe6/docs/ai_workload_research/reviews/AI_ARCH_A22_GSSCALE_STEP_STATE_LIFETIME_SOURCE_MAP_174NEW_V1.md)，blob `5c0e3350c53d6c5d54d13310f11ec10a9318a47d`；SHA256 `58dc5a66e0d430dfc81e71e3e127d3a90a1684ab593ad8a0cf30b61463b78d0f` | `ACCEPT_SCOPED_CODE_STATE_LIFETIME_MAP_WITH_INPUT_GAPS` |
| **A23 / Lane N** | [`c096521d06483517bf6772689e5cc2c513186173`](https://github.com/swayhrl/accel-sim-framework/commit/c096521d06483517bf6772689e5cc2c513186173)；tree `fd01a289f7f408e33ad204d99f350ee64f243553`；[report](https://github.com/swayhrl/accel-sim-framework/blob/c096521d06483517bf6772689e5cc2c513186173/docs/ai_workload_research/reviews/AI_ARCH_A23_3DGS_HARDWARE_PRIOR_AND_RESIDUAL_SCOPE_174NEW_V1.md)，blob `60ece04e0e68d392244805f81916ad001aa6dade`；SHA256 `1356c433a5e2f07bdeec0e1883ccb6f4236a2a08334710e4cfc097e964217303` | `ACCEPT_SCOPED_NEAREST_WORK / NO_HARDWARE_HEADROOM_QUALIFIED` |
| **A24 / Lane M** | [`fc73b042726ef2312cb62bb9204941ec0ac195d5`](https://github.com/swayhrl/accel-sim-framework/commit/fc73b042726ef2312cb62bb9204941ec0ac195d5)；tree `0dd93737c34cf8576c375cbfe8d3fed9a5d1706c`；[report](https://github.com/swayhrl/accel-sim-framework/blob/fc73b042726ef2312cb62bb9204941ec0ac195d5/docs/ai_workload_research/reviews/AI_ARCH_A24_GSSCALE_NODE109_CPU_PLATFORM_PREFLIGHT_V1.md)，blob `70905d3b1bd050a9911b665b62ba39b66c422a14`；SHA256 `97f4ddb65830c9814c5bd4298ed3fc0e9e5371035127913550f099ab0772c4d7` | `ACCEPT_SCOPED_HOST_CPU_VENDOR_PASS / PLATFORM_VERSION_GAP / SOURCE_ONLY_UNVERIFIED` |

四执行分支HEAD均与用户提交SHA一致；相对预建起点各`ahead=1 / behind=0`，**Git diff仅各新增一份Markdown**。Git commit tree、parent已核对；四文本中无U+FFFD。A23由本窗口独立SHA256与执行者报告相同；其余3份本窗口也分别重算SHA256，不能因此宣称对174/109真实私有receipt、磁盘或164原raw再校验。作者2026-10 Git快照并不等于作者ASPLOS论文实验确切commit。

## 1. A21：一份真正自然场景的训练合同已可以写出，资产尚未入库

**接受：** Mill-19 **Rubble**是作者论文真实室外场景，不是合成MatrixCity。GS-Scale README指向`rubble-pixsfm.tgz`与作者另提供的**合并train/test COLMAP**；4× downsampling、`test_every=83`、`test_after=-1`、`max_steps=200000`、固定的增密设置/相机排序及GPU-only/naive-host/optimized-host入口被A21按固定源锚定。只读HEAD由Lane T报告：Content-Length `9,773,995,561` bytes、Last-Modified、分段式ETag；**不能把分段ETag当SHA256**，也没有真实下载与本ChatGPT再次HEAD验证。合并COLMAP原文件清单、SHA、训练相机顺序、场景展开体积依旧UNKNOWN。

**关键输入边界：** 跨训练步的Gaussian row index在densification/pruning之后不保证持续稳定，active Gaussian IDs的时间复用、ID死亡与新生时刻没有被原任务测量，**8.28%作者单步平均活跃比例不能变成缓存hit-rate或加速oracle**。有了公开下载URL不等于有了原生可回放输入authority。

**数学/质量不可偷换：** 强基线至少`gsplat GPU-only`与`fully optimized GS-Scale`，naive host只作作者消融；GPU-only如果在目标大场景OOM，只有容量可完成性，不存在可除的时间。训练完整epoch时间、允许达标的PSNR/SSIM/LPIPS以及固定容量下可训练Gaussians为三种不同问题。deferred Adam在某些恢复修正里作epsilon近似，质量接近并非bitwise参数/梯度/优化器状态同义。原始作者§5.5 Rubble PSNR26.63/26.62，不能说109已得该质量。

**A21裁决：**`SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS`，不是`SCENE_IDENTITY_PASS`或`FULL_NATIVE_TRAINING_READY`。

## 2. A22：独立源行核查发现一个值得未来测、但不是已测瓶颈的时间交接

固定source：[GS-Scale`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)。

本ChatGPT定点重新读取`simple_trainer_hybrid_optimized.py`的参数创建、`rasterize_splats`、`Runner.train`和`cpu_adam.cpp`：优化版实际**GPU常驻means/scales/quats及其Adam，CPU常驻opacity/SH及其moments/counter**。这比原论文摘要“all Gaussians in host”的高层描述更准确，说明作者的**选择性驻留已经是强软件**。初始化含Morton重排。

**真实代码可追溯的依赖图**：

`已选camera`→`GPU frustum culling`→`GPU valid_ids → blocking D2H valid_ids.to(cpu)`→`host select opacity/SH`→`pinned H2D asynchronous copy`→`GPU render/backward`→`blocking D2H grad/info`→`CPU Adam delayed update of previous step while GPU runs`→`synchronize + join`→`下一step状态可用`。触发densification时更新全体host参数、可能二次cull和counter重置。**可见源代码的blocking/线程同步不代表真实主路径有多大时间损失，也不证明某硬件cache能省掉它。**

必须特别避免遗漏：参数/Adam状态按类型分别驻留，不是整个Gaussian对象一致地放CPU或GPU；只看单步可见比例无法判断时序重用；CPU optimizer与GPU thread时段重叠，不能相加当完整wall，也不能理想化全部隐藏。

**A22裁决：**`SOURCE_LIFETIME_MAP_COMPLETE_WITH_INPUT_GAPS`，原生CPU等待时间、跨步稳定ID/复用、必要传输量/重叠比例、动态增密长尾与硬件收益均UNKNOWN。

## 3. A23：硬件最近邻反证成立，但不能把“未证明头寸”误写为“零头寸”

**GSArch HPCA2025：** 出版者可访问原始摘要确有Hot/Cold Gaussian缓存、梯度过滤与bank-conflict重排思想、宣称至多6.49×/15.42×峰值优势；**本轮未取得合法可访问的完整PDF实验组**，因此平台实机/模拟细节、强GS-Scale对照、计算分母/场景身份皆不能填造。论文日期早于GS-Scale，本两项属于不同研究场景。不能把GSArch摘要加速当实测109或压缩成“该问题全面解决”。

**GS-Cache arXiv2502.14938：** 作者有MatrixCity等连续渲染frame的实际native FPS/复用消融，但它针对**推理渲染**的anchor/Gaussian解码缓存。不能把它的跨frame缓存推断为训练时活跃Gaussian/Adam/moments可复用，也不能以其渲染FPS替代训练epoch。

**GS-Scale真实训练：** 作者已经在RTX4080 Super/i9等平台通过selective state、CPU Adam/forwarding/deferred update和image-split解决朴素卸载与容量的大部分问题，作者桌面完整GS-Scale相对可fit GPU-only的epoch throughput几何均值仅**0.84×**（不是相对naive host）；说明系统仍可能付出代价，但该差额**不是单一SM/cache/PCIe/host-memory服务成本的测量**。作者还认为其平台的PCIe在总时长中只占较小部分，优先不能凭每步仅8.28%可见率申请cache机制。

**A23裁决：**`NO_HARDWARE_HEADROOM_QUALIFIED`正确理解为**目前缺必要数据，不能晋升**，不等于“3DGS架构优化空间物理上不存在”。尤其GSArch全文`ABSTRACT_ONLY`意味着该近邻审查尚不是精确的新颖性证明。

## 4. A24：109 Intel前提是真的，但代码线程硬编码是关键混杂变量

A24执行侧只读报告：Intel Core i7-13700（16核/24逻辑处理器）、AVX2/FMA、无AVX-512；系统Python3.12.3、原Lane M venv Python3.11.17、`torch2.10.0+cu126`，旧env无IPEX/CPUAdam/gsplat版分发记录、NumPy2.4.6；作者入口Python3.10/`torch2.2.0+cu121`/`torchvision0.17.0+cu121`/`IPEX2.2.0`，代码要求`numpy<2`。内存约62–63GiB总、可用60–61GiB快照，主盘约936GiB总、134–135GiB可用快照。**Intel厂商前提PASS，但已有环境根本不兼容原安装配置；未来只能另建隔离env并重新进行版本、ABI和数值资格。** 系统驱动/安装包元数据不能宣称实机CUDA已验证。

**值得独立指出的混杂**：本ChatGPT直接读取作者`cpu_adam/src/cpu_adam.cpp`确认`adam_deferred_update`内部调用`omp_set_num_threads(64)`并紧跟OpenMP parallel循环；A24还指出其它类似入口。因此实际CPU更新可能在16核/24线程机器上发生线程过量、调度争用及NUMA/cache影响，**不能仅用设置`OMP_NUM_THREADS=1`保证CPUAdam走一线程，也不能直接把慢归为纯内存带宽**。对线程数的合法调优会改变软件策略，不是物理CPU带宽单变量，对照应固定并报告。

硬件环境的正面信息也需保留：109 CPU厂商条件不需要另开发AMD后端，当前可用空间在“只看单个9.77GB归档”角度上不足以否决未来隔离env；但展开图像/合并COLMAP/checkpoint和CPU Adam host高峰未测，**不等于完整Rubble训练fit已PASS**。

**A24裁决：**`CPU_INTEL_VENDOR_PASS / CURRENT_SOFTWARE_VERSION_GAP / ISOLATED_STACK_RUNTIME_NOT_EVALUATED`。

## 5. 四报告联合因果链：哪些门已经闭合，哪些还没有？

| 科学/资源门 | 当前实证 | 决策 |
|---|---|---|
| 真正自然3DGS数据源 | Mill-19 Rubble公开原URL、处理规则、作者论文实场景可证；未下载、COLMAP与相机hash缺 | **SOURCE_ONLY_PASS / BYTE_IDENTITY_PENDING** |
| 完整强软件baseline | gsplat GPU-only、naive host、优化GS-Scale有可读实现，训练状态驻留/交接源逻辑清晰 | **STRONG_SOFTWARE_DESIGN_CONFIRMED / NODE109_NOT_INSTALLED** |
| 109宿主最小条件 | Intel i7 AVX2、磁盘/RAM静态余量核到，核心版本不同、OpenMP64硬编码 | **HOST_VENDOR_PASS / VERSION_ABI_EXECUTION_UNQUALIFIED** |
| 动态训练同语义 | deferred Adam epsilon、densification、frame相机序列及Gaussian row映射有差异 | **NUMERIC_QUALITY_AND_STATE_IDENTITY_NOT_QUALIFIED** |
| 本机完整训练时间/容量/质量 | 没有训练、没有传输/同步时长/活跃集时间线/PSNR门 | **NATIVE_NOT_EVALUATED** |
| 强软件后的物理资源剩余 | GSArch摘要已有cache/atomics设计、GS-Scale host overlap强；没有同平台强模型剩余关键wall和单变量资源干预 | **P13/P14_HARDWARE_HEADROOM_NOT_QUALIFIED** |

**唯一允许现在升级的是科学输入与源码身份整理程度，不是native/机制准入。**

## 6. 科研价值判断与后续合并工作法

**当前3DGS项目位置：`DISCOVERY_INPUT_AND_SOFTWARE_FEASIBILITY_SCOPED / NATIVE_RESOURCE_HEADROOM_UNKNOWN / HARDWARE_NO_GO`。** 它依然比合成3DGS或不带自然输入的普通embedding benchmark更有现实场景价值，但GS-Scale/GSArch新颖性覆盖已相当强，**不建议为了“已经做了四份source审查”立即在109下载9.77GB并搭数小时训练环境**；科学headroom需先说明获取大数据与训练能增加哪条不能从论文中得知的实际结果。

**如果研究者未来单独批准一个新的真实3DGS实验目标，必须将以下可共享同一科学对象的连续阶段合并成一条`ONE_GOAL_CONTIGUOUS`而不是机械拆A25/A26/A27**：

1. **Admission preflight（只读/CPU）**：冻结作者固定版本、一个真实Rubble/Building场景与公开完整asset manifest和下载/展开容量预算、CPUAdam线程与IPEX/ABI版本、GPU-only与GS-Scale strong算法/数值差异；若原数据身份不可获得、代码构建显著偏离作者，则`INPUT_OR_PLATFORM_DEFERRED`，不给GPU阶段。
2. **隔离环境＋原始资产（新增下载/安装必须明确获准）**：仅在许可的存储/download预算内取得场景hash与处理产物，固定真实camera/initial Gaussian ID以及何时densification；不得动旧NequIP/C16/AWMA环境、shared locks或164历史authority。
3. **原生正确性/质量canary（GPU需独立许可和独占锁）**：先证相同训练scene/配置/强软件有合法完整GPU/CPU step与质量目标；对不同Adam算法明确标`APPLICATION_QUALITY_MATCHED`而非`BITWISE_EQUIVALENT`。GPU-only OOM的点只作容量结果。
4. **只有通过科学门才有限时诊断**：测完整训练step及必要epoch、真正host CPU/PCIe/GPU关键路径、未被隐藏的更新/同步时长、动态active IDs和host state服务，再以合法的强软件对照定是否仍有硬件剩余；若没有`SOFTWARE_ABSORBED_STOP`。若有才考虑另起独立因果物理资源实验及PPA，不由此合同自动启动机制。

每阶段可以在**同一已批准Goal**内有界solve-and-continue（普通路径/manifest/版本兼容诊断），不因人为时间框、每个小任务编号、多个状态报告或长时间无人值守而机械STOP。**GPU锁/预算、scientific identity、数值、自然数据与物理资源轴变更仍应fail-closed**；绝不暗中开GPU或下载scene。若已有原文/公开源码已经足以判定硬件头寸不可归因，合法终态就是`PARKED`，不继续铺实验基础设施。

未来若只想继续论文/source工作，不需为A21/A22/A23/A24分别重新开多个Codex窗口；应将**真实原文组+强source+输入metadata+109 CPU元数据**统一交给既有单Lane的一条只读Goal，审查者一次独立交叉审阅，另有独立并行近邻研究仅在材料确实不同才有必要。

**本轮没有提交任何新的执行Goal，没有创建新GPU分支，没有对174/109发启动命令。所有四Lane执行分支继续STOP、旧历史项目不变。**
