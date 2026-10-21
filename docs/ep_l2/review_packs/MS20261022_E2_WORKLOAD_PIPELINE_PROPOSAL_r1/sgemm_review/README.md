SGEMM 已有 A2/C/D 准备材料足够进入 E2 独立资格收口；本次静态复核没有发现需要新增机制、重建 main 或重跑整套 native 的依据。当前仍为 `REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE`，本报告不是资格签发或启动授权。

`STATIC_REVIEW.json` 保存独立复核结果、37 个小型 Git blob 的真实身份以及输入 stat。脚本 `review_static.py` 可重复进行有界复核，不导入或执行 campaign runtime，不读取大型 trace 正文，不改变中央 registry、lease、CLIENT 或其他 lane 文件。

已经闭合的准备项：

- A2 在 `89c3f4e186e5a2514cda94163b37e3a813ec704e` 的 S149/F154 个最终有效选项独立重算一致。10 项差异恰为 5 个机制选项及 5 个输入绑定选项。物理 P1、1168 总 payload、固定有限资源不变，F 的 W/V/T/M 全 ON，copy/data-free 等诊断关闭。旧 main61 不添加 capacity master 选项。
- C 在 `93f6db1881bb7bbb59f5e7f53196b7441ef3268b` 发布的 manifest/ranges 与 A2 配置绑定副本字节相同。范围表只有 `first_line,last_line_inclusive` 表头，没有获准 RO line；`NO_READONLY_CERTIFICATION` 是明确安全 fallback，真实 RO 机会仍 UNKNOWN，不能改写为实测零。C manifest 的 06cf 字段是明确保留的 schema/preparation lineage，实际 runtime 仍为 Framework9dd/Cored010/main61，不混写或隐瞒。
- 已保存 D 全输入证据涵盖 1 kernel、528 blocks、51,847,488 条 warp 指令记录、1,658,916,864 条 active-lane 指令，全部 native grammar/opcode 覆盖，global/shared atomics 均无；没有首条拒绝记录。其输入 composite SHA 为 `694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb`。当前小命令表 SHA 完全匹配，三条命令是两个 HtoD 加一个 kernel，当前大文件长度匹配。
- 18 项 exact-main61 通用 gate 元数据均独立回读且 SHA/PASS/production-driven 匹配，包括既有 `new_combined_fallback` 的 native exit0 和空覆盖 flags-on 检查；保留原 delta applicability 与旧 joint fixture 的资格边界。
- 既有 `parse_main_terminal.py` 支持 F 并将 RO 实际 manifest/scope 与本条件配置比较，不强制所有 F 都是 `TRACE_MODEL_CLOSED_WORLD`。因此当前静态证据没有要求改 parser 的理由；仍须 E 对本输入和 profile 正式封印。

最小未闭合项与流水安排：

| 门 | Owner | 具体工作 |
|---|---|---|
| 当前完整输入内容绑定 | E2 | stat 和继承 SHA 不能冒充当前内容哈希。复用保存全 grammar/non-atomic 证明，在原入口满足现行完整内容 identity 门；不重复大 grammar 扫描。 |
| SGEMM 独立资格及 parser/profile/input seal | E2 | 独立制作本条件 S/F input semantics、C fallback adoption、exact ordered config、producer/main/archive/parser/native gate 绑定。不能复制 FWT 资格编号或先把候选标为 PASS。 |
| 新独立探索 batch 授权 | 用户批准后由 E2 采用 | 仅此 SGEMM S/F 两次新启动。原32矩阵与 contingency8 桶均保留且不扩充；总 count 上限取消不等于本条件已经授权，不占用或伪造未启动旧槽位。 |
| 每次启动实际准入 | E2 原唯一中央控制器 | 核查当前 source/main/archive/config/spec/input/trace/oracle/parser/lease、CPU/RAM/Share、5GiB 底线及 2GiB 监控余量、累计结果生成和单端硬上限。 |
| 运行后科学接受 | E2，接受后立即交 D | durable native OS wait exit0；全部1,658,916,864指令、1 kernel、完整3命令；64slice FT/B0/MS/TVD/RO；epoch结束后最终快照、exact-once/sector身份及共享/native/RO/WAD/WB/descriptor资源退尽；无fatal、cap或timeout。运行退出本身不代表 PASS。 |

建议成本为 **2 次真实启动，单端 384MiB，配对 768MiB**；collector、资格和 metadata 必须在根提案另列明确余量。真实 walltime **UNKNOWN**，保存 D 离线 grammar 837.48 秒不是应用 walltime。若加入 FWT，共4次、端点合计1.5GiB只是待批准方案，不预约或启动。任何失败仍计费，保留负结果，不自动重试或退款。

本应用属于预先按 dense compute/reuse 和低旧压力控制依据登记的独立探索集合，未按新 F 加速比挑选；不替代 Btree，不自动加入原 MAIN 分母。原 source revision、capture command 和数值 payload 来源 UNKNOWN 继续显式保留，所提科学范围仅为冻结 trace 模型对照。不能据空覆盖报告 detach 机制激活或把数值复现缺口当作已经闭合。

本次零新增应用、native、build、Goal 或 controller；未改中央状态。静态检查初次因作者误写空表的列名而 AssertionError；核对 C 原字节后修正检查为真实表头，未修改候选文件或生产代码，最终有界检查成功。历史科学失败、HOLD 均未变更。

补查保存 immutable fingerprint 已完成，见 `SAVED_FINGERPRINT_SUPPLEMENT.json`。有界复核原 D 六份已知小元数据及后续 E inventory：后续 inventory 的 device/inode/size 与当前两文件均相同，但原完整 grammar/SHA 证据没有保存与其绑定的 dev/inode/mtime_ns；后续 inventory 也没有 mtime_ns，且原本只是 stat-only。因此不能仅凭这次 stat 将内容适用性升级为 PASS。合并审批建议包含**一次 2,216,170,035B 的原 SGEMM kernel 文件流式 SHA256 身份核对**，比较保存 SHA，记录前后 stat 避免读期间修改；不重复 grammar、不新增 native 或应用。此次补查仍读取 trace 正文0字节。

E2 自有候选资产也已准备于 `prepared_assets/`，详见 `PREPARED_ASSET_BINDING.json`：base0/1/2、S 与 C manifest/ranges/小命令表均保持已发布原字节；F 仅把 `-gpgpu_ep_l2_ro_ranges`、`-gpgpu_ep_l2_ro_manifest` 两个路径改为本 E 工作树内实际资产绝对路径，其余 F 字节和选项不变。独立重算仍为 S149/F154、10项 S/F 差异、固定 finite P1/WVTM。小命令表副本只是引用资产，完整 runtime trace entry 仍指向原完整 trace 目录。此变更消除未来对 A2 工作树小文件路径的依赖，属于非语义候选准备，尚未 E seal、正式资格、registry 采用或启动；main61及生产协议未变。
