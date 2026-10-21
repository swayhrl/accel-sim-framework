# A2：D/F候选与冻结producer兼容性审查

审查完成；**无需为FWT或SGEMM调研重建、增加opcode或机制。当前新binary尚无完整F的E资格。** 最短路径是复用原输入属性证明，再由E分别审查准确runtime/profile/input；不是继承旧main61 PASS。此报告不授予启动权限，不替换原结果。机器可读证据、全部路径/SHA见`AUDIT.json`，逐项结论见`SUPPORT_GAPS.json`。

候选范围来自已fetch的D `f93add1ef2e22e5f8b04e1dce7de5b7ddfd15a80`、F `42846b018dc1f31f42a77ce1642d707195aa9a75`、E `0bb1699f71162963b2a8f061f4ee8c844df47f71`。E的workload_research明确先审FWT、SGEMM，再选完整不规则/迭代输入。这两个D/F HEAD尚无本轮新输入工程包，F的旧174-new环境材料不能当作原174输入资格；最后回读D新增三对capacity消费提交；其原候选审查/INPUT_SELECTION未变，新增结果消费不是新增F资格。下述是这次固定快照，不对后来新包预判。

## 准确source / binary / archive / config绑定

| 身份 | 源码 | 实物SHA256 /配置入口 | 资格适用边界 |
|---|---|---|---|
| 旧main61 | Core `d010911e3174a3764791183cd108fe4664ba8731` | main `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；archive `3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8` | 保留原准确S/F/profile/input资格及历史结果；不跨Core/main继承 |
| 当前capacity producer | Core `fe7e1fc1e8f40b5c4c6d0f232a528483891389c5` | main `93a9f28ddb9c0c9ceb93409764a5664666589477778fe5d41d90a179704706eb`；archive `bed717ec2c4c5cd533c1a1fa15b79059907710885e61a61c1d70e0ace00be708` | 已发布S master0/大容量data-free master1；当前E登记覆盖原五输入S/ON，**没有F** |
| 两者共同Framework/vendor | Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；pybind11 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b` | parser、ISA、commandlist frontend都按此Framework实物/commit核对 | Framework相同只支持复核输入属性；Core不同仍需E资格 |

上述四个main/archive重新SHA实物核验一致，两个生产source未修改。新producer路径及完整构建/test身份保持原正式包`MS20261021_A2_L2_LARGE_CAPACITY_PRODUCER_r1/RELEASE.json`。旧准确profile文档是`MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1/SUPPORTED_PROFILES.json`；顶层旧r28/main773文档不是main61权威。

FWT原S/F准确配置资产由E011/E012的`input_spec.json`、`input_audit.json`绑定；新source只能把它们作为配置参照并显式master0后重新建立runtime-config身份，不能复制旧run key/qualification id。原五输入新S/ON配置由原producer `APPLICATION_CONFIG_MANIFEST.json`绑定；不将这些输入或profile换名为FWT/SGEMM。SGEMM尚无E批准的完整S/F配置绑定，不能直接套Conv证书或spec。

## 候选支持与最小资格缺口

表中“格式/源码支持”是静态审查；“工程控制”指已经发生的检查；“E资格”要求准确source/main/profile/input一致。无文件的外部类别不能推定supported或unsupported。

