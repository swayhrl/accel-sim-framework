# DTC-MAIN 完整交接：研究资产、科学边界与 Oracle 收尾

版本：`DTC_MAIN_FULL_HANDOFF_20261109_V1`。编制日期：2026-11-09，用户时区 Asia/Shanghai。本文是新窗口接手指南和证据索引，**不是新增模拟、重跑、预算退款或论文改稿授权**。

## 0. 新窗口先读：现在真正剩下什么

本轮 Controlled Oracle 的 **32 个固定程序 × 4 模式 = 128 格**已经全部自然完成，通过运行端 strict、真实164归档及原生恢复。首批32和后续96是独立请求，各自额度已全部消费，remaining 均为0。最后的 GESUMMV/OFF_MATCHED 已于2026-11-07 19:43左右完成结果闭合，不再是长尾。不要再给它估算剩余时间、恢复 owner 或启动模型。

现有旧消费器逐行字段 `independent_review_status=NOT_YET_FINAL_INDEPENDENT_REVIEW` 不会自动感知后来落盘的D终审；它不是否定独审的证据。新正式包应以D回执和128项身份/SHA连接，前向添加终审说明，不改旧snapshot或原RESULT。

本次交接时进一步核实，前一轮两个 Agent 已经完成并冻结产物：

| 产物 | 当前事实 | 原始位置（相对下文 `$DTC_ROOT`） |
|---|---|---|
| 全128项独立终审 | `PASS_COMPLETE_CORE32_128CELL_INDEPENDENT_STRICT_TRUE164_NATIVE_RESTORE`，声明trace范围内无未决 scientific HOLD | `agents/D_CORE32_FINAL_INDEPENDENT_REVIEW_20261109_V1/` |
| 完整32程序机会分析 | 32个四模式共同输入，96个实际 Oracle/OFF 配对，缺失0；报告、逐应用表、kernel案例、来源和缺失计数均已生成 | `agents/M_CORE32_FINAL_OPPORTUNITY_ANALYSIS_20261109_V1/` |
| 已发布运行结果 | GitHub `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`，完整128格快照 | 下文“当前远端结果” |
| Main 最终合并签署 | **尚未完成**：D/M产物还需交叉核对、正式成果包整合与远端回读，不应仅凭模拟结束就宣布整个科研Goal完成 | 本文第14节 |

**接手后的主任务是只读科研收尾和发布，不是继续仿真。** 原先“独审尚未完成”的聊天状态已经被实际落盘的D终审更新；但不能由此跳过主协调者的整合与发布。

应用层旧 Goal 的最近查询仍为 `blocked`，这是此前管理进程事故留下的任务跟踪状态，不能据此推断服务器模型还被卡住。原科学owner PID525725/start1077052887已自然退出。旧request的state文字可能仍是RUNNING；以consumed/remaining/每个execution_receipt及终态证据判断，不为美化状态改历史字段。以本包 `CURRENT_STATE.json`、请求终态、原始结果和独审为准；不通过重启旧进程“修复界面状态”。本窗口没有把整个Goal标记complete。

## 1. 任务身份、论文身份与接手权限

唯一常驻科研角色：**174-new / DTC-MAIN**，研究完整 DTC-L1 微架构、原IO/OO谱系、性能、机制与论文证据。EP-L2是另一条科学线；共享164、工具或原生入口，不代表可以混用科学身份、结果或预算。原IO/OO归属及 Zhao Haoyu 的原始贡献保持原记载。

本轮正式科学Authority：

`18b1ee9d339902e555fc2e04ef51c84f77dfe1b1`

冻结合同目录：

`docs/dtc_l1/review_packs/DTC_WORKLOAD_HEADROOM_OPPORTUNITY_AUDIT_V1/`

必读三件套：

1. `NEXT_ORACLE_EXECUTION_GOAL_PENDING_APPROVAL.md`
2. `ORACLE_CONTROLLED_SCENARIOS.json`
3. `FUTURE_DH_ORACLE_MATRIX.json`

这些文件保留了批准前的 `PENDING`、`current_authorization=CPU_PREPARATION_ONLY` 等原始字段。用户后来已正式批准条件执行，并已实际完成128格；**不要改写这些冻结文件消除旧措辞，也不要仅据其旧字段否认已有合法运行**。实际实施、请求、Gate、strict、归档与D终审是后续事实链。

用户已授权继续完成本轮CPU-only核查、统计、独立复核、科研整合和GitHub审阅包发布，普通工程问题可自行解决。科学身份、输入语义、架构机制、预算或科学范围的新增改变，须另行明确授权。

唯一最后确认论文母稿：**英文 LaTeX v0.23**。本轮不修改、不晋升。其可编辑原包的可靠路径没有在本交接中确认，不能用Git旧v0.18或任何同名旧稿替代。此限制不阻塞只读结果收尾；后续真正改稿时才定位用户确认的原包。

## 2. 一次可用的环境入口

```bash
ssh hrl-174-new
cd /root/workspace
export DTC_ROOT=/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1
export DTC_RUN=/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24
```

`/root/workspace`是宿主入口及共享资产入口，不代表本轮代码、执行、归档都在该目录。`D:/repo`是本窗口Windows辅助脚本/文档副本位置，正式科学资产以174-new和true164为准。

