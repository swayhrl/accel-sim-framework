# EP-L2第二轮统一审阅（2026-10-16）

本次新增审查用户新报告的Lane 1和Lane 4，回读两条精确Framework发布SHA及release/ideal包的合同、源码地图、CSV，并继承上一轮对Lane 2/3/5/6的有限范围审阅。未在174启动任何程序，未替代Lane 5的独立验证。本次审阅是阶段审查，而非六lane全部进度的实时快照。

## 1. 优先级和过时指令处理

原科学/机制/资源合同仍为Framework协调提交6c136e2a56a008695f8c8b815723bf8f1a760db9。上一轮协调审阅提交c2f195019cdb1ec9540fd6e0c2245e4760ce8a2e中的REVIEW.md可以作为归档研究意见，但用户尚未向Codex下发其CONTINUE.md；本目录CONTINUE.md是这次统一下发的唯一续行指令，取代旧CONTINUE.md的执行状态描述。不要连续执行两套指令、重复跑老任务。

**首要链条：Lane 5消费冻结Lane 1 R0 -> 独立资格通过 -> 立即滚动B16_BANKED/U_WB16五点配对性能；不等Lane 2/3/4/6。** Lane 4的ideal patch并行建立R1诊断源码，不修改/覆盖R0 binary，不迫使R0主实验等ideal注册。

## 2. 本轮确切状态

### Lane 1生产者release：通过阶段审阅、未授予独立科学资格

Framework发布：02982b65e87f170103b44c6dbd562a8ffb03841e。
Core生产：126394be46b15f55b9756d43eb9ca9a9baae1c84。
Framework生产：37dec04d223ae65167c5584e56887c74f6540d27。
immutable release binary SHA256：0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698。

已回读Lane1 BASELINE_CONTRACT_V1.json：runtime_ready=true、directed_ready=true、independent_qualification=false。旧、新三个全OFF完整应用互相比对（vectorAdd_4M 73873；cfd_097k 81443；sad 110653 cycles）及instructions、7科学CSV均byte-identical；新旧对照又与历史基线相符。Producer声明12组生产directed、四个非法组合拒绝、八项解析测试及有界真实WB场景通过。此处认可对应review pack的阶段证据，不是我重新运行全部测试。

尚无正式B16/U_WB16应用结果或性能结论。不能将有限WB定向压力测试中unified peak 126解释成真实应用借用126项、也不能将OLD_D512_STATIC与新B16不同存储/端口模型的cycles作机制加速比。

已记账：B16/U_WB16同为1168个128B数据项/片、4x292 single op/bank/cycle，此外共有同预算128B/copy-pipeline-latch，独立于Payload主阵列并在B/U两侧一致（不视作可借数据项）。新static真实copy需source read、destination write及lower-send read；Unified原位WB避免copy但保留lower-send。B16相对OLD 1152项新增预算且bank排布不同，不是可直接混算的基线。真实SASS缺数值payload；使用独立sector版本与请求身份闭合来声明模型内正确性，不虚构full-byte/atomic数值验收。

本轮结论：**PRODUCER_READY_FOR_INDEPENDENT_VALIDATION**。Lane1自己的active_runs=[]；Lane 5在实际节点必须重新确认registry/进程后再启动。

### Lane 4理想化diagnostic：实现/历史pilot接收，新B16天花板未完成

Framework发布：96fbcb612773900fd75268ffe4e00ed9f13d3d42。
Core生产：b8b3d55b392fcff793d0aec684bddb73ba3065a9。
Framework生产：438df99dd5138ec42acd7ae9d05e76b9b01e2e5e。
Candidate binary SHA256：63f26de29e2b1932062934044cb3131fa5e2d36fa9821094939188bceb66a8ea。
其Core基于Lane 1准确父提交126394be46b15f55b9756d43eb9ca9a9baae1c84的最小补丁，不是另立物理设计。
已实现default-OFF I_WB、I_META、I_READ_HIT、I_WB_META；测试汇总记录12次生产C++、6非法配置、16 parser、3次完整应用运行。最新候选all-OFF历史vectorAdd的cycles/instructions/7 CSV仍等价。已回读CEILING_RESULTS.csv：OLD_D512_STATIC vectorAdd OFF 73873, I_READ_HIT 42918 cycles、均56000000 instructions，speedup=1.721259x。理想读参考移除真实读DRAM流量及相应下层排队，不是B16、不是EP-L2可实现性能，更非严格数学上界；dataless SASS不能证明完整数值输出。
正式B16首批18格均NOT_RUN，不能以零或同SHA混用旧静态行填入。Lane4自己active_runs=[]，不重发初始Goal。其接口集成需要与Lane5资格区分：补丁虽然默认OFF，仍产生不同Core/Framework与binary身份，R0 B16结果不能当成R1逐位匹配baseline。

