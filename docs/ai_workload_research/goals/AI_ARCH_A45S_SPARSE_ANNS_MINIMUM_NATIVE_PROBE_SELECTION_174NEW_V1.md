# A45S｜174-new：点云稀疏卷积 vs GPU ANNS最小原生实验选择（CPU/source-only）

**任务性质：科学决策收敛，而非重复A43大文献调研。** 用户同意A44后并行高效推进，本Goal只允许已有源码和论文的CPU/source-only资格与合同设计，不意味着允许GPU/模型训练/下载。独立新Codex窗口，node174-new，与A45H/node109完全独立。

Repository `swayhrl/accel-sim-framework`；branch `hrl/aiarch-a45s-next-probe-admission-174new-v1`；发布后的Goal提交SHA作为冻结入口，共同parent `8446f14595d2b084f5bcaea7b0ff4eac4d029a5d`。依次读 `docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、`literature/AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md`、`literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md`、`reviews/AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md`。前述所有冻结报告只读。

## Q-S45

**只在两个已确定的真实候选中选出一个更值得下次占109 GPU的、可在现有4080上强软件有效的最小probe**；不能把技术新颖性假设当事实。候选：
- **Q-S** 点云稀疏卷积：强Spira后，在真实空间坐标＋实际层组的完整结构生成/布局/使用寿命中，是否仍有不得不付的时间/资源组织成本？固定 `SPIN-Research-Group/Spira@aee69c61f3e001f72828a6d5a70f6a1200166f65`，以及A43已有TorchSparse++/Minuet/Insum强近邻；Spira官方MLSys26 artifact建议64GB主存/256GB存储/16GB GPU，不意味着单个small probe必须如此；而没有授权时**不得**拿真实Waymo/ScanNet/其他licensed scene下载。
- **Q-A** ANNS搜索：固定 `NVIDIA/cuvs@bc23aa84a0ef26d85900185ad5e68d3372be487e` 和A33 GloVe100真实查询/ground truth数据入口；CAGRA SMALL/HASH/AUTO、实际alg/CTA/清表间隔同时变化，不能冒充改变物理SMEM的单变量实验。保留同recall约束，不能复用旧CPU ANN榜单冒充GPU强基线。

## 连续G0→G3

**G0资源与权限：** 单个174-new独立worktree/output/tmp，CPU≤2 workers，RSS≤3GiB，新增文件/缓存≤40MiB，≤2h有界STOP；不访问109/164、GPU共享锁或其它正在执行的工作区，不进行CUDA/Torch导入、torch.cuda、依赖安装、JIT、模拟器，不下载场景/权重/向量数据或PDF大包。旧174 swap压力高先读resource，资源差时`RESOURCE_DEFERRED_STOP`。无需为管理状态开额外Git修补轮。

**G1锁定一个最小真实研究对象：** 从A33/A43已核源码直接给出每项具体输入源、强软件、精度/可比较的数值或recall、目标GPU与已知 ABI/driver要求、实际准备/计算完整边界；只审**阻塞下一次实验的缺口**。数据身份/source不等于input bytes已下载；只列必要bytes和许可证。对于Spira优先选最小公开/可合法获取的真实坐标，注意其loader可能为真实坐标＋synthetic特征，不可称实际训练模型质量。对于ANNS固定同一graph build与同recall的query，不能将AUTO路径切换混作物理资源。

**G2冻结实验投资筛选矩阵：** 每候选按(1)原生平台与依赖能否有界准备，(2)数据/数值权威，(3)最强合法实现，(4)诊断是否能真正区分软件与物理资源，(5)新增下载/盘/GPU锁时间，(6)独立holdout/负例保留排序。**明确拒绝为了“有GPU实验”在原场景上做弱baseline。** 不必先安装Spira的全套benchmark/下载三类scene，不要做无期限feature matrix。没有决定性证据时标UNKNOWN并按低成本选或NO_GO。

**G3输出最多一份未来GPU发现合同的草案（不执行）：** `ONE_SELECTED_PROBE_OR_NO_GO`，一个模型/数据源、最多两条强路径、≤12个发现点（可以更小）、明确首次功能/数值canary、完整wall、资源上限建议、计时/采样配对方法、只读/安全安装门、失效立即STOP规则。GPU预算、网络与存储只是**建议上限，不是授权**；需要实际用109时由用户单独确认并保留现有共享lock非阻塞。没有合法strong source/同recall或数据门，即正式`NONE_SELECTED`，不硬凑候选。

唯一报告：`docs/ai_workload_research/reviews/AI_ARCH_A45S_SPARSE_ANNS_ONE_PROBE_ADMISSION_174NEW_V1.md`，≤260行。仅当为计算容量/实验格数确有必要附一个小JSON；不得开发新benchmark/重复已有十轮文献索引。报告说明不能声称hardware headroom、不可自动进入GPU。普通URL/path小问题可同Goal有界解；严守所有历史STOP，别跨branch merge。完成commit/push/fetch-back exact SHA/tree/blob、clean后STOP。