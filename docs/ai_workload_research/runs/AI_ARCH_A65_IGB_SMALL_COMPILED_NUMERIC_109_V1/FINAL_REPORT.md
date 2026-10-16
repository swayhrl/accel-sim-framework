# A65：锁外磁盘资格失败，BUDGET_STOP

本轮科学终态 **BUDGET_STOP / FREE_FS_BELOW_64_GIB_AT_CPU_ADMISSION**。未申请 GPU 锁，未初始化 CUDA，未采样 minibatch，未执行 eagerA/eagerB/compiledC。数值资格与差异分类均 **NOT_RUN**，不是编译路径的正面或负面数值结果。

用户已明确批准 A65 最小诊断与合同预算，覆盖 Goal 历史待派发状态。执行分支 `hrl/aiarch-a65-igb-small-compiled-numeric-109-v1`，固定启动 `afe42345c4b0c45b3e09f3cb32ce4e3e0de09989`。新建独立 worktree、输出及 CPU 审计脚本，没有 merge 协调分支，也没有执行旧 A61 runner。

## 实际停止条件

CPU admission 的 `shutil.disk_usage` 实测可用 **67,234,635,776 bytes = 62.617134 GiB**。合同要求保留 **68,719,476,736 bytes = 64 GiB**，已缺 **1,484,840,960 bytes ≈ 1.383 GiB**。第二次 `df -B1 /data/c16` 同样低于门限，原始输出在 `raw/df_cpu_admission.txt`。这是数据盘所在文件系统的实际剩余空间门，与本任务自身新增文件是否小于 128 MiB 是两个独立要求。

没有删除旧文件、换盘、放宽门限、等待竞争资源或尝试 GPU。CPU admission 失败后仅进行小型证据归档，没有继续完整 payload/library 哈希、建立运行环境、比较器单测或 GPU runner。

## 已完成的 CPU 审查

完整读取 A65 Goal、原 A61 Goal/FINAL_REPORT/失败 JSON/原始 compile log、native.py/native_utils.py，并额外核查危险的 common.py/gpu_supervisor.py 与旧 sitecustomize。A64 独立审查从固定 `326dcac6227d1c1af6b38e4f76d21566525f35aa` 读取，没有 merge。所有所引 Git blob、SHA256 和大小见 `AUTHORITY_IDENTITY.json`。

科学父 A61 commit `37120f98186b83a946f4812755523f5d73245491` 的 tree `d13b446ca4824cb3ad7ffae25b5ce91c023b75a1` 已核验。原执行源码字节与该固定提交一致。原代码编译的是 `train_step` 函数，模型本身未替换成编译包装对象；失败谓词是参数名匹配与 allclose 的复合条件。旧第二名字、初态 SHA、compiled gradient/update delta 未捕获，仍为 UNKNOWN，不能据此宣称 Torch bug。

静态识别到原 eager canary 与 compiled 重用之间存在 cache 功能重放，缺少输入内容与生存期的前后闭合记录。新任务必须独立冻结唯一自然 batch、显式验证独立模型/optimizer 初态，分别记录名称/shape/dtype 和数值门；本轮没有进入这些 GPU 检查。

原 common.py/supervisor 向 A61 输出；旧 sitecustomize 的写入允许范围也硬编码 A61。三者均未运行或 import。A65 CPU 审计只用系统 Python 标准库，不 import Torch、DGL、NumPy 或旧环境。

原 IGB feature/label/edge、派生 CSC/edgekeys 文件均实际存在，大小与 A61 接受记录相符；split/order/environment 路径存在。但完整新 SHA 门因资源 STOP 未执行，不能填为本轮 ASSET_PASS。`ASSET_PRESENCE_ONLY.json` 明确区分旧接受 SHA 与本轮未重算字段。

旧 A61 全目录前后 lstat mode/size/mtime_ns/链接目标清单一致，见 `READONLY_CHECK.json`；完整清单留在独立 A65 私有输出并绑定 SHA。该检查是 metadata 级保护核验，不能冒充全部文件内容重哈希。没有写旧 A61 STOP、源码、raw、模型、cache 或环境。

## 各门与资源

| 门 | 实际结果 |
|---|---|
| 固定 branch/HEAD、A61/A64 authority、旧失败 CPU 源审查 | PASS |
| payload 存留 | 文件存在、大小匹配；完整新 SHA 资格 NOT_RUN |
| G0 磁盘 admission | FAIL：可用空间低于 64 GiB |
| 新比较器单测、运行库全量核验与 GPU runner | NOT_RUN，停止在此前 |
| G1 自然 frozen B1024 / 初始模型与 optimizer 身份 | NOT_RUN |
| eagerA / eagerB / compiledC | 全部 NOT_RUN；各 0 样本、0 更新 |
| loss / gradient / parameter-update 差异 | NOT_RUN，没有补造数值 |

GPU 锁申请 **0**，持锁 **0 s**，GPU 子进程 **0**，任务显存使用 **0**；没有通过 NVML/CUDA 探测 GPU。资格更新 **0**、工程 retry **0**、正式训练 **0**。科学数据/依赖下载 **0 bytes**、安装 **0**；仅执行任务要求的 Git 来源与审查提交 fetch。

CPU 审计固定 affinity `0,2,4,6`，标准库串行运行；审计自身 `ru_maxrss` **64,520,192 bytes ≈ 61.53 MiB**，约 **4.90 s**。这是该 CPU 进程的峰值，未冒充未运行的 GPU 任务树测量。独立 worktree+私有输出的实际 allocated bytes、最终空闲空间及 Git 增量记账在 `RESOURCE_RECEIPT.json`；没有生成新 venv、特征副本或编译 cache，新增文件远小于 128 MiB。

## 未完成事项及停止

A65 的同 batch 数值问题全部未执行；旧 A61 STOP 保持原样。本轮无强软件性能、供数瓶颈或硬件收益结论。首先需要由资源所有者使该文件系统重新满足至少 64 GiB 空闲，并给新任务输出留余量；本任务未授权清理历史资产，也不会自动重试。之后是否重新派发 GPU 数值诊断，交独立审查决定。

输入归属：Contains information from Illinois Graph Benchmark (IGB), Khatua et al., KDD 2023，按原 A61 固定来源及 ODC Attribution License 1.0 的已接受本地数值使用范围只读引用；不重新分发原始数据或宣称全面内容权利保证。

本分支独立归档 CPU 源审查、实际 STOP、原始资源输出、锁零占用收据和 SHA256SUMS。只 push 本分支；发布后 fetch-back 核 exact commit/tree/每个新增 blob 与 SHA、worktree clean。最终发布 SHA 与 readback 收据保存在 A65 私有输出并随最终回执提供，避免提交自引用。完成后 STOP，等待独立审查，不自动启动后续任务。
