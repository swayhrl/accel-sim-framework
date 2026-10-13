# 20小时无人值守｜Lane M A24：109 CPU侧GS-Scale安装前平台资格

**执行者：109既有Codex Lane M；全部CPU/read-only，绝对不用GPU。**  
**所属授权：** [20小时无人值守多Lane总计划](../ops/AI_ARCH_UNATTENDED_20H_2026-10-14_V1.md)。该Goal仅做CPU平台和现成依赖元数据查询，不能扩为GS-Scale原生训练、Torch/CUDA验证、模型下载或NequIP GreenContext实验。

## 科学目标

作者[GS-Scale fixed source `SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)当前README称**only Intel CPU supported**，`install.sh`以Python3.10、torch2.2.0+cu121、IPEX2.2.0为环境入口；论文称gsplat1.5.0/CUDA12.4/PyTorch2.2。我们109原Lane M环境为torch2.10+cu126，但**不能自动覆盖、升级或猜测主机CPU品牌**。

一次确认：这台109主机是否至少具有符合已发布GS-Scale源码要求的**CPU/ISA与独立环境空间条件**，并明确现有环境版本、潜在移植风险。结果**只能是静态资格/差距**，不是“已经成功运行或可重现训练”。

## 一次性只读检查（禁止导入Torch）

1. 新独立分支`hrl/aiarch-a24-gsscale-109-cpu-platform-gate-v1`与worktree，从总协调固定提交创建。核对旧Lane M A16R1 `6953ac1690b7a905b6000833a879f9164c7c9e43`及V1R1 `1f69559df4f51290589de72876f36a756c5439f0`均仍在原STOP，不动。
2. 只允许选择性只读命令：`/proc/cpuinfo`CPU vendor/family/是否AVX2/AVX512；`lscpu`指令集/核心数、内存与swap统计`free -b`、工作盘`df -B1`、操作系统ABI/glibc版本、已存在的Python解释器版本与已安装包发行版metadata。任何软件包检查用`importlib.metadata`或只读dist-info，**不`import torch`、不调用`cuda*`、不`nvidia-smi`、不加载任何驱动、绝不取得GPU共享锁**。
3. 从作者固定`README.md`/`install.sh`/`cpu_adam/src/cpu_adam.cpp`只读核CPU extension及OpenMP/编译器依赖；不能因为CPU型号是Intel就声称IPEX二进制、CPUAdam或整训练完整兼容。
4. 形成三列表：**已在109静态观察到**、**作者source所要求**、**为未来合法执行仍需运行验证**。判断是否可通过**另建隔离环境**达成而不污染现有NequIP/C16/AWMA；只写需预留的磁盘/内存条件，不能直接搭环境。
5. 资源不足、平台CPU不合或旧路径无法安全读取，则据实标`PLATFORM_INCOMPATIBLE_AS_IS`、`PLATFORM_VERSION_GAP`、`PLATFORM_RESOURCE_DEFERRED`或`SOURCE_ONLY_UNVERIFIED`。不能为了给“可运行”结果改代码/装IPEX/启用CPU-GPU模型。

## 单一报告与资源

唯一交付：
`docs/ai_workload_research/reviews/AI_ARCH_A24_GSSCALE_NODE109_CPU_PLATFORM_PREFLIGHT_V1.md`，不超过180行。明确实际CPU厂商/ISA和资源区间、现有Python/torch/IPEX发行版**仅元数据**、作者所需精确软件入口、compatibility caveats、是否需要Intel-only替代实现、下一步值得/不值得做的一个真实场景科学对照、所需新数据与GPU预算**仅提案不执行**。

- 设备影响：**CUDA初始化0、GPU显存分配0、GPU锁持有0、GPU kernel0、NCU/NSYS/NVBit0**。
- CPU最多1 worker、内存≤1GiB、新增worktree/log文件≤30MiB；最长**1小时**。不得下载模型、数据、依赖、conda/docker镜像、运行编译或安装`intel-extension-for-pytorch`。
- 本机检测所得原始stdout可能含hostname、IP、用户名、mount私有路径、账号/环境secret；**最终Git公开报告只能保存必要的非敏感CPU类别、版本及容量范围，不提交原`env`、SSH地址、路径或任何token**。
- GitHub来源读取若失败在同一Goal有界重试/本地cache复用；无权限读取就记录UNKNOWN/STOP，不跨节点找别人数据。
- 只在本独立分支提交、push、远端fetch-back commit/tree/blob后STOP，`UNATTENDED_20H_CLOSEOUT`列出完整状态。**不直接更新协调分支，不自动启动GPU或其它研究Goal**。

**目标结论：** 判断“GS-Scale源码目标109的CPU平台/包ABI能否在将来合法研究”，而不是让Lane M重新占GPU做环境调试。
