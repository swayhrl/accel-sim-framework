# EP-L2 EN-v5 — manuscript review and editorial revision

2026-10-17. DOCS_ONLY. This directory does not authorize a simulator run, alter scientific acceptance, or modify any Lane's source or frozen evidence.

## Manuscript and build

`EP_L2_EN_v5.tex` is a standalone IEEEtran conference manuscript with editable TikZ diagrams and the existing ten-item bibliography embedded. Compile twice with `pdflatex -interaction=nonstopmode -halt-on-error EP_L2_EN_v5.tex`. Its first publication is `442085c565213688387275e2c4ab2c207281f018`; remote blob `74517dc552e49dc02ac45fb934c616630e0abb2f` matches the local source used to build the delivered PDF. Source SHA256: `1d6d3d78713b7611ac67ed10a745b9b17dab33a933ef8aab676930a08405298e`.

The ChatGPT delivery includes the PDF, equivalent modular LaTeX, bundled pre-generated bibliography, build script, detailed Chinese review, source map, and PDF checks. No font files are bundled. The layout remains four technical pages plus a reference-only fifth page; experimental panels are placeholders, not data. The PDF is a working manuscript, not submission-ready.

## Exact review basis

- Full EN-v4 source: Lane6 `113eb6accb520db409b40193fba901089a723d20`, `docs/ep_l2/review_packs/FT20261017_LANE6_R14_REVIEW_r1/EP_L2_EN_v4.tex`; blob `00d505b6860b51f79e0f3b4423aecbfefc57739a`.
- EN-v4 figure/cost/evidence review: same pack, especially `PPA_REVIEW.md` and existing result-intake boundaries.
- Official producer: Core `088146f7f85b4073deb5d166a0a4484c7f3b48b2`, Framework `861a06b91e309832161eab0836b512853c833ffb`; published pack `9898c56d7a010c934de327784076ba0b9a36c9c4`.
- Latest read Lane5 status records independent 21/21 at `2026-10-17T03:23:14.493753+00:00`; branch readback `877c9759f61494e5061dbc92f2cc5d36a0760ff9`. The multiway replacement gate, complete eleven-gate certificate and formal applications remain pending. These are editorial snapshots, not runtime authorization.
- Configuration checked directly: Core `configs/tested-cfgs/SM7_QV100/gpgpusim.config`; Framework `gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config` and `tests/ep_l2/b0_banked_d512_850.config` at the producing commits above.
- Bibliographic metadata and comparison scope are inherited from EN-v2/EN-v4's ten-item audit. No new paper or claim of a repeated full literature audit is added here.

## 审稿结论

当前论文的机制中心成立：dirty payload原位转为WB ownership，Tag、数据和WAD分别退休。但证明链未闭合：正式应用结果为0，公共跨周期替换正确性仍需验证，静态bypass预留可能造成基线闲置容量，动态共享与静态重划分的区别未被实验分离，新增控制成本缺物理证据。这不证明机制无效，也不能靠英文润色补成实验结论。

| 问题 | EN-v5实际修改 | 仍需真实证据 |
|---|---|---|
| EN-v4写本轮生产测试未运行，已过期 | 更新producer21与independent21通过，但完整独立资格仍开放 | r15多way跨周期回归、11gate及应用接受 |
| 概念copy代价被隐含外推为工作负载瓶颈 | 引言限定所研究reference，拆开copy、quota和端到端问题 | 五对的WB/copy/pressure/cycles，不用旧撤回数字 |
| 全部三角色共享的图示超过当前主线 | 图1改为resident/WB owners；说明动态bypass并发未建立 | 真正bypass共存路径如需主张则独立验证 |
| B16固定split可能留下闲置bypass空间 | 正文要求WB-heavy等总容量static对照；不宣称优于所有static方案 | 新static quota接口和独立资格；一个1024/112/32点也不是最优性证明 |
| Fig4的WBUF8/静态对照可互相替代的暗示 | Fig4优先固定总容量static；WBUF8仅是另一1160预算敏感性 | 两者各自合法的结果输入 |
| 设计义务被写成已证明实现 | 增加跨周期事务身份、完整rollback和稳定retry条件 | 真实old-red/new-green；不删除assert、不免费加port |
| 统计口径混合logical/physical/attempt/retention | Fig2保留copy/send/WB总量；Fig3区分Tag-visible、landing、pool和WAD | 细粒度物理拆分需要额外审计映射，不将缺项填0 |
| 同data/Bank预算被读成同PPA | 单独列control/hit latency、generation/pin/queue、下层carrier成本 | 同工艺RTL/宏/STA/活动模型；当前无mm²/mW/Fmax |
| 系统配置缺计算规模与L2时钟/延迟 | 从实际配置补80SM、1132MHz core/ICNT/L2、850MHz DRAM及ROP160设置 | 最终仍绑定准确ordered config，不把ROP160称实测纯hit latency |
| 五workload名被当作完整输入与普遍覆盖 | 要求绑定完整input规模/commandlist，sad只称预定negative control | 完整五对与原holdout；不能择优子集均值 |
| 多机制分散主命题 | TVD/RO压缩为独立候选，主线OFF；Ideal只为诊断 | 有增量收益和成本再决定本次正文深度 |
| 主文重复内部审计语言 | 保留原六节，压缩重复禁令与免责声明，集中结果状态 | 实测段到达后替换计划文字，不继续叠加篇幅 |

## Strong-control reasoning boundary

The detailed review notes an additional **inference**, not an implemented experiment: when bypass activity is absent, an equal-1168-slot split such as 1024 resident / 0 bypass / 144 WB is a useful WB-heavy static-control candidate. Its WB data quota exceeds the 128-entry WAD limit, but that alone predicts neither bank behavior nor IPC. No such configuration is authorized or added to the current campaign. The manuscript retains the already proposed 1024/112/32 example while explicitly stating that it is unimplemented and not proof of the best static split.

## Figure and result intake

Fig1 stays a conceptual architecture/protocol diagram. Fig2 reserves two 40mm panels for matched performance and measured copy/WB work. Fig3 reserves three 43mm panels for capacity/order, bank service and downstream effects. Fig4 reserves 32mm for an equal-capacity static control; WBUF8 is not its substitute. No fabricated values, axes, means, bars or favorable results appear.

Lane6 may absorb the edits into a new revision, preserving old packs. Continue using its native Lane5 V2 intake, exact identity/proof and withdrawal checks. The manuscript adds no second acceptance implementation. A newly passed producer or independent directed replay is not an application pair. Only actual CURRENT_ACCEPTED pairs may populate the figures; five complete pairs are required for the declared group geomean. PPA remains source-level until physical evidence exists.

The most useful next inputs are the current correctness closure, the first accepted pair with valid copy/capacity/service metrics, the remaining four pairs, and evidence on whether static repartition removes the observed capacity problem. This editorial work does not issue new Codex Goals or change the running repair plan.
