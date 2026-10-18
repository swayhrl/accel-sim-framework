# Lane3：有限服务机会与匹配效果，首份交付

Goal `EPL2_SERVICE_OPPORTUNITY_AND_MATCHED_EFFECT_V1`；执行Framework `c8aa87bdbe220853eb2d27d8babd448cff02a66e`合同§4。原RO Core30c2920a、参数Core0cde5e90及全部旧review pack保持不变。本revision仅分析、模板和小型算术/导出脚本；没有新Core修改、C++构建、完整应用、常驻监听或Lane2性能任务。

首要结论：MQ2的队头WB/第二项读机会与RG1的retained-grant空转都有源码结构依据，**代表输入中的完整联合触发条件与效果尚未实测**。现有bank/queue累计和5000-cycle窗口不足以补出ready/服务时序。本轮将它们留为“源码可构造、生产见证/应用效果未证实”，没有冒称零机会，也没有从重试总数推算saved GPU stall。

- [机会表与结论范围](OPPORTUNITY_TABLE.md)：已实测、源码可构造、未证实分列；机器可读版本`OPPORTUNITY_TABLE.csv`。
- [已接受raw观测](ACCEPTED_RAW_OBSERVATIONS.md)：generation47、51 accepted catalog、46 finite raw哈希核对；保留正/负/零。
- [已接受四模式背景](FOUR_MODE_CONTEXT.md)：Conv/FWT同combined binary B16/S64/U_CAP16/Unified，避免把共性控制收益说成动态容量独有收益。
- [Lane1最小接口](MINIMAL_OBSERVER_TO_LANE1.md)：二项窗口真实head决策、四类client真实ready、per-bank实际服务及有界见证；待在producer原小case核对，未启动另一个观察工程。
- [Lane5三模式匹配表与结论模板](MATCHED_COMPARISON_AND_CONCLUSION_TEMPLATE.md)：18候选端点和6比较行均为NOT_RUN/null；完整身份、OFF同binary、绝对cycles/提速、EP/static交互及负例保留。
- [English paragraphs](PAPER_PARAGRAPHS_EN.md)：仅证据支持的插入段落，不重建论文母稿。

`derived/`来自独立只读脚本，source/input/config/binary/trace身份完整保留；`SOURCE_AUDIT.json`绑定Core7b8与9bd精确Git blob、行号和excerpt hash。MissQ cycle、lower-WB read及WAD/lower counter块两版相同；arbiter/response/frontend块含P2/Ideal/quota等差异，不声称整段同源码资格继承。实际比较仍按完整binary/source分组。

运行：`python3 util/ep_l2/service_opportunity_v1/derive.py --out <new-directory>`只读当前immutable acceptance；资源按中央lease。`report.py --derived <directory> --out <report-directory>`生成简表；`effects.py --endpoints <template-or-Lane5-reviewed-export> --out <file>`只计算匹配算术，不能授予科学资格。

下一事件：Lane1合法生产小case/精确candidate release，或Lane5当前接受的同源端点。只对该事件短增量更新；先重查撤回与source身份，无结果正常退出，不后台轮询。MQ2/RO/TVD/Ideal资格互不继承，原全应用预算、资源门槛和截止时间保持不变。
