# 完整方案增量成本：源码声明汇总，非PPA

本表从A/B/C准确发布源码说明和B receipt收集；完整组合尚未冻结，新增字段/比较/索引端口/固定查询延迟与容量共用单列于INCREMENTAL_COSTS.csv。C有RO packet逻辑区分位，B声称0新增packet身份位只适用于victim，不代表完整F也为0。

付费数据149504B/slice、共同目录128、D512各计一次。A目录两条CAM路径（frontend及completion）和三个indexed read/update视图不是免费软件map。RO额外有每slice每物理周期一查询、ready+1及有界比较/响应选择。二者如何整合、转发和仲裁仍待A冻结；不预言组合时钟或吞吐。dirty与fixed各源中可用不推出fixed+dirty+RO可用。

4224bit目录UID/flag和65536bit Tag generation是根据源码声明的独立逻辑尺寸示例，不是相对最终S的总增量；重用、位宽裁剪、共享字段、valid位/编码/端口/线网会影响实现，不能相加冒充完整设计总面积。C waiter仅保留D512句柄，不能再算第二个request-pointer/sector-mask池。offline SQLite体积不是硬件存储。

旧WB-only R3 RTL/DC面积与时序保持旧scope，绝不用于完整W+V+R方案PPA。完整F面积、关键路径、ABI尺寸和实测端口利用率目前UNKNOWN；没有启动RTL综合或native测试。成本需求已单次交A/B/C，后续仅按新准确交付增量更新。

收到A V2 r6最新公共前像eb6739、Framework957321a0后补充：符合L2条件的Tag miss先付TVD一周期，未命中再付RO查询一周期，可能串行增加两次查询时延。TVD服务的请求只记一次接受，不额外分配RO descriptor/landing，不再做RO查询。writer资格必须在TVD消费前检查。该共同接口仍是源码合同，角色枚举冲突等组合适配/native验证尚待完成；没有测得组合时序。当前FT1的F−W确实为DEPENDENT_CONTROL_UNSUPPORTED，不以S替代。
