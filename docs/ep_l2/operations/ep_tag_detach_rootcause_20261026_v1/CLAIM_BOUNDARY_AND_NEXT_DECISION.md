# Claim 边界与下一决策

Goal：EP_L2_TAG_DETACH_CAUSAL_ROOTCAUSE_V1。决定：**维持现有 T；不安排新的完整应用，不修改机制。** 本审查没有消耗epoch2预算，没有恢复旧Goal/controller，没有修改accepted simulator或EP-MAIN科学资产。

## 可使用的陈述

|级别|陈述|适用域|
|---|---|---|
|PROVEN|三个接受r5点的实际生产FT/RO调用域没有raw TagFAIL、relieve或detach；covered新Tag目标set最多3/16 RESERVED|CFD E056、DWT E057、native Vector的精确input/config/source/binary|
|PROVEN|构造真实16-way pending压力时，有限CPU fixture可以触发detach、保留旧payload、隔离旧返回与新Tag、最终退休|具体历史fixture与receipts，不是任意协议交错|
|PROVEN|SGEMM E051 positive certificate被识别，可见RO head全部resident hit，RO transaction0|r4单端，原FAILED后同raw离线补充接受|
|PROVEN|nonRO Frontend preview rawFAIL拒绝，不到commit relieve|源码与NATIVE_REQUESTER有限反例；不是三r5零值直接根因|
|PROVEN|Vector有newTag/reuse/eligible实际联合，但没有rawFAIL与reuse联合|covered head-cycle域；skip维度仍NA|
|LIKELY|现有T是触发条件窄的条件性机制；当前数据没有支持改保护条件的必要性|有限代码与测试证据，不能称形式化正确性证明|
|UNKNOWN|全部输入/skip域是否无压力；放松reuse是否安全；开放nonRO是否有净收益；T单独端到端收益|未测试或分母为0|
|HYPOTHESIS|真实同set突发和长pending窗口可能触发；部分曾merge事务或许可另行证明detach|没有本轮真实窗口、补丁或安全证明|

建议论文候选措辞：

> T在定向CPU测试中具有条件性功能证据。三个已接受r5应用诊断在精确生产及covered域未出现真实Tag分配失败或detach，因此目前没有真实应用上T独立性能收益的证据。

不要写成：T改善了原MAIN整体S/F；RO admission/eligible代表detach；full occupancy代表TagFAIL；Vector静态结构数与newTag边际相乘就是可救机会；TVDskip=0压力；单次detach就是关键路径收益；旧r4/main61与r5可以拼出控制配对。原母稿EN-v22实物未提供，本轮未编辑论文、未采用候选EN-v24或编造表号映射。

## 下一项工作的顺序

1. 采用本报告收紧T收益声明，保留负结果与NA；无需新的模拟预算。
2. 只有已有证据识别到真实 `newTag∧rawFAIL∧sameSetEligible` 窗口且可改变判断，才准备一项最小真实验证的精确spec。当前没有这样的窗口，因此**不提名或预定Conv r5**。
3. 若研究资源另获授权，W/V的同背景独立因果控制与端到端吞吐证据优先于为非零detach进行扫描。该建议不是运行授权。
4. 真正识别T收益需要同一精确binary的T-ON/OFF控制，背景W/V/M、input、config与结束条件匹配，记录接受/拒绝、关键等待、cycles及drain。不能从原MAIN S/F拆出T贡献。

## 未执行的策略补丁设计轮廓

状态：**DESIGN_ONLY / NOT_EXECUTED / NEEDS_INDEPENDENT_AUTHORIZATION**。没有改源码，也没有将诊断自动合并。

|候选|最小设计范围|先决条件|当前决定|
|---|---|---|---|
|nonRO requester可达性|若设计明确要求全requester relief，仅让native preview在rawFAIL时以同set detachable预测line availability，并与现有capacity/directory/owner语义一致；commit仍复核原can_detach与generation|确认这是设计缺口而非有意边界；证明preview/commit一致、dirty/WAD顺序和返回正确|不实施；现有真实应用无压力，不是收益修复|
|sticky reuse精化|另定义可证明的事务资格，显式处理当前waiters/descriptor与后续同line重请求；不简单清bit或删除guard|首先证明多waiter及分sector交错、旧新identity、地址唯一性和exact-once|不实施；安全性UNKNOWN|
|ready-pinned detach|须说明为什么释放不再RESERVED的Tag仍是必要机会，并保证已准备response的bank/身份寿命|识别实际必要场景；证明prepared/ICNT交错|不实施；当前无压力依据|

所有候选都保留：旧payload在detached后仍owned/pinned，旧response按原identity完成，不重定向旧fill到新Tag，不隐式扩大descriptor/payload/queue容量，不新增未经建模的response buffer。

## 策略改变前必须完成的正确性检查

- Tag、payload、transaction三种identity及generation一致；同line新请求、不同line占同way都不会混淆旧返回。
- required、issued、pending、ready在queued、lower accept、bank拒绝、乱序sector返回及response enqueue拒绝下分别闭合。
- 所有waiter exact-once；merge失败无状态改变；merged waiter先退休、其它仍pending时不释放payload/descriptor；M-OFF line MSHR寿命不变。
- TVD/directory/owner冲突、WAD与dirty写回、held frontend、WB quota、同bank落点不足仍遵守原顺序保护。
- preview重复调用无模型/observer副作用；预测允许且commit拒绝、detach后新请求拒绝时资源仍可恢复并drain。
- 下游及ICNT有界背压解除后前进；不以绕过Frontend的direct access代替真实路径。
- T-OFF、空证书、无同set RO、sticky reuse、zero-missing与混合native requester负控制保持正确。
- 独立新Core/binary/archive身份、source资格与性能控制登记；任何真实应用另需fresh预算/native准入。旧binary结果绝不继承。

本轮实际完成的是证据、离线验证和设计边界，不是这些候选的证明或授权。下一决定保持“维持现有T”。

## 交付和执行责任

仅主Agent写入独立审查分支本目录。A历史科学、B生产路径、C诊断设计三个只读任务均已完成、汇总、关闭；没有永久科研Lane。交付六份指定文件，外加诊断脚本和离线结果JSON。实际/历史/计划的测试分类见 [MINIMAL_DIAGNOSTIC_PLAN.md](MINIMAL_DIAGNOSTIC_PLAN.md)。原EP-MAIN基准、旧57/44/T0、失败/HOLD、预算和runtime源码保持原有科学身份。
