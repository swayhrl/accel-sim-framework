# D输入科学适用性独立报告

Btree保留原登记并继续HOLD。SpMV与Scan已复现明确的输入格式缺陷；SGEMM完成完整原字节/语法/非原子闭合，是本次唯一可提交E独立输入审查的候选。**D没有变更正式登记或启动应用；当前仍缺少经E接受的替代。** 原七输入统计目标和40次累计预算不变，七对均值保持UNKNOWN。

## Btree：两个解码器在此记录上没有地址差异，仍不能解除HOLD

E69301fe9冻结证据中的kernel-1第691行：mask=0x10000000，只有lane28，list_all携带32个地址。准确Framework9dd1ee57原生源码按popcount顺序读取，所以lane28取得第0列0x00007f8eed50bc04；固定32列解释的lane28为0x00007f8ef0d10f88。

D实际冻结C oracle aabc7d80/763cbcdf也取第0列，已用原始记录和准确函数复现。不能声称这条记录上“oracle取列28、native取列0”。问题是32列输入语义与原生紧凑active-lane语法未闭合，oracle缺少残余字段检查，两个解码器同样消费第0列不推出输入合法。native随后读取一个imm也不会按lane重排地址。此前3条只读line只是保留的模型派生物，不可作为native输入资格。

未修改原trace、生产解析器或C oracle。若要修复输入编码/生产解析器，须A/E单独确认producer格式、派生输入/源码新身份、准确原生资格和影响范围；当前不为此重编译。详细分工和源/记录SHA见SCIENTIFIC_SCOPE_AND_OWNER_ACTIONS.md与BTREE_MAPPING_COMPARISON.json。

## 现有替代候选

| 候选 | 本次实际检查 | 输入资格结论 |
|---|---|---|
| SpMV Dubcova3 large | 第80103行`0880 ffffffff 1 R9 IADD3 2 R9`，声明2个源寄存器但仅1个，且记录缺后续字段。34,529,277B全文件SHA55f2ef8d…与原已发布资产一致 | 原先第一备选已先审；不能直接登记。没有修补/拼接记录；旧模拟结束不替代当前语法证明 |
| Scan NO_ARGS | 前6kernel完成检查；kernel-7第64行mask0x80000000，仅lane31，STS却有32地址。原生消费第0列0xf1bf9283，固定32列的lane31为0 | 与Btree同类非零mask地址冲突，HOLD。没有为了强压力样本保留它，也没有完整扫描余下失败后kernel |
| SGEMM medium | 1kernel、528TB、51,847,488条warp指令记录、1,658,916,864活跃线程指令；全2,216,170,035B SHA1b073990…匹配原清单；全局/共享原子记录均0；无扩展零mask地址行；完整native composite SHA694ce08c… | D完整静态输入候选，通过当前检查但**待E独立输入审阅与正式登记**。不代表数值SASS或最终S/F运行正确性 |

来源、完整命令、逐body SHA/大小、规模、独立价值和成本代理在EXISTING_CANDIDATE_MANIFESTS.json、CANDIDATE_REVIEW.csv及REPLAY_REPRODUCIBILITY_AND_COST_SCOPE.md。SpMV/SGEMM原捕获run.sh和原应用revision仍UNKNOWN；可主张的是准确冻结trace replay范围，不能冒称从源码可重新捕获。SGEMM header显示binary70、NVBit1.4、tracer3，并不认证未知的原工具链。新native模拟walltime均UNKNOWN，D没有以运行来估时。

选择完全发生在候选新S/F性能可见之前。SpMV按原第一备选优先审查后因缺陷排除，Scan因实质语义冲突排除，SGEMM是唯一完成当前资格步骤的候选，其稠密计算/复用且旧低跟踪压力背景有独立对照价值。没有按新方案加速挑选。

## 交E的具体决定

SGEMM_PROPOSAL_TO_E.json含完整input manifest、native-source/checker绑定、指令闭合和待办。建议E先审查SGEMM适用性，再决定是否用新登记revision替换Btree；D不自动写入input_registrations或E台账。若E不接受SGEMM或现有证明不足，当前没有另一个通过检查的替代，明确保留缺失，不人为凑齐七输入。

SGEMM没有独立已接受RO证书，覆盖UNKNOWN；不能借Conv证书。采用时，固定完整F策略不逐应用改变，未认证line依已资格的空覆盖/普通路径保守回退。E还须绑定同一最终binary/config、当期真实资源、独立生产路径资格和剩余40累计额度。D静态检查不构成启动授权。

DWT2D已有10kernel完整输入/非原子/原字节与零mask证明保留，详见E_DWT_PROOF_RETAINED.json；没有重扫。原五输入全部不重扫。所有旧日志、证书、矩阵与结果保留，EN-v18未修改。

## 主图与增量分析

正式替代尚未被E接受，Btree的S/F位置标输入HOLD，七输入分母保持7，未测数据不填0或1，不生成6输入的“七输入均值”。analysis_preview/是新版接口预览，保留七个位置；只有E正式接受、同最终binary/固定策略的配对可进入结果。新增输入HOLD保护与既有撤回/身份保护共12项控制测试通过，非native PASS。矩阵32条件与40累计预算未更改，真实已用次数引用E最新回执；本轮D新增完整应用0。

审查总耗时1135.742s，SGEMM在837.479s内完成，不需要重试/缓存恢复。原始资源计数ru_maxrss为746,463,232B，属于整个进程生命周期（包括解析上限设置前的source setup）。解析阶段设置256MiB地址空间上限，但没有单独采样该阶段RSS，因此不宣称RSS满足256MiB。只读source-setup复核未扫trace，报告12MiB，未复现先前峰值；阶段归因UNKNOWN，原始计数和复核均保留，此项不用于任何科学资源放行。后续运行资源必须由E独立核准。全部D审查进程已退出，无后台等待器、GPU、C++编译或模拟启动。
