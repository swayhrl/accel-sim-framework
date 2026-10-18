# Lane Y2 independent K1 requalification — supplementary acceptance

2026-10-18，原174账户/容器。门禁 **PASS_K1_OO_MODEL_SCOPE**，仅限下述已运行的OO查找/生命周期模型范围；**不是八项合同全通过，也不产生AA2执行授权**。继续Y2分支，原Y1 `b673d046b38f61159b5db67a477d58d1afa4662f`及其FAIL_CLOSED包保持原tree，未重跑旧Goal。此前Y2证据commit `9a0d374df215e4878774ec2e3f9e49d1eda67b38`保留。

固定来源已独立fetch-back至Y2专用refs：Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`，X Framework `49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4`，V合同 `26abd496417d9392245052e54fbd9ba27c6ffd96`；冻结Core为 `6fba0136f8465b59fe5858a950fa39efb265f654`。见[绑定收据](supplement_r1/FETCH_BACK_BINDING.json)。完整冻结→新Core差分的10个路径全部审读；[差分清单](supplement_r1/FULL_DIFF_REVIEW.json)逐项列blob、内容/patch SHA和裁决。未修改生产Core，未发现已复现的生产缺陷。

本次新增16次真实ABI生产对象CPU运行：新Core omitted/0/1和冻结Core omitted，分别覆盖finite OFF/ON、1/3个cacheable消费者。新/冻结源各有独立detached source和完整CMake library build；探针各按相应头文件重新编译。每个进程用`dladdr(dlsym(ldst_unit::cycle))`核实实际装载的库绝对路径，逐binary/library SHA、compiler、flags、ELF build ID均在[构建身份](supplement_r1/BUILD_IDENTITY.json)和[逐命令收据](supplement_r1/ABI_RECEIPTS.json)。

|证据|已运行结果|
|---|---|
|K0三方配对|4组：新omitted = 新0 = 冻结；逐周期状态、physical/generation快照、实际下行packet轨迹、全部103项公共统计字段（含finite 11元组）完全相同|
|生产LD/ST|真实`issue/cycle/fill/writeback`、真实`mem_fetch`与返回路由、lower credit、scoreboard、完成ledger、operand collector bank拒绝；不再仅依赖提取夹具|
|source与ordinary|E=10立即撤销可查询Tag；真实ordinary miss owner/MSHR排空后到23才commit；请求/提交分开核对|
|occupancy/map-loss|31..34不调用LDST service，32发生配置失效；独立矩形积分、按identity查找可见性丢失→释放的计账与生产值一致；失效不推进service edge|
|失败负例|16个错误期望比较器均exit1；真实ABI重复sector被指定生产断言拒绝（生产crash handler处理SIGABRT后exit1，无terminal结果）|
|原Y2证据|62项独立API/逐字源函数体/header/parser比较及原先7/7 Core CMake CPU回归保留；本次未用重复上游测试代替独立证据|

[TEST_MATRIX.tsv](TEST_MATRIX.tsv)现有79行：原62项 + 16个真实ABI运行 + 1个真实重复sector拒绝。每次ABI运行的输入、期望、完整观察、退出码和失败负例见[ABI_OBSERVATIONS.json](supplement_r1/ABI_OBSERVATIONS.json)；[输入时序](inputs/abi_sequence.json)、[探针](scripts/abi_ldst_probe.cc)和[runner](scripts/run_abi_supplement.py)均可核。

|Lane V项|裁决|实际通过范围与缺口|
|---|---|---|
|K1-01|PARTIAL|真实MEMBAR guard/单SM、config同异/flush0/两cluster广播、真实空cluster重复idle通过；活动cluster部分SM未完成只在逐字源语句夹具覆盖|
|K1-02|PASS|OO模型：Ref0 API回收；真实pending/live多消费者、新旧同址不同physical、最后Ref保护；generation重用由生产API验证|
|K1-03|PASS|生产API/逐字grant/commit/partial路径：已接纳保留、未接纳重查、全引用恰好关闭；完整shader多line coalescer→dispatch组合未运行|
|K1-04|PASS|真实sector乱序和重复拒绝；API/逐字返回路径覆盖late waiter、finite return cursor、slot reuse、stale generation拒绝；没有真实NoC调度|
|K1-05|PASS|真实operand collector WB bank拒绝、pending writes/scoreboard/ledger与Ref保护；collection交错和generation重用兼有API/源体测试|
|K1-06|FAIL / IO STOP|未实现IO orphan机制，生产mode guard拒绝IO K1；排除于OO资格，绝不能称IO/OO共同通过|
|K1-07|PARTIAL|生产sidecar admit/complete/retire及proxy过滤源体通过；完整STORE/ATOMIC/BYPASS/PROXY指令与ACK序列、payload副作用未测|
|K1-08|PASS|OO模型：真实请求10/ordinary提交23、两SM config和idle重复；同cycle三种次序及bank quota由逐字源体/API测试覆盖|

[VALIDATION_GATE.json](VALIDATION_GATE.json)与[VALIDATION_GATE_V2.json](VALIDATION_GATE_V2.json)内容相同，均包含上述逐项裁决及缺口。PASS指明确的OO模型/API范围，不将夹具范围提升为完整ABI覆盖。目录sweep在source请求处原子执行、**零新增模拟cycle**是当前明示模型假设，未给出硬件延迟、端口或PPA证明。

K0通过有界OO LDST CPU严格配对；完整输入、真实store/atomic/ACK、NoC/DRAM及全部模式的运行等价性没有证明。建议Lane AA2使用新Core对完整同一输入重新跑K0，冻结/新结果严格配对；旧冻结结果不能替代新Core K0收据。这是验证建议，不授权或启动AA2。**实际architectural load数值、跨SM coherence及完整ISA支持仍UNPROVEN**；未以全ISA证明作为OO结构资格的前提。

外部原始输出/二进制保留于`/workspace/dtc-lane-y2-k1-requal-174-v1/supplement-r1/final-abi-v3/`；不提交原始日志、trace、binary或build。复跑使用全新run-label：

```bash
python3 docs/dtc_l1/review_packs/DTC_LANE_Y2_K1_REQUAL_V1/scripts/run_abi_supplement.py review_abi_unique_label
python3 docs/dtc_l1/review_packs/DTC_LANE_Y2_K1_REQUAL_V1/scripts/finalize_supplement.py
```

无kernel/trace replay/runtime模拟线程启动；只有组件调用及三个空GPU CORE tick。完整Gaussian/GEMM派发数=0，新执行authority数=0。交付文件SHA见[SHA256SUMS](SHA256SUMS)。最终commit/push/fetch-back/clean的精确SHA收据留在外部`/workspace/dtc-lane-y2-k1-requal-174-v1/supplement-r1/FINAL_FETCH_BACK.json`，避免自引用；原Y2最终收据不覆盖。
