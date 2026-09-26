# P12｜MiCache: An MSHR-inclusive Non-blocking Cache Design for FPGAs

Shaoxian Xu、Sitong Lu、Zhiyuan Shao、Xiaofei Liao、Hai Jin；FPGA2024，pp.22–32；DOI：10.1145/3626202.3637571。

**阅读记录。** 2026-09-26，用户上传11页PDF；正文§1–6、图4–6、配置/资源表和主要结果已核读。版本哈希见[来源表](UPLOADED_SOURCE_MANIFEST.tsv)。未进行代码复现或独立硬件验证。

## 1. 动机与实际创新

**原文：§3，PDF3–4页。** 通过SpMV观察到MSHR需求的突发、波动和持续高占用；在所测执行片段中cache命中率与MSHR占用具有互补趋势。作者据此不再为MSHR固定划一块独立BRAM，而让cache entry与MSHR entry共用空间。

这不是“删除MSHR”，而是**MSHR-inclusive**。§1–2还明确承认in-cache MSHR/共享存储概念在更早CPU研究中出现，作者贡献是FPGA上具体的统一存储组织、并行双流水线及配套优化。不能把所测命中率互补现象写成一切负载都遵循的定律。

## 2. 统一entry如何表示

**原文：§4.1–4.2、图4/5，PDF4–5页。** 元数据与data分开BRAM存储，使用cuckoo hash查找；一个entry的data field或存cache line，或存请求者ID/offset等MSHR子项。m位区分cache(m=0)与MSHR(m=1)，counter记录使用中的子项数。图5的512-bit data field对两种类型等大。

这与DTC的“同一物理行在失去Tag可见性后仍保存数据供旧指令使用”不是同一资源复用：MiCache的核心是**存数据与存等待者信息之间的空间转换**。同时，不应把它描述成完全无独立溢出结构；LUTRAM实现的全相联victim stash是设计的重要部分。

## 3. 请求/响应完整路径

| 事件 | 论文明确动作 | 定位 |
|---|---|---|
| cache hit | 读数据field、按字偏移返回PE | §4.3，PDF5–6页 |
| MSHR hit | 追加子项、增加counter；必要时使用stash扩展 | §4.3–4.4 |
| 新miss有空位置 | 写m=1的metadata和首个子项，下发内存请求 | §4.3 |
| 候选位置有cache entry | cache entry被新MSHR覆盖 | §4.3 |
| 候选位置全是MSHR | 轮转选择旧MSHR移入stash，空出位置；stash也满则停止接收新PE请求 | §4.3，PDF5–6页 |
| 响应命中BRAM MSHR | 清m/counter；将返回数据写入同一data field，同时读出原子项供response generator使用 | §4.3，PDF6页 |
| 响应命中stash MSHR | 读子项、清valid，不转换为cache entry | §4.3 |

元数据RAW依赖通过forwarding保证。两条流水线都访问存储，采用true dual-port BRAM并不意味着不存在冲突。

## 4. 与DTC最接近、必须保留的细节：旧记录停止接收新消费者但继续等响应

**原文：§4.4，PDF6页末至7页（印刷27–28页）。** 512-bit字段按文中配置最多存29个子项。某MSHR子项满时，将旧记录放入stash，在BRAM创建同tag、counter初始为0的新记录以继续收集消费者。

stash新增f位区分迁移原因：

- f=0：hash冲突迁移；仍可被请求流水线找到，并在空闲时尝试重插。
- f=1：子项溢出迁移；**PEreq不再匹配它，也不重插，但MEMresp会匹配并逐个处理同tag的多个记录。**

因此，上一轮把DTC与MiCache仅按“数据生命周期 versus MSHR共享”分开仍太粗。MiCache确有**新请求匹配域与旧请求响应处理域不同**的规则。它保护的是等待消费者记录，DTC讨论的是物理数据行及指令引用；两者不能直接等同，但也不能声称前者从未分离过新查询资格与旧状态保留。