### 其他四条Lane：继承上一轮review的版本范围

- Lane 2 Framework 24158d2344d086d2ff3d6ba31d1099682aac8e9d/Core 56abbacc1192d68995e78561899719649f838079：clean/dirty目录模块测试通过，不等于实际l2_cache生产路由。统计响应服务扇区字节≠DRAM节省字节，R1-METRIC仍待修订。
- Lane 3 Framework bfa193e76873ebf39ce5262483f4828f833dbc3d/Core ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5：RO oracle和共享store适配模块已交付，actual Tag/memport/epoch/开关未闭环；whole_commandlist closed-world作用域保留。FWT的空RO证书为有效负覆盖结果。
- Lane 5 Framework c603a5634b6b3f54aec10bdb1fc804e0a648b567：工具、配额、旧版模块独立验证已完成；其报告在Lane1 release前，runtime_ready=false的阻塞现已解除，不代表独立资格自动PASS；新B16主实验仍应由它主导。先前Lane3独立Core57801b42的PASS不覆盖ddedbf0f共享store适配及生产接线。
- Lane 6 Framework c6548bff73572f12f4b2abef8ba800e502f07ec1：中文工作稿、PPA bit ledger与图表脚本阶段交付；无新应用性能。T_RO=128仅算例，真实RO completion槽应映射实现容量；精简论文正文，13行Streaming历史check-point可核验后使用。

以上四个SHA是上一轮回读时的快照；开始新工作时必须有界fetch更新，不用旧head代替实际消费版本。

## 3. 必须执行的三道科学边界

1. **独立资格在先，但不堵资格测试本身**：Lane5可以立即验证Lane1 R0候选，包括source/binary/config哈希和production-driven gates。只有资格通过，正式runner才能消费INDEPENDENTLY_QUALIFIED release。SASS是dataless，不能把真正不存在的数值输出检查设为无法达成的门槛；版本reference/生产requester精确once/生命周期等证据要按范围如实标注。
2. **避免混源比较**：R0 B16 vs R0 U_WB16是主实验；R1理想开关集成到新binary后，要在同一R1 binary下测R1 B16和R1 ideal。R0 B16可以辅助跨binary OFF一致性检查，但不能作为R1 ideal的严格matched numerator。每点绑定Core SHA、Framework SHA、binary、ordered config/aux、trace hash、开关和epoch。
3. **真实进度和资源锁**：Lane5共享registry限制最多两项长模拟/8 CPU/32GiB预留，scan独占；每次启动前核查实际RSS/swap与其它项目活跃任务。Lane1当前自报无活动run，不等于Lane5/其它窗口也没有。拒绝重复run-key，不覆盖历史review包，失败/不完整行不混入平均。

## 4. 更有论文价值的解释优先级

首批B16/U_WB16应同时报告cycles、WB-data-full、WAD-full、实际WB创建/下层接收/完成、WB staged occupancy、借用来源与拒绝、copy读写服务、bank wait、lower queue与DRAM bytes。若只有copy消除而借用容量没有被真实触发，应把论点限定为数据搬运与bank服务优化；如果没有端到端加速，也须保留负结论和局部机制效果。有效时采用同1168项静态重划分强对照，避免仅靠闲置bypass静态挪给WBUF即可解释结果。

理想I_READ_HIT参考与I_WB/I_META单项、组合模式完全分开；不把1.721x宣称是EP-L2的天花板，也不由单点外推其他workload。Lane2的served_sector_bytes字段禁止直接当DRAM avoided_bytes。Lane6先将阶段代码/源hash放证据附件，正文聚焦问题、方法、真实结果及限定的结论。

## 5. 各Lane精确下一步

唯一执行续行指令见同目录CONTINUE.md；此文件不替代原6c136e2a科学合同，也不自动启动任何Codex。Lane1与Lane4无需重做本轮release/审计；Lane2/3继续实际生产适配；Lane5立即履行独立验证及滚动B16/U_WB；Lane6继续写作与成本差分。
