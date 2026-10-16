# EP-L2 English working manuscript EN-v1

2026-10-16. **DOCS_ONLY; not a simulator authorization or a submission-ready result.**

Base: Lane6 Framework `20676888aa9f1d98bb318573a6569f5fe88aa17a`, pack `docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r4`. This is a separate editorial branch; no existing Lane6 pack, source, result, registry, Storage-Ops or DTC-L1 asset is modified.

## Deliverable

`EP_L2_EN_v1.tex` is a standalone IEEEtran conference manuscript, with editable TikZ figures and bibliography embedded. Compile twice with pdflatex. Its first published content blob is `b13131a5b65cf1c2f174f4e9408bdc4d0ec2a503`, independently matched to the local source used for the attached document package. The ChatGPT delivery includes the rendered four-page PDF, equivalent modular LaTeX, a detailed Chinese review and source map. No font files are bundled.

```sh
pdflatex -interaction=nonstopmode -halt-on-error EP_L2_EN_v1.tex
pdflatex -interaction=nonstopmode -halt-on-error EP_L2_EN_v1.tex
```

Required packages: IEEEtran, newtx, amsmath, booktabs, tabularx, TikZ, cite, hyperref and microtype. No custom fonts or simulator components are needed.

## 核心编辑结论

原r4的协议边界和成本账有价值，但逐句英译仍会像内部验收文档。本稿重新组织为：固定分区中的真实WB搬运 → 原位角色转换 → 同payload/bank预算 → copy、容量压力、L2服务和应用cycles分别归因。

标题：**EP-L2: Elastic Payload Storage for In-Place Writeback in GPU L2 Caches**。

正文结构：Introduction；Architecture and Ownership Protocol；Evaluation Methodology and Result Status；Storage Cost and Implementation Requirements；Related Work and Scope；Conclusion。

主要直接修改：

- 用A/B地址和p/q payload解释旧Tag复用与旧数据保留，并新增静态copy/原位WB路径图和三种释放事件图。它们是解释图，不是运行时序测量。
- 1024 resident Tag与1168物理payload不混同；128B共同copy latch不属于可借用池；同bank class限制保留。
- 对一个等价完成WB episode推导3次与1次逻辑bank操作，但不据此填写应用总操作节约或speedup。实际eviction总量可能随模式改变。
- borrow计数不是容量收益，WAD-full不是WBUF data-full；只有真实静态容量压力与有效跨角色分配才能支持容量主张。
- 保留相同binary、完整trace、真实physical bank clock、host预热身份和生产路径验证；不把工具测试/C++源码检查写成应用资格。
- 只在容量主张出现时增加同总项静态重划分，在服务有改善而cycles不变时做有依据的下游四格诊断。
- PPA保留真实数据预算、11-bit索引和参数化gross字段账；generation/pin位宽不是已证明的最小硬件配置，共同项不是新增开销。无mm²/mW/Fmax数字。
- 原1.721259x诊断、shadow WBUF和旧suspended应用数字不进入主文新结果。旧文件均保留。
- TVD/RO保留为扩展说明；短文篇幅取舍不取消任何既定机制或改变实验矩阵。

## 科学结果与Lane6接收

正式接受配对仍为0，主结果表为破折号，含义是未知，不是零效果。作者信息和物理PPA仍待补齐。不得仅删除工作稿提示就提交。

Lane6后续可选择性吸收此文稿到**新revision**，不得覆盖r1–r4。继续使用r4的原生Lane5 V2 API；本稿不引入第二套科学验收逻辑。新结果必须由当前acceptance、完整identity/run-key/proof及动态withdrawal veto接受；launch authorization不是已完成结果。五个预定完整matched pair齐全后才生成组geomean。

官方生产源的精确commit/binary由Lane1发布、Lane5独立资格决定，不由此文稿冻结。此前审查的c9481845/57e1c363源修正不等于已编译或已取得科学资格。第一个合格pair到达后，先用真实copy/staging/bank/lower证据解释，再修改Abstract/Results/Conclusion；不按好看的speedup选负载。

## 来源和借鉴范围

项目主文、PPA与接收协议来自上述Lane6准确commit的 `PAPER_DRAFT_ZH_V4.md`、`PPA_LEDGER.md`、`V2_INTAKE_CONTRACT.md`；研究目标对照 `b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/project_spec/RESEARCH_CHARTER.md` 和用户交接文件。

DTC-L1方面，本次读到 `docs/dtc_l1/iscas2027/manuscript_audit/v05/README.md`（文件blob `35ada0fdeab8c770213e672d814f725dbaf87d97`），该文件说明完整稿/附录在旧对话资料包。当前检索未取得完整DTC稿和LaTeX源码，**不宣称复用了未读取的DTC LaTeX模块**。新模板直接采用会议要求的IEEEtran conference模式。

借鉴DTC审计的三条教训：相同配置不等于实际服务路径相同；ready/borrow/served等观测不等于可执行机会或流量收益；局部前进条件和字段账不能外推为GPU无死锁或物理PPA结果。

公开文献按已核实范围引用：

- V-Way，Qureshi/Thompson/Patt，ISCA2005；作者原文 https://hps.ece.utexas.edu/pub/qureshi_isca05.pdf 。用于既有Tag/Data解耦与本工作的区别；不移植性能结果。
- Accel-Sim，Khairy/Shen/Aamodt/Rogers，ISCA2020；作者原文 https://people.ece.ubc.ca/~aamodt/publications/papers/accelsim.isca2020.pdf 。用于模拟框架和验证组织；不给EP-L2套用外部相关性数字。
- Jouppi victim cache，ISCA1990；出版记录/摘要 https://doi.org/10.1145/325164.325162 。只用背景。
- Gu/Chen，DL-MSHR，ICS2019；作者目录 https://web.engr.oregonstate.edu/~chenliz/publications.html 。题名与研究主题已核实，作者PDF下载超时，未使用未读全文的实现/面积/性能细节。当前相关工作不是穷尽性新颖性证明。

会议格式：https://epapers2.org/iscas2027/ESR/samples.php 明确IEEEtran conference；https://epapers2.org/iscas2027/ESR/authorinfo1.php 规定4页技术内容与可选第5页纯参考文献，当前不是双盲、需作者信息。文稿仍须完成作者信息、科学结果和最终投稿校验。

本分支只交付论文编辑成果，不派发新的Codex Goal，不修改48GiB资源政策或任何删除权限。
