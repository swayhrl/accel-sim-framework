# 固定 T1-C：DWT2D / BICG 独立 holdout 审查包

本轮验证预先固定的 T1-C（OO128，64 sets × 8 ways），两个原完整输入各一次实际启动。两输入未参与 T1-C 选型，旧 OO/C+ baseline 已知。逐输入报告全部结果，不进行新选型、holdout GM 或论文主配置晋升。

| 输入 | 原 OO 周期 | 原 C+ 周期 | 固定 T1-C 周期 | R_OO | R_CPLUS | 对 OO 周期变化 | 对 C+ 周期变化 | 新点验收 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| DWT2D | 237,887 | 247,588 | 236,447 | 1.006090 | 1.047118 | -0.605% | -4.500% | PASS_STRICT_HOLDOUT_SCOPE |
| BICG | 47,533,116 | 25,353,488 | 41,157,397 | 1.154911 | 0.616013 | -13.413% | +62.334% | PASS_STRICT_HOLDOUT_SCOPE |

R_OO = 原 OO 周期 / 新周期；R_CPLUS = 原 C+ 周期 / 新周期。周期变化 = (新周期 / 对照周期 − 1) × 100%，正数代表周期增加。不完整点的正式速度比保持空值。完整六臂、UUID 和 stdout SHA 见 [FULL_MATRIX.tsv](FULL_MATRIX.tsv)。

## DWT2D：终态机制与同路径计数

| 字段 / 单位 | 原 OO128 | 固定 T1-C | 原 C+ |
| --- | ---: | ---: | ---: |
| ready reference outcomes / 128B refs | 6,034 | 18,069 | UNAVAILABLE |
| pending reference outcomes / 128B refs | 16,373 | 17,752 | UNAVAILABLE |
| new allocation outcomes / 128B refs | 232,173 | 218,759 | UNAVAILABLE |
| accepted reference count / 128B refs | 254,580 | 254,580 | UNAVAILABLE |
| ready fraction / accepted refs | 0.023702 | 0.070976 | UNAVAILABLE |
| pending fraction / accepted refs | 0.064314 | 0.069731 | UNAVAILABLE |
| new fraction / accepted refs | 0.911984 | 0.859294 | UNAVAILABLE |
| DTC lower created / 128B requests | 232,173 | 218,759 | UNAVAILABLE |
| Tag evictions / count | 223,982 | 187,200 | UNAVAILABLE |
| PIB residency / all-64SM cycle mean | 12.336532 | 12.542329 | UNAVAILABLE |
| physical residency / all-64SM cycle mean | 127.587793 | 420.226681 | UNAVAILABLE |
| ready-to-collect / cycles per retired cacheable warp | 1.269707 | 1.287840 | UNAVAILABLE |
| collection / cycles per retired cacheable warp | 1.073989 | 1.073016 | UNAVAILABLE |
| fully-ready-to-complete / cycles per retired cacheable warp | 2.458890 | 2.475760 | UNAVAILABLE |
| L2 read sectors / 32B sectors | 928,692 | 875,036 | 876,692 |
| DRAM read payload / bytes | 11,307,264 | 11,281,024 | 11,268,992 |
| DRAM write payload / bytes | 19,858,816 | 19,865,472 | 19,861,376 |

L2/DRAM 可比性：`PASS_SAME_PATH_TYPED_DEFINITIONS`。

## BICG：终态机制与同路径计数

