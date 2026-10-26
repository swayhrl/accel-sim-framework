# L1、ICNT、TLB 模型与 Counter 审计

本文件是只读源码审计，不是本轮fixture执行证明。Core精确版本为 `swayhrl/gpgpu-sim@1093d2629e3d6a9130ba25b9dd119b6f3e16c092`；Framework为 `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`。raw与config的身份、SHA及行号见 [MEMORY_PATH_EVIDENCE.json](MEMORY_PATH_EVIDENCE.json)。没有引用另一个AWMA runtime的翻译模型。

## 生产路径审计表

Core文件路径均相对 `src/gpgpu-sim/`；`abstract_hardware_model.cc`相对Core的`src/`。表中native/r5逐字相同文件的行号可直接共用；gpu-cache与l2cache发生observer增量的地方明确给r5行号。

|阶段|文件、函数/行号|PROVEN模型语义|所缺因果统计|
|---|---|---|---|
|Trace到核心|Framework `gpu-simulator/trace-driven/trace_driven.cc:155–179,251,645–665`|恢复寄存器依赖与lane地址，随后调用普通generate_mem_accesses；不是无限MLP注入器|warp memory ready→真实issue的逐原因机会计数|
|warp调度/scoreboard|`shader.cc:1266–1366,1567–1574`；`scoreboard.cc:83–106,128–149`|warp waiting、ibuffer、RAW/WAW与MEM pipeline约束发射；W0_Scoreboard意为有valid但无ready，注释仅说可能因memory|不能把所有RAW归访存，或将调度分布当GPU独占stallcycles|
|coalescer|`abstract_hardware_model.cc:477–515,696–735`|warp/subwarp lane地址合并；arch70按32B sector组织请求|按warp memory指令单独计数及sector数分布不在当前raw|
|L1 bypass|`shader.cc:2273–2347`|CACHE_GLOBAL、无L1、全局skip可bypass；其余访问L1|config skip0不证明所有opcode都不bypass；本例已有实际L1访问1.5M可约束总体|
|L1 bank/latency|`shader.cc:2075–2143`|4banks、20cycle hit/latency queue；有限bank queue产生冲突|bank冲突次数不等于独占wallcycles；实际occupancy/lifetime histogram不足|
|L1 MSHR/missq|`gpu-cache.cc`的mshr_table/发送请求函数；native679–701,1771–1835，r5同段约+3行|same-key merge、entry/merge cap及MissQ失败分列；失败是可重试事件|entryfail0不证明没有大量在途；需要occupancy来判余量|
|L1专用输出|`shader.cc:3110–3151`|`EPL2L1V1`输出kernel shared delta及application累计；保留overlap语义|多kernel重叠不能假装独立归属；本例单kernel|
|SM注入|`shader.cc:2294–2323,4687–4690,4708–4777`|bypass路径须ICNT buffer；global read/write计数于真实inject更新，L1 writeback也可能计global write|不是原始load/store指令数或独立128B line数|
|ICNT返回与SM buffer|`shader.cc:2866–2916,4814–4849`|cluster FIFO、LDST response FIFO、L1 fill/m_next_global有真实资源门禁|包数、flit数、请求者响应和DRAM完成不同单位|
|L2 ingress|`gpu-sim.cc:2197–2213`|每L2tick×subpartition检查full(SECTOR_CHUNCK_SIZE)，即使没有已确认head需求也可加gpu_stall_dramfull|它是输入满状态观察，不是DRAMcontroller拒绝，也不是unique packet拒绝率|
|L2 response注入|`gpu-sim.cc:2149–2166`|有返回head但ICNT buffer拒绝时才加gpu_stall_icnt2sh|零表示该门没有拒绝，不代表整条响应链无延迟|
|DRAM入口|`l2cache.cc:790–857`，尤其812–845|channel仲裁subpartition，检查return空间、credit、scheduler后进入dram_latency queue|DRAM issue/return、L2lower候选的分母不同|
|DRAM服务|`gpu-sim.cc:2174–2180`；`dram.cc:327–453,559–575`|当前非simple模式有FR-FCFS、bank/row/timing、命令与返回queue；不是只用固定100cycle完成所有访存|观测不能单独识别scheduler容量、bank时序或字节服务谁主导|

