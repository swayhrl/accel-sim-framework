# AI-ARCH Q1｜真实早期状态已取得，监控工程异常后合法收口

日期：2026-11-07（Asia/Shanghai）。

**执行终态 INPUT_OR_RUNTIME_NO_GO，具体原因为 MONITOR_OPTIONAL_VMSWAP_FIELD_LIFECYCLE_DEFECT。科学结论 INCONCLUSIVE；NO_HARDWARE_CANDIDATE_PROMOTED。** 本轮真正启动了GPU并完成早期自然训练，但没有完成晚期实验。不是锁冲突、GPU资源被拒绝、3DGS性能负例，也不能称完整恢复资格或研究矩阵通过。

冻结合同34a598f4e5f40fffde337ae6b167bd4ffb3fccac / tree6f705347ec2ca9aca1405ea7515db23f78019b6e已获用户明确批准。此次独立执行分支hrl/aiarch-q1-3dgs-late-pipeline-native-109-v1；8h/10800s GPU等上限不扩额。协调HEAD核对仍66b2dffc6141edf1c9f9f089091b3922556583f1。GS原authority cf80f6e及全部历史raw/合同只读，没有重做文献或旧实验。

## 实际发生了什么

1. 只读原GS-Scale关键文件SHA一致；原Torch2.2.0+cu121/IPEX2.2.0及CPUAdam扩展c451fda…复用，未安装升级。原1678张4×预处理图像的登记尺寸全匹配，三处抽样SHA匹配；继承已接受的完整输入身份，没有重复hash9.77GB归档。
2. 实际训练亲和8–21（14logical/10个拓扑core），监督22–23；均在自身kernel允许0–23与用户上限内，自身child继承readback通过。不声称独占CPU，排除0–7，不修改其它进程。cgroup采用root-owned独立SSH session，初始成员仅监督器及祖先，子进程继承；读取current/peak，无可写memory.max，不伪称内核硬隔离。
3. CPU预检175项实际测试通过，另2项Qwen专属static test明确不适用，由Q1原语句AST/实际监督器测试替代；重复运行不重复累计为独立测试。覆盖loader14、store27、Q1监督器30、observer12及继承监控/门控等。初始失败与修复日志保留。
4. 唯一一次fcntl.flock(LOCK_EX|LOCK_NB)成功，预约及Image-Lab运行版本/实例/loaded gate/quiescence、GPU UUID、桌面与活动准入通过。一个owner串行执行，GPU持锁437.8034826023504秒。没有发生第二次取锁。
5. EARLY首次attempt因私有TMPDIR过长，DataLoader AF_UNIX socket路径超限而无法交付首训练batch。监督器没有资源安全失败；root核验自身worker PID/UID/start/boot/实际解释器及PGID后仅终止自身进程组。用指向本轮private tmp的短alias修复并做CPU socket bind验证，在同一持锁窗口继续EARLY_R1，旧失败日志和精确执行源码保留。
6. EARLY_R1按原算法自然执行step0至7、next_step=8，N=1,694,315。写出C_E(next5)和C_R_E(next8)，源nominal max_steps仍200000，未关增密或改CPUAdam。完成端点6个参数及18个optimizer浮点字段有限性检查；pending梯度未被强制apply。
7. 随后监督器在读取自身进程status的VmSwap字段时，next(...)触发StopIteration。具体失败PID没有被原代码持久化，因此只能说与退出/无mm字段竞态相容，不能断言已证明某个zombie是根因。这个缺字段处理是本轮新增监控代码的工程缺陷。
8. 外层finally已停止/回收自身执行，NVML最终观测无自身context，释放共同锁和预约。该异常自动结束了窗口，固定合同只允许一次取锁，剩余预算不能用于再次获取GPU。后续只在本Goal内做CPU修复、核验与归档。

## 已保存的真实状态与资格

| 状态 | next_step | 原始storage字节 | 资格 |
|---|---:|---:|---|
| C_E | 5 | 1,621,583,583 | 44Tensor/44storage；全部chunk、metadata、manifest、sidecar、公开index绑定通过 |
| C_R_E | 8 | 1,657,910,947 | 同上；CPU已apply至step6，step7梯度pending，step8 camera已准备 |