| 字段 / 单位 | 原 OO128 | 固定 T1-C | 原 C+ |
| --- | ---: | ---: | ---: |
| ready reference outcomes / 128B refs | 517,676 | 523,246 | UNAVAILABLE |
| pending reference outcomes / 128B refs | 17,532 | 38,359 | UNAVAILABLE |
| new allocation outcomes / 128B refs | 17,814,872 | 17,788,475 | UNAVAILABLE |
| accepted reference count / 128B refs | 18,350,080 | 18,350,080 | UNAVAILABLE |
| ready fraction / accepted refs | 0.028211 | 0.028515 | UNAVAILABLE |
| pending fraction / accepted refs | 0.000955 | 0.002090 | UNAVAILABLE |
| new fraction / accepted refs | 0.970833 | 0.969395 | UNAVAILABLE |
| DTC lower created / 128B requests | 17,814,872 | 17,788,475 | UNAVAILABLE |
| Tag evictions / count | 17,810,776 | 17,777,467 | UNAVAILABLE |
| PIB residency / all-64SM cycle mean | 2.232003 | 2.341379 | UNAVAILABLE |
| physical residency / all-64SM cycle mean | 106.206448 | 154.793317 | UNAVAILABLE |
| ready-to-collect / cycles per retired cacheable warp | 1.159021 | 1.273339 | UNAVAILABLE |
| collection / cycles per retired cacheable warp | 2.762977 | 2.758131 | UNAVAILABLE |
| fully-ready-to-complete / cycles per retired cacheable warp | 3.926686 | 4.037465 | UNAVAILABLE |
| L2 read sectors / 32B sectors | 71,259,488 | 71,153,900 | 70,409,324 |
| DRAM read payload / bytes | 943,113,728 | 767,204,608 | 468,501,632 |
| DRAM write payload / bytes | 278,784 | 232,480 | 117,280 |

L2/DRAM 可比性：`PASS_SAME_PATH_TYPED_DEFINITIONS`。

两个固定 holdout 的周期均低于原 OO：DWT2D 改善幅度很小，BICG 改善幅度较大。但 BICG 仍比原 C+ 增加62.334%周期；这项负收益完整保留，不能据此建立普适优越性或替换论文主配置。DWT2D 的新增分配减少伴随极小的 DRAM read payload 变化；BICG 的新增分配计数变化很小，DRAM read payload 变化更大，且 ready-to-collect 与 fully-ready-to-complete 条件均值上升。这些现象描述同一固定模型下的共现变化，尚无可加的整机周期归因。

以上计数比较描述同一定义下的变化；不把 credit 转换成 DRAM 字节，不把条件服务均值差当作可加的整机周期贡献。C+ 无 DTC 路径字段标 UNAVAILABLE。L2/DRAM 采用 Lane M 已冻结的单 stream、终态、controller 和 atom 单位检查；不能闭合时标 UNCOMPARABLE。详细定义、分母及来源见 [TERMINAL_MECHANISM_COMPARISON.tsv](TERMINAL_MECHANISM_COMPARISON.tsv) 和 [METRIC_COMPARABILITY_EVIDENCE.json](METRIC_COMPARABILITY_EVIDENCE.json)。

## 执行资源与硬件成本边界

| 输入 | wall | user 秒 | system 秒 | 最大 RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| DWT2D | 5:04.68 | 301.80 | 2.69 | 937,984 |
| BICG | 3:11:22 | 11454.31 | 4.24 | 2,412,544 |

资源样本 197 份，最大采样间隔 61.17 秒；采样中本 Goal 新 simulator 最大并发 1。最小 cgroup 余量 144.78 GiB，最小可用磁盘 55.75 GiB；memory/IO full PSI avg10 最大值分别为 0.02 / 24.93。

资源压力与 swap/OOM 计数包含所有项目，不能归因于 DTC；分钟采样不能证明采样间无瞬态。逐点 time-v 和全局 counter delta 见 [EXECUTION_RESOURCES.tsv](EXECUTION_RESOURCES.tsv) 与 [RESOURCE_EXECUTION_SUMMARY.json](RESOURCE_EXECUTION_SUMMARY.json)。

期间 host pswpin/pswpout 分别增加 34 / 73 pages，cgroup swap.current 变化 0 bytes；cgroup oom/oom_kill 增量分别为 0 / 0。不把非零 host swap 活动改写成零，也不从累计历史 oom_kill 推断本次运行发生 OOM。两个10秒准入 probe 与运行期 emergency 门槛分别核验，见最终资源/身份复核。

物理池仍为 640×128B=80KiB，ordinary 16KiB，shared 96KiB，OO PIB128，4 Tag banks、原有限服务配额与 global lower cap32768 均保持。Tag 从128条增至512条，逻辑覆盖16KiB→64KiB；每 lookup 最大 way 比较由4增至8。既有示意 Tag 模型为8864→35840 bits（增加26976 bits，3372 bytes），只包含既有地址/物理索引/valid/LRU 信息模型；generation、Ref、waiter、布线、端口与时序成本未闭合。1 cycle lookup 是冻结模拟假设，PPA/native、等面积与同频结论均 UNAVAILABLE。[RESOURCE_OVERHEAD.tsv](RESOURCE_OVERHEAD.tsv) 的 A/B/T0 行仅是既有审计参考，本轮没有执行这些点。

