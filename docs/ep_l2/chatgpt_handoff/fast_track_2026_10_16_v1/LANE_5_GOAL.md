# Lane 5｜独立验证与共享实验调度

先完整阅读同目录README.md、COMMON_CONTRACT.md、COORDINATION_PROTOCOL.md，再执行本文件。公共合同单独保存，避免六份副本漂移。

本轮身份：Lane 5；执行分支：`hrl/ep-l2-ft20261016-lane5-v1`。这是待启动的连续执行Goal，不是运行状态。历史文档中的字母Lane不在本轮重命名范围。

## Goal

建立全局去重和资源配额，独立验证Lane 1/2/3/4版本，滚动执行最小功能矩阵。保持负结果与完整provenance，不为等待完整机制阻塞先完成的对照。

## 执行顺序

1. 自动定位节点仓库、已用CPU/内存/swap、活跃模拟器、trace与结果索引；不干扰其他项目任务。建立共享RUN_REGISTRY.json/锁和HOST_BUDGET.md。run-key必须覆盖公共合同的全部身份。
2. 阅读历史13-workload映射，不把不同输入规模当同workload重复结果。旧观察数据与新有限WBUF性能数据分表；不强迫重新跑80行校准。
3. 即刻建立结果schema和数据/版本参考测试接口，完成无依赖测试。Lane 1发布新B16 binary/config后运行全关等价与真实有限WBUF检查；未通过不能开展正式机制矩阵。
4. 初批五个开发workload：B16和U_WB16先行；Lane 2/3合格后追加U_WB_TVD16和U_WB_RO16；FULL在交互测试后追加，不最先运行。
5. 与Lane 4共用baseline和全局配额。每run启动前获取锁并检索run-key；中途变更source/config则新key，不覆盖已完成。所有raw/config/audit只写新结果目录。
6. 独立重算关键closure：unique requester恰好一次响应、sector数据正确、无stale tag fill、无Payload/descriptor/WAD泄漏、WB created/accepted/completed各自闭合；性能运行的合法终态按工作负载语义登记，不用软件进程退出代替硬件状态退尽。
7. U_WB有局部效果后，代表点追加同1168预算的静态重划分对照；视目标辨识能力增加compute-only WB144强参考。不要为了统一池看起来好而丢掉强对照。
8. C8只在出现真实机制效果的代表workload加上同1160预算匹配B8/U8；不把1168版U拿去与1160版B比。WBUF16为primary不随结果改变。
9. 对验证集btree/dwt2d冻结policy后运行；scan单独长任务。短片段只作为diagnostic，不纳入完整应用汇总。
10. 真正的mechanism x downstream headroom四格实验，只在已出现局部功能效果后选择一轴代表点。不能把H速度改善写成H0主结果。

## 必须产物

RUN_REGISTRY、HOST_BUDGET、VALIDATION_MATRIX、BASELINE_RESULTS、MECHANISM_RESULTS、RESOURCE_MOVEMENT、SOURCE_MANIFEST、RAW_LOG_INDEX、失败/未完成清单、给Lane 6的可直接制图CSV和解释。

所有CSV须机器可读；定义cycle累计是否按slice求和、need/block尝试分母、unique请求、bytes及WB/TVD寿命边界。禁止把retry计数等同停顿总周期或按full占用推因果。
