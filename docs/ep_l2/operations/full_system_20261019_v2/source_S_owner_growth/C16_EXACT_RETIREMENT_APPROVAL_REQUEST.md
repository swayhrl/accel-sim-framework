# C16 精确退役决定请求：S / OWNER_DECISION_AND_GROWTH

状态：**待一次明确的用户或实际 A/G owner 决定；没有签字，没有执行许可。** 本阶段的只读调查已完成，旧全局盘点和旧 TLS Goal 不重启。冻结协调提交 `b2e5328aca825d6e9ebfe09e46fa208957834636` 的 MASTER §0、RESOURCE §3–4 明确没有授予 C16 监督器修改、恢复写入或源 unlink 权限；历史上传收据和 164 模型存在也没有结束未来保留义务。

建议本次一次决定：**停止从原174这两套精确六文件路径继续供给 RAW7B/AWQ7B，未来统一由164权威版本及109经验证的本地副本供给；同意由实际 A/G owner 实施下列最小、可回滚的供给控制改动。** 将尚未开始的旧路径供给计划取消或改为新版本任务；正在运行或已预约的消费者必须逐项清退后才激活。任何一项未满足都保持该项 HOLD。该决定不包含删除12文件、执行原生恢复、模型传输、修改109副本或恢复TLS B0010。

本次审批对象为这个版本的请求及 `PINNED_INPUTS.json` 绑定的 selector / 控制源码。批准人、身份、时间、请求版本、A/G执行与运行队列签收回执均须记录；当前全部为空，S不代签。如果决定继续保留，两套源文件保持原状，记录保留责任人与下一次实际触发条件即可，不再循环做同一调查。

## 1. 精确范围与已有证据

复用 `8c238970e26c172a1c8e1baefb219fcd4405823b` 原报告的两个 selector，字节完全一致，没有重新盘点12文件，也没有读取/重哈希模型：

| 六文件集合 | 原报告文件 | SHA256 | 可见分配上界 |
| --- | --- | --- | --- |
| 外发 P2/P3 | `PROPOSED_SELECTOR_OUTBOUND_SIX_UNAPPROVED.json` | `2c258b589bff3eb0e7154e775bc2973c932ec94144075edb5060b0a2d5205581` | 20,802,138,112 B |
| 原始模型 | `PROPOSED_SELECTOR_LOCAL_MODEL_SIX_UNAPPROVED.json` | `0ce1ab80f4be37b5be29d8d82fcc25a6fc94e1d9efea83df0f99a65e966ef235` | 20,802,158,592 B |

原报告相对本目录为 `../../storage_c16_model_dualcopy_20261019_v1/old174_owner_second_shortlist/`。精确路径、device/inode、大小、uid/gid、不同 mode/mtime、历史预期 SHA、对应权威目标路径均在上述 selector；它们仍然是 **UNAPPROVED**。新阶段不把旧 metadata 或历史 SHA 标为当前内容验证。

两种 deployment：

| deployment | 冻结 revision | 文件 |
| --- | --- | --- |
| `c16_qwen25_7b_raw_reference` | `a09a35458c702b33eeacc393d103063234e8bc28` | `model-00001-of-00004.safetensors` 至 `model-00004-of-00004.safetensors` |
| `c16_qwen25_7b_awq` | `b25037543e9394b818fdfca67ab2a00ecc7dd641` | `model-00001-of-00002.safetensors`、`model-00002-of-00002.safetensors` |

外发根分别为 `/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_P2_168c9714/models/c16_qwen25_7b_raw_reference/` 和 `.../C16_GPU_PACKAGE_P3_168c9714/models/c16_qwen25_7b_awq/`；原始根分别为 `/workspace/c16_assets/c16-a/metadata/Qwen__Qwen2.5-7B-Instruct__a09a35458c702b33eeacc393d103063234e8bc28/` 和 `.../Qwen__Qwen2.5-7B-Instruct-AWQ__b25037543e9394b818fdfca67ab2a00ecc7dd641/`。只选择 selector 的12个普通文件，不扩大到任何目录、tokenizer、配置、包清单、Git、输入、trace、历史收据或其他模型。

