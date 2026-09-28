# 科学解释

K2560→3072：split1 GEMM L2 read hit fraction 从 0.905873 变为 0.634032（Δ=-0.271841），miss sectors增加 17145056；split8 GEMM从 0.958592 变为 0.958946（Δ=+0.000354）。

判定：`L2_READ_HIT_BEHAVIOR_DIRECTIONALLY_CONSISTENT_WITH_CAPACITY_KNEE`。该判定仅说明目标GEMM的srcunit TEX read-side L2 lookup行为在方向上是否与capacity knee一致。A reduction独立列示，不参与weight-locality解释。指标不区分qweight、input或metadata，不能作tensor级归因，也不证明唯一L2因果。
