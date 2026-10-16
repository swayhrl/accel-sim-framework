# EP-L2 review_r3｜生产资格撤回后的恢复与并行收敛
日期：2026-10-16。原科学合同：6c136e2a56a008695f8c8b815723bf8f1a760db9。本审阅只更新科学证据的使用资格与执行优先级，不改变WBUF16/8、1168/1160、4 bank、RO oracle、TVD+1cycle等架构合同。GitHub本次发布不等于服务器上任何任务已开始/完成。

## 0. 核心裁定（优先于此前reviews）

**撤销此前所有R0和R1在真实应用层面的科学资格，直到使用修复的新source/binary、真实生产路径测试和独立资格重新获取。** 原文件和完成终态不删除，但COMPLETE_VALID仅表明当时执行正常退出和旧合同不变量，不能覆盖后来发现的物理端口违反或预热身份缺失。

Lane5 authoritative evidence：
- Framework publication b134f76d8f4cd759c0852b68edf922ecbd445ea9
- docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/STATUS.md、APPLICATION_ACCEPTANCE.json、VALIDATION_MATRIX.json
- docs/ep_l2/review_packs/FT20261016_LANE5_MEMCPY_CLOCK_CORRECTION_r1/
- docs/ep_l2/review_packs/FT20261016_LANE5_WARMUP_IDENTITY_CANDIDATE_r2/

已执行旧R0 B16/U_WB16六次（sad、vectorAdd_4M、cfd_097k各两次），原始数据可核对但科学状态统一SUSPENDED_MEMCPY_PHYSICAL_CLOCK；convolutionSeparable与FWT两个配对（4 run）未启动。不能拿旧R0的任何数做正式速度、平均值或“无容量收益”的定论；Lane6 r2的sad 110593→110573 cycles图、章节与资格文字必须在新revision主动撤回，不覆盖旧revision。

旧R1拥有此前独立fixture资格但无新B16应用结果；其应用资格也需重新获取。Lane4旧静态模型vectorAdd I_READ_HIT的73873→42918 (1.721259x)仍仅作为旧静态系统的乐观读路径历史诊断，未自动被此次FT bank缺陷证伪，也不是R0/R1新理想数据。

## 1. 缺陷事实、修复成熟度与额外审查

### A：真实物理bank时间错误（已实测且时钟修复增量通过）

真实force_l2_tag_update累积memcpy offset 4096的生产partition试验显示：B16有124次、U_WB16有15次同一bank同一物理cycle grant>1；最大2次/周期；offset0没有违规。原因：native Tag replacement time含m_memcpy_cycle_offset合法用于Tag先后次序，却被FT bank arbiter和WB/WAD lifetime错作物理GPU时间，同一个物理cycle的状态被不恰当地清零。只看终态退尽捕捉不到这一点。

Core clock-only增量1565f1f04978f12e51a29fcbf9dab9a3c61b5c4e已通过4模式×offset相关的物理grant检查，源Core/port回归、WBUF8/16分区定向，保持Tag原timestamp，FT改用physical GPU cycle，加monotonic断言。它是合格的时钟修复增量，不是已资格通过的新完整application binary。

### B：untimed host prefill建立Tag但没有FT payload owner（未编译）

真实warm-hit命中触发旧R0 owner断言。Lane5已交付Core832d986b03dc3c940eb99a1ae6845dd07297f4ed候选、独立warmup delta5d974c3bf116ad21da74d3a27eace028c1f2e197和R0/R1最小patch应用检查；新候选force_tag_access拟给warming Tag在同一唯一allocator创建/复用resident句柄，维护bank class及32B sector的symbolic version-zero，禁止丢失pending/WAD/pin。**尚未编译、未通过实际warmup功能测试、未获资格**；patch apply PASS并不等于运行PASS。

额外必须审核：warmup原有Tag victim是否dirty、同line多sector重置、重复预热、已活跃owner复用、memcpy在epoch边界、Tag实际chosen index是否和预留slot一致，及预热线立即读、后续WB/eviction、full drain。禁止靠关闭owner assert或假设SASS包含数值数据过关。若设计仅支持先于kernel的host初始化，明确拒绝其它未覆盖情形，不扩大默认输入语义。

### C：空间hold是workspace磁盘，不是内存

Lane5最后资源记录workspace disk free=50,802,106,368 bytes≈47.313GiB，硬门槛48GiB=51,539,607,552 bytes，缺约737,501,184bytes≈0.687GiB；同时记录可用内存高于64GiB要求。三次构建admission被disk floor拒绝，编译器未启动；已做的归档与hardlink节省逻辑文件大小但还未达到真实文件系统门槛。

恢复策略：先在registry锁下核对最新df、fs路径、活跃任务及Lane-owned空间；优先将**可确定重建的本lane非活动编译临时文件/对象缓存**迁往经验证的其它文件系统或在校验保留可重建来源后清理，用有限预算恢复实际workspace空闲空间；严禁移动或删除冻结run raw、配置、CSV、原始trace、唯一二进制、审计资产、他人项目文件。保留清理前后的sha/path/inode/df receipt。若无法安全恢复空间，继续RESOURCE_HOLD，并报告可安全释放候选和实际门槛，绝不擅降48GiB；越过门槛时还应预留实测构建增量，避免刚过48便将磁盘写满。不能以“后台会继续”掩盖已停止。

## 2. 六lane阶段性审查

