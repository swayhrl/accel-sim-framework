# DTC-L1 科学决定：Btree有界地址解释与2DConvolution条件性可行性

**状态：USER_APPROVED_BOUNDED_CPU_CANDIDATE_AND_CONDITIONAL_PAIRS。**
批准依据：用户于2026-10-16明确同意ChatGPT此前“Btree先行、2D全kernel自洽才进入、LUD后置”的提议。
该批准允许Btree的独立派生输入CPU准入、在满足本文明确门槛后至多六组同一新输入对照；允许2DConvolution有限CPU可行性检查。
**当前仅批准条件与实施路径，尚未声称Btree候选已生成、准入或运行。**

## 0. 冻结基线和执行权

- 执行端是原174账户/容器，不是174-new。原Lane A Goal DTC_SERVICE_AND_MODERN_BASELINE_CLOSURE_174_V1保持运行。
- 本次核验的A远端HEAD=e52d3eac6708731e62f689a9cf602fa1c7232784；2026-10-16 14:51:10 UTC机器快照为原44行35 strict PASS、6 RUNNING、3旧Hotspot HOLD、0合法未启动。该HEAD是审阅锚点，执行时fetch新HEAD，不得reset/回退。
- Lane B结束时HEAD=d46cce269b88055decc2ca052dcb9baae0efee7e，所有原Btree/2D/LUD的FORMAT_APPLICABILITY_REVIEW_PENDING不变；B旧来源调查不自动重启。
- 原44行、全部旧数据/日志/失败和Hotspot V2五个独立新输入arm保留。不得改源trace、冻结parser、finite Core、传统Core、binary、global cap或其原已执行attempt；没有现代DTC、SpMV/LayerNorm、LUD新任务授权。
- CPU-only工作置于**新的独立工作树、独立新分支**，只读消费A/B证据。其窗口不具有启动模拟器的authority。GPU任务数为0。
- 本文件与所附Goal位于实验台账协调分支，不属于A的launcher或输入注册表。

## 1. Btree的原始已验证条件，不可提升为capture认证

- 原风险：一个Btree成员、findRangeK PC 1c40、LDG.E.SYS宽4B；6,000条mode0记录，每条仅一个P有效lane却有完整32个地址word。
- Lane B已核完整6000条原行SHA与full32长度；所检查P-only序列化源码与32word形态不相容；所检查旧E-list serializer按ascending E lanes排列地址，失去stride后会退为mode0。
- **条件E-list解释**：在该producer语义下，32个words对应全部32个执行lane，即E全32位；对P中唯一活动lane i，其原地址为raw_word[i]。该规则在6000条中有5792条与冻结decoder的raw_word[0]结果不同，208条相同。不能为得到有利性能更改规则、掩码或挑记录。
- 来源sha：producer revision 0e2fddcdef37fc59ad786553892b75567a5f2cdb / source SHA256 8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a。旧来源家族**compatible but capture unbound**；3个存档候选ELF在sm70 PC1c40是BRA并非本trace的LDG。
- 参考证据：Lane B的LEGACY_FORMAT_SOURCE_BINDING_V1/BTREE_SOURCE_BINDING.md、PRODUCER_POLICY_COMPARISON.json、INDEX_AND_SOURCE_MODEL_RECEIPT.json、原风险索引；不从本文件补造采集producer/hash。

## 2. Btree CPU阶段：最多一个E-list独立派生候选

G0 输入/解释合同：固定原kernel成员、原list和风险索引SHA。先按B的证据复核6000条原字节、P单lane、32word、PC/opcode/width；不符合即FAIL_CANDIDATE，STOP，不在同轮另选解释。

G1 确定性变换：仅对上述PC的全部6000条记录按条件E-list规则建立active-lane地址。候选用现行冻结consumer**能理解的合法mode0/P-list表示**承载唯一活动lane地址（先通过独立parser单元预检）；保留PC、opcode、P mask、CTA/warp、指令顺序、kernel/list顺序、同步、访存类型/宽度。其余记录地址/字节不变，原trace只读。报告每一条的old-new地址及sector/128B line身份差异，目标计数6000 touched / 5792 changed addresses；若不同，解释原因并FAIL_STOP，不能硬凑数字。

G2 独立准入：复用B的风险索引/原行SHA，再完整检查**该一个Btree成员**的字节变动白名单、完整指令/CTA/warp/kernel范围；用未改生产路径的实际SASS consumer/parser读完整派生成员，单独reference decoder复算所有memory records并对照其active-lane地址流HASH、instruction/ROI/boundary/response支持域。source-profile的前提、实际parser身份、Core兼容性、input bundle/list SHA及CPU证明工具SHA必须在性能前冻结。不得只比较指令总数或单个例子。所有差异的程序语义限定为该条件producer模型，不能宣布与原ELF/native output等价。
 