两态均包含模型/grad、CPU/GPU optimizer moments/counters、strategy/schedulers、15个跨步live值、loader排列/cursor、RNG、stable IDs与frontier。独立检查不使用load_state、Torch、pinned allocator、CUDA或NVML。每态3项pending梯度与6项浮点live storage的dense完整覆盖得到证明；NumPy流式有限性检查无NaN/Inf。

**这些是保存内容与字节完整性证据，不是实际GPU恢复PASS。** 没有执行初始runner重建精确比较、不断流vs恢复或A/A continuation，因此restoration_scientific_pass=false。它们也不是late checkpoint，尚未经过增密/剪枝轨迹或晚期规模验证。大型状态仍保留在本轮private目录，仅Git发布SHA/index。

## 未执行的科学工作

- C_D/C_V晚期状态及0→15140/15240连续推进：NOT_EXECUTED。
- T8/T16正式对照、J策略、observer OFF/ON配对：NOT_EXECUTED。
- 正式样本0；FORMAL_SAMPLES.tsv仅表头；median、MAD、加速比均不计算。
- 实际传输payload、GPU服务、CPU扫描/Adam/转发、主线程等待并集：NOT_MEASURED，字段为null而不是0。
- 自然camera独立验证、第二scene、收敛/质量对比、硬件机制归因：NOT_EXECUTED。

早期运行日志和CPU组件测试不进入性能统计。已有A44的14.084/14.746ms不是本轮新测；本轮不能支持或反驳H_CPU/H_GPU_LINK，也不能把工程异常归为资源瓶颈。

## 资源、共享与清理

GPU窗口观测峰值：自身NVML1146MiB，监督器进程树sampled RSS11.023GiB，独立session kernel charged peak8.390GiB。已取样值未超批准上限；VmSwap异常形成真实监控缺口，**不声明整体资源观测完整或全Goal峰值PASS**。持锁时间不是GPU计算忙碌时间。历史桌面逐进程activity缺口保留，共享测量不是完全独占。

正常完成行打印与RESULT COMPLETE保留；监督器在异常前未记录EARLY_R1最终OS退出码，不从输出文本补造exit0。最终持锁内owncontexts_cleared=true、unlock/close=true、reservation released=true；CPU后核查所有已知自身PID不存在、flock无自身holder、Image-Lab新鲜attestation为IDLE且无预约/自身compute。只删除本轮已不再使用的短tmp symlink，保留private失败IPC和原始证据，不清旧资产。


EARLY_R1只是同一Goal、同一flock内的worker attempt编号，不是新Goal或第二次取锁。CPU helpers使用独立轻量会话，其各自HWM/测试记录单列；GPU窗口峰值不冒称完整Goal全进程连续峰值。预约续租逻辑经CPU测试，但实际窗口短于1800s TTL，未发生续租POST。

## 本Goal内的工程修复与实际范围

- AF_UNIX短路径修复已在真实EARLY_R1生效，source/input/precision/backend不变。
- StopIteration后新增结构化进程观测，缺VmSwap不填0；只有同一incarnation的严格终态/双重消失证明及owner/gate完整时记censored，活进程缺字段、AccessDenied、PID复用、未知任务和独立gap仍STOP。部分观察先落盘，再判断。
- 后修复经CPU mock及集成回归；**没有GPU重跑，不把本轮FAIL改PASS**。原失败缺PID，无法追认其符合新分类。RSS的V7退出规则及40/48GiB等资源限值不改；observed live VmSwap小计不冒充完整峰值或上界。
- 原执行源码两个版本通过冻结SHA完整保留在raw/EXECUTED_SOURCE_SETS.tar.gz；最终工具目录的后修复代码与实际执行版本分列。

最终科学建议：Q1主问题保留，晚期科学目标未完成，不生成硬件候选或性能排名。本轮不自动启动新Goal、第二次GPU尝试、第二scene、Profiler扩展、模拟器或RTL。完成Git精确发布回读后STOP。
