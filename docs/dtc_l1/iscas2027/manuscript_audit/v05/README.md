# DTC完整稿v0.5：补强与服务模型审查

2026-10-15。维护者：ChatGPT。**DOCS_ONLY / NOT_A_SIMULATION_AUTHORIZATION**。

本次按用户要求对v0.4的逻辑、状态规则、方法和结果逐项补强。完整中文稿、六份附录、原数据和校验脚本保存在本次对话的v0.5资料包；此远端目录持久保存影响论文结论的关键源审计。它不修改当前协调合同、Core或接受结果，也不要求Codex自动继续。

基于协调提交：`d0f8e72b370271b7432c3785c0687e79ca3e0f4b`。SG3接受记录仍为`6886930ab22d63701e58732cfde18ba019d1dfde`。

## 1. 新发现：公共20周期配置不等于DTC读路径已匹配时延

核读Core `95ccdb7a056f2d53f740d90869785cac6d4ee0f5`：

- [传统访问函数](https://github.com/swayhrl/gpgpu-sim/blob/95ccdb7a056f2d53f740d90869785cac6d4ee0f5/src/gpgpu-sim/shader.cc#L2500-L2578)将读请求插入`l1_latency_queue[bank][l1_latency-1]`。
- [memory_cycle派发](https://github.com/swayhrl/gpgpu-sim/blob/95ccdb7a056f2d53f740d90869785cac6d4ee0f5/src/gpgpu-sim/shader.cc#L3730-L3810)对DTC可缓存非原子读，直接调用专用IO/OO路径，不经上述传统延迟队列。
- [IO写回](https://github.com/swayhrl/gpgpu-sim/blob/95ccdb7a056f2d53f740d90869785cac6d4ee0f5/src/gpgpu-sim/shader.cc#L3130-L3190)与[OO写回](https://github.com/swayhrl/gpgpu-sim/blob/95ccdb7a056f2d53f740d90869785cac6d4ee0f5/src/gpgpu-sim/shader.cc#L3420-L3492)检查完整接纳、ready和共享operand-collector许可后完成；未见独立物理数据池读bank／lane收集流水服务模型。
- [LD/ST周期](https://github.com/swayhrl/gpgpu-sim/blob/95ccdb7a056f2d53f740d90869785cac6d4ee0f5/src/gpgpu-sim/shader.cc#L4811-L4990)的DTC响应分支在传统fill前处理。循环以`m_next_global.size()`约束，DTC分支不增加该容器；`processed_count`也不是独立DTC回填端口额度。到达带宽和有限FIFO仍有限制，不能称为无限带宽；问题是没有对应物理池端口的显式本地预算。

`shader.cc`在Core95与2D共同版本Core658中的blob相同：`efed7d77d340e14b5c57c1ff0788c8304e043bb6`。这只证明该文件相同，不把两个完整运行程序称为相同。

**结论边界：** 原1.326×、1.592×以及数据容量匹配后的0.922×、1.107×仍作为原模型结果保留，但不能据此称时序匹配硬件收益或净重命名贡献。没有测量该差别影响多少，不能算术扣除，也不能直接给DTC随意加20周期。应先明确实际RTL或合理研究服务合同。

## 2. 新发现：历史IO HoL统计比可执行机会更宽

[io_frontend的ready_younger_count/entry_ready](https://github.com/swayhrl/gpgpu-sim/blob/95ccdb7a056f2d53f740d90869785cac6d4ee0f5/src/gpgpu-sim/dtc-l1-common.h#L300-L373)看的是前端已登记引用、分配未解决标志与外部依赖，不检查集成层`next_reference == references.size()`。

实际写回另有完整接纳和grant检查。因此，历史`io_hol_ready_younger_cycles`不能直接解释为“存在现在可先行完成的年轻指令”的周期。v0.5保留所有原整数和`64×io_cycles`分母，将图3改为前端已登记依赖的就绪状态。OO真实越序完成和最终回收数据继续作为实际状态使用证据，不由计数直接换算性能贡献。

## 3. 已补齐的源定义与推导

- 区分物理分配、下行候选、取得信用、事务创建与互链接收，不把它们合成同一个事件。
- 同一PIB项对同一次物理分配至多一引用；数据等待结束与消费者读后引用释放分开。
- 响应以事务UID或原事务UID找到原物理分配，整行128B等待四个32B回复；重复sector及地址受检查。
- 共享写回grant失败保留引用；成功完成才释放。代码顺序为writeback→responses→admission，不代表RTL端口已实现。
- 原始IO通过顺序推导依赖，软件前端又显式检查已登记refs ready；两者实现层级不混写。
- Tag和分配配置上限4不等于集成每步实际推进4项；专用memory_cycle每次推进一引用，实际步进次数要看clock multiplier和resolved配置。
- 提供有条件的物理分配前进充分条件：单条部分接纳、旧完整指令／外部操作最终完成、无隐藏未归属分配、每指令至多K个物理引用时，P≥T+K足以避免该读子系统的物理分配循环。证明按排空旧指令后至多T个可见行、K−1个当前不可见保留行进行。它不是必要条件，也不是整个GPU无死锁证明。默认P−T=512，但支持的全部K上界和RTL协议尚未核定，不能自动宣称默认普遍前进。

## 4. 真实未完成项

| 项目 | 当前完成 | 仍需证据 |
|---|---|---|
| 局部服务公平性 | 定位具体路径差别并修正稿件 | RTL或研究合同、匹配后的服务与性能验证 |
| 正确性／前进性 | 模型事件表、不变量和有条件推导 | RTL并行更新、事务编码、K与外部前进条件、实际测试 |
| 输入／计时 | 12项／629成员和原标签、接受的gpu_tot_sim_cycle字段 | producer构建宏／数据内容、完整parser/runner ROI绑定 |
| 硬件／总预算 | 四种配置和全状态／端口成本表已准备 | 统一PVT/SDC/SRAM/DC报告及合理强化传统参照 |

本轮包内148项算术／文件检查通过，只是PACKAGE_QA，不是新simulator strict PASS或RTL PASS。16个原数据文件与v0.4逐文件哈希一致。测试源码被查看但本轮未执行测试。旧学位论文面积结果未被填入当前硬件表。

## 5. 冻结与下一步边界

不覆盖原性能、不重标所有旧runtime、不清除失败、不重开SG3队列/NoC/DRAM/Tag sweep，不向原Codex自动发送任务。当前远端记录只是论文源审查。服务合同若需修改，应先科学审查，再以独立opt-in版本做最小定向验证；未经授权不要启动任何新仿真。
