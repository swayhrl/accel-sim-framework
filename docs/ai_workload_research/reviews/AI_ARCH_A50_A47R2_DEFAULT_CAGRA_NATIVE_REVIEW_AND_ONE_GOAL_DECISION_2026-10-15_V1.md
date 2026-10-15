# Round A50｜A47R2原生索引复验独立审查与一次性下一实验裁决

**审查者：ChatGPT／AI-ARCH Discovery，2026-10-15。协调基点：`891eec54d82fd8a1b1481c0434d94600ba54e92d`。**

## 0. 总裁决：接受有范围的默认路径资格，停止非默认Stream排障

**`ACCEPT_A47R2_SCOPED_NATIVE_C0_INDEX_FIELDS_PASS / C1_EXPLICIT_STREAM_SETUP_SIGSEGV / ONE_FUTURE_DEFAULT_ONLY_GLOVE_PROBE_CONDITIONAL`**。

A47R2的独立执行、资源、Git发布与STOP均接受。确认：

1. `C0_DEFAULT_RESOURCES_INDEX_METADATA_PASS`：真实109/RTX4080/SM89、冻结cuVS/RMM 26.10/默认RMM=`CudaMemoryResource`、CuPy allocator=`None.malloc`、`Resources()`路径成功实际调用一次1024×100合成FP32 cosine/IVF-PQ CAGRA构图，`res.sync()+deviceSynchronize()`通过，退出0。独立读取原始`raw/C0.log`和`raw/C0_result.json`，五项属性分别为`trained=True, size=1024, dim=100, degree=64, dtype=<class 'numpy.float32'>`；`np.dtype(idx.dtype)==np.dtype('float32')`为True。A49找到的原`str(idx.dtype)=="float32"`误判在这里得到本机实证纠正。
2. `C0_GRAPH_CONTENT_AND_SEARCH_NOT_QUALIFIED`：可选读取`idx.graph`后用`cp.from_dlpack`/`cp.asarray`做图内容检查时，报告ValueError，故图边ID范围/逻辑hash并未获得；这**不撤销预冻结必需五项PASS**，也不能声称Graph内容、搜索数值、recall或性能通过。
3. `C1_EXPLICIT_STREAM_SETUP_SIGSEGV`：单独fresh process使用同SHA输入和相同默认allocator，不改变构图参数，仅选择`cp.cuda.Stream(non_blocking=True)`＋`Resources(stream=stream.ptr)`的非默认配置。原日志在`GPU_INPUT_PASS`后发生SIGSEGV(exit-11)，faulthandler只指到**同时包含stream创建与Resources绑定的同一Python源码行**；`PADDED_DATASET`和`cagra.build`均未执行。无法定位更具体的子调用、指针或vendor根因；不可宣称是原A47中`libcuda cuStreamGetId`的同一故障点。
4. C0/C1说明此**一组软件配置存在执行差异**：默认path可得到合法索引元数据，而显式stream path无法完成构图前初始化；**不证明单独Stream是根因**，不能排除RMM/cuVS/driver接口交互等。原A47另外叠加显式pool，不能混同单因素结果。

**科研管理决策：** 既然C0默认path已合法工作，不继续修复非默认Stream、换驱动/版本或排查第三方库长尾。下一次真正有用的**新信息**是一个真实GloVe完整默认资源构图及同recall的软件强参照/真实时间。这个下一GPU实验**需要新的用户明确授权**。A47R2的授权和执行已STOP，不可自动消费其剩余GPU时间。

## 1. 精确身份与原始证据审查

