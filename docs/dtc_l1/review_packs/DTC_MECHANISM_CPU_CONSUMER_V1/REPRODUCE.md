# 只读CPU复核

执行分支 `hrl/iscas2027-dtc-mechanism-consumer-174-v1` 来自文档HEAD103c12ca；Lane A只读入口固定f5c37d6e。CPU输出在 `/workspace/dtc-mechanism-consumer-174-v1`。本任务已完成，不在现有目录重复启动或覆盖产物。所有阶段只写本新worktree/输出目录，使用exclusive-create；原始stdout/CSV/strict/trace/Core/binary不复制进Git。

源代码：

- `util/dtc_l1/mechanism_consumer_cpu_174_v1.py`：固定7个R2 UUID和2个BICG canonical复用；SHA核验、调用未改strong collector只读recollect，与final strict逐字段相等；独立解析stdout全部kernel/11服务字段/分访问类型cache桶/20controller DRAM tuple；核终端CSV；输出九臂表和全部raw counter摘要。
- `util/dtc_l1/mechanism_metric_definitions_174_v1.py`：生成69列指标的定义和逐源码SHA；把真实conventional HIT/HIT_RESERVED等原值放在独立上下文表，避免跨域命中率。
- `util/dtc_l1/mechanism_supplement_cpu_174_v1.py`：保存已执行的hypothesis封存、旧DWT2D核对、原表差分/累计范围审计及postcheck配方。前几项在本轮用等同内联CPU命令执行，随后将配方保存，不能把保存脚本当额外执行一次的收据。postcheck直接执行该脚本。

完整复现需另获授权的新隔离CPU输出，保留所有预选UUID、原始SHA、统计语义和顺序，仅调整wrapper的PACK/OUT位置及重复任务护栏；不能通过改原输入/collector/Core或期望值获得PASS。步骤：primary consumer → metric definitions → 在读取DWT2D机制字段前写原假设并执行supplement hypothesis → supplement holdout（仅两个旧accepted UUID）→ supplement derived → supplement postcheck → 文件清单及Git发布检查。任何科学身份/源语义矛盾保存FAIL_STOP，而非改字段/切近似baseline。

当前包无需重跑任何阶段即可只读复核：按SOURCE_SHA256.tsv逐一SHA对应源文件、raw/stdout、strict、config和CSV；按FILES_SHA256.tsv核本包与3个CPU工具。用INPUT_RUN_IDENTITIES的exact run/UUID与A最终ALL_ATTEMPTS/final integrity索引对读，不能凭程序名寻找相近attempt。源码行号以finite6fba0136为参照，traditional6582b9d同名函数文件SHA亦逐字段绑定。

原值和派生式：GLOBAL_ACC_R成功注入取一次最终counter；L2读TOTAL_ACCESS由HIT+HIT_RESERVED+MISS+SECTOR_MISS组成，并等于4×global read注入；MSHR_HIT是补充桶、RESERVATION_FAIL是重试，不加进TOTAL_ACCESS。实际DRAM读B=(末次20controller的n_rd+n_rd_L2_A总和)×32，写B=(n_write+n_wr_bk)×32；CSV末次sector数独立对齐。DTC11均值的numerator/denominator见METRIC_DEFINITIONS.tsv；每个有限run必须满足samples=64×cycles和ready分解恒等式。

SOURCE_SHA256覆盖large只读源的身份；FILES_SHA256覆盖Git交付的小文件，均排除自身以避免循环。没有把原trace payload重新扫描；其member/list身份复用A最终629-current-bytes收据，并现场核选定list，完整kernel/活动指令另由原raw独立对照。最终push/fetch-back的HEAD/tree回执保存在输出目录外部JSON，不写入包含自身HEAD的Git文件。
