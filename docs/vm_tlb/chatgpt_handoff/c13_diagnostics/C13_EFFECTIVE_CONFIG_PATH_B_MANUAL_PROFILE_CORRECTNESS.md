# C13 effective-config audit — Path B

状态：`CONDITIONAL_PATH_B_ONLY`

仅当 umbrella Goal `C13_EFFECTIVE_CONFIG_AUDIT_GOAL.md` 的 E0 审计已经证明：实际command、config SHA和independent option folding都支持intended geometry，但结果仍然无法满足C12 profile-equivalence时进入本路径。

本路径目标：

> 判断异常来自 MANUAL profile语义、vm_config构造/覆盖顺序、new selective Core的default-off equivalence，还是其他Core/config correctness问题；在根因闭合前不接受H1，并根据影响范围决定H2/H3是否需要quarantine。

## B0. 禁止直接解释性能

进入Path B后：

- Prefill H1 selective旧结果先标`QUARANTINED_PENDING_CORRECTNESS_ROOT_CAUSE`；
- 不把`+143881 cycles`继续用于“selective无效”科学结论；
- 原raw logs保留immutable；
- 不重跑H2/H3，除非证明其MANUAL geometry也受同一correctness问题影响。

## B1. 必做最小C12-binary equivalence control

运行或复用umbrella Goal授权的：

`C13-EQ-P320S10-C12BIN`

配置：

- Prefill
- C12 Core `57bb71...`
- C12 binary SHA `2351f67...`
- FAIR_ARM_MANUAL
- exact320
- standard L2 TLB
- Segment N8
- Lseg10
- no exclusion
- C12 frozen trace/registration/PA

与正式C12 Prefill F7-L10比较。

### B1-A：若C12-binary MANUAL control复现C12 F7-L10

则MANUAL profile本身可视为等价，异常优先归因于**new selective Core empty-exclusion default-off equivalence**。

进入`B2_NEW_BINARY_DEFAULT_OFF`。

### B1-B：若C12-binary MANUAL control不能复现C12 F7-L10

则异常在new binary之前已经存在，说明：

- MANUAL + nominal same geometry并不等价于F7 profile，或
- explicit config并未真正成为controller geometry，或
- `fair_arm`在runtime还有功能语义。

进入`B3_MANUAL_PROFILE_SEMANTICS`。

## B2_NEW_BINARY_DEFAULT_OFF — new Core equivalence审计

前提：B1-A成立。

### B2.1 source-diff审计

C13 selective Core `4f5f2a...`相对C12 Core仅允许range exclusion overlay相关修改。逐行审：

- option registration；
- config object construction；
- segment_config copy/assignment；
- controller constructors；
- service_lookups gating；
- any default initialization；
- exclusion map empty-path behavior。

要求证明：empty exclusion path下所有原C12状态/事件完全不变。

重点检查新增`segment_config`构造参数后所有旧call sites是否仍保持原字段值，尤其任何copy/temporary reconstruction是否意外丢失或重置L2/Segment相关配置。

### B2.2 default-off unit/equivalence test

优先增加轻量、非full-ROI测试：

- same translation_config；
- exclusion empty；
- C12 vs new Core的关键lookup/Segment path结果一致。

如果缺少现有unit harness，可以做最小确定性config/constructor test；不要先用14小时full ROI猜根因。

### B2.3 修复与rebuild

若发现bug：

- 在独立C13 Core branch修复；
- default-off仍为默认；
- full rebuild；
- 记录new binary SHA；
- 先跑Prefill same-new-binary no-exclusion control；
- 该control必须复现`C13-EQ-P320S10-C12BIN`/C12 F7-L10后，才能重跑selective candidate。

如果控制点仍不等价，继续根因审计，不允许为了推进而接受误差。

### B2.4 H1重新评价

control闭合后才重跑/评价Selective：

- exact320 + Segment N8 + L10
- candidate唯一差异=exclusion map

报告same-binary candidate-control差异。

Decode如果旧new-binary control已经证明default-off equivalence，也要在修复binary后决定是否需重新跑；若binary SHA变化且要保留Decode selective结论，则必须candidate/control同新binary成对。