| 用途 | 路径 |
|---|---|
| 本轮统一科研归档根（true164） | `$DTC_ROOT/` |
| Oracle隔离Core工作树 | `$DTC_ROOT/source/integration-core/` |
| Framework工作树 | `$DTC_ROOT/source/framework-build/` |
| 构建产物/回执 | `$DTC_ROOT/build/` |
| 本轮既有Git审阅工作树 | `$DTC_ROOT/review-worktree/` |
| 首批8程序×4模式执行根 | `/root/data/dtc_controlled_oracle_20261106_v1/initial8/` |
| 后续24程序×4模式执行根 | `$DTC_RUN/` |
| 实际冻结binary | `/root/data/dtc_controlled_oracle_20261106_v1/shared/bin/accel-sim.out` |
| 实际冻结libcudart | `/root/data/dtc_controlled_oracle_20261106_v1/shared/lib/libcudart.so` |
| 四模式追加配置 | `/root/data/dtc_controlled_oracle_20261106_v1/shared/configs/` |
| 本轮原始结果的164归档 | `$DTC_ROOT/scientific_execution/{initial8,remaining24}/results/`（以每项receipt为准） |
| 全128格当前派生表/机会分析 | `$DTC_ROOT/control/publication_unified_v3/background_state/derived/` |
| 当前交接包 | `$DTC_ROOT/handoffs/DTC_MAIN_FULL_HANDOFF_20261109_V1/` |
| 原生epoch2入口 | `/root/data/ep_l2_dtc_l1_native_v2/` |
| 原生科学台账 | `/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json` |
| 当前epoch描述 | `/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json` |
| 输入集合/命令列表 | `/root/workspace/assets/traces/bundles/`；具体trace_entry以每项spec为准 |
| 曾接收的V100输入总清单 | `/root/workspace/assets/traces/catalog/DTC_V100_READY_HANDOFF_20261025_V1.json` |
| 旧完整扫描输入binding | `/root/data/dtc_main_v100_sweep_20261025_v1/control/input_bindings/` |

每个执行根内部：`control/specs/`为冻结spec，`control/qualification_ledger/`为INTENT/DONE，`analysis/*.RESULT.json`为逐项结果，`DTC/run/results/<UUID>/`为原始运行产物，`DTC/run/recovery/<txid>/`为原生恢复。不能只看文件名；必须连接request/cohort/UUID/input/config/source与SHA。

true164当前映射为 `admin-wcx@10.208.130.164:/home/shared`，174-new侧挂载 `/root/share/mnt164`。本包中的target_mount_path与true164_root两种路径是同一归档的不同命名空间，不可当作两份独立实验。

## 3. 当前冻结科学身份

| 项目 | 固定值 |
|---|---|
| 原结构基Core | `9eedb3131937748f0492fa83aad37d3691118d70` |
| 隔离Oracle Core | `e6b41ab8992e7d41651501c4d34cfe24195c4f96` |
| Framework | `02775fd795cde5aae1480d81cee6eb481d0a08f4` |
| Oracle binary SHA256 | `3f8e547d87893aaf7319e337883a2bcc1f5717138296e3e6d1425cc75d055283` |
| libcudart SHA256 | `174f53a02223ae69e4a549e60a310f7e69a9334748e719fd48c40640c2a0af43` |
| 固定矩阵SHA256 | `11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee` |
| source/build freeze SHA256 | `b822d1336ed193d9e81b9d388cc5fce0d0e3173308e70880aae7e258daf8c781` |

source/build原始回执：`$DTC_ROOT/control/source_freeze_v1/SOURCE_BUILD_FREEZE.fixed.json`。不要在生产Core或这些已接受身份上改源码/binary/config。

平台是**固定SM70/V100-derived的64SM模型**，10MiB L2、DRAM850MHz；不是商用V100整机实测。DTC冻结Hash、512 logical Tags、640 physical lines、OO PIB128、Ref13及有限服务。精确字节容量、粒度和耦合必须读配置/源码，不从Tag数量自行推导论文口径。原270项非Oracle有效参数保留，新增 `-gpgpu_dtc_oracle_mode` 后有效271项；历史重复打印可能让原始输出行数不同，不靠行数猜身份。

两个一次性请求：

| request | 初始额度 | 已消费/已闭合 | remaining |
|---|---:|---:|---:|
| `DTC_ORACLE_INITIAL8_20261106_V1` | 32 | 32 | 0 |
| `DTC_ORACLE_REMAINING24_20261106_V1` | 96 | 96 | 0 |

首批固定8程序为2DCONV、GEMM、convolutionSeparable、scan、ATAX、MVT、BICG、vectorAdd。后24是同一固定Core32的其余成员，不是根据结果挑选。

完整32输入SHA、128个UUID、原始cycles、spec/config/strict/RESULT SHA与归档/恢复指针见本包 **`FIXED32_INPUT_AND_RESULT_INDEX.json`**。`input_digest`是冻结输入身份摘要，不能自动等同于trace bundle目录名或某一个trace文件的SHA。

## 4. Oracle的实际含义及禁止推断

四模式始终使用同一个Oracle binary：OFF_MATCHED、M_DATAREAD、L2_DATAREAD、L1_DATAREADY。不能用历史9eed/DH-P0替换同build OFF，即使某些cycles恰好相同。

