# Lane 3｜RO认证与Pending事务解耦

先完整阅读同目录README.md、COMMON_CONTRACT.md、COORDINATION_PROTOCOL.md，再执行本文件。公共合同单独保存，避免六份副本漂移。

本轮身份：Lane 3；执行分支：`hrl/ep-l2-ft20261016-lane3-v1`。这是待启动的连续执行Goal，不是运行状态。历史文档中的字母Lane不在本轮重命名范围。

## Goal

完成完整epoch RO oracle输入、保守资格验证及可独立开关的RO pending detach / Line-MSHR bypass路径。Oracle是实验假设，不声称现有硬件已有标记。

## 执行顺序

1. 独立分支/worktree；先阅读M3A_RO_CERTIFICATION_r1及Core write-allocate/ordering路径，不能重试!is_write()式不安全筛选后声称认证。
2. 用保留trace和源信息生成line粒度epoch manifest：绑定trace hash、epoch/kernel、address domain、read/store/atomic集合和排除原因。覆盖整个epoch所有可见agent；不能证明外部/并发写入不存在的范围不进入RO。只按模型假设排除外部agent时显式记账scope。
3. 使用流式/外存方法控制大trace的内存；初期只做开发集。资格只用来判RO，不把未来reuse信息混入实际policy。
4. 通过公共Payload接口维护独立事务{id,generation}，复用同一512项descriptor池。保留issued/ready/pending sector masks、waiter链、response backpressure和释放引用。
5. First miss可attached；attached同地址merge；detached后同地址新事务允许独立lower read。Detached Fill只服务waiters，不装Tag；旧返回不能修改新Tag。
6. 不复制现有按地址清理旧resident handle的静态逻辑，合法同地址多事务必须存活。payload role与resident visibility不能混为同一个状态。
7. 生产开关分开表示Tag detach与Line-MSHR bypass；不合法组合显式拒绝。首版采用保守waiter-aware策略（已出现同地址复用则保护）；不做预测器搜索。若细节与已接受语义矛盾，输出最小冲突，不擅改协议。
8. 测试sector乱序、同地址双事务、generation复用、descriptor满、响应背压、oracle违规注入和epoch终结。生产操作驱动数据/版本参考检验。
9. 交Lane 1最小接入patch；交Lane 5运行manifest与coverage/duplicate bytes统计。先发布可验证路径，再继续完善，不能把资格工具ready写成RO性能机制ready。

## 必须产物

RO_ORACLE_CONTRACT.md、绑定输入的manifest及exclusion/coverage.csv、RO_TRANSACTION_STATE.md、directed tests、SOURCE_MAP.md、patch/commit、RO_READY_MANIFEST。

RO line-metadata节省和新completion metadata成本必须同时披露；不得在MSHR128之外免费多给无界completion结构后称等预算优势。
