# ISCAS论文实验配置写作规范与可信来源（2026-10-16）

## 回答：是否应把Experimental Setup写进正文？

**是，而且必须给出本论文可复核的关键参数。** 英文v0.5已有`Table I: Per-SM Capacity Design Points`与`Table II: Local Service Parameters`，前者却少了常规side-path数据阵列和C+最终参数，后者仍是TBD；公共平台写在散文段里、输入规模未核定。因此配置不是“没有”，而是**不够完整且可能低估DTC数据存储占用**。

## 三篇近年ISCAS一手示例（不是“会议强制一张表”）

| 会议工作 | 原文中的证据 | 对本稿的启示 |
|---|---|---|
| SPEED, ISCAS2024 | [作者PDF](https://arxiv.org/pdf/2401.16872) §III-A `Experimental Setup`（PDF第3页）：Ara基线、VGG16/ResNet18/GoogLeNet/SqueezeNet、QuestaSim周期仿真、DC2014.09、TSMC28nm、4 lanes和4096-bit向量长度、tile尺寸等 | 即使5页文章也明确baseline、真实应用与工艺/工具/核心参数；有些通过精简段落而非大表给出 |
| Quark, ISCAS2023 | [作者PDF](https://arxiv.org/pdf/2302.05996)（PDF第3-4页）：ResNet18+CIFAR100与量化表I、QuestaSim10.7c；4 lanes/4096 bit、GF22FDX、DC21.06与Innovus21.14、具体频率面积表II | 配置不仅写“RISC-V仿真器”，还把性能、功能验证、实现资源边界连接到具体设计点 |
| DDR4 Benchmarking Platform, ISCAS2025 | [作者PDF](https://arxiv.org/pdf/2501.15582)，实验§III与Table II（PDF第3页）：主板/FPGA/DRAM型号、数据速率、PHY和AXI时钟；Table III给出FPGA资源开销 | 对存储研究，关键通道、时钟、存储容量、存储设备/方法用表格非常合理 |

这些只是高相关小样本。不能据此声称所有ISCAS论文都必须用Table I或Table II，也不意味着需要展示源码每个选项。

## 本稿必须展示的参数（不会从AWMA资格自动移植）

### 主64-SM / 64-SM finite-service

| 组别 | 参数 | 可信状态 |
|---|---|---|
| 公共GPU平台 | 64 SM；GTO；Core/ICNT/L2/DRAM 1410/1410/1410/850 MHz | accepted FAST64 shell resolved |
| 下游 | 20 memory channels×2 partitions=40 L2 subpartitions；总L2=10MiB；128B line/32B sector；192 MSHRs×merge4、miss queue32/partition | resolved config source, not independent silicon calibration |
| C16 / C80 | 搜索、数据16/80KiB；32sets×4/20way；PIB8；32 MSHRs×merge8 | accepted matched sector/new-read configurations must specify corresponding trace/mode |
| C+ (TRAD96-P256-M512) | 96KiB conventional data（32sets×24way）、PIB256、MSHR512 merge8 | 174 R2 fixed pre-registration, not equal-area evidence |
| IO / OO | 16KiB searchable tags；80KiB dedicated pool **plus 16KiB conventional side data**, each total96KiB data arrays; PIB256/128 | 174 R2 prereg and capacity-source audit; tag coverage does not represent an additional 16KiB data array |
| 有限服务V2 | Tag latency1/II1 per eligible lookup, four banks, integrated 1 ref/core-cycle; 32B refill≤1 sector/cycle; 128B ready after last sector+1cycle; waiter≤4/cycle; collection≤4 sectors/cycle; retirement≤1 instruction/cycle | 174 finite V1 fixed assumptions with R1 V2 pipeline correction/test; not a measured4080 physical port model |
| 全局lower cap | 新finite IO/OO 32768，须说明传统行中不同较小cap的非绑定与严格复用证明 | 174 R2 prereg |

### 现代4080（独立实验范围）

RTX4080模拟基线参考76SM、核心等域2505MHz、DRAM5600MHz、8 memory channels×2 subpartitions、64MiB L2、每SM统一L1/shared128KiB，adaptive partition启用、32cy原L1延迟、384×48 MSHR。所有这些是**模拟器配置**，不是经本轮证明的真实4080隐藏硬件参数。每个kernel有效L1/shared须解析，Hotspot此前观测96+32KiB；现代DTC容量合同保持128KiB总预算，**尚未通过实现准入**。

109真实RTX4080数据独立汇总，原生SpMV1138× JDS36 CTA小缓存驻留；LayerNorm FP32 1024×1024及8192×1024原生可测，trace被拒绝，不能出DTC sim结果。

## 放在正文哪里

推荐**一张紧凑双栏内Table I**同时展示公共主平台和L1配置（必要时两行注记C+与side path），再以单独服务表描述影响公平性的查询/回填/收集限制。如果实际篇幅不够，保留配置表和简短方法段，删除重复背景解释，不缩正文字号，不靠附录承担关键值。

实验输入单独至少写原12个应用与来源，输入规模/ROI如未核定明确TBD，不用NO_ARGS/文件名猜测。8、16、32B与128B的含义必须区别：line size=128B，sector=32B，新下行请求粒度与通道实际流量不是同一指标。证明载荷可用的source manifest/commit/validator在复现材料里，不要用“629 trace members”冒充629个独立程序。

尚未拿到五种组织的硬件面积/时序或资源端口时，表中保留TBD，不能用“equal area”替代资源向量。动态公版只在输入/effective service完全一致时作为对照。
