# Q1软件与科学解释边界

本轮不新增广泛文献或重新审查历史raw。软件近邻以已接受组合包f88e40123f4060328aa50a16d22fa328cee51cfe的RECENT_LITERATURE_AND_SOFTWARE_EXCLUSION.md和GS冻结证据为来源。

- GS-Scale自身已做deferred CPUAdam、参数forwarding和pipeline。原CPUAdam/增密/SH/LR/相机语义本轮保持；没有拿GPU-only的不同optimizer当等价强基线。
- CLM已覆盖camera/visibility reuse、选择性appearance传输、optimizer overlap与调度；泛称复用或隐藏等待不具新意。
- TideGS的工作集/异步与eviction后optimizer cold restart、camera顺序属于不同语义，不能当无损替换。
- A45H合成CPU组件、A44已收窄等待并集和A46线程混杂仍限定其旧范围，不是本轮native结果。

本轮T8/T16/J、兼容调度/状态复用/传输反事实均未执行，因此不能说SOFTWARE_ABSORBED已被本轮重新证明，也不能说软件已穷尽。监控工程异常不构成H_MEM/H_SM/GPU物理瓶颈证据。没有具体、强软件之后的已测残余和独立物理控制，不晋升硬件。
