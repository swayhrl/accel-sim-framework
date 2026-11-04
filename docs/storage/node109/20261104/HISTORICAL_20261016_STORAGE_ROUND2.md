# Historical Node109 report — public review copy

- Source ID: `storage_round2_20261016`
- Original SHA256: `08c517f63b2f282d0ccccb5d6a6e50d5929e3b9427371b183776368f136a34bb`
- Status: Historical snapshot, not the 2026-11-04 current-state result.
- Disclosure: Private host/account details were replaced; see `HISTORICAL_REPORT_PROVENANCE.json`. The local original remains unchanged.

---

109 第二轮过期资产清查：只读分析
时间：2026-10-16；基于首批已完成清理后的新扫描。

结论
目前根文件系统可用 285,098,242,048 bytes，约 265.52 GiB；/data/c16 占 363.52 GiB；workspace 占 9.70 GiB。当前没有第一轮清理前的空间紧迫性。
下一批值得评估的非重叠候选合计约 118.39 GiB：旧任务私有 pip HTTP 缓存约 8.49 GiB，以及已有 164 归档依据的 payload 本地副本约 109.90 GiB。这是候选容量，不是已批准删除量，也不是保证可释放量。
本轮未删除、移动、安装、运行 GPU、获取 GPU 锁、修改旧实验资产内容或向 164 写入。只生成新的审计记录与临时扫描脚本，没有修改 Git 分支或启动新实验。

一、优先评估：仅私有 HTTP 下载缓存，8.493 GiB
以下三个精确目录合计 allocated 9,119,387,648 bytes：
/data/c16/awma/r19_fp8_readiness_20261001/cache/pip/http-v2：3.484 GiB
/data/c16/awma/r17_graph_search_20260930/cache/pip/http-v2：2.283 GiB
/data/c16/awma/vla_rtc_vjp_boundary_20260930/cache/pip/http-v2：2.726 GiB
这些是 HTTP 响应缓存，不包括 wheels、venv、Triton、Inductor、CUDA 编译缓存或实验 raw。候选所属缓存范围内未发现多硬链接或外部项目软链接；本用户可读进程 fd/maps 快照未发现项目文件占用。
原 ~/.cache/pip/http 与 http-v2 已在首批删除，不能重复计入本轮收益；当前用户级 pip wheels 等小文件继续保留。
执行前仍须刷新占用检查；本轮没有证明其他用户/未来任务永远不会使用这些目录。

二、已有归档依据的冷副本候选，109.901 GiB
A. Qwen3-30B-A3B，56.889 GiB
109：/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
164：assets/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
历史收据为 EXACT_FILE_SET_SIZE_SHA256_PASS。本轮重新核对 16 个 shard 均现存、两端大小一致，总权重 61,066,575,648 bytes；109 config/index SHA 与归档收据吻合。仅历史收据，没有逐字节重哈希这些权重。

B. OLMoE-1B-7B-0125-Instruct，12.892 GiB
109：/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e
164：assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e
本轮补齐了第一轮的证据缺口：收据名称是 MODEL_ASSET_RECEIPT.json，而非 MODEL_ARCHIVE_RECEIPT.json。其 11 项 payload 在 109/164 均存在、大小匹配；109 已重哈希的小文件与收据匹配。三份权重的大文件 SHA 本轮未重算。

C. AWMA R26，24.463 GiB
109：/data/c16/awma/r26_tied_weight_production_capacity_109_v1_20261002/checkpoints
164：provenance/awma/r26_tied_weight_production_capacity_boundary_109_v1_20261002/checkpoints
共 10 份真实 checkpoint，logical 总量 26,266,909,440 bytes。164 的完整 207 项发布清单逐项存在且大小匹配；本地/归档 manifest SHA 相同，历史全量验证日志存在。553 KB compact tar 不是这些 checkpoint 的备份依据，真实独立 checkpoint 文件才是。

D. AWMA R27 系列，15.657 GiB
1) /data/c16/awma/r27_varied_batch_capacity_109_v1_20261003/parent_readback/COMMON_POST_BOOTSTRAP.pt
2) /data/c16/awma/r27r1_varied_batch_capacity_109_v1_20261003/checkpoints/COMMON_POST_BOOTSTRAP.pt
3) /data/c16/awma/r27r2_varied_batch_capacity_109_v1_20261003/checkpoints/COMMON_POST_BOOTSTRAP.pt
以上三份为独立 inode、nlink=1 的约 2.446 GiB 父检查点副本；发布记录明确引用 R26 在 164 的同 SHA canonical 父检查点，不要求三份各自复制到各自归档目录。
4) /data/c16/awma/r27r2_varied_batch_capacity_109_v1_20261003/checkpoints/B1_C1_K2.pt：约 2.446 GiB，164 同身份实际文件与发布清单均在。
5) /data/c16/awma/r27r3_numeric_attribution_109_v1_20261013/raw/B0_a.pt
6) /data/c16/awma/r27r3_numeric_attribution_109_v1_20261013/raw/B0_b.pt
两份各 3,152,550,620 bytes，合计约 5.872 GiB；164 中确有实际张量文件，不能仅以 17.5 KB compact tar 判断其归档。
R27/R27R1/R27R2/R27R3 的发布清单分别 103/11/95/21 项，本轮远端逐项大小均匹配，所有本地清单 SHA 与归档清单一致。大 payload 本轮未重哈希。
仅这些明确列出的文件属于候选，不包括各轮报告、raw 小证据、manifest、收据或整个 AWMA 目录。

