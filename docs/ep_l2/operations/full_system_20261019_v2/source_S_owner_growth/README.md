# S：OWNER_DECISION_AND_GROWTH，2026-10-19

独立有限阶段，原174，只读。协调冻结 `b2e5328aca825d6e9ebfe09e46fa208957834636`；执行分支 `hrl/ep-l2-full-system-s-owner-growth-20261019-v2`，以已完成原报告 `8c238970e26c172a1c8e1baefb219fcd4405823b` 为基底。协调分支仅提供授权材料，不充当实际科学运行身份。

主要交付：

- [增长与owner行动](WRITE_GROWTH_AND_OWNER_ACTIONS.json)：一次30秒间隔的两个快照；可见写入、deleted-open、共享盘归因限制及E许可缺口。
- [唯一退役决定请求](C16_EXACT_RETIREMENT_APPROVAL_REQUEST.md)：精确selector、A/G控制点、164/109交接、激活条件与回滚；尚无批准。
- [输入固定与selector摘要](PINNED_INPUTS.json)：5份V2材料及两个8c精确六文件selector，未重新盘点或哈希模型。
- `CURRENT_OWNER_IDENTITIES.json` / `ADDITIONAL_A_F_IDENTITIES.json`：实际可见HEAD与状态。E有正在编辑的4个tracked路径，保持原状；注册台账政策仍0/24不能被视为V2已发布。
- `GROWTH_SNAPSHOT_1.json` / `GROWTH_SNAPSHOT_2.json`：只含proc计数、路径/FD元数据和固定已知路径stat，不含cmdline、environment、日志或提示词正文。
- `FILESYSTEM_BACKING.json` / `E_READONLY_REGISTRY_PROJECTION.json`：路径设备及只读台账投影；没有调用或修改coordinator。

实测38.4554GiB可用，30.049秒下降23.6211MiB。D工作目录进程25,260,032B写入、Codex服务7,819,264B；不能用进程write_bytes等同净df下降。打开FD可见正分配增长184,320B，deleted-open去重24,576B。已知C16/DTC日志短区间未变；外部共享盘/瞬时写入未闭合，需实际owner或主机管理员核实。没有以namespace看不到为由证明没有写入，也不以cwd冒充E许可。

按实测距48GiB仍差9.5446GiB且需额外峰值余量。协调旧4.5GiB加38.747GiB上界仍不足48；两种时间点分别记录。当前假想释放后容量不是可用量、净收益或运行准入，授权释放0B。第二批三组保留原HOLD，无新全盘扫描。

本阶段没有删除/迁移12文件、修改监督器/C16或EP-L2/DTC-L1任务、恢复TLS B0010、重传B0001–B0009或重复T的SHA。T剩余三份与本次owner请求互不等待。完整W+V+T+M方案与累计40次由A/E落实；这些只读/控制证据不是native正确性、生产准入或科学结果。

`REPORT_SHA256_MANIFEST.json` 绑定本阶段发布内容。远端发布回读记录将单独附入，完成的是本次有限调查与请求交付，不是批准或清退执行。
