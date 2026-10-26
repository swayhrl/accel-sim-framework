# 最小受控实验与被动计数计划

追加研究 `MEMORY_PATH_MLP_AND_BOTTLENECK_ATTRIBUTION_V1`。状态：**DESIGN_ONLY / NOT_EXECUTED / NOT_SCHEDULED**。本轮不运行模拟、不编译、不消费已耗尽epoch2预算、不重新采集4080 trace、不操作SM70资产迁移或GPU109采集。

## 先用现有证据能做出的决定

[访存路径图](GPU_MEMORY_PATH_BOTTLENECK_MAP.md)已足以否定“Tag没满就代表全GPU没有MLP”以及“TLB或真实NoC带宽已证限制”的说法。Vector存在后端scheduler/full、L1/L2queue反压、core RAW-ready症状，但没有足够的独立控制确定其可减少cycles的排序。CFD/DWT全路径raw本轮本地不可用，不能依据Vector补写其瓶颈。

本轮实际执行的是有界离线脚本 [audit_memory_path_evidence.py](audit_memory_path_evidence.py)，读取已接受Vector r5、独立迁移Q2的raw及身份文件，SHA验证、最后累计快照去重、64slice/32channel闭合、范围及联合数据复核通过（最后0.202s，单CPU、nice10、30s timeout）。这不是新科学接受或完整应用启动。原Tag detach正确性fixtures仍仅阅读历史记录。

在考虑新应用前，CFD/DWT如需补齐原raw，应先形成明确COPY_ONLY取回清单、SHA和本地存储准入；不能因历史restore receipt就声称raw现存，也不自动跨远程存储搜索、恢复或干预当前搬运任务。

## 最小被动计数补充：先设计，不改生产

应只捕获真实现有决策点已计算的结果，不额外调用probe、CAM、reserve、bank-grant或query。计数器不能参与任何资源准入返回值。

|缺口|最小字段/人口|捕获位置|有界输出|
|---|---|---|---|
|SM是否限制内存产生|mem instruction valid/ready/issued，RAW、ibuffer、MEM-pipe拒绝分别计数；warp与lane单位分开|真实scheduler现有判定后|SM或scheduler累计；有界phase，不打印每指令|
|L1到ICNT|offered/accepted/denied，同line merge/newlower、bank/latency/MissQ原因；actual outstanding及高水位|真实L1 lookup/queue/inject结果|每SM histogram；不把重试变unique请求|
|ICNT到L2|实际head offered/pop/admit/deny，packet与bytes各列；ingress full且无head另列|已有ICNT pop与L2 full判定|每subpartition/window累计，不新增窥探影响仲裁|
|L2新Tag vs已有Tag sector miss|newTag request offered、actual allocation、sector miss、merge、rawFAIL；preview pass与commit accept分列|现有probe/commit结果|slice×set；重试计数与unique UID分开|
|RESERVED寿命|Tag generation＋reservation episode的enter/exit；区分新分配与existingTag重新RESERVED；退出原因ready/detach/retire/其它|现有Tag状态更新与generation路径|每slice×set occupancy histogram、episode count、sum/max/log2 lifetime；首尾carry-in/out明确|
|RO事务关联|attached/reuse/required/issued/ready、same-set eligible、lower-pending/response-only段|真实admit/merge/loweraccept/fill/response动作|有界aggregate，先不扩出永久逐事件trace|
|下游完成|DRAM接受/成功issue/完成/return，read sector与writeback line分列；scheduler/credit/return互斥和联合原因|既有lower尝试与真实完成点|channel/subpartition有界累计，明确clock domain|

64slice×64set×17 occupancy bins用uint64约544KiB，一个额外64bin lifetime histogram约2MiB；按精确设计核算固定上限，不能借估算无限扩容。若要增加更多phase/联合维度，先冻结内存/输出cap与溢出失效策略。本轮没有分配这些新模型资源，也没有改现有预算。

对固定set的Little Law验证，必须有同一人口的reservation episode到达、生命周期和时间occupancy；existingTag sector miss会重新进入RESERVED，不能只用newTag arrival替代全部episode。输出tick末观测与tick内部事件各自界定，不把全GPU平均延迟代入。

## 被动观察器非干扰性检查：待执行的定向fixture

若未来独立授权实现计数，先在独立开发区完成，accepted simulator保持原样：

