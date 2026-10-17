# Lane T — DTC-L1 有界 Tag/PIB 探索完整交付

**T1_CANDIDATE_FOR_REVIEW_ONLY：7/7 自然结束、7/7 strict PASS；预注册选择规则选出 T1-C（64 sets × 8 ways，512 mappings）。** 三个 T1 候选均通过探索门槛，C 的两输入几何均值最大，未触发 <0.5% 的 tie-break。此结论仅推荐进入后续审查，不是论文设计点或 holdout/PPA 资格。

原174独立分支 `hrl/iscas2027-dtc-tag-pilot-174-v1`。全部新运行在北京时间 2026-10-17 12:08–16:45 完成；执行器、后台只读监控均已自然退出，自己的执行锁已释放。新 attempt 恰好7个，无重复、重试或遗漏。

## 完整结果与固定评分

周期为模拟周期；R=同一原完整输入的 accepted original OO128 周期 / 新 OO 周期。T0 不参与候选选择。所有收益、负收益均原样保留。

| 点 | 输入 | 周期 | 对原 OO128 的 R | strict |
| --- | --- | ---: | ---: | --- |
| T0 | GEMM | 1,825,655 | 0.754753× | PASS |
| T1-A | GEMM | 1,151,431 | 1.196701× | PASS |
| T1-A | Gaussian | 3,335,973 | 1.138551× | PASS |
| T1-B | GEMM | 1,191,391 | 1.156563× | PASS |
| T1-B | Gaussian | 3,329,087 | 1.140906× | PASS |
| T1-C | GEMM | 1,071,405 | 1.286086× | PASS |
| T1-C | Gaussian | 3,278,356 | 1.158561× | PASS |

| 候选 | GEMM R | Gaussian R | 最小 R | 探索 GM | 选择 |
| --- | ---: | ---: | ---: | ---: | --- |
| T1-A | 1.196701× | 1.138551× | 1.138551× | 1.167264× | 合格，未选 |
| T1-B | 1.156563× | 1.140906× | 1.140906× | 1.148708× | 合格，未选 |
| T1-C | 1.286086× | 1.158561× | 1.158561× | 1.220659× | C胜出 |

门槛为两点 strict PASS、min(R)≥0.98、GM≥1.02。Decimal 40位精度独立复核得到同一 C 选择。GEMM/Gaussian 的原 OO128 周期分别为1,377,919 / 3,798,174，原 C+ 为1,511,333 / 3,379,152；C+ 比率完整保留在 [FULL_MATRIX.tsv](FULL_MATRIX.tsv)，不进入本次候选评分。

**T0负结果：** 新 GEMM IO128=1,825,655 周期，比原 IO256=1,457,468 周期增加25.262%。原 OO128=1,377,919，相对同深度 IO128 为1.324936×。这支持本输入上 OO 组织在实际 PIB128 时仍获益，同时显示缩减 IO 深度会退化；不能由此把 OO/C+ 差额分解成单一因果贡献。深度之外的组织元数据本来就不同。见 [T0_MATCHED128.tsv](T0_MATCHED128.tsv)。

## 机制观察及反向证据

下述计数只取最后一次累计打印，分母是同一输入的 accepted 128B DTC reference outcomes，不是重试次数或传统32B sector命中率。

- GEMM：成功新下行请求 3,993,335→2,091,696（减少47.62%）；ready reference占比 17.81%→41.25%；全64SM周期平均physical驻留 124.79→388.89 行/SM。fully-ready 到完成的条件均值却从 7.216 增至 12.392 周期/cacheable warp。

- Gaussian：成功新下行请求 1,392,149→638,862（减少54.11%）；ready reference占比 16.46%→38.85%；全64SM周期平均physical驻留 130.74→502.89 行/SM。fully-ready 到完成的条件均值却从 14.167 增至 17.909 周期/cacheable warp。

周期下降与更大的可查询映射、更少新下行请求、更多驻留利用在本探索中共同出现，但服务尾段条件均值变差；不能宣称所有阶段都改善或给出未测的因果占比。A/B同为256映射却有不同周期，说明sets/ways取舍不能只用条目数解释。DTC credits不是DRAM字节；M已披露原OO/C+下行量与DRAM路径的可比性限制，本轮不补造C+服务分解或DRAM收益。完整有类型字段见 [TERMINAL_MECHANISM_COMPARISON.tsv](TERMINAL_MECHANISM_COMPARISON.tsv) 和 [TERMINAL_METRIC_DEFINITIONS.md](TERMINAL_METRIC_DEFINITIONS.md)。

## 存储、比较和执行资源

固定 physical640×128B=80KiB、ordinary side16KiB、shared96KiB；OO PIB128、global cap32768、4 Tag banks、1 lookup/bank/cycle、finite服务和全部公共有效选项均保持。T1-C只把逻辑Tag从32×4增到64×8：映射128→512，地址覆盖16→64KiB；并未增加数据阵列。每次lookup最多比较4→8 ways，单bank映射32→128。

预登记显式packing例子中，Tag+physical-ID+valid+LRU信息量由8,864增至35,840 bit，增加26,976 bit（3,372 byte），约4.04倍。这个例子含可压缩set位，并未完整计入generation/Ref/waiter、端口、解码、fanout、比较器、电线、时钟或时序，**不是最小面积、RTL结果或PPA**。1cycle Tag只是冻结模拟假设，不能宣称相同频率或相同总面积。A/B较少映射及B较少ways的成本取舍完整保留，不能按不同负载另挑配置。见 [RESOURCE_OVERHEAD.tsv](RESOURCE_OVERHEAD.tsv) 与冻结的 [SCIENTIFIC_SCOPE.md](SCIENTIFIC_SCOPE.md)。