| 条目 | 固定审计结果 |
|---|---|
| 执行branch | `hrl/aiarch-a47r2-cagra-index-fields-stream-109-v1` |
| Goal固定parent | `bbbe9d89d05e268f7dc958886a571fb327c44584` |
| 完成commit | [`c37bfa976f556442f9a6856b899edb537b204875`](https://github.com/swayhrl/accel-sim-framework/commit/c37bfa976f556442f9a6856b899edb537b204875) |
| Git-data tree | `9ee03a24f78c1e5191a8b2065829bd42fa25a2c5` |
| `FINAL_REPORT.md` blob | `821220e4c44f0a5f0d316716085022de9a09d2b4f` |
| `raw/C0.log` blob | `408a7903f8024cd079c15c60c9ed472cdf637253` |
| `raw/C1.log` blob | `318df6e0f8f9d87d7b86ac84421d14c83c6a2682` |
| `tools/aiarch_a47r2/canary.py` blob | `aaf20a40d7c4d77df440a84b96de0ff22957de9f` |
| parent→branch | ahead1, behind0，新增15个文件，仅run目录和本次tools；final commit→branch identical |

主报告：[A47R2 FINAL_REPORT](https://github.com/swayhrl/accel-sim-framework/blob/c37bfa976f556442f9a6856b899edb537b204875/docs/ai_workload_research/runs/AI_ARCH_A47R2_CAGRA_INDEX_FIELDS_STREAM_109_V1/FINAL_REPORT.md)。检查`GATES.json`、`CONFIG_AND_FIELDS.json`、`RESOURCE_RECEIPT.json`、`NEXT_EXPERIMENT_PROPOSAL.json`及原始C0/C1日志，主张相互支持。严格将“执行侧工作区clean/锁释放”视为Codex receipt，本窗口不以Git回读冒充SSH实时观测。

### 资源

GPU锁累计2.601539s；RSS树采样峰903,643,136B（0.842GiB）；显存采样峰286MiB；新增文件5,525,504B（5.27MiB）；CPU准备93.04s；数据/依赖下载安装0；旧A47/R1的143个冻结SHA+mtime核验未变。采样瞬时可能漏峰，不能把它说成显存真实精确峰值。报告中的“Goal工具9秒”与执行侧约14分钟全流程时间是不同分母，不相互代替。

## 2. 源码反证和两个不可跳过的下一实验门

**A49误判已经被本机纠正。** cuVS源码`NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`的`cagra.pyx`中`idx.dtype`通过`cydlpack.pyx`返回NumPy**类`np.float32`**；合法比较必须做`np.dtype(idx.dtype)==np.dtype('float32')`。R2原始C0逐字段有独立结果，不再只是源码推论。

**维度warn不构成单独失败证据。** `cpp/src/neighbors/cagra.cuh`中`update_dataset`会比较新数据dim=100与图索引未附着时旧dim=0，记录warning之后继续返回新的index。R2最终idx.dim=100是后置实际值，证明这条具体warning不能直接当失败。

**图内容桥接仍未知。** R2的`idx.graph`公开视图在`cp.from_dlpack`/`cp.asarray`路径触发`ValueError("A DLPack tensor object cannot be consumed multiple times ...")`；暂不为此重构CAGRA Python端。未来真实索引应记录`cagra.save(...,include_dataset=True)`及精确序列化文件SHA、版本与索引所有权，使用合法`cagra.load(Index(),path,out_dataset=Dataset())`并进行输入、返回ID/距离和recall自检。若公开Graph视图仍不可合法导出，则`LOGICAL_GRAPH_HASH_UNKNOWN`，绝不能伪称已证明图逐元素字节相同。序列化SHA与功能一致不能替代直接Graph逐元素hash，但足以绑定本轮相同串行化资产与实际可比较搜索。

**一个实现细节必须在下一Goal锁死：** 默认`Resources()`与默认CuPy stream在构图、save/load、search和传输全部保持一致；Python`auto_sync_resources`在**显式传Resources对象**时不会自动同步，需要执行程序在各计时边界完成合法`res.sync()/deviceSynchronize()`。不复制原A47`native.py`内显式pool/非默认stream；新的driver/cache/版本安装会破坏R2比较身份。

## 3. 下一步：只提一次完整默认路径的真实发现实验，而不是继续小API诊断

独立复核R2机器可读`NEXT_EXPERIMENT_PROPOSAL.json`与A47原`PREREGISTRATION.json`：已有完整官方GloVe HDF5及normalized base/query/GT，SHA绑定；原查询划分`calibration=2000、report=8000、timing=2048`和原搜索参数`k10/itopk128/width1/max_iterations64/h9或h11`不改。**A47历史没有完整索引/性能数据，需要一次真正native来验证A33工作问题。**

拟议**单次连续109默认资源GloVe Goal**（等待授权）：

1. **G0：** 只读核109实际原A47数据/env/ABI/输入/query/GT/预登记SHA和GPU锁/余量；复用旧env、禁新下载/安装，所有脚本纯CPU静态/逻辑检查完成再占锁。任务有独立工作区/output/预算。
2. **G1：** 原同一完整base(1,183,514×100 FP32)使用默认Resources/RMM/CuPy路径、`cosine/ivf_pq/degree64/intermediate128`**最多一次真实完整构图**；逐项合法资格，不重试失败。保存与加载同一索引（include_dataset=True或合法显式绑定），保留dataset owner，hash序列化文件，图view不能合法转换只记UNKNOWN。G0/G1不成功后面全部NOT_RUN。
3. **G2：** 对32个独立CPU全base canary做返回ID/距离正确性；至少校准6个固定配置（B1/B256 × AUTO/h9/h11），最多2个功能配置canary；只用2000 calibration queries按recall≥0.95、A/B差异≤0.005选择**一个**在两个batch均适用的h。固定后8000独立report queries校验各B、各臂真实recall，失败STOP、不放宽质量。
4. **G3：** 四正式点（B1/B256×AUTO/SMALL），2048不同report queries、3fresh processes、10ABBA/BAAB配对block，明确区分GPU预驻留输入的同步host search与CPU-ready→H2D→search→D2H完整wall，原始全部保留、同图同recall。AUTO胜或无显著完整差距为合法负结论；SMALL胜首先是已有软件启发式/状态组织差异，不直接宣称硬件SMEM/Cache机会。
5. **G4：** fail-closed raw/收据/变更Git一次发布、回读核commit/tree/blob/SHA、释放同一共享锁并STOP；不自动发新硬件机制或第二数据集。

**拟议累计额度（尚未获得本轮执行授权）**：node109单RTX4080，GPU锁非阻塞总≤45min；新下载/安装=0；新磁盘≤2GiB且原FS空闲≥64GiB；CPU≤4有效workers、RSS≤8GiB、VRAM≤12GiB；CPU准备≤30min，raw/summary≤64MiB；正式4点＋最多8配置canary。源码/输入/数值/资源/质量失败即STOP，不变更科学对象、包版本、driver或算法以挽救结果。

**按冻结数据计算的最低存储（非峰值）：** base原始FP32`1,183,514×100×4 = 473,405,600B`；degree64×uint32图`1,183,514×64×4 = 302,979,584B`；合计`776,385,184B≈740.42MiB`；预设新盘2GiB仅容纳一个序列化索引、log和较小缓存，**不是已证明够用的runtime/build峰值**。只要监控发现索引+cache/临时会超2GiB或VRAM12GiB，保存证据并STOP，不再要求重新下载/重做资产或超支。

**研究优先级：** 由于前期已花CPU准备成本但default tiny C0成功，下一次完整真实GloVe观察具有明确新增价值。然而它依然是图式ANN负载上的**软件组织/资源发现**，不必为了保持ANNS方向而允许无限vendor debugging。若真实完整构图再失败，终止该路径的当前版本/平台探针，随后独立选择A43点云稀疏卷积或其它硬件相关AI负载，不自动部署它们。

## 4. STOP与权限

A47、A47R1、A47R2历史执行已合法结束，本报告只是`A50_INDEPENDENT_REVIEW`。本轮没有调用109 GPU、改库、下载或建立新的运行权限。**准备独立下一Goal草案不等于授权它运行**；需要用户就上述45分钟GPU/2GiB新增文件等额度明确回复同意。用户要求减少轮次，因此只计划一次完整G0→G4连续执行，而不是将env、index、recall、wall切成四条审批。