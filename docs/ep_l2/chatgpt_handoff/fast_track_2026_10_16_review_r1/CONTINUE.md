# Lane 1–6续行：从独立模块到生产路径

本文件承接原6c136e2a合同与本目录REVIEW.md，不重发初始启动任务，不重跑已合格的无关测试，不改变WBUF16主配置/8敏感性、同预算、TVD时序或RO语义。所有动作均在原独立lane分支继续；运行中的任务保持不动。

先读取本目录REVIEW.md，再有界fetch所需生产者分支并冻结准确SHA。审阅快照Core 126394be/Framework 37dec04d是公共候选，不是已获独立资格的版本；若已发布更新版本，核实差分与其合同后使用，不reset回旧版，也不把新HEAD自动视作合格。

## Lane 1：保住首个可运行闭环

1. 不停止、不重建正在服务all-OFF资格检查的source/binary；完成已登记vectorAdd/cfd/sad，发布真实等价表和可独立验证的candidate合同。
2. 优先让Lane 5完成B16/U_WB16资格与首批比较，不等TVD、RO、I_READ_HIT齐全。candidate_ready、old_OFF通过、独立合格、正式结果完成分别记录；没有独立资格不开展正式主结果。
3. 发布一次准确公共API/接口差分和可冻结接线父版本给Lane 2/3/4。之后由各lane在自己worktree完成生产adapter和patch，你负责最终应用、冲突协调与组合回归。不要在活跃基线工作树内接入这些patch。
4. 只消费匹配父提交、测试清单和feature向量的最小patch。2/3的独立模块ready不是要求你从零代写全部Tag/memport/响应接线。该分工不改变你作为公共Core最终集成者的权限。

## Lane 2：解除旧ABI等待，完成真实TVD接线补丁

1. 原Core56abbacc和Framework24158d23保持归档。读取Lane 1新共享store/API，不再以4fb91f0a仅有Handle ABI为当前阻塞。
2. 在自己的隔离接线worktree中适配共享allocator/pin/role/sector/Bank接口，不能另外生成WAD地址表或数据阵列。完成真实victim选择、Tag miss的一拍查询、WAD拒绝前的dirty read-forward、response提交、lower_accept/set_done及promotion/epoch钩子。源码改动交最小patch，Lane 1最终合入。
3. 先发布clean真实路径子集，再补dirty，允许滚动独立验证。两部分都须通过真实cache入口和数据/版本参考模型，而非只调用directory类。
4. 修订REVIEW的R1-METRIC：served-sector bytes与净lower/DRAM节省分开；增添同sector多请求合并对照的统计测试。旧字段需要保留时明确deprecated含义。
5. 交付PRODUCTION_ADAPTER_MAP、可apply补丁、实际路径触发计数、定向验证结果及新receipt。不因为正式全局baseline尚未ready就停止独立适配；确有缺失API时指出准确符号、调用点和版本，不泛称依赖未发布。

## Lane 3：完成实际Tag、路由和epoch接线

1. 保留r3、Core ddedbf0f和已完成oracle输入，不重抓trace或重算全部证书。whole_commandlist closed-world scope不变；确认实际启动边界符合证书。
2. 基于Lane 1公开候选在独立worktree补完实际Tag generation/visibility adapter、原始GLOBAL_ACC_R分类、cache/memport lower请求与sector返回路由、L2->ICNT同周期响应提交、epoch加载/结束和独立默认OFF开关。返回旧事务按handle/generation处理，不重新按地址索引detached实例。
3. bypass模式生产merge使用实际attached Tag给出的payload pointer，不能把测试便利的全completion地址扫描悄悄建模成免费硬件CAM。需要保留的常规MSHR索引与模拟观测扫描明确分开。
4. 交付具有生产入口触发证据的最小patch及四模式路径/非法组合回归；exact descriptor共享与部分sector/late-fill/背压作为增量关键检查，不重复所有不变的前处理。
5. 发布请求侧oracle覆盖和运行时RO到达/接收两种分母。FWT空证书按负覆盖保留；正路径canary从证书非空开发负载中选，不为增加coverage改epoch。将新实现字段交Lane 6核算completion实际容量，不按PPA算例缩成128。

## Lane 4：天花板线继续滚动，不等待完整机制

