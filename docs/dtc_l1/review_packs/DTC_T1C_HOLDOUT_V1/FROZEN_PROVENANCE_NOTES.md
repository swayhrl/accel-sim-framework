# 冻结前置证据与最终状态

PREREG_FILES_SHA256.tsv 中的63份文件保留性能前的原始字节。其中 CPU_ONLY、NOT_LAUNCHED、PENDING_NEW_STRICT_RUNS、new_full_simulator_attempts=0 是预注册时的状态；实际终态以 FULL_MATRIX.tsv、STRICT_AUDIT.json、FINAL_CONTRACT_AUDIT.json 和逐 UUID 收据为准，不回填预注册文件。

SOURCE_IDENTITY.json 逐字节复用 Lane T 的 source/proof SHA 清单。其两个 selection 注释中的 GEMM/Gaussian 指既有 Lane T 的原始选择；本轮 DWT2D/BICG 的完整输入和12个 kernel body proof 由 SOURCE_INPUT_IDENTITY.json、INPUT_PREFLIGHT.json、ORDERED_KERNELS.json 和 inputs/KERNEL_BODY_AUDIT.tsv 指定。仅复用已有证明，没有重扫629成员。

RESOURCE_OVERHEAD.tsv 也保留既有容量审计的 A/B/T0 参考行。本轮只运行 T1-C×DWT2D、T1-C×BICG；这些参考行不属于新的实际 attempt，也不表示扩大选型范围。

AUTHORITY_ACTIVE.json 的 foreground=true 是原有限 coordinator 的启动方式标签。之后核实其独立 session、无TTY、stdin=/dev/null，并挂接被动后台心跳及终态 CPU 归档；原 coordinator/runner/PID/start_ticks/timeout 未改变。

RESOURCE_EXECUTION_SUMMARY.json 的 samples_with_unrelated_project_processes 统计旧 wrapper 单独分类桶；新输出路径被保守保留在 processes 桶中，因此该字段为0不代表没有其它项目。全体 host/cgroup/PSI/disk 始终包含其它项目。EXTERNAL_PROCESS_FINAL_RECHECK.json 独立合并两个桶核实所有23个外部进程，原始采样文件 SHA 见资源收据。

保守的 SCIENTIFIC_AUTHORITY_CONFLICT_STOP_FURTHER_LAUNCH 标记和首次未知身份记录、归档原始失败均原样保留。最终身份闭合是补充审计，不清除此标记，不修改科学身份、资源门槛或执行历史，不重新启动任何模拟点。
