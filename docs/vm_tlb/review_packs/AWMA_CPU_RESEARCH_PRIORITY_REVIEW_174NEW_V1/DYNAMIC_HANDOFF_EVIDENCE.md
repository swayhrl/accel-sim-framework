# 强软件之后的动态准备与交接
优先对象仍是一个完整神经势能/力消费者；选择已有 OAM-S 是为了身份可追溯，不预设 Sobek 可替换。SOURCE_ONLY 与 ACCEPTED_NATIVE 分开。

## 必要依赖
```text
当前坐标/元素/盒子/PBC已就绪
  → 合法邻居搜索/skin更新判断
  → 有效有向边 + periodic shifts + 当前几何特征
  → consumer所需边方向/顺序/索引宽度/CSR或置换/执行计划
  → 两层实际神经网络前向 → energy
  → 对当前坐标的一阶 autograd → forces
```
邻居搜索与索引准备是不同工作。力推理只计所需一阶导数；force-loss 参数训练才可能需要 double backward。离散边更新不应求其伪梯度；当前边几何仍要参与正确的坐标梯度。缓存旧 SH/距离而不更新会改变力。

## 本轮新增/补实的接口判断
| 边界 | 固定来源与事实 | 对同语义接入的后果 |
|---|---|---|
| NequIP TP scatter | `27d9d218…/interaction_block.py:82–125,175–181` 逐 coupling 建 uvu intermediate，后接 simplify 后的 linear_2；row0 receiver / row1 source | 改输出 grouping 必须同时证明 path/normalization/weight 和 linear_2 等价；不能只换函数名 |
| Sobek 契约 | `c1f815bf…/tpconvproblem.py:75–85` 要求全部输入/输出 angular sector 同一 multiplicity；`irreps.py:79–89` 不接受重复 (l,parity)；`graph.py` row0 sender / row1 receiver | OAM 官方描述的 128/64 特征与 homogeneous uvu 不直接匹配；模型 package 精确 TPProblem 尚未在本轮读取。一般 NequIP intermediate 重复 irrep 也是独立阻断；不能靠切换 uvw 或零填充绕过且声称相同工作 |
| 图生命周期 | Sobek prepared graph 克隆并缓存；ALCHEMI prepared/reuse 输出可能借用同一底层 buffer 并原位更新 | 不可让 consumer 缓存 stale graph；新 topology version、edge shifts、有效长度及容量都须一致；无更新时才共享 |
| COO 与动态长度 | ALCHEMI 官方 guide 有多种输出与 selective rebuild；exact COO/容量输出的同步和溢出合同不同 | 不能规定一律 dense→COO；Sobek compact E 接口与 padded capacity 也非自动无拷贝兼容 |
| 最强消费者 | 旧 OAM-S 已接受的是 OEQ 原生/编译路径；其 atomic 路径不必外加确定性双向排序 | 不能人为加入 deterministic 要求或锁住慢消费者制造图准备收益；Sobek、OEQ、cuEquivariance 只有 task/numerics/连接一致才可比较 |

ALCHEMI 非性能实验组见 G06；其能力是强基线，不是本机净收益。Sobek 原文的已核排除项见 G01/G02；这个分母缺口保持 UNKNOWN。VTC 索引映射消除的 layout 搬运不能直接代替坐标依赖的邻居搜索与新边信息；Kitsune 的队列和任务调度也已覆盖一般 tile-ready 思路。

## 应用/输入与公平性
已接受 `62af3414…` 的 OAM-S:0.1 package SHA `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`，两 interaction layers、r_max=4.5；sitraj 原文件 SHA `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`，110 个 64-Si 周期帧。这证明旧身份可复用，不证明新 Sobek backend 资格。frame55 已是旧 discovery，不是 holdout，也不能用旧准备/force 失败来断言所有动态路径失败。

当前缺：package 每层精确 TPProblem 与 projection layout 等价、合法 CUDA/PyTorch backend 可用性、完整强路径的索引更新成本、输入的时间顺序。官方 MD22 loader 说明数据来源及划分，没有给此处所需 chronology 保证；不下载数据补猜。sitraj 独立帧只能检查帧级正确性，不能给自然 rebuild 率。换一个未经资格化 MACE checkpoint 也不能解决这个缺口；不得让 LJ fallback 冒充神经消费者。

## 竞争解释与论文潜力
先问跨层/跨帧共享是否把准备摊薄；现成 direct-output/prepared API 是否足够；必要搜索或网络算术是否占主导；另一等价 backend 是否更快。剩余索引与同步若只由 adapter 低效造成，应归软件集成。必须在这些解释被区分且有限成本成立之后才谈硬件。现有资料可支持明确待测依赖，尚不能支持独立架构论文主张。
