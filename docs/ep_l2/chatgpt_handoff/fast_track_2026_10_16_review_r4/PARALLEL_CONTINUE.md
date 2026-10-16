# EP-L2 / ISCAS2027 — review_r4 有界并行续行（2026-10-16）

> **增量CONTINUE，不是新Goal，不重启窗口。** 本文件仅协调已经存在的六个Lane与两个Storage-Ops窗口；发布GitHub文本不代表任何服务器进程已启动。执行前每个窗口有界fetch自己分支最新HEAD、STATUS、RECEIPT、共享registry及机器资源，若有较新证据，以新证据为准并记录差异。不得为采用本文件而reset/checkout其他Lane的工作树、覆盖冻结资产或强制push。

## 0. 核查时点、权威及科学边界

- 原合同 Framework `6c136e2a56a008695f8c8b815723bf8f1a760db9`；review_r3 `a41bfb55934303a4d4a342762f74a16d137d0316`。既定WBUF16主配置/WBUF8敏感性、B16_BANKED vs U_WB16同1168 Payload（146KiB/slice）、物理bank每周期最多1op、共同copy latch、RO完整epoch oracle、TVD Tag miss+1cycle及所有OFF默认设置不变。
- 六Lane Framework HEAD（本次只读核对，不是节点实时状态）：Lane1 `c2a536bdc08687260acc10e30e2fb80a6f791c9e`；Lane2 `057633f38fd4440f386283cbd7e1d2b11e4769ef`；Lane3 `c57564272fa340fce5f64b731f4a7fa6f0b4dd0a`；Lane4 `defb595878fb4ebd46fbab1fbe4c9b4a41fa173c`；Lane5 `2fb8a6d1144f6fce038f51e60192f9fa8b0207af`；Lane6 `70675cc3b2cd63e29fc7ab2b0b54dc924011f5e4`。
- Lane1 **未编译的R0.1源候选** Core `62dc1d179b5516e68b21b695c7a9c5d0667e9671`；Core Lane1执行分支 HEAD `c93d900e1f968a3b69990dc29b78d50fc18f35ac`，Lane1回执说明二者tree等价。此候选可供**只读/静态预适配**，但不是有二进制和资格的正式R0.1 release。
- Lane5最新公开 `APPLICATION_ACCEPTANCE.json` / supersession否决全部六条旧R0完成run，旧R0/R1正式科学结果维持SUSPENDED；当前合法R0.1接受配对0，`binary_sha256=null`；旧数据原样保留。以最新Lane5后续GitHub科学权威优先于旧run终态。
- 最近旧174源侧磁盘读数：`/workspace` 40,417,042,432B可用（37.64GiB）；R0.1建造至少48GiB空闲floor加2GiB预计增长空间（合50GiB，按本次快照还缺约12.36GiB）。这不是当前实时测量；禁止降低阈值或用已转存大小冒充回收。

## 1. Storage-Ops：最新V5握手（源、目标仍各自执行）

- **174-new目标侧** Framework `hrl/ops-174new-164-archive-exec-v1` 最新已公开HEAD `0af858b17e357a145e808b894439d2e34237daaf`；`docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261016_storageops_04/STATUS.md` 状态 `BRIDGE_HANDSHAKE_COMPLETE_TARGET_READY_AWAIT_S01_READY`。
- **旧174源侧不是Framework，而是第三仓库** `swayhrl/gpu-l2-cache-verilog` 分支 `hrl/ops-174-source-audit-exec-v1` HEAD `67b625bb43b69f4241fe4770fb58cd3a13c5020f`，最新STATUS仍为 `V5_PROBE_SOURCE_VERIFIED_AWAIT_TARGET_REMOVAL`，即公开源侧尚未报告自己独立的absent确认。**不同发布时间导致状态差异，不应将目标观察伪造为源侧独立PASS。**
- 174-new已经发布 `BOTH_NAMESPACE_PROBE_ABSENCE.json`、`TARGET_RECEIVER_READY.json`，报告创建方已清理8B nonce和READY marker。目标侧观察两个namespace的确切路径不存在；旧174现有源侧窗口必须自己再readback确认同两个路径均消失，并核对目标READY及冻结102文件manifest `d34a952f7dfa5fcd0a2a965fc82623a6ff5fb9666f007b7626269e295a8505d7`。若不一致，按V5停并报告，不猜测。
- 确认后由**唯一旧174源侧窗口**按V5在专用bridge `/root/share/host174_storage_recovery_bridge/20261016_storageops_02` 先stage S01（52个历史可重建`.vvp`，418,020,580B），原子发布批次READY；**174-new原窗口**读该READY、单流限速传164 SSHFS、关闭重开逐项SHA256和DEST_VERIFIED；再由源侧重新检查FD/process/路径/hash/唯一性与真实文件依赖，只有满足V5授权类别的精确`.vvp`可逐项安全释放，记录`df -B1 -P /workspace`净变化。S02（50个`.vvp`，403,579,225B）按相同次序；不要同开两批或重复源拷贝。
- S01+S02逻辑字节总量约0.765GiB，不足以解决约12.36GiB缺口。旧174继续**只读**筛查更大可重建scratch；`/tmp/*.vvp`中尚无逐项输入provenance的814个文件、含脏testbench的历史`.vvp`、旧trace、研究回执、唯一binary继续KEEP，直到逐文件资格证据成立；不得批量删除。
- 36批历史Git临时pack归档约11.563GiB仍保留，原始pack全部SOURCE_KEEP；没有Git对象健康/唯一性完全证明和用户对**精确对象**的单独授权，不执行`git gc/prune`或删除`tmp_pack_*`。旧V4非合规stage不追认为删除许可。
- 直到真正源删除并由Lane5独立在自己容器测得准入空闲，Lane1 build仍是HOLD。

