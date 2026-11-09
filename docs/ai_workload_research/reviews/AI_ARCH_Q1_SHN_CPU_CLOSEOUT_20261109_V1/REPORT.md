# 109-AI-ARCH Q1 shN V1：CPU-only 收口增量

本报告只补充固定执行结果 `2838e93cfc129183d7d727e80eccc1b2f577a82d`；旧提交、`PREFROZEN_CONTRACT.md`、用户 Goal、失败证据及私有原件保持原位。本轮没有恢复 GPU Goal、运行真实 Runner 或增加正式样本。

## 科学状态与执行状态

按本轮用户裁决，接受**该具体实现的描述性退化**及**本次资源窗口内有范围的容量可运行**。数值只接受四步短窗的确定性采样范围；可见数、更新数有微小波动，不登记全状态逐 bit 或长程质量等价。ON 逐操作诊断缺失，成本转移和退化的机制归因仍未闭合；维持 `NO_HARDWARE_CANDIDATE_PROMOTED`。AlexNet 下载偏差保留，不能登记全项合规 PASS。

109-AI-ARCH 两个 GPU 窗口已停止，原执行收据记录共同锁、预约和自身 GPU 上下文释放。W1/W2 持锁分别为 `274.805770` 与 `2753.310824` 秒，累计 `3028.116594/5400` 秒。本轮补丁只在新隔离分支中，未回写旧执行 HEAD。

## AlexNet 偏差追溯

| 事项 | 证据与结论 |
| --- | --- |
| 触发链 | 冻结 trainer `simple_trainer_hybrid_optimized.py` 第 517–520 行初始化 `LearnedPerceptualImagePatchSimilarity(net_type="alex", normalize=True)`；TorchMetrics 1.3.2 `lpips.py` 的 `AlexNet` 默认 `pretrained=True`，经 torchvision 0.17.0+cu121 的 `AlexNet_Weights.IMAGENET1K_V1` 走预训练权重加载。W1 首个 OFF worker 日志明确记录 `https://download.pytorch.org/models/alexnet-owt-7be5be79.pth` 下载。 |
| 本机资产身份 | 原私有路径 `.private/cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth`；`244,408,911` 字节，SHA-256 `7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02`。文件仍在 109-AI-ARCH 原目录，未复制进 Git、未删除。哈希前缀与文件名一致，且新预检函数对原文件的 CPU 回读通过。 |
| 时间关系 | W1 首个 OFF worker 于 **2026-11-09 04:38:34 PST** 启动；文件创建于 04:39:02、末次写入于 04:39:16。W1 ON 于 04:42:04 启动；W2 首个 worker 于 04:48:27 启动；首个正式样本于 04:56:55 启动。下载日志没有绝对传输起止时间，因此只断言下载发生于首个 OFF worker 内、文件在 W1 ON 和所有正式样本前已写完；下载没有计入正式闭合窗口。 |
| 各配置使用 | 原 `q1_supervisor.py` 每个 worker 均设置同一私有 `TORCH_HOME`；两种配置共用未改的 trainer LPIPS 初始化。36 个 worker 日志中只有首个 W1 OFF 记录 `Downloading:`，其余未记录下载。由共同路径、文件写入时序及成功退出，支持 W1 ON 与 W2 OFF/ON 从缓存加载同一文件的解释；旧执行没有逐 worker 已加载张量哈希，严格逐次字节身份证明为 **unknown**。 |
| 预检缺口 | 原 `prepare_binding.py` 核 gate、原状态 manifest 与资源 binding，但没有检查 LPIPS 辅助权重。原监督器给 worker 设置空私有 `TORCH_HOME`；`HF_HUB_OFFLINE=1` 和 `TRANSFORMERS_OFFLINE=1` 不约束 torchvision/Torch Hub 的下载路径。原 worker 在 CUDA 初始化后才加载 trainer，缺件没有在取锁或 CUDA 前被拦截。 |

这违反用户 Goal 和冻结合同的“不下载模型”要求。原收据 `COMPLETE_WITH_DISCLOSED_DEVIATION` 保持，不把下载追认为事前授权。更细来源、原件路径与哈希见 [EVIDENCE_INDEX.json](EVIDENCE_INDEX.json)。原私有 W1 收据和首个 worker 日志不在 Git；本轮只发布小型索引及必要事实，不搬运 raw 或模型文件。

