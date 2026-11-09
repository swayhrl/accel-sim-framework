# 未来true164接收任务的准入条件（当前未获执行授权）

本文件仅预备后续存储路线合同，**不授权109或174-DTC立即创建连接或传输**。须由用户明确指定具有独立true164权限的存储执行端，且不借正在运行科学Goal的174-DTC活动环境；再通过用户转交启动。无此条件，109保持`STOP_PENDING_EXPLICIT_TASK`。

## R0：仅只读认证接收端
- 核验实际true164主机身份、mount/namespace、设备或存储卷、被授权的专属新目标目录；不得将`hrl174new`的历史SSHFS代理、109本机alias或其他项目共享存储冒充独立直达true164。
- 确认source-to-receiver链路由用户已批准且独立，不猜ssh地址/密码，不试提权、不配置未经授权的新代理、不通过174-DTC工作区/锁/registry/publisher，不干预其当前科学执行。
- 核接收方权限、可用空间、I/O限制、归档/暂存容量和可重复的接收端实际读取SHA/manifest核验方法。补集304源文件逻辑字节合计264,260,294B（包括旧本地压缩包），不能用它代替临时空间或压缩包容量估算。
- 任何身份、权限、容量或独立核验缺项则标`RECEIVER_ROUTE_HOLD`并停止；没有资格不能进入COPY。

## R1：只有未来用户明确授权且R0独审PASS才执行
- 冻结白名单来自`a5e158a3...`中`EXTRA301_CPU3_SHA.json`，native301及CPU3每项独立相对路径、bytes、SHA；109只读源，`COPY+SOURCE_KEEP`，目的地使用全新专属目录，不能覆盖历史285/45归档和任何现有source。
- receiver重新读取实际目标每个文件或压缩成员，逐项核相对路径、size、SHA/完整清单，并另记archive chunk/whole/commit及目标宿主namespace；scp成功退出码与源SHA列表不能替代目标核验。保留失败/部分件和原文件，拒绝目录穿越与隐式补齐。
- 可在独立隔离空间对**新304补集**做restore；没有安全空间则注明`RESTORE_NOT_TESTED`。补集receiver PASS只说明`TRUE164_COMPLEMENT_DURABLE`，不等于native全586或CPU全48可恢复；后者还需当前285/45目的端完整身份和联合恢复。
- 不发新的GPU、native timing、NCU、capture、模型、request或budget。SpMV/LayerNorm SM89准入HOLD、Tag安全HOLD、英文v0.23、历史SOURCE_KEEP均不变。
- 交付R0 receiver证明、copy exact SHA收据、新旧成员范围/restore状态、固定GitHub小型结果及109独占CONTEXT增量。174-DTC只在它自己的自然收敛checkpoint消费短说明。

## 未来单条转交指令（当前不要执行）
当用户指定独立合法true164存储执行端后，将本固定文档与`a5e158a3...`的冻结304项列表交给该存储端和109-DTC：先证明R0身份、权限、容量及独立SHA；仅在R0及用户授权均PASS时执行R1精确304成员COPY+SOURCE_KEEP和目标验证；否则以RECEIVER_ROUTE_HOLD收尾，不经174-DTC中转。