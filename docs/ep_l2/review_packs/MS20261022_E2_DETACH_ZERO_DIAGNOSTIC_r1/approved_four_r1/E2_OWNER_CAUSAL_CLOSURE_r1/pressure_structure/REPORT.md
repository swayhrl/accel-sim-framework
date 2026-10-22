# Tag压力的结构性归因：已证边界与UNKNOWN

**已证的是必要触发未出现；尚未证出“为何同set的16个way没有同时对需要替换的新请求呈RESERVED”。** 这不是等待新实验才能交付的缺口：当前四点负结果和调用分支归因已经闭合，更强的空间/寿命解释保持UNKNOWN。Conv仍未独立接受，本版不纳入。

实际每slice：64sets×16ways=1024Tag，128B行/4×32B sectors，IPOLY set索引；共享D512、每canonical line32请求者、native line-MSHR128、L2 missq128；M1的RO绕过传统line-MSHR。payload共1168×128B，4bank、每bank每物理cycle1次操作。分区FIFO为64/128/64/64。

F的legacy WBUF16贡献于1024+128+16总预算，**不是当前unified mode2的WB角色硬上限**：wb_local_cap=0、无固定TVD物理分区（shared WAD/TVD目录128仍保留），角色共享1168池。DWT WBpeak39、Vector36合法；不改变原合同/资格。配置字符串中的resultfifo0也不代表L2真实响应FIFO为0。

| workload | liveRO峰值最大值 | issued-not-returned RO峰值 | cycle采样D峰值 | Tag绑定峰值 | RESIDENT pending峰值 | WB角色峰值 |
|---|---:|---:|---:|---:|---:|---:|
| sgemm | 0 | 0 | 72 | 1024 | 19 | 0 |
| cfd_097k | 64 | 59 | 255 | 1024 | 1 | 11 |
| dwt2d | 58 | 54 | 228 | 1024 | 48 | 39 |
| vectorAdd_4M | 96 | 70 | 369 | 1024 | 1 | 36 |

以上是**各slice峰值中的最大值**，不同资源峰值未必同时，不能相加当瞬时状态，也不能除64sets得到同set压力。liveRO含ready等待响应等状态；RESIDENT pending不含RO角色。

`bound_tag_peak`的源getter明确要求Tag非invalid且payload handle live，排除了invalid Tag保留句柄；它把有效/脏/RESERVED绑定共同计数，**不是RESERVED占用**。所有64slice都曾采样到1024个绑定，说明并非“Tag没装满”；满cache仍可有可替换validway。Tagprobe只有在未命中可用目标且同set全部way reserved时才因替换空间不足失败。sectorcache任一sector RESERVED即令该way reserved。

这些容量没有结构性地禁止触发：D512、line128、payload1168都不要求待返行均匀分散到64sets，M1还绕过RO line-MSHR。现有RO峰值64/58/96也不能证明某个set始终少于16个pendingway。native、RO、准备中的payload及不同ready/attached状态没有可用同set联合分布。

已有真实瓶颈依据：Vector的MISS_QUEUE_FULL为818,741个重叠head观察、涉及161,872个首次阻塞请求；DWT有148,372个BANK_COMPATIBLE_LANDING观察和34个WAD_FULL观察；四点都有DATA_SERVICE/VICTIM_LOOKUP重试。它们支持上游队列/共享服务存在压力，但没有同set联合数据把它们量化为“没有TagFAIL的原因”，不能相加当总stall或推因果份额。已咨询RO descriptor/address检查无失败也仅是条件性事实。

当前没有：每slice/set RESERVED-way高水位或0..16分布、pending年龄/剩余寿命、需求set和hit/miss/上游跳过的联合、native+RO+WB/TVD按way的同刻状态、完整missq占用高水位。全部保持UNKNOWN；不以总事务数、平均分布或高reuse率替代。

若未来确需回答更强“为何未见”，最小观测是既有probe处的bounded reserved-way分布及near-fullset joint ownership/reuse/missing/age，再关联同时的MSHR/queue占用；需要另行批准和新source非干扰资格。本轮不实现、不启动、不做参数网格，也不按已知F加速筛workload。

STRUCTURE.json记录精确源commit/blobSHA/行号、每slice峰值、采样语义、重叠B0指标及可证性矩阵。已有旧接受common-stat复现检查仅保留引用，不拿它复原oldmain61隐藏动态。
