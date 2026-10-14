# Round A48｜A47 GloVe/CAGRA有界原生实验独立审查：平台NO-GO与stream分配源审

**审查者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14；协调基点：`e3a8f1e08592664c3c7b8742c23a978b9fe548d4`。**

## 0. 独立科学裁决

**`ACCEPT_A47_PLATFORM_OR_ASSET_NO_GO / INPUT_QUALIFIED_NATIVE_CAGRA_BUILD_UNQUALIFIED / STOP`**。

本轮直接从GitHub固定commit读取原A47完整报告、GATES、RUN_IDENTITY、ENV_LOCK、输入与CPU质量、工具脚本、资源回执及GDB原始栈；独立复查NVIDIA/CUDA、cuVS及RMM的固定源码和官方版本兼容说明。**原终态保持`PLATFORM_OR_ASSET_NO_GO`，并收窄说明：本次实际阻断是`NATIVE_BUILD_API_SIGSEGV`，不是已检出的GloVe资产错误。**

- **G0合格范围**：24官方wheel/完整版本和SHA、Python3.12.3、CUDA12.9栈、cuVS 26.10.0发行内嵌源码提交`24ee1bf1cb17cad0ac611e39643af39ee1870124`、隔离安装的版本身份、设备读取和基础CuPy算术。**G0的PASS不是CAGRA构图ABI在真实执行时已合格**。
- **G1合格范围**：官方GloVe100-angular HDF5实体485,413,888B，完整下载后本地SHA256 `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`；1,183,514×100 base、10,000 query及top100 GT；32条query的全base CPU cosine参考与原GT第10距离最大绝对偏差`1.5522863217e-08`。**此为CPU输入/质量身份canary，不是CAGRA GPU数值/recall**。发布方未给事先签发的HDF5 SHA，本SHA仅是本次来源字节identity。
- **G2合法STOP**：唯一完整GloVe图构建`metric=cosine, build_algo=ivf_pq, graph_degree=64, intermediate=128`确实调用而SIGSEGV(exit -11)，没有生成/保存index。另一个许可内1024×100合成API诊断，在CUDA向量及`make_device_padded_dataset`功能通过后，调用相同CAGRA IVF-PQ build API再度SIGSEGV。因此失败**并非仅因118万向量数据规模或磁盘容量**；仍不可排除流、分配器、版本链接、特定接口组合和CAGRA内部调用路径因素。
- **G3严格NOT_RUN**：四个正式B1/B256×AUTO/SMALL样本均0，recall、calibration、真实搜索时间及算法/片上资源效应未测。不能将此NO-GO称为ANN工作负载没有硬件空间或AUTO强软件充分。
- **G4合格范围**：39个新增文件，仅本次run证据和`tools/aiarch_a47`，无改动旧authority；执行branch与最终commit identical。执行侧记录锁已释放、无新Goal、原实验worktree干净，本窗口未SSH追踪。

## 1. Git身份与已取原始证据