| 候选/完整输入 | 格式、opcode和source支持 | 已有工程/输入证据可复用 | E独立资格现状 | 最小缺口与处理 |
|---|---|---|---|---|
| **FWT_7_21**，`-logK 7 -logD 21`，19kernel，791609344 lane instructions，body 1785749388B | binary70，legacy header未声明tracer version，原生默认0；37种完整opcode均在现有Volta表；全输入global/shared atomic为0。S/F可走有限路径；ON仅S | 完整原字节/19文件SHA、非原子、oracle命令域证明可供E重绑定；当前parser/ISA与证明一致，Core访存生成文件一致。固定输入SHA `f3695b85379fb762faaf9830bda449e0a5f1e4d3e351774cf33d90850059b460` | 旧main61有准确S/F资格；E011/E012仍INCOMPLETE。当前93a9既无FWT S/F资格，也无FWT ON资格 | F核对捕获来源及源码revision UNKNOWN的既定冻结trace范围；C/E复核整个epoch零RO证书及host边界；若用新binary，先补有限F生产证据和FWT新source输入重绑定、terminal/parser资格。恢复运行仍由E另行批准执行，旧缺失exit不追认 |
| **Parboil SGEMM medium**，完整1kernel，1658916864 instructions，body 2216170035B | binary70，NVBit1.4/tracer3；21种完整opcode均映射；51847488 warp records；global/shared atomic为0。所见LDG/STG/LDS/STS/FFMA/BAR等不需新opcode | D已完成全字节/原生grammar/非原子证明；本轮核命令表SHA、物理大小和有界header，未重扫2.216GB。准确输入SHA `694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb` | 原中央已登记`E2_EXP_SGEMM_MEDIUM_20261020_r1`，**REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE**，非Btree替换；两binary均无SGEMM完整S/F资格 | F补真实源码/数据/capture命令与工具链来源（当前source revision、run.sh UNKNOWN），或交E明确批准冻结trace语义范围；C/E出本输入证书或明确零覆盖fallback，T/M保持ON；E绑定完整S/F配置、数据身份和终验。数值输出验证与trace模型资格分开列，不冒称numeric SASS正确性 |
| **Btree原mil/command输入**，2kernel，444467849 instructions | 名义LDG可decode，**实际完整输入地址映射不等价**：line691 mask10000000，仅lane28活动；原生list_all把第一地址给lane28 `0x7f8eed50bc04`，记录第28地址为`0x7f8ef0d10f88` | 保存的完整失败witness/来源可复用；静态RO证书、旧all-OFF canary不能解除HOLD | E明确INPUT_SCOPE_HOLD，未解除 | 保留HOLD。需真实输入格式/原始采集语义闭合；若需parser修复，单独走producer流程、新身份、受影响输入重新资格；不得补写/截断trace或沿用zero-mask-only证明 |
| **SpMV Dubcova3 large**，21131849 instructions | 完整grammar失败：line80103，`0880 ffffffff 1 R9 IADD3 2 R9` 声明2个源却仅1个；IADD3 opcode本身已支持 | 原始坏行、SHA、保存成本代理；旧23453周期属于另一runtime，非资格 | HOLD，两binary均无完整输入S/F资格 | F追溯真实完整输入/采集来源。不得猜补寄存器、放宽parser或以旧周期追认；真正需修复再独立producer流程 |
| **Scan NO_ARGS**，33kernel，1963460720 instructions | 后续完整文件有非零mask full32 shared-address尾部；line64 STS mask80000000，非zero-mask例外。前6文件通过不代表33全部通过 | 原失败记录及已审前缀仅作为定位证据，不作为完整资格 | HOLD | 先闭合原始地址编码语义/完整输入来源。不得删失败kernel或尾部、改称full application；当前非优先运行候选 |
| **BFS；Hotspot/stencil；PolyBench GEMM** | 只有类别/公开源码调查；这次handoff没有冻结的本地完整包、opcode集合、版本、总指令及oracle | 可复用E调查的选型理由，不可继承另一实现/输入资格 | UNKNOWN / NO_EXACT_INPUT_QUALIFICATION | D先选准确实现/输入；F交完整源码参数、数据/capture、kernel/host-command全清单及SHA；再查实际格式/opcode、atomic与模型语义。不能把SGEMM和GEMM自动视为同一实现 |
| **histo / histogram原子候选** | native decoder存在ATOM/ATOMG/RED和shared ATOMS分支；**不等于完整atomic数值/data/oracle科学资格**。尚无本输入完整opcode表 | 现有非原子输入及native检查不覆盖atomic新科学范围 | NOT_QUALIFIED；不建议首批 | 明确global/shared原子、RED、竞争返回与overflow语义及oracle排除；由A/E审实际路径并制定最小生产验证，再由E审新范围；本轮不增加机制 |
| **新Hopper/H200 tracez输入** | 当前PipeReader仅`.traceg`/`.xz`；无`.tracez` decoder；binary map仅35/60/61/70/75/80/86，无90 | 不继承公开发布或格式转换声称 | 当前此格式/架构路径不支持 | 不作为本轮可运行候选。需要转换/新ISA时单独生产流程与输入完整性证明；不能只改后缀或删除遗漏kernel |

