# 科学解释

strong GROUP_FULL_M split1中存在严格跨CTA重复：M64每个(Ntile,Ktile)转换4次、唯一1次，R_dup=75%；M32验证点R_dup=50%。现有kernel已通过register计算+B_shared staging消除CTA内主要重复，但没有跨CTA共享。剩余单tile展开8KiB，fanout 4 CTA；完整Ntile展开1MiB，whole operator展开96MiB并超过64MiB L2。更关键的是accepted natural SHARE3目标时间权重仅f=0.017400，即使目标零成本whole-decode ceiling也只有1.017708x。结合QUICK/FLUTE/StreamDQ等近邻与同步/分发成本，本问题有重复但当前系统headroom不足，不值得进入新dequant cache机制研究。
