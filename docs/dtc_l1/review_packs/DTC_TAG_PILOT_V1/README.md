# DTC_TAG_PILOT_V1：原174有界探索

授权入口：Framework `103c12ca28e0b5fb66f45b905a04108b501f8ec7` 的 SCIENTIFIC_CHARTER_AND_PREREG.md、GOAL_T_OPTIN_PILOT_174.md。原174 `huangrulin-174`，本独立分支 `hrl/iscas2027-dtc-tag-pilot-174-v1`。原A `f5c37d6e` 已收口，本任务不重启原Goal、不写其44行、raw、锁或监视进程。

本提交是**第一条新性能出现之前的完整七点预注册**。执行前还必须具备本提交push/fetch-back收据、Lane M提交的可核报告、实时资源和唯一authority gate。CPU检查PASS不是性能准入PASS。运行后以FULL_MATRIX.tsv、逐UUID strict、DISCOVERY_SCORE.tsv和LATEST_REPORT.md为最终状态；当前没有这类新性能文件。

## 完整固定矩阵

| 点 | 模式与Tag | 发现输入 | 新attempt上限 |
|---|---|---|---:|
| T0 | IO active PIB128，32sets×4ways | 原full GEMM | 1 |
| T1-A | OO128，32×8 | 原full GEMM、Gaussian | 2 |
| T1-B | OO128，64×4 | 原full GEMM、Gaussian | 2 |
| T1-C | OO128，64×8 | 原full GEMM、Gaussian | 2 |

合计最多7次，每条UUID、输入/list/member/ordered-kernel/CPU proof/config/Core/binary身份、已验对照UUID及stdout SHA、有效差异均在PRE_REGISTRATION.tsv和specs/。不重跑32×4原OO，不读任何新holdout candidate性能，不追加其它参数点。

输入检查只针对两个发现负载511成员，复用原629 CPU body审计中这两个子集，不重解码或重扫其它负载。GEMM：1 kernel、1024 CTA、739246080活动线程指令；Gaussian：510 ordered kernels、65790 CTA、283685120活动线程指令。两份**完整原列表**各含3条MemcpyHtoD，不删除、不重排、不仅拷kernel子序列。inputs/中的CPU表只取发现输入，保留来源SHA。

## 冻结服务与配置

finite Core `6fba0136f8465b59fe5858a950fa39efb265f654`、binary `fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b`、build Framework `18a68dcccd795f1b6cda75504e9450d00c9cee02`。普通16KiB side、80KiB/640行DTC池、96KiB shared、64SM、1410/1410/1410/850MHz、lower cap32768、4 Tag banks/1请求每bank每cycle、allocation4、现行LD/ST multiplier1、全部R1 finite配额和原路由都保持。

T0只改有效IO PIB256→128；T1只改logical_sets/ways。原options字节快照＋末尾overlay在config/；CPU从按顺序解析的配置与原完整option echo（含defaults）生成预期配置，性能运行的stdout必须再次逐选项核对。quoted multiline DRAM timing只在比较时规范化空白，原配置字节没有改动。ordinary cache的sets32/ways4与**DTC Tag几何**分开，禁止混改。

Tag源绑定已核实：gpu-sim.cc注册两尺寸，shader.cc构造传递，common头用sets×ways创建tags，查找/替换循环均用cfg；物理槽独立640，Ref仍每128B line reference。32/64 sets均被4整除，`((line%sets)%4)`对同地址的bank保持不变；增加sets改变set冲突/容量，增加ways还改变比较路数。Tag每lookup仍假定1cycle，这是探索模型条件，没有同频RTL资格。

## 已完成的CPU门槛

- SOURCE_IDENTITY.json：15个冻结源码/CPU proof源文件及对应commit逐字节核对；实际外置Core clean。动态CPU库身份单列，不伪造旧库历史等价。
- ACCEPTED_CONTROLS.json：GEMM IO256/OO128/C+和Gaussian OO128/C+，原raw、strict、full instructions、config/runner/runtime/hash全部复核。原周期保持1457468/1377919/1511333及3798174/3379152。
- CPU_DIRECTED_CHECKS.json：独立小build中编译运行原四个directed程序，另对原32×4及三个候选几何检查完整查找覆盖、bank quota、pending替换、晚返回generation/Ref、IO128准入上限。没有模拟器build或full replay。
- STRICT_COLLECTOR_READONLY_CHECK.json：增强collector对原GEMM IO256/OO128及Gaussian OO128全部kernel回归PASS，不改变原strict。每kernel独立指令、累计CTA/指令和累计finite字段均按真实scope处理，不把重复累计打印相加。
- RESOURCE_PREFLIGHT.json：两个间隔10秒快照，原锁只stat、无owner、无活跃外部模拟器，无新增swap/OOM，内存/磁盘/IO门槛通过。历史swap已用量和历史oom_kill不抹去；检查的是实时pressure及增量，执行前再做同样检查。

两个CPU wrapper断言失败及确定性修复见CPU_PREPARATION_FAILURES.json：DRAM打印空白和原列表Memcpy命令分类。均发生在任何新attempt之前，原科学配置/列表未改，无性能失败被覆盖。

## 执行与停止规则

POLICY.json固定7条UUID、最多2个新模拟并行、顺序、每GEMM 8小时/Gaussian 2小时墙钟上限及资源阈值。超时/资源终止自然验收FAIL，原收据保留，不重跑/改参数。唯一有限的foreground `run_pilot.py --execute` 持自己的AUTHORITY.lock，所有attempt独立root，只派发固定plan一次；没有第二个长期watcher或对原authority的接管。若身份/strict错误，保留并停止后续点；**合法负收益不触发停止或调参**。

增强strict复用原collector，再核新UUID、Core header、全配置echo、ordered names、每kernel活动指令/累计CTA、credit/dependency/PIB/inflight/lower/ordinary守恒、Ref及physical balance、64SM采样和11finite量。Retained tag-visible数据在正常结束后可以存在，不要求physical allocated=0；活引用、在途、部分分配必须排空。没有输出的独立sector/ordinary MSHR/架构数值等标UNAVAILABLE，详见SCIENTIFIC_SCOPE.md。

执行命令只可在全部gate通过后使用：

```bash
python3 docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/scripts/run_pilot.py --execute
```

raw和执行gate在 `/workspace/dtc-tag-pilot-174-v1`；原始stdout/trace/binary不推Git。包装脚本改自冻结runner/collector，来源在inputs/，差异仅预定UUID、独立authority、超时及额外验证；无模拟器源修改。

## 选择与报告规则

每个T1候选要求两个输入均strict PASS。`R=原OO128周期/新OO周期`，`R_min=min(R_GEMM,R_Gaussian)`，`R_g=sqrt(R_GEMM×R_Gaussian)`；须同时`R_min≥0.98`和`R_g≥1.02`。取最大R_g；与最大值相差不到0.5%（`(best-R_g)/best<0.005`）的候选按更少Tag条目、再更低ways决胜。T0不参与Tag选择，不按负载分别挑最佳。

没有合格点即NO_QUALIFIED_TAG_PROMOTION_IN_T1。只有两个预注册发现输入的探索评分，不叫GM12或论文总体加速。完整表包含失败、HOLD和负收益。即使有胜出候选，也在T1后停止，交审独立holdout及硬件成本；本Goal不启动DWT2D/BICG holdout、T2、modern128KiB或任何新机制。
