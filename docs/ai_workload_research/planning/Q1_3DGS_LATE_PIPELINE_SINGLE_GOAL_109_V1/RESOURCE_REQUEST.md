# Q1真实实验资源申请（尚未批准）

本页是可整体批准的具体申请。当前任务仅CPU定稿，未启动GPU/取锁。批准[一次性Goal](../../goals/AI_ARCH_Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1.md)时需要明确同意下表及实际执行窗口；历史48GiB与旧Image-Lab协议均不替代新资源许可。

## 依据和测算

A26GR1公开终态报告记录：两次真实0→15200推进、初期资格/编译及工程尝试累计持锁3734.497s（62.24min）；sampled进程树RSS26,337,488,896B（24.53GiB）、GPU3638MiB。不能简单除二当新运行保证，也不能以late每步133ms估算完整增密前缀。它支持为一个真实前缀加state/对照申请比30分钟显著更大的窗口。

本轮CPU一次只读元数据（epoch1793936967.3308907，未预约）：109总内存65454604KiB≈62.42GiB、当时MemAvailable58349812KiB≈55.65GiB；SSH helper own affinity0–23共24logical。workspace与/data同一文件系统，当时available149,102,342,144B≈138.86GiB。这些是瞬时capacity，不证明未来可用、不检查他人进程或GPU、不获得CPU/内存/磁盘保留。

## 请求整包上限

| 项目 | 新申请 | 理由与执行内资格 |
|---|---|---|
| 总Goal | ≤8小时 | 包含CPU工程/单测、合法asset/state资格、最长3h GPU、分析/IO与Git；不是占满目标 |
| GPU累计持锁 | ≤10800s（3h），单一连续窗口、一次非阻塞取锁 | 预算估算75min生产+30min保存/恢复+35min矩阵/诊断+25min工程/噪声余量+15min收口。只有总量为硬限，不因估算分项到点拆新Goal |
| GPU对象 | 109 RTX4080，固定UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59；一个owner | 其它型号/节点不替代；不访问164 |
| 自身GPU显存 | NVML≤14336MiB（14GiB） | 大于历史3.6GiB而为checkpoint/短诊断留空间；所有自身子context合计 |
| 外部共存 | 已接受受控Image-Lab resident+经认证桌面≤512MiB，门控/预约/实时活动完整 | 不是静态PID白名单；未知compute/失去quiescence立即停止自身 |
| 主机RSS | sampled进程树≤40GiB | 历史24.53GiB加实际loader/恢复/私有补丁余量；不允许全量clone主存state |
| charged memory | 保守上界≤48GiB | 优先私有delegated cgroup；否则经证明覆盖自身所有子树的共享祖先总current作保守观测，不用delta作own；owner需批准此观测方案 |
| 系统余量 | 准入MemAvailable≥50GiB，运行保持≥10GiB；不以swap扩容 | 全机62.42GiB下不申请64GiB独占；只停止自身，不干预其它任务 |
| CPU | owner指定≤16logical CPUs训练、另≤2logical轻量监督/分析 | 明确P/E/SMT/cpuset/NUMA；不要求64物理核，不默认独占整机24logical；配置T8/T16与可选J |
| 新增磁盘 | 私有总额≤64GiB；准入free≥96GiB、运行free≥32GiB | 同一FS合并计数，不能将/data和workspace当双份空间；最多2完整state槽+≤8GiB工具/raw/cache |
| checkpoint | 实测2S+8GiB≤64GiB，即单S≤28GiB | 不是估算出的state大小；stream/chunk≤256MiB、专用staging目标≤512MiB；不删moments/降精度节盘 |
| 下载/安装 | 数据/模型下载0、依赖安装升级0 | 原合法资产缺失记录STOP；已有隔离环境复用，不改生产runtime |
| 工具权限 | CPU工程、私有源补丁、实际状态保存恢复；必要时已有合法API/一段隔离timeline/少量counter | 不自动改系统Profiler权限、全局频率/功率、驱动或库；不可用可跳过可选工具 |
| 收口 | 预算内保留15min规划余量 | 不启动无法完整结束的区组；安全暂停/已提交工作完成、私有state与raw、全部清理和资源收据 |

RSS为离散观测；V7合法退出竞态保留censored，不填0、不宣称完整instantaneous峰值。若无私有cgroup硬max，shared current只是采样保守上界，不声称内核硬隔离；须记录memory.peak/events等实际可取范围，不能重置共享ancestor指标。真正不可恢复的观测缺口停止GPU。

运行内自身VmSwap相对准入增长超过64MiB即停止新工作并收口；系统swap已用不等于本任务使用，host pswpout只作保守辅助观察。MemAvailable或shared charged因他人变化触限同样停止自身，不调整其它进程。

## 需要用户/资源所有者批准的内容

1. 上述0→晚期自然训练、完整state生产/恢复及最小对照作为一个连续Goal，含私有checkpoint/observer/thread-policy工程。
2. 109一个最长3h合法GPU窗口、共同flock与现行Image-Lab门控共存；不是允许重启/部署Image-Lab。
3. 主机40GiB RSS / 48GiB charged预算、明确CPU集合与cgroup/保守观测方案；它们不是历史权限自动延续。
4. 私有新增64GiB与至少32GiB系统余量，允许仅轮转本Goal自己的临时恢复文件；旧资产不得清理。
5. 总Goal8h及预算内必要的既有工具诊断；不涉及下载、安装、系统设置、第二scene或硬件/模拟器。

若批准的数字更小，执行前必须重新计算单state与前缀可容纳性并冻结合同，不能暗中接受缩预算后必然重复STOP的方案。资格可在同Goal内部判定；缺合法state不再要求另批“先准备状态”，而直接走已批准自然推进分支。若原数据/环境消失或共享安全不成立，归档STOP，不擅自放宽或新增下载。
