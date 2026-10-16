# A：原174主窗口续接，不新建Goal

继续`DTC_SERVICE_AND_MODERN_BASELINE_CLOSURE_174_V1`。先完整阅读本目录README及当前execution分支最新报告；这份文档不要求reset、重编正在使用的binary、替换协调器或重启任何模拟。读取主分支新commit，而非强行退回e3dbe3db。

## 保持科学边界

保留44行原注册及已创建attempt。Hotspot的TRAD96、IO128、WAIT128三条保持launch HOLD；所有旧/新Hotspot数值保留原terminal/invariant状态，同时标注shared-format scientific HOLD，包括其B16-N/TC80-N分母和4080 baseline。不能因共享指令不直接进入DTC就说影响会抵消。其余输入未发现同类稀疏mask模式1记录，可以按原范围继续；不以此认定全部指令语义均已验证。

只有B提交足以唯一确定语义的来源和候选后，才准备局部correction计划：影响哪些trace、哪些设计参照、是否改变Framework/binary身份、哪些旧行可证等价。需要改变实际地址解释时先科学审查，不自动解除HOLD。保留四类状态：原结果、受影响但未更正、候选更正、正式更正。

## 单一调度与高效补位

当前scope协调器拥有唯一launch authority；旧协调器已被token禁止启动，不杀它也不新建第三个协调器。分发给辅助窗口的是问题，不是主44行的第二份启动清单。若将来委托某个执行进程，必须由主调度者唯一占有row key并发放任务，不能各窗口各自扫描待运行行。

1. 不同arm只依赖各自已通过的有效pilot；Btree三arm已通过，不等全部四pilot。Hotspot不再用于扩大资格。
2. 槽位释放后，优先使关键慢行与其配对参照早开；GESUMMV已运行不重复。已有两个heavy在跑时，用轻量主行或Btree/2D的IO128、WAIT128填剩余槽。
3. 机制控制以对应非HOLD输入的IO/OO已验证为准；主OO128结果直接复用。不能等完整cohort才开始控制，也不新增深度扫参。
4. 原terminal只有receipt缺失时恢复/核验receipt，不重跑。已有baseline确证兼容时复用；新地址或服务语义变更不能靠OFF某个小测试概括成全输入等价。
5. 发现fail时按source/输入作用域暂停受影响后续启动，系统性正确性问题仍须停止相应Core/contract；不能把所有失败都当成可忽略局部问题。

在现有launch器可安全配置的范围内，用实测CPU/RSS/换页和单位时间完成进度评估8→12→16；不要为升并发再重构调度器。主仿真优先于辅助全量编译。将对当前已运行程序的监视和验证继续流水化，避免主Codex陷入历史格式搜寻而放空工作队列。

## 接收辅助交付

B写`review_packs/DTC_HOTSPOT_FORMAT_CLOSURE_V1/`；C写`review_packs/DTC_MODERN_LAYOUT_PROPOSAL_V1/`；D写`review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/`。各自只写独立分支；接收immutable commit单次fetch，核范围后集成或报告具体决策问题。不能从文件名PASS推断输入已准入。辅助未交付时继续独立已授权任务，不做无限轮询。

发布检查点时同时给：注册总量、terminal通过且可用范围、terminal通过但scientific HOLD、运行、未启动、admission HOLD、可比配对及失败索引；没有完整/合法12项就不生成GM12。主论文同资源收益与原生现代相关性分开。当前8运行与检查点变化如实更新，不凭旧报告断言实时数量。