| 模式 | 受控处理边界 | 明确保留的关键部分 |
|---|---|---|
| OFF_MATCHED | 同build实际关闭Oracle的对照 | 冻结DH-P0原机制 |
| M_DATAREAD | 原本地lower-create/inject接受之后，将eligible read下游服务交给有限Oracle返回sequencer | 原issue/coalescing、PIB/Ref、Tag/physical admission、有限注入、返回FIFO、refill/collect/WB/retire；每sector回复与parent/generation守恒 |
| L2_DATAREAD | 正常路由、sector拆分及有限L2 admission后，eligible read用虚拟L2-hit服务 | ICNT、L2命中时序/端口、有限排队/返回、原非eligible流量及本地DTC完成路径 |
| L1_DATAREADY | 原Tag/physical准入及完整指令引用注册后，产生generation绑定的虚拟data-ready事件 | 原512Tag/640physical/PIB128、Tag banks/admission、Ref、有限通知/collect/WB/scoreboard/retire |

eligible仅普通DTC路径的cacheable、非atomic global data load。指令、constant、texture、显式bypass、store/writeback、atomic、fence/barrier及其顺序约束不被悄悄理想化。32B sector/DRAM atom与request object不是同一单位，128B parent不能伪装成单次32B回复。

stock `-gpgpu_perfect_mem=0`、`-l2_ideal=0`；不得用旧stock开关冒充本轮实现。原先审计指出stock perfect_mem包含shader memory interface/response FIFO且可能影响指令路径，l2_ideal旧开关并非合格生效路径。

指标：`S = cycles(同输入同build OFF) / cycles(Oracle)`；`H = 1 - cycles(Oracle)/cycles(OFF)`。各模式在同一固定32上分别计算GM。

这些是**受控反事实**，不是严格数学上界、不是免费硬件、不是DTC实际可实现同等收益。不同模式没有数学嵌套/单调保证；差额不可直接相加分解瓶颈，不能拼每程序最佳模式形成统一GM。`1-1/GM(S)`也不是逐应用H的算术均值。

## 5. 输入人群的完整演进与去重规则

| 人群/矩阵 | 科学含义与边界 |
|---|---|
| 原论文44-row | 原IO/OO论文证据角色，保留原归属与三个历史Hotspot HOLD；不等于后来的44个现代程序名 |
| 后来44程序名、72输入实例 | 同名不同规模/版本/capture仍是独立历史身份；四配置原矩阵288格；不得混入修复验证结果补原accepted |
| 42普通程序目标 | b+tree和hotspot的派生模型输入独立保留，不进普通主统计 |
| 35个已冻结代表输入 | 每程序依源码版本、原命令、输入身份、标准配置、capture范围裁决；不按加速比、耗时或是否PASS选择 |
| 7项UNRESOLVED | backprop、cfd、kmeans、nn、nw、pathfinder、streamcluster；不得替换或强行凑齐42 |
| 固定核心32 | 从35中另保留hybridsort、lavamd、SYRK为原始缺失/补充/暂缓；不是把它们删除或改成性能失败 |
| 本轮Oracle128 | 固定核心32×四模式，与8程序结构探索、35输入原扫描分别统计 |

fraction/trim等部分输入不进入本轮普通完整输入实验，历史仍保留。ATAX普通NO_ARGS对应固定4096²两内核全grid；`1of10/dd8955...`被字节级证明是原kernel body前缀并改grid的派生范围，不是较小完整应用，不用其较好性能替代全输入。它原合同下的strict PASS也不回写成失败。

关键身份裁决：scalarProd13920是13920×1024参数化输入，vectorAdd6000000是6,000,000元素；CFD193K实际有padding后193536 cells，但缺完整time_step/capture合同，仍UNRESOLVED。Rodinia2.0-ft/3.1、随机数据/原始视频、同参数不同capture不能凭名字自动等价。

完整44→42与72→42映射、12项裁决在 `DTC_PAPER42_HASH_REVIEW_20261027_V1/`；输入冻结SHA `a4157b56b48d8d8df048b9f64e62d54b091e80176d7a05169ef9c64b0c06da9d`。164旧审阅ZIP在`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper_suite_dedup_20261027_v1/review_v1.zip`，SHA `fa2cab7f27badc1fea5841fb2d65fd7a0eb11055a336925bb9362df32123a304`。

## 6. 历史阶段与authority地图

以下是资料导航，不是恢复旧实验的命令。历史README可能保留早期pending/31程序文字；必须使用对应冻结终态/独审/最终回读，不把旧段落当最新进度。