以上大文件候选未发现多硬链接或项目范围外部软链接。但文本扫描发现 Qwen/OLMoE 仍被历史脚本、manifest 引用，不能据此声称“没有依赖”。这些引用需要作为可重现路径保留；后续清理应先确认是否解除热副本保留，再核对本地与 164 的实时全量 SHA、当前文件占用及限定删除清单。

三、明确暂缓，不计入上述候选容量
E1 v1/v2：合计约 42.95 GiB。
/data/c16/e1_bounded_decode_trace_v1/formal_d1_d3_20260924_v1
/data/c16/e1_bounded_decode_trace_v1/formal_d1_d3_20260924_v2
本轮重新读取的终止证据分别是 INTERRUPTED_DIAGNOSTIC_NOT_SIM_INPUT 与 TERMINAL_RACE_REJECTED_NOT_SIM_INPUT，两者均禁止拼接并要求正式重新开始。它们不是合法 v3 输入，但仍是失败诊断证据。本轮对 164 的限定目录检索未建立同身份全量归档闭合；不得拿 v3 ACK 代替，不能直接当作已备份垃圾。

A26GR1 Rubble：整体约 40.77 GiB，继续保留。
场景/原始图像/下载包有较大空间，但尚无完整 164 归档与适用权利闭合。本轮不提出未经授权的大数据转储。
更重要的是，A61、A65、A67 各有 19 条外部软链接解析到其 venv，共 57 条。删除整个 A26GR1 会破坏当前科学资产的运行身份。A45H 还需保留原 CPUAdam 扩展与源码。

A61/A65/A67 与基础 Python：完整保留。
A65/A67 各有 90 条外部软链接指向 A61 的包，共 180 条；/data/c16/env/cpython-3.10.12 有 36 条项目外部入链。
原真实 IGB 数据、GraphBolt 转换、软件、数值失败证据、cache、A67 原始计时与审查资产都不列入本批回收。
A67 最新 HEAD 为 c425819d1f41e0cbd3053315cd5590697e808a3c，tree 为 5ae9be2bf51ba959b9588a8111ae28bf6f03af84，本轮 status 仍 clean，等待独立科学审查。

NequIP / A47 / A50G：暂保留。
NequIP V1R1 约 10.92 GiB，已有的小型归档不能证明完整 venv/wheelhouse 已归档；模型/AOT/canary/raw 必须保留。A47 cuVS 环境和 GloVe 数据有后续轮次复用关系，也不能用已发布报告代替完整依赖资格。

共享环境与 worktrees：不是本批优先目标。
/data/c16/env 约 27.61 GiB、envs 约 8.25 GiB，多个环境有共享包和历史复现引用，未建立整目录回收资格。AWMA 中几份大型 env 同样先保留。
Git 登记 188 个 worktree；workspace 总计约 9.70 GiB，其中 worktrees 约 8.94 GiB。尚未逐树证明 clean、已发布及无外部依赖，不提供可释放容量承诺；将来只能按 Git worktree 流程逐项处理。
/data/c16/capture 约 8.37 GiB，本轮未建立全部 trace 身份/硬链接/ACK 闭合，不计入可回收总量。

四、证据范围与限制
109 全新 du 元数据扫描、3,082 条项目软链接、20,588 个限定小型文本控制文件，以及本用户进程快照。fd/maps 的不可读项是 sshd/(sd-pam)；未扫描其他用户私有进程，也未查询 GPU 状态，因此不宣称所有外部任务为空。
164 经既有 174-new SSHFS 路径只读访问。本轮只重算小型清单、收据和部分模型配置 SHA，逐项核对选定 payload 现存与大小；没有重新哈希约 110 GiB payload，未运行历史归档验证脚本，未写入 164。
所有容量以 GiB=2^30 bytes 表示，目录 du 与文件 st_blocks 的微小差异来自目录本身。本批合计按选定文件块与精确 HTTP 目录统计，避免把父目录、子目录重复相加。候选文件的 nlink=1 排除了已知候选的硬链接双计。

建议顺序
空间目前充足，先完成 A67 独立审查。若后续决定清理，先选 8.49 GiB 私有 HTTP 缓存，再逐文件验证约 109.90 GiB 已有归档依据的冷副本。E1 旧失败 trace、共享环境和真实数据继续暂缓。没有自动执行任何后续清理或实验。

本地证据索引
summary.json：结论与容量总账。
node109-inventory.json：新目录大小、软链接、进程元数据、Git worktree 列表。
node164-inventory.json：指定归档的收据、manifest、实际目录元数据。
archive-manifest-checks.json：R26/R27 系列逐项远端大小核对。
archive-closure-and-dependencies.json：109/164 身份对应、父检查点映射、运行环境依赖与 E1 终止记录。
candidate-checks.json：候选 inode/link/size、可读进程占用快照与小型本地记录。
cache-breakdown.json / awma-breakdown.json：缓存及 AWMA 子目录体积。
bounded-text-references.json：限定控制文件中的历史路径引用，不含环境变量或认证材料。
SHA256SUMS：本地本轮全部文件的哈希索引。