# Hotspot V2 资格报告：供 ChatGPT 最终审查

结论：**DERIVED_INPUT_QUALIFICATION_CANDIDATE_READY_FOR_FINAL_REVIEW**。在已披露的重建源码模型下，Hotspot V2 的 CPU 资格检查通过。它是独立的新派生输入候选，不声称等价于历史采集二进制。用户已选择继续提交本候选，将 Btree、LUD、2DConvolution 分别作为独立科学风险审查；这三项风险不再阻塞 Hotspot 资格报告的交付。

这项选择不代表正式输入准入、科学结果接受、HOLD 解除或模拟器启动授权。最终审查之后，仍由 Lane A 决定新输入正式准入及新 attempt 的登记。原 trace、历史结果、主 parser、Lane A binary、44 行注册表及调度状态保持原样。

## 输入与解释

完整合同见 [DERIVED_INPUT_IDENTITY.json](DERIVED_INPUT_IDENTITY.json)。原成员 SHA 是 `ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8`；候选成员 SHA 是 `21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985`，1093377608 字节。候选 bundle digest 是 `dd0da35f5a3e3a2467a1cd23a53ce3966cd7eb6ee31035733e26f48dc532c169`，同时绑定新目录中的 list、成员、源码模型、SASS 和离线规范化器。

重建使用未改动的历史 Hotspot 源码（SHA `0f679be008be285d26ebd7d71eba47b164914dd52873c26ee63beecda2f68cc0`），CUDA9.1.85 前端及 CUDA10.1.243 汇编器。PTX/cubin/SASS、官方工具包和隔离 host-header 兼容调整的身份及命令已有收据，入口为 [REPRODUCE.md](REPRODUCE.md)。没有执行新 ELF、GPU kernel 或模拟器。

## 已通过的资格检查

1. 全部 13169524 条 warp 记录、377291004 条 active-thread instructions 再次核对，185 个已观察 PC 的 opcode 根和有序 GPR 签名均匹配重建 SASS。逐 PC 对照见 [PC_PROFILE_185.tsv](PC_PROFILE_185.tsv)。该比较不覆盖 predicate、指令 immediate、完整 opcode modifier 或机器码身份。
2. 独立的源码级地址模型匹配 16950260 个显式 shared 活动地址（660820 条记录）及 3720992 个显式 global-load 活动地址；输出 store 的 1048576 个 lane 地址也给出一致的输出基址。336608 条 active shared mode1 记录在该模型下具有唯一兼容执行锚点。见 [PROFILE_RECHECK.json](PROFILE_RECHECK.json)。
3. 独立于规范化器的逐行差分确认恰好修改 6 个 PC 的 122760 条记录，改变 2944024 个活动 lane 地址，其余 13268655 行字节完全一致。PC0180/0190 各修改1364条 LDG；PC0290/02a0 各修改1364条 STS；PC0ab0/0ac0 各修改58652条 LDS.U/STS。完整变更索引包含每条记录的原/候选行号、偏移、行 SHA 和地址向量，其路径及压缩/解压 SHA 见 [DIFFERENTIAL_RECHECK.json](DIFFERENTIAL_RECHECK.json)。
4. 历史 encoder/冻结 decoder 的26项 CPU 对照证据保留；正常和优化 Python 下12项候选拒绝检查通过。8个受保护元数据、HOLD、parser 和 binary 的哈希检查通过。没有修改主运行路径。

## 原始字节与重建模型的证据边界

PC、P mask、显式地址向量、base/stride 和文件/行身份由原 trace 字节直接支持。0180/0190 的候选值来自原记录的 full32 地址列表，按明确披露的历史 E-list 编码合同关联 lane，共2728条记录、46376个改变的活动地址；源码模型另作交叉校验。

0290/02a0/0ab0/0ac0 的候选有效地址及执行锚点依赖重建源码/SASS 的地址模型，共120032条记录、2897648个改变的活动地址。原压缩字节本身不能恢复其隐去的 E mask。独立显式向量支持该模型，但不把模型条件下的唯一性升级为历史原 ELF 身份证明。逐项边界见 [EVIDENCE_BOUNDARY.md](EVIDENCE_BOUNDARY.md)。

原始 ELF、traceall.so、driver/JIT 的不可变采集收据及 temp/power 数据字节身份尚未闭合；native 输出和精确历史执行等价均未证明。用户允许以明确披露的独立派生候选继续研究，不再把恢复原 ELF 当作继续资格研究的前提。对这个新输入的任何正式科学结论，仍须受上述支持域限制。

## 最小配对复验与最终审查事项

最终审查需判断：是否接受这一独立 source-profile-derived 输入定义及其证据边界，允许 Lane A 进入正式准入流程。此报告本身不作该决定。

如果获准，主 Hotspot baseline/IO/OO 比较至少需要**同一新输入、共同冻结兼容运行模型下的 B16-N、IO、OO 三个新 attempt**。只有实际用于论证的 TC80/TRAD96/IO128/WAIT128 控制才需追加匹配复验，现代容量和 SM89 不在此范围。详见 [MINIMUM_PAIRED_REVALIDATION.md](MINIMUM_PAIRED_REVALIDATION.md)。

新输入不能与旧 baseline 混算加速比，不能把旧 attempt 改写为新输入身份，不能因局部 CPU 地址检查就宣布 native fidelity 或 GM12 已成立。[AFFECTED_RESULT_ROWS.tsv](AFFECTED_RESULT_ROWS.tsv) 保留12个已选择的历史结果及控制身份。

其余11负载的限定格式审查已经交付；Btree、LUD、2DConvolution 的独立风险另作有界细化报告。相似编码现象既不是“历史结果已错”的充分证据，也不是“不受影响”的证明。没有变更它们的输入、已有结果或准入状态。
