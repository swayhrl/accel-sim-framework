# EP-L2 / ISCAS 2027 — review_r17｜首组CURRENT_ACCEPTED以及剩余四组的正确推进

2026-10-17，协调侧只读GitHub核查。**本文件是科学结果核对和后续建议，不更改Lane5 CURRENT_ACCEPTED权威、不会自动运行Codex Goal/新sim、不批准新配置或新增源删除。** 准确生产与旧版本区分，科学ledger可被未来新证据撤回，任何消费都应读当前Live Lane5 authority。

## 1. 现有确切发表数据（不再标成“还没通过”）

- 官方可被资格化的**修复后**产生源码：Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`、Framework `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`、binary SHA256 `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`。**不是**旧的 producer `088146.../861a.../e424...`。User所见Lane1截图该源和31/31真实定向PASS，先前Core旧版保留不覆盖。
- Lane5独立11-gate资格PASS（修复版31定向＋4非法配置负面拒绝＋OFF），V2 authority `generation=4`，`revision=FT20261017_LANE5_A1_B1_FIRST_SAD_ACCEPTED_r1`，HEAD `0677446bb61fef2e8dd0b85f3963d77b07f5d855`。V2追加2条SAD `CURRENT_ACCEPTED`，保留10条旧ledger原样（6 suspended、4 not-run），不可自动恢复。
- 合格SAD同source/binary/trace、同157583646条指令、64slice闭合：B16_BANKED周期`110773`，U_WB16周期`110749`，加速 `1.0002167062456546` 即 `+0.02166592942323131%`（减少24 cycles）。证据：Lane5 `FT20261017_LANE5_R0_1_A1_B1_SAD_PAIR_r1` 原始运行 `9aad33380a524b4177c1fec3fbd4f93cef3ac53b`，科学接受提交 `0677446...`，`LANE6_HANDOFF.json`。
- 两模式WB完成/下层接受相同 `3975`。完成的copy transfers B16 `3975` vs U `0`，logical bank ops `483611` vs `475661`（恰差`2×3975=7950`），Bank累计等待 `2255` vs `2233`。**两者WB data-full 0、pool-full 0、WAD满/冲突0、DRAM写字节508800相同、capacity_above_C16未观察到**。所以它是原预设的**near-tie负对照**：证明协议消除了copy操作，但没有证明容量收益或普遍加速；不假设24cycle差异有任何统计显著性。
- 内容资格限定为`FULL_NATIVE_NONATOMIC_ONLY_WITH_PER_SPEC_COMPLETE_CONTENT_PROOF`、32B symbolic sector versions/requester/WB/资源闭合；**不是SASS输出数值正确性验证**。C1旧resident headroom观测不能进入因果图。当前`1/5` pair accepted，**禁止四个尚未接受应用凑数或发布group geomean**。

## 2. 最节约时间的现有窗口分工

- **Lane5独占运行owner；维持原10h Goal**。V2正式SAD已经交给Lane6；自然推进已有五个预先指定开发负载里的其余四对，建议先可完整冻结且已认证无atomic/当前解析器可接受的`vectorAdd_4M`和`cfd_097k`，`convolutionSeparable`和`FWT_7_21`在并行CPU-only输入资格核对完后再运行。两个long sim全局上限、所有用户资源限制和实际registry锁不变；每一对后独立审查并及时发布，不能因为SAD平局就删掉/替换它或选最快完成的子集。
- **解析器兼容性是科学边界，不只是文本处理小事**：Convolution旧trace所含零活动掩码扩展地址字段不能简单静默丢弃后称完整原始输入；需给出native消费解析的独立字节/语义证明或明确`UNSUPPORTED_TRACE_FORMAT`，保留原始trace和失败证据。FWT需同样以完整内容入场，不拿roster哈希替代真实body哈希。不因格式问题悄悄裁剪、换输入或改负载。
- **Lane1原Goal已完成，可以闲置**；若Lane5发现对真实主线科学错误需源修复，才能回到Lane1新有界Goal。老Storage-Ops已经归档源释放关闭，不再授权清理。Lane2独立B1/C1/C2已交付并准确给主线，TVD分支最新新定向仍没有官方完整C++资格。Lane3 RO A2/A3 18次源码绑定C++ old-red/new-green PASS，但正式R2 19项C++/科学资格仍未做；可闲置，不抢两长sim。
- **Lane6可以一次性消费首个CURRENT_ACCEPTED**：从当前Lane5 generation4走原生V2 acceptance+native adapter完整身份/样本校验，只把SAD作为单独负对照证据条目，注明copy3975→0/ops7950少/无WB-data满/周期近乎持平/解释限制；修正EN-v5尚写0当前pair或无实测的时态表达，但**暂不向四个空图插入误导性单点bar或改abstract成总体性能成功**。编排Fig2/3待五对陆续收到再批量完成，严格保留4+1页与原10篇参考文献。如果当前Lane5未来撤回该row，应自动撤回该图表数据；不靠拷贝旧固定V2 gen4免核验。
- Lane4 Ideal待同binary正式R1.1和独立资格，不得用当前主binary跑18格。若要做`1024 resident/112 bypass/32 WB`等同总预算强静态对照，需要独立科学合同／准确配置、FIFO/Bank budget和实测资格；当前只保留方案，不擅自将WBUF32附加到1168容量而变1184。

## 3. 下一证据里程碑

1. 第一组SAD科学接受已闭合（历史版本不重算）。
2. 新的至少1组**非负对照**CURRENT_ACCEPTED后，立即比较实际WB/copy/Bank等待、WBUF满、下层bytes/服务与cycles是否同时变化；如果收益不显著而copy已减少，优先建立pressure定位和downstream作用，不盲目扩大trace。
3. 五组均CURRENT_ACCEPTED后才算geomean，保留所有减速/平局；再按资源/价值判断强静态对照、WBUF8敏感性、Ideal或TVD/RO增量是不是ISCAS正文必需。

**本r17不创建任何额外后台进程或轮询器。** Lane5当前工作不应被本文件打断；如Lane6窗口闲置可单次新Goal消费SAD，无需其余Lane恢复。
