# C16 Lane C — Stratified Sampling V2 and Qualification

Goal: `C16_C_STRATIFIED_SAMPLING_V2`。

Branch target: `hrl/vm-c16-c-sampling-v2-v0`。

Lane C 不使用 GPU，不启动新 simulator replay。它负责把 C15 被证伪的 phase-level N/n selector 升级为真正的分层采样方法，并按指标给出资格边界。

## 负责阶段

C16-0.8；C16-3.1~3.6；C16-6.1。协作 C16-2.5、4.2、5.5。

## C0 — 本地先完成 Sampling V2 实现

在任何新native结果前完成：
- strata schema；
- certainty-unit规则实现；
- Selector-R probability sampling；
- Selector-M deterministic representative/medoid；
- strata-specific additive estimator；
- ratio numerator/denominator重构；
- sampling-plan hash与freeze机制；
- fixtures与zero-sampling conservation。

不能把candidate mechanism speedup/miss结果作为selector输入。

## C1 — Strata定义

Primary key：
`Phase × Operator × Implementation × ShapeBucket × DType`。

只有数据证明必要时才加：KV representation / quant mode。Layer ID默认作为组内稳定性验证变量，不默认切成每层一个stratum。

UNKNOWN operator/shape/implementation形成显式UNKNOWN stratum，不删除。

## C2 — certainty units

C读取G提交的catalog，按预冻结规则生成：
- 单launch >= phase GPU time 1%；
- special semantics：E/O、KV management、MoE router/dispatch、rare implementation；
- stratum size <=2。

certainty unit只代表自身，weight=1；不得像C15 kernel691那样被N/n放大。

## C3 — 两类selector

### Selector-R

组内概率抽样，用于可解释的总体估计与seed sensitivity。保存 inclusion probability 与seed。

### Selector-M

组内代表点/medoid，用于挑选适合NCU/NVBit的行为代表。其结果可以作为结构代表，但不得伪造设计型置信区间。

二者不能混写成同一个sampling method。

## C4 — estimator

对可加量：

`Y_hat = sum(certainty Y_i) + sum_s (N_s/n_s) * sum(sample_s Y_i)`。

对rate：分别估计numerator/denominator再求比值。

对unique page/line union：不得使用上述可加估计器。若无专门set estimator，只报告sample observed set / stratum footprint distribution，并标 `STRUCTURAL_ONLY`。

## C5 — 预算分配

预算版本12/24/48；单位是每deployment/scenario/phase可选窗口数，certainty units优先计入。

剩余预算依据：
- stratum instance count；
- native duration mass；
- pre-outcome variation proxy；
- 约10% random audit reserve。

同时估算capture cost，不只算kernel数量。

## C6 — 历史回测

用C12/C13 per-kernel历史数据只做 `RETROSPECTIVE_ORACLE_CALIBRATION`：
- 验证zero-sampling守恒；
- 检查certainty unit + strata estimator是否修复C15的大误差；
- operator/layer字段属于historical oracle，不称cheap-native；
- 不因为历史回测漂亮就宣称prospective合格。

所有旧mode=1 C13仍禁止。

## C7 — prospective protocol

Wave-1 native目录出来后，先冻结：
- selector code SHA；
- strata version；
- seed；
- budgets；
- tuning deployments；
- holdout deployments/scenarios；
- metric thresholds。

推荐tuning：Llama、Qwen0.5、Qwen7 raw；holdout至少含Qwen7 AWQ和一个Qwen3/MoE部署。

冻结后才能读取holdout target metric。任何后改selector的结果必须新版本并把旧holdout标seen。

## C8 — 为G/H发布target plan

尽早发布：
- `SAMPLE_PLANS.tsv`
- `CERTAINTY_UNITS.tsv`
- `NVBIT_TARGET_PLAN.tsv`建议输入
- 每个target的reason、semantic key、estimated capture cost。

目标plan固定后，G做第二次运行时必须重新做target identity validation。

## C9 — C16-6.1 qualification

逐指标独立评：
- `QUALIFIED`
- `SCREENING_ONLY`
- `STRUCTURAL_ONLY`
- `NOT_QUALIFIED`
- `UNAVAILABLE`

至少覆盖native duration、可用counter counts/rates、page/line结构指标、机制响应（若没有高保真ground truth则通常NOT_QUALIFIED/UNAVAILABLE）。

5%宏观误差可以作为初始screening目标，但小于几百分点的机制收益需要更严格分辨率；不确定范围跨0必须INCONCLUSIVE。

## C禁止事项

- 不启动新full ROI；
- 不调阈值凑PASS；
- 不挑最好seed；
- 不用medoid结果伪装无偏估计；
- 不把native duration合格扩展为TLB/Cache合格；
- 不把C15历史结果称新blind test。

最终状态：`C16_C_SAMPLING_V2_READY_FOR_REVIEW` 或带明确 `NOT_QUALIFIED` 的partial scientific closeout。