| 阶段 | 固定authority/定位 | 核心事实 |
|---|---|---|
| 174-new原生接管 | `4a4931b2ac798c870df5b4661702dfec4900b331`；`docs/ep_l2/operations/174new_direct_native_takeover_20261023_v2/` | epoch1历史保留，epoch2新科学入口；迁移不返还旧额度 |
| AG/BA合并交接 | `564808e166ca4bde2201dec6bc7a4d6e50c47c48`；本包历史两份md副本 | AG8R1 Source实际2/2消费、1 accepted；新174-new GEMM/NN资格是独立新身份，非旧Gaussian修复 |
| AE匹配Hash及72输入扫描 | `DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1`、`DTC_AE_V100_FULL_SWEEP_20261025_V1` | 原CM/CH/DM/DH与修复请求保持分开；旧AD8/AG8R1不可reset |
| 42程序裁决/Hash分析 | `DTC_PAPER42_HASH_REVIEW_20261027_V1` | 原23项四配置交集：Hash前DTC/传统GM1.076346，Hash后1.123867，相对改善1.044150；不得外推42全体 |
| 下游18点 | `DTC_HASH_DOWNSTREAM18_20261027_V1` | ATAX/MVT/BICG×CH/DH×P0/PQ/PS；PQ改partition queue，PS改DRAM1700，仅该旧阶段有效 |
| L2 MLP全35探索Stage I | `361fa6fa0700825bb9cda43e25b9fd1f60e0b262`；`DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1` | 原350：331 accepted、18 archived negative、1 engineering negative；独立命名336视图不可冒充原矩阵 |
| Stage II-A准备 | `5001c3f35052f7f91f1ad41eeff83f2947a0878d` | CH-F128/F256公平匹配合同 |
| 首批16终审 | `5f67b4d6b94568a9f1acc80c3e56736bd81e4753` | 8输入×2 CH配置，独立科学身份 |
| Remaining48完整32观测 | `b665d5ea77b5ae022a86cd03c6c464f5b11cb15e` | 24输入×2新CH；固定核心32六格192个accepted来源槽位 |
| StageII-A最终科学交付 | `60ccf830553425105d6d5a905e392cc403475f65`（已保存最终回读副本） | 比旧31程序README更新；最终48/192、独审与可视化/成本整合归档 |
| Performance-First V1 | 164根`dtc_perf_first_parallel_exploration_20261104_v1/`；`C_final_structure32_v1/FINAL_REVIEW.json` | 8输入×4非Tag结构共32实际模型：28 accepted、4 scan archived negative；另16 Tag安全HOLD未启动 |
| V2 CPU co-design准备 | `320b1365902a72502fa61ba114cb4a4a28b934bb` | Physical768/1024×PIB192的16格；Tag/liveness路线不自动解封 |
| V2布局R1最终16 | `e218746921111d475c6ad8bda8023ad7fe33a33d`；`DTC_PERFORMANCE_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1` | 16/16 accepted；原16启动失败独立保留，不是退款或覆写；8输入GM小幅改善约0.78%/0.84% |
| 机会审定/Oracle未来合同 | `18b1ee9d339902e555fc2e04ef51c84f77dfe1b1` | 先CPU-only审计，再经用户正式批准实际Oracle实现与执行 |
| Oracle全128运行结果 | `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df` | 128 runtime closer accepted，32共同配对，缺失0 |

Stage I扫描固定DRAM850：E384/E768（MSHR192扩容），M8/M16（merge4扩容），Q64/Q128（miss queue32扩容），F128/F256（FR-FCFS64扩容）。基L2：`S:128:128:16,L:B:m:L:L,A:192:4,32:0,32`。F还把shared credits由255改319/447，不能叫孤立L2容量变化。

StageII固定32：P0的CH_cycles/DH_cycles GM约1.100072；F128的S_CH/S_DH分别1.015816/1.012595，I约0.996830；F256分别1.020645/1.019138，I约0.998523。共同系统加速不等于DTC相对优势增加。R定义为CH_cycles/DH_cycles，即DH相对CH性能，不能取反。

V1的四个scan结构负例分别为PHYS768、PHYS1024、PIB192、TAGSVC8；不能拿V2组合或Oracle成功填掉它们。V1均匀四结构比较只有7个共同accepted输入，不能宣称8程序全通过，更不能称完整32结果。V2组合的J必须来自真实同输入接受结果，缺单因素时保持缺失，不乘两个单因素加速比预测正式结果。

`CM/CH/DM/DH`中C/D指传统缓存/DTC，M/H区分原映射与匹配Hash角色，精确算法以原合同/config为准；这个M不是Oracle-M。CH/DH同Hash族不是等面积：L1容量、Tag、PIB、队列、完成服务、时序与物理成本仍不同。

## 7. 历史资料在哪：不要扫描所有RESULT后直接算GM

164共同前缀：`/root/share/mnt164/huangrulin/host174_storage_recovery/`。

| 阶段 | 164目录/重点文件 |
|---|---|
| 72输入与修复资料 | `ep_l2_full_workload_performance_20261027_v1/`、`dtc_completed_restore_cold_tier_20261026_v1/`、原生`/root/data/dtc_main_v100_sweep_20261025_v1/` |
| 纸面候选与Hash | `dtc_paper_suite_dedup_20261027_v1/`、`dtc_paper42_hash_review_20261027_v1/` |
| 原PQ/PS18点 | `dtc_hash_downstream18_20261027_v1/`；原生同名目录 |
| Stage I | `dtc_l2_mlp_full_workload_exploration_v1/`；原生`/root/data/dtc_l2_mlp_exploration_20261027_v1/` |
| Stage II-A | `dtc_stage_iia_preparation_20261103_v1/`、`dtc_stage_iia_first16_execution_20261104_v1/`、`dtc_stage_iia_remaining48_execution_20261104_v1/` |
| StageII最终包索引 | `dtc_stage_iia_remaining48_execution_20261104_v1/root_final_completion_20261105_v1/FINAL_PUBLICATION_READBACK.fixed.json` |
| V1结构探索 | `dtc_perf_first_parallel_exploration_20261104_v1/`；重点`C_final_structure32_v1/`、`root_full32_direction_review_v1/`、`final_analysis_v1/` |
| V2 | `dtc_perf_first_v2_cpu_preparation_20261105_v1/`、`dtc_perf_first_v2_codesign16_execution_20261105_v1/`、`dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1/` |
| Oracle前机会审定 | `dtc_workload_headroom_opportunity_audit_20261106_v1/` |
| 当前Oracle | `$DTC_ROOT/` |