## 2. 六Lane现在可以并行做什么（仅有界轻量工作）

以下为当前可执行准备项；已完成的检查不重复、不借“并行”制造大量日志/编译/仿真。若相关任务正在原窗口运行，合并到其现有计划，不创建第二worker。

| Lane | 立即续行（在旧174资源HOLD期间） | 严格待解锁的重操作 |
|---|---|---|
| **1 公共Core** | 保留Core `62dc1d...` 候选；一次性复核`build_r0_1.py`输入、两修复测试及将发布的新release身份/定向清单，无新全量clean/rebuild和无反复admission轮询。协调Storage-Ops、Lane5，但不接管源删除。 | 只有Live旧174空间满足48GiB floor+2GiB增长、mem≥64GiB、registry/其它进程无冲突时，**本Lane唯一正式构建一次**R0.1，运行生产定向、发布独立Source/Framework/binary SHA与RECEIPT，交Lane5。再考虑独立R1.1。 |
| **2 TVD** | **利用已发布但未编译的`62dc1d...`作精确静态目标**，将已有针对`832d986b...`的TVD预适配delta以独立worktree/patch方式迁到该候选，输出实际冲突、Tag/handle、WAD、WB、dirty-forward与真实bank时钟审计；13个已有静态PASS不重复冒充新runtime。 | 待官方R0.1源/二进制稳定后再以**真实官方父版本**重验最小patch、经安全配额跑必要生产定向，Lane1集成、Lane5独立资格后才正式应用。 |
| **3 RO** | 在同一`62dc1d...`候选上做RO补丁的**只读/静态精确rebase预演**，关注late detached fill、sector/generation、initial host prefill、bank clock、512 descriptor及backpressure；保留5个原oracle证书（FWT空证书为负覆盖），不开新trace生产。 | 等官方R0.1父版本发布后重核delta并做必要编译定向；Lane1独立集成、Lane5独立资格后再运行RO四模式。 |
| **4 Ideal** | 用Lane1当前候选及旧R1.1审计材料完成最小静态repair delta、18格匹配runner/expected mode/identity与非绑定诊断条件复核；禁止把未编译Tag timestamp候选当PASS。 | 仅在Lane1先发布正式R1.1、Lane5独立repair+ideal资格且同一R1.1 binary B16基线存在后，按registry和主线余量滚动18格。 |
| **5 独立资格** | 只读独立审计Lane1准确`62dc1d...`修复增量与两条新生产gate覆盖，检查新run-key/current-acceptance消费者是否已能拒旧六run；准备正式五对的身份/资源准入manifest。已有62测试和撤回审计不重跑无变化内容；不接管Storage-Ops文件删除，不重复构建。 | Lane1发布正式R0.1 binary且Live资源合格后，独立跑physical_bank_clock、memcpy_payload_identity与受影响旧门槛，签当前资格；再按最多2长仿真/8CPU/32GiB保留、48GiB磁盘/64GiB可用RAM、scan独占滚动五B16/U_WB16配对，每个新run-key完整绑定。 |
| **6 论文/PPA** | 继续在r3之上做紧凑四页正文的新revision：突出生命周期解耦与WB共享池机制的因果链，严格区分减少bank copy、容量借用、端到端效果；将可能的等预算静态重划分和同binary ideal对照作为**条件性实验设计**，补真实可审核字段位宽/比较逻辑/关键路径成本与图表占位，不写未验证加速或工艺数字。 | 仅当Lane5发布CURRENT_SCIENTIFIC_ACCEPTED新pair后吸收结果；五对全合格才算组geomean，原r1/r2/r3及撤回附录保留。 |

## 3. 首个正式实验的顺序和停点

1. **资源解锁前**可以六Lane并行做上述低成本工作，但不能并行开始六个C++大构建或六组长仿真。不要让源码预适配压过Storage-Ops的磁盘恢复。
2. **第一个生产门槛**只有Lane1官方R0.1；Lane5独立资格否决权不可被producer PASS、编译成功或旧`COMPLETE_VALID`绕过。
3. **第一组性能**是五开发负载的B16_BANKED vs U_WB16，同生产binary、匹配config/trace、真实bank单周期限额与终态；首个合格pair立即交Lane6。sad保留负控制；btree/dwt2d为holdout，scan单独调度。
4. 若copy减少但容量借用不触发，不能宣称容量共享加速。容量收益被观察到时补同总1168条的静态重划分对照（如1024/112/32），必要时区分copy成本。真实L2服务有变化而应用无变化，才选择一档有证据的下层headroom四格，不做全矩阵。
5. 若任何窗口发现当前HEAD/STATUS/RECEIPT已较上述更新，先做source/config/trace/acceptance差分、保留较新正确成果；不得将本文件静态快照覆盖真实在途活动。

## 4. 工作产物和执行边界

- 六Lane继续原`hrl/ep-l2-ft20261016-laneN-v1`及现有独立worktree，发布各自新revision STATUS/RECEIPT与最小patch、静态审计/真正生产测试范围；只stage自己路径，push后fetch/回读SHA，不force push。
- 旧174源Ops只在`swayhrl/gpu-l2-cache-verilog`自己的既有分支记录源侧独立确认和可能的释放；目标Ops只在Framework既有目标分支记录164 readback；研究Lane不代理删除。
- 无授权不得更改物理容量、bank端口、WAD/TVD、descriptor/oracle/trace、旧R0/R1 immutable资产、存储门槛或科学结果认证。
- 本文的派发只应在**现有Codex窗口**中作为增量消息使用：按当前窗口Lane ID只执行自己段落。普通工程问题自主修复、遇真实科学合同改变/高风险源删除立即停止受影响工作并向用户报告。