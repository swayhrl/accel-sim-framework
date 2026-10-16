# DTC实验台账 V7：已获用户授权的输入资格与来源审查

2026-10-16。**这是授权快照，不是新模拟结果。** 用户已同意Hotspot V2的条件准入与Btree/2DConvolution/LUD独立科学风险核查。原44行、所有RUNNING、旧trace、失败与HOLD保持不可变。

- [完整科学决定及source SHA](derived_input_authorization_v1/SCIENTIFIC_DECISION.md)
- [给原174主Lane A的补充Goal](derived_input_authorization_v1/GOAL_A.md)
- [给原174独立Lane B的补充Goal](derived_input_authorization_v1/GOAL_B.md)
- [26项更新矩阵](MASTER_MATRIX_V7.tsv)

## 分层状态
| 项目 | 现在允许什么 | 仍然不允许什么 |
|---|---|---|
| Hotspot | A先做独立bundle/consumer/输入语义检查；PASS后以新SHA登记B16/IO/OO和论文确需的相同输入资源参照 | 不能覆盖原trace/旧结果、不能即刻把新输入称native等价、不能未验收便算GM12 |
| Btree | B CPU-only审一个PC的full32来源合同 | 不改旧数据、不自动启动修正实验 |
| 2DConvolution | B CPU-only审修复前/后tracer version3来源 | 不凭版本3选择地址锚点 |
| LUD | B CPU-only审两kernel global load/store地址锚点 | 不把shared单条bank服务不变当全程序等价 |
| 主Lane A | 保持唯一启动器、原44行自然完成+strict验证 | 不reset或并发运行第二套旧矩阵 |

执行时先fetch实际174/A/B各branch HEAD与进程/锁。新注册的derived-input attempts必须先满足科学和资源gate。任何进一步协议/支持域/数据解释边界变化再停审。