# EP-L2 共享 Native registry 请求外层状态收尾

2026-11-11 00:34 UTC，EP-L2 唯一 Main 通过本项目三个已绑定的 owner `transaction()` 入口，逐请求把外层 `state=RUNNING` 修正为 `CLOSED_COMPLETED`。适用请求只有 `EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1`、`EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1` 和 `EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1`。

写入前逐项核对：Native epoch 2 与 registry SHA 配对；三个 request 均归 `EP-L2 Main`、余额和剩余写入承诺均为 0；3+2+1 个子点均一次消费、`CLOSED_ACCEPTED`，各归档回执 SHA 匹配且真 164 归档和两次不同 Native 目标恢复为 PASS；本批调度 claim 为空。owner 事务自动获取共享 `REGISTRY_UPDATE.lock`、保存前像、保护其他请求和历史字段、更新 epoch SHA、写入事件。未调用模型、登记、消费、验收、归档或退款。

| 核对 | 值 |
|---|---|
| 修正前 registry SHA256 | `32486efff5442bfe68ed4579edff8d38a691a325deaae0febe75e872e9455862` |
| 修正后 registry SHA256 | `159e694735a893d3c58f664c666b9fa4cb637171c07c3129dfed26eb950d0007` |
| owner 收尾回执 SHA256 | `f77466b96ad980002de53e0698917e5f4f2018f5762b1c378b3d91fe8454028e` |
| 全局剩余预算 | `84 → 84`，本批 3 个 request 均为 0 |
| 子点终态 | 6 个 `CLOSED_ACCEPTED`，未变 |
| Source | KEEP，未清理 |

独立回读确认当前 epoch 的 `native_registry_sha256` 与修正后文件 SHA 相同，三个请求均 `CLOSED_COMPLETED`、`remaining=0`、`reserved_write_bytes=0`，调度 claims 为 `{}`。`EP_L2_PARENT_REQUEST_CLOSEOUT_20261111_V1.json` 是现场 owner 回执；`close_ep_parent_requests.py` 是可审查的有界事务脚本，默认只读预检，`--apply` 已执行一次。事务的前像和逐请求事件保存在 Native `control/science_authority/request_history/` 与执行根 `control/authority_events/`。后续共享 registry 若被其他 owner 合法修改，应以新 epoch/registry 快照为准。
