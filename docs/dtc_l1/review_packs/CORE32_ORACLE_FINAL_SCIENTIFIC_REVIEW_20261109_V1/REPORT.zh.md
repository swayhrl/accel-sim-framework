# DTC CORE32 Controlled Oracle：Main 最终科学审阅

## 结论与适用范围

固定 32 程序、四模式共 128 个自然闭合结果，在声明的 **SM70/V100-derived 64SM trace 性能范围**内完成 strict、true164 归档、native typed restore，D 独立终审为 `PASS_COMPLETE_CORE32_128CELL_INDEPENDENT_STRICT_TRUE164_NATIVE_RESTORE`。M 的完整机会分析覆盖 32 个共同输入和 96 个同版本 OFF/Oracle 配对。Main 以固定交接包、D/M 冻结产物、运行结果逐项连接并复算，得到 128/128 身份、周期及 kernel 汇总一致、96/96 配对一致、全部 suite/阶段/全集 GM 与符号分布一致。该范围没有待补模型格或未决科学 HOLD。

本结论是 **受控反事实性能结论**。它既不证明原生完整应用数值正确，也不证明可实现 DTC 结构能取得同量收益、等面积收益或严格数学上界。论文英文 LaTeX v0.23 未改。原历史失败、负例与 HOLD 保留。

## 固定身份与来源

| 项目 | 身份 |
|---|---|
| 当前科研合同 authority | `18b1ee9d339902e555fc2e04ef51c84f77dfe1b1` |
| 原结构基 Core | `9eedb3131937748f0492fa83aad37d3691118d70` |
| Oracle 隔离 Core / Framework | `e6b41ab8992e7d41651501c4d34cfe24195c4f96` / `02775fd795cde5aae1480d81cee6eb481d0a08f4` |
| 实际 binary / libcudart SHA256 | `3f8e547d87893aaf7319e337883a2bcc1f5717138296e3e6d1425cc75d055283` / `174f53a02223ae69e4a549e60a310f7e69a9334748e719fd48c40640c2a0af43` |
| 固定矩阵 SHA256 | `11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee` |
| 已发布 128 结果 | commit `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`，`docs/dtc_l1/review_packs/DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1/live_results/20261107T114450Z_aa9bcfc6413509cd/` |
| 完整交接和 D/M 冻结证据 | commit `3f0036f2868e20a8d9a4b6244c7c74d940954188`，`docs/dtc_l1/handoffs/DTC_MAIN_FULL_HANDOFF_20261109_V1/` |

四种模式使用**同一个** Oracle build、同一固定输入及非 Oracle 选项，OFF 是每输入同 build 的实际运行；历史 9eed DH-P0 不是分母。`S = C_OFF/C_mode`，`H = (C_OFF-C_mode)/C_OFF`，每模式 GM 为同一 32 个输入上 `exp(mean(log S))`。整数周期和精确分数判断正、零、负；`1-1/GM(S)` 不等于逐程序 H 算术均值。模式移除不同阶段且保留各自有限服务，不具已证明的单调或可加关系。

合格域仅是普通 DTC 路径上 cacheable、非 atomic global data load。M 在 lower-create/inject 接纳后替换下游 read 服务，保留有限回复；L2 在正常路由与有限 L2 admission 后虚拟命中；L1 在真实 Tag/physical 准入与完整引用注册后虚拟 data-ready。指令、constant、texture、bypass、store、atomic、fence 等不顺带理想化。L1 仍保留 512 logical Tag、640 physical、PIB128、Ref13 与有限完成服务。

## Main 统计交叉核对