Native Stage I `analysis/`同时存在原始、额外身份与引用RESULT。全目录glob得到的数量不一定是350；不能将334、365之类目录文件统计写成原350结果。严格按冻结MATRIX/request/cohort/UUID/source role选择，独立R2/IR/EP/PQPS只保留其原角色。

原AA/AB/AC/AD/AE/AF/AG、X/Y/Z、SG、AG7分支是机制/负例/观测库，按历史合并交接的原commit索引读取，不重建常驻Lane、不盲合所有代码。本包保留两份原始交接全文；其旧预算0、旧PID绑定和“尚未启动”只描述当时时点。

## 8. 当前32程序结果与科学发现

| Oracle | 固定N | GM S | 正/零/负 | 缺失 |
|---|---:|---:|---:|---:|
| M_DATAREAD | 32 | 1.6767585258096842 | 32/0/0 | 0 |
| L2_DATAREAD | 32 | 1.2806486845080634 | 19/11/2 | 0 |
| L1_DATAREADY | 32 | 1.9399115770053144 | 32/0/0 | 0 |

初始8的GM分别3.4463/2.1034/5.1061，不能替代完整32的GM。其余24的GM分别约1.3188/1.0854/1.4050，说明必须保持预冻结人群，而非用少数强例作全套宣传。

最强例GESUMMV：OFF89,502,220 cycles，M8,699,612，L221,659,576，L12,496,495（约10.288×/4.132×/35.851×）。MVT/ATAX/BICG的L1约20.230×/18.593×/16.723×。vectorAdd、scan也有显著Oracle响应；不能因此推导一种可实现结构必有等量收益。

L2两个负例保留整数精度：myocyte145,147,976→145,147,978，慢2 cycles；srad_v1 7,324,411→7,339,063，慢14,652 cycles。myocyte5993个kernel中只有一个L2慢2 cycles，不可舍入成零；srad_v1有274个L2 kernel负例。11个精确零以及bfs/mri-q/myocyte的近零响应限制泛化范围。

3MM/GEMM的L2精确无响应，M还比L1更快；fastWalshTransform、scalarProd、heartwall也有M比L1快的例子。不要强制Oracle单调、剪裁S<1、只留有利程序或把不同模式差额相加。

完整逐应用/逐kernel/suite结果在M报告及本包证据副本。本文末尾附32程序简表，机器索引保留完整SHA和128个源结果连接。

## 9. 独立终审究竟核了什么

D文件：`agents/D_CORE32_FINAL_INDEPENDENT_REVIEW_20261109_V1/REVIEW.fixed.json`，SHA：

`a48369fe99fba2cbd35815a522f94285ade9022de37e6d7d4ed469f28b8b8f08`

D MF：`fd0f3b0b1c450dd19bddeb81a732be7b0fcd320719d1553f519f0f58e7b3ea63`。

独立重读5572个文件、约2.748GB唯一源字节，重新解析约3.373GB解压raw；逐项检查128 UUID/input/source/config/binary、270参数公平性、全部kernel顺序/工作量、cycle合计、自然终态/资源轨迹、true164分块与整流SHA、source与native restore完整typed trees（各2821 entries）、SHA/权限/owner/symlink。没有将运行端PASS标签当成独立验收。

边界：完整trace-body SHA/capture provenance引用既有回执；本次新核commandlist SHA及完整成员size/mtime/readability，不宣称重认证捕获二进制、原始输入内容或native全应用数值。D不自行Git/网络核远端，远端读取由Main在交接时另核。

审计中曾有90个已知稀疏打印字段解析KeyError与一个保守resume断言；它们是**审计器工程中间态**，已经保留中间文件，后续用精确冻结稀疏适配器重新核查。它们不是90个模型失败，也不能据此重跑任何模型。

M文件：`agents/M_CORE32_FINAL_OPPORTUNITY_ANALYSIS_20261109_V1/REPORT.zh.md`，SHA `7b0c7473a38acfd2eb7176e813628df4c7185bb5a73041b9ab68010b43c5668d`；MF `dc1747e37027ad8aeec5d1729978f65a7a7e89bb9ac488a83ccfbfa64dc32dda`。M重放qualified analyzer并核与现有机会分析一致，复用kernel缓存、未重新读raw；此证据等级与D的独立重解析不同，不能互相冒充。

## 10. 必须继续披露的真实性/数值/计数器边界

- 当前是已声明完整trace范围的性能结果，不是全部原应用数值认证。capture-time ELF、真实数据内容、原应用修改版/宏及source绑定仍有限制。
- 当前显式prefill=1、flushL1=1、flushL2=0、OO source-event invalidate=0。HtoD命令顺序和sidecar通过，不证明真实hook时序/重叠、数值freshness或跨kernel coherence。
- myocyte5993 kernel的13×461只属算术兼容，不是已证明的求解步/重试次数；3MM候选源码未初始化数组等线索不能直接判历史捕获数值错误，也不能偷偷修trace。
- 32B L2 sector、32B DRAM atom、request object和128B line不能混单位。打印均值/积分/峰值/gauge/cumulative各按原口径，不能随意作差。
- 缺失计数是UNKNOWN/null；只有冻结且源码证明的稀疏零派生可单独标注。全128共29192条kernel事实，部分延迟计数明确null；不补0。
- Physical占用可能含Ref-free retained cache，不等于活跃压力；ready/collect均值不是关键路径比例；零DRAM不证明compute-bound；跨warp全局issue order未证明相同。
- CH/DH不等面积，PPA/面积差额仍UNKNOWN；不从RSS、队列条目或Oracle直接得等面积结论。

