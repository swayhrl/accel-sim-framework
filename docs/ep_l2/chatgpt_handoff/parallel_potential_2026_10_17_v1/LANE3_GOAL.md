# Lane3 Goal：上游供给与 WB 完成控制的有限参数实验

先读 [PARALLEL_CONTRACT.md](PARALLEL_CONTRACT.md)。在原 Framework 分支 `hrl/ep-l2-ft20261016-lane3-v1` 续接；保留既有 RO 候选和未提交工作，在独立任务目录准备本轮条件，必要代码在从正式Core7b8建立的隔离worktree实现。RO完整资格不再是这些参数任务的前置依赖。

## 1. 直接交付四个单因素条件

每个条件准备 Convolution/FWT 的 B16_BANKED 和 U_WB16 配对，完整应用仍由 Lane5 调度。逐条件发布，先完成容易以现有 binary 生效的 ROP40，再推进其他项；不要等四条件全齐才交付。

| 条件 | 有效变化 | 所回答的问题 |
|---|---|---|
| ROP40_H0 | `-gpgpu_l2_rop_latency` 有效值160→40；其他H0 | 固定L2前置服务时间是否压住差异 |
| L1_32_H0 | L1容量64KiB→32KiB；保持128B line、4banks、20cycles、其余声明的策略/MSHR/队列 | L1过滤后的L2需求规模和局部性是否使弹性空间未被使用 |
| ICNT2_H0 | `-gpgpu_clock_domains 1132:2264:1132:850`；只提高ICNT域 | NoC输送速度是否限制到达和返回 |
| WAD256_Q4 | Q4资源条件下 `-gpgpu_ep_l2_wad_entries` 有效128→256 | 数据已交给下层后，直到WB真实完成的控制责任是否仍在阻塞 |

冻结母配置和官方 binary 身份见总合同。先读取实际运行配置、源注册及消费路径，构造最小 overlay，输出完整 effective dump 和字节hash。不能只引用选项默认值：当前有效 ROP 是160而不是注册默认85。

L1_32从实际 `-gpgpu_cache:dl1` 配置派生：仅更改一个容量决定字段，报告 sets×ways×128B 的实际结果；保留bank/latency及未研究的queue/MSHR字段。若现配置为4sets×128ways×128B，则4sets×64ways×128B才是目标32KiB；此示例必须由现场有效配置确认。该条件改变L2需求流，明确标作容量/局部性敏感性，不声称保留同一L2访问序列，也不更改原始应用trace。

Q4已看到WAD-full和scheduler-full，故WAD256选在Q4而非已无WAD-full的D4。保持lower accept只释放本地data、set_done才释放WAD的边界。WAD256增加metadata预算；不要把它误叫WB数据槽增加。

## 2. 真实生效与最小资格

对每个条件提供源注册位置、真实消费路径、有效参数和针对本次改变的生产检查：

- ROP40：请求进入/就绪时间差按40GPUcycles体现，返回/排序未提前完成。
- L1_32：有效Tag与容量、set/way边界、full/miss/refill及不变队列检查，禁止只修改配置名字。
- ICNT2：实际network mode、ICNT时钟推进次数及下游/SM clock保持；资格不能只证明DRAM频率变化。
- WAD256：有效上限、边界分配/拒绝、真实完成释放、地址顺序和退尽；若guard当前只接收128，通过Lane1做可审查opt-in条件支持，不能删除保护。

同一已冻结binary可支持且作用域已补齐的条件，交付配置和资格即可，不要求Lane5重编译。需要新源码时只提供最小patch和检查给Lane1滚动集成，不与Lane2/4共同编辑同一核心工作树。

不要为了增加测项使用无效旋钮：`-gpgpu_num_mem_units` 当前注册已警示没有接入；不能把它当访存单元数实验。`-gpgpu_l1_latency=0`非法；后续正值1/5、L1banks8、`gpgpu_mem_unit_ports=2`等只有在已有等待/Ideal对照明确指向对应限制时，作为总预算内追加候选。

## 3. 有界联合条件的准备

保留四个单因素的数据对照。读取Lane4/Lane5逐步到达的Ideal和实际压力，提出最多两个有限二因素组合，每个都在启动前写明：单因素证据、仍阻塞的资源、确切联合配置、B/U同等资源、额外代价和预期可证伪结果。

例如L25与ROP40、WAD256与某个已验证服务点、P2与已验证下游点，都必须按实际证据选；不是预先将所有资源同时放大。若选择的联合因素缺少同条件单因素端点，补齐该端点并计入72次总预算，或选择已有完整对照的组合。单项弱不自动拒绝联合实验。

## 4. 输出与完成

每个profile就绪即在原分支commit/push并远端回读，发布到现有shared handoff/coordination request体系。最少输出：config差分、有效参数、source/binary/config身份、B/U匹配、生产检查、资源增量和Lane5可运行的spec，不把“候选参数已写”标作应用完成。

四项配置及必要guard/检查完成后，继续分析已到结果并给出受总预算约束的联合候选；全应用仅由Lane5注册和调度。使用共享CPU/RAM/磁盘lease完成构建和小fixture，不为未到数据建高频watcher。

如实际不能启用某旋钮，发布源证据和明确缺口，继续其余条件；不可用项不填零、不假装负结果。无论最终相对收益增大、减小或中性，都保留该条件的绝对cycles、B/U比值、压力变化和配置成本。
