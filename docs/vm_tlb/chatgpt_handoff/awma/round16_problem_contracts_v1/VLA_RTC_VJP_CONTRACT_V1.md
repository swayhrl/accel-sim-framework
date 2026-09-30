# 实验合同一｜VLA推理VJP：真实开销与状态生命周期

**2026-09-30｜VLA_RTC_VJP_BOUNDARY_V1｜拟由Lane F / 109执行。** 本页冻结问题与最小实验；不代表节点已启动。来源与统一测量规则见`SOURCE_AND_SCOPE_NOTES.md`。

**问题与假设。** 固定完整RTC引导算法后，动作生成中的网络VJP是否真正发生？其激活保存、重算、物化或等待，经过强软件优化后是否仍影响完整动作chunk就绪时间？不预设访存主导，也不把VJP算术本身全部当成可消除开销。

**负载与准入。** 首选`lerobot/smolvla_libero`及对应`lerobot/libero`观测，采用RTC原作者完整VJP语义；不训练critic、不换大模型。先做CPU解析函数导数测试，再验证模型反向确实穿过action expert，权重保持冻结。当前LeRobot源码存在“denoiser调用之后才设置输入requires_grad”的风险，不能直接认定合格。优先使用已有正确版本；只允许一次有记录的求导连通性修复，以原算法重新冻结reference，不将修复前后差异记成优化收益。仍不合格即停；Kinetix仅作导数参考，不冒充VLA样本。[S1–S4]

**固定输入。** B=1；两个预选episode各取4个连续chunk窗口，A用于发现、B封存至验证。绑定checkpoint/source/tokenizer或processor、观测帧/状态/语言、初始噪声、原配置dtype/步数/chunk长、guidance权重与mask。上一chunk由同一reference生成，不用示教动作代替；一次reference canary确定合法delay，随后各arm不变。属于数据集观测驱动的开环回放，不声称真实机器人闭环。

**最小对照。** A0：合格的完整VJP reference。A1：同一数值合同下的一种强软件实现，限一次compile/静态buffer复用方案，保留原有合法prefix缓存，编译成本单列。D0：关闭guidance，仅说明额外工作，属于不同算法，不能用A0−D0宣传硬件空间。先测A；只有值得继续才解封B，不扫步数、batch或guidance。

**测量与正确性。** 主指标为观测输入就绪→完整chunk提交的未插桩墙钟/GPU完成延迟；分别记录视觉语言前缀、denoiser、VJP、修正/提交及重叠。保存VJP、逐步latent和最终动作；FP32检查`atol=1e-5, rtol=1e-4`，模型dtype检查`atol=1e-3, rtol=1e-2`，并报告最大误差；这是本轮工程容差，不是任务质量保证。计真实backward、峰值显存、saved-tensor去重字节及重算次数；这些字节不是DRAM流量。最多1次NSYS、2个有解释价值的NCU目标，不抓SASS trace。

**判断与终点。** 先用时间线/依赖图估计“仅移除目标生命周期成本”的乐观空间，保留必需算术和数据依赖；算不清就写未知，不按kernel时长直接相减。若完整chunk空间不足5%，或强软件已解决，停止硬件方向；若主要是数学管线，转为计算事实而非缓存动机。只有同合同、超出重复波动、验证episode同向且仍有明确状态/交接残差，才提交后续机制候选。5%仅是投入门槛。第一轮不做机器人成功率、deadline收益、硬件收益或跨VLA推广。
