# Lane 1｜公共Core、有限WBUF与统一WB池

先完整阅读同目录README.md、COMMON_CONTRACT.md、COORDINATION_PROTOCOL.md，再执行本文件。公共合同单独保存，避免六份副本漂移。

本轮身份：Lane 1；执行分支：`hrl/ep-l2-ft20261016-lane1-v1`。这是待启动的连续执行Goal，不是运行状态。历史文档中的字母Lane不在本轮重命名范围。

## Goal

完成新有限WBUF基线B16/B8、等预算bank-matched建模及U_WB最小功能闭环，发布可被其他lane使用的公共接口。不要等待RO/TVD完成。

## 执行顺序

1. 阅读公共合同，核查当前工作树/活跃任务；新建独立Core和Framework worktree。记录选用父SHA。保留历史分支只读。
2. 优先提交并发布INTERFACE_CONTRACT_V1.md：PayloadHandle、role、allocate/reserve/commit/rollback、pin/unpin、sector-ready、WB lower-accept/set_done、response-commit、Tag/目录可见性接口。Lane 2/3依据该接口独立开发。
3. 参数化物理项数和静态quota，保留旧1152全关模式。全关在vectorAdd/cfd/sad上核实cycles、instructions及已有关键计数一致。
4. 实现有限WBUF数据容量与真实producer admission，C=16/8。不能只把shadow counter变成统计。原子预留/rollback、实际数据接收释放及WAD独立寿命必须定向验证。
5. 实现B16_BANKED/B8_BANKED；对新增WBUF copy与读出的bank操作记账。对Legacy分离阵列端口作明确假设登记，不据此掩盖primary端口差异。
6. 实现U_WB原位转WB角色和动态landing分配，不启用TVD/RO。取消固定C项WB数据天花板但受物理池、WAD及有界控制结构约束。处理所有WB-producing write/read/writeback路径，不只覆盖一个benchmark所走分支。
7. 对最坏情况Pool满/WAD满/下层满/同bank冲突验证退尽；证明WB send不依赖新的resident allocation。失败预留不能消耗漏掉credit或修改victim数据。
8. 生产路径加数据版本参考检验；输出copy次数和bytes、WB staging occupancy/lifetime、借用来源和拒绝原因。
9. 发布BASELINE_CONTRACT_V1.json（准确Core/Framework/binary/config SHA、数据预算、服务模型和开关向量），交Lane 5开始5点B16/U_WB实验。你可以用Lane 5分配的配额运行短canary，不能私自重复启动正式run-key。
10. 接入Lane 2/3经过独立验证的模块，保持开关和归因；按单模块、组合顺序验证，不自动改变TVD/RO科学语义。

## 必须产物

INTERFACE_CONTRACT_V1.md、BASELINE_CONTRACT_V1.json、STORAGE_AND_PORT_LEDGER.md、SOURCE_MAP.md、DIRECTED_TEST_RESULTS、OLD_STATIC_EQUIVALENCE.csv、B16_UWB_READY.md、最小patch与准确提交。

完成标准：有限WBUF是真实功能限制；U_WB真实使用共享容量；默认全关保持历史行为；生产接口可供后续接入；不得以仅有allocator或仅计数非零宣告完成。
