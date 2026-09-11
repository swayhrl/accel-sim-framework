# C13 Path A — mode=1 config-synthesis root-cause scope correction

状态：`PATH_A_ROOT_CAUSE_CONFIRMED_SCOPE_REQUIRES_FULL_C13_SUPERSESSION`

本 addendum 在 Codex live audit 已闭合以下根因后生效，并覆盖 Path A 文档中“如果问题仅影响 Prefill selective pair，则只重跑该 pair”的窄化路径。

## 1. 已闭合根因

C13 config synthesis 使用的 source profile 含：

`-gpgpu_vm_l2_tlb_mode 1`

Core enum 明确：

- `L2_TLB_STANDARD = 0`
- `L2_TLB_SUBENTRY_16 = 1`

正式 C12 F7 之所以仍是 exact320，是因为 `configure_fair_arm(FAIR_ARM_F7_SEGMENT_EXACT_E320)` 在 simulator 内部显式执行：

- `config.l2 = tlb_config(320,16,...)`
- `config.l2_mode = L2_TLB_STANDARD`
- `config.segment.enabled = true`
- `config.segment.entries = 8`

而 C13 diagnostic configs 使用：

`-gpgpu_vm_fair_arm 0` (`FAIR_ARM_MANUAL`)

MANUAL 不会把 inherited `l2_mode=1` 改回 STANDARD。C13 manual override 只改 entries / Segment / Lseg 等字段，却未显式增加：

`-gpgpu_vm_l2_tlb_mode 0`

因此 nominal `exact320` / `exact768` 并不是 exact-page TLB；它们实际运行的是 SUBENTRY_16 mode，entries字段代表group-entry geometry，而不是 intended exact-page geometry。

这解释了：

- Prefill selective no-exclusion control虽然metadata写exact320，却与另一个large-capacity diagnostic表现出异常bit-exact/near-equivalent behavior；
- C13 several translation miss counts远低于真正C12 F7 exact320；
- 问题来自C13 config synthesis / effective geometry，不是range-exclusion Core机制本身。

## 2. 影响范围不得只限于两个 Prefill H1 rows

必须逐项审计所有9个C13新arm的实际effective mode。若其config未在C13 override尾部显式设置`gpgpu_vm_l2_tlb_mode 0`，则该arm的intended exact geometry失败。

已知/高度预期受影响集合：

### H3 fine latency

- `C13-LAT-P8`
- `C13-LAT-P9`
- `C13-LAT-D11`

它们intended为F7-like exact320 + Segment，但MANUAL继承mode=1时实际为subentry-group geometry。原fine-latency结论不得继续accepted。

### H2 capacity factorial

- `C13-CAP-P320`
- `C13-CAP-P768S10`

二者intended分别为exact320/no-Segment和exact768+Segment。若mode=1，则2×2 factorial A/B/C/D不再是所声明的capacity×Segment实验，原interaction和H2结论必须supersede。

### H1 selective

- `C13-SEL-P10-CTRL-NEWBIN`
- `C13-SEL-P10`
- `C13-SEL-D10-CTRL-NEWBIN`
- `C13-SEL-D10`

四者intended为exact320 + Segment N8 + Lseg10；若mode=1，candidate/control pair即使same-binary内部可比，也不是原H1要求的F7-like exact320环境，不能用于原H1结论。

**Decode control偶然复现C12 F7 cycles并不能恢复其scientific validity；geometry错误优先于数值相似。**

## 3. 旧9-arm证据处理

对确认mode=1的原C13 rows：

- raw logs / SHAs永久保留；
- 不覆盖、不删除；
- scientific状态标记为：
  `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16`
- 仍可作为“错误geometry历史证据”，不能继续用于H1/H2/H3结论。

原9/9 terminal/conservation PASS只说明这些错误geometry运行本身完整，不说明它们满足intended experiment contract。

## 4. 修复规则

所有intended exact-page C13 config必须在**最终C13 override段**显式追加：

`-gpgpu_vm_l2_tlb_mode 0`

并新增fail-fast effective-config checker，launch前至少验证：

- fair_arm
- L2 mode
- L2 entries
- assoc
- sets（由mode/entries/assoc一致推导）
- Segment enable/N/Lseg
- exclusion map
- binary/Core
- config SHA

metadata写`exact*`但effective mode!=0时必须拒绝launch。

## 5. 必须先做两个等价控制

在重跑scientific matrix前依次通过：

### EQ1 — C12 binary / MANUAL exact-mode control

`C13-EQ-P320S10-C12BIN-EXACTMODE`

- Prefill
- C12 Core/binary
- MANUAL
- `l2_mode=0`
- exact320
- Segment N8
- Lseg10
- no exclusion

必须与正式C12 Prefill F7-L10高度/严格等价。优先要求：full-ROI cycles、692 per-kernel cycles、关键translation counters、Segment counters闭合一致。

若EQ1不能复现C12 F7-L10，则立即停止Path A replay，转Path B；不得继续批量重跑。

### EQ2 — new selective binary default-off exact-mode control

在EQ1通过后运行：

`C13-EQ-P320S10-NEWBIN-EXACTMODE`

- same corrected exact mode
- new selective Core/binary
- exclusion empty

必须与EQ1/C12 F7-L10等价，证明range-exclusion实现default-off不改变C12 semantics。

若EQ2失败，转Path B `NEW_BINARY_DEFAULT_OFF`，不得跑selective candidate。

## 6. EQ1/EQ2通过后的最小科学重跑

由于config-synthesis bug影响所有intended exact C13 points，EQ1/EQ2通过后，原9个scientific arms原则上全部需要用corrected exact-mode configs获得superseding results：

### H3 corrected

- Prefill L8 exact320 Segment N8
- Prefill L9 exact320 Segment N8
- Decode L11 exact320 Segment N8

### H2 corrected

- Prefill exact320 no Segment
- Prefill exact768 + Segment N8 L10

### H1 corrected same-new-binary pairs

- Prefill control exact320 + Segment N8 L10, exclusion empty
- Prefill selective exact320 + Segment N8 L10, exclude tied E/O range
- Decode control same geometry, exclusion empty
- Decode selective same geometry, exclude tied E/O range

EQ2若与Prefill H1 control完全同一配置/identity，可复用为Prefill control，不需重复run；必须在provenance表显式记录复用关系。

不得因为旧错误geometry结果趋势“看起来合理”而选择性省略某个corrected arm。

## 7. 并发与运行纪律

- 使用fresh output dirs，例如`*-REPAIRED-EXACTMODE-A1`，不得覆盖原9个目录。
- 每arm结束立即terminal/conservation/effective-geometry验证。
- adaptive admission继续有效；按实时CPU/memory/PSI安全扩大并发。
- 不修改正式C12 branch/raw evidence。
- selective Core只保留当前default-off exclusion overlay；除非EQ2失败，不新增其他功能修改。

## 8. 最终报告必须明确supersession

`C13_EFFECTIVE_CONFIG_AUDIT/FINAL_REPORT.md`必须明确：

1. root cause = C13 config synthesis omitted explicit `l2_mode=0` under MANUAL；
2. 原9个C13 scientific rows中哪些实际mode=1；
3. 原C13报告哪些结论被superseded；
4. EQ1/EQ2结果；
5. corrected H1/H2/H3结果；
6. corrected结果与旧错误geometry结果差异；
7. 防回归effective-config gate。

Path A成功状态保持：

`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`
