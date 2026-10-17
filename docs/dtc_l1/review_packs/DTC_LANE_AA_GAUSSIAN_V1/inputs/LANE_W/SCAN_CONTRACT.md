# 暂停点和后续 CPU scan 合同

当前停止于任何 trace body open 之前，零扫描进度；没有后台 worker、自动重试或恢复任务。`build_readonly_pack.py` 只消费固定 git blobs、四个原 list、成员 stat 和 /proc；没有 scan 或模拟启动开关。重新执行该脚本也不会扫描 body。

暂停依据是本轮观察到的 I/O full avg10 超过5%，以及 df 可用空间意义下文件系统使用率超过98%。这是 W 为避免争用设置的保守读侧界限，不修改 T/U 已有资源合同。`RESOURCE_PREFLIGHT.json` 记录执行时数值和已有 simulator PID；这些都是外部活动，未启动、停止或干预。资源充足不自动授予新模拟权限。

若继续，只能按 TRACE_SCOPE_SHA256.tsv 中 Gaussian/GEMM 的精确原路径和顺序做单 worker 流式 CPU 解码。DWT2D/BICG 本版仅为封存身份补充，不自动扩展扫描；禁止扫盘、替换 trace、修复 decoder、写回解压副本。先复查 I/O/memory/disk、U 使用和冻结源码身份；高压力/U 占用/合同不明时保存 checkpoint 后停止。

解码前应固定独立分析器身份并用已验收 parser 分支对照小型 CPU fixtures 验证：version 0 与3布局、可选 lineinfo、active mask、opcode width、list-all、base-stride、base-delta、signed stride/delta、地址溢出、跨128B边界。出现非连续 mask base-stride 时不可自行补地址；该记录地址和相关统计记 UNAVAILABLE，保存合同缺口。不要执行 native 或原仿真二进制作为 oracle。

每条可解码 memory record 保存 workload/kernel/list position/CTA/warp/intra-warp ordinal/PC/opcode/space/cache class/active mask/width 与逐 lane 地址，转换为128B line内128bit byte mask和32B sector mask；不保存或推断 load值。按 kernel 汇总 R/W/atomic/bypass/fence，并保留 cacheable read 与其他路径区别。精确 line 集合可使用有上限的磁盘索引或内存集合，必须记录内存/输出上限和 checkpoint，禁止无界导出原trace。

输出每 kernel 的 distinct R/W lines，所有已完整处理 kernel 的 R∩R、相邻 kernel W∩R（可额外提供非相邻候选），line alias 与 byte overlap 分列。不同 warp 的记录无序，不能用文件 CTA 遍历顺序推断时序。同 warp 记录先后单列。没有 stream 或动态 invalidate 时间时只能使用 list ordinal 的候选语义；源码事件类型与动态事件实例分开。

即使找到 byte overlap，仍需满足“旧 Tag 可查询、未被替换、同一 DTC 域/SM、source-defined 生命周期覆盖、相关操作源模型排序”等条件才可能暴露旧映射。静态地址相交不能证明这些条件。任何原输入只能在已验原 consumer 范围内引用历史结果；K1 需独立合同/正确性评审，本 Goal 永不启动新模拟验证。
