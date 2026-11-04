# EP-L2 Performance-First V4：精确审批包

基线为用户已审提交9c4a1a958f726be1250608b0a3b82c79438d0926。旧8项接受和2项Vector技术失败全部关闭、消费不退款、不重试，原Spec/raw保持。本轮只有工程准备，正式应用启动/新预算登记/consume均为0；不恢复论文编辑或采集新Trace。

## 可分别审批的准确范围

| 请求 | 新完整应用预算 | 时钟/结构 | 当前状态与Host墙钟上限 |
|---|---:|---|---|
| A1 Stencil | 2：S、WV_ZERO_RO | Source78，DRAM850/L100，G64×8 | 私有Main工程资格就绪；S8h、WV6h，历史约4.83h/3.71h |
| B Vector4M | 2：W_ONLY、WV_ZERO_RO | Core862/接受ELF不变，DRAM1700/L100，G32×8 | 私有Main工程资格就绪；各900s；先W_ONLY完整接受、真164归档和两次独立恢复，再释放WV |
| A3 可选transpose | 2：S、WV_ZERO_RO | Source78，DRAM850/L100，G64×8 | 独立可选，不隐含加入A1；各30min，历史约12.10/12.30min |
| A2 3MM | 3：G64×8 S/WV，另WV_REF32×8 | Source78，DRAM850/L100 | 方案与预算已定，仍缺WV输入/模式资格及A2正式消费图；S12h、两WV各14h |

建议首批独立批准A1和B，共4次；如果希望尽早再得到一个短负载，可单独批准A3两次。A2可独立审核，但缺口未闭合前不放行，不阻塞其余合格任务。所有次数均为新范围、每点一次，无自动扩展、退款或重试。已接受的REF不重新花预算。

[机器可读准确cohort、Spec、Source5、预算与依赖](main/EXACT_SCIENTIFIC_APPROVAL_REQUESTS.json)

这些“资格就绪”指完成私有Main图与工程审查，**不是共享Native已激活或已获新科学授权**。用户批准后只做Main原子激活和当次动态资源/CPU/boot/mount绑定；固定证据不变时不再引入额外工程复审或重跑旧测试。

## Track A：绝对性能与跨负载

Stencil复用同Source接受REF：S5242939、WV4768893 cycles；transpose两种REF亦有实际接受及模式资格。新G64×8各模式与自身REF比较绝对cycles，再报告同背景S/WV；不把普通Tag容量收益全部归给EP。保留已接受G32×16、G64×16结果，不宣称8-way普适或等面积。

3MM已有同Source S_REF=1696618，WV_REF缺失。加入的新WV_REF恰是三点之一，不能用旧F替代；在该锚接受前，WV相对REF的绝对参数收益为UNKNOWN，新S/WV匹配比仍可单独解释。三kernel不意味着短任务，已有S实际约7.11h。

A1/A3最新消费ROOT见[最终图索引](track_a/resource_admission_followup_v2/FINAL_CONSUMER_GRAPH_INDEX.json)。原早期proposal及其16个缺字段记录保留为历史，不是最终激活图。四个最终候选的43字段、Source78原22依赖及5条Host helper依赖、真实只读资源snapshot和缺授权Native HOLD已检查。旧126/几何/应用NI测试未重跑。

## Track B：Host集成与两个新点

原124项CPU/Host验证直接复用。新增私有Main集成在消费事务前检查完整43字段、native_boot_id、mount namespace、Source862精确22 Native依赖及另外5条Host路径；保留原monitor/eventloop、Core862、接受ELF和原282硬件配置。

Main独立核对原monitor函数AST、所有原run_native语句均保留，新schema位于transaction之前。真实小CPU stub只验证新接线，不是模型或完整应用PASS。900秒预算由同SourceS/F的实际约308/419秒、0.48/0.49GiB RSS支撑，替代未选用的24h候选；RSS2GiB、AS10GiB、result128MiB、预测1GiB。只改Host限额，不动282硬件项。

最终选择的申请与可执行激活入口在[资源补充V3](track_b/resource_activation_addendum_v3/FRESH_TWO_POINT_REQUEST_V3.json)和[具体激活说明](track_b/resource_activation_addendum_v3/README_FINAL_RESOURCE_ACTIVATION_V3.md)。旧两次技术失败保持原状态，新请求独立预算2。复用S45974/F55925，不重跑。

Main发现过实际资源接线错误：旧适配器只改请求名，原SCOPES没有新请求，会直接unknown V3 scope。已另立私有资源补充，精确映射A1/A3/B三ROOT、保留原foreign数学/cap10，并通过真实只读snapshot；未注册admit仍拒绝。旧错误与旧图保留，不放松门限。[最终Main绑定](main/MAIN_SELECTED_RESOURCE_GRAPH_REVIEW.json)

## Track C：不把未建模成本当作免费

bf4/bab27c与Source78/Core862完全分开。既有CPU与283项实际parser回执不重做；私有Host/Native元数据6正例、19反例与依赖pin已完成，六点清单只作库存。

静态实现说明quota计数随安装、清洁行替换、promotion/reclaim更新；CLEAN→CLEAN有先减后加，可净增量合并是未来硬件设计选择。现在没有quota专用更新lane、服务周期或背压；epoch清理也可能在软件循环同cycle多次更新。因此端口/时序/PPA均未资格化，不能宣称免费计数器、更小SRAM或硬件可实现的性能收益。

[实际端口与时序成本表](track_c/QUOTA_COUNTER_UPDATE_COST_TABLE.json)。建议以后先收敛有界原子净增量/更新带宽与阻塞契约，再独立申请同Source FWT cap128基线1点，接受后另审cap64/0；不自动启动六点，也不用Source78结果替代bf4对照。

## 调度、科学边界与下一结构方向

沿已授权global EP cap10动态准入，不是凑十个模型才开跑。Main唯一调度/预算/Native/Git/归档owner；长Stencil或3MM不阻塞已批准且资格就绪的短任务。保留其他owner的真实RAM、cgroup、CPU和剩余写承诺；不重复扣已占用字节或静态历史SSD池。大输入留真164、共享归档锁和一个串行恢复窗口，Native安全余量至少5GiB。

下一结构优化首先验证512 Tag/slice的G64×8是否对更多输入保留收益；其次以Vector新W、WV绝对cycles区分W组织固定开销和额外V包成本，若低Victim服务而额外成本明显，优先减少无效lookup/调度/端口占用，不先扩Tag。WV到F包含RO/M/T及交互，不当作独立T因果结论。C必须把quota控制代价纳入同Source对照。

应用NI未测、B0/M0a未证明仍如实保留；无具体控制依赖风险时不额外申请NI模型。禁止跨Source GM、完整GPU/PPA或未运行点的性能宣称。论文编辑仍不恢复。

[Main工程复核](main/MAIN_INDEPENDENT_ENGINEERING_REVIEW.json) · [Source/资源最终绑定](main/MAIN_SELECTED_RESOURCE_GRAPH_REVIEW.json) · [调度释放政策](main/DISPATCH_AND_RELEASE_POLICY.json) · [旧预算保持/新启动0](main/OLD_SCOPE_AND_ZERO_NEW_STARTS_FINAL.json)
