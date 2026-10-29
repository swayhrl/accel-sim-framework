# R2构建实证与执行检查

本清单用于复用[重复缩减方法](WORKLOAD_REPETITION_REDUCTION_METHOD_V1.md)。每个结论只支持其冻结source、ELF和profile；原始证据定位见[R2索引](R2_WORKFLOW_EVIDENCE_REFS_V13.json)。

| 问题或检查点 | 实际证据与适用边界 | 后续处理 |
|---|---|---|
| directsource构建输出同basename cubin | aligned和transpose的离线预枚举暴露歧义，不能假设总能按basename唯一提取 | 在GPU前执行cuobjdump -lelf；修为原Make object再link，输出新OBJECTLINK_V2身份，保旧产物，不放松mapper |
| CUDA11.8包缺cuda/std/type_traits | 编译失败是header闭合问题，不是GPU或应用不支持 | 只用已有明确路径的补头，记录所有实际依赖SHA及编译器；不默装替换环境 |
| device代码看似没改但SASS不同 | transpose新同工具链控制8／8一致，历史diagonal仍有差异 | 保存两层比较与未知历史flags，声明剩余风险，不能写历史全等 |
| 旧注释与实际loop传播不符 | 现代transpose NUM_REPS用于host循环；旧429还涉及device重复及同步 | 读真实版本源码与变量传播，不全局替换名字，不混用旧版QA／性能解释 |
| coarse／fine原QA较弱 | 原程序对这两种partial transpose使用h_odata自比 | 原检查保持且披露，不能升级成全variant独立数学验收，也不默认重写oracle |
| 队列命名空间改变后的QA复用 | scan已有真实17 gold PASS且身份、用途与输入绑定 | 复用精确QA回执；只对真正变化的新身份追加必要QA |
| 只见trace增长或旧PID消失 | 两者均不能证明完整采集 | 按同run最终proposal、真实wait和owned／lease闭合判断，不因观测超时或退出直接重启 |
| tiny scratch预算带入原空间R2 | 原5D逐shard检查expanded×3，不是全kernel展开量；未实证本批发生1GiB拒绝 | Root显式NAS预算与RAM分开，24GiB为Root精确工程准入中的逐shard估算门，实际空闲34GiB为保守采样门，均非硬quota或执行资格 |
| CPU POST与GPU采集的锁边界 | GPU采集与CPU数据整理资格不同 | 采集遵守单GPU队列与Comfy协议；POST使用其独立CPU／I/O资源合同，不借此改变CUDA／consumer语义 |

## 每次提交给队列前

- 新profile是否保原N、shape、type、路径、warmup和完整算法stage；缩减的host与device循环分别有理由？
- 新ELF、argv、input、source、compiler、header、libc及用途是否均有可读字节绑定，所有cubin basename是否实际唯一？
- native QA是否属于这个身份，是否有真实gold结果、退出及owned闭合；source／编译成功是否被误写成QA？
- 原图完整launch／record是否覆盖，producer声明、F9／group数据和selected consumer资格是否分层？
- 增加的校准是否真有必要，原生、插桩与模拟预算是否分别定义；是否误用GB推模拟时长？
- 中断和不完整现场是否明确保留，原资产与历史是否仍在；新版本是否避免冒充旧大版完成？

模板只供填写审查。不要用空字段、固定次数2、源码相同或计划中预算替代真实验收，也不要默认新建数值oracle、全host数组转储、全配置或完整模型回放。

本时点四项120次完整采集均已Root独立接受，后处理和轻量consumer仍待实际运行。源码和编译接受、原程序已有数值检查、完整采集、F9数据验证、consumer以及科学资格分别记录。原QA范围包含已披露的弱检查，不用“全gold”字段冒充未实施的独立oracle。

共享I/O增量已经真实激活双CPU POST，原F9/F4、特征提取和5D算法字节未改。全记录通过、全部group SHA/CRC通过及owned闭合仍须分别检查。两个CPU使用真实排他角色槽加I/O读取锁，不能用私有memfd冒充公共I/O准入。
