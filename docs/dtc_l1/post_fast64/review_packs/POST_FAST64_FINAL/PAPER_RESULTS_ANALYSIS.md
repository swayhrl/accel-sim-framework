# POST-FAST64 paper results analysis

## 范围与证据边界（C01, C27, C28）

主性能严格来自冻结 FAST64；Lane-D 观察者证据仅作诊断，绝不进入 FAST12 GM。本 Lane-E repair 只做快照、表格、图形和 QA，不启动仿真或修改科学源。

## 主性能与机制证据（C01–C06）

12 个未四舍五入整数周期比值给出 IO GM 1.326143376x、OO GM 1.592062402x。ATAX、BICG、GESUMMV 的 IO 回归被完整保留；Gaussian 的约 1.108x 应表述为温和收益。Base pressure、IO HOL 和 OO retire/reclaim 是按各自分母定义的非互斥测量证据，不能拼成唯一因果解释。

## 敏感性与 D4（C07–C17, C22–C23, C26）

逻辑/物理/PIB 均只使用接受的同模式归一化单元。BICG/GESUMMV 16.5 KiB 是非数值资源边界，Btree 16.5 KiB 保持数值。D4 是容量的受控敏感性，覆盖仅限 BICG/GESUMMV/Btree；其内部 occupancy、inflight、L2、lifetime 和 pending-Tag 箭头仍是相关或不足，不能称为 L2 主导。

## 重复请求（C18–C21, C24–C25, C29）

IO pending-Tag eviction→pre-response same-line reallocation 的计数语义由源码证明；duplicate×128 B 仅为 lower-request payload。D5 的限定 OO 计数给出 7 个更低、3 个更高、2 个均为零；这不支持“OO 普遍消除重复”或由重复消除解释 OO 性能。Btree 的 OO/IO 比值较大仍须结合两边极小的绝对 duplicate share 解读。

## 12-workload explanations

`WORKLOAD_EXPLANATIONS.tsv` 保留了每个 Lane-A 的 performance behavior、pressure、HOL、retire/reclaim、traffic、interpretation 与 caveat，并逐项追加 C/D 的精确 duplicate 和 D4 范围。
