# 七输入只读覆盖：完整epoch模型证据，非运行资格

| 输入 | 候选RO line | RO读取lane引用 | 读取line覆盖 | 读取引用覆盖 |
|---|---:|---:|---:|---:|
| SAD | 396 | 25344 | 1.1543% | 2.2947% |
| 向量加法 | 250000 | 8000000 | 100.0000% | 100.0000% |
| CFD | 51612 | 1651584 | 77.2727% | 36.5321% |
| 可分离卷积 | 294912 | 11698176 | 50.0000% | 49.8952% |
| 快速Walsh变换 | 0 | 0 | 0.0000% | 0.0000% |
| B树 | 3 | 73728 | 0.0034% | 0.1393% |
| 二维小波 | 24576 | 786432 | 20.0000% | 13.4370% |

每份证据匹配本输入独立完整commandlist/全部kernel及原trace content hash；六新输入未重跑相同21项解析器测试，复用原准确工具。Conv原证书与C/E审阅保持，其余六份是待C/E审阅的新候选，均不自动授权runtime。全体没有unresolved opcode；FWT的0是完整模型分析后无可认证line，不能把它解释为实际R性能为0。其余原机会表UNKNOWN不变。

读取line覆盖分母为有全局读取的不同128B line；读取引用覆盖分母是全局读取lane-line触及次数。另列的model_line_coverage分母包括write-only line，不要混淆。统计不等于cache占用/命中、不同L2请求或受阻UID交集；后者全为UNKNOWN。

B树存在两kernel间host更新，更新覆盖的整128B line已保守排除，所以只剩3条候选；不得借Conv证书扩大。FWT全epoch读后有写，零候选意味着完整F中R安全回退，不为触发改trace或缩减规模。向量加法RO读取覆盖高也不自动证明line-MSHR/tag是瓶颈；保留baseline零压力证据。

所有输入当前active_runtime_coverage=0表示尚无最终qualified binding，并非实际RO机会为零。最终A/E接受后，仅本输入已认证line启用R，未知/未认证line使用native路径，证书内写入/host overlap应fail closed；不隐藏writer。其他六输入不可复制Conv证书。

新btree/dwt2d的全输入非原子资格仍待E独立检查；RO解析器不是native原子资格替代。完整真实应用结果和控制/离线输入证据严格分开。
