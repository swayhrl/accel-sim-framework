# Parboil BFS DM/DH 失败诊断（2026-10-25）

两点已定位到同一个源码缺口：**不写目标寄存器的 global atomic 完成后，M4 观察侧的 OO-PIB 生命周期没有关闭**。原样提取冻结源码函数并链接真实 OO frontend 头文件的 CPU fixture 已复现这一缺陷；它能使 128 个条目持续不可退休，随后拒绝第 129 个准入。它不是新的模拟，也没有修订历史失败结论。

对历史两点，精确的 OO-PIB 128 槽占满属于高置信推断。旧 dump 没有输出 OO 条目 UID、operation 与 external dependency 数量，不能把这个未直接记录的现场写成已观察事实。

## 两点及直接触发

| 点 | UUID | 运行结果 | full raw SHA-256 |
|---|---|---|---|
| DM | 5d58a06a-8465-4dcf-bf31-391b5a6c4737 | Core deadlock 检测后 SIGABRT | fac2a8365da10598be03fc5cfdbfcd1e57089ab25a1e6630f0e80d5149e5fecd |
| DH | a6161cff-a0fe-4f2d-b489-8644dcb61c89 | 同一精确停点、SIGABRT | 79c2901b10903054e01c292d000a10a99f2e74bdb2383ceeeb6d617767b59820 |

两份 gzip 全量解压 SHA 已与 NATIVE_EXIT 对上。它们均只进入第 1 kernel `_Z17BFS_in_GPU_kernelPiS_P4int2S1_S_S_iS_iiS_`，grid=1、block=512。最后 WB 在 cycle 51215，dump 在 150000，连续 98785 cycle 没有 WB。冻结 Core 的 50000-cycle progress equality 检查置 deadlock，`deadlock_check()` 输出现场后 `abort()`。`DTC_NATURAL_TELEMETRY_CLOSURE_MISSING` 是 abort 之后缺少自然闭合的下游现象。

两点 core0 的 LD/ST dispatch 都停在 **warp1、PC0x0710、BK_CONF**，active mask 对应 `00001fff`。同一份 trace 中这个 warp/PC/mask 只出现一次（line 67394）：

```
0710 00001fff 0 ATOMG.E.MIN.S32.STRONG.GPU 3 R4 R4 R3 4 2 ...
```

这里的 `0` 是目标寄存器个数。并非 trace 缺字段：冻结 v3 parser/decoder 允许零目标寄存器，保持 out[] 全零。地址 payload 的 `2` 是压缩格式，不能解释为地址空间。第 1 kernel 的全部 21971 条 global ATOMG 记录都是零目标寄存器；另有 10476 条 shared ATOMS。首 kernel 全量 body（22906288 bytes）SHA 为 `1469dbd66e8edf724d8eff8fec775a8c60b40b057039875038470c5f973a8fb2`。这次只读了必要的首 kernel，不宣称重新散列了完整 11-kernel 输入。

## 可证明的源码链条

冻结 Core commit 为 `2e3bef4364e578cddd0e881c0baace2e51c55930`；读取的 source bytes 均与该 commit 的 blob 相等。shader.cc SHA=`b2bb326916c505e43f5d70cfd9d9adc998de1c08248d035581be02f96f7c1c45`。文件绝对路径、其余 source SHA 见 JSON。

1. Framework `trace_driven.cc:274,332,422–431`：先把 out[] 清零，仅按 reg_dsts_num 填写；ATOMG/RED 都为 global、LOAD_OP、atomic=true、CACHE_GLOBAL。旧 cfd3ff56 与 cap1m 3b362ab5 的这一整个 decoder 文件 byte-for-byte 相同。
2. Core `shader.cc:3933–3947`：atomic 走 M4 ATOMIC 准入；不会走可缓存读合并路径。`2621–2642` 新建 OO PIB entry，同时加一项 external dependency。
3. `shader.cc:4543–4590` 的 `writeback_complete()` 只在正 out register 或 LDGSTS/sync/arrive/fence 等分支设置 completed=true；没有 zero-dest atomic 分支。真实 ATOMG 的 out[] 全零且不是这些特殊操作，返回 false。
4. `shader.cc:4652–4655,4687–4688`：常规 global writeback 已递减 architectural atomic count，但只有 completed=true 才调用 M4 observe_complete。该原子操作的 M4 external dependency 留下。`2658–2676` 中的关闭动作因而未执行。
5. 真实 `dtc-l1-common.h:544–568`：OO entry 数达到128时拒绝新准入；external dependency 未归零的条目不 ready，不能退休。`memory_cycle:3944–3947` 把这个准入失败记录为 BK_CONF。这与真实停止现场吻合。

CPU fixture 使用**未经修改的原始 writeback_complete 函数体**和冻结 `oo_frontend` header（仅外部架构类型用最小 stub），分别验证 zero-dest ATOMG/RED 都返回 false、returning atomic 和 fence 控制返回 true、128个 externaldep 条目堵住第129个。AE=0/1 两种 hash 配置相同。它证明源码中的缺口和有限资源后果；没有重建历史 warp 调度时序。fixture 源码、编译参数和结果均随附，可独立复验。

## 对照与排除

同输入 CM/CH 都通过全部11个 kernel、自然而完整闭合，cycles 都是4330430。其 M4 atomic_admits=0，因为传统 PAPER_BASE 不建立这个 OO 观察侧所有权。它们与 DM/DH 的差异包含模式、finite service、MSHR/PIB 与缓存布局，不能只归因于某一个容量。

DM 与 DH 的有效模型配置差异只有 tag_hash_bankrow=0/1；它们在不同 telemetry 上限下却停于同一 instruction/cycle/progress。global atomic 本身以 CACHE_GLOBAL bypass L1，不通过 hash 标签查找。因此目前证据支持共同的 OO/M4 集成缺陷，**不支持 AE/XOR 特有缺陷或 AE 收益结论**。

两点都只有7条 progress，远低于8192/1048576上限；两点捕获的 RAM/disk 样本全部通过，原策略采样均为 CONTINUE；峰值 RSS 同为583008256 bytes。真实调用栈显示 Core deadlock_check->abort。因此这两个失败的直接触发不是 telemetry cap，也不是外层内存/磁盘 guard。

core0 scoreboard、L1D MSHR、miss queue、response FIFO 均空；无 busy memory partition/interconnect 提示。BK_CONF 是公共 stall 分类，单凭名字不能断言是传统 cache bank conflict。其他 warp 停在0xEE0，本次没有 barrier bitmap；不能将“其他 warp PC 相似”写成输入 barrier 非法的证明。dump 的 gpu_tot_sim_cycle=4294817296 来自 unsigned(0−150000) 的打印下溢，不能当成已经执行42.9亿周期。

## 未知与后续最小验证

现有历史 dump 对 PAPER_IO 才额外打印 PIB 详情，缺少 PAPER_OO 的条目/依赖快照；准确的128槽现场、每个 owner UID 与最后依赖计数仍未知。下一步应先在 CPU fixture 中加入真实分片 atomic 响应聚合、只完成一次的约束、zero-dest RED/ATOMG、returning atomic、store/fence 与满128槽排空对照。修复必须沿真实完成所有分片的边界关闭生命周期，不能简单每个 reply 都关闭一次。

如以后另行安排带诊断的不可变模拟构建，再捕获 OO entry UID/operation/外部依赖数量，核实历史现场推断。此次没有启动/重跑模拟，没有改运行源、registry、INTENT、classification、历史账本或任何原资产；两点仍不接受 cycles，SOURCE_KEEP。
