# 给 DTC-L1-11 的完整审查交接

## 任务与当前决定边界

请在本目录的**固定 GitHub 提交**中审查 DTC-MAIN CORE32 Oracle 的最终科学审阅包，并对本轮受控 trace 性能结论、证据链、限制、正式总签署及下一阶段结构方向作科学审阅。当前任务是**审查与反馈**；本文件及 `NEXT_STRUCTURE_DRAFT.md` 不授权新模拟、新 request、新预算、GPU 采集、源码变更或解除 HOLD。DTC-MAIN 本轮 CPU-only 收尾已经 STOP。

固定交接基线 commit 为 `3f0036f2868e20a8d9a4b6244c7c74d940954188`；原 128 格运行结果已发布 commit 为 `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`。本目录是独立分支 `dtc/core32-oracle-main-closeout-20261109-v1` 的正式包，所有成员按 `MANIFEST.json` 固定字节 SHA。请按审查时给定的**完整 commit SHA**引用本包，不把可移动分支 HEAD 当永久证据。

## 建议阅读顺序及审查对象

1. `REPORT.zh.md`：Main 最终科学判断、方法、GM/分布、负例、真实性与数值限制。
2. `FINAL_SIGNOFF.md`、`MANIFEST.json`、`GITHUB_READBACK_PRE_SIGNOFF.json`：本轮范围、停止点、包成员来源与前次 GitHub 回读；最终提交的回读回执由接班端另存本机，审查时可按固定提交和 manifest 自行复核。
3. `evidence/D/REVIEW.fixed.json`、`evidence/D/REVIEW.md`、`evidence/D/VERIFIED128_ROWS.json`、`evidence/D/FIXED32_MATCHED_PAIRS.json`、`evidence/D/CYCLE_ACCOUNTING128.json`：128 格 D 独立终审、96 配对与周期口径。D 的最终状态为 `PASS_COMPLETE_CORE32_128CELL_INDEPENDENT_STRICT_TRUE164_NATIVE_RESTORE`。
4. `evidence/M/REPORT.zh.md`、`evidence/M/APPLICATION_OPPORTUNITY_MATRIX.csv`、`evidence/M/KERNEL_CASES.json`、`evidence/M/INPUT_PROVENANCE.json`、`evidence/M/CELL_EVIDENCE_REFERENCES.json`、`evidence/M/COUNTER_MISSINGNESS.json`：完整 32 程序机会分析、必要 kernel 案例、来源及缺失值。M 复用合格分析器和缓存，没有声称第二份 D 级 raw 审计。
5. `analysis/MAIN_CROSSCHECK.json`、`analysis/DTC_CORE32_REVIEW.csv`、`evidence/fixed/FIXED32_INPUT_AND_RESULT_INDEX.json`：Main 逐格连接、复算回执、逐程序排序及固定输入/结果身份。
6. `NODE_RELATIONSHIP.md`、`NEXT_STRUCTURE_DRAFT.md`：174-new/164/109 的资产关系，以及 E1/E2/E3 分层的结构方向与待授权最小实验合同草案。

原 128 格发布包位于 `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df:docs/dtc_l1/review_packs/DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1/live_results/20261107T114450Z_aa9bcfc6413509cd/`；完整交接依据位于 `3f0036f2868e20a8d9a4b6244c7c74d940954188:docs/dtc_l1/handoffs/DTC_MAIN_FULL_HANDOFF_20261109_V1/`。本目录是审阅所需的冻结小型证据包，不替代 164 的完整 raw、Trace、Source 与 native restore。

## 请核实的科学结论

固定 32 程序 × OFF/M/L2/L1 四模式，共 128 个自然闭合结果；M、L2、L1 各有 32 个同一 build OFF 配对，共 96 配对。相同输入、相同 Oracle build、相同非 Oracle 选项；历史 9eed DH-P0 不是分母。Main 对 128/128 身份和周期、96/96 配对、128 项 kernel 周期合计、各 suite/initial8/remaining24/全集 GM 与符号分布复算一致。全部结果包含 29,192 条 kernel 事实。GM 的定义是同集合 `exp(mean(log(C_OFF/C_mode)))`，不是逐程序节省率的均值。

| 集合 | M GM，正/零/负 | L2 GM，正/零/负 | L1 GM，正/零/负 |
|---|---|---|---|
| CORE32 全 32 | 1.676758525810，32/0/0 | 1.280648684508，19/11/2 | 1.939911577005，32/0/0 |
| initial8 | 3.446285317826，8/0/0 | 2.103432830864，7/1/0 | 5.106115891060，8/0/0 |
| remaining24 | 1.318793975160，24/0/0 | 1.085418270304，12/10/2 | 1.405008733853，24/0/0 |

特别审查 L2 的 **11 个精确零**和 **2 个回退**是否完整保留：`myocyte` 的 L2 比 OFF 慢 2 周期，`srad_v1` 慢 14,652 周期。`bfs` 快 5 周期、`mri-q` 快 692 周期，按精确整数周期为正，不能因展示精度舍入为零。`myocyte` 有 5,993 个 matched kernel、`srad_v1` 有 502 个，内部正/零/负混合；应用汇总不等于所有 kernel 单向变化。GESUMMV、MVT、ATAX、BICG 的强响应，3MM/GEMM 的 L2 精确零与 M/L1 响应，以及 M 比 L1 更快的程序，都需在解释中保留。initial8 的高响应不得代替 CORE32 全集。

