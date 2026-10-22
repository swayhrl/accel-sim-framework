现存 r4 native 证据足以排除“核心 detach 计数整条断线”，但不足以宣称 212 个字段的每个分支都已动态验证。该结论来自已完成的 48 个进程保存日志、正式 A2 release、固定 Core 源码及既有独立验收；没有重新执行 native、应用或 build。

固定 Core：`9243f769620653f2a9d4df5599e9581e9dae6067`。
生产 main SHA256：`d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13`。
生产 archive SHA256：`6c8dc6c3b456740155bfae4d51b53841ed271adc740aaa42c7c089d0aa82bb57`。
这些 native 是链接已登记生产 archive 的测试 ELF，不是完整应用。测试源码 `tests/ep_l2/test_detach_diagnostic.cc` SHA256：`0579f67c986ea58ce98aa368cf7184e4983421a1ae61672d5e31f73802899c89`；诊断 ELF 的已验证身份为 `1a33013c05edf474162fb8c6ae16deb77f5b6f8a6cf262dd461bbd5f16cdf40f`。本次不重复重哈希大型 binary，复用正式 intake 的物理身份闭合并核对小 flags/link 证据。COVERAGE.json 保存全部来源 SHA、每个实际命令、PID、exit、日志 SHA 和源码行。

|关键问题|已有实际证据|结论与边界|
|---|---|---|
|真实 Tag 全 reserved 是否能被观测？|`PRESSURE_ELIGIBLE_on` raw FAIL=4；`PRESSURE_NO_LIVE_RO_on` raw FAIL=15；`T_OFF_on` raw FAIL=15|raw 观测非断线。`gpu-cache.cc:2977–2999`保存 raw；preview 后仍保留原状态。|
|preview MISS 是否掩盖 raw FAIL？|`PRESSURE_ELIGIBLE_on` raw FAIL=4、rewrite MISS=2、commit raw FAIL=2|head-cycle 与 commit 是不同分母，不强行等同。`ep-l2-ro-runtime.inc:263–275`与`gpu-cache.cc:3027–3044`。|
|真实 relieve/eligible/detach 是否连通？|该控制 commit FAIL=2→relieve=2→eligible selected=2→detach calls/success=2；另4个ON控制各成功1次|合计6次真实成功。`ep-l2-ft-cache.inc:325–334`在后续capacity/WAD前调用relieve；`ep-l2-ro-runtime.inc:232–249`保持首个eligible选择；`ep-l2-ro-transactions.h:205–223`完成真实Tag detach。|
|旧返回会不会污染新同地址身份？|`PRESSURE_ELIGIBLE`测试行212–215断言旧Tag消失、旧payload仍live、新generation不同，旧返回后新Tag/新pending保持|真实身份与版本边界已测试。相关控制detach=2、返回packet/response/retire各2；结束前完成真实下游返回。|
|返回及资源是否真正退尽？|所有控制测试行260–264及fixture行77–88断言replies=expected、无pending/descriptor/payload操作、drained；成功数=detached_retired|正向闭环。`ep-l2-ro-transactions.h:248–264,291–303,372–379`为真实fill/response/retire路径。|
|reuse_seen是否真的会阻止选择？|`PRESSURE_STICKY_REUSE` MAIN：首次转换16、raw FAIL15、reuse way exposures240、live-but-noeligible15、detach0；已有16个合并waiter回复|证明reuse保护在合并waiter退尽后仍黏性。地址32子fixture另有1次转换，整个case累计17，不能混成MAIN16。测试196–198；transactions197–207。|
|no_missing负控制是否覆盖压力计数？|`PRESSURE_NO_MISSING`测试201–205断言真实ready+pinned、attached、无reuse、can_detach=false|仅证明真实资格谓词；raw FAIL=0、way_no_missing=0。源已明确不构造all-reserved压力，不能称该pressure分支非零覆盖。|
|T关闭负控制是否全面？|`T_OFF`实际T0M0：pressure_T_disabled=15、detach0|证明frontend T关闭分类；无RO runtime，故relieve_T_disabled、detach_false_T_disabled均未非零覆盖，不能扩称T0M1 runtime拒绝已测。|
|detach成功是否等于trigger接受？|`DETACH_THEN_LATER_DENIAL` MAIN真实detach1、trigger_denied1、capacity denial1；native requester直接access另有directory denial|明确分开；MissQ子fixture真实denied_missq1，address32/M0line子fixture证明正确短路原因。测试141–174,235–237。|
|response_backpressure是否已触发？|`RESPONSE_BACKPRESSURE`真实ICNT满、detached payload已ready仍pinned，之后退尽；其response_backpressure=0|此字段专指`commit_response(false)`（transactions291–299、runtime348–369），不是所有ICNT等待。测试名不等于字段非零。|
|observer是否改变旧路径或重复计数？|16组旧reference/newOFF/newON的cycles/event/state digest、旧RO记录完全一致；PREVIEW_REPEAT行222–234执行32轮preview+snapshot后total不变|支持有界非干涉，不能升级为所有应用性能相同。reference明确链接旧d010 archive，newOFF才是新源关闭observer。|

全部 212 字段存在于保存的ON帧、源绑定schema与发射器，字段类型、selected-slice/phase/global同字段汇总及既有闭合均成立。本次独立读取仅698,534字节保存native日志，完成8,950项小元数据/日志检查，全部通过。113字段在保存ON帧有非零实测，99字段仅有有效零；`samples_dropped=36`另由BOUNDED_OUTPUT的局部observer数据结构断言证明，不属于输出模型总体。每字段的非零控制列表与零-only状态完整记录在COVERAGE.json。

“所有字段都发射且恒等式通过”不能排除未刺激分支的局部断线：若一个未触发分支相关计数一同为零，恒等式仍可成立。异常、closure、identity-mismatch等非法路径也不应为覆盖率而制造成合法运行。现有正负控制对本次已接受应用“有RO、covered raw/commit均无Tag FAIL→没有relieve/detach”的归因已经有针对性支撑；不会因为缺少99字段非零而要求盲跑新应用。

若以后确需更强的分支声明，最小补证仅应是局部、非完整应用控制：

1. 复用真实transaction fixture并连接observer ledger，分别通过真实状态转换建立T0/M1、reused、ready和已detached状态，调用实际can_detach/detach，核对拒绝分类delta及最终退尽。明确这是直接API拒绝，不能冒充production guarded-relieve压力；不伪造no_missing的all-reserved状态。
2. 建立真实ready transaction及bank grant，保留一次未提交response，在下一physical cycle调用现有runtime prepare重试（或明确标记的transaction单元API），核对commit_response(false)计数、没有提前释放descriptor/回复、再次真实读grant与最终exactly-once退尽。

以上均只是方案，本轮未构建或运行。不建议为让212枚举全部非零而增加网格或全应用实验。native fixture的selected SLICE1 / registered cache2使GLOBAL epoch_closed=false，这个已知范围没有冒充64slice完整应用PASS；r3真实失败仍保留，r4仅测试ROP等待修复不改变生产机制。宏观无Tag FAIL也不证明Tags全局充足，TVD等上游未观测路径继续是NA。