## 11. 安全HOLD与负例库不得删除

两种Tag扩容（64×16、128×8，均1024 logical Tags、physical640）已构造可达无前进状态：640条真实lifecycle后，合法零Ref Tag仍可占住物理行，641次新请求持续NO_FREE_LINE。16格全部安全HOLD、未启动，不是性能负例。用户接受HOLD，暂不要求修复/替换，Oracle成功不解封它。

另有**自动处理未消费CPU绑定/清暂停的行政辅助器HOLD**：外部快照到撤暂停之间无法证明与owner错误写入方原子握手，可能掩盖新工程暂停。源/15个CPU例子保留但未部署。原先经主协调者现场屏障、未消费/无INTENT/claim/running复查而做的有限手工保全，不等于放行无人值守自动修改。

历史AG8R1 failed/held、三个Hotspot HOLD、StageI原负例、V1四个scan负例、V2原16启动失败、L2两个真实回退都独立保留。不能用本轮128成功改写它们。

## 12. 已解决的运行事故：只读参考，不要再执行

旧owner1498278/start977758783与辅助调试进程438646/start1072993843曾卡在管理端。一次性exec尝试未获得可验证新镜像ACK，旧ONCE/错误journal保留，**不改称成功**。后续普通OS管理清理辅助进程后，两者终结；未使用第二次exec、调试器注入来恢复。停止的调试/注入路线不要再试，私有环境和原始exec payload不进交接/Git。

随后合法串行新owner525725/start1077052887实际取得四把原锁和新私有lease，单独注册96；同PID不是用户科学合同的硬要求。旧32结果/request/lease/journal/875f CPU草稿保持原样，不把历史执行帧伪装成新owner上下文。

新入口首先因把未加锁open FD当竞争owner而HOLD，0模型/0UUID；独立forward guard改为区分passive FD与真实FLOCK，原4inode EX、PID/start、source、lease、祖先门仍保留。历史1112475只持被动FD，未被停掉。

新96登记误保留CPU草稿state，原生prepare拒绝。Main经已审纯CAS标准API只把该request.state置ARMED，保全精确ZERO_START暂停，未改额度/UUID/参数；同owner自然继续。后续未消费CPU旧binding冲突导致队首阻塞，Main仅在标准暂停跨周期ACK、目标无消费/INTENT/claim/running后保全旧binding，并撤自己的精确暂停；不动健康模型。全128已终结，现在没有任何理由重复这些操作。

## 13. 自动发布和Git纪律

当前只读发布器启动记录：`$DTC_ROOT/control/publication_unified_v3/ACTUAL_BACKGROUND_PUBLICATION_PROCESS.fixed.json`。原PID660465/start1079949574是历史标识，管理前重核，不能仅凭PID存在就判同进程。

源：`agents/M_unified_publication_proposal_v3_branch_guard_forward_v1/unified_watch_publish_v3.py`，SHA `677d5730fad6bd7bfebe2f7ace7985cb02da287d959d0f6dcbf1f8e47ac0b823`。D源审：`agents/D_independent_review_v1/unified_publication_native_index_transaction_source_review_v3/SOURCE_REVIEW.fixed.json`，SHA `1f1534bec0fb5dfe83c8a8237472b79b5d268195adbe964403f095484ed16b02`。

实际私有index：`/root/data/dtc_oracle_publication_v3/unified_main/CLEAN_UNIFIED_BACKGROUND_INDEX`。Git对象/原审阅工作树在true164，小型index改native；原SSHFS index曾超时留下0字节锁。所有隔离均先标准STOP服务、实际无Git writer/FD证明后保前像rename，不凭锁年龄删除。V3同PUBLOCK下双扫描、校验inode/内容稳定，只处理自己index；先核真实分支，再核HEAD/REMOTE/LATEST/manifest，只前向采用真实已提交对象，不reset/recommit；歧义HOLD。

1800秒是有变化结果的发布节流；无新闭合数据只COLLECT_ONLY，不用空提交制造“进展”。V3不启动模型、不写科学registry。管理只读发布服务不等于管理科学owner。

现有审阅W：`$DTC_ROOT/review-worktree`，分支 `DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1`。`.git`实际指向：

`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/planning-isolated.git/worktrees/review-worktree1`

**该旧工作树default index曾有大量预存staged deletions，绝不能用默认index add/commit/reset清理。** 不用`git add .`/`-A`/force-push；显式路径、独立index、`git diff --check`、source保前像，push后ls-remote/fetch/show精确SHA与manifest回读。

同一旧发布工作树的任何Git写者共用：`$DTC_ROOT/control/publication_v1/LOCK`（真实EX flock）。如果新窗口选择沿用旧发布工作树进行操作，须明确接手并遵守同锁；优先遵守仓库规则建立**新窗口独立branch/worktree**，不和既有只读发布器竞争。新worktree可采用no-checkout/稀疏文档检出，避免在只余有限空间的native盘展开大量旧资产。不要删除或重置任何旧工作树。

仓库AGENTS.md有针对旧`hrl/decoupled-l1-exp-m5-v0`的M5阅读/执行序列；当前不是该分支，不能把旧M5.0B等文字当成恢复旧Goal授权。通用Git/证据/归属规则仍遵守；本次用户冻结的Oracle合同和交接范围优先。

