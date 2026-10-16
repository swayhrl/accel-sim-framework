# Lane 2｜TVD功能与脏写回保留

先完整阅读同目录README.md、COMMON_CONTRACT.md、COORDINATION_PROTOCOL.md，再执行本文件。公共合同单独保存，避免六份副本漂移。

本轮身份：Lane 2；执行分支：`hrl/ep-l2-ft20261016-lane2-v1`。这是待启动的连续执行Goal，不是运行状态。历史文档中的字母Lane不在本轮重命名范围。

## Goal

在公共Payload接口上实现clean TVD、dirty WB retention及原位read service/promotion。先交付clean可独立开关版本，继续补齐dirty路径；不等待RO。

## 执行顺序

1. 使用独立分支，公共Core由Lane 1整合；先做TVD独立模块和生产操作参考测试，禁止与Lane 1共享可写worktree。
2. 读取已定RO/TVD架构和公共合同。WAD/TVD总地址槽位128；mandatory WAD优先。新增payload pointer/state/mask/age成本单列，不额外增128项地址目录冒充复用。
3. 接口未发布时完成状态表、read/write/atomic transition tests及可直接接入模块。Lane 1发布后按准确commit适配一次，不无限轮询。
4. Clean TVD从真实victim selection中保留旧payload；不足资源时允许不保留，不阻塞mandatory路径。Read在Tag miss后额外1cycle目录查询，仍需真实bank与响应队列服务；不promote。
5. 部分sector有效处理必须精确；不能把line地址匹配当成全部sector命中。clean write/atomic先promote，同payload，不产生两个authoritative copy。
6. Dirty版本区分WB_STAGED、WB_INFLIGHT、WB_COMPLETE；WBUF lower-accept边界后的额外保留记为TVD成本。WB pending/inflight不可被当成clean机会项回收。Dirty read-forward按有效sector和可达preview执行；write/atomic等WB完成再promote。
7. 若取下层packet后失去payload独立副本，则不能声称in-place forwarding。新增数据阵列或改变释放协议不在本Goal授权内，报告具体问题。
8. 测试Pool/WAD满、promotion换出dirty resident、同地址读写原子交错、下层与ICNT背压、bank冲突、epoch清理。与生产驱动的数据/版本参考模型比较。
9. 向Lane 1交付模块patch和定向结果；向Lane 5发布准确可用功能版本。正式实验由Lane 5去重调度。先报告真实TVD hit与避免的lower reads，再解释cycles，不把shadow命中作为功能命中。

## 必须产物

TVD_STATE_AND_SECTOR_CONTRACT.md、TVD_METADATA_COST.md、clean/dirty分别的producer-linked tests、SOURCE_MAP.md、TVD_READY_MANIFEST、patch/commit、对照统计字段定义。

完成标准：read/promotion/dirty等待与forward都有生产路径覆盖；clean子集可以提前交付但不得宣告full TVD完成；不能静默改成全部等WB完成。