旧 G 的 P2/P3 状态是 `CONSUMED_TRANSFER_HASH_CLOSED`，已上传及收据闭合，不证明没有重发义务。冻结包生产提交 `168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d`；P2/P3 package manifest SHA 分别为 `c937590dd4ea2b4f6407db7d8b077ed263af3cbc14562ef34142aa834b133f26`、`704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c`。原报告 `SOURCE_OWNER_DECISIVE_LINES.json`、G消耗回执、`C16_SIX_SHARD_OWNER_AND_FUTURE_USE.json` 继续作为来源。没有找到有效的 A/G 精确退役许可。

当前仍未闭合的具体计划不是“模型是否存在”，而是：G实际传输队列、脚本或定时调用是否仍指向上述旧路径；A是否允许停止两个deployment的本地供给；109实际副本的路径、owner与当前6文件manifest。历史 `SOURCE_RETAIN` 的 `/root/share/c16_recovery_v3/models` 不是这12路径的释放授权，不改该目录。

## 2. G：终止外发供给的最小控制改动

当前 G HEAD `73850d93a4c97537976d799759b9440112eadea9`。精确控制源码 `util/vm_tlb/c16/lane_g/runtime_package_transfer.py` 的当前摘要见 `PINNED_INPUTS.json`，原文只读副本 `G_RUNTIME_PACKAGE_TRANSFER_REFERENCE.py.txt`。

1. 对两个deployment建立一个**版本化、仅操作用途**的 retirement policy，绑定本请求、两个selector摘要、两种revision、6个逻辑artifact_id和12个旧路径。初始状态 `PENDING_APPROVAL`，不能凭文件存在激活，也不能改变历史包元数据或历史验收结论。
2. 在 `materialize()`（当前149行）完成小包metadata身份读取后、遍历任何payload或创建目标之前，检查所有待供给行；对退休deployment/旧路径命中直接拒绝整项任务。`payload_bytes()`（81行）在打开绝对路径前做同一检查，覆盖直接调用。仅给新代码加护栏不会阻止调用旧冻结代码，必须同步关闭实际调度/传输入口的旧任务。
3. 此 helper 是 transport-agnostic，只物化/核验，不调用 rsync；不能拿它冒充自动重发总开关。G须签收实际 launcher/队列/定时定义的精确路径和版本，针对两个外发六文件 source selector 在 **rsync/scp启动之前**设拒绝门，并取消/改版所有未启动旧路径任务。当前 launcher 与队列不能从已有证据完整确认，故该控制点的执行签收为 **HOLD**；不可声称已无计划消费者，也不可擅自停进程。
4. 不删除P2/P3 metadata，不修改历史 `CONSUMED_TRANSFER_HASH_CLOSED`；新增 `SOURCE_SUPPLY_RETIRED` 操作状态，指明未来入口是新的164/109供给任务。`verify()` 对已交付远端包的只读核验可保留，远端现有包、活动109副本及其他模型均不改动。
5. 以后确需提供旧布局时，使用绑定原包身份的新恢复任务；在允许旧任务恢复之前验证原路径恢复正确，不能直接绕过门或改历史包的 source_ref。

## 3. A：监督器与打包器的最小退出

当前 A HEAD `594108601277959fb60c3f475f7890eb8c68f6e7`。两个当前文件摘要仍与8c证据一致：

- `util/vm_tlb/c16/lane_a/c16_background_asset_supervisor.py`：`2edd5beb80f2b743fdc382785811c7f2a1678641604eaf2e6cc5fbaa77c80363`。
- `util/vm_tlb/c16/lane_a/c16_local_prep.py`：`d2f57d5fb80a0251c430b62c2c417972837dcb567a48804cce2de4b4b1ed6f54`。

监督器当前 `observe_once()` 188–192行始终对两个原始模型根执行 `worker_record/file_bytes`；200/202行按immutable receipts生成ready，222/223行仅按marker存在报告ready。只删payload会留下假ready。监督器本身不会启动/停止/重试下载；这个事实不能替代对其他入口的防再下载约束。

