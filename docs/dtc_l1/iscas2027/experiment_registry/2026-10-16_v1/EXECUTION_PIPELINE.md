# 并发／流水执行安排（科学gate与资源效率同时优先）

**不启动新Goal**。原174 Codex正在执行`DTC_SERVICE_AND_MODERN_BASELINE_CLOSURE_174_V1`，109原生任务已提交结束。本文件仅规范合法的rolling和优先级，不能覆盖原`GOAL_174.md`或`REGISTERED_ROWS_V2.tsv`。

## 可并行的五条独立路径

| 路径 | 可立即进行 | 不能等待的原因 | 停止／转移条件 |
|---|---|---|---|
| A：64-SM finite试点 | 已注册的IO/OO和TRAD96，每行结束立即strict validate；reuse B16N/TC80N | 是主结果关键路径 | R1 V2 gate已过；修改身份则单行重新资格 |
| B：64-SM其余12项 | 某arm一条合法pilot PASS后，余8程序同arm直接rolling；先测运行成本再安排重行 | GESUMMV/GEMM/MRI-Q是拖尾风险 | 不能跨arm gate；不得为了填矩阵重跑已受理行 |
| C：合法机制控制 | 4个IO128与4个WAIT128按每程序的IO+OO gate滚动 | 时间/占用解释可与其他应用模拟并行 | 只需原4诊断程序，限于新计数器定义 |
| D：4080原生/基线 | 109结果直接作为原生基线证据；174可继续现代传统baseline-only与SpMV CPU trace准入 | 不依赖现代DTC容量合同 | 当前原生任务结束；不得为LayerNorm skipped CALL开追踪器重构 |
| E：4080固定预算审计 | CPU-only，检查每kernel shared+L1+DTC+原side store与端口共存 | 不消耗仿真控制器，能尽早知道是否值得做现代DTC | 若改变支持域/协议，HOLD并报告，不启动现代DTC |
| F：论文及硬件 | 论文实验方法、图模板与旧证据位置立刻编写；用户硬件综合可独立进行 | H1不能等性能完结才开始 | 最终表只接收validated身份，缺数据保留空值 |

## 无批次屏障，但有科学依赖

`R1 V2 PASS → {pilot IO/OO, TRAD96 pilot, modern traditional-only pilot, asset review} → {same-arm 8-workload cohort, matched IO128/WAIT128 controls} → result figures`。

`109 native PASS → SpMV consumer opcode/ROI contract → (if admitted) paired SpMV simulation`；LayerNorm native-only, SASS NOT_ADMITTED。

`modern shared/L1 capacity audit (128 KiB fixed) → if legal and validated → 4080 DTC optional paired experiment`；不可从此箭头反推原64-SM任务需等待现代gate。

## 资源调度

- 在174运行前先读取`ps/cgroup/CPU RSS/swap/IO/其他项目`，不要把预设worker数当硬指标。初始建议4，已观测RSS允许再升8／16；同一时刻重资源行至多2条直至实际RSS确认，**不是强制越高越好**。
- 对已获资格的慢行尽早启动，而快速行在剩余槽中滚动；不要先把所有短任务做完才跑慢任务。单行结束先validator、终止／失败证据保留，然后补相同gate允许的下一行。
- 同一baseline在多组能严格等价复用时只运行一次。前端有限服务改动影响的IO/OO不能拿旧模型周期硬凑新GM。FAST64、Lane-E、TC80、SG0、SG3、logical80均不得再开矩阵。
- 109已结束，**不需要把GPU长期占着**。SpMV小样本有36 CTA、DRAM read=0，不构成现代容量瓶颈证明；LayerNorm native-only不进入DTC GM。
- 队列满事件的下降不足以证明端到端提速；若coarse screen已经回答论文问题，停止敏感性中间点。
- 避免硬盘大空闲阈值阻止合法任务；核对实际写权限、预估输出量、原始数据hash与rolling cleanup策略即可，失败日志和immutable attempts必须留存。

## 优先级退让顺序

时间不够时首先取消RTX3070、现代LayerNorm SASS修复、额外形状/额外敏感性中间点；其次若4080现代DTC容量合同需重构合法域，则现代DTC比较取消，仅保留baseline与原生趋势。保留E01正确模型、E04/E05核心公平比较、E07有限机制解释、E18成本边界；若完整GM12来不及，只报告完整受理的子集，**不得标GM12**。
