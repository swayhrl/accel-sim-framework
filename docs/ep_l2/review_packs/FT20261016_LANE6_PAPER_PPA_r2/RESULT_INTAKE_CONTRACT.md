# r2 增量结果接收契约

本 Lane 只消费结果，不更改 Lane-5 runner、资格门槛或共享 registry。
本契约是论文侧 adapter，不要求为了适配图形重跑已合格 R0。

优先入口是已经阅读的 Lane-5 `campaign_r0.publish_pair` 原生格式。adapter 传入
`qualification_publication` 与 `native_pairs=[{publication_commit,
pair_repository_path}]`，必要时提供 `result_root`。`native_pair_intake.py`
直接从准确 Git publication 读取原 `RESULTS.csv` 和 `PAIR_RECEIPT.json`，核对
publication 的 Lane-5 receipt 包含该 pair、原生 run-key、R0 mode 合同、独立
证书、ordered config/aux/environment 与 trace-content hash recipe，以及保留
raw 和冻结 config。之后确定性生成本地展示 packet，并保留全部原 row/result/spec。
**不要求 Lane 5 新增 normalized packet 字段或改变已冻结结果**。
下面的已绑定 normalized packet 是可选输入方式，不是主实验的先决条件。

## 独立资格、manifest 与 partial pair

`plot_qualified_pairs.py ADAPTER.json --framework-repo REPO --output-dir NEW_REV`
读取 adapter 的 `publication_commit,receipt_path,receipt_sha256,bundle_path,
bundle_sha256,packet_file`。receipt 与 bundle 按 Git 准确提交回读并校验 hash，
receipt 必须是 Lane 5，且 artefacts 包含 bundle 或所在目录；bundle 中的
`normalized_pair_packet_sha256` 绑定 packet 的完整字节。packet 是对原科学 CSV、
原 run manifests 和 qualification 的无损映射；构造它时必须同时保存原输入
CSV/manifest 的 hashes 和映射，不擅自创建任何不存在的成功门槛。

packet 包含：

- `evidence_kind=FUNCTIONAL_IMPLEMENTATION`。
- `qualification`：独立 `INDEPENDENTLY_QUALIFIED` 的 Core/Framework/binary。
- `runs`：每项有 workload/mode/status、原 `identity`、run_key、raw_log_sha256、
  summary.cycles/instructions、effective_base_config_sha256、validation 与
  numeric_payload_validation。保留原 ordered-config/aux 与 trace 内容索引，
  可作为额外字段直接携带。normalization 的 base-config fingerprint 仅移除
  明确 mode selector，其余设置/ordered aux 必须完全一致。

运行 identity 使用 Lane-5 原字段：source SHAs、binary、runtime_config_sha256、
trace_content_sha256、epoch_range、feature/ideal/termination。run-key 按原
canonical identity 验证，不因论文 schema 迁移改写。R0 `ro=false` 在展示层可
映射 detach=false/bypass=false；开启 RO 时必须有两项显式位，不影响旧 R0 hash。
feature vector 允许实际资源整数，不能把 finite_wbuf=true 误当一个待关闭的
优化开关，或要求所有资源字段都是 bool。

每个完整 pair 立即可发布；完整五点之前 whole_group_geomean=null。
失败、超时、未收到单元与已完成但没有配对的单元分别保留，不画为 0。
低效/退化 pair 不删除。仅允许预定五开发负载 B16/U_WB16 主比较；C8、
重分区及扩展功能需准确对应的下一比较契约。

## dataless SASS 验证范围

当前接收的独立范围为：normal_exit、parser_success、sector_version_reference、
requester_exact_once、payload_identity、terminal_clean、wb_milestone_closure。
这些源自实际生产/独立测试，不以总量相等替代 requester identity。
numeric_payload_validation 使用 `UNAVAILABLE_SASS_DATALESS` 或定向已知字节范围
`DIRECTED_KNOWN_BYTES_ONLY`；不要求不存在的应用 full-byte/atomic 数值输出，
也不把它声明成 PASS。归一化前必须对照 Lane-5 真正发布的 gate 名称与 scope，
名称有差异就记录映射，而不是猜补。

## R0 / R1 / 历史分离

正式主图只接收 R0 B16 与同 R0 binary U_WB16。正式 ideal 由 Lane 4 单列，
需要 R1 自身 binary 的 B16 matched baseline；不能将 R0 numerator 填进 R1。
旧静态历史 diagnostic 73873/42918 已另行核验并独立绘图，不进入本入口。
TVD served_sector_bytes 保留该语义；lower/DRAM saved 必须来自匹配 OFF/ON 的
真实事务/字节差分。sector locality 不转成 TVD hits。

## 当前接收状态

本 revision 已通过原生入口接收 b47b721d 发布的 sad 正式应用 pair，生成
`formal_sad/WB_PAIRS` 与完整 figure/runtime manifest；其余四点保持缺失，均值null。
Lane-5 可先独立验证 R0 并立即运行主 pair，不受本文 adapter、TVD、RO 或 ideal
集成所阻。`RESULT_COVERAGE.json` 保存当前准确消费范围；后来的完整 pair
通过新 publication 产生新 pack，不覆盖本版。