请特别核查来源和真实性表述：D 独审重新读取大规模 raw、true164 源与 native typed restore，验证固定输入、结果、配置公平性、kernel 序列/周期及自然终态；M 是冻结产物的机会分析，Main 是来源连接与交叉复算。D 工程中间失败记录继续保留，其后精确适配得到最终 PASS；M 快照中的 `NOT_YET_FINAL_INDEPENDENT_REVIEW` 是先于 D 终回执的静态字段。旧应用 Goal `blocked` 与 registry `RUNNING` 也不是模型未终结的证据，不应通过重启旧 owner、改 registry 或补跑模型“修复”。

计数器审查需保留 UNKNOWN：29,192 条 kernel 事实中，`averagemflatency`、`avg_icnt2mem_latency`、`avg_icnt2sh_latency` 各有 100 个显式 null，`avg_mrq_latency` 有 21,156 个显式 null。未打印也为 UNKNOWN；只有有冻结源码证明的稀疏零可另列派生值。32B L2 sector、32B DRAM atom、request object、128B line 不是同一单位；平均、峰值、瞬时 gauge、积分和累计不能任意相减。ready/collect 均值不是关键路径占比，零 DRAM 不证明 compute-bound。

## 结论的适用范围与反证

可接受的结论仅限 **SM70/V100-derived 64SM 固定 trace 的受控 Oracle 性能反事实**：有限资格域的 data-availability 干预可以产生不同强度和符号的响应，因此值得设计有限结构候选再验证。不能把 Oracle GM 说成可实现硬件的收益、CH/DH 的等面积收益或严格数学上界。当前证据不自动认证 capture 时 ELF/输入数据内容、原生完整应用数值、真实 hook 重叠、跨 kernel coherence、面积/功耗/有限吞吐或机制因果。

历史真实结构结果属于另一 Core/binary/config 身份，只作为 E2 背景：GESUMMV DH-P0/F128/F256 为 89,502,220/86,464,623/90,151,547 周期；vectorAdd 为 217,305/213,053/236,217 周期。F128 的正响应与 F256 的回退并存，不能用容量扩张必然获益解释。V2 Physical×PIB 已接受 16 点在 fixed8 的 GM 变化约 0.78%/0.84%，不能外推到全 32 或替代 Oracle。1024Tag/physical640 的合法 `NO_FREE_LINE` 无前进问题仍在安全 HOLD，本包 PASS 不解封。

## 结构方向与待审实验合同

请按 `NEXT_STRUCTURE_DRAFT.md` 分别判断三个方向的**价值、主要反证与优先级**：

1. **有限下游服务与本地完成协同**：E1 为强 Oracle 响应及控制程序；E2 为 F128 正响应、F256 回退；E3 为保留 sector 回复、有限注入/返回队列、generation/Ref 守恒及有限 notify/collect/WB 时能否实际改善服务的假设。
2. **PIB/Ref 与 physical 生命周期**：E1 为 L1 虚拟 data-ready 下的响应及 L2 零对照；E2 为历史小幅且有正负的结构变化；E3 为 admission、完整引用注册与有限 completion 耦合的机制假设。physical 占用不能直接当活跃压力。
3. **Tag 映射与前进性先验安全**：Oracle 未消除 Tag/PIB 压力；已有 1024Tag 候选触发 `NO_FREE_LINE` 安全 HOLD。先要隔离 CPU fixture 与源码级前进性证明、独立安全复核，再谈模型候选；本次不得解除 HOLD。

第一方向的**待批准**最小合同是先给出具体有限硬件状态/容量/时序、成本估计和 failure handling；CPU fixture 覆盖部分 mask、32/64/128B、重复/迟到回复、generation、Ref/credit 守恒、背压、公平性及终态 drain。若未来另获用户明确科学授权，再预登记 10 输入：GESUMMV、MVT、ATAX、BICG、vectorAdd、scan、3MM、GEMM、myocyte、srad_v1；一个冻结候选 binary 下每输入同 build OFF 与候选，合计 **20 个新科学格**。其余 22 输入/44 格只有首批终态、安全、数值范围和成本复核通过、且用户另行批准后才考虑。旧 Oracle OFF、历史 DH-P0、旧 UUID/预算均不能复用。方向 2/3 若执行须各自单独合同与预算。

## 请给出的审查回执

请明确给出：

1. 对“固定 trace 范围内 D/M/Main 科学收尾”是**接受、要求限定措辞、还是退回补证**；逐项指出需要修改的固定文件与证据行/字段。
2. 128/96 身份、GM 和分布、L2 零/近零/两回退、kernel 案例、计数器 UNKNOWN、真实性限制及历史 E2 隔离是否表达充分；若否，写出最小补核，不重开 128 格审计。
3. 对三项 E3 结构方向的价值排序、关键反证、首选候选的最小安全与成本准入要求，以及是否需要改写 10 输入/20 格草案。审查意见不等于科学执行授权。
4. 是否接受本轮总签署与 STOP 边界。真正未决项须标为后续独立资格：原生数值/capture 绑定、有限机制因果、CH/DH 面积/功耗/吞吐与扩展输入证据。

任何建议都应保持英文 LaTeX v0.23、原结果、负例、失败、Source、HOLD、只读 publisher 与其他项目服务原样。本轮新增科学模拟、request、预算消费和 GPU 采集均为 **0**。下一科学授权前 STOP。