## TLB/PTW：当前生产runtime没有这一路径

**PROVEN（精确源码域）**：

- 全Core `src`中的TLB/PTW残留是 `stats.h:42,49`枚举、`mem_fetch_status.tup:34`状态名，以及`shader.h:1786–1787,1907–1909,1989–1990`的声明/分配/释放数组。没有查找、miss处理、page walk发包或资源准入调用。
- Framework `trace_driven.cc:251`将trace lane地址直接set_addr；645–657使用正常generate_mem_accesses。
- `mem_fetch.cc:58–63`直接用地址做addrdec_tlx/partition_address，没有翻译阶段。

所以当前EP结果不能归因TLB容量、PTW并发、pagewalk缓存、地址转换延迟或TLB“低miss率”。这不是“测到TLB miss=0、资源富余”，而是该资源没有生产时序模型。真实GPU的翻译影响属于模型外UNKNOWN。

## ICNT：LOCAL_XBAR按packet仲裁，非真实字节链路带宽模型

actual config：network_mode2、subnets2、input/output buffer512、arbiter1、flit_size40。源码：

- `icnt_wrapper.h:64`：2为LOCAL_XBAR；`icnt_wrapper.cc:180–192`选择LocalInterconnect。
- `local_interconnect.cc:302–303,343–361,385–393`假定所有packet一个flit，Push不按byte size拆分，HasBuffer按一个packet检查，忽略传入byte size。
- `local_interconnect.cc:80–84,193–287`按有限packet queue及destination进行仲裁。

因此有buffer/仲裁约束，但不能用traffic bytes或40B配置换算这个模型实际施加的物理NoC带宽上限。Vector请求1.5Mpacket，input-full0，平均output queue51.9105 **packets**；不是51.9%利用率。输出avg_util的分母是cycle×active output queue，未除512；见`local_interconnect.cc:400–417`。有packet排队不等于真实NoC字节带宽饱和。

## Counter不能误读的七项边界

1. **gpu_stall_dramfull**：1546240/(64×75039)=32.1966% slice-L2-tick输入满观察。不是1546240个全GPU停顿cycle，不是DRAM直接full。
2. **DRAM scheduler full**：477774/(32×56346)=26.4978% channel-DRAM-cycle。C7E causal block952167则是有真实lower候选，scheduler_block且!return_block且!credit_block时的guard拒绝，见r5 `l2cache.cc:1762–1772`。两者不能相减或相加。
3. **MSV2 WAIT**：`ep-l2-mechanism-observer.h:45–83,113–123`中requests是该UID首次遇该reason；observations是每callback blocked；多reason可同次增加。reason sum/max从首次阻塞到首次known不再阻塞，seen位不重置，第二次阻塞不重新arm；ANY则直到真正admit。unknown保留未解决状态。故跨reason/跨slice都不可相加为可节省cycles。
4. **r5 route admitted**：Frontend允许一次commit尝试，不等于实际接受。Vector尝试1581555，commit accepted1500000、denied81555；denied_bank65277、denied_landing16278。本报告的funnel显式分开。
5. **latency**：`mem_latency_stat.cc:188–227`的mf从mem_fetch创建到SM LDST response buffer接受，包含WRITE_ACK（调用点shader4815–4829）；256–264的icnt2mem也从request timestamp开始，非纯网络飞行；`dram_sched.cc:237–247`的mrq是DRAM调度人口。1266/234/228/7均非Tag生存期，区间与分母不构成可加分解。
6. **L2_BW_total**：`gpu-sim.cc:1666–1675`用所有L2→ICNT reply packets×32B/time。Vector的500k写ACK实际8B；724.1035GB/s只是sector-equivalent reply rate，不是DRAM实际字节带宽。可用的是EPL2DRAMV1明确bytes/capacity：44897536/57698304=77.8143%模型窗口容量。
7. **Bank_Level_Parallism_Col无效**：同raw30785/31097给出1842581760/1842907392，超过16banks物理上限，**PROVEN不可用于归因**。r5 `dram.h:220–221`的banks_time_rw/banks_access_rw_total无字段初始化，`dram.cc:49`起constructor未清它们，386/391直接累加，729输出比值；未初始化是**LIKELY**原因，本轮未做工程复现或修改。其它ordinary bank-parallelism/rowlocality各自单独定义，不借损坏指标证明MLP。

