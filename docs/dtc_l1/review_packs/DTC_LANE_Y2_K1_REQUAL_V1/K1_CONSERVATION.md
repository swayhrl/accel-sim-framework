# OO K1 conservation audit

**PASS_K1_OO_MODEL_SCOPE**，实际范围及各合同PASS/PARTIAL/FAIL见`LATEST_REPORT.md`和`supplement_r1/CONTRACT_VERDICTS.json`；K1-01/07为PARTIAL、K1-06为FAIL/IO STOP。完整ISA、architectural load值和跨SM coherence未证明，不作为OO结构资格的假定前提。

新证据使用匹配Core头文件/动态库的完整GPU/core/LDST/cache/mem_fetch/Scoreboard/operand collector对象。测试以`-fno-access-control`打开测试接缝，未改变生产源码或对象布局；两套探针各按新/冻结ABI重编。控制的是合成预coalesced指令、绝对cycle、mem_fetch_interface transport和返回时机；不冒充真实kernel/NoC/DRAM。

实际一/三消费者序列中，E前同址消费者保留旧physical/generation和Ref，E后lookup为miss，ON新load获另一physical。真实请求创建/注入和4个sector乱序返回执行生产方法；最后distinct sector才关闭inflight并归还credit。每个tick断言`acquired-released == DTC inflight + ordinary fill owner`，并执行生产shadow-ref断言。全部物理快照、请求轨迹和103项公共统计在`ABI_OBSERVATIONS.json`，守恒与退出码可复核。

WB反压由真实operand collector在相同寄存器bank预占写端口造成，生产`writeback`拒绝分支保留PIB/Ref；不是伪造WB返回值。成功后真实pending writes、Scoreboard及completion ledger关闭，旧无Tag physical直到最后Ref才释放。finite1三消费者：3次拒绝、3个消费者退休、DTC两笔128B和ordinary一笔128B，所有credit归还、refs=0、allocated=0；map-loss sum/count=13/2。

occupancy独立矩形oracle在每tick快照重积分；map-loss按`physical_id,generation`从Tag失去可见性到释放计时，Ref0即时释放持续时间0，重复请求不重复计账。finite1单/三消费者ON的结果分别为[PIB integral,physical integral,map-loss sum,count]=[20,19,11,1]、[57,41,13,2]。E前采样不推进service edge；K0 omitted/0/frozen四组完整字段和周期严格相同。

原Y2的生产API/逐字源体fixture继续补足边缘输入：Ref0同ID重分配generation++、partial width1、grant只保存cycle/跨E commit重查、全接纳前不可退休、late第7个waiter与metadata cursor、PIB slot generation、非法重复/错址/write/stale generation拒绝、collection中E、同cycle ERW/REW/RWE和多bank quota。每项预期与错误期望负例保留；这些边缘组合没有全部提升为完整LDST对象运行。

本次额外真实ABI重复sector负例用两个独立真实child构造相同sector，命中生产`OO response identity/address mismatch`。Core自带crash handler处理SIGABRT后exit1，runner要求exit1、指定诊断且无terminal结果；不会将任意崩溃视为通过。原源体负例仍要求-6及指定断言。16个ABI比较另有cycles=44的错误期望，比较器均exit1。

K1-07保留PARTIAL：生产sidecar/source-completion/proxy过滤源体通过，但没有完整实际store/atomic/bypass/proxy指令和ACK序列；不声称副作用恰好一次已获完整运行证明。IO无orphan机制，`IO_K1_UNIMPLEMENTED_STOP`明确拒绝；MODERN HOLD。未发现需要交X修复的生产缺陷；开发期间的测试构造/调度/工具语法问题只在Y2修正，失败开发输出留在外部目录，不计作生产失败。