| 人群 | N | M GM / 正零负 | L2 GM / 正零负 | L1 GM / 正零负 |
|---|---:|---|---|---|
| CORE32 | 32 | 1.676758525810 / 32-0-0 | 1.280648684508 / 19-11-2 | 1.939911577005 / 32-0-0 |
| CUDA Samples | 9 | 1.730326206175 / 9-0-0 | 1.425064964511 / 5-4-0 | 1.767089720629 / 9-0-0 |
| Parboil | 7 | 1.254218832335 / 7-0-0 | 1.016872243319 / 6-1-0 | 1.257538669189 / 7-0-0 |
| PolyBench/GPU | 8 | 3.170315498503 / 8-0-0 | 1.775432921118 / 6-2-0 | 5.405615309351 / 8-0-0 |
| Rodinia | 8 | 1.103593091151 / 8-0-0 | 1.002290635336 / 2-4-2 | 1.129888264569 / 8-0-0 |
| 预冻结 initial8 | 8 | 3.446285317826 / 8-0-0 | 2.103432830864 / 7-1-0 | 5.106115891060 / 8-0-0 |
| 其余 remaining24 | 24 | 1.318793975160 / 24-0-0 | 1.085418270304 / 12-10-2 | 1.405008733853 / 24-0-0 |

initial8 的高响应不能代替 CORE32。完整整数周期、精确比值、排名和结果 SHA 见 `evidence/M/APPLICATION_OPPORTUNITY_MATRIX.csv`、`evidence/fixed/FIXED32_INPUT_AND_RESULT_INDEX.json`、`evidence/D/FIXED32_MATCHED_PAIRS.json` 及 `analysis/DTC_CORE32_REVIEW.csv`。`analysis/MAIN_CROSSCHECK.json` 给出 Main 可复算的每集合统计及连接回执；源代码 `main_crosscheck.py` 在本机 DTC-L1 工作区 deliveries，未读取大 raw。

**强响应与控制**：GESUMMV 的 OFF/M/L2/L1 周期分别为 89,502,220 / 8,699,612 / 21,659,576 / 2,496,495，即约 10.288× / 4.132× / 35.851×；MVT、ATAX、BICG 的 L1 分别约 20.230×、18.593×、16.723×。vectorAdd 与 scan 亦有三模式响应。这些说明受控 data-availability 干预可改变性能，未定位唯一关键路径。3MM、GEMM 的 L2 都**精确零**，但 M/L1 有响应；3MM、GEMM、fastWalshTransform、heartwall、scalarProd 中 M 比 L1 更快，myocyte 两者相等。

**L2 的 11 个精确零**：3MM、BlackScholes、GEMM、cutcp、dwt2d、gaussian、histogram、lud、mergeSort、particlefilter_naive、transpose。bfs 的 L2 仅比 OFF 少 **5 周期**，`S=4170294/4170289>1`；mri-q L2 少 692 周期，`S=360174/359482>1`，都不能因显示精度舍入为零。

**两个有效回退**：myocyte `145147976/145147978 = 0.9999999862209585`，慢 **2 周期**；srad_v1 `7324411/7339063 = 0.9980035598549842`，慢 **14,652 周期**。二者在完整 32 的 GM 中保留。`myocyte` 共 5993 个 matched kernel，L2 为 0 快、5992 相等、1 慢；`srad_v1` 共 502 个，L2 为 215 快、13 相等、274 慢。`stencil` 整应用 L2 略快（1.000944×），其 100 个 kernel 内仍有 46 个变慢。案例见 `evidence/M/KERNEL_CASES.json`，不是只用应用汇总遮盖内部分布。

## 证据连接、证据等级与计数器口径

本包直接字节保留 D 的 `REVIEW.fixed.json`/`REVIEW.md`、128 行审查结果及 96 个 matched pairs，M 的正式报告、32 程序表、12 个 kernel 案例、128 个证据引用、input provenance 与缺失计数。各副本 SHA 在 `MANIFEST.json`；源路径及原始身份见固定交接 `EVIDENCE_INDEX.json`。D 的最终状态须以独立回执为准；M 冻结分析里的 `NOT_YET_FINAL_INDEPENDENT_REVIEW` 是早于 D 回执的静态字段，不回写旧快照。

