# Optional128 最终源码有限同行审查

最终审查绑定 Core 3d3887bb2e8d5073d13b0792ff9116834e89fe2f，ELF SHA 9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86。本次发现的局部正确性、进展和排空问题均已在该版本修复，并有最终生产 CPU 回执及 Main 独立复放支持。审查没有修改 A 源码、运行应用或消费预算。

## 真实修复闭合

1. **满银行进展**：初版关闭了 Base 银行回收。G32×8 可出现 bank0 的64个 resident、128个 Base CLEAN 和100个 Ext CLEAN，合计292槽全满；新 dirty miss 无 landing。原257-owner 容量正例没有覆盖该情形。最终共享付费的 Base CLEAN→WB_COMPLETE 银行过滤归约，延迟2周期，核 revision 并占真实 Base 写 lane；释放后重新付费选择。实际 Bank292+dirty WB 分区正例及最终复放通过。
2. **own-DROP 单读口活锁**：55bd 版成功删除 Ext row1 后保留死 ticket，每轮重读 row1，占住唯一 indexed view，Native 替换所需 RR row0 永远拿不到读口。不是 atomic 本身不受支持；冷 Native atomic 对照能返回。修复只在自己成功 DROP 后将 ticket 退为 index128 sentinel，保留此前已付费的 absence/epoch。非 RR atomic、full-write、missing-sector 现均通过，旧失败保留。
3. **内部 WB 提前停钟**：WB 可能已存在于 L2 miss queue/producer，尚未进入 request tracker。最终 segmented 模式的 busy 加入 !ft_drained()；mode0 保留旧行为。实际内部 WB、Bank292 和所有权排空检查通过。
4. **counter 换行**：初版 literal backslash-n 已改为真实换行，Ext 与旧 Base 计数独立。旧版本与失败证据保留，不能当作最终版本的未闭合问题。

## DROP 修复没有赠送查询或漏掉新 owner

该 head 已完成付费地址查询，自己的成功 DROP 证明该地址在 Ext 中已不存在。唯一前端产生 Ext 新 owner 时搬的是被逐出的 Y，当前 Native MISS 是 X，源码要求 Y≠X；首次 Ext 分配后 host prefill 被拒绝。Base 新 owner 的64位 creation epoch 若变化，旧负证明会取消，重新付费查 Base；并未直接把 Ext ticket 解释成 Base ticket。修复只退役死行 token，不增加第二读口、不退款，也不免费重查。

## 成本和比较边界

Base/WAD128 不变，Ext128 仅保留 CLEAN；Payload1168、4 Bank/P1 不变。Base/Ext 共用一个128比较器地址查询端口，Base miss 再付1周期 Ext query。Base 原 CLEAN/WB_COMPLETE 选择不是免费扫描：128×101bit 宽读、bank/state gate、127个64位 age 比较器及 winner mux 按2周期合同计费。

Ext 固定 RR 槽单行读及后续重核，不扫描候选；新增 indexed read view1、metadata write lane1。每 tick 最多2个同 row/UID 的读 fanout；写合并只允许同 row/incarnation/UID/handle 的 BEGIN+END 或 BEGIN+CANCEL，INSTALL/DROP 不可合并，取消不退周期。Base/Ext 双行发布前两写 lane 已预留，revision/incarnation/overflow 先检查；原 Ext handle 在双写后释放，没有额外 Data 或免费搬运。

全 entry 实际 ABI80B，逻辑保守460bit/行，Ext128 合计58,880bit／ABI10,240B；没有借用尚未实现的 RTL 压缩。控制位、epoch、票据和更新口已列成本表。物理 PPA、时钟和比增大 Tag 更便宜均未知。

同一新 Source 上 mode0→1 是 segmented 付费硬件且禁装 Ext 的成本控制，mode1→2 是同硬件开启保留，mode0→2 是净效果。Stencil 仅0/2能回答净结果，不能拆开硬件税。旧 Source78 结果只作背景，不是新 ELF 的匹配对照。

## CPU证据与剩余边界

A 的三 mode 生产 CPU、8份实际283字段 constructor、必要额外8个分区 case、epoch overflow 和 source-off 有界差分均通过。Main 对最终 mode2、全部 extra 和 overflow 独立复放通过。source-off 两侧均 cycles14998、queries157、clean139、dirty1、responses15、promotions1、signature20726。

本报告只支持这些有限工程路径。atomic 使用符号 complete-sector 标签证明协议与所有权，不是独立数值 oracle。当前只资格化 assertion-enabled producer；Tag≤512、CLEAN-only，RO/fixed64/ideal、Ext分配后 host prefill、runtime L2 flush 明确拒绝。不声称覆盖所有多 client、clock、profile 和交错。真实硬件时序/PPA、正式 Main Host/Native 资格及完整应用性能仍待各自流程；本报告不放行模型或科学预算。

精确 Source5、SHA、逐项修复、源码行位和证据见 FINAL_SOURCE_PEER_REVIEW.json。历史快照及初始失败不改写；原 RO 5文件与首轮 peer 10文件 SHA 复核未变。