## 身份、预注册与执行收口

完整预注册提交 `e49de3c3967f8349485b62cd4040ff3b8574a697` 已于北京时间 `2026-10-17T19:31:44.717459+08:00` push 并 fetch-back，早于两个新启动；终态独立复核仍有 63 份冻结文件逐字节不变。实际新启动 2 次，时间区间最大并发 1；DWT2D strict PASS 后才启动 BICG，每个输入一次，没有重试或因性能调整参数。

Framework build `18a68dcccd795f1b6cda75504e9450d00c9cee02`，Core `6fba0136f8465b59fe5858a950fa39efb265f654`，binary SHA256 `fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b`。完整默认值与配置 echo 已逐项核对；相对各自原 OO 只有 sets32→64、ways4→8 两项差异。12 个原成员及完整 list、10/2 个 ordered kernels、逐 kernel CTA 与 active-thread instructions、守恒/排空和11项 finite service 的实际验收见 strict/ 与 run_receipts/。

原 coordinator 的保守标记 `SCIENTIFIC_AUTHORITY_CONFLICT_STOP_FURTHER_LAUNCH` 原样保留。两个授权点都已启动后，独立 EP-L2 更换输出根目录触发旧路径指纹拒绝后续派发。后续按实际 PID/start_ticks、精确 binary/config/source 身份只读核实为独立项目；原 coordinator、冻结63文件、timeout 和资源门槛均未修改，BICG 保持原进程运行。所有采样外部进程身份已闭合；原保守拒绝及首次未知证据不被清除。详见 [WRAPPER_SCOPE_ASSESSMENT.md](WRAPPER_SCOPE_ASSESSMENT.md)、外部身份收据与最终合同审计。

终态归档曾因第三个新 EP-L2 二进制的13条采样记录中断，原始失败已保存于 diagnostics/。这13条记录来自两个 PID/start_ticks 身份；恢复后按其精确 fb67448d… binary、Core/Framework 来源、逐配置及 input metadata SHA 单独闭合，只补充只读身份审计。197份资源样本中的23个独立外部进程均已识别；没有放宽原执行门槛或增加实际 attempt。见 [EXTERNAL_PROJECT_UNIFIED_FB_REVIEW.json](EXTERNAL_PROJECT_UNIFIED_FB_REVIEW.json) 与 [TERMINAL_ARCHIVE_REPAIR_RECEIPT.json](TERMINAL_ARCHIVE_REPAIR_RECEIPT.json)。

后台监控只读取终态与心跳，不负责 simulator 启动、重试或科学验收。终态归档工具也只在原执行权与 simulator 退出后读取完整 raw。strict、原始终态文件 SHA、输入/source/config 身份与独立数值重算见 [STRICT_AUDIT.json](STRICT_AUDIT.json)、[FINAL_CONTRACT_AUDIT.json](FINAL_CONTRACT_AUDIT.json)、[RAW_FILES_SHA256.tsv](RAW_FILES_SHA256.tsv) 和最终 FILES_SHA256.tsv。

## 科学边界与交审范围

原 GEMM/Gaussian 的 A/B/C 全矩阵只作已完成发现证据，不参与本轮新选型。本轮所有正负收益或失败均保留，不增加性能阈值。没有独立 sector 返回、内部 MSHR 占用和数值 load 正确性的输出证明，这些项目保持 UNAVAILABLE。

Lane A/M/T、原44行（41 PASS、3旧 Hotspot HOLD）、原 raw/control/locks、GM12 未定义状态、modern128 HOLD 和 v0.11-VI 主图均保持。本轮不授予 T1-C 论文主配置替换权，不开启 T2、新协议/机制/模型、物理池调参、新 Tag 或第三输入。完整声明见 [SCIENTIFIC_SCOPE.md](SCIENTIFIC_SCOPE.md)。

大 raw 保留 `/workspace/dtc-t1c-holdout-174-v1`；Git 仅提交小型审查证据。最终 HEAD/tree、全部文件 SHA、远端 fetch-back 与 clean 状态由独立 raw root 中的最终发布收据闭合，避免自引用哈希。