D 独审重新读 5572 个文件、约 2.748 GB 唯一源字节并重新解析约 3.373 GB raw，逐项审 128 UUID、输入、源/配置/binary、270 个非 Oracle 选项公平性、kernel 序列与周期、自然终态、true164 chunk/whole stream、source 与 native restore typed tree（各 2821 entries）。D 的初次 90 个稀疏字段解析 KeyError 及后续一次保守断言错误是**审计器中间工程记录**；精确适配后终审 PASS，模型结果未被更改。完整 trace-body SHA 与 capture provenance 引用已有回执，D 没有新认证 capture ELF/原始数据内容。M 复用 qualified analyzer 与 kernel cache，581 个唯一 pin、360 个 source-derived 零证明引用通过产物 QA；它没有重新读 raw，不能当成第二份 D 级独立 raw 审计。Main 连接了 42 个交接成员、128 个 fixed/D/M/发布行及 128 个 kernel 周期合计，未重做整轮审计。

全部 128 格共 **29192** 条 kernel 事实。显式 null：`averagemflatency`、`avg_icnt2mem_latency`、`avg_icnt2sh_latency` 各 100 条，`avg_mrq_latency` 21156 条。未打印键也保持 UNKNOWN；仅冻结且有源码证明的稀疏零可另行标为派生值。32B L2 sector、32B DRAM atom、request object 与 128B line 不能混作同一单位；打印均值、积分、峰值、瞬时 gauge 与累计值不能任意相减。ready/collect 均值不是关键路径占比，physical 占用可能含 Ref-free retained cache，零 DRAM 不证明 compute-bound，也未证明跨 warp 全局 issue order 完全相同。

## 真实性、结构成本与历史背景

当前 prefill=1、flushL1=1、flushL2=0、OO source-event invalidate=0；HtoD 命令顺序和 sidecar/strict 支持固定 trace 范围，却不证明 capture 时 ELF/数据内容、真实 hook 重叠、跨 kernel coherence 或原生完整应用数值。myocyte 的 5993 个 kernel 不能被命名为已验证的求解步数。CH/DH 面积、PPA 及等面积收益 UNKNOWN；不能从 RSS 或 Oracle 直接推定。历史 C1 真实结构实验属于其他 Core/binary/配置身份，只作为 E2 背景，不填 Oracle OFF、不混入本批 GM。

历史 GESUMMV DH-P0/F128/F256 周期为 89,502,220 / 86,464,623 / 90,151,547；vectorAdd 为 217,305 / 213,053 / 236,217。有限 F128 的正响应与 F256 回退并存，明显小于 Oracle 情景，说明不能把容量扩张许诺为同量收益。V2 fixed8 的 16 个已接受结构点仅给出约 0.78%/0.84% 的小幅 GM 变化，不能代替完整32。1024 Tag 两个候选 16 格保持安全 HOLD：真实生命周期下第 641 次新请求可能持续 `NO_FREE_LINE`；本轮 Oracle PASS 不解封它。

## Main 判断和停止点

在冻结 trace 性能范围，D 独审、M 完整分析、Main 交叉核对与正式包整合已经闭合。后续结构方向和待批准最小实验合同草案见 `NEXT_STRUCTURE_DRAFT.md`，其中 E1/E2/E3 分开标注，**没有取得科学启动授权**。真正未决的是原生完整应用数值/capture 绑定、成本与等面积公平性、结构机制因果及未来输入覆盖；这些不影响本次受控 Oracle 收尾，但限制外推。两个 request 均已消费完且 remaining=0，旧 `RUNNING`/应用层 `blocked` 只是历史静态状态；不为界面美观改 registry、重启 owner、重置预算或补跑。当前只读 publisher 原位保留。下一科学执行授权前 STOP。

本轮正式总签署及 GitHub 发布前回读见 [`FINAL_SIGNOFF.md`](FINAL_SIGNOFF.md) 和 [`GITHUB_READBACK_PRE_SIGNOFF.json`](GITHUB_READBACK_PRE_SIGNOFF.json)。

供 DTC-L1-11 使用的完整审查交接见 [`DTC_L1_11_REVIEW_BRIEF.md`](DTC_L1_11_REVIEW_BRIEF.md)。