资源规则：实际核host/cgroup、CPU/NUMA、MemAvailable、IO、native与true164；历史4GiB预测/16GiB硬上限只属于特定旧合同，不套到新任务。用户认可native5GiB安全底线，不无依据预留几十GiB；有真实source/write/restore预留则单独计。已接受Oracle保持SOURCE_KEEP，不能以早期“可迁移资产”泛授权删除冻结源或他人数据。当前没有新增模拟任务，CPU空闲也不是扩科学范围的理由。

## 14. 新窗口必须完成的明确待办（无需新增模拟授权）

1. 完整读本文、`CURRENT_STATE.json`、`EVIDENCE_INDEX.json`、三件套合同，核本包MANIFEST。查询当前native请求终态/实际进程；128已结束，拒绝“修owner/补跑缺点”的误操作。
2. 核D终审状态与scope，验证D MF；对照M MF、QA、32应用表和128结果索引。保持D重新读raw/归档与M使用缓存的不同证据等级。审计中间解析错误只保留，不重做模型。
3. 主协调者交叉核查完整32模式GM、每suite分布、两L2负例、零/近零响应、kernel工作量与计数器单位。不要沿用8程序GM替代32或混入历史C1/P0。
4. 整合正式 **CORE32 Oracle 最终科学审阅包**：完整运行/配对表、方法与counterfactual边界、逐应用与kernel案例、硬件成本UNKNOWN、数值/capture边界、独审全文及精确来源。可用已有数据绘制科学图，不启动新观测插桩或仿真。
5. 给出下一阶段DTC结构优先级与待批准实验合同：有限完成/通知/collect/WB与下游服务协同，PIB/并发/physical生命周期，再评估安全Tag映射等。区分E1本轮Oracle观察、E2历史真实结构响应、E3待验机制假设；最多3–5条高价值建议，不许Oracle加速直接许诺为硬件收益。
6. 将正式包发布到独立GitHub审阅分支/目录，按同一SHA核所有成员、Git blob及远端回读。原D/M冻结字节直接引用或副本保持SHA，不改成另一份“原始结果”。
7. 正式包、独审、结论与限制都完成并可复现后，才报告本科研Goal完成；在下一科学授权边界停下。原native请求预算不重置。应用层跟踪状态另行如实处理，不能用状态操作产生科学额度。

尚未授权：CH Oracle、新输入/补齐7项身份、补充/暂缓CH、1024Tag HOLD恢复、Tag512独立实验、跨组回收、额外数值验证、组合搜索、新capture、109 GPU任务、新架构或DRAM/容量/clock变化。普通已授权CPU-only解析/路径/Git/报告工程问题自行解决，无需重复让用户逐项批准。旧窗口/子Agent的会话内存不能跨窗当证据，若需并行自行创建临时CPU-only审阅Agent并使用冻结文件。

## 15. 解释与后续研究优先级（给下一步计划使用）

已有观察优先指向GESUMMV/MVT/ATAX/BICG的访存服务与完成路径机会，以及vectorAdd/scan的控制条件；不能因小总体GM忽略清楚的访存正例，也不能删掉bfs/mri-q/myocyte等近零例。

有限通知/收集/写回、PIB/Ref完成效率值得核查；ready-to-collect样本均值提示机会，不证明关键路径占比或PIB饱和。真实结构V2约0.8%改善与Oracle1.94×相距很大；要设计可实现、有限资源、无liveness破坏的机制，而非把Oraclesequencer或虚拟驻留当免费硬件。

保持Tag安全HOLD。可先在独立CPU-only源码/fixture形成liveness论证和下一阶段候选，不改生产Core或宣布新模型资格。既有Core、binary、input、接受结果与历史negative/HOLD必须留存。

## 16. 本交接包文件与验证

| 文件 | 作用 |
|---|---|
| `HANDOFF.md` | 本完整交接正文 |
| `NEW_WINDOW_MESSAGE.txt` | 可直接粘贴给新窗口的启动消息 |
| `CURRENT_STATE.json` | 交接时实际状态、请求/预算、独审状态、路径与边界 |
| `FIXED32_INPUT_AND_RESULT_INDEX.json` | 32完整输入SHA与128 UUID/cycles/config/RESULT/strict/archive/restore索引 |
| `EVIDENCE_INDEX.json` | 每个证据副本的原绝对路径、SHA、角色与是否可变 |
| `evidence/final_review/` | D终审关键冻结产物副本；其大审计中间表/完整SHA读账仍在原164目录 |
| `evidence/final_analysis/` | M正式分析关键产物副本；完整kernel案例/qualified分析在原目录 |
| `evidence/oracle_authority/` | 原18b三件套冻结副本，旧pending字样不被改写 |
| `evidence/history/` | 原AG/BA合并交接全文、StageII最终回读、V1最终审计及人群缺失边界 |
| `evidence/current/` | source/build、native终态、原32前像、当前派生表快照与发布状态 |
| `MANIFEST.json` | 本包相对路径、字节数与SHA，验证新窗口读取的确是这次冻结包 |

本包不是多TB raw/trace/binary/build的另一份副本；大资产保留原位置和SOURCE_KEEP，通过索引访问。可变的live结果表/发布状态被复制成不可变snapshot；以后其时间戳更新不能误判为原始结果被改。原始result_sha/UUID/input/config身份才用于跨快照核对。

仓库远端：`swayhrl/accel-sim-framework`。当前结果快照固定位置：