## 两窗口授权与续行核实

用户派发的完整 Goal 明确写明：“用户将本完整Goal作为正式GPU执行指令发送时，授权本合同明确列出的109 GPU工作与资源预算。”其资源表写“非阻塞GPU资源窗口：最多2个顺序窗口，累计预算不重置”。紧接着的**条件句**写：“只有前窗口已完全清理、存在本Goal允许修复的自身工程问题、资源owner重新批准实际时段且新的非阻塞准入成功，才可使用第二窗口。”这些是不同层次：`最多2窗`是上限，不能单独作为 W2 启动许可。

W1 私有资源收据为 `QUALIFICATION_WINDOW_COMPLETE`，两位 worker 均零退出，锁、预约、自身 context 均释放；W2 binding 记录 `window_id=W2`、剩余预算 `5125.194230` 秒，并从同一用户 Goal 继承通用 `authorization` 字符串。W2 已取得新的非阻塞锁/预约、通过门控并完成 34 个 worker。`prepare_binding.py` 检查了 W1 清理、预算及 gate，却没有记录“资源 owner 重新批准实际时段”的独立来源；已核对的用户续行消息和小型执行记录中也未找到该额外批准。W1 自身状态为资格完成，并非一份明确的工程失败回执。下载偏差存在，但 W2 前没有离线预检或外部下载保护修复，W2 只是复用已下载缓存。

旧 `PREFROZEN_CONTRACT.md` 另写首个资格通过后可在释放当前锁/预约后取得新的有界资源。它证明了执行计划的意图，**不能替代用户 Goal 对 W2 的额外条件**。因此 W2 的累计预算、清理和实时准入有记录，额外 owner 时段批准及“允许修复的自身工程问题”这两项条件的满足情况 **未证实**；记为解释/授权链偏差，不倒改原合同，也不凭空判定绝对没有口头批准。这个缺口不抹去已采集样本，但阻止“全项合规 PASS”。

本轮用户说明“174接班已接受”，本报告按用户当前裁决登记该状态。独立的 174 接受原文或 Git 固定 commit 未在本轮已核对材料中定位，故不虚构其签名或时间；所需小型关闭证据以索引绑定 109-AI-ARCH 原 W1 收据、首个日志、W2 binding 与现有 Git 收据。

## 离线预检与下载保护补丁

本轮新分支 `util/ai_workload_research/q1_shn_residency/offline_asset_guard.py` 固定 AlexNet 文件名、大小、SHA-256，缺件、大小/哈希不符或符号链接均在 GPU 预约、取锁、NVML 之前给出 NO-GO。worker 在 CUDA 初始化及 trainer 导入前再次核验，并安装 Python socket/DNS 及 urllib 外部 URL 阻断：非回环连接与外部 URL 失败；`localhost`/`127.0.0.1`/`::1` 与 AF_UNIX 本机 IPC 可用；移除 worker 的代理环境以免本机代理转发外部下载。保留原 LPIPS 和预训练权重语义，不以 `pretrained=False` 绕过依赖。保护范围是该 Python worker 的网络路径；不宣称系统防火墙或任意子进程都被隔离。

纯 CPU 验证：`python3 -m unittest -v test_offline_asset_guard_cpu`，3 项通过，覆盖缺件/错哈希/错大小/符号链接、外部 DNS 与直连拒绝、回环 HTTP 门控和 AF_UNIX 可用。`py_compile` 通过。独立 CLI 对原本机资产的 SHA-256/大小回读通过。没有导入 torch、初始化 CUDA、运行真实 Runner 或下载文件；该补丁的实际 GPU 执行效果未在本轮测试。

## 仍待审查

AI-ARCH-5/174 可据此区分科学结果与协议状态：描述性净退化和容量有范围成立；短窗采样之外的数值等价、ON 逐操作机制归因、W2 额外时段批准原记录及逐 worker 已加载权重哈希仍未闭合。本轮 CPU-only 增量完成后 STOP，不启动 V2、Profiler、额外样本或其它 GPU 工作。
