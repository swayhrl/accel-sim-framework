# 科学解释（producer描述性）

固定M=256、N=49152，仅改变K；所有新K的grid、scratch与reduction合同相同。K=12288直接引用accepted endpoint，未重跑。

- K=2048：full/L2=0.779，split1 gain=51.550%，B/A DRAM=0.056。
- K=2560：full/L2=0.974，split1 gain=44.332%，B/A DRAM=0.367。
- K=3072：full/L2=1.169，split1 gain=17.437%，B/A DRAM=1.445。
- K=4096：full/L2=1.559，split1 gain=-0.405%，B/A DRAM=1.828。
- K=12288：full/L2=4.676，split1 gain=-71.014%，B/A DRAM=3.168。

重点的K2560(<L2)与K3072(>L2)之间趋势只作描述；是否支持容量工作集机制由Lane6独立consumer重算。这里不声称硬64MiB阈值、具体tensor归因或唯一L2因果，也不自动触发SASS/Accel-Sim。
