# DTC_T1C_HARDWARE_COST_AUDIT_174_V1

已完成有界 CPU-only 来源审查；**当前证据不能给出原32×4 finite OO128的实际总硬件成本，不能确定 T1-C 64×8 的增量面积，也不能支持相同 ASIC 频率。** `T1C_RTL_NOT_AVAILABLE` 限于本包明确列出的已知来源。缺材料的项按 UNAVAILABLE/NOT_QUALIFIED 交付，不以估算或旧 L2 报告顶替。

运行位置为原174（`huangrulin-174`），执行分支 `hrl/iscas2027-dtc-t1c-hw-audit-174-v1`，独立 worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-t1c-hw-audit-174-v1`。先 fetch 并核对 Lane T 远端 `hrl/iscas2027-dtc-tag-pilot-174-v1` 的 HEAD 为 `f520a445436b57c0a0f2494fb858a1636f04d2bc`，完整阅读该锚点的四份指定文档。创建前已核无本 Goal 同名本地/远端分支或 worktree，无需覆盖、reset 或重复启动。最终交付 commit 以 Git branch HEAD 与外置 push/fetch-back 收据为准，避免在提交内容里制造自身 commit 的循环引用。

原32×4 OO目前证明到**软件资源和服务合同**这一步：128 mappings、16KiB coverage、640×128B physical pool、ordinary16KiB、OO PIB128、4 Tag banks、generation/refcount/pending/late-merge/reclaim 的行为来源。没有该 finite L1 RTL、真实宏绑定或实际 DC area/timing 报告。博士论文 §4.5.3 的 OO/IO 面积 +4.7% 是 `MEASURED_HISTORICAL_NOT_MATCHED`，原始 top、commit、工艺/PVT/电压、DC版本/约束及全部 SRAM 的记账未闭合。它不回答当前 A/B 成本。

T1-C 可核的结构差异是 Tag32×4→64×8：增加384 mappings；每 bank 的映射32→128、sets8→16；4-way compare/selection→8-way。物理数据80KiB、ordinary16KiB、shared96KiB（单列）、OO PIB128、4banks以及全局与 finite-service 限制保持模型合同。固定容量不证明宏外围或端口零增量。Lane T packing示例8,864→35,840 bit，增加26,976 bit（3,372 byte），**只属 ESTIMATED_ONLY**，没有混入实测面积表。per-Tag generation 副本、replacement 逻辑与 RMW/仲裁等仍需实现证据；详见 TAG_SCALING_COST.tsv 和 H1_S1_QUALIFICATION.md。

现有可见硬件材料来自已知 `gpu-l2-cache-verilog` 及4个命名 clean clone。v3 top为 `gsgpu_l2cache`，Tag默认256×16、data4×1024slots，L2组织与目标有限 L1 不匹配；DC脚本是占位库路径的 elaboration 模板。现有 R8审计明确无合格 PVT、宏时序和正式 SDC、无真实 ASIC STA。本次没有运行该脚本或任何 open-synthesis/商业 EDA。其 RAM blackbox/行为模型不能按零面积处理，也不能移作当前32×4或64×8的面积/同频结果。范围与逐文件 SHA 见 provenance 和 bounded-search 表。

最需先验证的路径是 bank/set decode、Tag RAM、8-way compare/way-select 到 physical identity/state 与 ref/waiter/LRU update；这只是结构风险推断，没有 STA 路径排名。ready selection、4路 consumer wakeup、collection/refill、一次退休的多引用减计数与最后引用 reclaim 同样缺实际端口和时序证据。模型1410MHz与1cycle假设不能形成 SAME_FREQUENCY_PASS；当前 TOTAL_AREA 和 SAME_FREQUENCY 都为 NOT_QUALIFIED，MEASURED_MATCHED 行数为0。不能据此反向断言设计必然达不到该频率。

|本轮交付核对|结果|
|---|---|
|T文档锚点、Core身份与逐文件SHA|PASS|
|packing分解与固定资源算术|PASS，范围限结构估算|
|32→64 sets 时4bank映射保持|PASS，穷尽模64周期；改变set冲突而不是bank编号|
|当前 A/B 匹配 RTL/宏/DC面积|UNAVAILABLE；B为T1C_RTL_NOT_AVAILABLE|
|完整 SRAM/外围总面积与同频|NOT_QUALIFIED；没有输出任何相应PASS|
|授权边界|CPU-only完成；源文件重哈希未变；无新RTL/EDA/模拟器/GPU工作|

需要补充的首要材料是**真实当前 L1 RTL 路径与 commit/top/参数**、既定技术库/PVT/电压与正式 SDC、DC版本/原始日志报告、SRAM宏端口/时序/面积manifest以及 finite-service RTL验证收据。不存在的路径没有猜测；具体已查目录、缺口和后续最小 Tag-bank配对综合→完整OO集成核对→按需物理实现，见 MISSING_IMPLEMENTATION_EVIDENCE.md。任何新实现/综合都须另行授权，本 Goal 到此停止扩展。

审阅文件：

- [HARDWARE_PROVENANCE.tsv](HARDWARE_PROVENANCE.tsv)：命名来源、commit、source SHA、适用性断点。
- [RTL_VARIANT_CROSSWALK.md](RTL_VARIANT_CROSSWALK.md)：A/B、IO、C+/Base、论文与已知 L2 的身份边界。
- [SRAM_MACRO_INVENTORY.tsv](SRAM_MACRO_INVENTORY.tsv)：结构接口与缺失的真实宏；不伪造面积/延时。
- [AREA_TIMING_COMPARISON.tsv](AREA_TIMING_COMPARISON.tsv)：逐项证据等级、参数/工艺/约束/宏/包含范围；缺项显式 UNAVAILABLE。
- [TAG_SCALING_COST.tsv](TAG_SCALING_COST.tsv)：独立的结构估算和条件，不等同综合结果。
- [H1_S1_QUALIFICATION.md](H1_S1_QUALIFICATION.md)：完整面积/同频与服务路径资格。
- [MISSING_IMPLEMENTATION_EVIDENCE.md](MISSING_IMPLEMENTATION_EVIDENCE.md)：待补材料和需单独授权的最小工作。
- [CPU_AUDIT_RECEIPT.json](CPU_AUDIT_RECEIPT.json)、[BOUNDED_SEARCH_SCOPE.tsv](BOUNDED_SEARCH_SCOPE.tsv)、[FILES_SHA256.tsv](FILES_SHA256.tsv)：核对收据、搜索边界与文件身份。

复核方式（只写本包的表和收据，不执行EDA）：在此 Framework worktree 运行 `python3 docs/dtc_l1/review_packs/DTC_T1C_HW_AUDIT_V1/scripts/audit_cpu.py`。脚本要求列出的外部 source commit 与路径仍可用，否则失败，不自动替换来源。复跑会刷新 UTC 收据及 manifest；原交付身份以 Git commit 和 FILES_SHA256.tsv 为准。论文定位时只对命名PDF第70–86页做了CPU文字提取，外置输出 `/workspace/dtc-t1c-hw-audit-174-v1/thesis_ch4_bounded.txt` 不提交完整论文或原始EDA日志。

未访问 Lane U 的运行状态、raw 或锁；未修改原trace、Core、binary、Lane A或HOLD。此包提交供 ChatGPT 审查，等待下一阶段科学裁决。
