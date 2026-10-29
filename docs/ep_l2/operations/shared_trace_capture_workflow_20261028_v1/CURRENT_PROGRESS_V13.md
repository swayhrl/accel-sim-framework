# V13 R2完整采集与后处理状态

时点：2026-10-29T15:38:10.108003+08:00。用户已批准逐程序分析后推广R2：优先保原空间工作集、类型、预热和算法阶段，仅减少确认属于计时的重复。延续[重复缩减方法](WORKLOAD_REPETITION_REDUCTION_METHOD_V1.md)与[审查模板](WORKLOAD_REPETITION_REDUCTION_REVIEW_TEMPLATE_V1.json)。

## 实际采集结果

四项均已完成原程序已有检查、完整采集及独立owned清理验收。下表记录数为producer声明，尚未成为F9全记录验证结果。

| 新输入 | 保留与缩减 | kernel | 声明warp记录 | 压缩trace字节 |
|---|---|---:|---:|---:|
| scan R2 | N6815744、17种长度、seed2009、所有阶段；100→2轮 | 66 | 182048256 | 987571924 |
| alignedTypes R2 | 49999872B内存、12类型、64×256；32→2轮 | 24 | 60755776 | 375484600 |
| transpose R2 | 1024²、8变体、每项1轮预热；100→2测量轮 | 24 | 18874368 | 97629336 |
| convolutionSeparable R2 | 3072²、seed200、17tap、行列两阶段、1轮预热；16→2测量轮 | 6 | 67903488 | 436263620 |

合计120次kernel启动、329581888条声明记录、1896949480B压缩trace。纯插桩应用时间合计约18.8分钟，排除构建、QA、调度和后处理；这不是原生GPU性能或模拟器耗时。scan采集546.3秒，仍保原52MiB两主数组，工程小scan的2MiB工作集没有混入本批研究输入。

scan原生17种长度全部Match；alignedTypes保12类型packed检查；卷积保原全图CPU行列参考，实际相对L2误差为0。transpose保原检查，其中coarse/fine仍是原程序自比较，不能声称八变体都经过独立数学oracle。所有输入、构建及用途按新binary和argv分别冻结，未替代旧默认输入。

## 下一阶段与资格

四项完整记录F9、group、CRC/整SHA、轻量consumer、裁剪及公共成对归档仍待完成。采集完整不授consumer或科学资格，producer声明不替代正文校验。两个CPU槽已实际启动完整F9：slot0处理scan，slot1处理alignedTypes，并在每项正闭合后自动接续transpose、卷积。两工作进程实际同时持各自角色槽WRITE与canonical LOCAL_IO READ；同qid Native资产EX和Root资源门保持。F9当前尚未产生PASS，不能从启动或I/O增长声称校验完成。

GPU保持单队列，canonical Comfy实时queue、GPU/LOCAL_IO及Native资产锁沿实际批准入口使用。本批已运行的legacy独占锁代码没有热替换。共享I/O仅对Root精确NAS角色生效：GPU最多1、CPU最多2，CPU固定不同核、各hard2GiB及phase1.5GiB，GPU角色在本批合同中INACTIVE。角色槽先EX、I/O再SH；旧EX持有者仍互斥。实际FD继承、私有负例、数据闭合和资源已独立审查后签准，当前两CPU工作进程同PID/ticks并行运行。

## 共享库基线与边界

严格公共目录保持71常规、71裁剪，计对象而非独立程序。RAW7独立公共目录已Root接受2453成员、54847407072B，Main与DTC均实际读取通过；其中大默认资产的重POST、裁剪及consumer缺口按用户范围延期。上述RAW数不能充作普通/裁剪完成数。

SM70归档和125输入NAS访问已完成；全库Native正文回读已取消。153项专项仍明确延期，不因Goal UI旧目标文字自动恢复。源KEEP、释放0，近期/计划/未知复用缓存保留。科学资格、预算、历史均不变，外部ChatGPT审稿尚未收到。

## 执行方法与已证实问题

见[构建与队列检查](R2_BUILD_CAPTURE_LESSONS_V13.md)和[机器时点](CURRENT_DELTA_V13.json)。已接受代码的检查快照在[R2流水源码快照](R2_PIPELINE_V13_SOURCE_SNAPSHOT/README.md)，供审阅，缺少Root运行授权不能执行。原始小验收快照和NAS引用见[R2证据索引](R2_WORKFLOW_EVIDENCE_REFS_V13.json)。
