# 在读取DWT2D raw之前封存的机制假设

本文件仅基于固定GEMM三臂和BICG六臂的原始已验日志。所有新candidate性能读取数为0；DWT2D仅已知科学合同披露的旧cycles，尚未读取其原始机制字段。后续DWT2D检查保持独立，不反向修改本文件。

**GEMM资源行为假设 M-G：** OO组织缩短cacheable warp fully-ready之后的排队/收集等待，可能支持其在更多下行/L2读量下仍优于C+。观测支持仅到：OO128比IO256的ready-to-collect均值小，GEMM三臂DRAM读写命令都为0，OO128比C+多读却更快。不能把等待总和差换成GPU cycles贡献；C+没有对应fully-ready分解。GEMM IO256/OO128不同深度，不能作为纯组织因果对照。

可证伪检查：预声明T0固定128深度后，若IO128的cycles不高于OO128，或相应ready-to-collect差异消失，则“同128深度OO仍优”的H1不获支持。T1中若Tag条目增大却没有减少每cacheable reference的新分配/Tag驱逐及下行读，则“扩大查询覆盖降低这些新请求”的路径不获支持；即使请求下降，也需独立观察cycles，不能保证收益。

**BICG资源行为假设 M-B：** OO128相对IO128改善退休组织、等待及下层时间局部性；但相对C+仍有更弱的下层复用和更大DRAM读取负担。计数显示IO128/OO128新下行读几乎相同，ready-to-collect差别很大，而OO128/C+的L2读命中分布和DRAM量又显著不同。这是关联性解释，不证明Tag容量单独造成退化，也不能把L2拒绝事件或物理驻留寿命当停顿周期。

可证伪检查：若以后经另审允许的同一T1胜出配置在BICG上减少Tag驱逐/新分配，却没有改善L2读命中、DRAM读量或cycles，则“扩大Tag覆盖可修复BICG下层复用并改善性能”的链条不成立或不充分。若cycles改善而DRAM量不降，则需要服务重叠/组织的解释，不能把收益归于节省DRAM。该holdout不在M中运行，也不由本文件追加T1点。

**预留DWT2D旧日志检查：** 只检查上述“快于C+不必伴随更少读量”的非普遍关系、既有11字段支持域和身份；不要求其复现GEMM/BICG的数值方向，不将DWT2D加入探索集、选择均值或新candidate性能。原T1候选、Gaussian发现负载、阈值和最多7个attempt均不更改。

状态分类：原始计数、严格同输入对照及有限服务分解为EVIDENCE_SUPPORTED；瓶颈、Tag覆盖改善与cycles的机制链为CORRELATION_ONLY/待干预；C+的fully-ready分解、OO重复在途地址和可比PIB-full周期为UNAVAILABLE。
