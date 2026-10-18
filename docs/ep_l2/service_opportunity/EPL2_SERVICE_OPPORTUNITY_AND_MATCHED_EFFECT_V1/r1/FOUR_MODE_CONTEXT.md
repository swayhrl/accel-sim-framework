# 四模式对照对本轮的约束

本表是已经接受的combined发行背景，不是新microopt的OFF/ON结果。Core9bd30ed、Framework8ab6013、binaryfb67448d的完整身份与run-key在CSV。

| 输入 | C_B | C_S64 | C_U_CAP16 | C_U | B/U | S64/U | U_CAP16/U |
|---|---:|---:|---:|---:|---:|---:|---:|
| convolutionSeparable | 292932 | 293258 | 292544 | 291525 | 1.004826344 | 1.005944602 | 1.003495412 |
| FWT_7_21 | 493189 | 494627 | 491696 | 491662 | 1.003105792 | 1.006030566 | 1.000069153 |

观察：增加静态WB从16到64没有使两个样本变快；S64比B16分别慢326/1438cycles。Unified相对U_CAP16分别快1019/34cycles（0.3495%/0.0069%的ratio增益），容量边际明显依输入变化。S64 observed wbuf_full为0、record峰值58/35，没有证明静态预算对所有输入非约束，也没有证明该分区是最优静态。S64不是额外48行的免费容量，128bypass减少为80；总payload1168不变。

竞争解释：B16→U_CAP16同时改变in-place/copy、payload角色组织与落点；不是纯copy单因素。U_CAP16→Unified保持统一组织而去掉local reserved+live≤16限制，较接近容量边际，但schedule/下游队列随其变化，不能把cycle差进一步无证据拆成独占阻塞。FWT在U_CAP16有967460次quota refusal而放开仅快34cycles，正好约束“refusal次数就是性能收益”的错误叙述。

受控对照：本轮要求B16/S64/Unified各自OFF→MQ2/RG1；四模式给出已有归因背景，不能跨新binary沿用这些OFF。保留同背景的Q4/WAD256、D2/D4及ICNT2正负例；不追加全扫。

结论范围：当前已接受数据支持统一组织相对这两个静态分区的有限优势，以及Conv比FWT更可见的容量边际；尚不能声称MQ2/RG1会扩展EP收益。局部/完整Ideals属于另有scope的端点，不是本轮服务回收机会的实测上界，也不跨binary拼成分解。