G3 仅G0/G1/G2全部PASS，才生成DERIVED_INPUT_ADMITTED_FOR_BTRE_E_LIST_CONTRACT回执，绑定新member/list/bundle SHA、原输入SHA、CPU独立proof/源版本和适用性限制。若实际consumer不支持合法P-only mode0表达、出现非白名单改动或身份/语义不符，STOP于CPU阶段，不补一个伪parser、不得为了通过而修改runtime解码语义。原Btree scientific pending维持。

## 3. Btree性能阶段：有条件预授权，不由CPU窗口执行

- 仅当独立CPU准入PASS并经科学审查确认G0-G3，另以**新输入身份**预登记至多六个固定arm：B16-N、TC80-N、TRAD96/C+、IO256、OO128、IO128。前五个回答主参照取舍，第六个提供同128 PIB深度的IO/OO对照。无WAIT128/现代DTC/其它新家族。
- 六臂全部使用同一个新Btree bundle/list/完整kernel及有效ROI；与原44行相同的公共SM/频率/ICNT/L2/DRAM配置，使用各设计原有已资格化的Core/binary与有限服务合同；按原Btree fixed variants逐项复核effective config、资源向量、line/sector、PIB、MSHR、额外side path和服务额定值。特别将下行cap及与原传统运行不同的选项**在观察任何新性能前**固定为一个共同可验证的合法值（优先32768，若其不能合法复用应STOP并提出科学改动审查）；不由性能选择cap/clock。
- 原baseline的输入不同，不重标旧C16/C80/C+为新输入分母。全部新arm重新匹配执行；不同设计族有合法Core/binary差别，但输入、指令、配置共同部分和完整范围必须相符。
- 启动权仅属于A原174现存**唯一authority / launch lock**，需新的独立lineage/attempt UUID/manifest与严格watcher，不能覆盖原44行登记，不创建第二个persistent launcher。已有六个原job不可因新研究而暂停/重启；在资源/配额许可且不破坏原任务的条件下滚动新增，否则等待原任务释放。不得把“空闲核”视为新实验自动启动许可。
- 每arm自然terminal+严格身份、原始输出hash、完整有序kernel/instruction、资源credit/reference/physical/PIB/lower/回填/收集/退休/普通路径排空审计PASS，传统有限服务指标缺失保持UNAVAILABLE。记录所有失败、重试与stop，不能用重跑隐藏负结果。
- 仅在完整、同一**新输入**配对后报告C16/C80/C+分别对IO/OO的比值、同128深度的IO/OO比值及机制计量。两种输入各自内部的相对排序可作有限稳健性比较；**不得交叉新/旧cycles取比、代入原GM12、声称捕获语义恢复或等面积/实机收益**。
- 预设STOP：G0-G3任何科学失败则不运行；新性能出现回退或与旧输入排序相反也须保留并停止扩大，不加参数扫点或另造第三解释。完成六arm后停止该分支追加实验。

## 4. 2DConvolution仅限CPU可行性，独立于Btree性能

- 原1成员10个PC，每PC4094条，共40940条有非零first(P)的mode1；9个LDG共36846、1个STG共4094；16376条有条件sector/line数风险。version3真实存在“打印P编码E”和“打印P编码P”两种不同源码；原采集版本/文件日期不足以决定。
- 本阶段仅做CPU证据门槛与方案评估：有无原capture source/build/format receipt能绑定其中一种合同；若选择独立派生源模型，能否对全部10个PC的**全kernel动态执行lane、P、base/stride**建立一致且与来源独立可检查的模型，尽可能含holdout。不得逐行挑first(E)端点、用bank冲突/性能选择解释或把“E可能0或1”作为两条完整合法trace。
- 复用已有40940风险索引与源审计，按必要最小原字节检查，不重新扫629、无界归档/ELF/工具链搜索，不编译/运行GPU。输出可行/不可行及最小缺口、候选输入精确定义（若有）；**2D不在本次授权中生成正式新输入、不准入、不跑配对仿真**，即使发现候选也需另行科学审定。
- LUD的源码global正面证据保留，暂不触碰。

## 5. 审阅/交接

CPU执行者新分支提交：PRECHECK_RECEIPT.json、BTREE_SOURCE_CONTRACT.md、BTREE_DERIVATION_AUDIT.tsv、BTREE_CONSUMER_EQUIVALENCE.json、2D_FEASIBILITY.md、INPUT_IDENTITY.json、GATE.json、FILES_SHA256.tsv、LATEST_REPORT.md（未执行步骤标NOT_RUN）；仅放可审小文件，大输入保留174/164并给只读位置/大小/hash。推送后fetch-back HEAD/tree，对科学PASS/FAIL负责。不要把这一研究写进原A报告直到独立准入和A注册验收通过。

若CPU FAIL或2D不可行，按条件STOP，把原因交ChatGPT审；普通工具/runner/清单问题如可由已核来源确定性恢复，自行solve-and-continue。