具体拟改动：

1. 使用与G同一签收policy。在 `observe_once()` 的 RAW/AWQ 分支前判断两deployment是否 **ACTIVE_RETIRED**。命中时不调用这些路径的 `worker_record`、`file_bytes`，也不重写其READY marker；写清 `SUPPLY_RETIRED_ON_DEMAND`、policy摘要、164权威locator及当前可用性未验证字段。`p2_ready/p3_ready=false` 表示原174当前供给不可用；另列 `historical_immutable_verified=true`，不把历史验证数当在线可读数。历史immutable receipt和ready marker原件保留，其他消费者必须先接受新退休状态，不能仍仅看旧marker。
2. Q30及其他模型的观察、状态写入、限额逻辑保持原有语义；不是停止整个资产管理器。当前60秒循环不会自动重载修改后的Python。A须核对PID/start_ticks和当前源码，发布命名新observer后，在owner批准的切换点仅替换这一observer实例，禁止顺手停止下载器、GPU任务或其他项目。当前阶段不发任何信号、不编辑其状态/配置。
3. 打包器在 `local_asset_files()`、`immutable_checkpoint_receipt()`、`local_row_package_entry()`、`package_local_payload_matches()`、`write_rolling_gpu_package()`、`write_gpu_package()` 的读取/生成入口加明确退休判定；任何命中的旧deployment/source路径在stat、read、hash、复制或重新生成包之前失败关闭。聚合命令须预检整个请求，不得执行一半后才失败。对退休对象返回清晰“须创建164/109新版本供给任务”，不自动下载、不凭历史receipt通过、不静默跳过后称全套READY。
4. 不自动重写旧绝对路径为164，不建symlink，不覆盖历史包/receipt，不引入缺文件自动恢复。A签收实际可能启动 RAW/AWQ 下载/最终化的调用方：原模型退休后这些入口必须拒绝两deployment；未证明入口覆盖前维持HOLD。当前heartbeat的downloader为空也不能证明未来不会启动。
5. 改动发布时保留精确preimage、policy前像和observer身份，仅更新退休控制与新的操作状态。至少验证退休路径零payload/stat访问、旧manifest不能绕过、其他模型分支不变、缺/错policy摘要不放行、READY不能误报、回滚可恢复原观察。只在临时小fixture做控制验证，不以此宣称原生科学正确性。

这里给出的是可评审的具体变更规格，没有在A/G工作树应用补丁。A/G实现需绑定实际新提交和这些验证回执；本请求不能被当作“已实施”证据。

## 4. 164/109 接管与恢复入口

权威根的 locator 是 **164 namespace** 下 `/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/`：RAW为 `qwen2.5-7b-instruct-raw/a09a35458c702b33eeacc393d103063234e8bc28/`，AWQ为 `qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/`。绑定冻结asset-readiness及T的当前内容回执，不能只信同名目录。本原174的同名 `/root/share/mnt164` 解析为本地 `/dev/md127`，不构成native164证明。

T协调快照 `c4f45d997a91056f034aa8568261939ba03f3af5` 仅RAW1–3完整SHA通过；剩RAW4、AWQ1–2共9,127,207,432 B由T独立继续。S不重读前三件、不新启哈希流、不等待T完成才提交owner决定。内容、revision、source identity改变须按T规则重审。T剩余结果不能以旧prefix摘要拼接替代完整SHA。

未来新任务先在164权威版本选择精确manifest，109 owner提供实际本地副本根、同revision及6个SHA、numeric metadata与consumer绑定回执后，在109本地读取；不让GPU直接从SSHFS运行。不猜109路径，不触碰109活动副本。若109没有合格副本，开独立、精确、获许可的供给任务，当前不传输。

