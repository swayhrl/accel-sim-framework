# 测量、源码事实与推断边界

本包是 CPU 只读证据消费与风险筛查，按用户明确的资源不合格收口条件完成有界审查；body scan保持 `DEFERRED_SAFE_STOP`。未扫描原 trace body，未新建模拟 attempt。`UNAVAILABLE` 不等于零；各表的 `ALL` 行是汇总，不能再与逐 kernel 行相加。

| 类别 | 已知事实 | 适用边界 |
|---|---|---|
| 本轮测量 | 四个指定原 list 逐字节及 SHA 匹配封存副本；523 个指定成员 stat 尺寸匹配 | 当前成员内容未重新 SHA；成员 SHA 是已验收身份，不能称为本轮重新完整验真 |
| 既有 CPU body proof | Gaussian 510 / 283,685,120；GEMM 1 / 739,246,080；DWT2D 10 / 148,684,429；BICG 2 / 145,666,048 active-thread instructions；全部声明 warp/grid 及终止 EXIT 覆盖 | 历史完整扫描的证明；不是本轮扫描、native 验证或 steady-state 证明 |
| 既有访问分布 | 每 kernel 的 cacheable global load、ordinary store、DWT2D shared 记录数；完整 opcode/width 目录 | 单位为动态 warp instruction records，不能乘 32 当成精确 active lanes，不能当成事务数、distinct lines 或访存字节 |
| 零值依据 | 所选四负载完整 opcode 目录没有 atomic/reduction、MEMBAR/FENCE 或 bypass load；global load 均为 LDG.E.SYS，frozen 配置 skip L1D=0 | 原冻结 consumer 模型下分类；BAR.SYNC 是 CTA barrier，不改称全局 memory fence；不同配置不能直接沿用 bypass=0 |
| 源码事实 | Core 6fba0136，Framework/parser 18a68dcc；普通 L1 invalidate 路径未调用 DTC invalidate；OO valid Tag 可跨指令退休保留 | 表中 invalidate 是源码事件类型，非动态事件或每个 kernel 必然发生的事件；不证明跨 kernel 仍驻留同 SM |
| 结构性推断 | Gaussian 有255个 Fan1、255个 Fan2，包含 cacheable reads/stores，且 Tag 可保留，因此跨 kernel 可查询映射复用值得研究 | 尚无地址交集，不证明任何指定 line/PC 存在复用；相同 kernel 名和重复 PC 都不等于相同地址 |
| 未测得 | PC、每段 distinct lines、R∩R、W∩R、byte/sector masks、同 warp 写后读、跨 warp 顺序、实际旧 Tag 命中 | 均为 UNAVAILABLE；候选范围不是已发现 alias pair；GEMM 原 list 无跨 kernel 对，仅可筛查 kernel 内风险 |
| 禁止推断 | load 返回的实际值、native 正确性、真实 happens-before、性能收益、K1 可比性 | SASS 地址记录与顺序不足以支持这些结论 |

地址语义采用冻结 consumer，而不是猜测历史 producer。Gaussian 的 proof `trace_version=0` 与 GEMM/BICG 的 version=3 必须分别走 parser 对应字段分支；不能将一个版本的字段布局套给其他版本。历史 producer/encoder 的完整不可变身份未由本轮建立。四个选择负载既有 body proof 中 sparse-mask base-stride 与 unaligned lane 地址计数均为零；这只排除了已知 Hotspot 类问题在这些字段上的出现，不能建立值正确性。

`COMMAND_SEQUENCE.tsv` 是文件顺序：列出原始 memcpy 地址/大小和 kernel ordinal。`stream_id=UNAVAILABLE`，不从 list 建造真实执行全序。Framework 允许不同 stream 的 kernel 在窗口内启动，且配置 max concurrent kernels=128；同 stream 的具体身份本包没有读取。源定义 cluster-idle invalidate 也不能替代 kernel-completion 时间戳。

line alias 指 `(address & ~127)` 相同；byte 冲突需两个精确覆盖 byte mask 的交集非空。32B sector mask 仅能给粗粒度相交；同 sector 或同 128B line 不能自动升级 byte 冲突。地址加 width 跨行时必须拆分；distinct lines 是集合基数，不能用每条指令最大32个 line references 或 load 总次数替代。

同一 kernel/CTA/warp 内可使用 trace 的 instruction ordinal 描述程序记录先后，但它不是源模型完成顺序，尤其不能跨 warp、跨 SM、跨 stream 编成全序。跨 kernel W→R 必须先称“前一 list kernel 的写与后续 list kernel 的读交集候选”，直到获得 stream/生命周期依据。

旧 Hotspot 原结果与 HOLD 保留，禁止修补 sparse-mask 地址、借新格式结果解封旧输入。旧/新 2DConvolution 身份分离并维持新输入 STOP；LUD 不追加、不晋升。DWT2D/BICG 只读固定 U 提交身份/proof，未访问其 raw、锁、后台控制文件；不改变 U 封存结论。用户确认U已正式完成，但本轮仍复查当前资源及其他模拟器，不以历史完成状态替代准入检查。

K1合同已从Lane V固定提交 `26abd496417d9392245052e54fbd9ba27c6ffd96` 读入并哈希；不再把合同标为UNAVAILABLE。其线性化点是source请求到达LDST时的DTC lookup撤销，同时保护旧physical/generation和消费者，不能等同于ordinary的延后Tag commit、统一kernel-end广播或一般写后可见性。K1不作为本Lane性能外推对象，也不等待Lane X实现；详细边界见 `K1_REVIEW_SCOPE.md`。