## B3_MANUAL_PROFILE_SEMANTICS — MANUAL与F7不等价审计

前提：B1-B成立。

### B3.1 全仓fair_arm runtime use audit

对C12 Core和C13 Core搜索所有：

- `fair_arm`
- `gpgpu_vm_fair_arm`
- `FAIR_ARM_MANUAL`
- `FAIR_ARM_F7_SEGMENT_EXACT_E320`

建立调用/数据流：

`option parse → shader config → translation_config → configure_fair_arm → validation → controller construction → runtime lookup/fill/PTW/Segment`

明确`fair_arm`是否在configure之后仍影响功能行为。

### B3.2 explicit geometry是否被后续重建/覆盖

重点检查：

- `tlb_config`构造与sets计算；
- controller内部L2实例真正读取哪个config对象；
- option parser重复字段的最终值；
- `configure_fair_arm(MANUAL)`后是否还有default/profile重建；
- runtime/config init是否基于fair_arm另选geometry。

### B3.3 建立effective-geometry receipt

为后续诊断新增一个**只读输出/receipt能力**，优先不改变模拟语义：在启动时记录controller真正构造后的：

- L2 mode/entries/assoc/sets/ports/latency；
- Segment enable/entries/Lseg/map/exclusion；
- fair_arm label；
- PWC；
- page size。

这个receipt必须来自真正controller config，而不是launcher metadata。

如需代码修改，仅限diagnostic print/receipt，default-off且不改变timing。

### B3.4 重新定义C13 diagnostic运行方式

如果证明MANUAL无法保证与F7语义等价：

- 旧C13使用MANUAL且依赖F7-like解释的点全部按影响范围quarantine；
- 不得继续把L8/L9/L11叫“F7 fine latency”或把CAP点当2×2，除非重新建立等价运行机制。

应设计最小C13-only diagnostic profile/override，使：

1. 先完整建立F7 baseline semantics；
2. 再只覆盖diagnostic变量（例如Lseg 8/9/11或exact entries）；
3. effective receipt明确证明最终controller geometry；
4. C13 profile default不会污染C12。

允许新增C13-only diagnostic fair-arm enum或post-profile diagnostic override，但必须：

- 独立Core branch；
- default-off；
- 不改C12 branch；
- 先用L10 exact320 control复现C12 F7-L10。

通过该control后，才决定最小重跑：

- H3：P8/P9/D11；
- H2：B/C中受影响的点；
- H1：new-binary control/candidate。

不要机械重跑全部9点。

## B4. 结果保留/废止规则

- 任何被correctness问题影响的旧结果：保留raw log和SHA，状态改为`QUARANTINED_BY_PROFILE_CORRECTNESS`；
- 不受影响的C13点保留accepted；
- 修复后新结果使用fresh output dirs和新raw SHAs；
- 旧报告通过supplement/superseding表纠正，不静默删除历史。

## B5. 输出

在：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_EFFECTIVE_CONFIG_AUDIT/`

至少生成：

- `PATH_B_ROOT_CAUSE.md`
- `FAIR_ARM_RUNTIME_USE.tsv`
- `CONTROLLER_EFFECTIVE_GEOMETRY.tsv`
- `EQUIVALENCE_CONTROL.tsv`
- `QUARANTINED_ARM_AUDIT.tsv`
- `CORRECTNESS_FIX_AUDIT.md`（若有修复）
- `SUPERSEDING_C13_RESULTS.tsv`（若有重跑）
- `FINAL_REPORT.md`

最终必须对H1/H2/H3逐项给出：

- `ACCEPTED_AFTER_PATH_B_CORRECTION`
- `UNCHANGED_ACCEPTED`
- `QUARANTINED`
- `SUPERSEDED`
- `UNRESOLVED`

成功状态：

`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_B_READY_FOR_REVIEW`

如果证明有真实Core correctness问题但短期无法安全修复，才允许：

`C13_EFFECTIVE_CONFIG_AUDIT_HARD_BLOCKER_WITH_EVIDENCE`

普通代码/构建/launcher/resource问题不是停止条件；Goal应连续推进。