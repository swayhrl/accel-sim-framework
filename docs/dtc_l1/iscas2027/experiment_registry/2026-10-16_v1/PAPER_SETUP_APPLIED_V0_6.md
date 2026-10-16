# 论文实验设置表修订已实际落实到英文工作稿v0.6

2026-10-16。内容修改发生于ChatGPT本地LaTeX工作稿，不在174仿真执行分支；文稿为IEEEtran 4技术页+第5页参考文献，检查了编译、20条引用和字体。实际PDF作为对话附件交付，**本仓库文献/实验规划分支不冒充已上传论文源码或已经验收新仿真结果**。

正文`Table I: Simulation Setup and Per-SM L1 Design Points`包括64-SM/GTO/1410/1410/1410/850MHz/20内存通道/40 L2子分区/10MiB L2，及C16/C80/C+/IO/OO的每SM容量、PIB、传统MSHR数。**明确IO/OO每SM的DTC 80KiB池之外仍建模了16KiB传统side-path数据阵列，二者合计96KiB**；C+预注册96KiB、PIB256、MSHR512，不称等面积。

正文`Table II: Finite DTC Service Assumptions (R1 V2)`列出当前经过R1 V2定向资格的保守服务假设：Tag1cycle/II1，回复1×32B/SM/cycle、ready+1cy，waiter4/cycle、data collect4×32B/cycle、writeback1 instruction/cycle；集成流水每核周期至多处理一DTC逻辑引用。引用174`e1c474f31dd69a34c84f3222330e1c2518472104`的finite service contract和V2 receipt，不冒充真实RTX4080内部端口或全12项性能验收。

新增的实验配置未填伪造性能、面积或输入规模；现代RTX4080 fixed128KiB容量gate保持HOLD。评估方法与本分支`PAPER_SETUP_REQUIREMENTS.md`以及源174`R2_PREREGISTRATION_V1.md`一致。文稿验收另有可下载的LaTeX源码包和已编译PDF，提交后仍要由作者审查TBD、实验主张、结果和最终图表。
