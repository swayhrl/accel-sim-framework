# R20问题准备卡｜逐world收敛之后的批量求解执行

2026-10-01。**PREPARATION ONLY；没有GPU/模拟器授权，不是Codex Goal。**

## 要回答什么

MuJoCo Warp已经跳过已收敛world的算术，并用全局未完成计数控制条件图循环。若自然求解进度不同，保留原world维度的发射是否仍造成可避免的完整step成本？慢world的必要工作、现有mask足够、软件配置问题必须作为竞争解释。

## 已有能力

冻结来源`google-deepmind/mujoco_warp@3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`，solver blob`090061796792f4d11408eaa69b4ef3c44465c705`。

必须保留/核清：ctx.done、nsolving、capture_while、warmstart、incremental/stable-state、实际sparse/compact分支、已有限制空slot发射的优化。Madrona、GATO和CUDA条件图是直接能力近邻；动态队列或一block一问题本身不是创新。

## 输入入口及缺口

首选核`benchmarks/unitree_g1/scene_hfield.xml`与同目录descriptor绑定的`shuffle_dance.npz`，Menagerie revision `affef0836947b64cc06c4ab1cbf0152835693374`。先核字节、控制shape、初始化/偏移规则、实际solver和迭代overflow；本轮没有下载/运行。

一个scene、一个显存合法batch、一个回放区间。若作者驱动只是完全相同world克隆，则它只作工程canary；可事前确定不同回放相位组成真实轨迹状态诊断batch，但必须标明构造分布，不能冒称实际RL训练分布。不能按求解时间挑困难样本。

## 最小后续设计（待另授权）

1. CPU/source和runtime canary合并，不另造长期平台。绑定graph模式、步长、求解器容差、容量、warmstart、控制与完整状态。
2. 先取一个发现窗口和一个封存窗口；观测k_i、未完成world数、nefc、overflow与完整solver/step时间。不同world的迭代占用只作结构统计。
3. 如有真实活动集合收缩且有界可实现，选一个在线活跃world-ID/有限worker软件诊断；不能依赖未来k_i，不能减少正确方程/约束或更早停止。原先逻辑world到模型参数的映射不变。
4. 计入列表维护、间接索引、状态gather/scatter和同步；候选须覆盖完整所改阶段。仅某个kernel的微测试不升级成step收益。
5. 主要区间为所有world同一step的输入就绪→全部结果提交。不能让早完成world提前进入下一policy步。
6. 数值规则基于物理baseline重复性和残差，而非沿用LLM容差；保留constraint coverage、收敛/上限状态和物理状态比较。正式timing不含重型统计。
7. 有稳定增量才用封存状态检验；若需要大幅重写求解器，先STOP设计审查。没有现象、现有能力充分或必要慢world主导，均可结束。

## 同数据备选，不另开系统

复用回放统计逐world约束峰值与njmax工作区：contact池化已有；检查sparse/compact之后剩余预留容量是否真的影响完整step或可行batch。字节多不是性能问题，不能缩容量到overflow/丢约束。

## 边界

这只是具身RL环境计算负载；不声称训练time-to-reward收益，不声称所有GPU优化空间，不是Accel-Sim仿真。109 runtime、FP32重复性、真实分布和成本都待验证。Lane E/F/G全部STOP。

完整来源与证据层级见`../rounds/2026-10-01_ROUND_20_EMBODIED_COMPUTE_PROBLEM_DISCOVERY.md`。
