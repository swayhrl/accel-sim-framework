# V6｜Lane B最终资格审查及主实验科学适用性风险（2026-10-16）
 
**已核对来源：** Hotspot资格`0bd0e603f48a93414c47583b7c205595600e72af`，其他三个负载风险`266a8e375eb21552774956222208848d5902f37a`，Lane A当前已提交`5419e60cd5bd3668b58560ebd4fc0a49baf7c7d2`，其R2检查点`2026-10-16 12:28 UTC`。**此文为审查建议和已发布状态，非用户对新输入/新实验的正式授权。** 保留V1—V5，原174执行分支、RUNNING和全部HOLD均未改变。

## Hotspot：候选资格与科学准入是两个门槛

- 接受`DERIVED_INPUT_QUALIFICATION_CANDIDATE`的**CPU来源模型资格**：185个PC的opcode-root/GPR签名、16,950,260条显式shared+3,720,992条显式global load地址与独立源模型吻合。隔离规范化只改变6个PC、122,760行、2,944,024个活动lane地址。
- 保留精确输入身份：原member SHA `ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8`；新候选member SHA `21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985`；bundle `dd0da35f5a3e3a2467a1cd23a53ce3966cd7eb6ee31035733e26f48dc532c169`。
- **仍不能证明**精确历史ELF、tracer/JIT、predicate/immediate、输入temp/power与native输出等价。2,897,648个改变的shared活动地址依赖重建SASS/源码，compressed bytes本身不唯一恢复E mask；原full32向量在历史E-list合同下支持2,728行LDG修复。
- **推荐待用户明确批准**后进入新lineage`HOTSPOT_SOURCE_PROFILE_RECONSTRUCTION_V2`的Lane A输入准入预检。批准条件：原输入和全部结果冻结，新SHA/list/完整scope+source identity+opcode/width/地址准入审查通过；新旧输入任何结果不混算。最小B16-N/IO/OO同新输入配对，TC80/TRAD96/IO128/WAIT128按最终claim是否使用决定。新输入运行必须作为新immutable attempts，不改原44行。
- 不因原始ELF缺失而无限寻找，也不把假设称原生硬件真实性。原Hotspot三条禁运行行维持HOLD直到明确的新输入/新授权和独立准入。

## Btree、2DConvolution、LUD：应及时升级审稿风险

| 应用 | 条件性输入风险 | 论文行动建议 |
|---|---|---|
| Btree | 6000条LDG.E.SYS mode0的32地址列表，5792条在历史E-list关联下改变sector/line **identity**（单条引用数仍1） | 优先单PC获取采集来源规则；这是DTC已测显著收益负载，**不宜未经核实直接作为最终加速证据** |
| 2DConvolution | 40940条mode1，36846条cacheable LDG；其中12282条global-load可能改变sector/line **count** | 优先确定tracer V3编码修复前后合同；源模型必要时仅限单kernel十PC；该负载既有强收益不能自动推广 |
| LUD | 57536条mode1含11904 cacheable LDG、7936 STG、37696 shared；5760条LDG可能改变line count；共享bank单条服务在已审参考几何下不变 | 先追global路径与两个kernel E-mask锚点，不以shared service相等代替完整语义等价 |

**建议只在独立科学证据表标`FORMAT_APPLICABILITY_REVIEW_PENDING`**，保留原`terminal_validation=PASS`及运行中程序；这不是用户已授权的Lane A调度HOLD，也不是宣布全部原结果错误。其余8负载本次仅未发现所查格式机制的活动地址风险，不能称“所有输入native正确性完全证明”。

尤其需要防止发表未经限定的12负载GM：Hotspot即使新派生准入，Btree、2DConvolution和LUD仍独立OPEN。若最终无法消除歧义，可展示清楚限定的原模型指标和另行定义的格式风险过滤集合，不得把删负载后的GM仍称GM12，也不得按加速好坏选择负载。

## Lane A与效率

最近Lane A `5419e60cd5bd3668b58560ebd4fc0a49baf7c7d2` 报告R2注册44行中30 terminal/invariant PASS、11 LIVE、3 original Hotspot ADMISSION_HOLD；**0 eligible unstarted**；无重复或重启。BICG OO128 47,533,116 cycles 对TRAD96 25,353,488 cycles的负结果保留，另有7个主三臂完整。以上为固定旧解码器下的严格执行检查，不能免除新科学格式适用性风险。主窗口只需自然terminal/严格验证/报告，不为新的输入歧义杀死任何旧作业。

Lane B的候选调查已完成，本轮下一科学决定为：(1)是否允许Hotspot作为独立派生输入尝试新配对；(2)是否在科学采纳层面暂缓Btree/2D/LUD结论并安排最小CPU-only来源绑定；(3)如果后续确需对这些输入派生修订，是否由用户另行批准新source/attempt合同。C、D现代NO_GO无需重启。

## 实验登记（提要）

| 项目 | 目前已公布状态 | 处理 |
|---|---|---|
| 固定44主R2 | 30 exec PASS,11 LIVE,3 held | 保持Lane A调度不变、strict验收 |
| Hotspot V2 | CPU资格完成，科学准入待用户决定 | 不启动 |
| Btree | 高优先级地址关联风险OPEN | CPU-only单PC溯源优先 |
| 2DConvolution | 高优先级tracer V3合同风险OPEN | CPU-only producer辨别优先 |
| LUD | 高优先级执行锚点风险OPEN | 先global paths |
| 现代4080 DTC、SpMV仿真 | 原NO_GO不变 | 不扩工程 |
| 面积/时序 | 仍待实际硬件证据 | 论文主成本约束 |

**不授予新仿真、修订parser、静默替换输入或更改A的科学合同权限。**