`7ffcca7f908a21f45ba1a6ebb3b335ff962f97df:docs/dtc_l1/review_packs/DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1/live_results/20261107T114450Z_aa9bcfc6413509cd/`

该快照MF SHA：`ac01186af49dcbf5c6e38055ca53a8cddc925b1e454136f607d08eb621b5f54a`。本交接包自己的新提交SHA/回读记录另行提供，不能自引用假定它等于旧128格提交。

## 17. 固定32程序便查表

下表由已核对的M应用矩阵生成；SHA前缀仅便查，完整SHA、原始cycles及128身份必须用机器索引。所有S均为同build实际OFF/对应模式，非历史CH或混合P0。

<!-- GENERATED_FIXED32_TABLE -->

| Suite | 程序 | input_digest前16位 | OFF cycles | M S | L2 S | L1 S |
|---|---|---|---:|---:|---:|---:|
| CUDA Samples | BlackScholes | `b31a85e4eb8d32ef` | 8971 | 1.096833354 | 1.000000000 | 1.107804396 |
| CUDA Samples | convolutionSeparable | `4114a3dc0d06b55b` | 800572 | 2.490270001 | 2.198709181 | 2.496645970 |
| CUDA Samples | fastWalshTransform | `f7f22a2ccc836a8a` | 185317 | 1.241513529 | 1.013819061 | 1.240018200 |
| CUDA Samples | histogram | `3722a5c85d91a948` | 98202 | 1.336554427 | 1.000000000 | 1.453122226 |
| CUDA Samples | mergeSort | `dd9f695c4f53b083` | 111917 | 1.116913834 | 1.000000000 | 1.138942034 |
| CUDA Samples | scalarProd | `2b93f70cd0666c51` | 411009 | 1.833576466 | 1.481967982 | 1.826089854 |
| CUDA Samples | scan | `6df3a84b612086e8` | 6648993 | 3.180808258 | 3.071965570 | 3.204178014 |
| CUDA Samples | transpose | `65151d2c661f88f3` | 237820 | 1.246318481 | 1.000000000 | 1.248064823 |
| CUDA Samples | vectorAdd | `e7bb67e63e3c3847` | 217305 | 3.778691660 | 2.388518229 | 4.053214705 |
| Parboil | bfs | `1df9d5479504d9c7` | 4170294 | 1.000633690 | 1.000001199 | 1.000762157 |
| Parboil | cutcp | `af7320f9d9dc6629` | 4490473 | 1.023377963 | 1.000000000 | 1.023419712 |
| Parboil | histo | `2c506bf13c81ff5d` | 5865589 | 1.511480558 | 1.109387063 | 1.520072925 |
| Parboil | mri-q | `dc7a91531846c113` | 360174 | 1.004128879 | 1.001924992 | 1.004257668 |
| Parboil | sad | `db89be14146b9163` | 114870 | 1.135550327 | 1.004099615 | 1.137856230 |
| Parboil | sgemm | `ffc8a89493c8a211` | 409417 | 1.073168494 | 1.006373764 | 1.079484063 |
| Parboil | stencil | `c885293ad99e21ee` | 4662889 | 2.577719855 | 1.000944083 | 2.589712659 |
| PolyBench/GPU | 2DCONV | `d984ea5475a581ad` | 462740 | 2.034862756 | 1.192751830 | 2.035158088 |
| PolyBench/GPU | 3DCONV | `79f8ab6241faeed6` | 2200332 | 1.294156120 | 1.005851343 | 1.321602478 |
| PolyBench/GPU | 3MM | `977a2f7007cb1f96` | 2402871 | 1.152961538 | 1.000000000 | 1.079704730 |
| PolyBench/GPU | ATAX | `eededb785179fc04` | 31880220 | 6.556675155 | 2.741552971 | 18.593125956 |
| PolyBench/GPU | BICG | `ae34174fbbdf83b2` | 28685812 | 5.900413871 | 2.551461799 | 16.723076376 |
| PolyBench/GPU | GEMM | `fc0705ae3721e999` | 826089 | 1.183715492 | 1.000000000 | 1.113219472 |
| PolyBench/GPU | GESUMMV | `769e6d9fd5f9cd53` | 89502220 | 10.288070319 | 4.132224010 | 35.851151314 |
| PolyBench/GPU | MVT | `f437190767aaed49` | 34687540 | 7.134045239 | 2.846955561 | 20.230406200 |
| Rodinia | dwt2d | `e5638b94095098ac` | 73071 | 1.045978328 | 1.000000000 | 1.047147504 |
| Rodinia | gaussian | `16f4c42373e4961e` | 740717 | 1.034396707 | 1.000000000 | 1.040157558 |
| Rodinia | heartwall | `731af5428c4b8155` | 8551 | 1.125872284 | 1.009801606 | 1.124244018 |
| Rodinia | lud | `b33381cf25d44359` | 478654 | 1.071128228 | 1.000000000 | 1.074123194 |
| Rodinia | myocyte | `977e34578994c3d2` | 145147976 | 1.000037908 | 0.999999986 | 1.000037908 |
| Rodinia | particlefilter_float | `b41cc74c66ca6ed4` | 2100874 | 1.130127974 | 1.010604528 | 1.286565515 |
| Rodinia | particlefilter_naive | `3f85d1878aba9f04` | 384601 | 1.280419881 | 1.000000000 | 1.289534213 |
| Rodinia | srad_v1 | `0e62c67daa020853` | 7324411 | 1.165292307 | 0.998003560 | 1.217253618 |
