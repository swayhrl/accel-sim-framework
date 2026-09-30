# Round16｜两份实验合同的来源、边界与执行安排

日期：2026-09-30。交付类型：研究设计，不是已执行结果或完整Codex Goal。

## 1. 决策

先推进两条准备线：Lane F对应VLA/RTC/VJP，Lane G对应R102新增真实输入准入。Lane名称不变；Lane E保持STOP，不新增模拟器任务。109只有一张卡，未来CUDA任务使用既有`/data/c16/locks/c16_gpu_campaign.lock`互斥执行，CPU/source/小型artifact审计可以并行。本次未向109/174发送任务、未下载模型、未运行GPU实验。

CCE/Liger低成本旁路本轮暂缓：目前前两题分别需要运行语义资格和真实输入资格，再开第三套训练loss环境会分散投入。保留题目，不声称其已被验证或没有空间；不因前两线等待就自动启动第三条GPU线。后续确有可直接复用的真实hidden/labels和兼容强基线，再另做一个完整loss-forward/backward小对照。

## 2. 已继承的项目authority

- Round15设计依据：`swayhrl/accel-sim-framework@c6958df456393b46a9268add5898bbd7f12c1ca9`；该版本已重新读取。
- R101R5执行记录：`48f5bf24a2136521e272ed4d1da18ba5aa5f798e`；继续保留范围性Native未观察到支持，不据此宣称模拟器结果错误。
- 旧R102：`056daae4082aafb4bfaab10db19f004d4d76ec73`。此次由主handoff的§7.7重新定位：无真实before/after完整tensor，CUDA及GPU锁获取为0。未将Round15候选描述当成已执行结果。
- 工程原则：164为大型资产authority，109可留活跃副本，174不stage大trace；可重建wrapper不是科学payload缺失。沿用现有协议，不重建平台。

## 3. 本次重新核查的原始来源

下面的Git blob是本次实际读取内容的指纹，不冒充已在109验证的runtime commit。正式计时前，执行端必须固定完整repo commit、依赖版本及模型/输入revision和文件hash。本文没有运行作者代码。

| ID | 一手来源及位置 | 本次证实的内容与限制 |
|---|---|---|
| S1 | https://huggingface.co/docs/lerobot/main/rtc | RTC guided模式支持SmolVLA；trained模式要求特定Pi05训练checkpoint，不能视为同一合同替代。文档不证明当前具体源码已经正确反向。 |
| S2 | `huggingface/lerobot`, `src/lerobot/policies/rtc/modeling_rtc.py`, blob `24f0c6a5bf994da0794e6e758ee5561e717d2817` | `denoise_step`先clone/detach，先调用denoiser，随后才设`requires_grad_(True)`并求grad。若denoiser没有另行建立对输入的梯度连接，网络Jacobian项不会进入该VJP。属于源码风险及推论，不是已完成109动态故障验证。 |
| S3 | `huggingface/lerobot`, `src/lerobot/policies/smolvla/modeling_smolvla.py`, blob `cbea888a8f4e414498b8f12c1cc3f8499ac3191b`; https://huggingface.co/lerobot/smolvla_libero | 公开checkpoint及action-expert denoise路径可定位；实际显存峰值、当前依赖兼容和RTC数值资格尚未运行确认。 |
| S4 | `Physical-Intelligence/real-time-chunking-kinetix`, `src/model.py`, blob `9e04c86cd3b26e33627128032aa8e98bc6f7de70`；README blob `6b2d21e5f905bb111f9aee81ddfe4d74a5e5990a` | `realtime_action`明确用`jax.vjp(denoiser, x_t, has_aux=True)`；README提供BC checkpoint入口。Kinetix是动作策略而不是视觉语言模型，只作算法参考。 |
| S5 | https://arxiv.org/html/2602.03839v1 ，§3–4、Appendix E/G | PULSE研究真实RL权重变化，以绝对值patch和anchor链重建；存在CPU压缩、通信及发布窗口层次，不能称整套GPU实测。正文公开地址不等于我们已取得原始tensor。 |
| S6 | https://arxiv.org/html/2605.07330v1 ；`scitix/helix/README.md` blob `e35e1760bf8342fe926285f7ed74e7ce268ea1c9` | SparseRL-Sync/Helix提供稀疏同步和dump分析代码；README不是完整before/after tensor。此次没有宣布新输入已经到位。 |
| S7 | `one-covenant/grail/README.md` blob `3b0cf81845eb4984448246c2343b4d67c755d52e` | 当前代码描述GRPO训练和R2 checkpoint发布；需要检查真实artifact访问和版本映射。不注册Bittensor、不申请凭据、不部署分布式训练来取得输入。 |
| S8 | 用户AWMA主handoff §7.7，旧R102 execution commit如上 | 旧结论是输入未资格化，不是“GPU实现无收益”。新合同只扩展真实数据入口，不重复旧GPU任务。 |

Guided Action Flow仍是近邻，不选作首轮主对象：作者仓库明确critic/rollout大文件不入Git、需重跑或另取artifact；本轮不为此先训练critic。已查入口：https://github.com/ylhaichen/guided-action-flow 。

## 4. 第一份合同的关键数值语义

按LeRobot的时间方向，denoised状态写为`x1 = x - t*v(x, observation)`，修正项是`J_x(x1)^T * stop_gradient(error)`。必须包含denoiser对action latent的Jacobian，而非只对恒等分支求导。CPU解析canary可取`v(x)=2*x`，此时修正应是`(1-2*t)*error`；它只是正确性fixture，不是AI性能样本。

权重冻结不等于整个forward处于`no_grad`：允许观测前缀按原实现合法缓存，但需要求导的action-expert必须保持对输入的计算图。不求参数梯度，不额外反传整个视觉语言前缀，不跨denoise步无界retain_graph。若为恢复作者算法而修正求导时机，必须形成单独reference身份；不能把增加真实VJP之后的变慢称为原框架的天然开销。

第一份合同的FP32和模型dtype容差是我们预注册的工程筛选要求，原论文未据此保证机器人质量。候选失败不得放宽容差追求speedup；误差无法收敛时停止数值资格。开环观测回放可以测chunk-ready latency，不能报告闭环成功率或真实动作时效收益。

## 5. 两份合同的共同最小预算与判定

- 正式计时在语义canary后进行；每个冻结条件使用3组配对重复，每组2次预热、5次未插桩测量，保存每次值、median和MAD。复位、输入加载、编译各自独立计时；应用本来需要的同步/提交不能隐藏到区间外。
- A1/B2只允许一种有界软件方案，不以兼容性为由无界重写编译器或训练框架。普通工程修复并入本轮，但更换算法/模型/数值合同不得伪装为工程修复。
- instrumentation独立运行；saved-tensor字节、allocator峰值、NCU DRAM流量不是同一指标。profiling结果不替代未插桩计时。
- 上限分析保留必需算术、依赖和已有重叠；仅在明确假设下用依赖图消除目标成本。不得无条件使用`max(T_producer,T_consumer)`或把算法关闭后的差值当硬件上界。
- 5%是本轮追加投入门槛，不是测量误差阈值、性能保证或“低于5%无科学意义”的定理。没有时间线/权重时写未知；未知不等于负结果，也不自动获得机制准入。
- 交付统一为一张结果表、数值与target receipt、简短判断和raw/hash索引；不复制几十项旧平台gate，不为每个小问题另开Goal。
- 未授权训练模型/critic、机器人硬件操作、NVBit/SASS采集、Accel-Sim、FULL5、容量/参数扫描或新硬件机制。