FWT/SGEMM的旧大SHA来自完整扫描证据，不是本轮重新哈希；这次只对小commandlist、保存metadata、源码以及四个生产main/archive重新核验。全输入“字节/grammar完整”和“应用源码/数值输出语义完整”分别列，不混淆。

## 精确profile兼容矩阵

所有有限profile要求master0；新总开关默认0仅保留旧路径可达，**不是统一F的producer/E认证**。传统S：ft_mode1，W/V/T/M=0；完整F：ft_mode2，W/V/T/M=1、tvd_clean=dirty1、T/M各1、data_free/copy_free0、fixed0、P1。有限共享预算1168payload、1024Tag、128line-MSHR、512descriptor、每址32、WAD128、legacyWB16、4banks×1op保持原准确配置。

| profile | 两版源码路径 | 新93a9实际已有验证/资格 | 对新增候选的缺口 |
|---|---|---|---|
| S，master0 | 可达；有限传统S | 生产12项含S/OFF及旧archive对照；E五输入S资格 | FWT/SGEMM逐输入重绑定与E终验；新五输入S不能代替它们 |
| F，master0 | 可达；U/W+V+T+M；受原finite guard约束 | **本轮12项及E14步骤没有统一F生产行为用例**；当前登记F资格0 | 新source有限F生产定向证据＋E独立profile/输入/parser资格；旧main61门证据仅供受影响分析 |
| W_ONLY / F_MINUS_V / F_MINUS_R / WV_T_ONLY / WV_M_ONLY，master0 | 原路径保留；分别W / WTM / WV / WVT / WVM，ft_mode2；涉及T/M者必须本输入证书/fallback | 新source无这些profile的E资格；旧main61具体已接受控制只对旧准确输入有效 | 若D正式选择再补对应有限生产控制和E资格，不自动扩消融网格 |
| S_COPY_FREE / S_L2_DATA_FREE / F_L2_DATA_FREE，master0 | source可达；COPY_FREE仅S；两个data-free各保持有限容量 | 新capacity ON不是上述任一有限容量data-free资格 | 分别验证真实有限残余服务/固定latch、数据/WB/drain、诊断标签；F端另需F资格。不能以大容量ON替代有限F_L2_DATA_FREE |
| STATIC_WB64/S_WB64，master0 | 原static_s64路径；1168=1024+80+64，不是完整fixed64 victim | 新source尚无此E资格 | 仅在准确profile/source/input下审；不能当F_FIXED64_DIRTY_RO |
| S大容量＋L2_DATA_FREE，master1 | **只支持传统S**，固定共同64x向量；F/W/V/T/M/RO/COPY_FREE等组合直接拒绝 | A12项、E14步骤以及原五输入S/ON资格；非硬件P1吞吐 | 新输入仍须单独资格；不改参数逐输入择优，不继承完整F |
| F_MINUS_W；完整F_FIXED64_DIRTY_RO；master1+F | 不支持；最后一项是明确非法组合 | 无 | 保留边界，本轮不开发、不用不等价替代物 |

## 调用链、真实语义与资格复用

