# Btree E-list CPU资格审阅包

结论：**G0 / G1 / G2 / G3全部PASS**，回执为 `DERIVED_INPUT_ADMITTED_FOR_BTRE_E_LIST_CONTRACT`（严格沿用授权文件的BTRE拼写）。这是独立派生输入的条件合同CPU资格，待ChatGPT科学审阅；原Btree的 `FORMAT_APPLICABILITY_REVIEW_PENDING` 保留。**本窗口GPU、模拟器、新六臂和A注册均为0 / NOT_RUN。**

执行端为原 `huangrulin-174`。首次fetch文档远端HEAD为 `f2c106a1b767042733600fcfe3b4ba88f1e6ef26`，完整读取两份授权文件后，新建 `hrl/iscas2027-dtc-btree-format-stability-174-v1` 和隔离worktree；未覆盖同名任务。输入与大日志位于 `/workspace/dtc-btree-format-stability-cpu-174-v1/`，不进Git。

| 项目 | 结果 | 可核证据 |
|---|---|---|
| G0 原输入/合同 | PASS | 原list、两个成员及风险索引SHA；固定6000条原行SHA、单P/full32、PC/opcode/width全匹配 |
| G1 唯一候选 | PASS | 全6000条改为mode0/P-list；5792地址改变、208相同；5792 sector及128B line身份改变；逐行审计TSV |
| G2 独立完整准入 | PASS | 完整成员字节白名单；实际冻结parser读取完整两个kernel；所有访存地址流SHA及指令流SHA与独立reference分别一致 |
| G3 输入封存 | PASS | 新bundle `6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585`；完整INPUT_IDENTITY/GATE及工具SHA |
| 2D采集来源绑定 | FAIL / UNRESOLVED | version3打印P/编码E及打印P/编码P都存在，无固定capture构建收据 |
| 2D整kernel解释可行性门槛 | FAIL / INCOMPLETE | 统一源码偏移假设匹配30个有界见证，但独立PC/SASS、动态E/控制流及输出基址证据未闭合；停止扩展 |
| 六臂公共配置/32768 cap合法性 | PASS（提案） | SIX_ARM_PROPOSAL.json保存六份完整effective options、来源SHA、资源向量及全部差异；无注册、无执行 |

原list包含 `findRangeK` 和 `findK` 两个kernel。保留原580字节list及全部Memcpy命令/顺序，仅修改kernel-1；kernel-2逐字节不变。完整ROI是16,000 CTA、128,000 warp、15,609,327 warp指令记录和444,467,849活动线程指令。两个kernel共2,011,551条访存记录，实际宽度4/8B；所有活动地址满足对齐及单lane不跨32B sector/128B line，单指令最多2个128B reference、5个sector。原始头、CTA/warp、PC/GPR、mask、opcode、同步、访存类型/宽度、指令与kernel顺序不变。完整核验包括未改kernel-2，没有重复629成员扫描。

实际生产路径为冻结framework `18a68dcccd795f1b6cda75504e9450d00c9cee02` 的完整 `trace_parser.cc`，SHA `f63db893d39bfcd4cbf679ea1158fd9a0594211181333e13b2fdbb478d60ddb7`。CPU driver调用生产list→kernel→threadblock→instruction接口，链接真实CUDA类型头；没有stub/parser替代品，没有执行Core或模拟器。Core兼容性是全输入合法域检查与两个冻结Core源代码审查，后续运行的credit/reference/physical/排空审计仍必须由A完成。

首次reference工具误把风险PC的4B宽度套到原成员所有访存，在原第24行 `LDG.E.64.SYS` 停止。按冻结parser/Core既有合法宽度修正工具后完整复核PASS；输入没有再生成或修改。原失败、原工具精确版本及修正说明均保留，见ENGINEERING_FAILURE_HISTORY.json。这不是修改科学输入/支持域，也没有删失败重跑性能。

需审查的科学边界：历史E-list serializer与本成员形态相容，但**没有绑定实际capture producer、原ELF或native输出等价性**。只在明确采用该新条件合同后研究，不能重标旧结果。2D目前没有完整候选输入定义；只保留有界相容性证据，不按地址合理性选择first(E)，不生成两条端点trace。LUD未触碰。

最多六臂建议固定为B16-N、TC80-N、TRAD96/C+、IO256、OO128、IO128，全部绑定同一新bundle/完整两kernel和共同32768下行cap。科学审阅通过后仍需原A唯一authority独立准入、UUID lineage和调度；此提案不是A的manifest或启动许可。全部新臂配齐后才计算新输入内部比值；禁止新旧输入cycles交叉取比、并入原GM12、宣称native/等面积收益。出现科学失败、退化或排序反转时保留结果并停止扩大，不调参或造第三解释。

原A HEAD、原44行、冻结parser/Core/binary、原trace及原有HOLD均只读。POSTCHECK_RECEIPT确认六个原作业和唯一scoped authority的PID/start ticks保持，未reset、重启或恢复B/C/D。

审阅入口：[GATE.json](GATE.json)、[INPUT_IDENTITY.json](INPUT_IDENTITY.json)、[BTREE_SOURCE_CONTRACT.md](BTREE_SOURCE_CONTRACT.md)、[BTREE_CONSUMER_EQUIVALENCE.json](BTREE_CONSUMER_EQUIVALENCE.json)、[2D_FEASIBILITY.md](2D_FEASIBILITY.md)、[SIX_ARM_PROPOSAL.md](SIX_ARM_PROPOSAL.md)、[REPRODUCE.md](REPRODUCE.md)。