## Tag和RO人口的观测范围

r5 `ep-l2-ro-transactions.h:318–331`只将live且issued&~ready的RO事务计lower并发，并在同一次scratch中排序line去重。lower_accepted会增加人口，fill/retire不能增加；它不含MissQ待发、native请求或ready待response事务。live RO峰、descriptor峰与lower独立line峰可以发生在不同时间，不能相加。

B0另有更宽的全set域：r5 `l2cache.cc:1730,2151–2172`在每L2 cache cycle末采样，只有B0开关门控，不要求有head。`gpu-cache.cc:242–253,256–289,303–312`初始化并在真实Tag状态变更维护reserved_by_set/当前set最大，getter取compact状态。`l2cache.cc:1882`跨tick取set最大峰。Vector每slice75039样本、任一set最大3，因此该结论不限r5 covered head域，但仍不覆盖tick内部瞬态，也不补TVD requester/raw/reuse联合。

L2构造的sector初始INVALID，`gpu-cache.h:305–322`；r5分类1097–1106按any RESERVED、all INVALID、any MODIFIED、其余clean，和401–414的line谓词一致。Vector raw143确认perf_sim_memcpy1，317–318确认两段HtoD各16000000B；Framework `gpu-simulator/accel-sim.cc:115–131`先无时序prefill再begin RO epoch，Core`gpu-sim.cc:2422–2443`、`ep-l2-ft-cache.inc:103–115`填Tag/ready。因此prefill存在是PROVEN，解释covered INVALID=0为LIKELY；未逐地址验证其覆盖所有target sets，不能写FT冷启动全VALID或命中率由此必然决定。

## 源码身份核验与执行范围

下列native d010与r5 1093文件逐字同blob，供行号引用，不构成跨binary性能拼接：

|文件|blob|
|---|---|
|ep-l2-mechanism-observer.h|703e866c5e2eceed179a9514328024964825b20b|
|shader.cc|c6254b75aed125c8ed745f533b75ea77a8cad759|
|mem_fetch.cc|14db8b0ebebc05c31c508cc49893b6653e37bdb1|
|gpu-sim.cc|3b8da4e62b04a9122aca2bcffd58635c387c9b24|
|dram.cc|8d28418d7ea9e7c711ff741c2ce7c818d7aebdd0|
|mem_latency_stat.cc|c77a686487459382a9972eb2556905ad0f17cacc|
|scoreboard.cc|44a99809893718e05e90e8e3684940d029518ccc|
|abstract_hardware_model.cc|e8ddf95ab5fe91dcd489fe422e40a062ded66f47|

Framework trace_driven.cc blob `dbe1c55aeb8253458ee1d240cbabb02b67183666`；r5 local_interconnect.cc blob `93689c783a629a0b83ea55097e948b2286512c17`。本轮按精确commit由GitHub connector读取缺失历史blob，未在protected partial clone触发新的lazy fetch。

本轮实际执行仅有原raw/summary/config的有界解析与SHA核对。被动计数补充、非干扰fixture、统计修复或单因素实验均是设计，见 [MINIMAL_CONTROLLED_EXPERIMENT_PLAN.md](MINIMAL_CONTROLLED_EXPERIMENT_PLAN.md)，未实施。
