# Source estimates versus physical implementation evidence

审查结论：r5 PPA_LEDGER/COST_MODEL/FIELD_COST_LEDGER没有把sizeof当面积，也没有实测面积/频率/功耗。Core仍c948，故不重复九字段bit计算或六参数场景；以旧精确文件hash绑定保留账，不复制一份几乎不变的账冒充新测量。

| 层级 | 本轮可支持 | 尚不支持/下一证据 |
|---|---|---|
| 预算恒等 |1168×128B=146KiB/slice，64 slices=9.125MiB；共同128B latch=8KiB/chip。WBUF8是不同1160预算 | 同数据字节不证明同面积/功耗/频率；这不是硅测量 |
| 软件字段→候选硬件表示 |P=11；tag/WB handles含G，role/state/masks/pins/owner、预留rollback字段有明确假设。A/G/K/Qb/E未知不能填零 | Gross fields不能全部计作U相对B增量：B也pointerized，共同项应抵消；也不能把all fields都免费抵消。真实编码/基线差分尚缺 |
| 仿真shadow/reference |versions、expected、reference snapshots用于符号sector/requester验证 | 不把std::map/vector/pointer/64-bit cycle/sizeof直接综合为硬件，不把symbolic sidecar当额外data cache；也不能用它代替实际128B数据承载 |
| 逻辑与关键路径 |generation/owner比较、bank-compatible free selection、oldest-ready arbitration、reservation rollback、TVD查找和RO响应检查都有代价 | 有界队列深度、age wrap、fanout、读端口、pipeline阶段、ECC/宏外围/线网未定；软件循环次数不等于门级深度。+1 TVD仿真cycle不是STA通过 |
| WB控制与驻留 |WAD128保持到td；WB-only payload到ta后释放，已计账下层carrier继续持有数据 | 16个static数据位不是控制上限；U不能获无限metadata。carrier必须在实际硬件预算可定位，不能因mem_fetch指针就当免费 |
| 下层队列成本 |原合同L2→DRAM128/slice等是共同队列配置，ta后数据不能消失 | 需要同时驻留的唯一data carrier容量/宽度/队列映射；不要把同一packet途经多个队列重复算多份RAM，也不要假定所有队列只存免费指针。此项仍未形成完整物理账 |
| 增量能量 |只能写Σevents×同工艺宏energy + control/wiring/leakage×time | Native logical op与physical grants不可混用；copy-source/destination精确分类有R6缺口。无宏能量、活动和duration不填节能率 |
| 最终PPA |area_mm2=null，STA_frequency=null，power_mW=null，physical evidence absent | 匹配RTL、SRAM宏、工艺角、约束/clock、综合布局布线/STA与活动模型，才可比较实际面积/时序/能量 |

本账只覆盖WB-only官方候选的源级场景；TVD/RO/Ideal独立分支没有当前整合后完整metadata/端口账。“共享预算”不是扩展零面积，oracle作用域/实现成本须另报告。没有通过r14放宽任何资源门槛或增加硬件预算。