- Branch: `hrl/aiarch-a47-cagra-glove100-native-109-v1`
- Goal parent: `26ef7b20172495f26ed53248bfab792ae8af9040`
- Final commit: `ce92807ca80e1a694e41376eab3dd6b146824fd8`
- Tree (Git-data重新查询): `40e873ed2ff07359d54ce75d2440ee1f789beadc`
- Final report blob: `d3f8a6b6831235225452d7872a9f1e8ead30a595`
- [固定FINAL_REPORT](https://github.com/swayhrl/accel-sim-framework/blob/ce92807ca80e1a694e41376eab3dd6b146824fd8/docs/ai_workload_research/runs/AI_ARCH_A47_CAGRA_GLOVE100_109_V1/FINAL_REPORT.md)、[GDB原始栈](https://github.com/swayhrl/accel-sim-framework/blob/ce92807ca80e1a694e41376eab3dd6b146824fd8/docs/ai_workload_research/runs/AI_ARCH_A47_CAGRA_GLOVE100_109_V1/raw/small_api_gdb.log)、[native.py](https://github.com/swayhrl/accel-sim-framework/blob/ce92807ca80e1a694e41376eab3dd6b146824fd8/tools/aiarch_a47/native.py)、[api_fixture.py](https://github.com/swayhrl/accel-sim-framework/blob/ce92807ca80e1a694e41376eab3dd6b146824fd8/tools/aiarch_a47/api_fixture.py)。

接受原资源回执：下载3,128,933,154B（≈2.914GiB；科学数据485,414,912B＝0.452GiB，计数口径包含少量下载控制字节）、新增盘7,895,879,680B（≈7.354GiB）、RSS采样峰1,496,051,712B（≈1.393GiB）、GPU锁累计4.115s、显存采样峰752MiB、CPU准备3,620.57秒，均未突破原累计硬限。诊断极短，不能把采样未观测到显存当峰值为零。

## 2. 崩溃定位：已知真实调用链、仍未知根因

GDB诊断的第1线程栈（caller→callee）：

`libcuvs cuvs::neighbors::ivf_pq::build → rmm::_RMM_26_10::device_buffer::allocate_async → rmm/pylibrmm/memory_resource/_memory_resource.abi3.so → libcuda cuStreamGetId → SIGSEGV`。

**本轮新独立源码印证：**
- 冻结[RMM v26.10.00 `stream_ordered_memory_resource.hpp`](https://github.com/rapidsai/rmm/blob/v26.10.00/cpp/include/rmm/mr/detail/stream_ordered_memory_resource.hpp)（blob`e2655e2fb2d8a61654ab18d79062d49e36a19a6b`）的`get_event(cuda::stream_ref)`在非默认stream分支查询`cudaStreamGetId(stream_to_store, &stream_id)`，由CUDA runtime经驱动路径进入`cuStreamGetId`是合乎源码调用层次的解释；这与GDB栈相符，**但GDB没有提供崩溃时完整stream实参与对象生命周期，本窗口不宣称已证明是哪一个stream或具体源码行导致崩溃**。
- [RMM v26.10.00 `device_buffer.cpp`](https://github.com/rapidsai/rmm/blob/v26.10.00/cpp/src/device_buffer.cpp)（blob`345dd4588e3829efe7eb066337f7986c04b90b46`）的buffer分配确实经`_mr.allocate(stream(), bytes, alignment())`。
- [cuVS v26.10.00 CHANGELOG](https://github.com/NVIDIA/cuvs/blob/24ee1bf1cb17cad0ac611e39643af39ee1870124/CHANGELOG.md)（blob`434b97f8a21a57ba10a91dc62f506b3a249f7f59`）声明了`rmm::cuda_stream_view`至`cuda::stream_ref`的stream API迁移；这是需要核对的**兼容性近邻线索**，不是已定位该PR引入的回归。
- [CUDA 12.5 Driver API `cuStreamGetId`](https://docs.nvidia.com/cuda/archive/12.5.0/cuda-driver-api/group__CUDA__STREAM.html)允许合法普通stream及特殊stream，说明无效stream句柄可导致undefined behavior。看到`libcuda`栈顶不代表NVIDIA驱动有根因。
- [NVIDIA CUDA兼容性指南](https://docs.nvidia.com/deploy/cuda-compatibility/latest/why-cuda-compatibility.html)明确较新driver支持较旧toolkit；本机Driver API13000 / runtime12090不应**仅凭数字不相等**就诊断为错误，真实二进制链仍待审。

**程序当时的合法软件设置**：固定原[api_fixture.py](https://github.com/swayhrl/accel-sim-framework/blob/ce92807ca80e1a694e41376eab3dd6b146824fd8/tools/aiarch_a47/api_fixture.py)显式创建`rmm.mr.PoolMemoryResource(CudaMemoryResource,512MiB,10GiB)`，设置当前设备资源及CuPy allocator，再建`cupy.cuda.Stream(non_blocking=True)`及`cuvs.Resources(stream=stream.ptr)`；`stream`对象在Python作用域内保留。cuVS发行源码`resources.pyx`本身给出`Resources(stream=cupy_stream.ptr)`示例，**不能根据用了非默认stream本身就判用户程序错误**。数据准备成功，进入CAGRA build之后资源分配失败；需要由独立合法控制区别allocator/pool与显式stream/handle变化。

## 3. 当前科学状态与下一步成本策略

**A47原STOP保持，不返工，不把用户之前授予的A47额度视为自动延续到R1。**

如果未来**单独明确授权**做一个`A47R1`最小工程恢复，推荐先复用已保留109的原冻结wheel/HDF5/venv和共享锁，限两个独立fresh-process的**小型synthetic API构图canary**（不得再次整GloVe构图）：(A) 官方cuVS/RMM默认resource/默认stream最小路径，(B) 在(A)通过时只改变一个resource或stream条件以定位差异；具体两臂前须CPU/source核确ABI和对象生命周期。零驱动/核心版本升级、零科学数据下载/重建、无新增正式性能点；GPU锁≤5分钟、RAM≤2GiB、VRAM≤2GiB（需现场资源资格和原锁非阻塞）。若不能先建立互不混杂的两臂，或两者都崩溃，就以`PLATFORM_STILL_UNQUALIFIED`STOP，不在同一任务无限试6种RMM组合。任何API通过只能证明小fixture wrapper/版本条件可执行；**恢复原118万base完整构图和4正式点需要新授权与完整数据/质量门**。

**价值判断：** 已取得的真实GloVe资产和完整包闭包值得保留，不应因为一个vendor堆栈崩溃就销毁；但AI-ARCH的P01/P13硬件问题未获得新增数据。下一次投入应先问“是否值得花一小步排除RMM/stream wrapper”，而不是为了完美复现无上限调试cuVS。候补点云稀疏卷积Q-S仍未授权；不要因为cuVS失败就自动切换Spira大环境。A44 3DGS CPU软件反证、A45H、A30T/N等冻结结论不变。

## 4. 证据和能力边界

本窗口只连接GitHub读取版本固定文件与公开官方CUDA文档，不读取109现场内存或运行`cuStreamGetId`，因此GDB中没有register dump/崩溃时指针，无法证实invalid handle、ABI二进制布局、pool内部资源生命周期或驱动bug。未取得cuVS G3性能，不可据此判断本地cache/SMEM/occupancy。该review是独立source/Git判断，不是新的硬件或GPU测量。