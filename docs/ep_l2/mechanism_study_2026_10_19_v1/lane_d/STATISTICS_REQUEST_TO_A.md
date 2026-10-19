# D → A：一次性最小统计需求 V1

Authority d9263fa2431592b33e900d9b48c6f20029d8b544；请求者D，原174；2026-10-19。只要紧凑application-cumulative汇总和64slice闭合，不要逐访问日志/全关键路径追踪。可直接复用语义一致的既有统计，不重复实现或改时序。

1. **共同身份与口径**：每项计数附schema/units/present、模式及干预白名单；区分logical operations、真正收费physical grants和diagnostic免除服务。记录完整cycles/instructions、lower接受的真实读写packet及有效sector bytes、exact-once/版本/排空。不存在的统计写UNKNOWN或present=false，不能写0。固定观察点为实际native L2调度周期：被阻请求的native UID+slice+generation/已有请求描述符，不把多次retry当不同请求。多个原因可同时成立，不以优先级枚举遮掉其他原因；各原因不能相加为独占GPU stall。
2. **W**：WB-data空间不足、WAD记录不足分别给retry events、首次受阻的不同UID数、首等待→解除的物理GPU周期直方图（0、1、2–3、4–7…溢出），completed/cancelled/unresolved及最大值；对活跃请求最多复用现512 descriptor内的小字段/已有observer状态，新增控制字节列成本，禁止无界UID集合。WB reserved/live物理槽与WB顺序记录分别给sum/sample_count/peak。copy逻辑读/写、实际收费读/写、免除的服务及下游WB readout分列；COPY_FREE不得把copy消失或lower读取免费化。
3. **V**：在真实L2访问/替换顺序上做有界128条影子目录（只作机会估计，不服务数据、不改真实状态）；报告policy、cap/drop与观测覆盖。淘汰后再读且有合法数据槽/共享WAD-victim目录余量、版本仍有效/无同地址write的机会及未满足原因。真正ON另给clean/dirty阶段、真实retained hits、lower reads/bytes avoided、promotion/invalidation、mandatory回收及额外查询1cycle/每slice每cycle≤1次的收费。不要从SM trace线性次序认证可捕获hit。
4. **R**：set全pending、line-MSHR满、descriptor满分别给真实拒绝retry及不同UID/等待直方图；occupancy高不算拒绝。T-only/M-only/11分别计actual detach、实际绕开line-MSHR、accepted/completed useful independent inflight、重复同地址lower reads/bytes；返回落点/descriptor等sum/sample/peak。只读oracle资格与全epoch覆盖由C/E另交，统计不能把一次LDG当资格。
5. **观察器验证与资源**：observer ON/OFF正常模式数据/版本/总cycles相等；计数0要有完整观测范围。每slice时间不能求和当全GPU周期；等待直方图报告request-weighted且保留未完成样本，不把sum(slice means)当均值。输出预算以每run compact汇总为主，不引入另一套大规模追踪或扫描框架。

现已知缺口：旧五输入有WB/copy及C7d重试，但不同UID/等待分布和真实淘汰后重用缺失；tag-all-pending尝试从既有raw恢复。请按上述一次性需求提供可用字段/明确UNIMPLEMENTED清单。D不修改公共cache/partition。