1. 已有活动任务不打断。阶段切换时刷新Lane 1/5合同，旧启动STATUS中的未发布说明不得当作当前事实。核查历史结果复用后发布REUSE_AUDIT的实际状态，只有计划不算结果。
2. 优先完成与B16精确匹配的I_WB、I_META及已授权组合；I_READ_HIT有语义接线困难时保留明确NOT_RUN/问题，不让它阻塞已验证诊断。未合格新B16之前的旧父版pilot只记历史诊断。
3. 与Lane 5复用同run-key baseline和共享配额。理想化与预算内机制分表，不删ordering、不用全read hit代表WB/RO可实现收益。按完成顺序提交准确模式源码和结果，不因尚有另一个模式未完成而等齐。

## Lane 5：现在消费新候选，保留正式门槛

1. 重新读取Lane 1 a23a13b7或更新发布的合同。当前快照已有binary/config与directed_ready，但独立资格未完成。可以做候选输入冻结、生产定向复验和归一化准备，不能用“runtime_ready=false”拒绝独立验证本身；正式runner的INDEPENDENTLY_QUALIFIED门槛保持。
2. 复用registry中已存在的旧/新all-OFF精确匹配任务，检查来源及退尽后消费，不重复发车。整个必要资格闭合后，直接按原合同滚动执行B16/U_WB16开发集，不再为已授权实验等一次人工启动许可。
3. Lane 3旧独立验证57801b42不能替代ddedbf0f及新生产接线。优先验证共享store/Tag/memport差分；Lane 2同理由目录级升级为真实cache路径验证，保留以前PASS的准确版本范围。
4. RO正式输入前版本化扩展feature向量：tag_detach、line_mshr_bypass分开，四组合逐一绑定相应资格；保留已完成B16/WB运行身份，不能为了schema升级重跑同一旧实验。迁移要有明确old->new语义映射，不静默默认新位。
5. 与Lane 2/6对齐served-sector bytes和实际lower/DRAM delta字段。同一请求多次重试不得变成多次流量节省；独立参考模型检验该场景。
6. 共享配额沿用已发布预算并根据实际RSS/活动任务重新核查；不盲增并行，也不因本审阅停止他lane的活跃运行。已合格的单对结果可提前提交给Lane 6，平均值需固定完整集合或明确partial。

## Lane 6：内部材料冻结，开始精简投稿正文

1. r1工作稿与全部来源保留不覆盖，新revision生成精简中文论文稿。先集中写WB数据共享这一最早可验证主线；TVD/RO作为边界清楚的可选扩展，不能提前宣布都有收益。结果未知处保留局部占位，不把整篇写成项目审计报告。
2. 从摘要/引言/机制主文移走用户确认、lane编号、commit/hash、receipt、run registry和大量NOT_RUN管理语言，放在可复现附件/claim map。保留影响科学解释的有限预算、oracle scope、时序假设、对照及局限。
3. PPA分三栏：绑定具体源码的逻辑字段账、明确假设算例、待RTL/工艺验证。T_RO=128、generation等算例不得充当实际开销。先给B16/U_WB16差分，TVD/RO增量分别列，不用未完成FULL阻塞公共部分。
4. 读取cdab5765下DRAFT_FIGURES_CHECKPOINT_r1/plotting_tables/SOURCE_ROWS.csv及其准确CSV/hash，迁移完整13行历史sector检查点，不重新模拟，不把旧12行prefinal误称全量。观察、shadow与新机制结果继续分开。
5. 当前只验证图表可重复生成不等于版面合格；对投稿尺寸做视觉检查与字体/标签检查。复用距离首档保留源码定义的0或<=，不得只改标签为1起点。
6. 仅消费Lane 5/4绑定完整manifest的合格新结果；已验证单个匹配点可以填对应位置，不因其它点缺失而无限等待。不增编性能数字、不把TVD served bytes当DRAM avoided bytes。

## 共同收尾与停止边界

各lane完成后发布新revision、STATUS/RECEIPT及准确远端SHA；非最终性能阶段仍按实际成熟度命名。普通工程修复自行完成并继续；需要改变已定预算/顺序/证书scope等才停止受影响部分报告。所有活动任务结束与否通过真实进程/registry核实，不凭本文件推定。

此更新没有在节点启动、恢复或重启任何进程。已结束的Lane 2/3/5/6可继续原窗口消费本指令；仍在执行的Lane 1/4在自然阶段边界读取，不另开重复任务。
