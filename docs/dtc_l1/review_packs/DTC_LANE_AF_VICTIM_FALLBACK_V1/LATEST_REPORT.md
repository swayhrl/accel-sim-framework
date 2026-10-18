# Lane AF — reclaimable-victim fallback candidate

**CPU_PASS_BOUNDED / FULL_INTEGRATION_PARTIAL / NO_GO_REAL_INPUT_PERFORMANCE。** 原174主机 `huangrulin-174`，原容器root账户，CPU-only；非174-new。没有GPU/native workload、完整模拟、真实输入raw或AA5/其它Lane锁操作。只在AF独立分支/worktree修改源码与本包，不修改AG或其它Lane文件，不自动加入AG的8点主矩阵。

| 发布对象 | 不可变身份 / 入口 |
|---|---|
| Core基准 | X2 `e32afdcf44be3374ff36d22568ed01a075459b6f`，新worktree起点精确匹配 |
| AF Core | `hrl/iscas2027-dtc-lane-af-victim-fallback-core-174-v1` @ **`19dafca6b5636ee26f4c35e566c24e17e645edaf`**，已push/fetch-back、7-path allowlist和clean通过 |
| AF Framework | `hrl/iscas2027-dtc-lane-af-victim-fallback-174-v1`，基于X2发布 `631eb6418f6e7f1f548afd33351cbc0d98d27145`；最终commit/tree/clean见发布回执 |
| 输出 | `docs/dtc_l1/review_packs/DTC_LANE_AF_VICTIM_FALLBACK_V1/` |

默认OFF开关 `-gpgpu_dtc_l1_reclaimable_victim_fallback 0` 已注册并接入PAPER_OO frontend。ON仅当miss commit处无free physical、原LRU valid且有live Ref不能回收时，选择**同set最老的安全ready Ref0 mapping**。候选还要求allocated/visible/identity一致、waiters空、没有同identity finite service-return owner；pending lower持Ref与ready转移的不变量排除在途owner。没有候选仍按原路径拒绝；其它set不受影响。已有free、invalid原victim、原LRU本已可回收、命中或配额不足时保持原行为。

重查相同行优先hit/merge，已接纳consumer与旧generation不变；选择后复用原map-loss→release→RR allocation→generation++，不强制释放pending/live行。K1不等待global quiescence，旧Ref/late return仍沿保存identity完成，重复source请求/观察不造成double-free或重复map-loss。IO/sector/其它模式ON fail closed；其算法、sector mask、Ref粒度和共用stats/K1合同未修改。源码与机会定义见 [MECHANISM_AND_REACHABILITY.md](MECHANISM_AND_REACHABILITY.md)。

| CPU证据 | 结果与限制 |
|---|---|
| 新定向synthetic | **17/17 PASS**；2×3ways/physical4的高Ref LRU+Ref0次选机会，及physical3>Tag2、隐藏旧live allocation自然撑满pool，两种见证ON选择/OFF拒绝 |
| 无候选/已有free/原LRU安全/原victim invalid | ON/OFF均保持原选择/拒绝；其它set的Ref0行不被利用 |
| K1、身份与有限配额 | 旧Ref保留、late return、重复/旧generation负测、0xF sector mask、4-waiter quota、同cycle重复观察、Ref shadow、physical与map-loss守恒通过 |
| 原7个CTest＋2个新CTest | **9/9 PASS**；旧测试源码未改；实际生产option parser省略/0/1通过 |
| default-OFF differential | AF与固定X2的4组CPU API序列 **524行逐字节一致**；不是完整输入性能等价证明 |
| WB与candidate-full | 受控WB拒绝期间Ref不减少，结合未改动真实LDST gate源码；未进行完整operand collector/真实满queue注入，保留PARTIAL |

局部ON机会/触发计数 `reclaimable_victim_fallbacks()` 已实现：一次已通过前置门槛的access成功选择安全替代victim计1，getter无副作用；测试触发可核。它不是周期去重/唯一地址数，OFF的0不能证明机会不存在。**没有为此修改冻结AA5二进制/旧stdout，也没有改共用normal stats出口**；真实输入终态计数当前UNAVAILABLE，后续出口需单独审查。

9/9最终CTest前保留一次工程失败：新parser测试最初继承库搜索路径，加载CUDA vendor libcudart而缺Core符号。CTest环境绑定AF库后重建、全部通过；失败的XML/stdout/stderr SHA与修复commit保存在 [ENGINEERING_FAILURE_PRESERVED.json](ENGINEERING_FAILURE_PRESERVED.json)。没有因失败重跑模拟或改变策略。

构建最多2任务、CTest串行；完整Core库CPU构建wall1:46.51，最大单child RSS610304KiB（非合计峰值）。C++ ABI `config`仍56B，OO frontend488→496B；这些不是硬件面积。候选scan无新增simulated-cycle延迟是显式模型假设，端口、扇出、最老安全选择/回收同步与PPA/频率仍未证明。见 [RESOURCE_COST_AND_LIMITS.md](RESOURCE_COST_AND_LIMITS.md) 和 [RESOURCE_AND_BINARY_IDENTITY.json](RESOURCE_AND_BINARY_IDENTITY.json)。

**GO/NO_GO：** 可作CPU候选审查；暂不建议真实性能实验。必须先有同定义真实输入可达性事件，再由AG在性能前预注册AF-arm与新增预算；不从synthetic或全SM平均occupancy推断真实窗口/加速，不替换8点。必要原始事件字段见 [REQUIRED_EVENT_FIELDS.tsv](REQUIRED_EVENT_FIELDS.tsv)，简明判据见 [GO_NO_GO.md](GO_NO_GO.md)，未自动执行事项见 [PENDING_REQUESTS.md](PENDING_REQUESTS.md)。数值load/coherence、全ISA、真实加速、硬件资格均未由本包证明。

`SOURCE_SHA256.tsv`、`CORE_DELTA.patch`、`SOURCE_SCOPE_AUDIT.json`与包内 `FILES_SHA256.tsv`公开精确源身份/差异/文件SHA。Core发布回执 [CORE_FETCH_BACK.json](CORE_FETCH_BACK.json)；Framework内容发布回执随后写入 `CONTENT_PUBLICATION_FETCH_BACK.json`。最终两仓库commit/tree、逐blob与clean核验保存为 `/workspace/dtc-lane-af-victim-fallback-174-v1/FINAL_FETCH_BACK.json`，避免提交自身SHA循环依赖。AG按用户指定入口由**本会话＋GitHub不可变提交**交接，不创建AG分支/目录、不直接写其它Lane工作树。
