# Codex Goal M — DTC-L1 frozen stdout mechanism consumer（原174 CPU-only）

**授权：只读CPU-only；不运行/不复活GPU或模拟器。** 以同目录`SCIENTIFIC_CHARTER_AND_PREREG.md`为唯一科学范围，先消费最终strict接受的实际raw。执行原174账户/容器，不是174-new。此任务可独立与T的CPU前置资格检查并行。

1. `git fetch` Framework `hrl/iscas2027-dtc-mechanism-tuning-plan-v1` 并核实远端HEAD；完整读科学合同与本Goal。读取Lane A最终执行分支 `hrl/iscas2027-dtc-service-closure-174-v1` HEAD `f5c37d6edcce832a72cb0830021bffa78df6cc13` 的 `final_closure_v1`、最终收据和统计定义，核对最新HEAD身份（不可reset/rebase A）。新建独立执行worktree/分支 `hrl/iscas2027-dtc-mechanism-consumer-174-v1`；若存在同名就先核是否活动并STOP，不覆盖。
2. 检查原A已经结束的coordinator和可能尚存的disabled/strict watcher与锁，纯stat/只读；不停止、不取得它们的锁。读取已验的GEMM C+/IO256/OO128与BICG C+/IO128/OO128/C16/C80/WAIT128原stdout（用final目录`ALL_ATTEMPTS.tsv`/UUID精确索引定位）及必要的已验strict/raw。原始二进制、trace、parser、Core、完整44原manifest均只读。不得做宽泛629 trace重审。
3. 建立每一字段的`source location + source SHA + logging stage + typed units + numerator/denominator + cacheable vs all instructions + includes retry? + per kernel or whole scope + conventional/finite comparability`。除既有DTC11服务字段外，检查可比的ready hits、pending merges、new lower read requests、L2/DRAM实际traffic、Tag/set/MSHR/PIB/pool阻塞、ordinary side path和重复Tag驱逐再分配。严格区分`counter events`与`cycle stalls`。不存在写UNAVAILABLE；语义不同写UNCOMPARABLE；禁止拿credit数乘以固定128B伪造DRAM流量。
4. 如果对C+与OO128的成功下行请求/字节等存在对齐的读路径字段，列出差异与由地址作用域支持的最小解释；禁止未经干预试验写成性能差额的单一因果贡献。GEMM的IO256/OO128是不同PIB深度，BICG的IO128/OO128才是合法同深度。严格区分ready-to-collect、collect、WB、ready-to-complete和完整replay。64SM全周期占用包括idle/tail，不推断active-only均值。
5. CPU审计形成一个预注册前结果：GEMM、BICG能否分别提出一条**可证伪的资源行为假设**，明确观察到/未观察到/不可比较。与探险组T将要改变的`logical_sets/logical_ways`的关系只能作为假设，不能从减少credit直接推断Tag命中改善。DWT2D维持独立核对，不展开新candidate。
6. 必须输出到执行分支 `docs/dtc_l1/review_packs/DTC_MECHANISM_CPU_CONSUMER_V1/`：
   `LATEST_REPORT.md`,`METRIC_DEFINITIONS.md`,`EXISTING_RUN_MECHANISM.tsv`,`CLAIM_SUPPORT.md`,`MISSING_FIELDS.md`,`INPUT_RUN_IDENTITIES.json`,`FILES_SHA256.tsv`。完整原stdout不要推Git，只提交小型证据摘要及SHA/只读路径。报告里逐条区分EVIDENCE_SUPPORTED、CORRELATION_ONLY、UNAVAILABLE。
7. 普通wrapper/manifest问题可基于已验来源确定性恢复，solve-and-continue；原始科学payload缺失、输入/运行身份不闭合、解释与冻结代码矛盾、指标语义变化则保留失败STOP。不得因结果不支持喜好而改字段/范围或追加负载。
8. 完成后commit、push、fetch-back并核HEAD/tree/工作树干净，报告实际HEAD、结论、下一步最小缺口及是否建议启动已预声明T0/T1。阶段M本身没有启动T任务的权力；T的运行权由单独严格合同和实时资源/独立预注册决定。

**冻结原事实（不重测）：** 原44行41严格PASS/3旧Hotspot HOLD，GEMM C+1511333/IO2561457468/OO1281377919，BICG C+25353488/IO12893312525/OO12847533116。不存在GM12、native DTC或等面积证明。
