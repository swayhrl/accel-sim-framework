# EP-L2 / ISCAS2027 — review_r14 | 机制成熟度、四个闲置Lane的轻量续行

2026-10-17。**协调审查，不是新科学/构建/源文件删除授权。** 各工作在原有Worktree/执行分支可恢复有界CONTINUE，不能把Codex Goal已退出等于后台进程已停止，也不能凭旧Git STATUS声称后台仍在运行。相关权威：基础science `6c136e2a56a008695f8c8b815723bf8f1a760db9`，r7并行/资源 `99e7515f81b0038ac49d274b73f774e8ea801e46`，r8工程pilot `56a0517d3a5941a0a870b50e8c915a8a36b9ee5d`，r13两PolyBench目录准确有条件释放 `31251186feccffec192cc1fef8fc7d8164d12d9f`。最新Git HEAD为下面的**远端快照**，运行前重新fetch/检查真实core/registry/进程/磁盘。

## 1. 对“实现完成”的严格定义与当前等级

| Mechanism | Source-level state | Compiler/direct execution | Integrated/scientific state |
|---|---|---|---|
| **U_WB / common B16_BANKED vs U_WB16** | Lane1 Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355`、Framework生产 `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`；包含physical-bank-clock及后续host Tag/payload prefill修复；发布Core `57e1c363aede1a7790bdf94136d832d35ee7b34b`与c948同tree | **本次修复后R0.1尚未构建；21项producer定向NOT_RUN** | **0 CURRENT_ACCEPTED新配对**；旧R0/R1六条科学SUSPENDED；不是现在可以投稿的主性能结论 |
| **TVD** | Lane2 Core `ab413abc2030bfc9aaeea0579b34dfa998671adb`相对c948的10文件独立补丁，包含WAD/TVD/cache/partition/production fixture；Framework `dc21af497c319672c30752ed2192a2a8cc937bab`。TVD算法存在源代码，新的read-version-presence guard不允许missing填零 | 10个预备C++进程/21 positive groups/7 expected rejections均NOT_COMPILED_NOT_RUN；源级检查不是运行PASS | 尚未合入并验证Lane1官方R2；待独立Lane5资格。切勿将本独立branch或static patch看作已完成主线组合 |
| **RO** | Lane3 Core `5ae8b06d58b61189140f571ab37b5f6d51228632`相对c948源码候选（ep-l2-ro-oracle/runtime/transactions/store-port、direct prefill epoch guard）；Framework `e8d6f9671da0748b5f4eb780d6cdf163e91b58d1`，完整commandlist oracle冻结 | 19条准备的production invocation均NOT_RUN；最新source静态与Python工具PASS，不是独立正确性验收 | 无新RO binary、无正式RO应用资格；独立Lane5科学认证欠缺；首个U_WB主线配对不必等RO |
| **Ideal R1.1** | Lane4 Core `8ff56eb0804a027f1e253e629dd2915b02bc03b5`、Framework `4a55269d5a4f1e11b93e67e9d4eadebe8b3b3493`；修复后续合法clean/quiescent host prefill导致I_READ_HIT ReferenceMemory stale符号/版本，保留其他byte/snapshot/counter | 两个新C++ regression NOT_COMPILED_NOT_RUN；正式R1.1 binary=null，18格NOT_RUN | Old1.721×不是当前结果。必须有同-R1.1-binary B16、Lane5当前repair+ideal资格、原正式资源准入 |
| **最终整合/物理PPA** | 无已验证单一版本同时组合并通过TVD/RO/Ideal；Lane6已形成EN-v3文章和9字段源级cost账 | PPA无RTL/综合/STA测量；EN-v3的Fig2–4目前是待测图位 | 当前没有真实合格新性能pair/geomean/硅面积/功率数据，不允许补造 |

当前科学比较是**1168 physical slots/slice、4 banks×292 slots、每bank每physical GPU cycle至多一个line-size op**，B16_BANKED与U_WB16相同物理容量；B8 sensitivity是1160。旧早期路线图里的1152 slots不是此轮accepted运行配置。

## 2. 停止Goal ≠ 机制已完成/需要10h空转

**推荐给四个闲置Codex窗口各一项短Goal**（通常期望60–120分钟以内按实际工作量，触发当前依赖不可用就阶段性停止、保留证据）。它们只能做各自隔离worktree的**非重资源/源码与论文证据**工作，不能启动第二构建/GateWaiter、第二长sim或全量监控器；Lane1独占公共正式R0.1 producer，Lane5独占官方11gate/五对科学实验及run admission。
- **Lane2**：在`ab413…`准确候选上做**TVD与RO/Ideal/common U_WB未来集成的精确冲突风险审查**，着重WAD地址/容量、dirty WB inflight、clean retention、bank service、host prefill、response generation、shared descriptors/owners；可检查现有文件精确差分、编写针对真实未覆盖边界的**少量**最小测试源码/风险表；不得重复既有10-file patch apply/Python listener suite、不得擅自merge Lane1 R2、不得提前启动C++重编译。出`LANE2_TVD_INTEGRATION_READINESS_AND_UNTESTED_GATES`，标明source ready vs compile pending vs scientific pending。
- **Lane3**：针对已经冻结whole-commandlist oracle，独立检查RO与common U_WB/TVD host epoch、stale generation、detached fill与descriptor drain、read duplication/lower traffic的未来共存合同。优先列**真实源码可证的接口冲突/正确性风险**，必要时仅编写小fixture/工具guard；不得改oracle输入、重复采trace、虚构runtime、替Lane1合入。
- **Lane4**：把最新reference sync补丁整理成明确可被Lane1未来R1.1精确挑入的最小源码&两C++新回归合同；核对最新Lane5的CLIENT_CONTRACT hash漂移是历史期待与现时registry身份差异而不是跳过验签许可。仅短准备、无编译/18格。源码语义已经解决的不要再改成initial-only host prefill。
- **Lane6**：基于EN-v3进行**一次严谨的机制-证据-稿件一致性/ISCAS审稿风险核对**：第一贡献只按U_WB当前目标描述、TVD/RO尚无生产结果不能被措辞成已验证性能；核对标题、摘要、图位、负面baseline、bank公平、WAD/Tag/descriptor逻辑、已有真实/缺少的PPA数字与参考引用；不得填性能数、重复没有证据的PPA或不必要全稿重写。输出按论文段落的可执行优先级清单及必要小修；如没有新可信证据，保留待测图位并终止该短Goal。
- 各自完成一次可验证的工作后**允许闲置**，不要为了“窗口有人干活”重复静态检查、GitHub polling或扩大量化矩阵。人工Codex Goal结束后并没有跨窗口自动唤醒；真正官方binary/当前科学接受到达后需用户在对应窗口发事件驱动新CONTINUE。

## 3. 下一依赖触发的严格顺序

1. Storage-Ops按用户r13两条绝对PolyBench closeout stage manifest，独立确认164 recovery pointer和源侧活动身份后有条件分组释放；先correlation、df真实增量；再看正式Lane1是否解锁，必要时covariance。其它科研源文件不许删除。
2. Lane1 GateWaiter重新检查真实旧174 `f_bavail`，原50GiB+mem/registry/进程独占合法才正式构建一次R0.1；工程pilot若无Lane5独立安全token不可使用；正式binary+21 producer directed/完整哈希入库。
3. Lane5独立11gate、V2原生科学权威与资源准入，滚动B16_BANKED/U_WB16五对；首个CURRENT_ACCEPTED交Lane6，五对俱合格才计算geomean。若主线出现科学问题停止受影响声明。
4. Lane2 TVD和Lane3 RO分别**待官方父版本出来**后按自己隔离Core+Framework新binary与受控shared admission做有限C++生产验证，Lane1作为R2最终integrator、Lane5独立新机制资格。不能使用只含U_WB的官方binary当作包含TVD/RO。
5. Lane4 ideal独立R1.1 source/binary出来后用同binary B16与真实ideal overlay跑18格；旧1.721×不能报告为当前。
6. Lane6只有当前V2原生受理的真实结果与后续PPA硬件证据可补Fig/表/摘要，当前可审阅EN-v3但不是正式投稿实测稿。

**本r14不授权任何编译、科学应用、旧结果升格、原science修改、Storage-Ops额外源释放或后台执行。** 仅用于短时、可信且可终止的并行准备，保留所有历史审计/失败证据。