CPU执行记录：单点峰值RSS最高5,009,408 KiB（约4.78GiB）；采样并行RSS峰值10,014,720 KiB（约9.55GiB），最多2个新模拟并发。277个约一分钟样本中，最小cgroup内存余量151.20GiB，最小磁盘余量71.98GiB；内存full PSI avg10峰值0，I/O full PSI avg10峰值24.51。没有新增OOM/oom_kill，历史oom_kill=17没有清零。

初始10秒准入探针的swap/OOM增量检查通过。全程主机pswpin增加15页，pswpout不变，cgroup swap减少16KiB；这些共享计数包含其它项目，不能归因为本pilot，也不能宣称全程零swap活动。离散采样不证明采样间无瞬态。每点 user/system/wall/RSS 在 [EXECUTION_RESOURCES.tsv](EXECUTION_RESOURCES.tsv)，采样摘要和原始资源样本SHA在 [RESOURCE_EXECUTION_SUMMARY.json](RESOURCE_EXECUTION_SUMMARY.json)。

## 严格证据、包装修复与保留事项

性能前完整预注册提交 `ebdbbc753193a9783b5b276780c42d580f6ac79b`，12:07:57北京时间完成push/fetch-back；第一点12:08:40启动。原66份冻结文件至今与该提交逐字节一致。Lane M `d723784a8b897566b63113f95972f7a8d12a01ce` 的可核报告先于性能消费；hypothesis/input gate通过，同时保留字段缺口。

7点完整原输入：GEMM每点739,246,080 active-thread instructions/1 kernel，Gaussian每点283,685,120/510 kernels。最终复核共1,534个逐kernel严格结果、511个所选成员SHA；复用已有CPU body proof，没有重扫629成员。actual option echo含默认值逐项闭合；T0只改IO PIB，T1只改sets/ways；Core/build/runtime、trace、parser、640池、cap、64SM和其余有效选项均闭合。各点 source/raw/config/terminal/runner/hash 与 strict 收据绑定。

逐kernel检查natural exit0、完整顺序/CTA/active instructions、credit/lower/dependency/ordinary balance、PIB/inflight/active Ref/partial排空、physical allocation/reclaim守恒、64SM采样与11项finite统计。Tag-visible retained data合法，不强制physical allocated=0。独立sector返回计数、ordinary内部MSHR占用、数值load正确性、OO拒绝/重复地址的同义字段与真实PPA仍UNAVAILABLE，不用缺失字段伪造PASS。

保留一次确定性包装修复：V1把独立EP-L2项目误识别为DTC执行权冲突；在没有新点完成性能时，V2仅按固定binary/config/path fingerprint区分该项目，所有项目仍计入同一资源压力与内存门槛。原2个runner按UUID/PID/start_ticks接续，未重启、未重置超时、未创建新attempt。修复在后续5点启动前push/fetch-back；原HOLD、交接证据及退出码保留在 [wrapper_repair_v2](wrapper_repair_v2) 和 [WRAPPER_AUTHORITY_SCOPE_REPAIR_V2.md](WRAPPER_AUTHORITY_SCOPE_REPAIR_V2.md)。

用户13:03要求后台监控并暂停Goal后，独立只读observer仅记录状态；最初一次observer因继承PYTHONHOME启动失败，以system Python -E确定性修复，未触及模拟或参数。observer于16:46自然退出并写完成标记。监控交接提交84ff15071的两次TLS推送失败如实保留于pause handoff，该提交已随完整内容303019529一并推送并fetch-back核实，见 CONTENT_PUBLICATION_FETCH_BACK.json。旧工具轮询停止不等于模拟失败；原实际7个attempt均自然exit0。

原Lane A HEAD f5c37d6e、Core6fba0136均clean且未变；原44行manifest、HOLD_LAUNCHES、ROW_ADMISSION_HOLDS、旧锁inode与无owner状态均复核。5个旧对照stdout/start/terminal/config/runtime身份再次核实。未重启原Goal、未写旧raw。未运行DWT2D/BICG holdout、T2、modern128、LUD/2D/其它新输入或新机制；没有改原GM12或主图。

## 交付入口与后续边界

最终矩阵 [FULL_MATRIX.tsv](FULL_MATRIX.tsv)，固定评分 [DISCOVERY_SCORE.tsv](DISCOVERY_SCORE.tsv)，每UUID的 [strict](strict) 与 [run_receipts](run_receipts)，独立终态审计 [FINAL_IDENTITY_AUDIT.json](FINAL_IDENTITY_AUDIT.json)，完整attempt原文件SHA [FINAL_RAW_FILES_SHA256.tsv](FINAL_RAW_FILES_SHA256.tsv)，控制身份 [FINAL_CONTROL_IDENTITIES.tsv](FINAL_CONTROL_IDENTITIES.tsv)，根目录收据/资源SHA [ROOT_EVIDENCE_SHA256.tsv](ROOT_EVIDENCE_SHA256.tsv)，包内文件SHA [FILES_SHA256.tsv](FILES_SHA256.tsv)。大raw和资源样本保留在原174 `/workspace/dtc-tag-pilot-174-v1`，未提交日志、trace、binary或build树。

本T1到此结束。C值得提交“同一个配置的独立holdout + 实际硬件成本”审查；两输入探索GM不是论文GM12。当前没有自动holdout/T2执行权，不能把C替换进原44行、原IO/OO或冻结主结果。完整科学内容提交303019529已逐文件push/fetch-back，回执见 [CONTENT_PUBLICATION_FETCH_BACK.json](CONTENT_PUBLICATION_FETCH_BACK.json)。最终元数据提交的commit/tree/remote/manifest/clean回执另保存在原174根目录 FINAL_FETCH_BACK.json，以避免Git提交自身hash的循环依赖。