1. **格式**：Framework `gpu-simulator/trace-parser/trace_parser.cc:234`解析commandlist，`:135`解析寄存器/mask/地址；`:192`的list_all只为活动lane依次消费地址。`:431`只接受xz或traceg。FWT全部19kernel没有原zero-mask扩展尾部；SGEMM tracer3完整grammar已审。DWT/Btree等其他输入的zero-mask证明不能扩大到非零mask full32。
2. **opcode**：`trace-driven/trace_driven.cc:104`按binary version选ISA；`:192`拆opcode基名并查表，未知指令assert。FWT37/SGEMM21种完整opcode与当前Volta表逐项匹配，未发现需增加opcode。**存在的旧边界**：不支持binary version分支`:118–121`打印错误却exit0，故E仍必须要求完整kernel/instruction、fatal排除和drain；exit0单独不成立。它不影响两项binary70，本轮不以未选外部90输入触发自动生产修复。
3. **旧证明身份复核**：FWT旧输入证明使用Framework9bd；当前9dd的parser/ISA完全同SHA。trace_driven.cc不是全文件同SHA：唯一新增`ep_l2_mq2_ordinary_read = inst_t::ep_l2_plain_ldg(opcode_tokens)`（当前`:195`）。本轮S/F/ON均MQ2=0；解码表/地址不变已逐字节delta验证。Core `abstract_hardware_model.cc`与旧证明SHA仍完全一致。可复用的是这些静态属性，非旧runtime PASS。
4. **epoch/host命令**：`accel-sim.cc:109`按完整commandlist走HtoD，RO启用时在drained边界执行；首次kernel开启整commandlist epoch，完成/最终drain后`:101`关闭并打印complete。只识别HtoD与kernel，DtoH被parser忽略，不能从trace重放推断CPU数值输出对照已执行。FWT/SGEMM命令表实物均为2次HtoD；每次输出oracle/原应用验证由F列真实来源和缺口。
5. **F证书和fallback**：Core `src/gpgpu-sim/ep-l2-ro-runtime.inc:34–71`校验geometry、ranges/manifest SHA、whole_commandlist及address domain；零覆盖必须显式`SAFE_FALLBACK_NO_CERTIFIED_LINES`＋`NO_READONLY_CERTIFICATION`且ranges为空。FWT已有whole-epoch零RO背景（全局读行均有同line写），可交E复核重绑；这不等于T/M关闭。SGEMM不能借Conv/FWT的证书，须自有证书或经E认可的零覆盖fallback。
6. **master互斥**：Core `gpu-cache.cc:181–204`仅在master1转换容量/free-service并拒绝F/RO/V；`gpu-cache.h:3327–3365`保留finite F和RO/诊断guard。master0的F代码仍可达，但共享slot容量边界/构造/统计/deep-check路径经过本次Core修改；S等价不能替代对F的实测。特别是`ep-l2-ft-cache.inc:497`后F借位统计已从常量换成capacity accessor，需纳入E受影响审查。
7. **atomic边界**：Framework `trace_driven.cc:295–319`将global ATOM/RED设为L2 atomic、shared ATOMS走shared；Core `ep-l2-ft-cache.inc:150–170`只是symbolic sector版本标签，注释明确回调归response consumer。不能从此推导atomic数值、返回值/顺序或data-free的全应用认证；当前FWT/SGEMM完整非原子证据仅排除了这类新增风险。

新增完整F最小生产证据应针对准确新archive，用现有小fixture覆盖：有限U的payload角色/dirty V和WB完成、同址WAD重试/rollback、T/M late-sector与host更新、shared目录/descriptor退压、sector版本/exact-once/全drain、P1与mode合法性，外加本输入证书/fallback绑定及64slice终验schema。E可先做source-delta覆盖映射、复用**同一新身份**确已覆盖的门，仅对确有缺口做有界native；不是要求重跑全部旧17项，更不要求重建完整模拟器。本轮没有运行这些新检查，也没有自签“已有PASS”。

## 交接与边界

F交准确完整输入/来源/oracle缺口；D冻结选型和排除原因，保留原负结果与探索队列；A只对确实定位到的生产兼容缺陷按原流程最小修复、独立source/build/output、冻结新身份及受影响native；E独立接纳新runtime/profile/input、科学范围和唯一控制器执行。此次审查没有发现FWT/SGEMM必须修改当前producer的真实兼容缺陷。

本轮新构建0、native0、完整应用0、trace全扫0、机制修改0、E台账/runner修改0。中央只读快照见`AUDIT.json`；新SGEMM探索HOLD、旧FWT INCOMPLETE、B/C原联合失败边界、F_MINUS_W/fixed64边界全部保留。数值/时间上限的后来取消也不授权新输入或重试，本报告不变更任何政策。