需要恢复旧包或旧模型路径时，入口是 **T发布、另获执行许可** 的native两布局恢复程序：分别重建两个selector的原相对布局及各自uid/gid/mode/mtime_ns，逐文件验证6个内容SHA。可以依次恢复两布局以控制峰值，不能用硬链接假装不同mode/mtime同时独立恢复，也不能修改164规范文件属性。恢复目标必须native、可写、独立且有明确预算；当前本请求没有执行该程序的权限。

## 5. 激活、回滚和以后释放的边界

本次若批准owner退役策略与最小控制改动：先由A/G发布精确补丁和签收回执；G清退实际队列，A确认所有当前/计划读取者已经改约，109绑定副本，T完成6/6当前SHA与原生恢复方案。任何未闭合项只暂停对应对象；12文件仍保留。新的供给policy激活之前核对所有门禁，不把“无打开文件”当作计划消费者清退。

源仍在时回滚：记录新旧代码/策略摘要和切换身份，撤销退休policy，回到原observer版本，验证READY来自确实存在且身份正确的原文件；G恢复任务也须重新核对原包identity和consumer，不自动发包。不改变其他模型的历史状态。任一将来源释放后，**先在另获许可下完成原布局恢复并验收，再恢复旧消费者/旧policy**；不允许仅切回READY、自动重下或默默从不同路径供给。

将来unlink必须再有精确的恢复/释放执行批准包：两selector、6个当前内容SHA、两套numeric metadata、A/G生效回执、native恢复实测和执行权限、专门低磁盘操作预算、刚刷新过的真实/计划消费者清退证据，以及source-only逐文件持久 `INTENT/DONE` 日志（写前fsync意图，精确身份复核，unlink后fsync父目录并提交DONE，崩溃逐项核账）。本次批准退役不等于批准unlink或恢复写入。TLS16GiB/P9权限均不得借用，B0010不恢复，B0001–B0009不重传。

## 6. 当前空间与本阶段调查结论

2026-10-19 14:40:24–14:40:54 UTC两次快照原174可用量为41,315,979,264 → **41,291,210,752 B（38.4554 GiB）**，30.049秒下降24,768,512 B（23.6211 MiB）。这与协调交接的4.50GiB不同；本阶段没有释放数据，之前变化来源未确认，不归给S。当前距48GiB底线仍差 **9.5446 GiB**，还未计构建/链接临时峰值和结果预算，因此不是准入。

可见D工作目录进程PID944387/start_ticks917275806记录25,260,032 B写入，Codex公共服务PID375900记录7,819,264 B，DTC受保护监控进程另有小量写入；持续打开FD可确认净分配正增长仅184,320 B。已知C16/DTC两日志与heartbeat该短区间未增长，不能外推其长期停止。deleted-open普通文件去重仅24,576 B，不是GiB级可释放对象，不停止持有者。没有观察到这12文件的持续写FD，不证明没有瞬时/未来消费者。

进程write_bytes包含覆盖/取消写入，不与df净变化相等，D进程瞬时关闭的输出也未捕获。共享底层盘本namespace之外或未观测到的写入仍未闭合；需实际owner/主机管理员用该时间窗、设备与PID证据定位，不能归咎盘点或先前释放失败。当前E只读台账无活动lease/run，实际已用0、上限仍24；协调要求保留真实已用计数改40，S不代改。D/E需识别该写入任务和路径并提供相应许可；不能仅凭cwd称其为正式编译/模拟，亦不作“全部本轮写入已获E许可”的无据声明。F仅在本namespace看到本地checkout，174-new真正执行及host-aware lease由F/E闭合。

旧4.5GiB情景加两套38.747022GiB可见分配上界仅43.248661GiB，仍差4.751339GiB，废弃12.76GiB旧算法。按本次实测情景相加为77.202457GiB，但既未授权释放也非净回收承诺，不能拿该假设放行。第二批三组≥10.431774GiB仍全部HOLD，不重新扫描、不计作可用量。

**待答复的唯一决定：是否批准本请求所列的两deployment原174供给退役策略，并授权实际A/G owner实施上述最小可回滚控制改动（门禁闭合后激活；不含删源、恢复写入、模型传输或TLS恢复）？**