| Lane | Framework报告SHA | Core/生产SHA | r3成熟度 |
|---|---|---|---|
| 1 | eb5a42d89e49e19f8cca5a0ebcd9c55d740f42c6 | R1 be651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de；R0 126394be... | 原R0/R1冻结证据保留，应用资格撤回；Lane1是修复R0.1/R1.1唯一官方集成者 |
| 2 | e1df2b71d8e28344d24cabf479a04b48fc0e8180 | c197c14d8292e8c2aa522711f4125ed5624b5549 | TVD真实生产接线＋12组定向/3非法拒绝；未有多slice应用资格或性能 |
| 3 | 0db7ce4bcc91db96860e5e18f0c88178f25dc562 | ac3028b00aa37c08b2210b1c9a1fe8444060c0f9 | RO真实Tag、lower、epoch接线＋定向验证；未有独立实际应用资格/性能 |
| 4 | be21c95d9c846c9af0904d24c78c10c3243dc64b | b8b3d55b392fcff793d0aec684bddb73ba3065a9（候选） | R1最小patch与绑定测试已交付，旧B16正式ideal18格仍NOT_RUN，必须对修复版R1.1重新归一化 |
| 5 | b134f76d8f4cd759c0852b68edf922ecbd445ea9 | clock-only 1565f1f...已测试；warmup 832d986...未编译 | 科学撤回权威，当前无活动run；受48GiB workspace disk floor限制 |
| 6 | 6a3c00cb17aaff2a2c23c5990e7ef90f294aa8df | 无Core | r2文字/图生成和PPA账可复用，但sad图及“已独立合格”文字必须由新revision撤回 |

Lane2、3的定向测试遵守各自已声明scope，不能因为已拥有真实生产caller就推断完整应用可接入新修复版本；也不能因为R0 bank bug推断它们独立模块测试全部无效。Lane2真实matched directed lower reads 2→1包、64→32字节，仅是该定向输入的L2下层读请求变化，不是DRAM流量/系统收益。Lane3闭世界oracle作用域、FWT空证书不变。

## 3. 科学数据消费的撤回优先级

优先级：**较新明确的科学supersession/撤回记录 > 原历史release资格文件 > 原run终态。** 保留旧的INDEPENDENTLY_QUALIFIED.json以证明当时门槛，但论文/正式表的consumer必须同时引入Lane5最新发布的APPLICATION_ACCEPTANCE（或其后续可验证新revision），检查原run_key/core/Framework/binary/config/trace对应的当前科学资格。过期/缺失/不匹配→fail closed，不得因历史qualification文件不可变就让已撤回pair再次被绘图。

新R0.1的每条run使用新Core/Framework/binary身份、新run_key、新结果目录和新资格；旧6次结果**只可作开发诊断或修复对照**。不要修改旧run的COMPLETE_VALID，因为那是旧执行终态事实；另记SCIENTIFIC_ACCEPTANCE_SUSPENDED。

Lane6 r2可作为历史论文工作稿存档，但其formal_sad/WB_PAIRS及§5.1“已经独立合格”、§6“首个配对结果”不可继续作为当前学术结果。下一版脚本必须有explicit acceptance supersession gate；同一状态一致后才能产生主性能图和汇总。对新的修复版R0.1也不得自动沿用r2 NATIVE_SAD_ADAPTER指向旧r0 paths。

## 4. 当前收敛次序（不串行等待全文重做）

1. **Lane5+Lane1抢先解决磁盘/修复验证：**Lane5资源审计与受控恢复；Lane1从Lane5源码补丁在隔离分支集成clock+warmup，单次最小实际编译、定向验证、冻结R0.1。Lane5对精确R0.1做独立复核，不必双窗口各做一次昂贵全编译。
2. **修复R0.1资格→立刻新身份五负载B16/U_WB16：**先小型生产canary（包括offset非零和实际预热），再恢复正式五点；sad/vectorAdd/cfd虽曾运行，但旧数据不能作为合格结果复用，必须新run_key。至少在结果里区分bank/copy消除与容量借用，没有容量借用时不能声称容量收益。
3. **R1.1诊断与Lane4：**用同样修复增量应用于不同R1源码，在独立build/结果目录生成R1.1 binary；Lane5提供精确R1.1 B16 baseline资格与run specs，Lane4滚动正式ideal，不用旧R0/R1。
4. **Lane2/3在各自分支适配新的repair-base，**保留现有producer测试，提交delta和冲突审计。Lane1根据精确父版本先后集成新TVD/RO分支，Lane5只在新应用版本通过独立资格后分配正式任务。绝不让R2/R3覆盖R0.1二进制。
5. **Lane6立即纠正证据使用和稿件：**这不依赖磁盘/模拟器，先发表r3撤回旧正式sad图与独立资格措辞，保留结构、PPA和历史理想化分析；加入自动拒绝已撤回release的验收测试。新应用验证后再填入结果。

## 5. 不做的事

不重新讨论已经确定的EP-L2架构，不把它退回机会研究阶段；不调WBUF16主配置/8敏感性、不增加缓存银行/端口或偷偷扩大物理储存。不能以降低磁盘安全门槛为“解决资源问题”，不能停止其它项目进程或清空原raw历史。未取得新资格前不以R0中的低加速或负加速决定放弃机制，也不拿旧静态I_READ_HIT 1.721×代替R0.1上限。

本次GitHub协调修订是ChatGPT审阅授权与消费者规则，不是对任何运行的实测复核。正式验收仍以Lane5更新证据为准。
