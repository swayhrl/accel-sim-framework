# 109-DTC-L1 Durability Complement V1

固定合同 `2e8a7d4fc155f6a8ab041d3b31893abaacac12f2`；白名单固定在首次接手 `2e009bb7a360054dcebe47c680d64aa16d4a8b88` 的 `METADATA_MEMBER_MAP.json`。109 `PC` / `/home/huangrulin`，本次来源读段 `2026-11-09T15:24:52.428922+00:00` 至 `2026-11-09T15:24:52.755151+00:00` UTC。最终状态 **`SOURCE_SHA_PINNED_TARGET_ROUTE_HOLD`**。

## Gate A：当前 source 身份

只对冻结的 native extra301 与 SM89 CPU extra3 做逐文件内容 SHA256，使用逐路径 `O_NOFOLLOW`、regular-file 检查及读前/读后 `fstat`。结果 native **301/301、263,676,362B**，CPU **3/3、583,932B** 均 `SOURCE_SHA_PINNED`；无越界、不可读、变化或与上轮大小不符项。逐项路径、类别、当前大小、SHA 和读前/后元数据见 `EXTRA301_CPU3_SHA.json`。没有重 hash 原索引 285/45 个内部 payload。

native 本地 285 成员压缩包今日 SHA256 `af5c6ec76179f881f689f486829c025055764bd9e564e598c0dc18560865f984`，与 2026-10-16 历史归档文件 SHA 相同；CPU 本地 45 成员压缩包今日 SHA256 `95f3e6d6e3a986bdc7d9d2468374275e2e008b81cbd88d0ec026315117a6f28f`，也与原本地回执相同。这只核两个**压缩包文件本身**，没有重新读取压缩成员；native 164 目的端的历史 PASS 与今日目标状态分列。

## Gate B：真实 true164 直达路线

109 当前可见的两处相关 SSHFS 挂载都指向 `hrl174new:/root/share/mnt164/...`，属于历史经 174 的路线；在本次检查的 109 挂载表、既有入口和 SSH 配置元数据中，未核实到预先授权、可独立证明真实164宿主/namespace、接收权限与容量的直达接收端。因此 Gate B **HOLD**：没有建立目标目录，没有复制或传输文件，也没有接收端 SHA 或恢复测试。此结论只覆盖本轮检查范围，不宣称其他路线永不存在。

后续若要保全到 true164，需另有独立授权的直达接收端，提供真实宿主/namespace、专属新目录权限、可用容量和接收端独立逐成员 SHA 方法；不能经正在执行科研 Goal 的 174-DTC 环境借道。本轮 source 保持原位；未清理、改写、解压或搬移历史资产。

## 科学边界与停止

此包仅固定补集 source 身份，**没有取得 true164 新副本**；native 整树 586 文件不因此成为 `RESTORE_PASS`。SpMV cubin89 `NO_GO/HOLD`、LayerNorm cubin86/CALL 缺口、modern DTC 与 Tag 安全 HOLD 均保持。没有运行 native、NCU/nsys、capture、GPU、模拟或科学 request。下一步 `STOP_PENDING_EXPLICIT_TASK`。