本段没有把“同tag新记录”当作必然新增独立DRAM事务。原文说明一次响应可匹配多个记录；下发次数和异常并发边界若需实现级结论，应核代码，不能从“新MSHR”三个字推断。

## 5. 双流水线及响应优先

**原文：§4.3–4.4，图6，PDF5–7页。** PEreq与MEMresp各有hash、metadata fetch、stash lookup、target match、data process阶段。metadata BRAM的Port B争用时，优先级为MEMresp写 > PEreq写 > MEMresp读，以先完成旧miss、缓解积压。MEMresp的部分表读取可推测执行；匹配不能确定时重入流水线。

这说明其收益包括请求/响应吞吐组织，不只是“共享空间”一项。对DTC的启发是硬件表应包含返回更新、读写冲突和选择逻辑；把SRAM位数减少等同于整个结构更快是不充分的。

## 6. 评估配置和公平性

**原文：§5、表1–3，PDF7–10页。** 在Xilinx Alveo U280上实现并评估；4个SpMV PE；矩阵CSR流从DDR4输入，向量在一个HBM pseudo-channel中经cache随机访问。七个公开稀疏矩阵，向量随机生成，索引uint32、值FP32。两种cache bank数为1和4；基线与MiCache均225MHz、512-bit cache line。主要性能指标是平均每周期返回响应数，不应自动改称通用GPU IPC或完整应用时间加速。

两类比较必须分开：

1. **等名义cache容量/最大MSHR数。** MiCache最大cache状态与最大MSHR状态共享同一空间，不能同时都按峰值占满；baseline则各自分配BRAM。
2. **相近BRAM预算。** §5.3为baseline尝试不同cache/MSHR组合，并按每个dataset展示最佳表现。它不是严格逐项等面积，也不是完全不调参的baseline；LUT/FF/DSP和端口仍需单列。

## 7. 正负结果与不能混用的数字

- 表2一bank的256KB配置：MiCache总62 BRAM，baseline75.5，按表约省17.9%；MiCache LUT更多、FF更少，双流水线还使DSP由4增至8。不能概括为所有硬件资源都下降。
- §5.2.1一bank等配置报告1.07–1.32×；§5.2.2四bank多数点有益，但某些点因子项/stash溢出变差，报告5%–19%性能下降。
- §5.3.2四bank相近BRAM的总结为21个点中16个有1.01–1.50×改善；文中1.15×平均明确**排除了baseline更快的情况**。不能当作所有点均值。
- 摘要给最高1.56×，§5.3.2四bank总结给最高1.50×，结论再次用56%。这是不同位置的数字/范围差异；本轮保留而不自行统一。正文引用必须附分组，不用一个“总体平均”遮掉回退。
- road_usa的部分收益被作者归因于cache也改用cuckoo hash造成的替换/驻留变化，不能把所有收益纯粹归给共享容量或双流水线。

## 8. 对DTC的具体影响〔比较推断〕

最重要的不是决定谁总体更先进，而是明确二者各自解耦什么：MiCache在同一entry空间内转换cache payload和miss子项，并用stash保存被迁出的等待记录；DTC分开Tag查询、PIB等待指令与仍被引用的物理数据行。DTC的论文应给出地址查找、旧消费者归属、数据位置和回收条件，而不能只写“无独立MSHR”。

**尤其需要修改的新颖性边界：** “旧记录不再对新请求可见，但仍为旧请求保留”不是足够排他的DTC表述；MiCache的f=1路径必须正面讨论。更窄的物理行生命周期/指令依赖组织可以比较，但当前四篇文本不构成首次性证明。

## 9. 后续来源线索，不是本轮已读论文

§1–2与参考文献[5]明确指向Farkas/Jouppi1994的in-cache MSHR思想；[2]是Asiatici/Ienne2019 *Stop Crying Over Your Cache Miss Rate: Handling Efficiently Thousands of Outstanding Misses in FPGAs*。若继续考察miss-state组织，应先追这两项，而非把MiCache当作共享状态的起点。
