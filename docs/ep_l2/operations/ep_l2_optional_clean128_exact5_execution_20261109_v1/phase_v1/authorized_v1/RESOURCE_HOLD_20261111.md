# Stencil EXT1 授权接收与资源 HOLD

用户在审阅固定提交 `680b20f5ee2dc3f5cd335adf005c7235ebc5abce` 的单点审查结论及精确草案后，明确回复“授权”。[授权记录](AUTHORIZATION_RECORD.json)只覆盖 Stencil EXT1 **一次**完整应用启动及一次消费，不继承已用尽的五点预算，无自动重试、退款或第二 dispatcher。

本轮先作只读接管和无启动准备。Native epoch 为 2，registry SHA256 `71d40678efd24108b112d5b0b4ab515de69760139af3ae84d334ca0309c511b1`；旧五点各 cohort 均 `CLOSED_ACCEPTED`、两份 request `remaining=0`，未发现新 EXT1 request/cohort、活动模型或本 Main 的 claims。旧 request 的状态字段仍是 `RUNNING`，不能把它当成活动模型。Source5 Core/Framework HEAD 与冻结身份相符且 tracked 树干净；ELF、静态库 SHA 相符。Stencil 输入绑定、101 个成员的 stat/路径、命令表 SHA 及真164 sshfs 挂载均核对通过，未重哈希巨大 Trace。

EXT1 283 项候选 map 以已消费 EXT2 的 `FROZEN_SPEC.json` SHA256 `34559c8f77cdb5ddd51dbdbed5eef65ef6bb426e233ff91fd2e023cd2c5f442a` 为基，唯一变化是 `-gpgpu_ep_l2_victim_extension: 2→1`；候选 canonical SHA256 `36b9d132a37645c2f6b3f68522fbfca39ed1f0ff091aab0b93d5668fb1738af9`，单行 overlay SHA256 `fef517887bdccd7b48d6803d14e371ee3aa2d68ce39f7577ccd0328a007fe7c5`。这些是**无启动候选计算**，不是新点已冻结的正式 Spec。

只读资源采样时 Native 可用 `3,828,506,624 B`。沿现有策略作一次保守的无启动试算：其他 owner 已承诺未来写入 `8,380,228,658 B`，本点结果与单个全局恢复窗口等 `203,423,744 B`，有效 Native 底线 `5,368,709,120 B`；准入所需 `13,952,361,522 B`，当时缺 `10,123,854,898 B`。该缺口随现场变化，执行时须重算。主机 RAM/CPU 账面有余量，真164挂载有效；旧资源适配器还把已验收但 request 状态仍为 `RUNNING` 的 GEMM 行报作未映射活动 RAM，需在新点适配时凭 terminal cohort/无活模型证据有界消除，不能改其账本或削减其他 owner 写入承诺。

**当前状态：已获新增单点科学授权；未正式绑定新 Spec、未登记新预算、未 claim、未消费、未启动。**当前空间低于 5 GiB 底线，本 Main 不清理旧资产。下一动作是在 Native 真实可用空间及 owner 承诺变化后，完成新点 Host/Native/资源有界适配与无启动验证，冻结新 Spec 并正式登记一次；随后在全局锁内做新鲜准入，合格才启动并按原合同验收、真164归档和双恢复。不能依据上述旧采样自动启动。