1. 同精确源、trace/config、资源值下，observer OFF/ON比较cycles、instructions、真实bank/queue/packet序列摘要、原计数及终态drain；observer只能记录，不能改变cache行为或发射节奏。
2. 同physical cycle重复preview32次，Tag/generation、payload/masks/pins、transaction/reuse、descriptor、queues、bank调度及全部observer累计snapshot完全相同。不能只检查head counter不增。
3. 定向覆盖newTag、existingTag sector miss、same-line merge、all16 pressure、T-OFF、noeligible、sticky reuse、早期query/directory/WAD拒绝、preview-pass/commit-deny、分sector返回、ICNT背压及最终drain。
4. 小计数cap/overflow/输出截断必须显式INVALID；NA/unknown不填0；无未完成scope回退到早期“好看”快照。
5. 对Bank_Level_Parallism_Col的疑似初始化问题，如另做工程修复，先写计数生命周期/16banks上界fixture和reset验证，给新Core身份；旧raw保留并继续剔除无效指标。不自动将修复并入accepted source。

本轮上述fixture均未编写或执行。未来CPU验证也需先核验资源/权限、既有ELF/source/archive，单进程有界运行，不以CPUfixture资格代替新完整应用native资格。

## 下一轮最值得的一至两项实验：单因素、顺序决策

两项都保持T、M、W、V和保护条件不变，不以非零detach作为成功标准。不形成当前预算请求或自动启动。

### E1：DRAM域服务敏感性（优先）

问题：后端服务改变是否会减少Vector端到端cycles，并同步缓解下游至上游反压？

最小对照：同一冻结输入、同一精确binary、相同config，唯一改变DRAM clock由850MHz到预注册935MHz（+10%）；core/ICNT/L2保持1132MHz，buswidth、burst、timing参数的cycle值、scheduler/queue容量均保持。这是**DRAM域整体服务缩放**，同时改变命令时序的物理时间和理论字节容量，不能宣称分离出纯带宽贡献。若该解释不符合研究问题，应先重新冻结规格，而不是执行后改口。

观察：end-to-end cycles/instructions/drain、真实DRAM bytes及新clock对应容量、scheduler occupancy/full、C7E causal拒绝、L2 ingress full、L1 MissQ重试、每set reservation histogram/lifetime与真实TagFAIL/relieve/detach。没有新计数时只能使用既有C7D全set峰与r5联合，不声称补出寿命。

判据：cycles与队列压力协同改善支持后端DRAM域敏感；只队列/latency变化而cycles不变是应保留的负结果，说明等待转移或其它瓶颈。若Tag压力反而下降，正是更快服务缩短pending的可检验现象，不是实验失败。任何非零detach也只属扰动条件，不回写原始应用收益。

### E2：L1 MissQ容量单因素（条件性第二项）

问题：L1 MissQ重试是否为可独立改善吞吐的上游限制，还是下游反压的表征？

最小对照：同baseline trace/config/binary，唯一改变精确L1 MissQ容量16→32，保持L1 banks4、latency20、MSHR512/merge8、cache容量/策略、ICNT、L2、DRAM、T/M全不变。配置字符串必须只更改MissQ字段，读取actual option回显核验，不能顺手扩L1 MSHR或更换替换策略。

观察同E1，另看L1 actual outstanding/高水位、offered/accepted/denied。若重试降低但cycles不变且下游queue更满，接受为瓶颈迁移负结果；若到达L2的新line更快但set峰仍低，支持空间分布/合并的限制，不据此继续扫描容量以制造detach。

先完成E1的结果判断，再决定E2是否仍有信息价值。E2必须对照共同baseline，不与E1叠加后称单因素。

## 精确执行和授权边界

基线与两个对照必须同一binary；若新增被动计数导致binary变化，先做该新binary的baseline及非干扰资格，不能把旧r5既有运行冒充新binary baseline。最少设计是baseline＋E1，E2条件性追加；这里没有授予2次或3次启动预算。

CFD/DWT先补原始统计可用性，再决定是否复用相同问题，不能自动扩成三应用矩阵。新spec/cohort、entry admission、resource cap、native qualification、fresh scoped budget和结果归档/接受需独立授权；当前epoch2余额0不变。保留全部负结果，不改变旧失败/HOLD或accepted assets，不接触SM70迁移、4080采集或GPU109。

## 论文当前解释与统一决定

建议表述：

> EP-L2的定向测试证明了Tag detach的条件性功能。已接受应用诊断没有出现真实Tag分配失败；Vector同时存在显著下游排队、上游反压与较高slice级并发，但pending Tag分散于多个set，未达到16路不可替换条件。因此目前不能将EP-L2整体性能变化归因于T，也不能将零触发解释为TLB瓶颈或全GPU缺乏MLP。

统一决定仍为**维持现有T**。未来优先检验DRAM域服务及L1 queue的端到端敏感性，随后才判断是否值得扩大T研究；没有为获取非零detach而改保护条件或扫描参数。
