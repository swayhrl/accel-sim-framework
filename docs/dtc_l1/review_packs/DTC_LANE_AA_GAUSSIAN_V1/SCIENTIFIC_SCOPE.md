# Lane AA Gaussian factorial: CPU reservation, execution STOP

本包仅属于 `DTC_LANE_AA_GAUSSIAN_INVALIDATION_FACTORIAL_174_V1`。唯一授权的新 full attempts 为原完整 Gaussian 的 K0_32x4、K0_64x8、K1_32x4、K1_64x8，各一次，合计上限恰好四次。当前实际启动数为零，canary 也为零。四个 UUID 已保留；PRE_REGISTRATION.tsv 和四份 spec 是 **未绑定的设计预留，尚非完整可执行预注册**。

科学准入要求先绑定 Lane V 的事件科学合同、Lane W 的输入及地址别名风险、Lane X 独立 Core 的 push/fetch-back、Lane Y 独立验证 PASS、Lane Z 指标定义。还须证明原 Gaussian 中合法 source-defined invalidate 事件实际可达，并确定 timing model 支持域。源代码存在调用位置不等于输入事件收据，输入重哈希也不等于地址别名风险已解除。现场收到并核读 V 的待审合同、W 的 DEFERRED_SAFE_STOP 与 X 的 SCIENTIFIC_STOP_SOURCE_EVENT_CONTRACT_MISMATCH。X明确没有实现K1、没有注册新开关，Core仅文档差分；X的Framework/Core已独立fetch-back绑定。Y独立PASS/Z最终定义未绑定，模型支持域与事件计数仍未确定，依用户明确门槛 STOP。不能把“未证明”改写成“事件为零”或“无效果”。

K0 关闭 Lane X 开关，K1 仅在原 source-defined invalidate 时使 Tag lookup mapping 失效；保持既有 Ref/generation/credit/owner 生命周期合法，不额外创造 kernel 边界、强制释放活引用、flush 数据、合并/拆分 lower 请求或改变延迟。当前尚无可绑定的新开关 CLI 名称和新 binary，相关字段 UNAVAILABLE。不得把旧 binary 的 K0 行或虚构 K1 option 当作新实现。

两个 Tag 级别为32 sets×4 ways与64 sets×8 ways。所有点 OO128、physical640×128B、ordinary16KiB、shared96KiB、64SM、原4 Tag banks、finite V1、global lower cap32768、1410MHz、L1 flush=1及全部公共 effective options 相同。config 快照沿用已接受的原顺序；CONTROLLED_DELTA.tsv 列出全部实际有效公共选项与 Tag 配置，另以明确无效的概念占位行表示未绑定 K 开关。当前配置不能用于新矩阵运行。

完整执行预注册还必须含新 source/Core/build Framework/binary SHA、全部依赖文件与独立审计 SHA、K0 默认 OFF 的完整身份/有效 options/行为差分、event count 精确合同及开关实参。上述缺项补全并 commit/push/fetch-back 之前不能发射。四个已保留 UUID 不得换号或消耗于诊断；本包不提供后台 launcher，不自动轮询发射。

若后续在本授权内恢复工作，先确认 U 原 coordinator、runner、simulator 的 PID/start_ticks 对应实例全部实际终止且执行锁释放；不得接管 U 锁、重启 U Goal 或建立与 U 并发的共享执行权。再复核全部科学与资源准入，完成不可变完整预注册后，按 K0_32x4→K0_64x8→K1_32x4→K1_64x8 顺序发射。两个新 K0 都须自然 exit0、逐 kernel strict PASS，且周期分别精确等于3,798,174和3,278,356。任何差异立即阻止全部 K1，保存差异且不 retune。旧两数字和旧原运行仅是历史校准参考，不能替代新 K0 配对。

每点须510个 kernel 完整原顺序、完整 memcpy/list 命令、成员 SHA、CTA、active-thread instructions、Core/build/binary/config 及64SM有效回读。逐 kernel 检查 PIB/inflight/lower/Ref 清空、generation合法性、credit/响应/ordinary/physical守恒、保留物理行边界及11 finite metrics。Tag-visible 无 live Ref 的 retained physical lines 可合法保留，不能强求所有 physical allocations=0。独立 sector 返回计数、ordinary内部 MSHR占用、数值 load 正确性无字段时保持 UNAVAILABLE。

新事件须独立检查预注册 event count、实际失效 mapping 数量、失效后持有引用的合法存活及最终释放。不得用 eviction 数量代替事件数，不得将无字段项目判 PASS。所有失败、timeout、deadlock、阴性及退化保留；不因性能不佳重跑，每 UUID 最多一次实际 simulator 启动。仅 wrapper 失败允许在原 UUID/原绝对 deadline 内确定性恢复，必须证明不会第二次启动 simulator。

资源合同见 EXECUTION_CONTRACT.json：默认并发1。用户允许在 U结束后且本 Lane 资源充分时提升至2；本次固定上限1，不启用提升。所有项目计入 RSS、cgroup headroom、swap/PSI、磁盘/I/O。不得停止他人进程；运行期资源故障如需终止，仅可针对 AA 自己的已绑定 PID/start_ticks/process group。timeout自首次实际启动起7200秒，不重置。

比较公式见 COMPARISON_FORMULAS.md。四点未全部严格通过时 factorial 效应保持 UNAVAILABLE；局部已接受配对可独立描述但不补齐缺失点。11 finite metrics/终态派生量使用固定 typed 分母；不能从 credit 推导 DRAM字节，不能把服务条件均值差当作整机周期贡献。Lane Z 未绑定前的 METRIC_DICTIONARY.tsv 是候选定义，未授予可比性 PASS。

不创建或修改 GM12、原44行、BICG/DWT2D复测、GEMM点、T2、新Tag候选、其它输入、服务参数、现代DTC、新Core增强或论文主图。所有 raw 位于 `/workspace/dtc-lane-aa-gaussian-174-v1`；Git仅提交小文件。完成本次 STOP 记录和远端回读后停止，不保留自动发射进程。
