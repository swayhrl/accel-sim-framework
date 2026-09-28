# 机制解释

K2560到3072仅增长20%，split1 DRAM却增长4.04倍，split8总DRAM仅增长1.03倍；split1 median timing同步增长1.60倍。连续K序列显示split1收益随K总体恶化并在K4096附近接近翻转，K12288延续为强负收益。工作集容量是重要因素，但64MiB不是硬阈值，也不能把全部DRAM归为qweight或唯一归因L2。

建议后续只做K4096 M256 N49152 split1/split8 paired capacity counterfactual；本consumer不执行。
